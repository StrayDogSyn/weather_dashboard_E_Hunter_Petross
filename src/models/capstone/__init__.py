"""Enhanced Capstone Models for Weather Dashboard.

This package contains modular implementations of advanced models with
flexible design patterns, split into domain-specific modules for
better maintainability and organization.

Modules:
- base: Core interfaces, protocols, and base classes
- comparison: City comparison models and strategies
- journal: Weather journaling models
- activities: Activity suggestion models
- poetry: Weather poetry generation models
- factories: Factory patterns for model creation
"""

# Import all public classes for backward compatibility
from .activities import (
    Activity,
    ActivityDifficulty,
    ActivityRequirements,
    ActivitySuggestion,
    ActivityType,
    SeasonalPreference,
)
from .base import AIEnhancedModel, ExtensibleEnum, ModelProtocol
from .comparison import (
    ComparisonStrategy,
    DefaultComparisonStrategy,
    OutdoorActivityStrategy,
    WeatherComparison,
)
from .factories import ActivityFactory, WeatherComparisonBuilder
from .journal import JournalEntry, MoodType, WeatherImpact, WeatherMoodCorrelation
from .poetry import PoemMetadata, PoemType, TemperatureRange, WeatherPoem

# Maintain backward compatibility
__all__ = [
    # Base classes
    "ModelProtocol",
    "AIEnhancedModel",
    "ExtensibleEnum",
    # Enums
    "ActivityType",
    "MoodType",
    "WeatherImpact",
    "ActivityDifficulty",
    "SeasonalPreference",
    "PoemType",
    "TemperatureRange",
    # Models
    "WeatherComparison",
    "WeatherMoodCorrelation",
    "JournalEntry",
    "Activity",
    "ActivitySuggestion",
    "WeatherPoem",
    "PoemMetadata",
    "ActivityRequirements",
    # Strategies
    "ComparisonStrategy",
    "DefaultComparisonStrategy",
    "OutdoorActivityStrategy",
    # Factories
    "ActivityFactory",
    "WeatherComparisonBuilder",
]
