"""
Activity Suggestion Service for Weather Dashboard.

This service provides activity suggestions based on current weather conditions.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from ..models.capstone_models import (
    Activity,
    ActivityFactory,
    ActivitySuggestion,
    ActivityType,
)
from ..models.weather_models import CurrentWeather, WeatherCondition


class ActivitySuggestionService:
    """Service for suggesting activities based on weather conditions."""

    def __init__(self):
        """Initialize the activity suggestion service."""
        self.logger = logging.getLogger(__name__)
        self.activity_factory = ActivityFactory()
        self.activities: List[Activity] = self.activity_factory.get_default_activities()

        self.logger.info(
            f"Activity service initialized with {len(self.activities)} default activities"
        )

    def get_activity_suggestions(
        self, weather: CurrentWeather, max_suggestions: int = 5
    ) -> ActivitySuggestion:
        """
        Get activity suggestions based on current weather.

        Args:
            weather: Current weather conditions
            max_suggestions: Maximum number of suggestions to return

        Returns:
            ActivitySuggestion object with suggested activities
        """
        self.logger.info(
            f"Getting activity suggestions for {weather.location.display_name}"
        )

        suitable_activities = []

        for activity in self.activities:
            is_suitable, score = activity.is_suitable_for_weather(weather)
            if is_suitable:
                suitable_activities.append((activity, score))

        # Sort by suitability score (highest first)
        suitable_activities.sort(key=lambda x: x[1], reverse=True)

        # Limit the number of suggestions
        top_suggestions = suitable_activities[:max_suggestions]

        suggestion = ActivitySuggestion(
            weather=weather, suggested_activities=top_suggestions
        )

        self.logger.info(f"Generated {len(top_suggestions)} activity suggestions")
        return suggestion

    def get_activities_by_type(self, activity_type: ActivityType) -> List[Activity]:
        """
        Get all activities of a specific type.

        Args:
            activity_type: Type of activities to return

        Returns:
            List of activities of the specified type
        """
        return [
            activity
            for activity in self.activities
            if activity.activity_type == activity_type
        ]

    def get_indoor_activities(
        self, weather: CurrentWeather
    ) -> List[Tuple[Activity, float]]:
        """
        Get indoor activity suggestions.

        Args:
            weather: Current weather conditions

        Returns:
            List of indoor activities with suitability scores
        """
        indoor_activities = []

        for activity in self.activities:
            if activity.indoor:
                is_suitable, score = activity.is_suitable_for_weather(weather)
                if is_suitable:
                    indoor_activities.append((activity, score))

        indoor_activities.sort(key=lambda x: x[1], reverse=True)
        return indoor_activities

    def get_outdoor_activities(
        self, weather: CurrentWeather
    ) -> List[Tuple[Activity, float]]:
        """
        Get outdoor activity suggestions.

        Args:
            weather: Current weather conditions

        Returns:
            List of outdoor activities with suitability scores
        """
        outdoor_activities = []

        for activity in self.activities:
            if not activity.indoor:
                is_suitable, score = activity.is_suitable_for_weather(weather)
                if is_suitable:
                    outdoor_activities.append((activity, score))

        outdoor_activities.sort(key=lambda x: x[1], reverse=True)
        return outdoor_activities

    def add_custom_activity(self, activity: Activity) -> bool:
        """
        Add a custom activity to the suggestions.

        Args:
            activity: Activity to add

        Returns:
            True if added successfully
        """
        try:
            # Check if activity with same name already exists
            existing_names = [a.name.lower() for a in self.activities]
            if activity.name.lower() in existing_names:
                self.logger.warning(f"Activity '{activity.name}' already exists")
                return False

            self.activities.append(activity)
            self.logger.info(f"Added custom activity: {activity.name}")
            return True

        except Exception as e:
            self.logger.error(f"Error adding custom activity: {e}")
            return False

    def remove_activity(self, activity_name: str) -> bool:
        """
        Remove an activity by name.

        Args:
            activity_name: Name of activity to remove

        Returns:
            True if removed successfully
        """
        try:
            for i, activity in enumerate(self.activities):
                if activity.name.lower() == activity_name.lower():
                    removed = self.activities.pop(i)
                    self.logger.info(f"Removed activity: {removed.name}")
                    return True

            self.logger.warning(f"Activity '{activity_name}' not found")
            return False

        except Exception as e:
            self.logger.error(f"Error removing activity: {e}")
            return False

    def get_weather_suitability_explanation(
        self, activity: Activity, weather: CurrentWeather
    ) -> str:
        """
        Get explanation of why an activity is or isn't suitable for the weather.

        Args:
            activity: Activity to check
            weather: Current weather conditions

        Returns:
            Explanation string
        """
        is_suitable, score = activity.is_suitable_for_weather(weather)
        temp_c = weather.temperature.to_celsius()

        explanations = []

        if activity.indoor:
            explanations.append("This is an indoor activity, suitable in any weather.")
        else:
            # Temperature checks
            if (
                activity.min_temperature is not None
                and temp_c < activity.min_temperature
            ):
                explanations.append(
                    f"Too cold (needs ≥{activity.min_temperature}°C, current: {temp_c: .1f}°C)"
                )
            elif (
                activity.max_temperature is not None
                and temp_c > activity.max_temperature
            ):
                explanations.append(
                    f"Too hot (needs ≤{activity.max_temperature}°C, current: {temp_c: .1f}°C)"
                )
            else:
                explanations.append(f"Temperature is suitable ({temp_c: .1f}°C)")

            # Wind checks
            if (
                activity.max_wind_speed is not None
                and weather.wind.speed > activity.max_wind_speed
            ):
                explanations.append(
                    f"Too windy (needs ≤{activity.max_wind_speed}km/h, current: {weather.wind.speed}km/h)"
                )
            else:
                explanations.append(
                    f"Wind conditions are acceptable ({weather.wind.speed}km/h)"
                )

            # Weather condition checks
            if weather.condition in activity.ideal_conditions:
                explanations.append(
                    f"Perfect weather conditions ({weather.condition.value})"
                )
            elif (
                activity.requires_clear_weather
                and weather.condition != WeatherCondition.CLEAR
            ):
                explanations.append(
                    f"Requires clear weather (current: {weather.condition.value})"
                )
            else:
                explanations.append(
                    f"Weather conditions are acceptable ({weather.condition.value})"
                )

        suitability = (
            "Highly suitable"
            if score >= 8
            else "Suitable" if score >= 5 else "Moderately suitable"
        )

        if is_suitable:
            return f"{suitability} (Score: {score: .1f}/10). " + " ".join(explanations)
        else:
            return "Not suitable. " + " ".join(explanations)

    def get_activity_statistics(
        self, weather_history: List[CurrentWeather]
    ) -> Dict[str, Any]:
        """
        Get statistics about activity suggestions based on weather history.

        Args:
            weather_history: List of historical weather data

        Returns:
            Dictionary with activity statistics
        """
        if not weather_history:
            return {}

        activity_counts: Dict[str, int] = {}
        condition_counts: Dict[str, int] = {}

        for weather in weather_history:
            suggestions = self.get_activity_suggestions(weather, max_suggestions=3)

            # Count weather conditions
            condition = weather.condition.value
            condition_counts[condition] = condition_counts.get(condition, 0) + 1

            # Count suggested activities
            for activity, score in suggestions.suggested_activities:
                activity_counts[activity.name] = (
                    activity_counts.get(activity.name, 0) + 1
                )

        # Find most common activities and conditions
        most_common_activity = (
            max(activity_counts.items(), key=lambda x: x[1])
            if activity_counts
            else None
        )
        most_common_condition = (
            max(condition_counts.items(), key=lambda x: x[1])
            if condition_counts
            else None
        )

        return {
            "total_weather_records": len(weather_history),
            "activity_suggestions": activity_counts,
            "weather_conditions": condition_counts,
            "most_suggested_activity": (
                most_common_activity[0] if most_common_activity else None
            ),
            "most_common_condition": (
                most_common_condition[0] if most_common_condition else None
            ),
            "total_unique_activities": len(activity_counts),
            "average_suggestions_per_weather": (
                sum(activity_counts.values()) / len(weather_history)
                if weather_history
                else 0
            ),
        }

    def create_activity_report(self, weather: CurrentWeather) -> str:
        """
        Create a detailed activity report for the current weather.

        Args:
            weather: Current weather conditions

        Returns:
            Formatted activity report
        """
        suggestions = self.get_activity_suggestions(weather, max_suggestions=10)

        lines = []
        lines.append(f"🎯 Activity Suggestions for {weather.location.display_name}")
        lines.append("=" * 60)
        lines.append(f"Weather: {weather.description.title()}")
        lines.append(f"Temperature: {weather.temperature}")
        lines.append(f"Wind: {weather.wind.speed}km/h {weather.wind.direction_name}")
        lines.append(f"Humidity: {weather.humidity}%")
        lines.append("")

        if not suggestions.suggested_activities:
            lines.append(
                "😕 No suitable activities found for current weather conditions."
            )
            return "\n".join(lines)

        # Top suggestion
        if suggestions.top_suggestion:
            top_activity = suggestions.top_suggestion
            top_score = suggestions.suggested_activities[0][1]
            lines.append(f"🏆 Top Suggestion: {top_activity.name}")
            lines.append(f"   {top_activity.description}")
            lines.append(f"   Suitability: {top_score: .1f}/10")
            lines.append("")

        # Outdoor activities
        outdoor = suggestions.outdoor_activities
        if outdoor:
            lines.append("🌞 Outdoor Activities:")
            for activity, score in outdoor[:5]:
                lines.append(f"   • {activity.name} (Score: {score: .1f})")

        # Indoor activities
        indoor = suggestions.indoor_activities
        if indoor:
            lines.append("")
            lines.append("🏠 Indoor Activities:")
            for activity, score in indoor[:5]:
                lines.append(f"   • {activity.name} (Score: {score: .1f})")

        return "\n".join(lines)
