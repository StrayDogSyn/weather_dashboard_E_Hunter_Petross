"""Weather poetry models and generation."""

import json
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import auto
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from uuid import UUID
from uuid import uuid4

from .base import AIEnhancedModel
from .base import ExtensibleEnum
from .base import ModelProtocol


class PoemType(ExtensibleEnum):
    """Types of weather poems."""

    HAIKU = "haiku"
    SONNET = "sonnet"
    FREE_VERSE = "free_verse"
    LIMERICK = "limerick"
    ACROSTIC = "acrostic"
    CINQUAIN = "cinquain"
    TANKA = "tanka"


class TemperatureRange(ExtensibleEnum):
    """Temperature ranges for poetry context."""

    FREEZING = "freezing"
    COLD = "cold"
    COOL = "cool"
    MILD = "mild"
    WARM = "warm"
    HOT = "hot"
    SCORCHING = "scorching"


@dataclass
class PoemMetadata:
    """Metadata for weather poems."""

    syllable_count: Optional[int] = None
    line_count: int = 0
    rhyme_scheme: str = ""
    mood: str = "neutral"
    imagery_themes: List[str] = field(default_factory=list)
    literary_devices: List[str] = field(default_factory=list)
    reading_level: str = "intermediate"
    estimated_reading_time: int = 30  # seconds


@dataclass
class WeatherPoem(AIEnhancedModel, ModelProtocol):
    """AI-generated weather poetry with rich metadata."""

    poem_id: UUID = field(default_factory=uuid4)
    title: str = ""
    content: str = ""
    poem_type: PoemType = PoemType.FREE_VERSE

    # Weather context
    weather_condition: str = ""
    temperature_range: TemperatureRange = TemperatureRange.MILD
    location_context: Optional[str] = None
    inspiration_weather: Optional[str] = None

    # Poem metadata
    metadata: PoemMetadata = field(default_factory=PoemMetadata)

    # AI generation details
    ai_model_used: str = "gemini-pro"
    generation_prompt: str = ""
    confidence_score: float = 0.8

    # User interaction
    user_rating: Optional[int] = None  # 1-5 stars
    user_feedback: str = ""
    tags: List[str] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: Optional[datetime] = None

    # AI analysis
    ai_analysis: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize after creation."""
        super().__init__()
        if self.content:
            self._analyze_poem_structure()

    @property
    def formatted_text(self) -> str:
        """Get formatted poem text with proper line breaks."""
        if not self.content:
            return ""

        # Ensure proper line breaks for display
        lines = self.content.split("\n")
        formatted_lines = []

        for line in lines:
            line = line.strip()
            if line:
                formatted_lines.append(line)
            else:
                formatted_lines.append("")  # Preserve empty lines for stanza breaks

        return "\n".join(formatted_lines)

    @property
    def word_count(self) -> int:
        """Get word count of the poem."""
        return len(self.content.split()) if self.content else 0

    @property
    def line_count(self) -> int:
        """Get line count of the poem."""
        return (
            len([line for line in self.content.split("\n") if line.strip()])
            if self.content
            else 0
        )

    def _analyze_poem_structure(self) -> None:
        """Analyze and update poem metadata based on content."""
        if not self.content:
            return

        lines = [line.strip() for line in self.content.split("\n") if line.strip()]
        self.metadata.line_count = len(lines)

        # Detect poem type based on structure
        if len(lines) == 3 and self._count_syllables_roughly(lines) in [15, 17]:
            self.poem_type = PoemType.HAIKU
        elif len(lines) == 5:
            self.poem_type = PoemType.CINQUAIN
        elif len(lines) == 14:
            self.poem_type = PoemType.SONNET
        elif len(lines) == 5 and any("limerick" in tag.lower() for tag in self.tags):
            self.poem_type = PoemType.LIMERICK

        # Estimate reading time (average 150 words per minute)
        self.metadata.estimated_reading_time = max(10, (self.word_count / 150) * 60)

    def _count_syllables_roughly(self, lines: List[str]) -> int:
        """Rough syllable counting for haiku detection."""
        # Very simple syllable estimation
        total_syllables = 0
        for line in lines:
            words = line.split()
            for word in words:
                # Simple heuristic: count vowel groups
                vowels = "aeiouy"
                syllables = sum(
                    1
                    for i, char in enumerate(word.lower())
                    if char in vowels and (i == 0 or word[i - 1].lower() not in vowels)
                )
                total_syllables += max(1, syllables)  # At least 1 syllable per word
        return total_syllables

    def add_tag(self, tag: str) -> None:
        """Add a tag to the poem."""
        tag = tag.lower().strip()
        if tag and tag not in self.tags:
            self.tags.append(tag)
            self.last_modified = datetime.now()

    def set_user_rating(self, rating: int, feedback: str = "") -> None:
        """Set user rating and feedback."""
        if 1 <= rating <= 5:
            self.user_rating = rating
            self.user_feedback = feedback
            self.last_modified = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["poem_id"] = str(self.poem_id)
        data["poem_type"] = self.poem_type.value
        data["temperature_range"] = self.temperature_range.value
        data["created_at"] = self.created_at.isoformat()
        if self.last_modified:
            data["last_modified"] = self.last_modified.isoformat()
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeatherPoem":
        """Create from dictionary."""
        if "poem_type" in data:
            data["poem_type"] = PoemType(data["poem_type"])
        if "temperature_range" in data:
            data["temperature_range"] = TemperatureRange(data["temperature_range"])
        if "poem_id" in data and isinstance(data["poem_id"], str):
            data["poem_id"] = UUID(data["poem_id"])
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "last_modified" in data and isinstance(data["last_modified"], str):
            data["last_modified"] = datetime.fromisoformat(data["last_modified"])
        return cls(**data)

    def validate(self) -> bool:
        """Validate poem data."""
        return (
            bool(self.content)
            and self.poem_id is not None
            and 0 <= self.confidence_score <= 1
            and (self.user_rating is None or 1 <= self.user_rating <= 5)
        )

    def get_ai_prompt(self) -> str:
        """Generate AI prompt for poem analysis."""
        return f"""
        Analyze this weather-inspired poem and provide insights:
        
        Poem Type: {self.poem_type.value}
        Weather Context: {self.weather_condition}, {self.temperature_range.value}
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
        lines = analysis_text.split("\n")

        in_suggestions = False
        for line in lines:
            line = line.strip()
            if "suggestion" in line.lower():
                in_suggestions = True
            elif in_suggestions and line and not line.startswith("#"):
                suggestions.append(line)

        return suggestions[:5]  # Limit to 5 suggestions

    def get_summary(self) -> str:
        """Get a brief summary of the poem."""
        summary_parts = [
            f"'{self.title}'" if self.title else "Untitled Poem",
            f"({self.poem_type.value})",
            f"Weather: {self.weather_condition}",
            f"Lines: {self.line_count}",
            f"Words: {self.word_count}",
        ]

        if self.user_rating:
            summary_parts.append(f"Rating: {self.user_rating}/5")

        return " - ".join(summary_parts)

    def export_for_sharing(self) -> Dict[str, Any]:
        """Export poem data suitable for sharing."""
        return {
            "title": self.title,
            "content": self.formatted_text,
            "type": self.poem_type.value,
            "weather": self.weather_condition,
            "location": self.location_context,
            "created_date": self.created_at.strftime("%Y-%m-%d"),
            "word_count": self.word_count,
            "line_count": self.line_count,
        }
