"""Models package for the Weather Dashboard application."""

from .weather_models import (
    # Enums
    WeatherCondition,
    TemperatureUnit,
    
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
    
    # API Response models
    APIResponse,
    WeatherAPIResponse,
    ForecastAPIResponse,
    
    # Type aliases
    WeatherData,
    ForecastData,
    LocationData
)

from .capstone_models import (
    # Enums
    ActivityType,
    MoodType,
    
    # Capstone entities
    WeatherComparison,
    JournalEntry,
    Activity,
    ActivitySuggestion,
    WeatherPoem,
    
    # Default data
    DEFAULT_ACTIVITIES
)

__all__ = [
    # Enums
    'WeatherCondition',
    'TemperatureUnit',
    'ActivityType',
    'MoodType',
    
    # Core entities
    'Location',
    'Temperature',
    'Wind',
    'Precipitation',
    'AtmosphericPressure',
    'CurrentWeather',
    'WeatherForecastDay',
    'WeatherForecast',
    'WeatherAlert',
    'FavoriteCity',
    
    # Capstone entities
    'WeatherComparison',
    'JournalEntry',
    'Activity',
    'ActivitySuggestion',
    'WeatherPoem',
    
    # API Response models
    'APIResponse',
    'WeatherAPIResponse',
    'ForecastAPIResponse',
    
    # Type aliases
    'WeatherData',
    'ForecastData',
    'LocationData',
    
    # Default data
    'DEFAULT_ACTIVITIES'
]
