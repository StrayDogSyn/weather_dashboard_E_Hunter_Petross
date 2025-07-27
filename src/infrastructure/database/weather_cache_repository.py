"""Repository implementation for weather data caching with TTL and archival."""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import json

from .base_repository import BaseRepository
from .models import WeatherCacheModel
from .connection_manager import DatabaseConnectionManager, RedisConnectionManager
from ...shared.exceptions import DatabaseError, ValidationError


logger = logging.getLogger(__name__)


class WeatherCacheRepository(BaseRepository[WeatherCacheModel]):
    """Repository for managing weather data cache with TTL and archival."""
    
    def __init__(self, db_manager: DatabaseConnectionManager, redis_manager: RedisConnectionManager):
        super().__init__(db_manager, redis_manager, "weather_cache", "weather_cache")
    
    def _get_select_query(self) -> str:
        """Get the SELECT query for fetching records."""
        return """
        SELECT id, cache_key, location_name, latitude, longitude,
               data_type, weather_data, expires_at, created_at, updated_at,
               access_count, last_accessed_at, data_size, is_archival_eligible
        FROM weather_cache
        """
    
    def _get_insert_query(self) -> str:
        """Get the INSERT query for creating records."""
        return """
        INSERT INTO weather_cache (
            cache_key, location_name, latitude, longitude,
            data_type, weather_data, expires_at, created_at, updated_at,
            access_count, last_accessed_at, data_size, is_archival_eligible
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    def _get_update_query(self) -> str:
        """Get the UPDATE query for modifying records."""
        return """
        UPDATE weather_cache SET
            location_name = ?, latitude = ?, longitude = ?,
            data_type = ?, weather_data = ?, expires_at = ?,
            updated_at = ?, access_count = ?, last_accessed_at = ?,
            data_size = ?, is_archival_eligible = ?
        WHERE id = ?
        """
    
    def _extract_model_from_row(self, row: tuple) -> WeatherCacheModel:
        """Extract model from database row."""
        return WeatherCacheModel(
            id=row[0],
            cache_key=row[1],
            location_name=row[2],
            latitude=row[3],
            longitude=row[4],
            data_type=row[5],
            weather_data=self._deserialize_json_field(row[6], {}),
            expires_at=self._parse_datetime(row[7]),
            created_at=self._parse_datetime(row[8]),
            updated_at=self._parse_datetime(row[9]),
            access_count=row[10] or 0,
            last_accessed_at=self._parse_datetime(row[11]) if row[11] else None,
            data_size=row[12] or 0,
            is_archival_eligible=bool(row[13]) if row[13] is not None else False
        )
    
    def _get_insert_values(self, model: WeatherCacheModel) -> tuple:
        """Get values for INSERT query."""
        now = datetime.now()
        data_json = self._serialize_json_field(model.weather_data)
        data_size = len(data_json.encode('utf-8')) if data_json else 0
        
        return (
            model.cache_key,
            model.location_name,
            model.latitude,
            model.longitude,
            model.data_type,
            data_json,
            model.expires_at.isoformat() if model.expires_at else None,
            now.isoformat(),
            now.isoformat(),
            model.access_count or 0,
            model.last_accessed_at.isoformat() if model.last_accessed_at else None,
            data_size,
            model.is_archival_eligible or False
        )
    
    def _get_update_values(self, model: WeatherCacheModel) -> tuple:
        """Get values for UPDATE query."""
        data_json = self._serialize_json_field(model.weather_data)
        data_size = len(data_json.encode('utf-8')) if data_json else 0
        
        return (
            model.location_name,
            model.latitude,
            model.longitude,
            model.data_type,
            data_json,
            model.expires_at.isoformat() if model.expires_at else None,
            datetime.now().isoformat(),
            model.access_count or 0,
            model.last_accessed_at.isoformat() if model.last_accessed_at else None,
            data_size,
            model.is_archival_eligible or False,
            model.id
        )
    
    def _generate_cache_key(self, location_name: str, latitude: float, longitude: float, 
                           data_type: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Generate a unique cache key for weather data."""
        key_data = {
            'location': location_name,
            'lat': round(latitude, 4),
            'lon': round(longitude, 4),
            'type': data_type,
            'params': params or {}
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get_by_cache_key(self, cache_key: str) -> Optional[WeatherCacheModel]:
        """Get weather data by cache key."""
        redis_cache_key = f"{self.cache_prefix}:key:{cache_key}"
        
        try:
            # Check Redis cache first
            cached = await self._get_from_cache(redis_cache_key)
            if cached:
                # Update access statistics
                await self._update_access_stats(cached.id)
                return cached
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"{self._get_select_query()} WHERE cache_key = ? AND (expires_at IS NULL OR expires_at > ?)",
                    (cache_key, datetime.now().isoformat())
                )
                row = await cursor.fetchone()
                
                if row:
                    model = self._extract_model_from_row(row)
                    
                    # Cache in Redis with TTL
                    ttl = self._calculate_redis_ttl(model.expires_at)
                    await self._set_cache(redis_cache_key, model, ttl=ttl)
                    
                    # Update access statistics
                    await self._update_access_stats(model.id)
                    
                    return model
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get weather data by cache key '{cache_key}': {e}")
            raise DatabaseError(f"Failed to get weather data by cache key: {e}")
    
    async def get_by_location(self, location_name: str, data_type: str, 
                             max_age_hours: Optional[int] = None) -> List[WeatherCacheModel]:
        """Get weather data for a location and data type."""
        cache_key = f"{self.cache_prefix}:location:{location_name}:{data_type}:{max_age_hours}"
        
        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached
            
            query = f"{self._get_select_query()} WHERE location_name = ? AND data_type = ?"
            params = [location_name, data_type]
            
            # Add expiration check
            query += " AND (expires_at IS NULL OR expires_at > ?)"
            params.append(datetime.now().isoformat())
            
            # Add max age filter if specified
            if max_age_hours:
                min_created_at = datetime.now() - timedelta(hours=max_age_hours)
                query += " AND created_at >= ?"
                params.append(min_created_at.isoformat())
            
            query += " ORDER BY created_at DESC"
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()
                
                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models, ttl=300)  # 5 minute cache
                return models
                
        except Exception as e:
            logger.error(f"Failed to get weather data by location '{location_name}': {e}")
            raise DatabaseError(f"Failed to get weather data by location: {e}")
    
    async def get_by_coordinates(self, latitude: float, longitude: float, 
                                data_type: str, radius_km: float = 1.0) -> List[WeatherCacheModel]:
        """Get weather data near specific coordinates."""
        try:
            # Use a simple bounding box for proximity search
            # 1 degree ≈ 111 km, so radius in degrees
            radius_deg = radius_km / 111.0
            
            min_lat = latitude - radius_deg
            max_lat = latitude + radius_deg
            min_lon = longitude - radius_deg
            max_lon = longitude + radius_deg
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE data_type = ?
                        AND latitude BETWEEN ? AND ?
                        AND longitude BETWEEN ? AND ?
                        AND (expires_at IS NULL OR expires_at > ?)
                    ORDER BY created_at DESC
                    """,
                    (data_type, min_lat, max_lat, min_lon, max_lon, datetime.now().isoformat())
                )
                rows = await cursor.fetchall()
                
                return [self._extract_model_from_row(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get weather data by coordinates ({latitude}, {longitude}): {e}")
            raise DatabaseError(f"Failed to get weather data by coordinates: {e}")
    
    async def cache_weather_data(self, location_name: str, latitude: float, longitude: float,
                                data_type: str, weather_data: Dict[str, Any], 
                                ttl_hours: int = 1, params: Optional[Dict[str, Any]] = None) -> WeatherCacheModel:
        """Cache weather data with TTL."""
        try:
            cache_key = self._generate_cache_key(location_name, latitude, longitude, data_type, params)
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
            
            # Check if cache entry already exists
            existing = await self.get_by_cache_key(cache_key)
            
            if existing:
                # Update existing entry
                existing.weather_data = weather_data
                existing.expires_at = expires_at
                existing.updated_at = datetime.now()
                
                model = await self.update(existing)
            else:
                # Create new entry
                model = WeatherCacheModel(
                    cache_key=cache_key,
                    location_name=location_name,
                    latitude=latitude,
                    longitude=longitude,
                    data_type=data_type,
                    weather_data=weather_data,
                    expires_at=expires_at,
                    access_count=0,
                    is_archival_eligible=False
                )
                
                model = await self.create(model)
            
            # Cache in Redis with appropriate TTL
            redis_cache_key = f"{self.cache_prefix}:key:{cache_key}"
            redis_ttl = min(ttl_hours * 3600, 86400)  # Max 24 hours in Redis
            await self._set_cache(redis_cache_key, model, ttl=redis_ttl)
            
            return model
            
        except Exception as e:
            logger.error(f"Failed to cache weather data for '{location_name}': {e}")
            raise DatabaseError(f"Failed to cache weather data: {e}")
    
    async def cleanup_expired(self) -> int:
        """Remove expired cache entries."""
        try:
            async with self.db_manager.get_connection() as conn:
                # Get expired entries for logging
                cursor = await conn.execute(
                    "SELECT id, cache_key, location_name FROM weather_cache WHERE expires_at <= ?",
                    (datetime.now().isoformat(),)
                )
                expired_entries = await cursor.fetchall()
                
                # Delete expired entries
                cursor = await conn.execute(
                    "DELETE FROM weather_cache WHERE expires_at <= ?",
                    (datetime.now().isoformat(),)
                )
                
                deleted_count = cursor.rowcount
                await conn.commit()
                
                # Clear related caches
                for entry in expired_entries:
                    await self._clear_cache_pattern(f"{self.cache_prefix}:key:{entry[1]}*")
                
                await self._clear_cache_pattern(f"{self.cache_prefix}:location:*")
                
                logger.info(f"Cleaned up {deleted_count} expired weather cache entries")
                return deleted_count
                
        except Exception as e:
            logger.error(f"Failed to cleanup expired cache entries: {e}")
            raise DatabaseError(f"Failed to cleanup expired cache entries: {e}")
    
    async def archive_old_data(self, days_old: int = 30) -> int:
        """Archive old weather data to archive table."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            async with self.db_manager.get_connection() as conn:
                # Get archival candidates
                cursor = await conn.execute(
                    """
                    SELECT id, cache_key, location_name, latitude, longitude,
                           data_type, weather_data, expires_at, created_at, updated_at,
                           access_count, last_accessed_at, data_size
                    FROM weather_cache
                    WHERE is_archival_eligible = TRUE
                        AND created_at <= ?
                        AND (last_accessed_at IS NULL OR last_accessed_at <= ?)
                    """,
                    (cutoff_date.isoformat(), cutoff_date.isoformat())
                )
                candidates = await cursor.fetchall()
                
                archived_count = 0
                
                for row in candidates:
                    # Insert into archive table
                    cursor = await conn.execute(
                        """
                        INSERT INTO weather_archive (
                            original_id, cache_key, location_name, latitude, longitude,
                            data_type, weather_data, expires_at, created_at, updated_at,
                            access_count, last_accessed_at, data_size, archived_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (*row, datetime.now().isoformat())
                    )
                    
                    # Delete from main cache table
                    cursor = await conn.execute(
                        "DELETE FROM weather_cache WHERE id = ?",
                        (row[0],)
                    )
                    
                    if cursor.rowcount > 0:
                        archived_count += 1
                
                await conn.commit()
                
                # Log archival operation
                if archived_count > 0:
                    await conn.execute(
                        """
                        INSERT INTO weather_cleanup_log (
                            operation_type, records_affected, operation_date, details
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (
                            'archive',
                            archived_count,
                            datetime.now().isoformat(),
                            f"Archived {archived_count} records older than {days_old} days"
                        )
                    )
                    await conn.commit()
                
                # Clear caches
                await self._clear_cache_pattern(f"{self.cache_prefix}:*")
                
                logger.info(f"Archived {archived_count} old weather cache entries")
                return archived_count
                
        except Exception as e:
            logger.error(f"Failed to archive old weather data: {e}")
            raise DatabaseError(f"Failed to archive old weather data: {e}")
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache usage statistics."""
        try:
            async with self.db_manager.get_connection() as conn:
                # Basic statistics
                cursor = await conn.execute(
                    """
                    SELECT COUNT(*) as total_entries,
                           COUNT(CASE WHEN expires_at > ? THEN 1 END) as active_entries,
                           COUNT(CASE WHEN expires_at <= ? THEN 1 END) as expired_entries,
                           AVG(access_count) as avg_access_count,
                           SUM(data_size) as total_data_size,
                           COUNT(DISTINCT location_name) as unique_locations,
                           COUNT(DISTINCT data_type) as unique_data_types
                    FROM weather_cache
                    """,
                    (datetime.now().isoformat(), datetime.now().isoformat())
                )
                basic_stats = await cursor.fetchone()
                
                # Data type distribution
                cursor = await conn.execute(
                    """
                    SELECT data_type, COUNT(*) as count, AVG(data_size) as avg_size
                    FROM weather_cache
                    GROUP BY data_type
                    ORDER BY count DESC
                    """
                )
                data_type_stats = await cursor.fetchall()
                
                # Most accessed locations
                cursor = await conn.execute(
                    """
                    SELECT location_name, SUM(access_count) as total_accesses,
                           COUNT(*) as cache_entries
                    FROM weather_cache
                    GROUP BY location_name
                    ORDER BY total_accesses DESC
                    LIMIT 10
                    """
                )
                top_locations = await cursor.fetchall()
                
                # Cache hit efficiency (from Redis)
                redis_stats = await self.redis_manager.get_info()
                
                return {
                    'total_entries': basic_stats[0] or 0,
                    'active_entries': basic_stats[1] or 0,
                    'expired_entries': basic_stats[2] or 0,
                    'avg_access_count': round(basic_stats[3] or 0, 2),
                    'total_data_size_bytes': basic_stats[4] or 0,
                    'unique_locations': basic_stats[5] or 0,
                    'unique_data_types': basic_stats[6] or 0,
                    'data_type_distribution': [
                        {'type': row[0], 'count': row[1], 'avg_size': round(row[2] or 0, 2)}
                        for row in data_type_stats
                    ],
                    'top_locations': [
                        {'location': row[0], 'total_accesses': row[1], 'cache_entries': row[2]}
                        for row in top_locations
                    ],
                    'redis_memory_usage': redis_stats.get('used_memory_human', 'N/A'),
                    'redis_hit_rate': redis_stats.get('keyspace_hits', 0) / max(redis_stats.get('keyspace_hits', 0) + redis_stats.get('keyspace_misses', 0), 1)
                }
                
        except Exception as e:
            logger.error(f"Failed to get cache statistics: {e}")
            raise DatabaseError(f"Failed to get cache statistics: {e}")
    
    async def _update_access_stats(self, cache_id: int) -> None:
        """Update access statistics for a cache entry."""
        try:
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    """
                    UPDATE weather_cache 
                    SET access_count = access_count + 1, 
                        last_accessed_at = ?
                    WHERE id = ?
                    """,
                    (datetime.now().isoformat(), cache_id)
                )
                await conn.commit()
                
        except Exception as e:
            logger.warning(f"Failed to update access stats for cache entry {cache_id}: {e}")
    
    def _calculate_redis_ttl(self, expires_at: Optional[datetime]) -> Optional[int]:
        """Calculate Redis TTL based on database expiration."""
        if not expires_at:
            return 3600  # Default 1 hour
        
        ttl_seconds = int((expires_at - datetime.now()).total_seconds())
        return max(60, min(ttl_seconds, 86400))  # Between 1 minute and 24 hours
    
    async def get_archival_candidates(self, days_old: int = 30, min_access_count: int = 0) -> List[WeatherCacheModel]:
        """Get entries that are candidates for archival."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE is_archival_eligible = TRUE
                        AND created_at <= ?
                        AND access_count >= ?
                        AND (last_accessed_at IS NULL OR last_accessed_at <= ?)
                    ORDER BY created_at ASC
                    """,
                    (cutoff_date.isoformat(), min_access_count, cutoff_date.isoformat())
                )
                rows = await cursor.fetchall()
                
                return [self._extract_model_from_row(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get archival candidates: {e}")
            raise DatabaseError(f"Failed to get archival candidates: {e}")
    
    async def validate_cache_entry(self, model: WeatherCacheModel) -> List[str]:
        """Validate weather cache entry data."""
        errors = []
        
        # Required fields
        if not model.cache_key or not model.cache_key.strip():
            errors.append("Cache key is required")
        
        if not model.location_name or not model.location_name.strip():
            errors.append("Location name is required")
        
        if not model.data_type or not model.data_type.strip():
            errors.append("Data type is required")
        
        if not model.weather_data:
            errors.append("Weather data is required")
        
        # Coordinate validation
        if model.latitude is not None and not (-90 <= model.latitude <= 90):
            errors.append("Latitude must be between -90 and 90")
        
        if model.longitude is not None and not (-180 <= model.longitude <= 180):
            errors.append("Longitude must be between -180 and 180")
        
        # Data type validation
        valid_data_types = ['current', 'forecast', 'historical', 'alerts', 'radar']
        if model.data_type not in valid_data_types:
            errors.append(f"Invalid data type. Must be one of: {', '.join(valid_data_types)}")
        
        # Expiration validation
        if model.expires_at and model.expires_at <= datetime.now():
            errors.append("Expiration time must be in the future")
        
        # Access count validation
        if model.access_count is not None and model.access_count < 0:
            errors.append("Access count cannot be negative")
        
        return errors
    
    async def create_with_validation(self, model: WeatherCacheModel) -> WeatherCacheModel:
        """Create a new cache entry with validation."""
        errors = await self.validate_cache_entry(model)
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")
        
        return await self.create(model)
    
    async def update_with_validation(self, model: WeatherCacheModel) -> WeatherCacheModel:
        """Update a cache entry with validation."""
        errors = await self.validate_cache_entry(model)
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")
        
        return await self.update(model)


async def create_weather_cache_repository(
    db_manager: DatabaseConnectionManager,
    redis_manager: RedisConnectionManager
) -> WeatherCacheRepository:
    """Factory function to create a WeatherCacheRepository."""
    return WeatherCacheRepository(db_manager, redis_manager)