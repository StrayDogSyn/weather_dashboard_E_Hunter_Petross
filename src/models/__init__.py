"""Models package for the Weather Dashboard application."""

from .capstone_models import (  # Enums; Capstone entities; Enhanced models
    Activity,
    ActivityFactory,
    ActivitySuggestion,
    ActivityType,
    JournalEntry,
    MoodType,
    WeatherComparison,
    WeatherComparisonBuilder,
    WeatherPoem,
    # Enhanced enums
    ActivityDifficulty,
    WeatherImpact,
    PoemType,
    TemperatureRange,
    # Convenience functions
    create_activity_suggestions,
    create_journal_entry_from_weather,
    create_weather_poem,
)
from .weather_models import (  # Enums; Core entities; API Response models; Type aliases
    APIResponse,
    AtmosphericPressure,
    CurrentWeather,
    FavoriteCity,
    ForecastAPIResponse,
    ForecastData,
    Location,
    LocationData,
    Precipitation,
    Temperature,
    TemperatureUnit,
    WeatherAlert,
    WeatherAPIResponse,
    WeatherCondition,
    WeatherData,
    WeatherForecast,
    WeatherForecastDay,
    Wind,
)

__all__ = [
    # Enums
    "WeatherCondition",
    "TemperatureUnit",
    "ActivityType",
    "MoodType",
    # Core entities
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
    # Capstone entities
    "WeatherComparison",
    "JournalEntry",
    "Activity",
    "ActivitySuggestion",
    "WeatherPoem",
    # Enhanced enums
    "ActivityDifficulty",
    "WeatherImpact",
    "PoemType",
    "TemperatureRange",
    # Factory and builder patterns
    "ActivityFactory",
    "WeatherComparisonBuilder",
    # Convenience functions
    "create_activity_suggestions",
    "create_journal_entry_from_weather",
    "create_weather_poem",
    # API Response models
    "APIResponse",
    "WeatherAPIResponse",
    "ForecastAPIResponse",
    # Type aliases
    "WeatherData",
    "ForecastData",
    "LocationData",
    # Enhanced functionality - use ActivityFactory.get_default_activities() instead
]
