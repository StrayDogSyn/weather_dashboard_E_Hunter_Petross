"""Repository implementation for application settings and user preferences."""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from .base_repository import BaseRepository
from .models import SettingsModel
from .connection_manager import DatabaseConnectionManager, RedisConnectionManager
from ...shared.exceptions import DatabaseError, ValidationError


logger = logging.getLogger(__name__)


class SettingsRepository(BaseRepository[SettingsModel]):
    """Repository for managing application settings and user preferences."""
    
    def __init__(self, db_manager: DatabaseConnectionManager, redis_manager: RedisConnectionManager):
        super().__init__(db_manager, redis_manager, "settings", "settings")
    
    def _get_select_query(self) -> str:
        """Get the SELECT query for fetching records."""
        return """
        SELECT id, setting_key, setting_value, setting_type, category,
               description, is_user_configurable, default_value,
               created_at, updated_at
        FROM settings
        """
    
    def _get_insert_query(self) -> str:
        """Get the INSERT query for creating records."""
        return """
        INSERT INTO settings (
            setting_key, setting_value, setting_type, category,
            description, is_user_configurable, default_value,
            created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    def _get_update_query(self) -> str:
        """Get the UPDATE query for modifying records."""
        return """
        UPDATE settings SET
            setting_value = ?, setting_type = ?, category = ?,
            description = ?, is_user_configurable = ?, default_value = ?,
            updated_at = ?
        WHERE id = ?
        """
    
    def _extract_model_from_row(self, row: tuple) -> SettingsModel:
        """Extract model from database row."""
        return SettingsModel(
            id=row[0],
            setting_key=row[1],
            setting_value=row[2],
            setting_type=row[3],
            category=row[4],
            description=row[5],
            is_user_configurable=bool(row[6]),
            default_value=row[7],
            created_at=self._parse_datetime(row[8]),
            updated_at=self._parse_datetime(row[9])
        )
    
    def _get_insert_values(self, model: SettingsModel) -> tuple:
        """Get values for INSERT query."""
        now = datetime.now()
        return (
            model.setting_key,
            model.setting_value,
            model.setting_type,
            model.category,
            model.description,
            model.is_user_configurable,
            model.default_value,
            now.isoformat(),
            now.isoformat()
        )
    
    def _get_update_values(self, model: SettingsModel) -> tuple:
        """Get values for UPDATE query."""
        return (
            model.setting_value,
            model.setting_type,
            model.category,
            model.description,
            model.is_user_configurable,
            model.default_value,
            datetime.now().isoformat(),
            model.id
        )
    
    async def get_by_key(self, setting_key: str) -> Optional[SettingsModel]:
        """Get a setting by its key."""
        cache_key = f"{self.cache_prefix}:key:{setting_key}"
        
        try:
            # Check cache first
            cached = await self._get_from_cache(cache_key)
            if cached:
                return cached
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"{self._get_select_query()} WHERE setting_key = ?",
                    (setting_key,)
                )
                row = await cursor.fetchone()
                
                if row:
                    model = self._extract_model_from_row(row)
                    await self._set_cache(cache_key, model)
                    return model
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get setting by key '{setting_key}': {e}")
            raise DatabaseError(f"Failed to get setting by key: {e}")
    
    async def get_by_category(self, category: str) -> List[SettingsModel]:
        """Get all settings in a specific category."""
        cache_key = f"{self.cache_prefix}:category:{category}"
        
        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"{self._get_select_query()} WHERE category = ? ORDER BY setting_key",
                    (category,)
                )
                rows = await cursor.fetchall()
                
                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models)
                return models
                
        except Exception as e:
            logger.error(f"Failed to get settings by category '{category}': {e}")
            raise DatabaseError(f"Failed to get settings by category: {e}")
    
    async def get_user_configurable(self) -> List[SettingsModel]:
        """Get all user-configurable settings."""
        cache_key = f"{self.cache_prefix}:user_configurable"
        
        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"{self._get_select_query()} WHERE is_user_configurable = TRUE ORDER BY category, setting_key"
                )
                rows = await cursor.fetchall()
                
                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models)
                return models
                
        except Exception as e:
            logger.error(f"Failed to get user configurable settings: {e}")
            raise DatabaseError(f"Failed to get user configurable settings: {e}")
    
    async def get_value(self, setting_key: str, default: Any = None) -> Any:
        """Get a setting value by key, with optional default."""
        setting = await self.get_by_key(setting_key)
        if setting:
            return self._convert_setting_value(setting.setting_value, setting.setting_type)
        return default
    
    async def set_value(self, setting_key: str, value: Any, setting_type: Optional[str] = None) -> bool:
        """Set a setting value by key."""
        try:
            existing = await self.get_by_key(setting_key)
            
            if existing:
                # Update existing setting
                existing.setting_value = str(value)
                if setting_type:
                    existing.setting_type = setting_type
                existing.updated_at = datetime.now()
                
                await self.update(existing)
                
                # Clear related caches
                await self._clear_cache_pattern(f"{self.cache_prefix}:key:{setting_key}*")
                await self._clear_cache_pattern(f"{self.cache_prefix}:category:{existing.category}*")
                
                return True
            else:
                # Create new setting
                new_setting = SettingsModel(
                    setting_key=setting_key,
                    setting_value=str(value),
                    setting_type=setting_type or self._infer_setting_type(value),
                    category="user",
                    description=f"User setting: {setting_key}",
                    is_user_configurable=True,
                    default_value=str(value)
                )
                
                await self.create(new_setting)
                return True
                
        except Exception as e:
            logger.error(f"Failed to set setting '{setting_key}' to '{value}': {e}")
            raise DatabaseError(f"Failed to set setting: {e}")
    
    async def reset_to_default(self, setting_key: str) -> bool:
        """Reset a setting to its default value."""
        try:
            setting = await self.get_by_key(setting_key)
            if not setting:
                return False
            
            if setting.default_value is not None:
                setting.setting_value = setting.default_value
                setting.updated_at = datetime.now()
                
                await self.update(setting)
                
                # Clear related caches
                await self._clear_cache_pattern(f"{self.cache_prefix}:key:{setting_key}*")
                await self._clear_cache_pattern(f"{self.cache_prefix}:category:{setting.category}*")
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to reset setting '{setting_key}' to default: {e}")
            raise DatabaseError(f"Failed to reset setting to default: {e}")
    
    async def reset_category_to_defaults(self, category: str) -> int:
        """Reset all settings in a category to their default values."""
        try:
            settings = await self.get_by_category(category)
            reset_count = 0
            
            for setting in settings:
                if setting.default_value is not None:
                    setting.setting_value = setting.default_value
                    setting.updated_at = datetime.now()
                    await self.update(setting)
                    reset_count += 1
            
            # Clear category cache
            await self._clear_cache_pattern(f"{self.cache_prefix}:category:{category}*")
            
            return reset_count
            
        except Exception as e:
            logger.error(f"Failed to reset category '{category}' to defaults: {e}")
            raise DatabaseError(f"Failed to reset category to defaults: {e}")
    
    async def get_categories(self) -> List[str]:
        """Get all unique setting categories."""
        cache_key = f"{self.cache_prefix}:categories"
        
        try:
            # Check cache first
            cached = await self._get_from_cache(cache_key)
            if cached:
                return cached
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    "SELECT DISTINCT category FROM settings ORDER BY category"
                )
                rows = await cursor.fetchall()
                
                categories = [row[0] for row in rows]
                await self._set_cache(cache_key, categories)
                return categories
                
        except Exception as e:
            logger.error(f"Failed to get setting categories: {e}")
            raise DatabaseError(f"Failed to get setting categories: {e}")
    
    async def bulk_update(self, settings: Dict[str, Any]) -> int:
        """Update multiple settings in a single transaction."""
        try:
            updated_count = 0
            
            async with self.db_manager.get_connection() as conn:
                for setting_key, value in settings.items():
                    # Check if setting exists
                    cursor = await conn.execute(
                        "SELECT id, category FROM settings WHERE setting_key = ?",
                        (setting_key,)
                    )
                    row = await cursor.fetchone()
                    
                    if row:
                        # Update existing setting
                        cursor = await conn.execute(
                            "UPDATE settings SET setting_value = ?, updated_at = ? WHERE setting_key = ?",
                            (str(value), datetime.now().isoformat(), setting_key)
                        )
                        if cursor.rowcount > 0:
                            updated_count += 1
                    else:
                        # Create new setting
                        cursor = await conn.execute(
                            """
                            INSERT INTO settings (
                                setting_key, setting_value, setting_type, category,
                                description, is_user_configurable, default_value,
                                created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                setting_key,
                                str(value),
                                self._infer_setting_type(value),
                                "user",
                                f"User setting: {setting_key}",
                                True,
                                str(value),
                                datetime.now().isoformat(),
                                datetime.now().isoformat()
                            )
                        )
                        if cursor.rowcount > 0:
                            updated_count += 1
                
                await conn.commit()
                
                # Clear all settings caches
                await self._clear_cache_pattern(f"{self.cache_prefix}:*")
                
                return updated_count
                
        except Exception as e:
            logger.error(f"Failed to bulk update settings: {e}")
            raise DatabaseError(f"Failed to bulk update settings: {e}")
    
    async def export_settings(self, category: Optional[str] = None, user_configurable_only: bool = False) -> Dict[str, Any]:
        """Export settings as a dictionary."""
        try:
            if category:
                settings = await self.get_by_category(category)
            elif user_configurable_only:
                settings = await self.get_user_configurable()
            else:
                settings = await self.get_all()
            
            export_data = {
                'exported_at': datetime.now().isoformat(),
                'category_filter': category,
                'user_configurable_only': user_configurable_only,
                'settings': {}
            }
            
            for setting in settings:
                export_data['settings'][setting.setting_key] = {
                    'value': self._convert_setting_value(setting.setting_value, setting.setting_type),
                    'type': setting.setting_type,
                    'category': setting.category,
                    'description': setting.description,
                    'is_user_configurable': setting.is_user_configurable,
                    'default_value': setting.default_value
                }
            
            return export_data
            
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            raise DatabaseError(f"Failed to export settings: {e}")
    
    async def import_settings(self, settings_data: Dict[str, Any], overwrite_existing: bool = False) -> int:
        """Import settings from a dictionary."""
        try:
            imported_count = 0
            
            if 'settings' not in settings_data:
                raise ValidationError("Invalid settings data format")
            
            for setting_key, setting_info in settings_data['settings'].items():
                existing = await self.get_by_key(setting_key)
                
                if existing and not overwrite_existing:
                    continue
                
                if existing:
                    # Update existing
                    existing.setting_value = str(setting_info['value'])
                    existing.setting_type = setting_info.get('type', existing.setting_type)
                    existing.category = setting_info.get('category', existing.category)
                    existing.description = setting_info.get('description', existing.description)
                    existing.updated_at = datetime.now()
                    
                    await self.update(existing)
                else:
                    # Create new
                    new_setting = SettingsModel(
                        setting_key=setting_key,
                        setting_value=str(setting_info['value']),
                        setting_type=setting_info.get('type', 'string'),
                        category=setting_info.get('category', 'imported'),
                        description=setting_info.get('description', f"Imported setting: {setting_key}"),
                        is_user_configurable=setting_info.get('is_user_configurable', True),
                        default_value=setting_info.get('default_value')
                    )
                    
                    await self.create(new_setting)
                
                imported_count += 1
            
            # Clear all caches
            await self._clear_cache_pattern(f"{self.cache_prefix}:*")
            
            return imported_count
            
        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            raise DatabaseError(f"Failed to import settings: {e}")
    
    def _convert_setting_value(self, value: str, setting_type: str) -> Any:
        """Convert string setting value to appropriate Python type."""
        if not value:
            return None
        
        try:
            if setting_type == 'boolean':
                return value.lower() in ('true', '1', 'yes', 'on')
            elif setting_type == 'integer':
                return int(value)
            elif setting_type == 'float':
                return float(value)
            elif setting_type == 'json':
                import json
                return json.loads(value)
            else:  # string or unknown type
                return value
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to convert setting value '{value}' to type '{setting_type}': {e}")
            return value
    
    def _infer_setting_type(self, value: Any) -> str:
        """Infer the setting type from the value."""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, (dict, list)):
            return 'json'
        else:
            return 'string'
    
    async def validate_setting(self, model: SettingsModel) -> List[str]:
        """Validate setting data."""
        errors = []
        
        # Required fields
        if not model.setting_key or not model.setting_key.strip():
            errors.append("Setting key is required")
        
        if model.setting_value is None:
            errors.append("Setting value is required")
        
        # Key format validation
        if model.setting_key and not model.setting_key.replace('_', '').replace('.', '').isalnum():
            errors.append("Setting key must contain only alphanumeric characters, underscores, and dots")
        
        # Key length validation
        if len(model.setting_key) > 100:
            errors.append("Setting key must be 100 characters or less")
        
        # Value length validation
        if len(str(model.setting_value)) > 10000:
            errors.append("Setting value must be 10,000 characters or less")
        
        # Type validation
        valid_types = ['string', 'integer', 'float', 'boolean', 'json']
        if model.setting_type and model.setting_type not in valid_types:
            errors.append(f"Invalid setting type. Must be one of: {', '.join(valid_types)}")
        
        # Category validation
        if model.category and len(model.category) > 50:
            errors.append("Category must be 50 characters or less")
        
        # Description validation
        if model.description and len(model.description) > 500:
            errors.append("Description must be 500 characters or less")
        
        # Value type consistency validation
        if model.setting_type:
            try:
                self._convert_setting_value(str(model.setting_value), model.setting_type)
            except Exception:
                errors.append(f"Setting value is not compatible with type '{model.setting_type}'")
        
        return errors
    
    async def create_with_validation(self, model: SettingsModel) -> SettingsModel:
        """Create a new setting with validation."""
        errors = await self.validate_setting(model)
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")
        
        # Check for duplicate key
        existing = await self.get_by_key(model.setting_key)
        if existing:
            raise ValidationError(f"Setting with key '{model.setting_key}' already exists")
        
        return await self.create(model)
    
    async def update_with_validation(self, model: SettingsModel) -> SettingsModel:
        """Update a setting with validation."""
        errors = await self.validate_setting(model)
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")
        
        return await self.update(model)


async def create_settings_repository(
    db_manager: DatabaseConnectionManager,
    redis_manager: RedisConnectionManager
) -> SettingsRepository:
    """Factory function to create a SettingsRepository."""
    return SettingsRepository(db_manager, redis_manager)