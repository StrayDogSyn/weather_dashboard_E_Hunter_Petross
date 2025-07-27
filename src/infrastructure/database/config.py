"""Database configuration management with environment variable support."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class DatabaseConfig:
    """SQLite database configuration."""

    path: str = "weather_dashboard.db"
    pool_size: int = 10
    timeout: float = 30.0
    enable_wal_mode: bool = True
    enable_foreign_keys: bool = True
    cache_size: int = -64000  # 64MB cache
    temp_store: str = "memory"
    synchronous: str = "NORMAL"
    journal_mode: str = "WAL"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.pool_size < 1:
            raise ValueError("Pool size must be at least 1")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive")
        if self.cache_size > 0 and self.cache_size < 1000:
            raise ValueError("Cache size must be at least 1000 pages if positive")

    @property
    def absolute_path(self) -> str:
        """Get absolute path to database file."""
        return str(Path(self.path).resolve())

    @property
    def connection_string(self) -> str:
        """Get SQLite connection string with parameters."""
        params = []
        if self.timeout != 30.0:
            params.append(f"timeout={int(self.timeout * 1000)}")

        if params:
            return f"file:{self.absolute_path}?{'&'.join(params)}"
        return f"file:{self.absolute_path}"

    @property
    def pragma_statements(self) -> Dict[str, Any]:
        """Get PRAGMA statements for database optimization."""
        pragmas = {
            "foreign_keys": "ON" if self.enable_foreign_keys else "OFF",
            "cache_size": self.cache_size,
            "temp_store": self.temp_store,
            "synchronous": self.synchronous,
        }

        if self.enable_wal_mode:
            pragmas["journal_mode"] = self.journal_mode

        return pragmas


@dataclass
class RedisConfig:
    """Redis configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    username: Optional[str] = None
    pool_size: int = 10
    max_connections: int = 50
    retry_on_timeout: bool = True
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    health_check_interval: int = 30
    decode_responses: bool = True
    encoding: str = "utf-8"
    ssl: bool = False
    ssl_cert_reqs: Optional[str] = None
    ssl_ca_certs: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None

    # TTL settings
    default_ttl: int = 3600  # 1 hour
    weather_cache_ttl: int = 1800  # 30 minutes
    user_session_ttl: int = 86400  # 24 hours
    temporary_data_ttl: int = 300  # 5 minutes

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not (1 <= self.port <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        if not (0 <= self.db <= 15):
            raise ValueError("Database number must be between 0 and 15")
        if self.pool_size < 1:
            raise ValueError("Pool size must be at least 1")
        if self.max_connections < self.pool_size:
            raise ValueError("Max connections must be at least pool size")
        if self.socket_timeout <= 0:
            raise ValueError("Socket timeout must be positive")
        if self.socket_connect_timeout <= 0:
            raise ValueError("Socket connect timeout must be positive")

    @property
    def connection_kwargs(self) -> Dict[str, Any]:
        """Get Redis connection keyword arguments."""
        kwargs = {
            "host": self.host,
            "port": self.port,
            "db": self.db,
            "socket_timeout": self.socket_timeout,
            "socket_connect_timeout": self.socket_connect_timeout,
            "retry_on_timeout": self.retry_on_timeout,
            "health_check_interval": self.health_check_interval,
            "decode_responses": self.decode_responses,
            "encoding": self.encoding,
        }

        if self.password:
            kwargs["password"] = self.password

        if self.username:
            kwargs["username"] = self.username

        if self.ssl:
            kwargs["ssl"] = True
            if self.ssl_cert_reqs:
                kwargs["ssl_cert_reqs"] = self.ssl_cert_reqs
            if self.ssl_ca_certs:
                kwargs["ssl_ca_certs"] = self.ssl_ca_certs
            if self.ssl_certfile:
                kwargs["ssl_certfile"] = self.ssl_certfile
            if self.ssl_keyfile:
                kwargs["ssl_keyfile"] = self.ssl_keyfile

        return kwargs

    @property
    def pool_kwargs(self) -> Dict[str, Any]:
        """Get Redis connection pool keyword arguments."""
        return {
            **self.connection_kwargs,
            "max_connections": self.max_connections,
        }

    def get_ttl(self, cache_type: str) -> int:
        """Get TTL for specific cache type."""
        ttl_map = {
            "weather": self.weather_cache_ttl,
            "session": self.user_session_ttl,
            "temp": self.temporary_data_ttl,
            "default": self.default_ttl,
        }
        return ttl_map.get(cache_type, self.default_ttl)


@dataclass
class MigrationConfig:
    """Database migration configuration."""

    migrations_dir: str = "migrations"
    auto_migrate: bool = True
    backup_before_migration: bool = True
    validate_checksums: bool = True
    max_migration_time: int = 300  # 5 minutes

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.max_migration_time <= 0:
            raise ValueError("Max migration time must be positive")

    @property
    def migrations_path(self) -> Path:
        """Get absolute path to migrations directory."""
        return Path(self.migrations_dir).resolve()


@dataclass
class CacheConfig:
    """Cache configuration settings."""

    enable_redis: bool = True
    enable_memory_cache: bool = True
    memory_cache_size: int = 1000
    cache_compression: bool = True
    compression_threshold: int = 1024  # Compress data larger than 1KB
    cache_serialization: str = "json"  # json, pickle, msgpack

    # Cache key prefixes
    key_prefix: str = "weather_dashboard"
    weather_prefix: str = "weather"
    user_prefix: str = "user"
    session_prefix: str = "session"
    temp_prefix: str = "temp"

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.memory_cache_size < 0:
            raise ValueError("Memory cache size must be non-negative")
        if self.compression_threshold < 0:
            raise ValueError("Compression threshold must be non-negative")
        if self.cache_serialization not in ["json", "pickle", "msgpack"]:
            raise ValueError("Cache serialization must be json, pickle, or msgpack")

    def get_cache_key(self, cache_type: str, key: str) -> str:
        """Generate cache key with proper prefix."""
        prefix_map = {
            "weather": self.weather_prefix,
            "user": self.user_prefix,
            "session": self.session_prefix,
            "temp": self.temp_prefix,
        }

        type_prefix = prefix_map.get(cache_type, cache_type)
        return f"{self.key_prefix}:{type_prefix}:{key}"


@dataclass
class DatabaseServiceConfig:
    """Complete database service configuration."""

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    migration: MigrationConfig = field(default_factory=MigrationConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Service-level settings
    enable_health_checks: bool = True
    health_check_interval: int = 60  # seconds
    enable_metrics: bool = True
    enable_query_logging: bool = False
    log_slow_queries: bool = True
    slow_query_threshold: float = 1.0  # seconds

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.health_check_interval <= 0:
            raise ValueError("Health check interval must be positive")
        if self.slow_query_threshold <= 0:
            raise ValueError("Slow query threshold must be positive")


def load_config_from_env() -> DatabaseServiceConfig:
    """Load configuration from environment variables."""

    # Database configuration
    db_config = DatabaseConfig(
        path=os.getenv("DB_PATH", "weather_dashboard.db"),
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        timeout=float(os.getenv("DB_TIMEOUT", "30.0")),
        enable_wal_mode=os.getenv("DB_WAL_MODE", "true").lower() == "true",
        enable_foreign_keys=os.getenv("DB_FOREIGN_KEYS", "true").lower() == "true",
        cache_size=int(os.getenv("DB_CACHE_SIZE", "-64000")),
        temp_store=os.getenv("DB_TEMP_STORE", "memory"),
        synchronous=os.getenv("DB_SYNCHRONOUS", "NORMAL"),
        journal_mode=os.getenv("DB_JOURNAL_MODE", "WAL"),
    )

    # Redis configuration
    redis_config = RedisConfig(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        password=os.getenv("REDIS_PASSWORD"),
        username=os.getenv("REDIS_USERNAME"),
        pool_size=int(os.getenv("REDIS_POOL_SIZE", "10")),
        max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
        retry_on_timeout=os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true",
        socket_timeout=float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0")),
        socket_connect_timeout=float(os.getenv("REDIS_CONNECT_TIMEOUT", "5.0")),
        health_check_interval=int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30")),
        decode_responses=os.getenv("REDIS_DECODE_RESPONSES", "true").lower() == "true",
        encoding=os.getenv("REDIS_ENCODING", "utf-8"),
        ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
        ssl_cert_reqs=os.getenv("REDIS_SSL_CERT_REQS"),
        ssl_ca_certs=os.getenv("REDIS_SSL_CA_CERTS"),
        ssl_certfile=os.getenv("REDIS_SSL_CERTFILE"),
        ssl_keyfile=os.getenv("REDIS_SSL_KEYFILE"),
        default_ttl=int(os.getenv("REDIS_DEFAULT_TTL", "3600")),
        weather_cache_ttl=int(os.getenv("REDIS_WEATHER_TTL", "1800")),
        user_session_ttl=int(os.getenv("REDIS_SESSION_TTL", "86400")),
        temporary_data_ttl=int(os.getenv("REDIS_TEMP_TTL", "300")),
    )

    # Migration configuration
    migration_config = MigrationConfig(
        migrations_dir=os.getenv("MIGRATIONS_DIR", "migrations"),
        auto_migrate=os.getenv("AUTO_MIGRATE", "true").lower() == "true",
        backup_before_migration=os.getenv("BACKUP_BEFORE_MIGRATION", "true").lower()
        == "true",
        validate_checksums=os.getenv("VALIDATE_CHECKSUMS", "true").lower() == "true",
        max_migration_time=int(os.getenv("MAX_MIGRATION_TIME", "300")),
    )

    # Cache configuration
    cache_config = CacheConfig(
        enable_redis=os.getenv("ENABLE_REDIS_CACHE", "true").lower() == "true",
        enable_memory_cache=os.getenv("ENABLE_MEMORY_CACHE", "true").lower() == "true",
        memory_cache_size=int(os.getenv("MEMORY_CACHE_SIZE", "1000")),
        cache_compression=os.getenv("CACHE_COMPRESSION", "true").lower() == "true",
        compression_threshold=int(os.getenv("COMPRESSION_THRESHOLD", "1024")),
        cache_serialization=os.getenv("CACHE_SERIALIZATION", "json"),
        key_prefix=os.getenv("CACHE_KEY_PREFIX", "weather_dashboard"),
        weather_prefix=os.getenv("CACHE_WEATHER_PREFIX", "weather"),
        user_prefix=os.getenv("CACHE_USER_PREFIX", "user"),
        session_prefix=os.getenv("CACHE_SESSION_PREFIX", "session"),
        temp_prefix=os.getenv("CACHE_TEMP_PREFIX", "temp"),
    )

    # Service configuration
    service_config = DatabaseServiceConfig(
        database=db_config,
        redis=redis_config,
        migration=migration_config,
        cache=cache_config,
        enable_health_checks=os.getenv("ENABLE_HEALTH_CHECKS", "true").lower()
        == "true",
        health_check_interval=int(os.getenv("HEALTH_CHECK_INTERVAL", "60")),
        enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
        enable_query_logging=os.getenv("ENABLE_QUERY_LOGGING", "false").lower()
        == "true",
        log_slow_queries=os.getenv("LOG_SLOW_QUERIES", "true").lower() == "true",
        slow_query_threshold=float(os.getenv("SLOW_QUERY_THRESHOLD", "1.0")),
    )

    return service_config


def get_default_config() -> DatabaseServiceConfig:
    """Get default configuration."""
    return DatabaseServiceConfig()


def validate_config(config: DatabaseServiceConfig) -> None:
    """Validate the complete configuration."""
    # Check if database path is writable
    db_path = Path(config.database.path)
    db_dir = db_path.parent

    if not db_dir.exists():
        try:
            db_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(f"Cannot create database directory {db_dir}: {e}")

    if not os.access(db_dir, os.W_OK):
        raise ValueError(f"Database directory {db_dir} is not writable")

    # Check migrations directory
    if config.migration.auto_migrate:
        migrations_path = config.migration.migrations_path
        if not migrations_path.exists():
            try:
                migrations_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValueError(
                    f"Cannot create migrations directory {migrations_path}: {e}"
                )

    # Validate Redis configuration if enabled
    if config.cache.enable_redis:
        if not config.redis.host:
            raise ValueError("Redis host cannot be empty when Redis is enabled")

        if config.redis.ssl and not all(
            [config.redis.ssl_cert_reqs, config.redis.ssl_ca_certs]
        ):
            raise ValueError("SSL configuration incomplete for Redis")


# Global configuration instance
_config: Optional[DatabaseServiceConfig] = None


def get_config() -> DatabaseServiceConfig:
    """Get the global configuration instance."""
    global _config

    if _config is None:
        _config = load_config_from_env()
        validate_config(_config)

    return _config


def set_config(config: DatabaseServiceConfig) -> None:
    """Set the global configuration instance."""
    global _config

    validate_config(config)
    _config = config


def reset_config() -> None:
    """Reset the global configuration to None."""
    global _config
    _config = None
