"""Database and Redis connection managers with pooling and transaction support."""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, Optional

import aiosqlite
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from ...config.config import Config
from ...shared.exceptions import CacheError, DatabaseError

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """SQLite connection manager with connection pooling and transaction support."""

    def __init__(self, config: Config):
        self.config = config
        self.db_path = Path(config.database.sqlite_path)
        self._connection_pool: Dict[str, aiosqlite.Connection] = {}
        self._pool_size = config.database.connection_pool_size
        self._current_connections = 0
        self._lock = asyncio.Lock()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the database and connection pool."""
        if self._initialized:
            return

        try:
            # Ensure database directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            # Create initial connection to set up database
            async with aiosqlite.connect(str(self.db_path)) as conn:
                # Enable WAL mode for better concurrency
                await conn.execute("PRAGMA journal_mode=WAL")
                # Enable foreign key constraints
                await conn.execute("PRAGMA foreign_keys=ON")
                # Set reasonable timeout
                await conn.execute("PRAGMA busy_timeout=30000")
                await conn.commit()

            self._initialized = True
            logger.info(f"Database connection manager initialized: {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        if not self._initialized:
            await self.initialize()

        connection = None
        connection_id = None

        try:
            async with self._lock:
                # Try to reuse existing connection or create new one
                if len(self._connection_pool) < self._pool_size:
                    connection_id = f"conn_{self._current_connections}"
                    connection = await aiosqlite.connect(str(self.db_path))

                    # Configure connection
                    await connection.execute("PRAGMA journal_mode=WAL")
                    await connection.execute("PRAGMA foreign_keys=ON")
                    await connection.execute("PRAGMA busy_timeout=30000")

                    self._connection_pool[connection_id] = connection
                    self._current_connections += 1

                    logger.debug(f"Created new database connection: {connection_id}")
                else:
                    # Get existing connection (simple round-robin)
                    connection_id = list(self._connection_pool.keys())[0]
                    connection = self._connection_pool[connection_id]
                    logger.debug(f"Reusing database connection: {connection_id}")

            yield connection

        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if connection and connection_id:
                # Remove faulty connection from pool
                async with self._lock:
                    if connection_id in self._connection_pool:
                        await connection.close()
                        del self._connection_pool[connection_id]
                        self._current_connections -= 1
            raise DatabaseError(f"Database operation failed: {e}")

    @asynccontextmanager
    async def get_transaction(self):
        """Get a database connection with transaction management."""
        async with self.get_connection() as conn:
            try:
                await conn.execute("BEGIN")
                yield conn
                # Transaction will be committed by the caller
            except Exception as e:
                await conn.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise

    async def execute_script(self, script: str) -> None:
        """Execute a SQL script (for migrations)."""
        try:
            async with self.get_connection() as conn:
                await conn.executescript(script)
                await conn.commit()
                logger.info("SQL script executed successfully")
        except Exception as e:
            logger.error(f"Failed to execute SQL script: {e}")
            raise DatabaseError(f"Script execution failed: {e}")

    async def check_connection(self) -> bool:
        """Check if database connection is healthy."""
        try:
            async with self.get_connection() as conn:
                cursor = await conn.execute("SELECT 1")
                result = await cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    async def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        try:
            async with self.get_connection() as conn:
                info = {}

                # Get database size
                cursor = await conn.execute("PRAGMA page_count")
                page_count = (await cursor.fetchone())[0]

                cursor = await conn.execute("PRAGMA page_size")
                page_size = (await cursor.fetchone())[0]

                info["size_bytes"] = page_count * page_size
                info["page_count"] = page_count
                info["page_size"] = page_size

                # Get table information
                cursor = await conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = [row[0] for row in await cursor.fetchall()]
                info["tables"] = tables

                # Get connection pool info
                info["pool_size"] = len(self._connection_pool)
                info["max_pool_size"] = self._pool_size

                return info

        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            raise DatabaseError(f"Failed to get database info: {e}")

    async def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        async with self._lock:
            for connection_id, connection in self._connection_pool.items():
                try:
                    await connection.close()
                    logger.debug(f"Closed database connection: {connection_id}")
                except Exception as e:
                    logger.warning(f"Error closing connection {connection_id}: {e}")

            self._connection_pool.clear()
            self._current_connections = 0
            logger.info("All database connections closed")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_all_connections()


class RedisConnectionManager:
    """Redis connection manager with connection pooling."""

    def __init__(self, config: Config):
        self.config = config
        self._connection_pool: Optional[ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Redis connection pool."""
        if self._initialized:
            return

        try:
            # Create connection pool
            self._connection_pool = ConnectionPool(
                host=self.config.redis.host,
                port=self.config.redis.port,
                db=self.config.redis.db,
                password=self.config.redis.password,
                max_connections=self.config.redis.max_connections,
                retry_on_timeout=True,
                socket_timeout=self.config.redis.socket_timeout,
                socket_connect_timeout=self.config.redis.connect_timeout,
                decode_responses=False,  # We'll handle encoding/decoding ourselves
            )

            # Create Redis client
            self._client = redis.Redis(
                connection_pool=self._connection_pool,
                socket_timeout=self.config.redis.socket_timeout,
                socket_connect_timeout=self.config.redis.connect_timeout,
            )

            # Test connection
            await self._client.ping()

            self._initialized = True
            logger.info(
                f"Redis connection manager initialized: {self.config.redis.host}:{self.config.redis.port}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise CacheError(f"Redis initialization failed: {e}")

    async def get_client(self) -> redis.Redis:
        """Get Redis client."""
        if not self._initialized:
            await self.initialize()

        if not self._client:
            raise CacheError("Redis client not initialized")

        return self._client

    async def check_connection(self) -> bool:
        """Check if Redis connection is healthy."""
        try:
            if not self._client:
                return False

            await self._client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

    async def get_info(self) -> Dict[str, Any]:
        """Get Redis server information."""
        try:
            client = await self.get_client()
            info = await client.info()

            # Add connection pool info
            if self._connection_pool:
                info["pool_created_connections"] = (
                    self._connection_pool.created_connections
                )
                info["pool_available_connections"] = len(
                    self._connection_pool._available_connections
                )
                info["pool_in_use_connections"] = len(
                    self._connection_pool._in_use_connections
                )

            return info

        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")
            raise CacheError(f"Failed to get Redis info: {e}")

    async def flush_database(self, db: Optional[int] = None) -> None:
        """Flush Redis database."""
        try:
            client = await self.get_client()

            if db is not None:
                # Switch to specific database and flush
                await client.select(db)
                await client.flushdb()
                # Switch back to configured database
                await client.select(self.config.redis.db)
            else:
                # Flush current database
                await client.flushdb()

            logger.info(f"Redis database flushed: {db or self.config.redis.db}")

        except Exception as e:
            logger.error(f"Failed to flush Redis database: {e}")
            raise CacheError(f"Failed to flush Redis database: {e}")

    async def get_memory_usage(self) -> Dict[str, Any]:
        """Get Redis memory usage statistics."""
        try:
            client = await self.get_client()
            info = await client.info("memory")

            return {
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "used_memory_peak": info.get("used_memory_peak", 0),
                "used_memory_peak_human": info.get("used_memory_peak_human", "0B"),
                "maxmemory": info.get("maxmemory", 0),
                "maxmemory_human": info.get("maxmemory_human", "unlimited"),
                "mem_fragmentation_ratio": info.get("mem_fragmentation_ratio", 0),
            }

        except Exception as e:
            logger.error(f"Failed to get Redis memory usage: {e}")
            raise CacheError(f"Failed to get Redis memory usage: {e}")

    async def set_ttl_for_pattern(self, pattern: str, ttl: int) -> int:
        """Set TTL for all keys matching a pattern."""
        try:
            client = await self.get_client()
            keys = await client.keys(pattern)

            if not keys:
                return 0

            # Use pipeline for efficiency
            pipe = client.pipeline()
            for key in keys:
                pipe.expire(key, ttl)

            results = await pipe.execute()
            updated_count = sum(1 for result in results if result)

            logger.info(
                f"Set TTL {ttl}s for {updated_count} keys matching pattern: {pattern}"
            )
            return updated_count

        except Exception as e:
            logger.error(f"Failed to set TTL for pattern {pattern}: {e}")
            raise CacheError(f"Failed to set TTL for pattern: {e}")

    async def delete_by_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern."""
        try:
            client = await self.get_client()
            keys = await client.keys(pattern)

            if not keys:
                return 0

            deleted_count = await client.delete(*keys)
            logger.info(f"Deleted {deleted_count} keys matching pattern: {pattern}")
            return deleted_count

        except Exception as e:
            logger.error(f"Failed to delete keys by pattern {pattern}: {e}")
            raise CacheError(f"Failed to delete keys by pattern: {e}")

    async def close(self) -> None:
        """Close Redis connections."""
        try:
            if self._client:
                await self._client.close()
                self._client = None

            if self._connection_pool:
                await self._connection_pool.disconnect()
                self._connection_pool = None

            self._initialized = False
            logger.info("Redis connections closed")

        except Exception as e:
            logger.warning(f"Error closing Redis connections: {e}")

    async def __aenter__(self):
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


class ConnectionManagerFactory:
    """Factory for creating connection managers."""

    _db_manager: Optional[DatabaseConnectionManager] = None
    _redis_manager: Optional[RedisConnectionManager] = None

    @classmethod
    async def get_database_manager(cls, config: Config) -> DatabaseConnectionManager:
        """Get singleton database connection manager."""
        if cls._db_manager is None:
            cls._db_manager = DatabaseConnectionManager(config)
            await cls._db_manager.initialize()
        return cls._db_manager

    @classmethod
    async def get_redis_manager(cls, config: Config) -> RedisConnectionManager:
        """Get singleton Redis connection manager."""
        if cls._redis_manager is None:
            cls._redis_manager = RedisConnectionManager(config)
            await cls._redis_manager.initialize()
        return cls._redis_manager

    @classmethod
    async def close_all(cls) -> None:
        """Close all connection managers."""
        if cls._db_manager:
            await cls._db_manager.close_all_connections()
            cls._db_manager = None

        if cls._redis_manager:
            await cls._redis_manager.close()
            cls._redis_manager = None

        logger.info("All connection managers closed")
