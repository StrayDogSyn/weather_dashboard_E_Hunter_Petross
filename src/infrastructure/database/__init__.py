"""Database infrastructure package."""

from .base_repository import BaseRepository
from .connection_manager import DatabaseConnectionManager, RedisConnectionManager
from .migration_manager import MigrationManager
from .models import FavoriteCity, JournalEntry, UserSetting, WeatherCache
from .repositories import (
    FavoritesRepository,
    JournalRepository,
    SettingsRepository,
    WeatherCacheRepository,
)

__all__ = [
    "BaseRepository",
    "DatabaseConnectionManager",
    "RedisConnectionManager",
    "MigrationManager",
    "FavoritesRepository",
    "JournalRepository",
    "SettingsRepository",
    "WeatherCacheRepository",
    "FavoriteCity",
    "JournalEntry",
    "UserSetting",
    "WeatherCache",
]
