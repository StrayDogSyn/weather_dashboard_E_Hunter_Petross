"""Interfaces package for the Weather Dashboard application."""

from .weather_interfaces import (
    IWeatherAPI,
    IDataStorage,
    ICacheService,
    IUserInterface
)

__all__ = [
    'IWeatherAPI',
    'IDataStorage', 
    'ICacheService',
    'IUserInterface'
]
