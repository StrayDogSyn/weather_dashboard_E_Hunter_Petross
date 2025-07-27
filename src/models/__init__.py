"""Enhanced Models Package for the Weather Dashboard Application.

This package provides comprehensive weather-related models with AI integration,
design patterns, and advanced functionality.

Enhancements:
- AI-powered insights and analysis
- Factory and Builder patterns
- Repository pattern for data access
- Enhanced validation and error handling
- Rich metadata and analytics
- Predictive modeling with ML/AI
- Extensible architecture
"""

# Enhanced Capstone Models with AI Integration
from .capstone_models import (
    Activity,  # Core entities; Enhanced enums; Factory and Builder patterns; Protocols and base classes
)
from .capstone_models import ActivityDifficulty
from .capstone_models import ActivityFactory
from .capstone_models import ActivitySuggestion
from .capstone_models import ActivityType
from .capstone_models import AIEnhancedModel
from .capstone_models import ComparisonStrategy
from .capstone_models import DefaultComparisonStrategy
from .capstone_models import ExtensibleEnum
from .capstone_models import JournalEntry
from .capstone_models import ModelProtocol
from .capstone_models import MoodType
from .capstone_models import OutdoorActivityStrategy
from .capstone_models import PoemType
from .capstone_models import SeasonalPreference
from .capstone_models import TemperatureRange
from .capstone_models import WeatherComparison
from .capstone_models import WeatherComparisonBuilder
from .capstone_models import WeatherImpact
from .capstone_models import WeatherPoem

# Enhanced Database Models with Repository Pattern
from .database_models import ActivityRecommendations
from .database_models import AIEnhancedMixin as DatabaseAIEnhancedMixin
from .database_models import AuditMixin
from .database_models import Base
from .database_models import BaseRepository
from .database_models import DatabaseModelFactory
from .database_models import DatabaseRepository
from .database_models import FavoriteCities
from .database_models import FavoriteCitiesRepository
from .database_models import JournalEntries
from .database_models import JournalEntriesRepository
from .database_models import SessionLocal
from .database_models import UserPreferences
from .database_models import UserPreferencesRepository
from .database_models import WeatherHistory
from .database_models import close_db_session
from .database_models import engine
from .database_models import get_db_session
from .database_models import init_database
from .database_models import init_enhanced_database

# Enhanced Predictive Models with AI Integration
from .predictive_models import (
    AIPredictionStrategy,  # Core prediction classes; Strategy patterns; Factory pattern; Abstract classes
)
from .predictive_models import EnhancedWeatherPredictor
from .predictive_models import MLPredictionStrategy
from .predictive_models import ModelMetrics
from .predictive_models import ModelType
from .predictive_models import PredictionResult
from .predictive_models import PredictionStrategy
from .predictive_models import PredictiveModelFactory
from .predictive_models import WeatherPatternClassifier
from .predictive_models import WeatherPredictor

# Enhanced Weather Models with AI and Factory Patterns
from .weather_models import (
    AIEnhancedWeatherModel,  # Core entities; Enhanced enums; Protocols and base classes; Factory and Builder patterns; API Response models; Type aliases; Convenience functions
)
from .weather_models import APIResponse
from .weather_models import AtmosphericPressure
from .weather_models import CurrentWeather
from .weather_models import CurrentWeatherBuilder
from .weather_models import FavoriteCity
from .weather_models import ForecastAPIResponse
from .weather_models import ForecastData
from .weather_models import Location
from .weather_models import LocationData
from .weather_models import Precipitation
from .weather_models import Temperature
from .weather_models import TemperatureUnit
from .weather_models import WeatherAlert
from .weather_models import WeatherAnalyzer
from .weather_models import WeatherAPIResponse
from .weather_models import WeatherCondition
from .weather_models import WeatherData
from .weather_models import WeatherFactory
from .weather_models import WeatherForecast
from .weather_models import WeatherForecastDay
from .weather_models import Wind
from .weather_models import create_location_from_dict
from .weather_models import create_weather_from_api_response

__all__ = [
    # === Enhanced Enums ===
    "WeatherCondition",
    "TemperatureUnit",
    "ActivityType",
    "ActivityDifficulty",
    "MoodType",
    "WeatherImpact",
    "PoemType",
    "TemperatureRange",
    "SeasonalPreference",
    "ModelType",
    # === Core Weather Entities ===
    "Location",
    "Temperature",
    "Wind",
    "Precipitation",
    "AtmosphericPressure",
    "CurrentWeather",
    "WeatherForecastDay",
    "WeatherForecast",
    "WeatherAlert",
    "FavoriteCity",
    # === Capstone Entities ===
    "WeatherComparison",
    "JournalEntry",
    "Activity",
    "ActivitySuggestion",
    "WeatherPoem",
    # === Database Models ===
    "UserPreferences",
    "FavoriteCities",
    "JournalEntries",
    "WeatherHistory",
    "ActivityRecommendations",
    # === Predictive Models ===
    "EnhancedWeatherPredictor",
    "WeatherPatternClassifier",
    "PredictionResult",
    "ModelMetrics",
    # === Protocols and Abstract Classes ===
    "ModelProtocol",
    "AIEnhancedModel",
    "ExtensibleEnum",
    "WeatherAnalyzer",
    "AIEnhancedWeatherModel",
    "DatabaseAIEnhancedMixin",
    "WeatherPredictor",
    "DatabaseRepository",
    "AuditMixin",
    # === Factory Patterns ===
    "ActivityFactory",
    "WeatherFactory",
    "DatabaseModelFactory",
    "PredictiveModelFactory",
    # === Builder Patterns ===
    "WeatherComparisonBuilder",
    "CurrentWeatherBuilder",
    # === Strategy Patterns ===
    "ComparisonStrategy",
    "DefaultComparisonStrategy",
    "OutdoorActivityStrategy",
    "PredictionStrategy",
    "MLPredictionStrategy",
    "AIPredictionStrategy",
    # === Repository Patterns ===
    "BaseRepository",
    "UserPreferencesRepository",
    "FavoriteCitiesRepository",
    "JournalEntriesRepository",
    # === API Response Models ===
    "APIResponse",
    "WeatherAPIResponse",
    "ForecastAPIResponse",
    # === Type Aliases ===
    "WeatherData",
    "ForecastData",
    "LocationData",
    # === Convenience Functions ===
    "create_activity_suggestions",
    "create_journal_entry_from_weather",
    "create_weather_poem",
    "create_location_from_dict",
    "create_weather_from_api_response",
    # === Database Utilities ===
    "Base",
    "engine",
    "SessionLocal",
    "get_db_session",
    "close_db_session",
    "init_database",
    "init_enhanced_database",
]
