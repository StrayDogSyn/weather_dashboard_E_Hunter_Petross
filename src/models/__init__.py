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

__all__ = [
    # Enums
    'WeatherCondition',
    'TemperatureUnit',
    
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
    
    # API Response models
    'APIResponse',
    'WeatherAPIResponse',
    'ForecastAPIResponse',
    
    # Type aliases
    'WeatherData',
    'ForecastData',
    'LocationData'
]
