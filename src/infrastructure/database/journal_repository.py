"""Repository implementation for journal entries with full-text search and caching."""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from .base_repository import BaseRepository
from .models import JournalEntryModel
from .connection_manager import DatabaseConnectionManager, RedisConnectionManager
from ...shared.exceptions import DatabaseError, ValidationError
from ...interfaces.journal_interfaces import JournalEntryType, WeatherMood, SearchSortBy


logger = logging.getLogger(__name__)


class JournalRepository(BaseRepository[JournalEntryModel]):
    """Repository for managing journal entries with full-text search."""
    
    def __init__(self, db_manager: DatabaseConnectionManager, redis_manager: RedisConnectionManager):
        super().__init__(db_manager, redis_manager, "journal_entries", "journal")
    
    def _get_select_query(self) -> str:
        """Get the SELECT query for fetching records."""
        return """
        SELECT id, title, content, entry_type, weather_mood, location_name,
               latitude, longitude, weather_data, tags, is_favorite, is_private,
               template_id, created_at, updated_at, weather_date
        FROM journal_entries
        """
    
    def _get_insert_query(self) -> str:
        """Get the INSERT query for creating records."""
        return """
        INSERT INTO journal_entries (
            title, content, entry_type, weather_mood, location_name,
            latitude, longitude, weather_data, tags, is_favorite, is_private,
            template_id, created_at, updated_at, weather_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    def _get_update_query(self) -> str:
        """Get the UPDATE query for modifying records."""
        return """
        UPDATE journal_entries SET
            title = ?, content = ?, entry_type = ?, weather_mood = ?,
            location_name = ?, latitude = ?, longitude = ?, weather_data = ?,
            tags = ?, is_favorite = ?, is_private = ?, template_id = ?,
            updated_at = ?, weather_date = ?
        WHERE id = ?
        """
    
    def _extract_model_from_row(self, row: tuple) -> JournalEntryModel:
        """Extract model from database row."""
        return JournalEntryModel(
            id=row[0],
            title=row[1],
            content=row[2],
            entry_type=row[3],
            weather_mood=row[4],
            location_name=row[5],
            latitude=row[6],
            longitude=row[7],
            weather_data=self._deserialize_json_field(row[8], {}),
            tags=self._deserialize_json_field(row[9], []),
            is_favorite=bool(row[10]),
            is_private=bool(row[11]),
            template_id=row[12],
            created_at=self._parse_datetime(row[13]),
            updated_at=self._parse_datetime(row[14]),
            weather_date=self._parse_datetime(row[15]) if row[15] else None
        )
    
    def _get_insert_values(self, model: JournalEntryModel) -> tuple:
        """Get values for INSERT query."""
        now = datetime.now()
        return (
            model.title,
            model.content,
            model.entry_type,
            model.weather_mood,
            model.location_name,
            model.latitude,
            model.longitude,
            self._serialize_json_field(model.weather_data),
            self._serialize_json_field(model.tags),
            model.is_favorite,
            model.is_private,
            model.template_id,
            now.isoformat(),
            now.isoformat(),
            model.weather_date.isoformat() if model.weather_date else None
        )
    
    def _get_update_values(self, model: JournalEntryModel) -> tuple:
        """Get values for UPDATE query."""
        return (
            model.title,
            model.content,
            model.entry_type,
            model.weather_mood,
            model.location_name,
            model.latitude,
            model.longitude,
            self._serialize_json_field(model.weather_data),
            self._serialize_json_field(model.tags),
            model.is_favorite,
            model.is_private,
            model.template_id,
            datetime.now().isoformat(),
            model.weather_date.isoformat() if model.weather_date else None,
            model.id
        )
    
    async def search_full_text(self, query: str, limit: int = 20, offset: int = 0) -> Tuple[List[JournalEntryModel], int]:
        """Perform full-text search on journal entries.
        
        Returns:
            Tuple of (entries, total_count)
        """
        cache_key = f"{self.cache_prefix}:search:{query}:{limit}:{offset}"
        
        try:
            # Check cache first
            cached = await self._get_from_cache(cache_key)
            if cached:
                return cached
            
            async with self.db_manager.get_connection() as conn:
                # Get total count
                count_cursor = await conn.execute(
                    "SELECT COUNT(*) FROM journal_entries_fts WHERE journal_entries_fts MATCH ?",
                    (query,)
                )
                total_count = (await count_cursor.fetchone())[0]
                
                # Get search results with ranking
                cursor = await conn.execute(
                    f"""
                    SELECT je.id, je.title, je.content, je.entry_type, je.weather_mood,
                           je.location_name, je.latitude, je.longitude, je.weather_data,
                           je.tags, je.is_favorite, je.is_private, je.template_id,
                           je.created_at, je.updated_at, je.weather_date
                    FROM journal_entries je
                    JOIN journal_entries_fts fts ON je.id = fts.rowid
                    WHERE fts MATCH ?
                    ORDER BY fts.rank
                    LIMIT ? OFFSET ?
                    """,
                    (query, limit, offset)
                )
                rows = await cursor.fetchall()
                
                models = [self._extract_model_from_row(row) for row in rows]
                result = (models, total_count)
                
                await self._set_cache(cache_key, result, ttl=300)  # 5 minute cache for search
                return result
                
        except Exception as e:
            logger.error(f"Failed to perform full-text search for '{query}': {e}")
            raise DatabaseError(f"Failed to perform full-text search: {e}")
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime, 
                               entry_type: Optional[str] = None) -> List[JournalEntryModel]:
        """Get journal entries within a date range."""
        cache_key = f"{self.cache_prefix}:date_range:{start_date.date()}:{end_date.date()}:{entry_type}"
        
        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached
            
            query = f"{self._get_select_query()} WHERE created_at BETWEEN ? AND ?"
            params = [start_date.isoformat(), end_date.isoformat()]
            
            if entry_type:
                query += " AND entry_type = ?"
                params.append(entry_type)
            
            query += " ORDER BY created_at DESC"
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()
                
                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models, ttl=600)  # 10 minute cache
                return models
                
        except Exception as e:
            logger.error(f"Failed to get entries by date range: {e}")
            raise DatabaseError(f"Failed to get entries by date range: {e}")
    
    async def get_by_location(self, location_name: str, limit: int = 50) -> List[JournalEntryModel]:
        """Get journal entries for a specific location."""
        cache_key = f"{self.cache_prefix}:location:{location_name}:{limit}"
        
        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE location_name = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (location_name, limit)
                )
                rows = await cursor.fetchall()
                
                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models)
                return models
                
        except Exception as e:
            logger.error(f"Failed to get entries by location '{location_name}': {e}")
            raise DatabaseError(f"Failed to get entries by location: {e}")
    
    async def get_by_weather_mood(self, mood: str, limit: int = 50) -> List[JournalEntryModel]:
        """Get journal entries by weather mood."""
        cache_key = f"{self.cache_prefix}:mood:{mood}:{limit}"
        
        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE weather_mood = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (mood, limit)
                )
                rows = await cursor.fetchall()
                
                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models)
                return models
                
        except Exception as e:
            logger.error(f"Failed to get entries by mood '{mood}': {e}")
            raise DatabaseError(f"Failed to get entries by mood: {e}")
    
    async def get_favorites(self, limit: int = 50) -> List[JournalEntryModel]:
        """Get favorite journal entries."""
        cache_key = f"{self.cache_prefix}:favorites:{limit}"
        
        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE is_favorite = TRUE
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (limit,)
                )
                rows = await cursor.fetchall()
                
                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models)
                return models
                
        except Exception as e:
            logger.error(f"Failed to get favorite entries: {e}")
            raise DatabaseError(f"Failed to get favorite entries: {e}")
    
    async def get_by_tags(self, tags: List[str], match_all: bool = False, limit: int = 50) -> List[JournalEntryModel]:
        """Get journal entries that have any or all of the specified tags."""
        cache_key = f"{self.cache_prefix}:tags:{'_'.join(sorted(tags))}:{match_all}:{limit}"
        
        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached
            
            # Get all entries and filter by tags in Python (SQLite JSON handling is limited)
            all_entries = await self.get_all()
            
            if match_all:
                # Entry must have ALL specified tags
                filtered = [
                    entry for entry in all_entries
                    if all(tag in entry.tags for tag in tags)
                ]
            else:
                # Entry must have ANY of the specified tags
                filtered = [
                    entry for entry in all_entries
                    if any(tag in entry.tags for tag in tags)
                ]
            
            # Sort by creation date and limit
            filtered.sort(key=lambda x: x.created_at, reverse=True)
            result = filtered[:limit]
            
            await self._set_list_cache(cache_key, result, ttl=300)
            return result
            
        except Exception as e:
            logger.error(f"Failed to get entries by tags {tags}: {e}")
            raise DatabaseError(f"Failed to get entries by tags: {e}")
    
    async def get_recent(self, days: int = 30, limit: int = 50) -> List[JournalEntryModel]:
        """Get recent journal entries."""
        cache_key = f"{self.cache_prefix}:recent:{days}:{limit}"
        
        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached
            
            start_date = datetime.now() - timedelta(days=days)
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE created_at >= ?
                    ORDER BY created_at DESC
                    LIMIT ?
                    """,
                    (start_date.isoformat(), limit)
                )
                rows = await cursor.fetchall()
                
                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models, ttl=300)  # 5 minute cache
                return models
                
        except Exception as e:
            logger.error(f"Failed to get recent entries: {e}")
            raise DatabaseError(f"Failed to get recent entries: {e}")
    
    async def toggle_favorite(self, entry_id: int) -> bool:
        """Toggle the favorite status of a journal entry."""
        try:
            async with self.db_manager.get_connection() as conn:
                # Get current favorite status
                cursor = await conn.execute(
                    "SELECT is_favorite FROM journal_entries WHERE id = ?",
                    (entry_id,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return False
                
                new_favorite_status = not bool(row[0])
                
                # Update favorite status
                cursor = await conn.execute(
                    "UPDATE journal_entries SET is_favorite = ?, updated_at = ? WHERE id = ?",
                    (new_favorite_status, datetime.now().isoformat(), entry_id)
                )
                
                if cursor.rowcount > 0:
                    await conn.commit()
                    
                    # Clear related caches
                    await self._clear_cache_pattern(f"{self.cache_prefix}:favorites*")
                    await self._clear_cache_pattern(f"{self.cache_prefix}:{entry_id}*")
                    await self._clear_cache_pattern(f"{self.cache_prefix}:all*")
                    
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Failed to toggle favorite for entry {entry_id}: {e}")
            raise DatabaseError(f"Failed to toggle favorite: {e}")
    
    async def get_mood_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get mood statistics for the specified period."""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            async with self.db_manager.get_connection() as conn:
                # Mood distribution
                cursor = await conn.execute(
                    """
                    SELECT weather_mood, COUNT(*) as count
                    FROM journal_entries
                    WHERE weather_mood IS NOT NULL
                        AND created_at >= ?
                    GROUP BY weather_mood
                    ORDER BY count DESC
                    """,
                    (start_date.isoformat(),)
                )
                mood_distribution = dict(await cursor.fetchall())
                
                # Mood trends by day
                cursor = await conn.execute(
                    """
                    SELECT DATE(created_at) as date, weather_mood, COUNT(*) as count
                    FROM journal_entries
                    WHERE weather_mood IS NOT NULL
                        AND created_at >= ?
                    GROUP BY DATE(created_at), weather_mood
                    ORDER BY date DESC
                    """,
                    (start_date.isoformat(),)
                )
                mood_trends = await cursor.fetchall()
                
                # Most common mood
                most_common_mood = max(mood_distribution.items(), key=lambda x: x[1])[0] if mood_distribution else None
                
                return {
                    'period_days': days,
                    'mood_distribution': mood_distribution,
                    'mood_trends': mood_trends,
                    'most_common_mood': most_common_mood,
                    'total_entries_with_mood': sum(mood_distribution.values()),
                    'unique_moods': len(mood_distribution)
                }
                
        except Exception as e:
            logger.error(f"Failed to get mood statistics: {e}")
            raise DatabaseError(f"Failed to get mood statistics: {e}")
    
    async def get_location_statistics(self) -> Dict[str, Any]:
        """Get location-based statistics."""
        try:
            async with self.db_manager.get_connection() as conn:
                # Entries by location
                cursor = await conn.execute(
                    """
                    SELECT location_name, COUNT(*) as entry_count,
                           MIN(created_at) as first_entry,
                           MAX(created_at) as latest_entry
                    FROM journal_entries
                    WHERE location_name IS NOT NULL
                    GROUP BY location_name
                    ORDER BY entry_count DESC
                    """
                )
                location_stats = await cursor.fetchall()
                
                # Total unique locations
                cursor = await conn.execute(
                    "SELECT COUNT(DISTINCT location_name) FROM journal_entries WHERE location_name IS NOT NULL"
                )
                unique_locations = (await cursor.fetchone())[0]
                
                return {
                    'location_stats': location_stats,
                    'unique_locations': unique_locations,
                    'most_frequent_location': location_stats[0] if location_stats else None
                }
                
        except Exception as e:
            logger.error(f"Failed to get location statistics: {e}")
            raise DatabaseError(f"Failed to get location statistics: {e}")
    
    async def get_writing_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get writing pattern statistics."""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            async with self.db_manager.get_connection() as conn:
                # Writing frequency by day
                cursor = await conn.execute(
                    """
                    SELECT DATE(created_at) as date, COUNT(*) as entries,
                           AVG(LENGTH(content)) as avg_length
                    FROM journal_entries
                    WHERE created_at >= ?
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                    """,
                    (start_date.isoformat(),)
                )
                daily_stats = await cursor.fetchall()
                
                # Overall statistics
                cursor = await conn.execute(
                    """
                    SELECT COUNT(*) as total_entries,
                           AVG(LENGTH(content)) as avg_content_length,
                           MAX(LENGTH(content)) as max_content_length,
                           MIN(LENGTH(content)) as min_content_length,
                           COUNT(DISTINCT entry_type) as entry_types
                    FROM journal_entries
                    WHERE created_at >= ?
                    """,
                    (start_date.isoformat(),)
                )
                overall_stats = await cursor.fetchone()
                
                # Entry type distribution
                cursor = await conn.execute(
                    """
                    SELECT entry_type, COUNT(*) as count
                    FROM journal_entries
                    WHERE created_at >= ?
                    GROUP BY entry_type
                    ORDER BY count DESC
                    """,
                    (start_date.isoformat(),)
                )
                entry_type_distribution = dict(await cursor.fetchall())
                
                return {
                    'period_days': days,
                    'daily_stats': daily_stats,
                    'total_entries': overall_stats[0],
                    'avg_content_length': round(overall_stats[1] or 0, 2),
                    'max_content_length': overall_stats[2] or 0,
                    'min_content_length': overall_stats[3] or 0,
                    'entry_types_used': overall_stats[4] or 0,
                    'entry_type_distribution': entry_type_distribution,
                    'avg_entries_per_day': round((overall_stats[0] or 0) / days, 2)
                }
                
        except Exception as e:
            logger.error(f"Failed to get writing statistics: {e}")
            raise DatabaseError(f"Failed to get writing statistics: {e}")
    
    async def validate_entry(self, model: JournalEntryModel) -> List[str]:
        """Validate journal entry data."""
        errors = []
        
        # Required fields
        if not model.title or not model.title.strip():
            errors.append("Entry title is required")
        
        if not model.content or not model.content.strip():
            errors.append("Entry content is required")
        
        # Title length validation
        if len(model.title) > 200:
            errors.append("Title must be 200 characters or less")
        
        # Content length validation
        if len(model.content) > 50000:
            errors.append("Content must be 50,000 characters or less")
        
        # Entry type validation
        valid_types = [e.value for e in JournalEntryType]
        if model.entry_type and model.entry_type not in valid_types:
            errors.append(f"Invalid entry type. Must be one of: {', '.join(valid_types)}")
        
        # Weather mood validation
        if model.weather_mood:
            valid_moods = [m.value for m in WeatherMood]
            if model.weather_mood not in valid_moods:
                errors.append(f"Invalid weather mood. Must be one of: {', '.join(valid_moods)}")
        
        # Coordinate validation
        if model.latitude is not None and not (-90 <= model.latitude <= 90):
            errors.append("Latitude must be between -90 and 90")
        
        if model.longitude is not None and not (-180 <= model.longitude <= 180):
            errors.append("Longitude must be between -180 and 180")
        
        # Tags validation
        if model.tags:
            for tag in model.tags:
                if not isinstance(tag, str) or not tag.strip():
                    errors.append("All tags must be non-empty strings")
                    break
                if len(tag) > 50:
                    errors.append("Tags must be 50 characters or less")
                    break
        
        return errors
    
    async def create_with_validation(self, model: JournalEntryModel) -> JournalEntryModel:
        """Create a new journal entry with validation."""
        errors = await self.validate_entry(model)
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")
        
        return await self.create(model)
    
    async def update_with_validation(self, model: JournalEntryModel) -> JournalEntryModel:
        """Update a journal entry with validation."""
        errors = await self.validate_entry(model)
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")
        
        return await self.update(model)


async def create_journal_repository(
    db_manager: DatabaseConnectionManager,
    redis_manager: RedisConnectionManager
) -> JournalRepository:
    """Factory function to create a JournalRepository."""
    return JournalRepository(db_manager, redis_manager)