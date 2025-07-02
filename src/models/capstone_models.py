"""
Extended models for Weather Dashboard capstone features.

This module contains additional models for:
- City Comparison
- Weather Journal
- Activity Suggestions
- Weather Poetry
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .weather_models import CurrentWeather, Location, WeatherCondition


class ActivityType(Enum):
    """Types of activities that can be suggested."""

    OUTDOOR_SPORTS = "outdoor_sports"
    INDOOR_ACTIVITIES = "indoor_activities"
    SIGHTSEEING = "sightseeing"
    EXERCISE = "exercise"
    RELAXATION = "relaxation"
    CULTURAL = "cultural"
    SHOPPING = "shopping"
    DINING = "dining"


class MoodType(Enum):
    """Mood types for weather journal."""

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


@dataclass
class WeatherComparison:
    """Represents a comparison between two cities' weather."""

    city1_weather: CurrentWeather
    city2_weather: CurrentWeather
    comparison_timestamp: datetime = field(default_factory=datetime.now)

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
    def warmer_city(self) -> str:
        """Get name of the warmer city."""
        if self.temperature_difference > 0:
            return self.city1_weather.location.display_name
        elif self.temperature_difference < 0:
            return self.city2_weather.location.display_name
        else:
            return "Same temperature"

    @property
    def better_weather_city(self) -> str:
        """Determine which city has 'better' weather based on multiple factors."""
        score1 = self._calculate_weather_score(self.city1_weather)
        score2 = self._calculate_weather_score(self.city2_weather)

        if score1 > score2:
            return self.city1_weather.location.display_name
        elif score2 > score1:
            return self.city2_weather.location.display_name
        else:
            return "Similar weather quality"

    def _calculate_weather_score(self, weather: CurrentWeather) -> float:
        """Calculate a weather quality score (higher is better)."""
        score = 0.0

        # Temperature score (prefer moderate temperatures)
        temp_c = weather.temperature.to_celsius()
        if 18 <= temp_c <= 26:  # Ideal range
            score += 10
        elif 15 <= temp_c <= 30:  # Good range
            score += 7
        elif 10 <= temp_c <= 35:  # Acceptable range
            score += 4

        # Humidity score (prefer moderate humidity)
        if 30 <= weather.humidity <= 60:  # Ideal range
            score += 5
        elif 20 <= weather.humidity <= 70:  # Good range
            score += 3

        # Wind score (prefer light breeze)
        if 5 <= weather.wind.speed <= 15:  # Light breeze
            score += 3
        elif weather.wind.speed <= 25:  # Moderate wind
            score += 1

        # Condition score
        if weather.condition == WeatherCondition.CLEAR:
            score += 8
        elif weather.condition == WeatherCondition.CLOUDS:
            score += 5
        elif weather.condition in [WeatherCondition.RAIN, WeatherCondition.DRIZZLE]:
            score += 2

        return score


@dataclass
class JournalEntry:
    """Represents a weather journal entry."""

    date: date
    location: str
    weather_summary: str
    temperature: float
    condition: str
    mood: MoodType
    notes: str
    activities: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def formatted_date(self) -> str:
        """Get formatted date string."""
        return self.date.strftime("%Y-%m-%d")

    @property
    def mood_emoji(self) -> str:
        """Get emoji for the mood."""
        mood_emojis = {
            MoodType.HAPPY: "😊",
            MoodType.SAD: "😢",
            MoodType.ENERGETIC: "⚡",
            MoodType.RELAXED: "😌",
            MoodType.EXCITED: "🤩",
            MoodType.PEACEFUL: "😇",
            MoodType.ANXIOUS: "😰",
            MoodType.CONTENT: "😊",
            MoodType.MOTIVATED: "💪",
            MoodType.COZY: "🤗",
        }
        return mood_emojis.get(self.mood, "😐")


@dataclass
class Activity:
    """Represents a suggested activity."""

    name: str
    description: str
    activity_type: ActivityType
    ideal_conditions: List[WeatherCondition]
    min_temperature: Optional[float] = None  # Celsius
    max_temperature: Optional[float] = None  # Celsius
    max_wind_speed: Optional[float] = None  # km/h
    requires_clear_weather: bool = False
    indoor: bool = False

    def is_suitable_for_weather(self, weather: CurrentWeather) -> Tuple[bool, float]:
        """
        Check if activity is suitable for given weather conditions.
        Returns (is_suitable, suitability_score).
        """
        score = 0.0

        # Temperature check
        temp_c = weather.temperature.to_celsius()
        if self.min_temperature is not None and temp_c < self.min_temperature:
            return False, 0.0
        if self.max_temperature is not None and temp_c > self.max_temperature:
            return False, 0.0

        # Wind check
        if self.max_wind_speed is not None and weather.wind.speed > self.max_wind_speed:
            return False, 0.0

        # Clear weather requirement
        if self.requires_clear_weather and weather.condition != WeatherCondition.CLEAR:
            return False, 0.0

        # Indoor activities are always suitable
        if self.indoor:
            score = 8.0
        else:
            # Condition scoring
            if weather.condition in self.ideal_conditions:
                score += 10.0
            elif weather.condition == WeatherCondition.CLEAR:
                score += 8.0
            elif weather.condition == WeatherCondition.CLOUDS:
                score += 6.0
            else:
                score += 3.0

            # Temperature scoring
            if self.min_temperature and self.max_temperature:
                optimal_temp = (self.min_temperature + self.max_temperature) / 2
                temp_diff = abs(temp_c - optimal_temp)
                score += max(0, 5 - temp_diff)

        return True, score


@dataclass
class ActivitySuggestion:
    """Represents activity suggestions for current weather."""

    weather: CurrentWeather
    suggested_activities: List[Tuple[Activity, float]]  # (activity, suitability_score)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def top_suggestion(self) -> Optional[Activity]:
        """Get the top activity suggestion."""
        if self.suggested_activities:
            return self.suggested_activities[0][0]
        return None

    @property
    def outdoor_activities(self) -> List[Tuple[Activity, float]]:
        """Get only outdoor activity suggestions."""
        return [
            (activity, score)
            for activity, score in self.suggested_activities
            if not activity.indoor
        ]

    @property
    def indoor_activities(self) -> List[Tuple[Activity, float]]:
        """Get only indoor activity suggestions."""
        return [
            (activity, score)
            for activity, score in self.suggested_activities
            if activity.indoor
        ]


@dataclass
class WeatherPoem:
    """Represents a weather-inspired poem or phrase."""

    text: str
    poem_type: str  # "haiku", "phrase", "limerick", etc.
    weather_condition: WeatherCondition
    temperature_range: str  # "cold", "mild", "warm", "hot"
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def formatted_text(self) -> str:
        """Get formatted poem text with proper line breaks."""
        if self.poem_type in ["haiku", "limerick"]:
            lines = self.text.split(" / ")
            return "\n".join(lines)
        return self.text


# Predefined activities database
DEFAULT_ACTIVITIES = [
    # Outdoor Sports
    Activity(
        name="Go for a bike ride",
        description="Enjoy cycling in pleasant weather",
        activity_type=ActivityType.OUTDOOR_SPORTS,
        ideal_conditions=[WeatherCondition.CLEAR, WeatherCondition.CLOUDS],
        min_temperature=10,
        max_temperature=30,
        max_wind_speed=25,
        indoor=False,
    ),
    Activity(
        name="Go hiking",
        description="Explore nature trails and scenic views",
        activity_type=ActivityType.OUTDOOR_SPORTS,
        ideal_conditions=[WeatherCondition.CLEAR, WeatherCondition.CLOUDS],
        min_temperature=5,
        max_temperature=28,
        max_wind_speed=30,
        indoor=False,
    ),
    Activity(
        name="Play outdoor sports",
        description="Basketball, tennis, or soccer in the park",
        activity_type=ActivityType.OUTDOOR_SPORTS,
        ideal_conditions=[WeatherCondition.CLEAR, WeatherCondition.CLOUDS],
        min_temperature=15,
        max_temperature=32,
        max_wind_speed=20,
        indoor=False,
    ),
    # Indoor Activities
    Activity(
        name="Read a book",
        description="Cozy up with a good book indoors",
        activity_type=ActivityType.RELAXATION,
        ideal_conditions=[
            WeatherCondition.RAIN,
            WeatherCondition.SNOW,
            WeatherCondition.THUNDERSTORM,
        ],
        indoor=True,
    ),
    Activity(
        name="Visit a museum",
        description="Explore art, history, or science exhibits",
        activity_type=ActivityType.CULTURAL,
        ideal_conditions=[WeatherCondition.RAIN, WeatherCondition.SNOW],
        indoor=True,
    ),
    Activity(
        name="Go shopping",
        description="Browse stores or malls",
        activity_type=ActivityType.SHOPPING,
        ideal_conditions=[
            WeatherCondition.RAIN,
            WeatherCondition.SNOW,
            WeatherCondition.THUNDERSTORM,
        ],
        indoor=True,
    ),
    Activity(
        name="Try indoor rock climbing",
        description="Challenge yourself at a climbing gym",
        activity_type=ActivityType.EXERCISE,
        ideal_conditions=[WeatherCondition.RAIN, WeatherCondition.SNOW],
        indoor=True,
    ),
    # Weather-specific activities
    Activity(
        name="Build a snowman",
        description="Have fun in the snow",
        activity_type=ActivityType.OUTDOOR_SPORTS,
        ideal_conditions=[WeatherCondition.SNOW],
        min_temperature=-10,
        max_temperature=2,
        indoor=False,
    ),
    Activity(
        name="Listen to rain",
        description="Enjoy the calming sound of rainfall",
        activity_type=ActivityType.RELAXATION,
        ideal_conditions=[WeatherCondition.RAIN, WeatherCondition.DRIZZLE],
        indoor=True,
    ),
    Activity(
        name="Photography walk",
        description="Capture beautiful weather scenes",
        activity_type=ActivityType.SIGHTSEEING,
        ideal_conditions=[
            WeatherCondition.CLEAR,
            WeatherCondition.CLOUDS,
            WeatherCondition.FOG,
        ],
        min_temperature=0,
        max_temperature=35,
        indoor=False,
    ),
    Activity(
        name="Picnic in the park",
        description="Enjoy outdoor dining",
        activity_type=ActivityType.DINING,
        ideal_conditions=[WeatherCondition.CLEAR, WeatherCondition.CLOUDS],
        min_temperature=18,
        max_temperature=28,
        max_wind_speed=15,
        requires_clear_weather=False,
        indoor=False,
    ),
]
