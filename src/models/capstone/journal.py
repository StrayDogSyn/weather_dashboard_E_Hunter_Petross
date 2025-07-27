"""Weather journal models and mood tracking."""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from enum import auto
from typing import Any, ClassVar, Dict, List, Optional
from uuid import UUID, uuid4

from .base import AIEnhancedModel, ExtensibleEnum, ModelProtocol


class MoodType(ExtensibleEnum):
    """Enhanced mood types with extensibility."""

    EXCELLENT = "excellent"
    GOOD = "good"
    NEUTRAL = "neutral"
    POOR = "poor"
    TERRIBLE = "terrible"
    ENERGETIC = "energetic"
    CALM = "calm"
    ANXIOUS = "anxious"
    MOTIVATED = "motivated"
    LAZY = "lazy"


class WeatherImpact(ExtensibleEnum):
    """How weather impacts mood and activities."""

    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


@dataclass
class WeatherMoodCorrelation:
    """Correlation between weather conditions and mood."""

    weather_condition: str
    temperature_range: tuple
    mood_impact: float  # -1.0 to 1.0
    energy_impact: float  # -1.0 to 1.0
    activity_preference: List[str]
    sample_size: int = 1
    confidence: float = 0.5


@dataclass
class JournalEntry(AIEnhancedModel, ModelProtocol):
    """Enhanced weather journal entry with rich metadata."""

    # Core identification
    entry_id: UUID = field(default_factory=uuid4)
    date: date = field(default_factory=date.today)

    # Location and weather context
    location: str = ""
    weather_summary: str = ""
    temperature: Optional[float] = None
    weather_condition: str = ""

    # Mood and energy tracking
    mood: MoodType = MoodType.NEUTRAL
    energy_level: int = field(default=5)  # 1-10 scale
    weather_impact: WeatherImpact = WeatherImpact.NEUTRAL

    # Activities and experiences
    activities: List[str] = field(default_factory=list)
    activity_satisfaction: Dict[str, int] = field(
        default_factory=dict
    )  # activity -> 1-10

    # Personal notes and reflection
    notes: str = ""
    gratitude_notes: List[str] = field(default_factory=list)
    challenges_faced: List[str] = field(default_factory=list)
    lessons_learned: str = ""

    # Metadata
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    # AI enhancement
    ai_insights: Optional[str] = field(default=None, init=False)
    mood_patterns: Optional[Dict[str, Any]] = field(default=None, init=False)

    # Class-level constants
    ENERGY_SCALE: ClassVar[tuple] = (1, 10)
    SATISFACTION_SCALE: ClassVar[tuple] = (1, 10)

    def __post_init__(self):
        """Initialize after creation."""
        super().__init__()
        self.validate_data()

    @property
    def mood_emoji(self) -> str:
        """Get emoji representation of mood."""
        mood_emojis = {
            MoodType.EXCELLENT: "😄",
            MoodType.GOOD: "😊",
            MoodType.NEUTRAL: "😐",
            MoodType.POOR: "😔",
            MoodType.TERRIBLE: "😞",
            MoodType.ENERGETIC: "⚡",
            MoodType.CALM: "😌",
            MoodType.ANXIOUS: "😰",
            MoodType.MOTIVATED: "💪",
            MoodType.LAZY: "😴",
        }
        return mood_emojis.get(self.mood, "😐")

    @property
    def formatted_date(self) -> str:
        """Get formatted date string."""
        return self.date.strftime("%B %d, %Y")

    @property
    def weather_impact_description(self) -> str:
        """Get human-readable weather impact description."""
        descriptions = {
            WeatherImpact.VERY_POSITIVE: "Weather significantly boosted my mood",
            WeatherImpact.POSITIVE: "Weather had a positive effect on my day",
            WeatherImpact.NEUTRAL: "Weather didn't notably affect my mood",
            WeatherImpact.NEGATIVE: "Weather negatively impacted my mood",
            WeatherImpact.VERY_NEGATIVE: "Weather significantly dampened my spirits",
        }
        return descriptions.get(self.weather_impact, "No weather impact recorded")

    def add_activity(self, activity: str, satisfaction: Optional[int] = None) -> None:
        """Add an activity with optional satisfaction rating."""
        if activity not in self.activities:
            self.activities.append(activity)

        if satisfaction is not None and 1 <= satisfaction <= 10:
            self.activity_satisfaction[activity] = satisfaction

        self.updated_at = datetime.now()

    def add_gratitude(self, gratitude: str) -> None:
        """Add a gratitude note."""
        if gratitude and gratitude not in self.gratitude_notes:
            self.gratitude_notes.append(gratitude)
            self.updated_at = datetime.now()

    def add_challenge(self, challenge: str) -> None:
        """Add a challenge faced."""
        if challenge and challenge not in self.challenges_faced:
            self.challenges_faced.append(challenge)
            self.updated_at = datetime.now()

    def add_tag(self, tag: str) -> None:
        """Add a tag to the entry."""
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the entry."""
        tag = tag.lower().strip()
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()

    def calculate_overall_satisfaction(self) -> float:
        """Calculate overall satisfaction score from activities."""
        if not self.activity_satisfaction:
            return 5.0  # Neutral

        return sum(self.activity_satisfaction.values()) / len(
            self.activity_satisfaction
        )

    def get_mood_score(self) -> float:
        """Get numeric mood score (-2 to 2)."""
        mood_scores = {
            MoodType.TERRIBLE: -2.0,
            MoodType.POOR: -1.0,
            MoodType.NEUTRAL: 0.0,
            MoodType.GOOD: 1.0,
            MoodType.EXCELLENT: 2.0,
            MoodType.ANXIOUS: -1.5,
            MoodType.CALM: 1.5,
            MoodType.ENERGETIC: 1.5,
            MoodType.MOTIVATED: 1.5,
            MoodType.LAZY: -0.5,
        }
        return mood_scores.get(self.mood, 0.0)

    def validate_data(self) -> None:
        """Validate entry data."""
        # Validate energy level
        if not (1 <= self.energy_level <= 10):
            self.energy_level = max(1, min(10, self.energy_level))

        # Validate activity satisfaction scores
        for activity, score in list(self.activity_satisfaction.items()):
            if not (1 <= score <= 10):
                del self.activity_satisfaction[activity]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert enums to strings
        data["mood"] = self.mood.value
        data["weather_impact"] = self.weather_impact.value
        # Convert dates to strings
        data["date"] = self.date.isoformat()
        data["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            data["updated_at"] = self.updated_at.isoformat()
        # Convert UUID to string
        data["entry_id"] = str(self.entry_id)
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JournalEntry":
        """Create from dictionary."""
        # Convert string values back to proper types
        if "mood" in data:
            data["mood"] = MoodType(data["mood"])
        if "weather_impact" in data:
            data["weather_impact"] = WeatherImpact(data["weather_impact"])
        if "date" in data and isinstance(data["date"], str):
            data["date"] = date.fromisoformat(data["date"])
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if "entry_id" in data and isinstance(data["entry_id"], str):
            data["entry_id"] = UUID(data["entry_id"])

        return cls(**data)

    def validate(self) -> bool:
        """Validate the journal entry."""
        return (
            self.entry_id is not None
            and isinstance(self.date, date)
            and isinstance(self.mood, MoodType)
            and isinstance(self.weather_impact, WeatherImpact)
            and 1 <= self.energy_level <= 10
        )

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
            "mood_score": self.get_mood_score(),
            "energy_level": self.energy_level,
            "weather_correlation": self.weather_impact.value,
            "activity_satisfaction": self.calculate_overall_satisfaction(),
            "tags": self.tags,
        }

    def get_summary(self) -> str:
        """Get a brief summary of the journal entry."""
        return (
            f"{self.formatted_date} - {self.mood.value.title()} mood "
            f"({self.mood_emoji}) in {self.location}. "
            f"Weather: {self.weather_summary}. "
            f"Energy: {self.energy_level}/10. "
            f"{len(self.activities)} activities recorded."
        )
