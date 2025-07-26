"""Business layer for Weather Dashboard.

This package contains all business logic, domain models, and service interfaces
following Domain-Driven Design (DDD) principles and clean architecture.
"""

from .interfaces import (
    IWeatherService,
    ICityComparisonService,
    IWeatherJournalService,
    IActivitySuggestionService,
    IWeatherPoetryService,
    ICortanaVoiceService,
    ICacheService,
    IStorageService,
)

from .services import (
    WeatherService,
    CityComparisonService,
    WeatherJournalService,
    ActivitySuggestionService,
    WeatherPoetryService,
    CortanaVoiceService,
)

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
    # Implementations
    "WeatherService",
    "CityComparisonService",
    "WeatherJournalService",
    "ActivitySuggestionService",
    "WeatherPoetryService",
    "CortanaVoiceService",
]