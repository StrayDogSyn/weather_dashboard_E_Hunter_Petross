"""Interfaces package for the Weather Dashboard application."""

from .weather_interfaces import ICacheService
from .weather_interfaces import IDataStorage
from .weather_interfaces import IUserInterface
from .weather_interfaces import IWeatherAPI

__all__ = ["IWeatherAPI", "IDataStorage", "ICacheService", "IUserInterface"]
