"""Factory patterns for creating capstone models."""

import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..weather_models import CurrentWeather
from ..weather_models import WeatherCondition
from .activities import Activity
from .activities import ActivityDifficulty
from .activities import ActivitySuggestion
from .activities import ActivityType
from .comparison import ComparisonStrategy
from .comparison import DefaultComparisonStrategy
from .comparison import OutdoorActivityStrategy
from .comparison import WeatherComparison
from .journal import JournalEntry
from .journal import MoodType
from .journal import WeatherImpact


class ActivityFactory:
    """Factory for creating activity suggestions based on weather conditions."""

    _activity_templates = {
        "outdoor": [
            {
                "name": "Nature Walk",
                "description": "Peaceful walk through natural surroundings",
                "activity_type": ActivityType.OUTDOOR,
                "difficulty": ActivityDifficulty.EASY,
                "ideal_conditions": ["clear", "clouds"],
                "duration_minutes": (30, 90),
                "participants": (1, 6),
            },
            {
                "name": "Hiking",
                "description": "Explore trails and enjoy scenic views",
                "activity_type": ActivityType.OUTDOOR,
                "difficulty": ActivityDifficulty.MODERATE,
                "ideal_conditions": ["clear", "clouds"],
                "duration_minutes": (60, 240),
                "participants": (1, 8),
            },
            {
                "name": "Outdoor Photography",
                "description": "Capture beautiful weather moments",
                "activity_type": ActivityType.CREATIVE,
                "difficulty": ActivityDifficulty.EASY,
                "ideal_conditions": ["clear", "clouds", "rain", "snow"],
                "duration_minutes": (45, 180),
                "participants": (1, 4),
            },
        ],
        "indoor": [
            {
                "name": "Reading by the Window",
                "description": "Enjoy a good book while watching the weather",
                "activity_type": ActivityType.RELAXATION,
                "difficulty": ActivityDifficulty.EASY,
                "ideal_conditions": ["rain", "snow", "thunderstorm"],
                "duration_minutes": (30, 180),
                "participants": (1, 1),
            },
            {
                "name": "Cooking a Warm Meal",
                "description": "Prepare comfort food perfect for the weather",
                "activity_type": ActivityType.CREATIVE,
                "difficulty": ActivityDifficulty.MODERATE,
                "ideal_conditions": ["rain", "snow", "cold"],
                "duration_minutes": (45, 120),
                "participants": (1, 4),
            },
            {
                "name": "Indoor Exercise",
                "description": "Stay active indoors with bodyweight exercises",
                "activity_type": ActivityType.EXERCISE,
                "difficulty": ActivityDifficulty.MODERATE,
                "ideal_conditions": ["rain", "thunderstorm", "extreme_heat"],
                "duration_minutes": (20, 60),
                "participants": (1, 2),
            },
        ],
        "weather_specific": {
            "rain": [
                {
                    "name": "Rain Watching Meditation",
                    "description": "Mindful listening to rainfall sounds",
                    "activity_type": ActivityType.RELAXATION,
                    "difficulty": ActivityDifficulty.EASY,
                    "ideal_conditions": ["rain", "drizzle"],
                    "duration_minutes": (15, 45),
                    "participants": (1, 3),
                }
            ],
            "snow": [
                {
                    "name": "Snow Photography",
                    "description": "Capture winter wonderland scenes",
                    "activity_type": ActivityType.CREATIVE,
                    "difficulty": ActivityDifficulty.EASY,
                    "ideal_conditions": ["snow"],
                    "duration_minutes": (30, 120),
                    "participants": (1, 4),
                }
            ],
            "clear": [
                {
                    "name": "Stargazing",
                    "description": "Observe celestial objects on clear nights",
                    "activity_type": ActivityType.EDUCATIONAL,
                    "difficulty": ActivityDifficulty.EASY,
                    "ideal_conditions": ["clear"],
                    "duration_minutes": (30, 180),
                    "participants": (1, 6),
                }
            ],
        },
    }

    @classmethod
    def get_default_activities(cls) -> List[Activity]:
        """Get a list of default activities from all templates."""
        activities = []

        # Add activities from all categories
        for template in cls._activity_templates["outdoor"]:
            activities.append(cls._create_activity_from_template(template))

        for template in cls._activity_templates["indoor"]:
            activities.append(cls._create_activity_from_template(template))

        # Add weather-specific activities
        for condition_activities in cls._activity_templates[
            "weather_specific"
        ].values():
            for template in condition_activities:
                activities.append(cls._create_activity_from_template(template))

        return activities

    @classmethod
    def create_weather_activities(
        cls, weather: CurrentWeather, max_activities: int = 5
    ) -> List[Activity]:
        """Create activity suggestions based on current weather."""
        activities = []
        condition = weather.condition.value.lower()
        temp_celsius = weather.temperature.to_celsius()

        # Determine if conditions favor outdoor or indoor activities
        outdoor_friendly = (
            condition in ["clear", "clouds"]
            and 0 <= temp_celsius <= 35
            and weather.wind.speed < 25
        )

        # Add weather-specific activities first
        if condition in cls._activity_templates["weather_specific"]:
            for template in cls._activity_templates["weather_specific"][condition]:
                activity = cls._create_activity_from_template(template)
                activities.append(activity)

        # Add outdoor activities if conditions are suitable
        if outdoor_friendly:
            for template in cls._activity_templates["outdoor"]:
                if len(activities) >= max_activities:
                    break
                if condition in template["ideal_conditions"]:
                    activity = cls._create_activity_from_template(template)
                    activities.append(activity)

        # Fill remaining slots with indoor activities
        while len(activities) < max_activities:
            for template in cls._activity_templates["indoor"]:
                if len(activities) >= max_activities:
                    break
                activity = cls._create_activity_from_template(template)
                activities.append(activity)

        return activities[:max_activities]

    @classmethod
    def create_activity_suggestion(
        cls, weather: CurrentWeather, user_preferences: Optional[Dict[str, Any]] = None
    ) -> ActivitySuggestion:
        """Create a complete activity suggestion with multiple options."""
        suggestion = ActivitySuggestion(
            weather_context=f"{weather.condition.value} at {weather.temperature.to_celsius():.1f}°C",
            location=weather.location.display_name,
            user_preferences=user_preferences or {},
        )

        # Generate activities
        activities = cls.create_weather_activities(weather)

        # Score and add each activity
        for activity in activities:
            score = cls._calculate_activity_score(activity, weather, user_preferences)
            reason = cls._generate_activity_reason(activity, weather)
            suggestion.add_activity_suggestion(activity, score, reason)

        return suggestion

    @classmethod
    def _create_activity_from_template(cls, template: Dict[str, Any]) -> Activity:
        """Create an Activity instance from a template."""
        return Activity(
            name=template["name"],
            description=template["description"],
            activity_type=template["activity_type"],
            difficulty=template["difficulty"],
            ideal_conditions=template["ideal_conditions"],
            duration_minutes=template["duration_minutes"],
            participants=template["participants"],
            indoor=template.get("indoor", False),
        )

    @classmethod
    def _calculate_activity_score(
        cls,
        activity: Activity,
        weather: CurrentWeather,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate suitability score for an activity given current weather."""
        score = 0.5  # Base score
        condition = weather.condition.value.lower()
        temp_celsius = weather.temperature.to_celsius()

        # Weather suitability
        if condition in activity.ideal_conditions:
            score += 0.3

        # Temperature suitability (very basic)
        if activity.activity_type == ActivityType.OUTDOOR:
            if 15 <= temp_celsius <= 25:
                score += 0.2
            elif 10 <= temp_celsius < 15 or 25 < temp_celsius <= 30:
                score += 0.1
        else:  # Indoor activities
            score += 0.1  # Always somewhat suitable

        # User preference matching
        if user_preferences:
            preferred_types = user_preferences.get("activity_types", [])
            if activity.activity_type.value in preferred_types:
                score += 0.2

            preferred_difficulty = user_preferences.get("difficulty_level")
            if (
                preferred_difficulty
                and activity.difficulty.value == preferred_difficulty
            ):
                score += 0.1

        return min(1.0, max(0.0, score))

    @classmethod
    def _generate_activity_reason(
        cls, activity: Activity, weather: CurrentWeather
    ) -> str:
        """Generate a reason why this activity is suggested."""
        condition = weather.condition.value.lower()
        temp_celsius = weather.temperature.to_celsius()

        reasons = []

        if condition in activity.ideal_conditions:
            reasons.append(f"Perfect for {condition} weather")

        if activity.activity_type == ActivityType.OUTDOOR and 15 <= temp_celsius <= 25:
            reasons.append("Ideal temperature for outdoor activities")
        elif activity.activity_type != ActivityType.OUTDOOR and condition in [
            "rain",
            "snow",
        ]:
            reasons.append("Great indoor alternative for current weather")

        if activity.difficulty == ActivityDifficulty.EASY:
            reasons.append("Easy to start and enjoy")

        return "; ".join(reasons) if reasons else "Suitable for current conditions"


class WeatherComparisonBuilder:
    """Builder for creating weather comparisons with different strategies."""

    def __init__(self):
        """Initialize the builder."""
        self.logger = logging.getLogger(__name__)
        self._reset()

    def _reset(self) -> None:
        """Reset the builder state."""
        self._weather1: Optional[CurrentWeather] = None
        self._weather2: Optional[CurrentWeather] = None
        self._strategy: Optional[ComparisonStrategy] = None

    def with_cities(
        self, weather1: CurrentWeather, weather2: CurrentWeather
    ) -> "WeatherComparisonBuilder":
        """Set the two weather conditions to compare."""
        self._weather1 = weather1
        self._weather2 = weather2
        return self

    def with_strategy(self, strategy: ComparisonStrategy) -> "WeatherComparisonBuilder":
        """Set the comparison strategy."""
        self._strategy = strategy
        return self

    def with_default_strategy(self) -> "WeatherComparisonBuilder":
        """Use the default comparison strategy."""
        self._strategy = DefaultComparisonStrategy()
        return self

    def with_outdoor_strategy(self) -> "WeatherComparisonBuilder":
        """Use the outdoor activity comparison strategy."""
        self._strategy = OutdoorActivityStrategy()
        return self

    def build(self) -> WeatherComparison:
        """Build the weather comparison."""
        if not self._weather1 or not self._weather2:
            raise ValueError("Both weather conditions must be set before building")

        if not self._strategy:
            self.logger.info("No strategy specified, using default")
            self._strategy = DefaultComparisonStrategy()

        comparison = WeatherComparison(
            city1_weather=self._weather1,
            city2_weather=self._weather2,
            strategy=self._strategy,
        )

        self._reset()  # Reset for next use
        return comparison

    @classmethod
    def quick_comparison(
        cls,
        weather1: CurrentWeather,
        weather2: CurrentWeather,
        strategy_type: str = "default",
    ) -> WeatherComparison:
        """Quick method to create a comparison with minimal setup."""
        builder = cls()
        builder.with_cities(weather1, weather2)

        if strategy_type == "outdoor":
            builder.with_outdoor_strategy()
        else:
            builder.with_default_strategy()

        return builder.build()
