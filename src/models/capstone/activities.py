"""Activity suggestion models and enums."""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import auto
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from .base import AIEnhancedModel, ExtensibleEnum, ModelProtocol


class ActivityType(ExtensibleEnum):
    """Types of activities with extensibility."""

    OUTDOOR = "outdoor"
    INDOOR = "indoor"
    SPORTS = "sports"
    CULTURAL = "cultural"
    SOCIAL = "social"
    EXERCISE = "exercise"
    RELAXATION = "relaxation"
    CREATIVE = "creative"
    EDUCATIONAL = "educational"
    ADVENTURE = "adventure"


class ActivityDifficulty(ExtensibleEnum):
    """Activity difficulty levels."""

    EASY = "easy"
    MODERATE = "moderate"
    CHALLENGING = "challenging"
    EXPERT = "expert"


class SeasonalPreference(ExtensibleEnum):
    """Seasonal activity preferences."""

    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"
    ALL_SEASONS = "all_seasons"


@dataclass
class ActivityRequirements:
    """Requirements and constraints for activities."""

    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    preferred_conditions: List[str] = field(default_factory=list)
    avoid_conditions: List[str] = field(default_factory=list)
    max_wind_speed: Optional[float] = None
    indoor_alternative: bool = True
    equipment_needed: List[str] = field(default_factory=list)
    group_size_range: Tuple[int, int] = (1, 10)
    duration_minutes: Tuple[int, int] = (30, 120)
    accessibility_level: str = "moderate"


@dataclass
class Activity(AIEnhancedModel, ModelProtocol):
    """Enhanced activity model with weather dependencies."""

    activity_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    activity_type: ActivityType = ActivityType.OUTDOOR
    difficulty: ActivityDifficulty = ActivityDifficulty.EASY
    seasonal_preference: SeasonalPreference = SeasonalPreference.ALL_SEASONS

    # Weather requirements
    requirements: ActivityRequirements = field(default_factory=ActivityRequirements)
    indoor: bool = False
    ideal_conditions: List[str] = field(default_factory=list)

    # Activity details
    duration_minutes: Tuple[int, int] = (30, 120)
    participants: Tuple[int, int] = (1, 4)
    cost_estimate: str = "free"

    # Enhancement data
    tags: List[str] = field(default_factory=list)
    popularity_score: float = 5.0  # 1-10
    safety_rating: float = 8.0  # 1-10
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Initialize after creation."""
        super().__init__()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["activity_type"] = self.activity_type.value
        data["difficulty"] = self.difficulty.value
        data["seasonal_preference"] = self.seasonal_preference.value
        data["activity_id"] = str(self.activity_id)
        data["created_at"] = self.created_at.isoformat()
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Activity":
        """Create from dictionary."""
        if "activity_type" in data:
            data["activity_type"] = ActivityType(data["activity_type"])
        if "difficulty" in data:
            data["difficulty"] = ActivityDifficulty(data["difficulty"])
        if "seasonal_preference" in data:
            data["seasonal_preference"] = SeasonalPreference(
                data["seasonal_preference"]
            )
        if "activity_id" in data and isinstance(data["activity_id"], str):
            data["activity_id"] = UUID(data["activity_id"])
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)

    def validate(self) -> bool:
        """Validate activity data."""
        return (
            bool(self.name)
            and bool(self.description)
            and 1 <= self.popularity_score <= 10
            and 1 <= self.safety_rating <= 10
        )

    def get_ai_prompt(self) -> str:
        """Generate AI prompt for activity enhancement."""
        return f"""
        Enhance and create variations for this activity:

        Activity: {self.name}
        Description: {self.description}
        Type: {self.activity_type.value}
        Difficulty: {self.difficulty.value}
        Indoor: {self.indoor}
        Ideal Conditions: {self.ideal_conditions}
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
        lines = ai_text.split("\n")

        current_variation = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                if any(
                    word in line.lower()
                    for word in ["variation", "alternative", "option"]
                ):
                    if current_variation:
                        variations.append(current_variation)
                    current_variation = {"description": line}
                elif current_variation:
                    current_variation["details"] = (
                        current_variation.get("details", "") + " " + line
                    )

        if current_variation:
            variations.append(current_variation)

        return variations[:5]  # Limit to 5 variations


@dataclass
class ActivitySuggestion(AIEnhancedModel, ModelProtocol):
    """AI-enhanced activity suggestion with personalization."""

    suggestion_id: UUID = field(default_factory=uuid4)
    activity: Activity = None
    weather_context: str = ""
    confidence_score: float = 0.8  # 0-1
    reasoning: str = ""

    # Personalization
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    suggested_activities: List[Tuple[Activity, float, str]] = field(
        default_factory=list
    )

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    location: str = ""
    ai_recommendations: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize after creation."""
        super().__init__()

    def add_activity_suggestion(
        self, activity: Activity, score: float, reason: str
    ) -> None:
        """Add an activity suggestion with score and reasoning."""
        self.suggested_activities.append((activity, score, reason))
        # Sort by score in descending order
        self.suggested_activities.sort(key=lambda x: x[1], reverse=True)

    def get_top_suggestions(self, limit: int = 5) -> List[Tuple[Activity, float, str]]:
        """Get top activity suggestions."""
        return self.suggested_activities[:limit]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["suggestion_id"] = str(self.suggestion_id)
        data["created_at"] = self.created_at.isoformat()

        # Convert suggested activities
        activities_data = []
        for activity, score, reason in self.suggested_activities:
            activities_data.append(
                {"activity": activity.to_dict(), "score": score, "reason": reason}
            )
        data["suggested_activities"] = activities_data

        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActivitySuggestion":
        """Create from dictionary."""
        # Implementation would parse the complex structure
        raise NotImplementedError("from_dict method needs full implementation")

    def validate(self) -> bool:
        """Validate suggestion data."""
        return (
            self.suggestion_id is not None
            and 0 <= self.confidence_score <= 1
            and bool(self.weather_context)
        )

    def get_ai_prompt(self) -> str:
        """Generate AI prompt for personalized activity suggestions."""
        current_activities = [
            activity.name for activity, _, _ in self.suggested_activities[:5]
        ]

        return f"""
        Given the current weather and existing activity suggestions, provide personalized recommendations:

        Weather Conditions:
        - Location: {self.location}
        - Weather Context: {self.weather_context}

        Current Top Suggestions:
        {', '.join(current_activities)}

        User Preferences:
        {json.dumps(self.user_preferences, indent=2) if self.user_preferences else 'No specific preferences provided'}

        Please provide:
        1. 3-5 highly personalized activity suggestions
        2. Specific reasons why each activity suits the current weather
        3. Tips for making the most of these weather conditions
        4. Any safety or preparation advice

        Keep suggestions practical and weather-appropriate (under 200 words total).
        """
