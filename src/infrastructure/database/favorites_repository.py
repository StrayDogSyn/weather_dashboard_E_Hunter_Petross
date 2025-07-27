"""Repository implementation for favorite locations with caching."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...shared.exceptions import DatabaseError, ValidationError
from .base_repository import BaseRepository
from .connection_manager import DatabaseConnectionManager, RedisConnectionManager
from .models import FavoriteLocationModel

logger = logging.getLogger(__name__)


class FavoritesRepository(BaseRepository[FavoriteLocationModel]):
    """Repository for managing favorite weather locations."""

    def __init__(
        self,
        db_manager: DatabaseConnectionManager,
        redis_manager: RedisConnectionManager,
    ):
        super().__init__(db_manager, redis_manager, "favorite_locations", "favorites")

    def _get_select_query(self) -> str:
        """Get the SELECT query for fetching records."""
        return """
        SELECT id, name, latitude, longitude, country, state, timezone,
               is_default, display_order, tags, notes, created_at, updated_at,
               last_accessed, access_count
        FROM favorite_locations
        """

    def _get_insert_query(self) -> str:
        """Get the INSERT query for creating records."""
        return """
        INSERT INTO favorite_locations (
            name, latitude, longitude, country, state, timezone,
            is_default, display_order, tags, notes, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

    def _get_update_query(self) -> str:
        """Get the UPDATE query for modifying records."""
        return """
        UPDATE favorite_locations SET
            name = ?, latitude = ?, longitude = ?, country = ?, state = ?,
            timezone = ?, is_default = ?, display_order = ?, tags = ?,
            notes = ?, updated_at = ?
        WHERE id = ?
        """

    def _extract_model_from_row(self, row: tuple) -> FavoriteLocationModel:
        """Extract model from database row."""
        return FavoriteLocationModel(
            id=row[0],
            name=row[1],
            latitude=row[2],
            longitude=row[3],
            country=row[4],
            state=row[5],
            timezone=row[6],
            is_default=bool(row[7]),
            display_order=row[8],
            tags=self._deserialize_json_field(row[9], []),
            notes=row[10],
            created_at=self._parse_datetime(row[11]),
            updated_at=self._parse_datetime(row[12]),
            last_accessed=self._parse_datetime(row[13]),
            access_count=row[14] or 0,
        )

    def _get_insert_values(self, model: FavoriteLocationModel) -> tuple:
        """Get values for INSERT query."""
        now = datetime.now()
        return (
            model.name,
            model.latitude,
            model.longitude,
            model.country,
            model.state,
            model.timezone,
            model.is_default,
            model.display_order,
            self._serialize_json_field(model.tags),
            model.notes,
            now.isoformat(),
            now.isoformat(),
        )

    def _get_update_values(self, model: FavoriteLocationModel) -> tuple:
        """Get values for UPDATE query."""
        return (
            model.name,
            model.latitude,
            model.longitude,
            model.country,
            model.state,
            model.timezone,
            model.is_default,
            model.display_order,
            self._serialize_json_field(model.tags),
            model.notes,
            datetime.now().isoformat(),
            model.id,
        )

    async def get_by_coordinates(
        self, latitude: float, longitude: float, tolerance: float = 0.001
    ) -> Optional[FavoriteLocationModel]:
        """Find favorite location by coordinates with tolerance."""
        cache_key = f"{self.cache_prefix}:coords:{latitude}:{longitude}:{tolerance}"

        try:
            # Check cache first
            cached = await self._get_from_cache(cache_key)
            if cached:
                return cached

            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE ABS(latitude - ?) <= ? AND ABS(longitude - ?) <= ?
                    ORDER BY
                        (ABS(latitude - ?) + ABS(longitude - ?)) ASC
                    LIMIT 1
                    """,
                    (latitude, tolerance, longitude, tolerance, latitude, longitude),
                )
                row = await cursor.fetchone()

                if row:
                    model = self._extract_model_from_row(row)
                    await self._set_cache(cache_key, model)
                    return model

                return None

        except Exception as e:
            logger.error(
                f"Failed to get favorite by coordinates ({latitude}, {longitude}): {e}"
            )
            raise DatabaseError(f"Failed to get favorite by coordinates: {e}")

    async def get_default_location(self) -> Optional[FavoriteLocationModel]:
        """Get the default favorite location."""
        cache_key = f"{self.cache_prefix}:default"

        try:
            # Check cache first
            cached = await self._get_from_cache(cache_key)
            if cached:
                return cached

            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE is_default = TRUE
                    ORDER BY display_order ASC
                    LIMIT 1
                    """
                )
                row = await cursor.fetchone()

                if row:
                    model = self._extract_model_from_row(row)
                    await self._set_cache(cache_key, model)
                    return model

                return None

        except Exception as e:
            logger.error(f"Failed to get default location: {e}")
            raise DatabaseError(f"Failed to get default location: {e}")

    async def set_default_location(self, location_id: int) -> bool:
        """Set a location as the default (unsets others)."""
        try:
            async with self.db_manager.get_transaction() as conn:
                # First, unset all default flags
                await conn.execute(
                    "UPDATE favorite_locations SET is_default = FALSE, updated_at = ?",
                    (datetime.now().isoformat(),),
                )

                # Set the new default
                cursor = await conn.execute(
                    "UPDATE favorite_locations SET is_default = TRUE, updated_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), location_id),
                )

                if cursor.rowcount == 0:
                    return False

                await conn.commit()

                # Clear related caches
                await self._clear_cache_pattern(f"{self.cache_prefix}:default*")
                await self._clear_cache_pattern(f"{self.cache_prefix}:all*")
                await self._clear_cache_pattern(f"{self.cache_prefix}:ordered*")

                logger.info(f"Set location {location_id} as default")
                return True

        except Exception as e:
            logger.error(f"Failed to set default location {location_id}: {e}")
            raise DatabaseError(f"Failed to set default location: {e}")

    async def get_by_display_order(self) -> List[FavoriteLocationModel]:
        """Get all favorites ordered by display_order."""
        cache_key = f"{self.cache_prefix}:ordered"

        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached

            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    ORDER BY display_order ASC, name ASC
                    """
                )
                rows = await cursor.fetchall()

                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models)
                return models

        except Exception as e:
            logger.error(f"Failed to get favorites by display order: {e}")
            raise DatabaseError(f"Failed to get favorites by display order: {e}")

    async def update_display_order(
        self, location_orders: List[tuple[int, int]]
    ) -> bool:
        """Update display order for multiple locations.

        Args:
            location_orders: List of (location_id, new_order) tuples
        """
        try:
            async with self.db_manager.get_transaction() as conn:
                for location_id, new_order in location_orders:
                    await conn.execute(
                        "UPDATE favorite_locations SET display_order = ?, updated_at = ? WHERE id = ?",
                        (new_order, datetime.now().isoformat(), location_id),
                    )

                await conn.commit()

                # Clear related caches
                await self._clear_cache_pattern(f"{self.cache_prefix}:*")

                logger.info(
                    f"Updated display order for {len(location_orders)} locations"
                )
                return True

        except Exception as e:
            logger.error(f"Failed to update display order: {e}")
            raise DatabaseError(f"Failed to update display order: {e}")

    async def search_by_name(
        self, query: str, limit: int = 10
    ) -> List[FavoriteLocationModel]:
        """Search favorites by name (case-insensitive)."""
        cache_key = f"{self.cache_prefix}:search:{query.lower()}:{limit}"

        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached

            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE LOWER(name) LIKE ? OR LOWER(country) LIKE ? OR LOWER(state) LIKE ?
                    ORDER BY
                        CASE
                            WHEN LOWER(name) = LOWER(?) THEN 1
                            WHEN LOWER(name) LIKE ? THEN 2
                            ELSE 3
                        END,
                        name ASC
                    LIMIT ?
                    """,
                    (
                        f"%{query.lower()}%",
                        f"%{query.lower()}%",
                        f"%{query.lower()}%",
                        query.lower(),
                        f"{query.lower()}%",
                        limit,
                    ),
                )
                rows = await cursor.fetchall()

                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(
                    cache_key, models, ttl=300
                )  # Shorter TTL for search results
                return models

        except Exception as e:
            logger.error(f"Failed to search favorites by name '{query}': {e}")
            raise DatabaseError(f"Failed to search favorites: {e}")

    async def get_by_tags(
        self, tags: List[str], match_all: bool = False
    ) -> List[FavoriteLocationModel]:
        """Get favorites that have any or all of the specified tags."""
        cache_key = f"{self.cache_prefix}:tags:{'_'.join(sorted(tags))}:{match_all}"

        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached

            # Get all favorites and filter by tags in Python (SQLite JSON handling is limited)
            all_favorites = await self.get_all()

            if match_all:
                # Location must have ALL specified tags
                filtered = [
                    fav for fav in all_favorites if all(tag in fav.tags for tag in tags)
                ]
            else:
                # Location must have ANY of the specified tags
                filtered = [
                    fav for fav in all_favorites if any(tag in fav.tags for tag in tags)
                ]

            await self._set_list_cache(cache_key, filtered, ttl=300)
            return filtered

        except Exception as e:
            logger.error(f"Failed to get favorites by tags {tags}: {e}")
            raise DatabaseError(f"Failed to get favorites by tags: {e}")

    async def update_access_info(self, location_id: int) -> bool:
        """Update last accessed time and increment access count."""
        try:
            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    """
                    UPDATE favorite_locations
                    SET last_accessed = ?, access_count = access_count + 1, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        datetime.now().isoformat(),
                        datetime.now().isoformat(),
                        location_id,
                    ),
                )

                if cursor.rowcount > 0:
                    await conn.commit()

                    # Clear cache for this specific location
                    await self._clear_cache_pattern(
                        f"{self.cache_prefix}:{location_id}*"
                    )
                    await self._clear_cache_pattern(f"{self.cache_prefix}:all*")

                    return True

                return False

        except Exception as e:
            logger.error(
                f"Failed to update access info for location {location_id}: {e}"
            )
            raise DatabaseError(f"Failed to update access info: {e}")

    async def get_most_accessed(self, limit: int = 5) -> List[FavoriteLocationModel]:
        """Get most frequently accessed favorite locations."""
        cache_key = f"{self.cache_prefix}:most_accessed:{limit}"

        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached

            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE access_count > 0
                    ORDER BY access_count DESC, last_accessed DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = await cursor.fetchall()

                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(
                    cache_key, models, ttl=600
                )  # 10 minute cache
                return models

        except Exception as e:
            logger.error(f"Failed to get most accessed favorites: {e}")
            raise DatabaseError(f"Failed to get most accessed favorites: {e}")

    async def get_recently_accessed(
        self, limit: int = 5
    ) -> List[FavoriteLocationModel]:
        """Get recently accessed favorite locations."""
        cache_key = f"{self.cache_prefix}:recently_accessed:{limit}"

        try:
            # Check cache first
            cached = await self._get_list_from_cache(cache_key)
            if cached:
                return cached

            async with self.db_manager.get_connection() as conn:
                cursor = await conn.execute(
                    f"""
                    {self._get_select_query()}
                    WHERE last_accessed IS NOT NULL
                    ORDER BY last_accessed DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                rows = await cursor.fetchall()

                models = [self._extract_model_from_row(row) for row in rows]
                await self._set_list_cache(cache_key, models, ttl=300)  # 5 minute cache
                return models

        except Exception as e:
            logger.error(f"Failed to get recently accessed favorites: {e}")
            raise DatabaseError(f"Failed to get recently accessed favorites: {e}")

    async def validate_location(self, model: FavoriteLocationModel) -> List[str]:
        """Validate favorite location data."""
        errors = []

        # Required fields
        if not model.name or not model.name.strip():
            errors.append("Location name is required")

        if not model.country or not model.country.strip():
            errors.append("Country is required")

        # Coordinate validation
        if not (-90 <= model.latitude <= 90):
            errors.append("Latitude must be between -90 and 90")

        if not (-180 <= model.longitude <= 180):
            errors.append("Longitude must be between -180 and 180")

        # Check for duplicate coordinates (within tolerance)
        existing = await self.get_by_coordinates(model.latitude, model.longitude, 0.001)
        if existing and existing.id != model.id:
            errors.append(
                f"Location with similar coordinates already exists: {existing.name}"
            )

        # Display order validation
        if model.display_order < 0:
            errors.append("Display order must be non-negative")

        # Tags validation
        if model.tags:
            for tag in model.tags:
                if not isinstance(tag, str) or not tag.strip():
                    errors.append("All tags must be non-empty strings")
                    break

        return errors

    async def create_with_validation(
        self, model: FavoriteLocationModel
    ) -> FavoriteLocationModel:
        """Create a new favorite location with validation."""
        errors = await self.validate_location(model)
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")

        return await self.create(model)

    async def update_with_validation(
        self, model: FavoriteLocationModel
    ) -> FavoriteLocationModel:
        """Update a favorite location with validation."""
        errors = await self.validate_location(model)
        if errors:
            raise ValidationError(f"Validation failed: {'; '.join(errors)}")

        return await self.update(model)

    async def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about favorite locations."""
        try:
            async with self.db_manager.get_connection() as conn:
                # Total count
                cursor = await conn.execute("SELECT COUNT(*) FROM favorite_locations")
                total_count = (await cursor.fetchone())[0]

                # Count by country
                cursor = await conn.execute(
                    "SELECT country, COUNT(*) FROM favorite_locations GROUP BY country ORDER BY COUNT(*) DESC"
                )
                by_country = dict(await cursor.fetchall())

                # Access statistics
                cursor = await conn.execute(
                    "SELECT AVG(access_count), MAX(access_count), COUNT(*) FROM favorite_locations WHERE access_count > 0"
                )
                access_stats = await cursor.fetchone()

                # Most common tags
                all_favorites = await self.get_all()
                tag_counts = {}
                for fav in all_favorites:
                    for tag in fav.tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1

                most_common_tags = sorted(
                    tag_counts.items(), key=lambda x: x[1], reverse=True
                )[:10]

                return {
                    "total_locations": total_count,
                    "locations_by_country": by_country,
                    "average_access_count": round(access_stats[0] or 0, 2),
                    "max_access_count": access_stats[1] or 0,
                    "accessed_locations": access_stats[2] or 0,
                    "most_common_tags": most_common_tags,
                    "total_unique_tags": len(tag_counts),
                }

        except Exception as e:
            logger.error(f"Failed to get favorites statistics: {e}")
            raise DatabaseError(f"Failed to get statistics: {e}")


async def create_favorites_repository(
    db_manager: DatabaseConnectionManager, redis_manager: RedisConnectionManager
) -> FavoritesRepository:
    """Factory function to create a FavoritesRepository."""
    return FavoritesRepository(db_manager, redis_manager)
