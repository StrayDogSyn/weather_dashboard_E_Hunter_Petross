"""Interfaces for weather-based activity recommendation services."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any


class ActivityCategory(Enum):
    """Categories of activities."""
    OUTDOOR_SPORTS = "outdoor_sports"
    INDOOR_SPORTS = "indoor_sports"
    RECREATION = "recreation"
    CULTURAL = "cultural"
    ADVENTURE = "adventure"
    RELAXATION = "relaxation"
    SOCIAL = "social"
    FITNESS = "fitness"
    FAMILY = "family"
    ROMANTIC = "romantic"
    EDUCATIONAL = "educational"
    SHOPPING = "shopping"


class ActivityDifficulty(Enum):
    """Difficulty levels for activities."""
    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"
    EXPERT = "expert"


class WeatherSuitability(Enum):
    """Weather suitability ratings."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NOT_SUITABLE = "not_suitable"


class ActivityDuration(Enum):
    """Expected duration of activities."""
    SHORT = "short"  # < 2 hours
    MEDIUM = "medium"  # 2-6 hours
    LONG = "long"  # 6+ hours
    FULL_DAY = "full_day"  # 8+ hours


@dataclass
class WeatherConditions:
    """Current weather conditions for activity recommendations."""
    temperature: float
    humidity: float
    wind_speed: float
    precipitation: float
    visibility: float
    uv_index: Optional[float] = None
    condition: Optional[str] = None
    feels_like: Optional[float] = None
    pressure: Optional[float] = None
    timestamp: Optional[datetime] = None


@dataclass
class ActivityPreferences:
    """User preferences for activity recommendations."""
    preferred_categories: List[ActivityCategory]
    difficulty_level: Optional[ActivityDifficulty] = None
    duration: Optional[ActivityDuration] = None
    indoor_preference: Optional[bool] = None
    group_size: Optional[int] = None
    budget_range: Optional[str] = None  # "low", "medium", "high"
    accessibility_needs: Optional[List[str]] = None
    age_group: Optional[str] = None  # "child", "teen", "adult", "senior"
    fitness_level: Optional[str] = None  # "low", "medium", "high"


@dataclass
class Activity:
    """Represents a recommended activity."""
    id: str
    name: str
    description: str
    category: ActivityCategory
    difficulty: ActivityDifficulty
    duration: ActivityDuration
    indoor: bool
    equipment_needed: List[str]
    cost_estimate: Optional[str] = None
    location_type: Optional[str] = None  # "home", "park", "gym", "venue"
    min_participants: int = 1
    max_participants: Optional[int] = None
    age_restrictions: Optional[str] = None
    safety_considerations: Optional[List[str]] = None
    seasonal_availability: Optional[List[str]] = None
    website_url: Optional[str] = None
    image_url: Optional[str] = None


@dataclass
class WeatherRequirement:
    """Weather requirements for an activity."""
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    max_wind_speed: Optional[float] = None
    max_precipitation: Optional[float] = None
    min_visibility: Optional[float] = None
    max_humidity: Optional[float] = None
    max_uv_index: Optional[float] = None
    required_conditions: Optional[List[str]] = None
    prohibited_conditions: Optional[List[str]] = None


@dataclass
class ActivityRecommendation:
    """A recommended activity with weather suitability."""
    activity: Activity
    suitability: WeatherSuitability
    confidence_score: float  # 0.0 to 1.0
    weather_match_score: float  # 0.0 to 1.0
    preference_match_score: float  # 0.0 to 1.0
    reasons: List[str]
    warnings: Optional[List[str]] = None
    alternatives: Optional[List[str]] = None
    best_time: Optional[str] = None
    preparation_tips: Optional[List[str]] = None


@dataclass
class ActivityRequest:
    """Request for activity recommendations."""
    weather_conditions: WeatherConditions
    preferences: ActivityPreferences
    location: Optional[str] = None
    date: Optional[datetime] = None
    max_recommendations: int = 10
    include_alternatives: bool = True
    include_indoor_backup: bool = True


@dataclass
class ActivityResponse:
    """Response containing activity recommendations."""
    request: ActivityRequest
    recommendations: List[ActivityRecommendation]
    indoor_alternatives: Optional[List[ActivityRecommendation]] = None
    weather_summary: Optional[str] = None
    general_advice: Optional[List[str]] = None
    generated_at: Optional[datetime] = None


@dataclass
class ActivityFilter:
    """Filter criteria for activity search."""
    categories: Optional[List[ActivityCategory]] = None
    difficulty: Optional[ActivityDifficulty] = None
    duration: Optional[ActivityDuration] = None
    indoor_only: Optional[bool] = None
    outdoor_only: Optional[bool] = None
    equipment_available: Optional[List[str]] = None
    max_cost: Optional[str] = None
    location_type: Optional[str] = None
    group_size: Optional[int] = None


class IActivityDatabase(ABC):
    """Interface for activity database operations."""

    @abstractmethod
    async def get_all_activities(self) -> List[Activity]:
        """Get all available activities."""
        pass

    @abstractmethod
    async def get_activity_by_id(self, activity_id: str) -> Optional[Activity]:
        """Get activity by ID."""
        pass

    @abstractmethod
    async def search_activities(self, filter_criteria: ActivityFilter) -> List[Activity]:
        """Search activities by filter criteria."""
        pass

    @abstractmethod
    async def get_activities_by_category(self, category: ActivityCategory) -> List[Activity]:
        """Get activities by category."""
        pass

    @abstractmethod
    async def add_activity(self, activity: Activity) -> bool:
        """Add new activity to database."""
        pass

    @abstractmethod
    async def update_activity(self, activity: Activity) -> bool:
        """Update existing activity."""
        pass

    @abstractmethod
    async def delete_activity(self, activity_id: str) -> bool:
        """Delete activity from database."""
        pass


class IWeatherMatcher(ABC):
    """Interface for matching weather conditions to activities."""

    @abstractmethod
    async def calculate_weather_suitability(
        self,
        activity: Activity,
        weather: WeatherConditions,
        requirements: WeatherRequirement
    ) -> WeatherSuitability:
        """Calculate weather suitability for an activity."""
        pass

    @abstractmethod
    async def get_weather_score(
        self,
        activity: Activity,
        weather: WeatherConditions,
        requirements: WeatherRequirement
    ) -> float:
        """Get numerical weather match score (0.0 to 1.0)."""
        pass

    @abstractmethod
    async def get_weather_requirements(self, activity: Activity) -> WeatherRequirement:
        """Get weather requirements for an activity."""
        pass

    @abstractmethod
    async def generate_weather_warnings(
        self,
        activity: Activity,
        weather: WeatherConditions
    ) -> List[str]:
        """Generate weather-related warnings for an activity."""
        pass


class IPreferenceMatcher(ABC):
    """Interface for matching user preferences to activities."""

    @abstractmethod
    async def calculate_preference_score(
        self,
        activity: Activity,
        preferences: ActivityPreferences
    ) -> float:
        """Calculate preference match score (0.0 to 1.0)."""
        pass

    @abstractmethod
    async def filter_by_preferences(
        self,
        activities: List[Activity],
        preferences: ActivityPreferences
    ) -> List[Activity]:
        """Filter activities by user preferences."""
        pass

    @abstractmethod
    async def get_preference_reasons(
        self,
        activity: Activity,
        preferences: ActivityPreferences
    ) -> List[str]:
        """Get reasons why activity matches preferences."""
        pass


class IRecommendationEngine(ABC):
    """Interface for activity recommendation engine."""

    @abstractmethod
    async def generate_recommendations(
        self,
        request: ActivityRequest
    ) -> List[ActivityRecommendation]:
        """Generate activity recommendations based on request."""
        pass

    @abstractmethod
    async def rank_activities(
        self,
        activities: List[Activity],
        weather: WeatherConditions,
        preferences: ActivityPreferences
    ) -> List[ActivityRecommendation]:
        """Rank activities based on weather and preferences."""
        pass

    @abstractmethod
    async def get_indoor_alternatives(
        self,
        outdoor_activities: List[Activity],
        preferences: ActivityPreferences
    ) -> List[ActivityRecommendation]:
        """Get indoor alternatives for outdoor activities."""
        pass

    @abstractmethod
    async def generate_preparation_tips(
        self,
        activity: Activity,
        weather: WeatherConditions
    ) -> List[str]:
        """Generate preparation tips for an activity."""
        pass


class IActivityService(ABC):
    """High-level interface for activity recommendation service."""

    @abstractmethod
    async def get_recommendations(self, request: ActivityRequest) -> ActivityResponse:
        """Get activity recommendations based on weather and preferences."""
        pass

    @abstractmethod
    async def get_quick_recommendations(
        self,
        weather: WeatherConditions,
        category: Optional[ActivityCategory] = None,
        indoor_only: bool = False
    ) -> List[ActivityRecommendation]:
        """Get quick activity recommendations."""
        pass

    @abstractmethod
    async def search_activities(
        self,
        query: str,
        filter_criteria: Optional[ActivityFilter] = None
    ) -> List[Activity]:
        """Search activities by text query and filters."""
        pass

    @abstractmethod
    async def get_activity_details(self, activity_id: str) -> Optional[Activity]:
        """Get detailed information about a specific activity."""
        pass

    @abstractmethod
    async def get_weather_advice(
        self,
        weather: WeatherConditions,
        activity_id: str
    ) -> Dict[str, Any]:
        """Get weather-specific advice for an activity."""
        pass

    @abstractmethod
    async def get_seasonal_activities(
        self,
        season: str,
        preferences: Optional[ActivityPreferences] = None
    ) -> List[Activity]:
        """Get activities suitable for a specific season."""
        pass

    @abstractmethod
    async def save_user_feedback(
        self,
        activity_id: str,
        weather_conditions: WeatherConditions,
        rating: float,
        feedback: Optional[str] = None
    ) -> bool:
        """Save user feedback for improving recommendations."""
        pass

    @abstractmethod
    async def get_trending_activities(
        self,
        weather: WeatherConditions,
        limit: int = 5
    ) -> List[Activity]:
        """Get trending activities for current weather."""
        pass