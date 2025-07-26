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
    # Core entities
    Activity,
    ActivitySuggestion,
    JournalEntry,
    WeatherComparison,
    WeatherPoem,
    # Enhanced enums
    ActivityType,
    ActivityDifficulty,
    MoodType,
    WeatherImpact,
    PoemType,
    TemperatureRange,
    SeasonalPreference,
    # Factory and Builder patterns
    ActivityFactory,
    WeatherComparisonBuilder,
    # Protocols and base classes
    ModelProtocol,
    AIEnhancedModel,
    ExtensibleEnum,
    ComparisonStrategy,
    DefaultComparisonStrategy,
    OutdoorActivityStrategy,
    # Convenience functions
    create_activity_suggestions,
    create_journal_entry_from_weather,
    create_weather_poem,
)

# Enhanced Weather Models with AI and Factory Patterns
from .weather_models import (
    # Core entities
    Location,
    Temperature,
    Wind,
    Precipitation,
    AtmosphericPressure,
    CurrentWeather,
    WeatherForecastDay,
    WeatherForecast,
    WeatherAlert,
    FavoriteCity,
    # Enhanced enums
    WeatherCondition,
    TemperatureUnit,
    # Protocols and base classes
    WeatherAnalyzer,
    AIEnhancedWeatherModel,
    # Factory and Builder patterns
    WeatherFactory,
    CurrentWeatherBuilder,
    # API Response models
    APIResponse,
    WeatherAPIResponse,
    ForecastAPIResponse,
    # Type aliases
    WeatherData,
    ForecastData,
    LocationData,
    # Convenience functions
    create_location_from_dict,
    create_weather_from_api_response,
)

# Enhanced Database Models with Repository Pattern
from .database_models import (
    # ORM Models
    UserPreferences,
    FavoriteCities,
    JournalEntries,
    WeatherHistory,
    ActivityRecommendations,
    # Repository pattern
    BaseRepository,
    UserPreferencesRepository,
    FavoriteCitiesRepository,
    JournalEntriesRepository,
    # Factory pattern
    DatabaseModelFactory,
    # Protocols and mixins
    DatabaseRepository,
    AuditMixin,
    AIEnhancedMixin as DatabaseAIEnhancedMixin,
    # Database utilities
    Base,
    engine,
    SessionLocal,
    get_db_session,
    close_db_session,
    init_database,
    init_enhanced_database,
)

# Enhanced Predictive Models with AI Integration
from .predictive_models import (
    # Core prediction classes
    EnhancedWeatherPredictor,
    WeatherPatternClassifier,
    PredictionResult,
    ModelMetrics,
    ModelType,
    # Strategy patterns
    PredictionStrategy,
    MLPredictionStrategy,
    AIPredictionStrategy,
    # Factory pattern
    PredictiveModelFactory,
    # Abstract classes
    WeatherPredictor,
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