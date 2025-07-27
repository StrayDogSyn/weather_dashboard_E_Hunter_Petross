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
from .activities import Activity
from .activities import ActivityDifficulty
from .activities import ActivityRequirements
from .activities import ActivitySuggestion
from .activities import ActivityType
from .activities import SeasonalPreference
from .base import AIEnhancedModel
from .base import ExtensibleEnum
from .base import ModelProtocol
from .comparison import ComparisonStrategy
from .comparison import DefaultComparisonStrategy
from .comparison import OutdoorActivityStrategy
from .comparison import WeatherComparison
from .factories import ActivityFactory
from .factories import WeatherComparisonBuilder
from .journal import JournalEntry
from .journal import MoodType
from .journal import WeatherImpact
from .journal import WeatherMoodCorrelation
from .poetry import PoemMetadata
from .poetry import PoemType
from .poetry import TemperatureRange
from .poetry import WeatherPoem

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
