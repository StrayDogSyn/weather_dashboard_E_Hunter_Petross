"""Base repository class with common CRUD operations and caching."""

import asyncio
import json
import logging
import sqlite3
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import aiosqlite
import redis.asyncio as redis

from ...shared.exceptions import CacheError, RepositoryError
from .connection_manager import DatabaseConnectionManager, RedisConnectionManager

logger = logging.getLogger(__name__)

# Generic type for model classes
T = TypeVar("T")


class BaseRepository(Generic[T], ABC):
    """Base repository class implementing repository pattern with caching."""

    def __init__(
        self,
        db_manager: DatabaseConnectionManager,
        redis_manager: RedisConnectionManager,
        model_class: Type[T],
        table_name: str,
        cache_prefix: str,
        default_ttl: int = 3600,  # 1 hour default TTL
    ):
        self.db_manager = db_manager
        self.redis_manager = redis_manager
        self.model_class = model_class
        self.table_name = table_name
        self.cache_prefix = cache_prefix
        self.default_ttl = default_ttl
        self._redis_client: Optional[redis.Redis] = None

    async def _get_redis_client(self) -> redis.Redis:
        """Get Redis client with lazy initialization."""
        if self._redis_client is None:
            self._redis_client = await self.redis_manager.get_client()
        return self._redis_client

    def _get_cache_key(self, identifier: Union[str, int]) -> str:
        """Generate cache key for an entity."""
        return f"{self.cache_prefix}:{identifier}"

    def _get_list_cache_key(self, query_hash: str = "all") -> str:
        """Generate cache key for entity lists."""
        return f"{self.cache_prefix}:list:{query_hash}"

    async def _serialize_for_cache(self, obj: T) -> str:
        """Serialize object for Redis storage."""
        try:
            if is_dataclass(obj):
                data = asdict(obj)
            elif hasattr(obj, "__dict__"):
                data = obj.__dict__
            else:
                data = obj

            # Handle datetime objects
            def datetime_handler(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            return json.dumps(data, default=datetime_handler)
        except Exception as e:
            logger.error(f"Error serializing object for cache: {e}")
            raise CacheError(f"Failed to serialize object: {e}")

    async def _deserialize_from_cache(self, data: str) -> T:
        """Deserialize object from Redis storage."""
        try:
            obj_data = json.loads(data)
            return await self._create_model_from_dict(obj_data)
        except Exception as e:
            logger.error(f"Error deserializing object from cache: {e}")
            raise CacheError(f"Failed to deserialize object: {e}")

    @abstractmethod
    async def _create_model_from_dict(self, data: Dict[str, Any]) -> T:
        """Create model instance from dictionary data."""
        pass

    @abstractmethod
    async def _create_model_from_row(self, row: sqlite3.Row) -> T:
        """Create model instance from database row."""
        pass

    @abstractmethod
    def _get_insert_query(self) -> str:
        """Get SQL INSERT query for this entity type."""
        pass

    @abstractmethod
    def _get_update_query(self) -> str:
        """Get SQL UPDATE query for this entity type."""
        pass

    @abstractmethod
    def _get_select_query(self) -> str:
        """Get SQL SELECT query for this entity type."""
        pass

    @abstractmethod
    def _get_delete_query(self) -> str:
        """Get SQL DELETE query for this entity type."""
        pass

    @abstractmethod
    def _extract_model_values(self, model: T) -> tuple:
        """Extract values from model for database operations."""
        pass

    @abstractmethod
    def _get_model_id(self, model: T) -> Union[str, int]:
        """Get the ID/primary key of a model instance."""
        pass

    async def get_by_id(self, entity_id: Union[str, int]) -> Optional[T]:
        """Get entity by ID with cache-aside pattern."""
        try:
            # Try cache first
            cache_key = self._get_cache_key(entity_id)
            redis_client = await self._get_redis_client()

            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for {self.table_name}:{entity_id}")
                return await self._deserialize_from_cache(cached_data)

            # Cache miss - fetch from database
            logger.debug(f"Cache miss for {self.table_name}:{entity_id}")
            async with self.db_manager.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = await conn.execute(
                    f"{self._get_select_query()} WHERE id = ?", (entity_id,)
                )
                row = await cursor.fetchone()

                if row:
                    entity = await self._create_model_from_row(row)

                    # Cache the result
                    serialized = await self._serialize_for_cache(entity)
                    await redis_client.setex(cache_key, self.default_ttl, serialized)

                    return entity

                return None

        except Exception as e:
            logger.error(f"Error getting {self.table_name} by ID {entity_id}: {e}")
            raise RepositoryError(f"Failed to get entity: {e}")

    async def get_all(self, limit: Optional[int] = None, offset: int = 0) -> List[T]:
        """Get all entities with optional pagination."""
        try:
            # Generate cache key based on query parameters
            query_hash = f"limit_{limit}_offset_{offset}"
            cache_key = self._get_list_cache_key(query_hash)
            redis_client = await self._get_redis_client()

            # Try cache first
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for {self.table_name} list query")
                entity_ids = json.loads(cached_data)
                entities = []

                # Fetch individual entities (which may also be cached)
                for entity_id in entity_ids:
                    entity = await self.get_by_id(entity_id)
                    if entity:
                        entities.append(entity)

                return entities

            # Cache miss - fetch from database
            logger.debug(f"Cache miss for {self.table_name} list query")
            query = self._get_select_query()
            params = []

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            if offset > 0:
                query += " OFFSET ?"
                params.append(offset)

            async with self.db_manager.get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()

                entities = []
                entity_ids = []

                for row in rows:
                    entity = await self._create_model_from_row(row)
                    entities.append(entity)
                    entity_ids.append(self._get_model_id(entity))

                    # Cache individual entities
                    cache_key = self._get_cache_key(self._get_model_id(entity))
                    serialized = await self._serialize_for_cache(entity)
                    await redis_client.setex(cache_key, self.default_ttl, serialized)

                # Cache the list of IDs
                list_cache_key = self._get_list_cache_key(query_hash)
                await redis_client.setex(
                    list_cache_key,
                    self.default_ttl // 2,  # Shorter TTL for lists
                    json.dumps(entity_ids),
                )

                return entities

        except Exception as e:
            logger.error(f"Error getting all {self.table_name}: {e}")
            raise RepositoryError(f"Failed to get entities: {e}")

    async def create(self, entity: T) -> T:
        """Create new entity."""
        try:
            async with self.db_manager.get_transaction() as conn:
                cursor = await conn.execute(
                    self._get_insert_query(), self._extract_model_values(entity)
                )

                # Get the created entity ID if it was auto-generated
                if hasattr(entity, "id") and getattr(entity, "id") is None:
                    entity_id = cursor.lastrowid
                    # Update the entity with the new ID
                    if hasattr(entity, "__dict__"):
                        entity.id = entity_id
                    elif is_dataclass(entity):
                        # For dataclasses, we need to create a new instance
                        entity_dict = asdict(entity)
                        entity_dict["id"] = entity_id
                        entity = self.model_class(**entity_dict)

                await conn.commit()

            # Cache the new entity
            redis_client = await self._get_redis_client()
            cache_key = self._get_cache_key(self._get_model_id(entity))
            serialized = await self._serialize_for_cache(entity)
            await redis_client.setex(cache_key, self.default_ttl, serialized)

            # Invalidate list caches
            await self._invalidate_list_caches()

            return entity

        except Exception as e:
            logger.error(f"Error creating {self.table_name}: {e}")
            raise RepositoryError(f"Failed to create entity: {e}")

    async def update(self, entity: T) -> T:
        """Update existing entity."""
        try:
            entity_id = self._get_model_id(entity)

            async with self.db_manager.get_transaction() as conn:
                cursor = await conn.execute(
                    f"{self._get_update_query()} WHERE id = ?",
                    (*self._extract_model_values(entity), entity_id),
                )

                if cursor.rowcount == 0:
                    raise RepositoryError(f"Entity with ID {entity_id} not found")

                await conn.commit()

            # Update cache
            redis_client = await self._get_redis_client()
            cache_key = self._get_cache_key(entity_id)
            serialized = await self._serialize_for_cache(entity)
            await redis_client.setex(cache_key, self.default_ttl, serialized)

            # Invalidate list caches
            await self._invalidate_list_caches()

            return entity

        except Exception as e:
            logger.error(f"Error updating {self.table_name}: {e}")
            raise RepositoryError(f"Failed to update entity: {e}")

    async def delete(self, entity_id: Union[str, int]) -> bool:
        """Delete entity by ID."""
        try:
            async with self.db_manager.get_transaction() as conn:
                cursor = await conn.execute(self._get_delete_query(), (entity_id,))

                if cursor.rowcount == 0:
                    return False

                await conn.commit()

            # Remove from cache
            redis_client = await self._get_redis_client()
            cache_key = self._get_cache_key(entity_id)
            await redis_client.delete(cache_key)

            # Invalidate list caches
            await self._invalidate_list_caches()

            return True

        except Exception as e:
            logger.error(f"Error deleting {self.table_name} with ID {entity_id}: {e}")
            raise RepositoryError(f"Failed to delete entity: {e}")

    async def exists(self, entity_id: Union[str, int]) -> bool:
        """Check if entity exists."""
        try:
            # Check cache first
            redis_client = await self._get_redis_client()
            cache_key = self._get_cache_key(entity_id)

            if await redis_client.exists(cache_key):
                return True

            # Check database
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"SELECT 1 FROM {self.table_name} WHERE id = ?", (entity_id,)
                )
                row = await cursor.fetchone()
                return row is not None

        except Exception as e:
            logger.error(
                f"Error checking existence of {self.table_name} with ID {entity_id}: {e}"
            )
            raise RepositoryError(f"Failed to check entity existence: {e}")

    async def count(self) -> int:
        """Get total count of entities."""
        try:
            # Try cache first
            redis_client = await self._get_redis_client()
            count_cache_key = f"{self.cache_prefix}:count"

            cached_count = await redis_client.get(count_cache_key)
            if cached_count:
                return int(cached_count)

            # Cache miss - query database
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(f"SELECT COUNT(*) FROM {self.table_name}")
                row = await cursor.fetchone()
                count = row[0] if row else 0

                # Cache the count with shorter TTL
                await redis_client.setex(
                    count_cache_key,
                    self.default_ttl // 4,  # Shorter TTL for counts
                    str(count),
                )

                return count

        except Exception as e:
            logger.error(f"Error counting {self.table_name}: {e}")
            raise RepositoryError(f"Failed to count entities: {e}")

    async def clear_cache(self, entity_id: Optional[Union[str, int]] = None) -> None:
        """Clear cache for specific entity or all entities."""
        try:
            redis_client = await self._get_redis_client()

            if entity_id:
                # Clear specific entity cache
                cache_key = self._get_cache_key(entity_id)
                await redis_client.delete(cache_key)
            else:
                # Clear all caches for this repository
                pattern = f"{self.cache_prefix}:*"
                keys = await redis_client.keys(pattern)
                if keys:
                    await redis_client.delete(*keys)

        except Exception as e:
            logger.error(f"Error clearing cache for {self.table_name}: {e}")
            raise CacheError(f"Failed to clear cache: {e}")

    async def _invalidate_list_caches(self) -> None:
        """Invalidate all list caches for this repository."""
        try:
            redis_client = await self._get_redis_client()
            pattern = f"{self.cache_prefix}:list:*"
            keys = await redis_client.keys(pattern)
            if keys:
                await redis_client.delete(*keys)

            # Also invalidate count cache
            count_cache_key = f"{self.cache_prefix}:count"
            await redis_client.delete(count_cache_key)

        except Exception as e:
            logger.warning(f"Error invalidating list caches for {self.table_name}: {e}")

    async def refresh_cache(self, entity_id: Union[str, int]) -> Optional[T]:
        """Force refresh cache for specific entity."""
        try:
            # Clear existing cache
            await self.clear_cache(entity_id)

            # Fetch fresh data from database
            return await self.get_by_id(entity_id)

        except Exception as e:
            logger.error(
                f"Error refreshing cache for {self.table_name}:{entity_id}: {e}"
            )
            raise CacheError(f"Failed to refresh cache: {e}")

    async def batch_get(self, entity_ids: List[Union[str, int]]) -> List[T]:
        """Get multiple entities by IDs efficiently."""
        try:
            entities = []
            missing_ids = []

            redis_client = await self._get_redis_client()

            # Try to get from cache first
            for entity_id in entity_ids:
                cache_key = self._get_cache_key(entity_id)
                cached_data = await redis_client.get(cache_key)

                if cached_data:
                    entity = await self._deserialize_from_cache(cached_data)
                    entities.append(entity)
                else:
                    missing_ids.append(entity_id)

            # Fetch missing entities from database
            if missing_ids:
                placeholders = ",".join("?" * len(missing_ids))
                query = f"{self._get_select_query()} WHERE id IN ({placeholders})"

                async with self.db_manager.get_connection() as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = await conn.execute(query, missing_ids)
                    rows = await cursor.fetchall()

                    for row in rows:
                        entity = await self._create_model_from_row(row)
                        entities.append(entity)

                        # Cache the entity
                        cache_key = self._get_cache_key(self._get_model_id(entity))
                        serialized = await self._serialize_for_cache(entity)
                        await redis_client.setex(
                            cache_key, self.default_ttl, serialized
                        )

            return entities

        except Exception as e:
            logger.error(f"Error batch getting {self.table_name}: {e}")
            raise RepositoryError(f"Failed to batch get entities: {e}")

    async def search(self, **criteria) -> List[T]:
        """Search entities by criteria. Override in concrete repositories."""
        raise NotImplementedError(
            "Search method must be implemented in concrete repositories"
        )

    async def close(self) -> None:
        """Close repository resources."""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
