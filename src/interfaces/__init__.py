"""Interfaces package for the Weather Dashboard application."""

from .weather_interfaces import ICacheService, IDataStorage, IUserInterface, IWeatherAPI

__all__ = ["IWeatherAPI", "IDataStorage", "ICacheService", "IUserInterface"]
