"""Business layer for Weather Dashboard.

This package contains all business logic, domain models, and service interfaces
following Domain-Driven Design (DDD) principles and clean architecture.
"""

from .interfaces import IActivitySuggestionService
from .interfaces import ICacheService
from .interfaces import ICityComparisonService
from .interfaces import ICortanaVoiceService
from .interfaces import IStorageService
from .interfaces import IWeatherJournalService
from .interfaces import IWeatherPoetryService
from .interfaces import IWeatherService

# Service implementations are in the core package

__all__ = [
    # Interfaces
    "IWeatherService",
    "ICityComparisonService",
    "IWeatherJournalService",
    "IActivitySuggestionService",
    "IWeatherPoetryService",
    "ICortanaVoiceService",
    "ICacheService",
    "IStorageService",
    # Service implementations are in the core package
]
