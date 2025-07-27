"""
Enhanced Capstone Models for Weather Dashboard.

This module provides backward compatibility imports from the new modular structure.
The models have been split into domain-specific modules for better maintainability:

- base: Core interfaces and AI-enhanced models
- comparison: Weather comparison models and strategies
- journal: Weather journaling and mood tracking
- activities: Activity suggestions and management
- poetry: Weather poetry generation
- factories: Factory patterns for model creation

For new code, import directly from the specific modules in the capstone package.
"""

# Import all classes from the modular structure for backward compatibility
from .capstone import *

# Explicit imports to maintain the same interface
from .capstone.activities import Activity
from .capstone.activities import ActivityDifficulty
from .capstone.activities import ActivityRequirements
from .capstone.activities import ActivitySuggestion
from .capstone.activities import ActivityType
from .capstone.activities import SeasonalPreference
from .capstone.base import AIEnhancedModel
from .capstone.base import ExtensibleEnum
from .capstone.base import ModelProtocol
from .capstone.comparison import ComparisonStrategy
from .capstone.comparison import DefaultComparisonStrategy
from .capstone.comparison import OutdoorActivityStrategy
from .capstone.comparison import WeatherComparison
from .capstone.factories import ActivityFactory
from .capstone.factories import WeatherComparisonBuilder
from .capstone.journal import JournalEntry
from .capstone.journal import MoodType
from .capstone.journal import WeatherImpact
from .capstone.journal import WeatherMoodCorrelation
from .capstone.poetry import PoemMetadata
from .capstone.poetry import PoemType
from .capstone.poetry import TemperatureRange
from .capstone.poetry import WeatherPoem

# Maintain exact same exports as before
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
