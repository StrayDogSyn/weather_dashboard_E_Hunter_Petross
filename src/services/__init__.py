"""Services package for the Weather Dashboard application."""

from .cache_service import MemoryCacheService
from .data_storage import FileDataStorage
from .location_service import LocationDetectionService
from .poetry_service import WeatherPoetryService
from .sound_service import SoundService, SoundType, play_sound, play_weather_sound
from .storage_factory import DataStorageFactory
from .team_data_service import TeamDataService
from .visualization_service import WeatherVisualizationService
from .weather_api import OpenWeatherMapAPI

# Conditional imports for SQLAlchemy-dependent services
try:
    from .sql_data_storage import SQLDataStorage

    _SQLALCHEMY_AVAILABLE = True
except ImportError:
    _SQLALCHEMY_AVAILABLE = False
    SQLDataStorage = None

__all__ = [
    "OpenWeatherMapAPI",
    "FileDataStorage",
    "MemoryCacheService",
    "DataStorageFactory",
    "LocationDetectionService",
    "WeatherVisualizationService",
    "WeatherPoetryService",
    "SoundService",
    "SoundType",
    "play_sound",
    "play_weather_sound",
    "TeamDataService",
]

# Add SQLDataStorage to exports only if available
if _SQLALCHEMY_AVAILABLE:
    __all__.append("SQLDataStorage")
