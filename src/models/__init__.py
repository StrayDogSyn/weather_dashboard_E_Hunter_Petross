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
from .capstone_models import (  # Core entities; Enhanced enums; Factory and Builder patterns; Protocols and base classes; Convenience functions
    Activity,
    ActivityDifficulty,
    ActivityFactory,
    ActivitySuggestion,
    ActivityType,
    AIEnhancedModel,
    ComparisonStrategy,
    DefaultComparisonStrategy,
    ExtensibleEnum,
    JournalEntry,
    ModelProtocol,
    MoodType,
    OutdoorActivityStrategy,
    PoemType,
    SeasonalPreference,
    TemperatureRange,
    WeatherComparison,
    WeatherComparisonBuilder,
    WeatherImpact,
    WeatherPoem,
    create_activity_suggestions,
    create_journal_entry_from_weather,
    create_weather_poem,
)

# Enhanced Database Models with Repository Pattern
from .database_models import ActivityRecommendations
from .database_models import (
    AIEnhancedMixin as DatabaseAIEnhancedMixin,  # ORM Models; Repository pattern; Factory pattern; Protocols and mixins; Database utilities
)
from .database_models import (
    AuditMixin,
    Base,
    BaseRepository,
    DatabaseModelFactory,
    DatabaseRepository,
    FavoriteCities,
    FavoriteCitiesRepository,
    JournalEntries,
    JournalEntriesRepository,
    SessionLocal,
    UserPreferences,
    UserPreferencesRepository,
    WeatherHistory,
    close_db_session,
    engine,
    get_db_session,
    init_database,
    init_enhanced_database,
)

# Enhanced Predictive Models with AI Integration
from .predictive_models import (  # Core prediction classes; Strategy patterns; Factory pattern; Abstract classes
    AIPredictionStrategy,
    EnhancedWeatherPredictor,
    MLPredictionStrategy,
    ModelMetrics,
    ModelType,
    PredictionResult,
    PredictionStrategy,
    PredictiveModelFactory,
    WeatherPatternClassifier,
    WeatherPredictor,
)

# Enhanced Weather Models with AI and Factory Patterns
from .weather_models import (  # Core entities; Enhanced enums; Protocols and base classes; Factory and Builder patterns; API Response models; Type aliases; Convenience functions
    AIEnhancedWeatherModel,
    APIResponse,
    AtmosphericPressure,
    CurrentWeather,
    CurrentWeatherBuilder,
    FavoriteCity,
    ForecastAPIResponse,
    ForecastData,
    Location,
    LocationData,
    Precipitation,
    Temperature,
    TemperatureUnit,
    WeatherAlert,
    WeatherAnalyzer,
    WeatherAPIResponse,
    WeatherCondition,
    WeatherData,
    WeatherFactory,
    WeatherForecast,
    WeatherForecastDay,
    Wind,
    create_location_from_dict,
    create_weather_from_api_response,
)

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
