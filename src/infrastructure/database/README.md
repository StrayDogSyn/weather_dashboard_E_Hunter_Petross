# Weather Dashboard - Data Storage and Caching Layer

A comprehensive data storage and caching solution built with SQLite for persistence and Redis for
high-performance caching, following the Repository pattern and implementing cache-aside strategies.

## Architecture Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                            │
│  (WeatherService, JournalService, ActivityService, etc.)    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 DatabaseService                             │
│              (Orchestrates all repositories)                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Repository Layer                             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │ Favorites   │ │   Journal   │ │  Settings   │ │Weather │ │
│  │ Repository  │ │ Repository  │ │ Repository  │ │ Cache  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Base Repository                                │
│         (Generic CRUD + Caching Logic)                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│            Connection Managers                              │
│  ┌─────────────────┐           ┌─────────────────┐          │
│  │ SQLite Manager  │           │  Redis Manager  │          │
│  │ (Persistence)   │           │   (Caching)     │          │
│  └─────────────────┘           └─────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 🗄️ **Persistent Storage (SQLite)**

- Connection pooling and transaction management
- WAL mode for better concurrency
- Automatic schema migrations
- Full-text search capabilities
- Optimized indexes and views

### ⚡ **High-Performance Caching (Redis)**

- Cache-aside pattern implementation
- Configurable TTL for different data types
- Automatic serialization/deserialization
- Connection pooling and health monitoring
- Memory usage optimization

### 🔄 **Repository Pattern**

- Generic base repository with CRUD operations
- Type-safe concrete implementations
- Integrated caching at repository level
- Consistent error handling
- Async/await throughout

### 📊 **Migration System**

- Version-controlled schema updates
- Automatic migration detection and execution
- Rollback capabilities
- Checksum validation
- Built-in migrations for core functionality

## Quick Start

### 1. Installation

```bash
# Install required dependencies
pip install aiosqlite redis python-dotenv
```

### 2. Environment Configuration

Create a `.env` file:

```env
# Database Configuration
DB_PATH=weather_dashboard.db
DB_POOL_SIZE=10
DB_TIMEOUT=30.0
DB_WAL_MODE=true

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
REDIS_POOL_SIZE=10

# Cache TTL Settings (seconds)
REDIS_DEFAULT_TTL=3600
REDIS_WEATHER_TTL=1800
REDIS_SESSION_TTL=86400

# Migration Settings
AUTO_MIGRATE=true
BACKUP_BEFORE_MIGRATION=true
```

### 3. Basic Usage

```python
import asyncio
from src.infrastructure.database import (
    initialize_database_service,
    get_database_service,
    shutdown_database_service
)
from src.infrastructure.database.models import FavoriteLocationModel

async def main():
    # Initialize the database service
    await initialize_database_service()
    
    # Get the service instance
    db_service = await get_database_service()
    
    # Use repositories
    favorites = db_service.favorites
    
    # Create a favorite location
    location = FavoriteLocationModel(
        name="New York City",
        latitude=40.7128,
        longitude=-74.0060,
        country="US",
        state="NY",
        is_default=True
    )
    
    created = await favorites.create(location)
    print(f"Created: {created.name}")
    
    # Retrieve (will use cache on subsequent calls)
    retrieved = await favorites.get_by_id(created.id)
    print(f"Retrieved: {retrieved.name}")
    
    # Search operations
    results = await favorites.search_by_name("New York")
    print(f"Search results: {len(results)}")
    
    # Cleanup
    await shutdown_database_service()

if __name__ == "__main__":
    asyncio.run(main())
```

## Repository Implementations

### FavoritesRepository

Manages favorite weather locations with geographic search capabilities.

```python
# Create a favorite location
location = FavoriteLocationModel(
    name="San Francisco",
    latitude=37.7749,
    longitude=-122.4194,
    country="US",
    state="CA",
    tags=["tech", "coastal"]
)
created = await favorites_repo.create(location)

# Search by coordinates (with radius)
nearby = await favorites_repo.get_by_coordinates(
    latitude=37.7749,
    longitude=-122.4194,
    radius_km=50
)

# Filter by tags
tech_locations = await favorites_repo.filter_by_tags(["tech"])

# Get default location
default = await favorites_repo.get_default_location()
```

### JournalRepository

Manages weather journal entries with full-text search and mood tracking.

```python
# Create a journal entry
entry = JournalEntryModel(
    title="Beautiful Sunny Day",
    content="Perfect weather for outdoor activities...",
    entry_type=JournalEntryType.DAILY_REFLECTION,
    weather_mood=WeatherMood.ENERGETIC,
    location="Central Park",
    tags=["sunny", "outdoor"]
)
created = await journal_repo.create(entry)

# Full-text search
results = await journal_repo.search_entries("sunny outdoor")

# Get entries by mood
contemplative = await journal_repo.get_by_weather_mood(
    WeatherMood.CONTEMPLATIVE
)

# Get mood statistics
stats = await journal_repo.get_mood_statistics()
```

### SettingsRepository

Manages application settings with categorization and type safety.

```python
# Set a setting
await settings_repo.set_setting("theme", "dark")

# Get by category
ui_settings = await settings_repo.get_by_category("ui")

# Bulk update
updates = {
    "temperature_unit": "celsius",
    "wind_speed_unit": "kmh"
}
await settings_repo.bulk_update(updates)

# Export settings
exported = await settings_repo.export_settings()
```

### WeatherCacheRepository

Manages weather data caching with automatic expiration and archival.

```python
# Cache weather data
await weather_repo.cache_weather_data(
    cache_key="weather:nyc:current",
    location="New York City",
    latitude=40.7128,
    longitude=-74.0060,
    data_type="current",
    weather_data={"temperature": 72, "condition": "sunny"},
    ttl_seconds=1800
)

# Retrieve cached data
cached = await weather_repo.get_by_cache_key("weather:nyc:current")

# Cleanup expired entries
expired_count = await weather_repo.cleanup_expired()

# Get cache statistics
stats = await weather_repo.get_cache_statistics()
```

## Migration System

The migration system provides version-controlled database schema updates.

### Built-in Migrations

1. **001_initial_schema.sql** - Core tables and indexes
2. **002_journal_fulltext_search.sql** - FTS5 search capabilities
3. **003_weather_data_archival.sql** - Data archival and cleanup

### Creating Custom Migrations

```python
from src.infrastructure.database.migration_manager import MigrationManager

# Create a new migration
migration_manager = MigrationManager(db_manager)
await migration_manager.create_migration(
    name="add_user_preferences",
    sql="""
    CREATE TABLE user_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        preference_key TEXT NOT NULL,
        preference_value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, preference_key)
    );
    """
)

# Apply pending migrations
await migration_manager.apply_pending_migrations()
```

## Configuration

### Database Configuration

```python
from src.infrastructure.database.config import DatabaseConfig

db_config = DatabaseConfig(
    path="weather_dashboard.db",
    pool_size=10,
    timeout=30.0,
    enable_wal_mode=True,
    cache_size=-64000,  # 64MB cache
    synchronous="NORMAL"
)
```

### Redis Configuration

```python
from src.infrastructure.database.config import RedisConfig

redis_config = RedisConfig(
    host="localhost",
    port=6379,
    db=0,
    pool_size=10,
    default_ttl=3600,
    weather_cache_ttl=1800,
    decode_responses=True
)
```

## Performance Optimization

### Caching Strategy

- **Cache-aside pattern**: Data is loaded into cache on first access
- **TTL-based expiration**: Different TTL values for different data types
- **Automatic serialization**: JSON serialization with compression for large objects
- **Connection pooling**: Reuse connections for better performance

### Database Optimization

- **WAL mode**: Better concurrency for read-heavy workloads
- **Optimized indexes**: Strategic indexes for common query patterns
- **VACUUM and ANALYZE**: Automatic database optimization
- **Connection pooling**: Efficient connection management

### Query Optimization

```python
# Use indexes effectively
results = await favorites_repo.get_by_coordinates(
    latitude=40.7128,
    longitude=-74.0060,
    radius_km=10  # Uses spatial index
)

# Full-text search with FTS5
entries = await journal_repo.search_entries(
    "sunny weather outdoor"  # Uses FTS5 index
)

# Efficient pagination
results = await journal_repo.get_recent_entries(
    limit=20,
    offset=0
)
```

## Monitoring and Health Checks

### System Health

```python
# Comprehensive health check
health = await db_service.health_check()
print(f"Overall status: {health['overall_status']}")

for component, status in health['components'].items():
    print(f"{component}: {status['status']}")
```

### System Statistics

```python
# Get detailed statistics
stats = await db_service.get_system_statistics()
print(f"Database size: {stats['database']['file_size']} bytes")
print(f"Redis memory: {stats['cache']['memory_usage']}")
print(f"Total entries: {stats['repositories']['journal']['total_entries']}")
```

### Data Cleanup

```python
# Clean up expired data
cleanup_results = await db_service.cleanup_expired_data()
print(f"Cleaned up {cleanup_results['weather_cache_expired']} expired entries")

# Optimize database
optimization = await db_service.optimize_database()
print(f"Size reduction: {optimization['size_reduction']} bytes")
```

## Error Handling

The system provides comprehensive error handling with custom exceptions:

```python
from src.shared.exceptions import DatabaseError, ValidationError

try:
    location = await favorites_repo.create(invalid_location)
except ValidationError as e:
    print(f"Validation failed: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
```

## Testing

Run the comprehensive example to test all functionality:

```bash
python examples/database_usage_example.py
```

This will demonstrate:

- Repository CRUD operations
- Caching behavior and performance
- Search and filtering capabilities
- System health and statistics
- Data cleanup and optimization

## Best Practices

### Repository Usage

1. **Always use repositories**: Never access the database directly from services
2. **Leverage caching**: Repositories automatically handle caching
3. **Use transactions**: For multi-step operations
4. **Handle errors gracefully**: Use try-catch blocks for database operations

### Performance

1. **Use appropriate TTL**: Set TTL based on data freshness requirements
2. **Batch operations**: Use bulk operations when possible
3. **Monitor cache hit rates**: Optimize caching strategy based on metrics
4. **Regular cleanup**: Schedule periodic cleanup of expired data

### Security

1. **Validate input**: Always validate data before database operations
2. **Use parameterized queries**: Prevent SQL injection
3. **Secure Redis**: Use authentication and encryption in production
4. **Regular backups**: Implement automated backup strategies

## Production Deployment

### Environment Variables

Set appropriate environment variables for production:

```env
# Production database
DB_PATH=/var/lib/weather_dashboard/weather_dashboard.db
DB_POOL_SIZE=20
DB_TIMEOUT=60.0

# Production Redis
REDIS_HOST=redis.production.com
REDIS_PORT=6379
REDIS_PASSWORD=secure_password
REDIS_SSL=true

# Performance tuning
REDIS_POOL_SIZE=20
REDIS_MAX_CONNECTIONS=100
CACHE_COMPRESSION=true

# Monitoring
ENABLE_HEALTH_CHECKS=true
ENABLE_METRICS=true
LOG_SLOW_QUERIES=true
```

### Docker Configuration

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - DB_PATH=/data/weather_dashboard.db
      - REDIS_HOST=redis
    volumes:
      - ./data:/data
    depends_on:
      - redis
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

## Contributing

When extending the database layer:

1. **Follow the Repository pattern**: Extend `BaseRepository` for new entities
2. **Add migrations**: Create migration scripts for schema changes
3. **Update models**: Add corresponding dataclass models
4. **Write tests**: Include comprehensive test coverage
5. **Document changes**: Update this README with new features

## Troubleshooting

### Common Issues

1. **Database locked**: Ensure WAL mode is enabled and connections are properly closed
2. **Redis connection failed**: Check Redis server status and connection parameters
3. **Migration failed**: Check migration logs and validate SQL syntax
4. **Cache misses**: Verify TTL settings and Redis memory limits

### Debug Mode

Enable debug logging for detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable query logging
config = get_config()
config.enable_query_logging = True
config.log_slow_queries = True
config.slow_query_threshold = 0.1  # Log queries > 100ms
```

---

## Built with ❤️ for the Weather Dashboard project

This data storage and caching layer provides a solid foundation for building scalable,
high-performance weather applications with proper separation of concerns and enterprise-grade
reliability.
