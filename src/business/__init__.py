"""Business layer for Weather Dashboard.

This package contains all business logic, domain models, and service interfaces
following Domain-Driven Design (DDD) principles and clean architecture.
"""

from .interfaces import (
    IActivitySuggestionService,
    ICacheService,
    ICityComparisonService,
    ICortanaVoiceService,
    IStorageService,
    IWeatherJournalService,
    IWeatherPoetryService,
    IWeatherService,
)

# Service implementations are in the core package
# from .services import (
#     ActivitySuggestionService,
#     CityComparisonService,
#     CortanaVoiceService,
#     WeatherJournalService,
#     WeatherPoetryService,
#     WeatherService,
# )

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
