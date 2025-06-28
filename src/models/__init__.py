"""Models package for the Weather Dashboard application."""

from .capstone_models import (  # Enums; Capstone entities; Default data
    DEFAULT_ACTIVITIES,
    Activity,
    ActivitySuggestion,
    ActivityType,
    JournalEntry,
    MoodType,
    WeatherComparison,
    WeatherPoem,
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
    # API Response models
    "APIResponse",
    "WeatherAPIResponse",
    "ForecastAPIResponse",
    # Type aliases
    "WeatherData",
    "ForecastData",
    "LocationData",
    # Default data
    "DEFAULT_ACTIVITIES",
]
