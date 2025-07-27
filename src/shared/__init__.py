"""Shared utilities and common components for Weather Dashboard.

This package contains utilities, constants, exceptions, and other
shared components used across the application.
"""

from .constants import API_TIMEOUT
from .constants import DEFAULT_CACHE_TTL
from .constants import DEFAULT_TEMPERATURE_UNIT
from .constants import MAX_FORECAST_DAYS
from .exceptions import ConfigurationError
from .exceptions import DependencyInjectionError
from .exceptions import ServiceError
from .exceptions import ValidationError
from .exceptions import WeatherDashboardError

__all__ = [
    "WeatherDashboardError",
    "DependencyInjectionError",
    "ConfigurationError",
    "ValidationError",
    "ServiceError",
    "DEFAULT_CACHE_TTL",
    "MAX_FORECAST_DAYS",
    "DEFAULT_TEMPERATURE_UNIT",
    "API_TIMEOUT",
]
