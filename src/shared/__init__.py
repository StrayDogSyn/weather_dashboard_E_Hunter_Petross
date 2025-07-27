"""Shared utilities and common components for Weather Dashboard.

This package contains utilities, constants, exceptions, and other
shared components used across the application.
"""

from .constants import (
    API_TIMEOUT,
    DEFAULT_CACHE_TTL,
    DEFAULT_TEMPERATURE_UNIT,
    MAX_FORECAST_DAYS,
)
from .exceptions import (
    ConfigurationError,
    DependencyInjectionError,
    ServiceError,
    ValidationError,
    WeatherDashboardError,
)

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
