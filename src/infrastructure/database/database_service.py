"""Database service that orchestrates all repositories and provides unified data access."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ...shared.exceptions import ConfigurationError, DatabaseError
from .connection_manager import (
    ConnectionManagerFactory,
    DatabaseConnectionManager,
    RedisConnectionManager,
)
from .favorites_repository import FavoritesRepository, create_favorites_repository
from .journal_repository import JournalRepository, create_journal_repository
from .migration_manager import MigrationManager
from .settings_repository import SettingsRepository, create_settings_repository
from .weather_cache_repository import (
    WeatherCacheRepository,
    create_weather_cache_repository,
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """Unified database service that manages all repositories and connections."""

    def __init__(
        self,
        db_manager: DatabaseConnectionManager,
        redis_manager: RedisConnectionManager,
        migration_manager: MigrationManager,
    ):
        self.db_manager = db_manager
        self.redis_manager = redis_manager
        self.migration_manager = migration_manager

        # Initialize repositories
        self._favorites_repo: Optional[FavoritesRepository] = None
        self._journal_repo: Optional[JournalRepository] = None
        self._settings_repo: Optional[SettingsRepository] = None
        self._weather_cache_repo: Optional[WeatherCacheRepository] = None

        self._initialized = False

    async def initialize(self, run_migrations: bool = True) -> None:
        """Initialize the database service and all repositories."""
        try:
            logger.info("Initializing database service...")

            # Initialize connection managers
            await self.db_manager.initialize()
            await self.redis_manager.initialize()

            # Run migrations if requested
            if run_migrations:
                logger.info("Running database migrations...")
                await self.migration_manager.apply_pending_migrations()

            # Initialize repositories
            self._favorites_repo = await create_favorites_repository(
                self.db_manager, self.redis_manager
            )
            self._journal_repo = await create_journal_repository(
                self.db_manager, self.redis_manager
            )
            self._settings_repo = await create_settings_repository(
                self.db_manager, self.redis_manager
            )
            self._weather_cache_repo = await create_weather_cache_repository(
                self.db_manager, self.redis_manager
            )

            self._initialized = True
            logger.info("Database service initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database service: {e}")
            raise DatabaseError(f"Database service initialization failed: {e}")

    async def shutdown(self) -> None:
        """Shutdown the database service and close all connections."""
        try:
            logger.info("Shutting down database service...")

            # Close connection managers
            if hasattr(self.db_manager, "close"):
                await self.db_manager.close()

            if hasattr(self.redis_manager, "close"):
                await self.redis_manager.close()

            self._initialized = False
            logger.info("Database service shutdown complete")

        except Exception as e:
            logger.error(f"Error during database service shutdown: {e}")

    def _ensure_initialized(self) -> None:
        """Ensure the service is initialized before use."""
        if not self._initialized:
            raise DatabaseError(
                "Database service not initialized. Call initialize() first."
            )

    @property
    def favorites(self) -> FavoritesRepository:
        """Get the favorites repository."""
        self._ensure_initialized()
        if not self._favorites_repo:
            raise DatabaseError("Favorites repository not available")
        return self._favorites_repo

    @property
    def journal(self) -> JournalRepository:
        """Get the journal repository."""
        self._ensure_initialized()
        if not self._journal_repo:
            raise DatabaseError("Journal repository not available")
        return self._journal_repo

    @property
    def settings(self) -> SettingsRepository:
        """Get the settings repository."""
        self._ensure_initialized()
        if not self._settings_repo:
            raise DatabaseError("Settings repository not available")
        return self._settings_repo

    @property
    def weather_cache(self) -> WeatherCacheRepository:
        """Get the weather cache repository."""
        self._ensure_initialized()
        if not self._weather_cache_repo:
            raise DatabaseError("Weather cache repository not available")
        return self._weather_cache_repo

    async def health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check of all database components."""
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "components": {},
            }

            # Check SQLite database
            try:
                db_health = await self.db_manager.health_check()
                health_status["components"]["sqlite"] = {
                    "status": "healthy",
                    "details": db_health,
                }
            except Exception as e:
                health_status["components"]["sqlite"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_status["overall_status"] = "degraded"

            # Check Redis
            try:
                redis_health = await self.redis_manager.health_check()
                health_status["components"]["redis"] = {
                    "status": "healthy",
                    "details": redis_health,
                }
            except Exception as e:
                health_status["components"]["redis"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_status["overall_status"] = "degraded"

            # Check migration status
            try:
                migration_status = await self.migration_manager.get_migration_status()
                pending_count = len(migration_status.get("pending_migrations", []))

                health_status["components"]["migrations"] = {
                    "status": "healthy" if pending_count == 0 else "warning",
                    "pending_migrations": pending_count,
                    "details": migration_status,
                }

                if pending_count > 0:
                    health_status["overall_status"] = "warning"

            except Exception as e:
                health_status["components"]["migrations"] = {
                    "status": "unhealthy",
                    "error": str(e),
                }
                health_status["overall_status"] = "degraded"

            # Test repository operations
            if self._initialized:
                try:
                    # Test a simple operation on each repository
                    await self.settings.get_categories()
                    health_status["components"]["repositories"] = {
                        "status": "healthy",
                        "message": "All repositories operational",
                    }
                except Exception as e:
                    health_status["components"]["repositories"] = {
                        "status": "unhealthy",
                        "error": str(e),
                    }
                    health_status["overall_status"] = "degraded"

            return health_status

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "unhealthy",
                "error": str(e),
            }

    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics."""
        try:
            self._ensure_initialized()

            stats = {
                "timestamp": datetime.now().isoformat(),
                "database": {},
                "cache": {},
                "repositories": {},
            }

            # Database statistics
            try:
                db_info = await self.db_manager.get_database_info()
                stats["database"] = db_info
            except Exception as e:
                logger.warning(f"Failed to get database statistics: {e}")
                stats["database"] = {"error": str(e)}

            # Redis statistics
            try:
                redis_info = await self.redis_manager.get_info()
                memory_stats = await self.redis_manager.get_memory_usage()
                stats["cache"] = {
                    "redis_info": redis_info,
                    "memory_usage": memory_stats,
                }
            except Exception as e:
                logger.warning(f"Failed to get Redis statistics: {e}")
                stats["cache"] = {"error": str(e)}

            # Repository statistics
            try:
                # Favorites statistics
                favorites_count = await self.favorites.count()
                stats["repositories"]["favorites"] = {
                    "total_locations": favorites_count
                }

                # Journal statistics
                journal_count = await self.journal.count()
                mood_stats = await self.journal.get_mood_statistics()
                stats["repositories"]["journal"] = {
                    "total_entries": journal_count,
                    "mood_statistics": mood_stats,
                }

                # Settings statistics
                settings_count = await self.settings.count()
                categories = await self.settings.get_categories()
                stats["repositories"]["settings"] = {
                    "total_settings": settings_count,
                    "categories": categories,
                }

                # Weather cache statistics
                cache_stats = await self.weather_cache.get_cache_statistics()
                stats["repositories"]["weather_cache"] = cache_stats

            except Exception as e:
                logger.warning(f"Failed to get repository statistics: {e}")
                stats["repositories"] = {"error": str(e)}

            return stats

        except Exception as e:
            logger.error(f"Failed to get system statistics: {e}")
            raise DatabaseError(f"Failed to get system statistics: {e}")

    async def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data across all repositories."""
        try:
            self._ensure_initialized()

            cleanup_results = {
                "weather_cache_expired": 0,
                "weather_cache_archived": 0,
                "redis_keys_cleaned": 0,
            }

            # Clean up expired weather cache entries
            try:
                expired_count = await self.weather_cache.cleanup_expired()
                cleanup_results["weather_cache_expired"] = expired_count
                logger.info(f"Cleaned up {expired_count} expired weather cache entries")
            except Exception as e:
                logger.warning(f"Failed to cleanup expired weather cache: {e}")

            # Archive old weather data
            try:
                archived_count = await self.weather_cache.archive_old_data()
                cleanup_results["weather_cache_archived"] = archived_count
                logger.info(f"Archived {archived_count} old weather cache entries")
            except Exception as e:
                logger.warning(f"Failed to archive old weather data: {e}")

            # Clean up Redis expired keys (Redis handles this automatically, but we can get stats)
            try:
                redis_info = await self.redis_manager.get_info()
                cleanup_results["redis_keys_cleaned"] = redis_info.get(
                    "expired_keys", 0
                )
            except Exception as e:
                logger.warning(f"Failed to get Redis cleanup stats: {e}")

            logger.info(f"Data cleanup completed: {cleanup_results}")
            return cleanup_results

        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
            raise DatabaseError(f"Failed to cleanup expired data: {e}")

    async def backup_data(
        self, backup_path: str, include_cache: bool = False
    ) -> Dict[str, Any]:
        """Create a backup of the database."""
        try:
            self._ensure_initialized()

            backup_info = {
                "timestamp": datetime.now().isoformat(),
                "backup_path": backup_path,
                "include_cache": include_cache,
                "tables_backed_up": [],
                "total_records": 0,
            }

            # Use SQLite backup functionality
            async with self.db_manager.get_connection() as conn:
                # Get table information
                cursor = await conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = [row[0] for row in await cursor.fetchall()]

                # Filter out cache table if not included
                if not include_cache:
                    tables = [t for t in tables if not t.startswith("weather_cache")]

                backup_info["tables_backed_up"] = tables

                # Count total records
                total_records = 0
                for table in tables:
                    cursor = await conn.execute(f"SELECT COUNT(*) FROM {table}")
                    count = (await cursor.fetchone())[0]
                    total_records += count

                backup_info["total_records"] = total_records

            # Perform the actual backup using SQLite's backup API
            await self.db_manager.backup_database(backup_path)

            logger.info(f"Database backup completed: {backup_info}")
            return backup_info

        except Exception as e:
            logger.error(f"Failed to backup database: {e}")
            raise DatabaseError(f"Failed to backup database: {e}")

    async def restore_data(self, backup_path: str) -> Dict[str, Any]:
        """Restore database from a backup."""
        try:
            restore_info = {
                "timestamp": datetime.now().isoformat(),
                "backup_path": backup_path,
                "success": False,
            }

            # Close current connections
            await self.shutdown()

            # Restore from backup
            await self.db_manager.restore_database(backup_path)

            # Reinitialize
            await self.initialize(run_migrations=False)

            restore_info["success"] = True
            logger.info(f"Database restore completed: {restore_info}")
            return restore_info

        except Exception as e:
            logger.error(f"Failed to restore database: {e}")
            raise DatabaseError(f"Failed to restore database: {e}")

    async def optimize_database(self) -> Dict[str, Any]:
        """Optimize database performance."""
        try:
            self._ensure_initialized()

            optimization_info = {
                "timestamp": datetime.now().isoformat(),
                "operations_performed": [],
                "before_size": 0,
                "after_size": 0,
            }

            # Get initial database size
            db_info_before = await self.db_manager.get_database_info()
            optimization_info["before_size"] = db_info_before.get("file_size", 0)

            async with self.db_manager.get_connection() as conn:
                # Vacuum database
                await conn.execute("VACUUM")
                optimization_info["operations_performed"].append("VACUUM")

                # Analyze tables for query optimization
                await conn.execute("ANALYZE")
                optimization_info["operations_performed"].append("ANALYZE")

                # Reindex all indexes
                await conn.execute("REINDEX")
                optimization_info["operations_performed"].append("REINDEX")

                await conn.commit()

            # Get final database size
            db_info_after = await self.db_manager.get_database_info()
            optimization_info["after_size"] = db_info_after.get("file_size", 0)
            optimization_info["size_reduction"] = (
                optimization_info["before_size"] - optimization_info["after_size"]
            )

            logger.info(f"Database optimization completed: {optimization_info}")
            return optimization_info

        except Exception as e:
            logger.error(f"Failed to optimize database: {e}")
            raise DatabaseError(f"Failed to optimize database: {e}")


async def create_database_service(
    sqlite_path: str = "weather_dashboard.db",
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_db: int = 0,
    redis_password: Optional[str] = None,
    pool_size: int = 10,
) -> DatabaseService:
    """Factory function to create a DatabaseService with default configuration."""
    try:
        # Get connection managers
        connection_factory = ConnectionManagerFactory()

        db_manager = await connection_factory.get_database_manager(
            database_path=sqlite_path, pool_size=pool_size
        )

        redis_manager = await connection_factory.get_redis_manager(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            password=redis_password,
            pool_size=pool_size,
        )

        # Create migration manager
        migration_manager = MigrationManager(db_manager)

        # Create and return database service
        service = DatabaseService(db_manager, redis_manager, migration_manager)

        logger.info("Database service created successfully")
        return service

    except Exception as e:
        logger.error(f"Failed to create database service: {e}")
        raise ConfigurationError(f"Database service creation failed: {e}")


# Global database service instance
_database_service: Optional[DatabaseService] = None


async def get_database_service() -> DatabaseService:
    """Get the global database service instance."""
    if _database_service is None:
        raise DatabaseError(
            "Database service not initialized. Call initialize_database_service() first."
        )

    return _database_service


async def initialize_database_service(**kwargs) -> DatabaseService:
    """Initialize the global database service instance."""
    global _database_service

    if _database_service is not None:
        logger.warning("Database service already initialized")
        return _database_service

    _database_service = await create_database_service(**kwargs)
    await _database_service.initialize()

    logger.info("Global database service initialized")
    return _database_service


async def shutdown_database_service() -> None:
    """Shutdown the global database service instance."""
    global _database_service

    if _database_service is not None:
        await _database_service.shutdown()
        _database_service = None
        logger.info("Global database service shutdown")
