"""
Enhanced Capstone Models for Weather Dashboard.

This module implements advanced models with flexible design patterns for:
- City Comparison with configurable metrics
- Weather Journal with rich metadata 
- Dynamic Activity Suggestions with AI integration
- Weather Poetry with multi-provider AI support
- Extensible frameworks for adding new features

Design Patterns Used:
- Factory Pattern for model creation
- Strategy Pattern for comparison algorithms
- Observer Pattern for model updates
- Builder Pattern for complex model construction
- Template Method Pattern for common operations
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union, Protocol, ClassVar
from uuid import uuid4, UUID

import google.generativeai as genai
from pydantic import BaseModel, Field, validator, root_validator

from .weather_models import CurrentWeather, Location, WeatherCondition


# ============================================================================
# Core Interfaces and Protocols
# ============================================================================

class ModelProtocol(Protocol):
    """Protocol for all capstone models with common operations."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        ...
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        ...
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelProtocol':
        """Create model from dictionary."""
        ...


class AIEnhancedModel(ABC):
    """Abstract base class for models that can be enhanced with AI."""
    
    @abstractmethod
    def generate_ai_content(self, gemini_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI-enhanced content for this model."""
        pass
    
    @abstractmethod
    def get_ai_prompt(self) -> str:
        """Get the AI prompt for content generation."""
        pass


# ============================================================================
# Enhanced Enums with Extensibility
# ============================================================================

class ExtensibleEnum(Enum):
    """Base class for enums that can be dynamically extended."""
    
    @classmethod
    def add_value(cls, name: str, value: str) -> None:
        """Dynamically add a new enum value."""
        setattr(cls, name.upper(), value)
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all enum values as strings."""
        return [item.value for item in cls]
    
    @classmethod
    def get_display_names(cls) -> Dict[str, str]:
        """Get human-readable display names."""
        return {item.value: item.name.replace('_', ' ').title() for item in cls}


class ActivityType(ExtensibleEnum):
    """Enhanced activity types with dynamic extensibility."""

    OUTDOOR_SPORTS = "outdoor_sports"
    INDOOR_ACTIVITIES = "indoor_activities"
    SIGHTSEEING = "sightseeing"
    EXERCISE = "exercise"
    RELAXATION = "relaxation"
    CULTURAL = "cultural"
    SHOPPING = "shopping"
    DINING = "dining"
    ADVENTURE = "adventure"
    CREATIVE = "creative"
    SOCIAL = "social"
    WELLNESS = "wellness"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    
    @property
    def emoji(self) -> str:
        """Get emoji representation for activity type."""
        emoji_map = {
            "outdoor_sports": "🏃‍♂️",
            "indoor_activities": "🏠",
            "sightseeing": "🏛️",
            "exercise": "💪",
            "relaxation": "😌",
            "cultural": "🎭",
            "shopping": "🛍️",
            "dining": "🍽️",
            "adventure": "🗻",
            "creative": "🎨",
            "social": "👥",
            "wellness": "🧘‍♀️",
            "educational": "📚",
            "entertainment": "🎬"
        }
        return emoji_map.get(self.value, "📝")


class MoodType(ExtensibleEnum):
    """Enhanced mood types with emotional intelligence."""

    HAPPY = "happy"
    SAD = "sad"
    ENERGETIC = "energetic"
    RELAXED = "relaxed"
    EXCITED = "excited"
    PEACEFUL = "peaceful"
    ANXIOUS = "anxious"
    CONTENT = "content"
    MOTIVATED = "motivated"
    COZY = "cozy"
    NOSTALGIC = "nostalgic"
    INSPIRED = "inspired"
    CONTEMPLATIVE = "contemplative"
    ADVENTUROUS = "adventurous"
    GRATEFUL = "grateful"
    
    @property
    def emoji(self) -> str:
        """Get emoji representation for mood."""
        emoji_map = {
            "happy": "😊",
            "sad": "😢",
            "energetic": "⚡",
            "relaxed": "😌",
            "excited": "🤩",
            "peaceful": "😇",
            "anxious": "😰",
            "content": "😊",
            "motivated": "💪",
            "cozy": "🤗",
            "nostalgic": "🥺",
            "inspired": "✨",
            "contemplative": "🤔",
            "adventurous": "🌟",
            "grateful": "🙏"
        }
        return emoji_map.get(self.value, "😐")
    
    @property
    def intensity(self) -> float:
        """Get emotional intensity scale (0.0 to 1.0)."""
        intensity_map = {
            "happy": 0.7,
            "sad": 0.6,
            "energetic": 0.9,
            "relaxed": 0.3,
            "excited": 0.9,
            "peaceful": 0.2,
            "anxious": 0.8,
            "content": 0.4,
            "motivated": 0.8,
            "cozy": 0.4,
            "nostalgic": 0.5,
            "inspired": 0.8,
            "contemplative": 0.4,
            "adventurous": 0.9,
            "grateful": 0.6
        }
        return intensity_map.get(self.value, 0.5)


class WeatherImpact(Enum):
    """How weather affects different aspects of life."""
    
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"
    
    @property
    def score(self) -> float:
        """Get numeric score for impact."""
        score_map = {
            "very_positive": 1.0,
            "positive": 0.75,
            "neutral": 0.5,
            "negative": 0.25,
            "very_negative": 0.0
        }
        return score_map[self.value]


# ============================================================================
# Weather Comparison Framework
# ============================================================================

class ComparisonStrategy(ABC):
    """Strategy pattern for different weather comparison algorithms."""
    
    @abstractmethod
    def calculate_score(self, weather: CurrentWeather, preferences: Optional[Dict[str, Any]] = None) -> float:
        """Calculate weather score based on strategy."""
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get human-readable strategy name."""
        pass


class DefaultComparisonStrategy(ComparisonStrategy):
    """Default weather comparison strategy focusing on comfort."""
    
    def calculate_score(self, weather: CurrentWeather, preferences: Optional[Dict[str, Any]] = None) -> float:
        """Calculate comfort-based weather score."""
        score = 0.0
        prefs = preferences or {}
        
        # Temperature score (configurable ideal range)
        temp_c = weather.temperature.to_celsius()
        ideal_min = prefs.get('ideal_temp_min', 18)
        ideal_max = prefs.get('ideal_temp_max', 26)
        
        if ideal_min <= temp_c <= ideal_max:
            score += 10
        elif ideal_min - 5 <= temp_c <= ideal_max + 5:
            score += 7
        elif ideal_min - 10 <= temp_c <= ideal_max + 10:
            score += 4
        
        # Humidity score
        humidity_weight = prefs.get('humidity_weight', 1.0)
        if 30 <= weather.humidity <= 60:
            score += 5 * humidity_weight
        elif 20 <= weather.humidity <= 70:
            score += 3 * humidity_weight
        
        # Wind score
        wind_weight = prefs.get('wind_weight', 1.0)
        if 5 <= weather.wind.speed <= 15:
            score += 3 * wind_weight
        elif weather.wind.speed <= 25:
            score += 1 * wind_weight
        
        # Condition score
        condition_preferences = prefs.get('preferred_conditions', [WeatherCondition.CLEAR])
        if weather.condition in condition_preferences:
            score += 8
        elif weather.condition == WeatherCondition.CLEAR:
            score += 6
        elif weather.condition == WeatherCondition.CLOUDS:
            score += 4
        
        return score
    
    def get_strategy_name(self) -> str:
        return "Comfort-Based Comparison"


class OutdoorActivityStrategy(ComparisonStrategy):
    """Weather comparison strategy optimized for outdoor activities."""
    
    def calculate_score(self, weather: CurrentWeather, preferences: Optional[Dict[str, Any]] = None) -> float:
        """Calculate outdoor activity suitability score."""
        score = 0.0
        
        # Prioritize clear weather
        if weather.condition == WeatherCondition.CLEAR:
            score += 15
        elif weather.condition == WeatherCondition.CLOUDS:
            score += 10
        elif weather.condition in [WeatherCondition.RAIN, WeatherCondition.SNOW]:
            score += 2
        
        # Moderate temperatures preferred
        temp_c = weather.temperature.to_celsius()
        if 15 <= temp_c <= 28:
            score += 10
        elif 10 <= temp_c <= 32:
            score += 5
        
        # Low wind preferred
        if weather.wind.speed <= 20:
            score += 5
        elif weather.wind.speed <= 35:
            score += 2
        
        return score
    
    def get_strategy_name(self) -> str:
        return "Outdoor Activity Optimized"


@dataclass
class WeatherComparison(AIEnhancedModel):
    """Enhanced weather comparison with configurable strategies and AI insights."""
    
    city1_weather: CurrentWeather
    city2_weather: CurrentWeather
    id: UUID = field(default_factory=uuid4)
    comparison_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    strategy: ComparisonStrategy = field(default_factory=DefaultComparisonStrategy)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    ai_insights: Optional[Dict[str, Any]] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize comparison with calculated metrics."""
        self._calculate_all_metrics()
    
    def _calculate_all_metrics(self) -> None:
        """Calculate all comparison metrics."""
        self.custom_metrics.update({
            'city1_score': self.strategy.calculate_score(self.city1_weather, self.user_preferences),
            'city2_score': self.strategy.calculate_score(self.city2_weather, self.user_preferences),
            'temperature_difference': self.temperature_difference,
            'humidity_difference': self.humidity_difference,
            'pressure_difference': self.pressure_difference,
            'wind_speed_difference': self.wind_speed_difference
        })
    
    @property
    def temperature_difference(self) -> float:
        """Get temperature difference between cities (city1 - city2)."""
        temp1 = self.city1_weather.temperature.to_celsius()
        temp2 = self.city2_weather.temperature.to_celsius()
        return temp1 - temp2
    
    @property
    def humidity_difference(self) -> int:
        """Get humidity difference between cities (city1 - city2)."""
        return self.city1_weather.humidity - self.city2_weather.humidity
    
    @property
    def pressure_difference(self) -> float:
        """Get pressure difference between cities (city1 - city2)."""
        pressure1 = getattr(self.city1_weather, 'pressure', None)
        pressure2 = getattr(self.city2_weather, 'pressure', None)
        if pressure1 and pressure2:
            return pressure1.value - pressure2.value
        return 0.0
    
    @property
    def wind_speed_difference(self) -> float:
        """Get wind speed difference between cities (city1 - city2)."""
        return self.city1_weather.wind.speed - self.city2_weather.wind.speed
    
    @property
    def warmer_city(self) -> str:
        """Get name of the warmer city."""
        if self.temperature_difference > 0.5:
            return self.city1_weather.location.display_name
        elif self.temperature_difference < -0.5:
            return self.city2_weather.location.display_name
        else:
            return "Similar temperature"
    
    @property
    def preferred_city(self) -> str:
        """Get the preferred city based on current strategy."""
        score1 = self.custom_metrics.get('city1_score', 0)
        score2 = self.custom_metrics.get('city2_score', 0)
        
        if score1 > score2 + 1:  # Add threshold to avoid minor differences
            return self.city1_weather.location.display_name
        elif score2 > score1 + 1:
            return self.city2_weather.location.display_name
        else:
            return "Similar weather quality"
    
    def set_strategy(self, strategy: ComparisonStrategy) -> None:
        """Change comparison strategy and recalculate metrics."""
        self.strategy = strategy
        self._calculate_all_metrics()
    
    def add_custom_metric(self, name: str, calculator: callable) -> None:
        """Add a custom comparison metric."""
        try:
            value = calculator(self.city1_weather, self.city2_weather)
            self.custom_metrics[name] = value
        except Exception as e:
            logging.warning(f"Failed to calculate custom metric '{name}': {e}")
    
    def generate_ai_content(self, gemini_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI insights about the weather comparison."""
        if not gemini_api_key:
            return {"error": "Gemini API key not provided"}
        
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = self.get_ai_prompt()
            response = model.generate_content(prompt)
            
            insights = {
                "summary": response.text[:200] + "..." if len(response.text) > 200 else response.text,
                "detailed_analysis": response.text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "comparison_id": str(self.id)
            }
            
            self.ai_insights = insights
            return insights
            
        except Exception as e:
            logging.error(f"Failed to generate AI insights: {e}")
            return {"error": f"AI generation failed: {str(e)}"}
    
    def get_ai_prompt(self) -> str:
        """Generate AI prompt for weather comparison analysis."""
        return f"""
        Analyze and compare the weather between these two cities:
        
        City 1: {self.city1_weather.location.display_name}
        - Temperature: {self.city1_weather.temperature.to_celsius():.1f}°C
        - Condition: {self.city1_weather.condition.value}
        - Humidity: {self.city1_weather.humidity}%
        - Wind: {self.city1_weather.wind.speed} km/h
        
        City 2: {self.city2_weather.location.display_name}
        - Temperature: {self.city2_weather.temperature.to_celsius():.1f}°C
        - Condition: {self.city2_weather.condition.value}
        - Humidity: {self.city2_weather.humidity}%
        - Wind: {self.city2_weather.wind.speed} km/h
        
        Strategy: {self.strategy.get_strategy_name()}
        
        Provide a brief, insightful comparison focusing on:
        1. Which city has more favorable conditions and why
        2. Best activities for each city's current weather
        3. Any notable weather patterns or differences
        
        Keep the response concise but informative (under 150 words).
        """
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "city1": self.city1_weather.location.display_name,
            "city2": self.city2_weather.location.display_name,
            "timestamp": self.comparison_timestamp.isoformat(),
            "strategy": self.strategy.get_strategy_name(),
            "metrics": self.custom_metrics,
            "preferences": self.user_preferences,
            "ai_insights": self.ai_insights
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherComparison':
        """Create instance from dictionary (partial implementation)."""
        # This would need full implementation with weather data reconstruction
        raise NotImplementedError("Dictionary reconstruction not yet implemented")


# ============================================================================
# Enhanced Journal System
# ============================================================================

@dataclass
class WeatherMoodCorrelation:
    """Represents correlation between weather and mood."""
    
    weather_condition: WeatherCondition
    temperature_range: Tuple[float, float]  # Min, Max in Celsius
    mood_impact: WeatherImpact
    correlation_strength: float = field(default=0.5)  # 0.0 to 1.0
    notes: str = ""
    
    def matches_weather(self, weather: CurrentWeather) -> bool:
        """Check if weather matches this correlation pattern."""
        temp_c = weather.temperature.to_celsius()
        return (
            weather.condition == self.weather_condition and
            self.temperature_range[0] <= temp_c <= self.temperature_range[1]
        )


@dataclass 
class JournalEntry(AIEnhancedModel):
    """Enhanced weather journal entry with rich metadata and AI insights."""
    
    date: date
    location: str
    id: UUID = field(default_factory=uuid4)
    weather_data: Optional[CurrentWeather] = None
    weather_summary: str = ""
    temperature: float = 0.0
    condition: str = ""
    mood: MoodType = MoodType.CONTENT
    energy_level: int = field(default=5)  # 1-10 scale
    notes: str = ""
    activities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    weather_impact: WeatherImpact = WeatherImpact.NEUTRAL
    mood_correlations: List[WeatherMoodCorrelation] = field(default_factory=list)
    photos: List[str] = field(default_factory=list)  # Photo paths/URLs
    ai_reflections: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Initialize journal entry with derived data."""
        if self.weather_data:
            self.weather_summary = f"{self.weather_data.condition.value.title()}, {self.weather_data.temperature.to_celsius():.1f}°C"
            self.temperature = self.weather_data.temperature.to_celsius()
            self.condition = self.weather_data.condition.value
    
    @property
    def formatted_date(self) -> str:
        """Get formatted date string."""
        return self.date.strftime("%Y-%m-%d")
    
    @property
    def mood_emoji(self) -> str:
        """Get emoji for the mood."""
        return self.mood.emoji
    
    @property
    def energy_emoji(self) -> str:
        """Get emoji for energy level."""
        if self.energy_level >= 8:
            return "🔥"
        elif self.energy_level >= 6:
            return "⚡"
        elif self.energy_level >= 4:
            return "🔋"
        else:
            return "😴"
    
    @property
    def impact_emoji(self) -> str:
        """Get emoji for weather impact."""
        impact_emojis = {
            WeatherImpact.VERY_POSITIVE: "🌟",
            WeatherImpact.POSITIVE: "👍",
            WeatherImpact.NEUTRAL: "😐",
            WeatherImpact.NEGATIVE: "👎", 
            WeatherImpact.VERY_NEGATIVE: "💔"
        }
        return impact_emojis[self.weather_impact]
    
    def add_activity(self, activity: str, category: Optional[ActivityType] = None) -> None:
        """Add an activity with optional categorization."""
        if activity not in self.activities:
            self.activities.append(activity)
            if category:
                self.tags.append(f"activity:{category.value}")
        self.updated_at = datetime.now(timezone.utc)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the entry."""
        if tag not in self.tags:
            self.tags.append(tag.lower())
        self.updated_at = datetime.now(timezone.utc)
    
    def calculate_mood_weather_correlation(self) -> float:
        """Calculate correlation between mood and weather conditions."""
        if not self.weather_data:
            return 0.0
        
        # Simple correlation based on typical weather-mood relationships
        base_score = 0.5
        
        # Temperature correlation
        temp_c = self.weather_data.temperature.to_celsius()
        if 18 <= temp_c <= 26:  # Ideal range
            temp_factor = 1.0
        elif 15 <= temp_c <= 30:  # Good range
            temp_factor = 0.8
        else:
            temp_factor = 0.4
        
        # Condition correlation
        condition_factors = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.CLOUDS: 0.7,
            WeatherCondition.RAIN: 0.3,
            WeatherCondition.SNOW: 0.6,
            WeatherCondition.THUNDERSTORM: 0.2
        }
        condition_factor = condition_factors.get(self.weather_data.condition, 0.5)
        
        # Mood intensity factor
        mood_factor = self.mood.intensity
        
        correlation = (base_score + temp_factor + condition_factor + mood_factor) / 4
        return min(1.0, max(0.0, correlation))
    
    def generate_ai_content(self, gemini_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI reflections and insights about the journal entry."""
        if not gemini_api_key:
            return {"error": "Gemini API key not provided"}
        
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = self.get_ai_prompt()
            response = model.generate_content(prompt)
            
            reflections = {
                "insights": response.text,
                "mood_analysis": self._analyze_mood_patterns(),
                "activity_suggestions": self._get_activity_suggestions(),
                "weather_correlation": self.calculate_mood_weather_correlation(),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "entry_id": str(self.id)
            }
            
            self.ai_reflections = reflections
            return reflections
            
        except Exception as e:
            logging.error(f"Failed to generate AI reflections: {e}")
            return {"error": f"AI generation failed: {str(e)}"}
    
    def get_ai_prompt(self) -> str:
        """Generate AI prompt for journal reflection."""
        return f"""
        Analyze this weather journal entry and provide thoughtful insights:
        
        Date: {self.formatted_date}
        Location: {self.location}
        Weather: {self.weather_summary}
        Mood: {self.mood.value} ({self.mood_emoji})
        Energy Level: {self.energy_level}/10
        Weather Impact: {self.weather_impact.value}
        Activities: {', '.join(self.activities) if self.activities else 'None listed'}
        Notes: {self.notes if self.notes else 'No additional notes'}
        
        Please provide:
        1. Insights about the relationship between weather and mood
        2. Patterns you notice in activities and weather conditions
        3. Suggestions for optimizing well-being based on weather
        4. Any interesting observations about this particular day
        
        Keep the response encouraging and insightful (under 200 words).
        """
    
    def _analyze_mood_patterns(self) -> Dict[str, Any]:
        """Analyze mood patterns (placeholder for future implementation)."""
        return {
            "primary_mood": self.mood.value,
            "intensity": self.mood.intensity,
            "energy_alignment": abs(self.energy_level - 5) / 5,  # How far from neutral
            "weather_correlation": self.calculate_mood_weather_correlation()
        }
    
    def _get_activity_suggestions(self) -> List[str]:
        """Get activity suggestions based on current state."""
        suggestions = []
        
        if self.energy_level >= 7:
            suggestions.extend(["Try a new outdoor adventure", "Engage in physical exercise"])
        elif self.energy_level <= 3:
            suggestions.extend(["Practice relaxation techniques", "Enjoy quiet indoor activities"])
        
        if self.mood in [MoodType.SAD, MoodType.ANXIOUS]:
            suggestions.extend(["Connect with friends", "Practice mindfulness"])
        elif self.mood in [MoodType.EXCITED, MoodType.ENERGETIC]:
            suggestions.extend(["Channel energy into creative projects", "Try new experiences"])
        
        return suggestions[:3]  # Limit to top 3 suggestions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "date": self.date.isoformat(),
            "location": self.location,
            "weather_summary": self.weather_summary,
            "temperature": self.temperature,
            "condition": self.condition,
            "mood": self.mood.value,
            "energy_level": self.energy_level,
            "notes": self.notes,
            "activities": self.activities,
            "tags": self.tags,
            "weather_impact": self.weather_impact.value,
            "ai_reflections": self.ai_reflections,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'JournalEntry':
        """Create instance from dictionary."""
        # Convert string dates back to date objects
        entry_date = datetime.fromisoformat(data['date']).date()
        created_at = datetime.fromisoformat(data['created_at'])
        updated_at = datetime.fromisoformat(data['updated_at'])
        
        return cls(
            id=UUID(data['id']),
            date=entry_date,
            location=data['location'],
            weather_summary=data['weather_summary'],
            temperature=data['temperature'],
            condition=data['condition'],
            mood=MoodType(data['mood']),
            energy_level=data['energy_level'],
            notes=data['notes'],
            activities=data['activities'],
            tags=data['tags'],
            weather_impact=WeatherImpact(data['weather_impact']),
            ai_reflections=data.get('ai_reflections'),
            created_at=created_at,
            updated_at=updated_at
        )


# ============================================================================
# Enhanced Activity System with AI Integration
# ============================================================================

class ActivityDifficulty(Enum):
    """Activity difficulty levels."""
    
    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"
    EXPERT = "expert"
    
    @property
    def emoji(self) -> str:
        """Get emoji for difficulty level."""
        emoji_map = {
            "easy": "🟢",
            "moderate": "🟡",
            "challenging": "🟠",
            "expert": "🔴"
        }
        return emoji_map[self.value]


class SeasonalPreference(Enum):
    """Seasonal activity preferences."""
    
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"
    ALL_YEAR = "all_year"


@dataclass
class ActivityRequirements:
    """Detailed requirements for an activity."""
    
    min_temperature: Optional[float] = None  # Celsius
    max_temperature: Optional[float] = None  # Celsius
    max_wind_speed: Optional[float] = None  # km/h
    max_humidity: Optional[int] = None  # Percentage
    requires_clear_weather: bool = False
    avoid_conditions: List[WeatherCondition] = field(default_factory=list)
    preferred_time_of_day: List[str] = field(default_factory=lambda: ["morning", "afternoon", "evening"])
    seasonal_preference: SeasonalPreference = SeasonalPreference.ALL_YEAR
    equipment_needed: List[str] = field(default_factory=list)
    
    def check_weather_compatibility(self, weather: CurrentWeather) -> Tuple[bool, List[str]]:
        """Check weather compatibility and return reasons for incompatibility."""
        issues = []
        
        temp_c = weather.temperature.to_celsius()
        if self.min_temperature is not None and temp_c < self.min_temperature:
            issues.append(f"Temperature too low ({temp_c:.1f}°C < {self.min_temperature}°C)")
        if self.max_temperature is not None and temp_c > self.max_temperature:
            issues.append(f"Temperature too high ({temp_c:.1f}°C > {self.max_temperature}°C)")
        
        if self.max_wind_speed is not None and weather.wind.speed > self.max_wind_speed:
            issues.append(f"Wind too strong ({weather.wind.speed} km/h > {self.max_wind_speed} km/h)")
        
        if self.max_humidity is not None and weather.humidity > self.max_humidity:
            issues.append(f"Humidity too high ({weather.humidity}% > {self.max_humidity}%)")
        
        if self.requires_clear_weather and weather.condition != WeatherCondition.CLEAR:
            issues.append(f"Requires clear weather (current: {weather.condition.value})")
        
        if weather.condition in self.avoid_conditions:
            issues.append(f"Weather condition not suitable: {weather.condition.value}")
        
        return len(issues) == 0, issues


@dataclass
class Activity(AIEnhancedModel):
    """Enhanced activity with rich metadata and AI-generated variations."""
    
    name: str
    description: str
    activity_type: ActivityType
    id: UUID = field(default_factory=uuid4)
    difficulty: ActivityDifficulty = ActivityDifficulty.MODERATE
    ideal_conditions: List[WeatherCondition] = field(default_factory=list)
    requirements: ActivityRequirements = field(default_factory=ActivityRequirements)
    indoor: bool = False
    duration_minutes: Tuple[int, int] = (30, 120)  # Min, Max duration
    cost_range: Tuple[float, float] = (0.0, 0.0)  # Min, Max cost
    group_size: Tuple[int, int] = (1, 10)  # Min, Max participants
    health_benefits: List[str] = field(default_factory=list)
    safety_considerations: List[str] = field(default_factory=list)
    ai_variations: Optional[List[Dict[str, Any]]] = None
    popularity_score: float = 0.5  # 0.0 to 1.0
    user_rating: Optional[float] = None  # 1.0 to 5.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def is_suitable_for_weather(self, weather: CurrentWeather, user_preferences: Optional[Dict[str, Any]] = None) -> Tuple[bool, float, List[str]]:
        """
        Enhanced weather suitability check.
        Returns (is_suitable, suitability_score, compatibility_notes).
        """
        prefs = user_preferences or {}
        is_compatible, issues = self.requirements.check_weather_compatibility(weather)
        
        if not is_compatible:
            return False, 0.0, issues
        
        # Calculate detailed suitability score
        score = 0.0
        notes = []
        
        # Indoor activities base score
        if self.indoor:
            score = 8.0
            notes.append("Indoor activity - weather independent")
        else:
            # Condition scoring
            if weather.condition in self.ideal_conditions:
                score += 10.0
                notes.append(f"Ideal weather condition: {weather.condition.value}")
            elif weather.condition == WeatherCondition.CLEAR:
                score += 8.0
                notes.append("Clear weather is generally good")
            elif weather.condition == WeatherCondition.CLOUDS:
                score += 6.0
                notes.append("Cloudy conditions are acceptable")
            else:
                score += 3.0
                notes.append(f"Weather condition {weather.condition.value} is manageable")
            
            # Temperature scoring with preferences
            temp_c = weather.temperature.to_celsius()
            temp_pref_min = prefs.get('preferred_temp_min', 15)
            temp_pref_max = prefs.get('preferred_temp_max', 25)
            
            if temp_pref_min <= temp_c <= temp_pref_max:
                score += 5.0
                notes.append("Temperature is in your preferred range")
            elif self.requirements.min_temperature and self.requirements.max_temperature:
                optimal_temp = (self.requirements.min_temperature + self.requirements.max_temperature) / 2
                temp_diff = abs(temp_c - optimal_temp)
                temp_score = max(0, 5 - temp_diff)
                score += temp_score
                if temp_score > 3:
                    notes.append("Temperature is suitable for this activity")
            
            # Wind scoring
            if weather.wind.speed <= 10:
                score += 2.0
                notes.append("Calm wind conditions")
            elif weather.wind.speed <= 20:
                score += 1.0
                notes.append("Light wind")
        
        # Difficulty and user experience adjustments
        if self.difficulty == ActivityDifficulty.EASY:
            score += 1.0
        
        # Popular activities get slight boost
        score += self.popularity_score * 2
        
        return True, min(10.0, score), notes
    
    def generate_ai_content(self, gemini_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI variations and enhancements for the activity."""
        if not gemini_api_key:
            return {"error": "Gemini API key not provided"}
        
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = self.get_ai_prompt()
            response = model.generate_content(prompt)
            
            # Parse AI response to extract variations
            variations_text = response.text
            variations = self._parse_ai_variations(variations_text)
            
            ai_content = {
                "variations": variations,
                "enhanced_description": variations_text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "activity_id": str(self.id)
            }
            
            self.ai_variations = variations
            return ai_content
            
        except Exception as e:
            logging.error(f"Failed to generate AI activity content: {e}")
            return {"error": f"AI generation failed: {str(e)}"}
    
    def get_ai_prompt(self) -> str:
        """Generate AI prompt for activity enhancement."""
        return f"""
        Enhance and create variations for this activity:
        
        Activity: {self.name}
        Description: {self.description}
        Type: {self.activity_type.value}
        Difficulty: {self.difficulty.value}
        Indoor: {self.indoor}
        Ideal Conditions: {[c.value for c in self.ideal_conditions]}
        Duration: {self.duration_minutes[0]}-{self.duration_minutes[1]} minutes
        
        Please provide:
        1. 3-5 creative variations of this activity
        2. Specific tips for different weather conditions
        3. Ways to adjust difficulty level
        4. Equipment or preparation suggestions
        5. Safety considerations
        
        Format as practical, actionable advice. Keep each variation under 50 words.
        """
    
    def _parse_ai_variations(self, ai_text: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured variations."""
        # Simple parsing - in production, this would be more sophisticated
        variations = []
        lines = ai_text.split('\n')
        
        current_variation = {}
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                if current_variation:
                    variations.append(current_variation)
                current_variation = {
                    "name": line[2:].strip()[:50],  # Extract variation name
                    "description": line[2:].strip(),
                    "generated": True
                }
            elif current_variation and line:
                current_variation["description"] += f" {line}"
        
        if current_variation:
            variations.append(current_variation)
        
        return variations[:5]  # Limit to 5 variations
    
    def get_estimated_duration(self) -> str:
        """Get formatted duration estimate."""
        min_dur, max_dur = self.duration_minutes
        if min_dur == max_dur:
            return f"{min_dur} minutes"
        elif max_dur >= 120:
            return f"{min_dur//60}-{max_dur//60} hours"
        else:
            return f"{min_dur}-{max_dur} minutes"
    
    def get_cost_estimate(self) -> str:
        """Get formatted cost estimate."""
        min_cost, max_cost = self.cost_range
        if min_cost == max_cost == 0:
            return "Free"
        elif min_cost == max_cost:
            return f"${min_cost:.2f}"
        else:
            return f"${min_cost:.2f} - ${max_cost:.2f}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "type": self.activity_type.value,
            "difficulty": self.difficulty.value,
            "ideal_conditions": [c.value for c in self.ideal_conditions],
            "indoor": self.indoor,
            "duration": self.duration_minutes,
            "cost_range": self.cost_range,
            "group_size": self.group_size,
            "health_benefits": self.health_benefits,
            "safety_considerations": self.safety_considerations,
            "ai_variations": self.ai_variations,
            "popularity_score": self.popularity_score,
            "user_rating": self.user_rating,
            "requirements": asdict(self.requirements)
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Activity':
        """Create instance from dictionary."""
        requirements_data = data.get('requirements', {})
        requirements = ActivityRequirements(**requirements_data)
        
        return cls(
            id=UUID(data['id']) if 'id' in data else uuid4(),
            name=data['name'],
            description=data['description'],
            activity_type=ActivityType(data['type']),
            difficulty=ActivityDifficulty(data.get('difficulty', 'moderate')),
            ideal_conditions=[WeatherCondition(c) for c in data.get('ideal_conditions', [])],
            requirements=requirements,
            indoor=data.get('indoor', False),
            duration_minutes=tuple(data.get('duration', [30, 120])),
            cost_range=tuple(data.get('cost_range', [0.0, 0.0])),
            group_size=tuple(data.get('group_size', [1, 10])),
            health_benefits=data.get('health_benefits', []),
            safety_considerations=data.get('safety_considerations', []),
            ai_variations=data.get('ai_variations'),
            popularity_score=data.get('popularity_score', 0.5),
            user_rating=data.get('user_rating')
        )


@dataclass
class ActivitySuggestion(AIEnhancedModel):
    """Enhanced activity suggestions with AI-powered personalization."""
    
    weather: CurrentWeather
    id: UUID = field(default_factory=uuid4)
    suggested_activities: List[Tuple[Activity, float, List[str]]] = field(default_factory=list)  # (activity, score, notes)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    filter_criteria: Dict[str, Any] = field(default_factory=dict)
    ai_personalized_suggestions: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Initialize with basic activity scoring if suggestions are empty."""
        if not self.suggested_activities:
            self._generate_basic_suggestions()
    
    def _generate_basic_suggestions(self) -> None:
        """Generate basic activity suggestions from default activities."""
        # Import here to avoid circular imports - would be reorganized in production
        factory = ActivityFactory()
        default_activities = factory.get_default_activities()
        
        scored_activities = []
        for activity in default_activities:
            is_suitable, score, notes = activity.is_suitable_for_weather(self.weather, self.user_preferences)
            if is_suitable and score > 0:
                scored_activities.append((activity, score, notes))
        
        # Sort by score (descending)
        scored_activities.sort(key=lambda x: x[1], reverse=True)
        self.suggested_activities = scored_activities[:10]  # Top 10 suggestions
    
    @property
    def top_suggestion(self) -> Optional[Tuple[Activity, float, List[str]]]:
        """Get the top activity suggestion with score and notes."""
        if self.suggested_activities:
            return self.suggested_activities[0]
        return None
    
    @property
    def outdoor_activities(self) -> List[Tuple[Activity, float, List[str]]]:
        """Get only outdoor activity suggestions."""
        return [
            (activity, score, notes)
            for activity, score, notes in self.suggested_activities
            if not activity.indoor
        ]
    
    @property
    def indoor_activities(self) -> List[Tuple[Activity, float, List[str]]]:
        """Get only indoor activity suggestions."""
        return [
            (activity, score, notes)
            for activity, score, notes in self.suggested_activities
            if activity.indoor
        ]
    
    def filter_by_type(self, activity_type: ActivityType) -> List[Tuple[Activity, float, List[str]]]:
        """Filter suggestions by activity type."""
        return [
            (activity, score, notes)
            for activity, score, notes in self.suggested_activities
            if activity.activity_type == activity_type
        ]
    
    def filter_by_difficulty(self, difficulty: ActivityDifficulty) -> List[Tuple[Activity, float, List[str]]]:
        """Filter suggestions by difficulty level."""
        return [
            (activity, score, notes)
            for activity, score, notes in self.suggested_activities
            if activity.difficulty == difficulty
        ]
    
    def filter_by_duration(self, max_minutes: int) -> List[Tuple[Activity, float, List[str]]]:
        """Filter suggestions by maximum duration."""
        return [
            (activity, score, notes)
            for activity, score, notes in self.suggested_activities
            if activity.duration_minutes[0] <= max_minutes
        ]
    
    def apply_user_preferences(self, preferences: Dict[str, Any]) -> None:
        """Apply user preferences to re-score activities."""
        self.user_preferences.update(preferences)
        
        # Re-score all activities with new preferences
        rescored_activities = []
        for activity, _, _ in self.suggested_activities:
            is_suitable, score, notes = activity.is_suitable_for_weather(self.weather, self.user_preferences)
            if is_suitable:
                rescored_activities.append((activity, score, notes))
        
        # Sort by new scores
        rescored_activities.sort(key=lambda x: x[1], reverse=True)
        self.suggested_activities = rescored_activities
    
    def generate_ai_content(self, gemini_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI-personalized activity suggestions."""
        if not gemini_api_key:
            return {"error": "Gemini API key not provided"}
        
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = self.get_ai_prompt()
            response = model.generate_content(prompt)
            
            # Parse AI suggestions
            personalized_suggestions = self._parse_ai_suggestions(response.text)
            
            ai_content = {
                "personalized_suggestions": personalized_suggestions,
                "reasoning": response.text,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "suggestion_id": str(self.id)
            }
            
            self.ai_personalized_suggestions = personalized_suggestions
            return ai_content
            
        except Exception as e:
            logging.error(f"Failed to generate AI activity suggestions: {e}")
            return {"error": f"AI generation failed: {str(e)}"}
    
    def get_ai_prompt(self) -> str:
        """Generate AI prompt for personalized activity suggestions."""
        current_activities = [activity.name for activity, _, _ in self.suggested_activities[:5]]
        
        return f"""
        Given the current weather and existing activity suggestions, provide personalized recommendations:
        
        Weather Conditions:
        - Location: {self.weather.location.display_name}
        - Temperature: {self.weather.temperature.to_celsius():.1f}°C
        - Condition: {self.weather.condition.value}
        - Humidity: {self.weather.humidity}%
        - Wind: {self.weather.wind.speed} km/h
        
        Current Top Suggestions:
        {', '.join(current_activities)}
        
        User Preferences:
        {json.dumps(self.user_preferences, indent=2) if self.user_preferences else 'No specific preferences provided'}
        
        Please provide:
        1. 3-5 highly personalized activity suggestions
        2. Specific reasons why each activity suits the current weather
        3. Tips for making the most of these weather conditions
        4. Any unique or creative activities not in the standard list
        
        Focus on practical, enjoyable activities that match the weather and user preferences.
        """
    
    def _parse_ai_suggestions(self, ai_text: str) -> List[Dict[str, Any]]:
        """Parse AI response into structured suggestions."""
        suggestions = []
        lines = ai_text.split('\n')
        
        current_suggestion = {}
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                if current_suggestion:
                    suggestions.append(current_suggestion)
                current_suggestion = {
                    "name": line[2:].strip()[:100],
                    "description": line[2:].strip(),
                    "ai_generated": True,
                    "reasoning": ""
                }
            elif current_suggestion and line and not line.startswith(('Tips:', 'Unique:')):
                current_suggestion["reasoning"] += f" {line}"
        
        if current_suggestion:
            suggestions.append(current_suggestion)
        
        return suggestions[:5]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "weather_location": self.weather.location.display_name,
            "weather_summary": f"{self.weather.condition.value}, {self.weather.temperature.to_celsius():.1f}°C",
            "timestamp": self.timestamp.isoformat(),
            "total_suggestions": len(self.suggested_activities),
            "top_activities": [
                {
                    "name": activity.name,
                    "score": score,
                    "notes": notes,
                    "type": activity.activity_type.value,
                    "indoor": activity.indoor
                }
                for activity, score, notes in self.suggested_activities[:5]
            ],
            "user_preferences": self.user_preferences,
            "ai_suggestions": self.ai_personalized_suggestions
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActivitySuggestion':
        """Create instance from dictionary (partial implementation)."""
        # This would need full implementation with weather data reconstruction
        raise NotImplementedError("Dictionary reconstruction not yet implemented")


# ============================================================================
# Enhanced Poetry System with AI Generation
# ============================================================================

class PoemType(Enum):
    """Types of weather poetry."""
    
    HAIKU = "haiku"
    LIMERICK = "limerick"
    FREE_VERSE = "free_verse"
    PHRASE = "phrase"
    COUPLET = "couplet"
    ACROSTIC = "acrostic"
    WEATHER_REPORT = "weather_report"
    MICRO_POEM = "micro_poem"
    
    @property
    def structure_description(self) -> str:
        """Get description of poem structure."""
        descriptions = {
            "haiku": "5-7-5 syllable structure",
            "limerick": "5-line AABBA rhyme scheme",
            "free_verse": "No specific structure",
            "phrase": "Short descriptive phrase",
            "couplet": "Two rhyming lines",
            "acrostic": "First letters spell a word",
            "weather_report": "Poetic weather description",
            "micro_poem": "Very short poem (under 25 words)"
        }
        return descriptions.get(self.value, "Creative poetry")


class TemperatureRange(Enum):
    """Enhanced temperature ranges with specific thresholds."""
    
    FREEZING = "freezing"  # < 0°C
    COLD = "cold"  # 0-10°C
    COOL = "cool"  # 10-18°C
    MILD = "mild"  # 18-24°C
    WARM = "warm"  # 24-30°C
    HOT = "hot"  # 30-35°C
    SCORCHING = "scorching"  # > 35°C
    
    @classmethod
    def from_celsius(cls, temp_c: float) -> 'TemperatureRange':
        """Get temperature range from Celsius value."""
        if temp_c < 0:
            return cls.FREEZING
        elif temp_c < 10:
            return cls.COLD
        elif temp_c < 18:
            return cls.COOL
        elif temp_c < 24:
            return cls.MILD
        elif temp_c < 30:
            return cls.WARM
        elif temp_c < 35:
            return cls.HOT
        else:
            return cls.SCORCHING
    
    @property
    def emoji(self) -> str:
        """Get emoji for temperature range."""
        emoji_map = {
            "freezing": "🥶",
            "cold": "❄️",
            "cool": "🍃",
            "mild": "🌤️",
            "warm": "☀️",
            "hot": "🔥",
            "scorching": "🌡️"
        }
        return emoji_map[self.value]


@dataclass
class PoemMetadata:
    """Rich metadata for weather poems."""
    
    inspiration_source: str = "weather_conditions"
    emotional_tone: str = "neutral"
    literary_devices: List[str] = field(default_factory=list)
    cultural_references: List[str] = field(default_factory=list)
    target_audience: str = "general"
    reading_time_seconds: int = 30
    complexity_score: float = 0.5  # 0.0 (simple) to 1.0 (complex)
    
    def add_literary_device(self, device: str) -> None:
        """Add a literary device used in the poem."""
        if device not in self.literary_devices:
            self.literary_devices.append(device)


@dataclass
class WeatherPoem(AIEnhancedModel):
    """Enhanced weather poem with AI generation and rich metadata."""
    
    text: str
    poem_type: PoemType
    weather_condition: WeatherCondition
    temperature_range: TemperatureRange
    id: UUID = field(default_factory=uuid4)
    location_context: str = ""
    mood_inspiration: Optional[MoodType] = None
    ai_generated: bool = False
    ai_model_used: Optional[str] = None
    metadata: PoemMetadata = field(default_factory=PoemMetadata)
    user_rating: Optional[float] = None  # 1.0 to 5.0
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def __post_init__(self):
        """Initialize poem with derived metadata."""
        self._analyze_text_complexity()
        self._estimate_reading_time()
    
    def _analyze_text_complexity(self) -> None:
        """Analyze text complexity and update metadata."""
        words = self.text.split()
        avg_word_length = sum(len(word.strip('.,!?;:')) for word in words) / max(len(words), 1)
        sentence_count = len([c for c in self.text if c in '.!?'])
        
        # Simple complexity scoring
        complexity = 0.0
        complexity += min(1.0, avg_word_length / 10)  # Longer words = more complex
        complexity += min(1.0, len(words) / 50)  # Longer poems = more complex
        if sentence_count > 0:
            complexity += min(1.0, len(words) / sentence_count / 15)  # Longer sentences = more complex
        
        self.metadata.complexity_score = complexity / 3
    
    def _estimate_reading_time(self) -> None:
        """Estimate reading time in seconds."""
        word_count = len(self.text.split())
        # Average reading speed: 200-250 words per minute
        reading_time = (word_count / 225) * 60  # seconds
        self.metadata.reading_time_seconds = max(10, int(reading_time))
    
    @property
    def formatted_text(self) -> str:
        """Get formatted poem text with proper line breaks."""
        if self.poem_type in [PoemType.HAIKU, PoemType.LIMERICK]:
            # Handle common line separators
            for separator in [" / ", "/", " | ", "|"]:
                if separator in self.text:
                    lines = self.text.split(separator)
                    return "\n".join(line.strip() for line in lines)
        
        # For other types, preserve existing line breaks or add smart breaks
        if "\n" in self.text:
            return self.text
        
        # Add smart line breaks for long texts
        if len(self.text) > 80 and self.poem_type != PoemType.PHRASE:
            words = self.text.split()
            lines = []
            current_line = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + 1 > 40:  # Wrap at ~40 characters
                    if current_line:
                        lines.append(" ".join(current_line))
                        current_line = [word]
                        current_length = len(word)
                else:
                    current_line.append(word)
                    current_length += len(word) + 1
            
            if current_line:
                lines.append(" ".join(current_line))
            
            return "\n".join(lines)
        
        return self.text
    
    @property
    def display_title(self) -> str:
        """Get a display title for the poem."""
        if self.location_context:
            return f"{self.poem_type.value.title()} for {self.location_context}"
        else:
            return f"{self.weather_condition.value.title()} {self.poem_type.value.title()}"
    
    @property
    def word_count(self) -> int:
        """Get word count of the poem."""
        return len(self.text.split())
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the poem."""
        if tag.lower() not in [t.lower() for t in self.tags]:
            self.tags.append(tag.lower())
    
    def rate_poem(self, rating: float) -> None:
        """Rate the poem (1.0 to 5.0)."""
        if 1.0 <= rating <= 5.0:
            self.user_rating = rating
        else:
            raise ValueError("Rating must be between 1.0 and 5.0")
    
    def generate_ai_content(self, gemini_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Generate AI variations and analysis of the poem."""
        if not gemini_api_key:
            return {"error": "Gemini API key not provided"}
        
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = self.get_ai_prompt()
            response = model.generate_content(prompt)
            
            analysis = {
                "literary_analysis": response.text,
                "suggested_improvements": self._extract_suggestions(response.text),
                "style_notes": self._extract_style_notes(response.text),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "poem_id": str(self.id)
            }
            
            return analysis
            
        except Exception as e:
            logging.error(f"Failed to generate AI poem analysis: {e}")
            return {"error": f"AI analysis failed: {str(e)}"}
    
    def get_ai_prompt(self) -> str:
        """Generate AI prompt for poem analysis."""
        return f"""
        Analyze this weather-inspired poem and provide insights:
        
        Poem Type: {self.poem_type.value}
        Weather Context: {self.weather_condition.value}, {self.temperature_range.value}
        Location: {self.location_context or 'General'}
        
        Poem Text:
        {self.formatted_text}
        
        Please provide:
        1. Literary analysis of the poem's effectiveness
        2. Assessment of how well it captures the weather mood
        3. Suggestions for improvement or variation
        4. Literary devices used (metaphor, alliteration, etc.)
        5. Overall emotional impact and imagery
        
        Keep the analysis constructive and educational.
        """
    
    def _extract_suggestions(self, analysis_text: str) -> List[str]:
        """Extract improvement suggestions from AI analysis."""
        # Simple extraction - would be more sophisticated in production
        suggestions = []
        lines = analysis_text.split('\n')
        
        capturing_suggestions = False
        for line in lines:
            line = line.strip()
            if 'suggestion' in line.lower() or 'improve' in line.lower():
                capturing_suggestions = True
            elif capturing_suggestions and line and not line.startswith(('1.', '2.', '3.', '4.', '5.')):
                suggestions.append(line)
            elif capturing_suggestions and len(suggestions) >= 3:
                break
        
        return suggestions[:3]
    
    def _extract_style_notes(self, analysis_text: str) -> List[str]:
        """Extract style notes from AI analysis."""
        # Simple extraction for literary devices and style elements
        style_terms = ['metaphor', 'alliteration', 'imagery', 'rhythm', 'rhyme', 'personification', 'simile']
        found_elements = []
        
        for term in style_terms:
            if term in analysis_text.lower():
                found_elements.append(term.title())
        
        return found_elements
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "text": self.text,
            "formatted_text": self.formatted_text,
            "poem_type": self.poem_type.value,
            "weather_condition": self.weather_condition.value,
            "temperature_range": self.temperature_range.value,
            "location_context": self.location_context,
            "mood_inspiration": self.mood_inspiration.value if self.mood_inspiration else None,
            "ai_generated": self.ai_generated,
            "ai_model_used": self.ai_model_used,
            "metadata": asdict(self.metadata),
            "user_rating": self.user_rating,
            "tags": self.tags,
            "word_count": self.word_count,
            "display_title": self.display_title,
            "created_at": self.created_at.isoformat()
        }
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WeatherPoem':
        """Create instance from dictionary."""
        metadata_data = data.get('metadata', {})
        metadata = PoemMetadata(**metadata_data)
        
        return cls(
            id=UUID(data['id']) if 'id' in data else uuid4(),
            text=data['text'],
            poem_type=PoemType(data['poem_type']),
            weather_condition=WeatherCondition(data['weather_condition']),
            temperature_range=TemperatureRange(data['temperature_range']),
            location_context=data.get('location_context', ''),
            mood_inspiration=MoodType(data['mood_inspiration']) if data.get('mood_inspiration') else None,
            ai_generated=data.get('ai_generated', False),
            ai_model_used=data.get('ai_model_used'),
            metadata=metadata,
            user_rating=data.get('user_rating'),
            tags=data.get('tags', []),
            created_at=datetime.fromisoformat(data['created_at'])
        )


# ============================================================================
# Factory Patterns and Model Builders
# ============================================================================

class ActivityFactory:
    """Factory for creating and managing activities with AI enhancement."""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize factory with optional AI capabilities."""
        self.gemini_api_key = gemini_api_key
        self.logger = logging.getLogger(__name__)
        self._activity_cache: Dict[str, Activity] = {}
    
    def create_activity(
        self,
        name: str,
        description: str,
        activity_type: ActivityType,
        **kwargs
    ) -> Activity:
        """Create a new activity with optional AI enhancements."""
        
        # Extract equipment_needed and put it in requirements
        equipment_needed = kwargs.pop('equipment_needed', [])
        requirements = kwargs.get('requirements', ActivityRequirements())
        if equipment_needed and hasattr(requirements, 'equipment_needed'):
            requirements.equipment_needed = equipment_needed
        kwargs['requirements'] = requirements
        
        # Create base activity
        activity = Activity(
            name=name,
            description=description,
            activity_type=activity_type,
            **kwargs
        )
        
        # Enhance with AI if available
        if self.gemini_api_key:
            try:
                ai_content = activity.generate_ai_content(self.gemini_api_key)
                if "variations" in ai_content:
                    self.logger.info(f"Enhanced activity '{name}' with AI variations")
            except Exception as e:
                self.logger.warning(f"Failed to enhance activity with AI: {e}")
        
        # Cache the activity
        self._activity_cache[activity.name.lower()] = activity
        return activity
    
    def get_default_activities(self) -> List[Activity]:
        """Get enhanced default activities with better structure."""
        activities = []
        
        # Outdoor Sports
        activities.extend([
            self.create_activity(
                name="Cycling Adventure",
                description="Enjoy cycling through scenic routes in pleasant weather",
                activity_type=ActivityType.OUTDOOR_SPORTS,
                difficulty=ActivityDifficulty.MODERATE,
                ideal_conditions=[WeatherCondition.CLEAR, WeatherCondition.CLOUDS],
                requirements=ActivityRequirements(
                    min_temperature=10, max_temperature=30, max_wind_speed=25
                ),
                duration_minutes=(45, 180),
                cost_range=(0.0, 20.0),
                health_benefits=["Cardiovascular fitness", "Leg strength", "Mental well-being"],
                safety_considerations=["Wear helmet", "Check bike condition", "Be visible to traffic"]
            ),
            
            self.create_activity(
                name="Nature Hiking",
                description="Explore nature trails and discover scenic views",
                activity_type=ActivityType.OUTDOOR_SPORTS,
                difficulty=ActivityDifficulty.MODERATE,
                ideal_conditions=[WeatherCondition.CLEAR, WeatherCondition.CLOUDS],
                requirements=ActivityRequirements(
                    min_temperature=5, max_temperature=28, max_wind_speed=30
                ),
                duration_minutes=(60, 240),
                health_benefits=["Cardiovascular health", "Leg strength", "Nature connection"],
                safety_considerations=["Bring water", "Wear appropriate footwear", "Tell someone your route"]
            ),
            
            self.create_activity(
                name="Outdoor Sports Games",
                description="Basketball, tennis, soccer, or frisbee in the park",
                activity_type=ActivityType.OUTDOOR_SPORTS,
                difficulty=ActivityDifficulty.MODERATE,
                ideal_conditions=[WeatherCondition.CLEAR, WeatherCondition.CLOUDS],
                requirements=ActivityRequirements(
                    min_temperature=15, max_temperature=32, max_wind_speed=20
                ),
                duration_minutes=(30, 120),
                group_size=(2, 20),
                health_benefits=["Full-body workout", "Coordination", "Social interaction"]
            )
        ])
        
        # Indoor Activities
        activities.extend([
            self.create_activity(
                name="Cozy Reading Session",
                description="Relax with a good book and warm beverage",
                activity_type=ActivityType.RELAXATION,
                difficulty=ActivityDifficulty.EASY,
                ideal_conditions=[WeatherCondition.RAIN, WeatherCondition.SNOW, WeatherCondition.THUNDERSTORM],
                indoor=True,
                duration_minutes=(30, 180),
                health_benefits=["Mental stimulation", "Stress reduction", "Vocabulary expansion"]
            ),
            
            self.create_activity(
                name="Museum or Gallery Visit",
                description="Explore art, history, science, or cultural exhibitions",
                activity_type=ActivityType.CULTURAL,
                difficulty=ActivityDifficulty.EASY,
                ideal_conditions=[WeatherCondition.RAIN, WeatherCondition.SNOW],
                indoor=True,
                duration_minutes=(90, 240),
                cost_range=(5.0, 25.0),
                health_benefits=["Mental stimulation", "Cultural enrichment", "Walking exercise"]
            ),
            
            self.create_activity(
                name="Creative Cooking Project",
                description="Try a new recipe or cooking technique",
                activity_type=ActivityType.CREATIVE,
                difficulty=ActivityDifficulty.MODERATE,
                ideal_conditions=[WeatherCondition.RAIN, WeatherCondition.SNOW],
                indoor=True,
                duration_minutes=(45, 150),
                cost_range=(10.0, 50.0),
                health_benefits=["Creativity", "Practical skills", "Nutrition awareness"]
            )
        ])
        
        # Weather-Specific Activities
        activities.extend([
            self.create_activity(
                name="Snow Day Fun",
                description="Build snowmen, have snowball fights, or make snow angels",
                activity_type=ActivityType.OUTDOOR_SPORTS,
                difficulty=ActivityDifficulty.EASY,
                ideal_conditions=[WeatherCondition.SNOW],
                requirements=ActivityRequirements(
                    min_temperature=-10, max_temperature=2
                ),
                duration_minutes=(30, 120),
                health_benefits=["Physical activity", "Vitamin D", "Joy and playfulness"],
                safety_considerations=["Dress warmly", "Stay dry", "Be aware of ice"]
            ),
            
            self.create_activity(
                name="Rain Appreciation",
                description="Listen to rainfall, watch from a window, or enjoy the fresh smell",
                activity_type=ActivityType.RELAXATION,
                difficulty=ActivityDifficulty.EASY,
                ideal_conditions=[WeatherCondition.RAIN, WeatherCondition.DRIZZLE],
                indoor=True,
                duration_minutes=(15, 60),
                health_benefits=["Stress reduction", "Mindfulness", "Sensory awareness"]
            ),
            
            self.create_activity(
                name="Weather Photography",
                description="Capture the beauty of current weather conditions",
                activity_type=ActivityType.CREATIVE,
                difficulty=ActivityDifficulty.MODERATE,
                ideal_conditions=[WeatherCondition.CLEAR, WeatherCondition.CLOUDS, WeatherCondition.FOG],
                requirements=ActivityRequirements(
                    min_temperature=0, max_temperature=35
                ),
                duration_minutes=(30, 180),
                equipment_needed=["Camera or smartphone", "Weather protection for equipment"],
                health_benefits=["Creativity", "Outdoor time", "Artistic expression"]
            )
        ])
        
        return activities
    
    def create_from_ai_suggestion(self, suggestion_text: str, weather: CurrentWeather) -> Optional[Activity]:
        """Create an activity from AI-generated suggestion."""
        if not self.gemini_api_key:
            return None
        
        try:
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            prompt = f"""
            Convert this activity suggestion into structured data:
            
            Suggestion: {suggestion_text}
            Current Weather: {weather.condition.value}, {weather.temperature.to_celsius():.1f}°C
            
            Provide:
            - Activity name (short, catchy)
            - Detailed description
            - Activity type (outdoor_sports, indoor_activities, sightseeing, exercise, relaxation, cultural, shopping, dining, adventure, creative, social, wellness, educational, entertainment)
            - Difficulty level (easy, moderate, challenging, expert)
            - Duration estimate in minutes
            - Whether it's indoor or outdoor
            - Equipment needed (if any)
            - Safety considerations
            
            Format as structured text with clear labels.
            """
            
            response = model.generate_content(prompt)
            
            # Parse the AI response and create activity
            # This would need more sophisticated parsing in production
            activity_data = self._parse_ai_activity_response(response.text)
            
            if activity_data:
                return self.create_activity(**activity_data)
            
        except Exception as e:
            self.logger.error(f"Failed to create activity from AI suggestion: {e}")
        
        return None
    
    def _parse_ai_activity_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse AI response into activity parameters."""
        # Simplified parsing - would be more robust in production
        lines = response_text.split('\n')
        activity_data = {}
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                if key in ['name', 'description']:
                    activity_data[key] = value
                elif key == 'activity_type':
                    try:
                        activity_data['activity_type'] = ActivityType(value.lower())
                    except ValueError:
                        activity_data['activity_type'] = ActivityType.RELAXATION
                elif key == 'difficulty':
                    try:
                        activity_data['difficulty'] = ActivityDifficulty(value.lower())
                    except ValueError:
                        activity_data['difficulty'] = ActivityDifficulty.MODERATE
                elif key == 'indoor':
                    activity_data['indoor'] = 'indoor' in value.lower()
        
        return activity_data if 'name' in activity_data else None


class WeatherComparisonBuilder:
    """Builder pattern for creating complex weather comparisons."""
    
    def __init__(self):
        """Initialize builder."""
        self._city1_weather: Optional[CurrentWeather] = None
        self._city2_weather: Optional[CurrentWeather] = None
        self._strategy: ComparisonStrategy = DefaultComparisonStrategy()
        self._preferences: Dict[str, Any] = {}
        self._gemini_api_key: Optional[str] = None
    
    def with_cities(self, city1_weather: CurrentWeather, city2_weather: CurrentWeather) -> 'WeatherComparisonBuilder':
        """Set the cities to compare."""
        self._city1_weather = city1_weather
        self._city2_weather = city2_weather
        return self
    
    def with_strategy(self, strategy: ComparisonStrategy) -> 'WeatherComparisonBuilder':
        """Set comparison strategy."""
        self._strategy = strategy
        return self
    
    def with_preferences(self, preferences: Dict[str, Any]) -> 'WeatherComparisonBuilder':
        """Set user preferences."""
        self._preferences.update(preferences)
        return self
    
    def with_ai_insights(self, gemini_api_key: str) -> 'WeatherComparisonBuilder':
        """Enable AI insights."""
        self._gemini_api_key = gemini_api_key
        return self
    
    def build(self) -> WeatherComparison:
        """Build the weather comparison."""
        if not self._city1_weather or not self._city2_weather:
            raise ValueError("Both cities must be set before building comparison")
        
        comparison = WeatherComparison(
            city1_weather=self._city1_weather,
            city2_weather=self._city2_weather,
            strategy=self._strategy,
            user_preferences=self._preferences
        )
        
        # Generate AI insights if enabled
        if self._gemini_api_key:
            try:
                comparison.generate_ai_content(self._gemini_api_key)
            except Exception as e:
                logging.warning(f"Failed to generate AI insights for comparison: {e}")
        
        return comparison


# ============================================================================
# Convenience Functions and Factories
# ============================================================================

def create_journal_entry_from_weather(
    weather: CurrentWeather,
    mood: MoodType,
    notes: str = "",
    activities: Optional[List[str]] = None
) -> JournalEntry:
    """Convenience function to create journal entry from weather data."""
    return JournalEntry(
        date=date.today(),
        location=weather.location.display_name,
        weather_data=weather,
        mood=mood,
        notes=notes,
        activities=activities or [],
        weather_impact=_determine_weather_impact(weather, mood)
    )


def _determine_weather_impact(weather: CurrentWeather, mood: MoodType) -> WeatherImpact:
    """Determine weather impact based on conditions and mood."""
    # Simple heuristic - would be more sophisticated in production
    temp_c = weather.temperature.to_celsius()
    
    # Base impact from weather conditions
    condition_impacts = {
        WeatherCondition.CLEAR: WeatherImpact.POSITIVE,
        WeatherCondition.CLOUDS: WeatherImpact.NEUTRAL,
        WeatherCondition.RAIN: WeatherImpact.NEGATIVE,
        WeatherCondition.SNOW: WeatherImpact.NEUTRAL,
        WeatherCondition.THUNDERSTORM: WeatherImpact.NEGATIVE
    }
    
    base_impact = condition_impacts.get(weather.condition, WeatherImpact.NEUTRAL)
    
    # Adjust based on temperature
    if 18 <= temp_c <= 26:
        # Ideal temperature range
        if base_impact == WeatherImpact.POSITIVE:
            return WeatherImpact.VERY_POSITIVE
        elif base_impact == WeatherImpact.NEUTRAL:
            return WeatherImpact.POSITIVE
    elif temp_c < 0 or temp_c > 35:
        # Extreme temperatures
        if base_impact in [WeatherImpact.POSITIVE, WeatherImpact.NEUTRAL]:
            return WeatherImpact.NEGATIVE
        elif base_impact == WeatherImpact.NEGATIVE:
            return WeatherImpact.VERY_NEGATIVE
    
    # Consider mood alignment
    positive_moods = [MoodType.HAPPY, MoodType.EXCITED, MoodType.ENERGETIC, MoodType.MOTIVATED]
    if mood in positive_moods and base_impact in [WeatherImpact.POSITIVE, WeatherImpact.VERY_POSITIVE]:
        return WeatherImpact.VERY_POSITIVE
    
    return base_impact


def create_activity_suggestions(
    weather: CurrentWeather,
    user_preferences: Optional[Dict[str, Any]] = None,
    gemini_api_key: Optional[str] = None
) -> ActivitySuggestion:
    """Convenience function to create activity suggestions."""
    factory = ActivityFactory(gemini_api_key)
    suggestion = ActivitySuggestion(
        weather=weather,
        user_preferences=user_preferences or {}
    )
    
    # Generate AI-personalized suggestions if enabled
    if gemini_api_key:
        try:
            suggestion.generate_ai_content(gemini_api_key)
        except Exception as e:
            logging.warning(f"Failed to generate AI activity suggestions: {e}")
    
    return suggestion


def create_weather_poem(
    weather: CurrentWeather,
    poem_type: PoemType = PoemType.HAIKU,
    gemini_api_key: Optional[str] = None
) -> WeatherPoem:
    """Create a weather poem, optionally AI-generated."""
    
    if gemini_api_key:
        # Generate AI poem
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            temp_range = TemperatureRange.from_celsius(weather.temperature.to_celsius())
            
            prompt = f"""
            Write a {poem_type.value} about the current weather:
            
            Weather: {weather.condition.value}
            Temperature: {weather.temperature.to_celsius():.1f}°C ({temp_range.value})
            Location: {weather.location.display_name}
            
            The poem should capture the mood and atmosphere of these conditions.
            {poem_type.structure_description}
            
            Make it evocative and beautiful.
            """
            
            response = model.generate_content(prompt)
            
            return WeatherPoem(
                text=response.text.strip(),
                poem_type=poem_type,
                weather_condition=weather.condition,
                temperature_range=temp_range,
                location_context=weather.location.display_name,
                ai_generated=True,
                ai_model_used="gemini-pro"
            )
            
        except Exception as e:
            logging.error(f"Failed to generate AI poem: {e}")
    
    # Fallback to template-based poem
    temp_range = TemperatureRange.from_celsius(weather.temperature.to_celsius())
    
    # Simple template poem (placeholder)
    template_text = f"Weather {weather.condition.value} today / Temperature {temp_range.value} and bright / Nature's gift to see"
    
    return WeatherPoem(
        text=template_text,
        poem_type=poem_type,
        weather_condition=weather.condition,
        temperature_range=temp_range,
        location_context=weather.location.display_name,
        ai_generated=False
    )


# Export all enhanced models and utilities
__all__ = [
    # Core Models
    'WeatherComparison', 'JournalEntry', 'Activity', 'ActivitySuggestion', 'WeatherPoem',
    
    # Enums
    'ActivityType', 'MoodType', 'WeatherImpact', 'ActivityDifficulty', 'SeasonalPreference',
    'PoemType', 'TemperatureRange',
    
    # Supporting Classes
    'ActivityRequirements', 'WeatherMoodCorrelation', 'PoemMetadata',
    
    # Strategies and Patterns
    'ComparisonStrategy', 'DefaultComparisonStrategy', 'OutdoorActivityStrategy',
    'ActivityFactory', 'WeatherComparisonBuilder',
    
    # Protocols and Abstract Classes
    'ModelProtocol', 'AIEnhancedModel', 'ExtensibleEnum',
    
    # Convenience Functions
    'create_journal_entry_from_weather', 'create_activity_suggestions', 'create_weather_poem'
]