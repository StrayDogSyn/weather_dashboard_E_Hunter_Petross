"""Shared utilities and common components for Weather Dashboard.

This package contains utilities, constants, exceptions, and other
shared components used across the application.
"""

from .exceptions import (
    WeatherDashboardError,
    DependencyInjectionError,
    ConfigurationError,
    ValidationError,
    ServiceError,
)
from .constants import (
    DEFAULT_CACHE_TTL,
    MAX_FORECAST_DAYS,
    DEFAULT_TEMPERATURE_UNIT,
    API_TIMEOUT,
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