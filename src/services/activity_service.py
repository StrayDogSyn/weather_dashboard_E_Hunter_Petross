"""Weather-based activity recommendation service implementation."""

import asyncio
import json
import logging
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from ..interfaces.activity_interfaces import (
    Activity,
    ActivityCategory,
    ActivityDifficulty,
    ActivityDuration,
    ActivityFilter,
    ActivityPreferences,
    ActivityRecommendation,
    ActivityRequest,
    ActivityResponse,
    IActivityDatabase,
    IActivityService,
    IPreferenceMatcher,
    IRecommendationEngine,
    IWeatherMatcher,
    WeatherConditions,
    WeatherRequirement,
    WeatherSuitability,
)

logger = logging.getLogger(__name__)


class InMemoryActivityDatabase(IActivityDatabase):
    """In-memory activity database with predefined activities."""

    def __init__(self):
        self._activities: Dict[str, Activity] = {}
        self._initialize_default_activities()

    async def get_all_activities(self) -> List[Activity]:
        """Get all available activities."""
        return list(self._activities.values())

    async def get_activity_by_id(self, activity_id: str) -> Optional[Activity]:
        """Get activity by ID."""
        return self._activities.get(activity_id)

    async def search_activities(
        self, filter_criteria: ActivityFilter
    ) -> List[Activity]:
        """Search activities by filter criteria."""
        activities = list(self._activities.values())

        if filter_criteria.categories:
            activities = [
                a for a in activities if a.category in filter_criteria.categories
            ]

        if filter_criteria.difficulty:
            activities = [
                a for a in activities if a.difficulty == filter_criteria.difficulty
            ]

        if filter_criteria.duration:
            activities = [
                a for a in activities if a.duration == filter_criteria.duration
            ]

        if filter_criteria.indoor_only:
            activities = [a for a in activities if a.indoor]

        if filter_criteria.outdoor_only:
            activities = [a for a in activities if not a.indoor]

        if filter_criteria.equipment_available:
            available_equipment = set(filter_criteria.equipment_available)
            activities = [
                a
                for a in activities
                if not a.equipment_needed
                or set(a.equipment_needed).issubset(available_equipment)
            ]

        if filter_criteria.group_size:
            activities = [
                a
                for a in activities
                if a.min_participants <= filter_criteria.group_size
                and (
                    a.max_participants is None
                    or filter_criteria.group_size <= a.max_participants
                )
            ]

        return activities

    async def get_activities_by_category(
        self, category: ActivityCategory
    ) -> List[Activity]:
        """Get activities by category."""
        return [a for a in self._activities.values() if a.category == category]

    async def add_activity(self, activity: Activity) -> bool:
        """Add new activity to database."""
        try:
            self._activities[activity.id] = activity
            return True
        except Exception as e:
            logger.error(f"Error adding activity: {e}")
            return False

    async def update_activity(self, activity: Activity) -> bool:
        """Update existing activity."""
        try:
            if activity.id in self._activities:
                self._activities[activity.id] = activity
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating activity: {e}")
            return False

    async def delete_activity(self, activity_id: str) -> bool:
        """Delete activity from database."""
        try:
            if activity_id in self._activities:
                del self._activities[activity_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting activity: {e}")
            return False

    def _initialize_default_activities(self):
        """Initialize database with default activities."""
        default_activities = [
            # Outdoor Sports
            Activity(
                id="hiking",
                name="Hiking",
                description="Explore nature trails and enjoy scenic views",
                category=ActivityCategory.OUTDOOR_SPORTS,
                difficulty=ActivityDifficulty.MODERATE,
                duration=ActivityDuration.MEDIUM,
                indoor=False,
                equipment_needed=["hiking boots", "water bottle", "backpack"],
                cost_estimate="low",
                location_type="park",
                safety_considerations=[
                    "check weather conditions",
                    "inform someone of your route",
                ],
            ),
            Activity(
                id="cycling",
                name="Cycling",
                description="Bike ride through parks or city paths",
                category=ActivityCategory.OUTDOOR_SPORTS,
                difficulty=ActivityDifficulty.EASY,
                duration=ActivityDuration.MEDIUM,
                indoor=False,
                equipment_needed=["bicycle", "helmet"],
                cost_estimate="low",
                location_type="park",
            ),
            Activity(
                id="tennis",
                name="Tennis",
                description="Play tennis at local courts",
                category=ActivityCategory.OUTDOOR_SPORTS,
                difficulty=ActivityDifficulty.MODERATE,
                duration=ActivityDuration.SHORT,
                indoor=False,
                equipment_needed=["tennis racket", "tennis balls"],
                cost_estimate="medium",
                location_type="venue",
                min_participants=2,
                max_participants=4,
            ),
            # Indoor Sports
            Activity(
                id="gym_workout",
                name="Gym Workout",
                description="Strength training and cardio at the gym",
                category=ActivityCategory.INDOOR_SPORTS,
                difficulty=ActivityDifficulty.MODERATE,
                duration=ActivityDuration.SHORT,
                indoor=True,
                equipment_needed=["gym membership"],
                cost_estimate="medium",
                location_type="gym",
            ),
            Activity(
                id="swimming_indoor",
                name="Indoor Swimming",
                description="Swimming laps in an indoor pool",
                category=ActivityCategory.INDOOR_SPORTS,
                difficulty=ActivityDifficulty.EASY,
                duration=ActivityDuration.SHORT,
                indoor=True,
                equipment_needed=["swimsuit", "goggles"],
                cost_estimate="medium",
                location_type="venue",
            ),
            # Recreation
            Activity(
                id="picnic",
                name="Picnic",
                description="Outdoor meal in a park or scenic location",
                category=ActivityCategory.RECREATION,
                difficulty=ActivityDifficulty.EASY,
                duration=ActivityDuration.MEDIUM,
                indoor=False,
                equipment_needed=["picnic blanket", "food", "drinks"],
                cost_estimate="low",
                location_type="park",
                min_participants=2,
            ),
            Activity(
                id="beach_day",
                name="Beach Day",
                description="Relax and enjoy activities at the beach",
                category=ActivityCategory.RECREATION,
                difficulty=ActivityDifficulty.EASY,
                duration=ActivityDuration.LONG,
                indoor=False,
                equipment_needed=["sunscreen", "towel", "water"],
                cost_estimate="low",
                location_type="beach",
                seasonal_availability=["spring", "summer"],
            ),
            # Cultural
            Activity(
                id="museum_visit",
                name="Museum Visit",
                description="Explore art, history, or science museums",
                category=ActivityCategory.CULTURAL,
                difficulty=ActivityDifficulty.EASY,
                duration=ActivityDuration.MEDIUM,
                indoor=True,
                equipment_needed=[],
                cost_estimate="medium",
                location_type="venue",
            ),
            Activity(
                id="movie_theater",
                name="Movie Theater",
                description="Watch the latest films in cinema",
                category=ActivityCategory.CULTURAL,
                difficulty=ActivityDifficulty.EASY,
                duration=ActivityDuration.SHORT,
                indoor=True,
                equipment_needed=[],
                cost_estimate="medium",
                location_type="venue",
            ),
            # Adventure
            Activity(
                id="rock_climbing",
                name="Rock Climbing",
                description="Indoor or outdoor rock climbing",
                category=ActivityCategory.ADVENTURE,
                difficulty=ActivityDifficulty.CHALLENGING,
                duration=ActivityDuration.MEDIUM,
                indoor=False,
                equipment_needed=["climbing gear", "helmet"],
                cost_estimate="high",
                location_type="venue",
                safety_considerations=[
                    "proper training required",
                    "use safety equipment",
                ],
            ),
            # Family
            Activity(
                id="playground",
                name="Playground Visit",
                description="Fun activities for children at local playground",
                category=ActivityCategory.FAMILY,
                difficulty=ActivityDifficulty.EASY,
                duration=ActivityDuration.SHORT,
                indoor=False,
                equipment_needed=[],
                cost_estimate="low",
                location_type="park",
                age_restrictions="child-friendly",
            ),
            Activity(
                id="board_games",
                name="Board Games",
                description="Indoor board game session with family or friends",
                category=ActivityCategory.FAMILY,
                difficulty=ActivityDifficulty.EASY,
                duration=ActivityDuration.SHORT,
                indoor=True,
                equipment_needed=["board games"],
                cost_estimate="low",
                location_type="home",
                min_participants=2,
            ),
            # Shopping
            Activity(
                id="shopping_mall",
                name="Shopping Mall",
                description="Browse stores and shop for items",
                category=ActivityCategory.SHOPPING,
                difficulty=ActivityDifficulty.EASY,
                duration=ActivityDuration.MEDIUM,
                indoor=True,
                equipment_needed=[],
                cost_estimate="medium",
                location_type="venue",
            ),
        ]

        for activity in default_activities:
            self._activities[activity.id] = activity


class WeatherMatcher(IWeatherMatcher):
    """Matches weather conditions to activity suitability."""

    def __init__(self):
        self._weather_requirements = self._initialize_weather_requirements()

    async def calculate_weather_suitability(
        self,
        activity: Activity,
        weather: WeatherConditions,
        requirements: WeatherRequirement,
    ) -> WeatherSuitability:
        """Calculate weather suitability for an activity."""
        score = await self.get_weather_score(activity, weather, requirements)

        if score >= 0.8:
            return WeatherSuitability.EXCELLENT
        elif score >= 0.6:
            return WeatherSuitability.GOOD
        elif score >= 0.4:
            return WeatherSuitability.FAIR
        elif score >= 0.2:
            return WeatherSuitability.POOR
        else:
            return WeatherSuitability.NOT_SUITABLE

    async def get_weather_score(
        self,
        activity: Activity,
        weather: WeatherConditions,
        requirements: WeatherRequirement,
    ) -> float:
        """Get numerical weather match score (0.0 to 1.0)."""
        score = 1.0
        penalty_factor = 0.0

        # Temperature checks
        if requirements.min_temperature is not None:
            if weather.temperature < requirements.min_temperature:
                penalty_factor += 0.3

        if requirements.max_temperature is not None:
            if weather.temperature > requirements.max_temperature:
                penalty_factor += 0.3

        # Wind speed checks
        if requirements.max_wind_speed is not None:
            if weather.wind_speed > requirements.max_wind_speed:
                penalty_factor += 0.2

        # Precipitation checks
        if requirements.max_precipitation is not None:
            if weather.precipitation > requirements.max_precipitation:
                penalty_factor += 0.4  # Heavy penalty for rain on outdoor activities

        # Visibility checks
        if requirements.min_visibility is not None:
            if weather.visibility < requirements.min_visibility:
                penalty_factor += 0.2

        # Humidity checks
        if requirements.max_humidity is not None:
            if weather.humidity > requirements.max_humidity:
                penalty_factor += 0.1

        # UV index checks
        if requirements.max_uv_index is not None and weather.uv_index is not None:
            if weather.uv_index > requirements.max_uv_index:
                penalty_factor += 0.1

        # Prohibited conditions
        if requirements.prohibited_conditions and weather.condition:
            for prohibited in requirements.prohibited_conditions:
                if prohibited.lower() in weather.condition.lower():
                    penalty_factor += 0.5

        # Indoor activities are less affected by weather
        if activity.indoor:
            penalty_factor *= 0.3

        return max(0.0, score - penalty_factor)

    async def get_weather_requirements(self, activity: Activity) -> WeatherRequirement:
        """Get weather requirements for an activity."""
        return self._weather_requirements.get(activity.id, WeatherRequirement())

    async def generate_weather_warnings(
        self, activity: Activity, weather: WeatherConditions
    ) -> List[str]:
        """Generate weather-related warnings for an activity."""
        warnings = []

        if not activity.indoor:
            if weather.precipitation > 5.0:
                warnings.append("Heavy rain expected - consider indoor alternatives")
            elif weather.precipitation > 0.5:
                warnings.append("Light rain possible - bring waterproof gear")

            if weather.wind_speed > 15.0:
                warnings.append("Strong winds expected - exercise caution")

            if weather.temperature < 0:
                warnings.append("Freezing temperatures - dress warmly")
            elif weather.temperature > 35:
                warnings.append("Very hot weather - stay hydrated and seek shade")

            if weather.uv_index and weather.uv_index > 7:
                warnings.append("High UV index - use sunscreen and protective clothing")

        return warnings

    def _initialize_weather_requirements(self) -> Dict[str, WeatherRequirement]:
        """Initialize weather requirements for activities."""
        return {
            "hiking": WeatherRequirement(
                min_temperature=-5.0,
                max_temperature=35.0,
                max_wind_speed=20.0,
                max_precipitation=2.0,
                min_visibility=1000.0,
                prohibited_conditions=["thunderstorm", "severe"],
            ),
            "cycling": WeatherRequirement(
                min_temperature=5.0,
                max_temperature=35.0,
                max_wind_speed=25.0,
                max_precipitation=1.0,
                min_visibility=2000.0,
                prohibited_conditions=["thunderstorm", "fog"],
            ),
            "tennis": WeatherRequirement(
                min_temperature=10.0,
                max_temperature=35.0,
                max_wind_speed=15.0,
                max_precipitation=0.1,
                prohibited_conditions=["rain", "thunderstorm"],
            ),
            "picnic": WeatherRequirement(
                min_temperature=15.0,
                max_temperature=35.0,
                max_wind_speed=20.0,
                max_precipitation=0.1,
                prohibited_conditions=["rain", "thunderstorm"],
            ),
            "beach_day": WeatherRequirement(
                min_temperature=20.0,
                max_temperature=40.0,
                max_wind_speed=25.0,
                max_precipitation=0.1,
                prohibited_conditions=["thunderstorm"],
            ),
            "rock_climbing": WeatherRequirement(
                min_temperature=5.0,
                max_temperature=30.0,
                max_wind_speed=15.0,
                max_precipitation=0.0,
                prohibited_conditions=["rain", "thunderstorm", "fog"],
            ),
            "playground": WeatherRequirement(
                min_temperature=10.0,
                max_temperature=35.0,
                max_wind_speed=20.0,
                max_precipitation=0.5,
                prohibited_conditions=["thunderstorm"],
            ),
        }


class PreferenceMatcher(IPreferenceMatcher):
    """Matches user preferences to activities."""

    async def calculate_preference_score(
        self, activity: Activity, preferences: ActivityPreferences
    ) -> float:
        """Calculate preference match score (0.0 to 1.0)."""
        score = 0.0
        total_weight = 0.0

        # Category preference (high weight)
        if preferences.preferred_categories:
            weight = 0.4
            total_weight += weight
            if activity.category in preferences.preferred_categories:
                score += weight

        # Difficulty preference
        if preferences.difficulty_level:
            weight = 0.2
            total_weight += weight
            if activity.difficulty == preferences.difficulty_level:
                score += weight

        # Duration preference
        if preferences.duration:
            weight = 0.2
            total_weight += weight
            if activity.duration == preferences.duration:
                score += weight

        # Indoor/outdoor preference
        if preferences.indoor_preference is not None:
            weight = 0.1
            total_weight += weight
            if activity.indoor == preferences.indoor_preference:
                score += weight

        # Group size compatibility
        if preferences.group_size:
            weight = 0.1
            total_weight += weight
            if activity.min_participants <= preferences.group_size and (
                activity.max_participants is None
                or preferences.group_size <= activity.max_participants
            ):
                score += weight

        # If no preferences specified, return neutral score
        if total_weight == 0:
            return 0.5

        return score / total_weight

    async def filter_by_preferences(
        self, activities: List[Activity], preferences: ActivityPreferences
    ) -> List[Activity]:
        """Filter activities by user preferences."""
        filtered = activities.copy()

        # Filter by categories
        if preferences.preferred_categories:
            filtered = [
                a for a in filtered if a.category in preferences.preferred_categories
            ]

        # Filter by difficulty
        if preferences.difficulty_level:
            filtered = [
                a for a in filtered if a.difficulty == preferences.difficulty_level
            ]

        # Filter by duration
        if preferences.duration:
            filtered = [a for a in filtered if a.duration == preferences.duration]

        # Filter by indoor/outdoor preference
        if preferences.indoor_preference is not None:
            filtered = [
                a for a in filtered if a.indoor == preferences.indoor_preference
            ]

        # Filter by group size
        if preferences.group_size:
            filtered = [
                a
                for a in filtered
                if a.min_participants <= preferences.group_size
                and (
                    a.max_participants is None
                    or preferences.group_size <= a.max_participants
                )
            ]

        return filtered

    async def get_preference_reasons(
        self, activity: Activity, preferences: ActivityPreferences
    ) -> List[str]:
        """Get reasons why activity matches preferences."""
        reasons = []

        if (
            preferences.preferred_categories
            and activity.category in preferences.preferred_categories
        ):
            reasons.append(
                f"Matches your interest in {activity.category.value.replace('_', ' ')}"
            )

        if (
            preferences.difficulty_level
            and activity.difficulty == preferences.difficulty_level
        ):
            reasons.append(f"Suitable for {activity.difficulty.value} difficulty level")

        if preferences.duration and activity.duration == preferences.duration:
            reasons.append(f"Fits your preferred {activity.duration.value} duration")

        if preferences.indoor_preference is not None:
            if preferences.indoor_preference and activity.indoor:
                reasons.append("Indoor activity as preferred")
            elif not preferences.indoor_preference and not activity.indoor:
                reasons.append("Outdoor activity as preferred")

        if preferences.group_size:
            if activity.min_participants <= preferences.group_size:
                if activity.max_participants is None:
                    reasons.append(
                        f"Suitable for groups of {preferences.group_size} or more"
                    )
                elif preferences.group_size <= activity.max_participants:
                    reasons.append(
                        f"Perfect for your group size of {preferences.group_size}"
                    )

        return reasons


class RecommendationEngine(IRecommendationEngine):
    """Engine for generating activity recommendations."""

    def __init__(
        self, weather_matcher: IWeatherMatcher, preference_matcher: IPreferenceMatcher
    ):
        self.weather_matcher = weather_matcher
        self.preference_matcher = preference_matcher

    async def generate_recommendations(
        self, request: ActivityRequest
    ) -> List[ActivityRecommendation]:
        """Generate activity recommendations based on request."""
        # This would typically get activities from database
        # For now, we'll use a mock set of activities
        all_activities = await self._get_available_activities()

        # Filter by preferences first
        suitable_activities = await self.preference_matcher.filter_by_preferences(
            all_activities, request.preferences
        )

        # Rank activities
        recommendations = await self.rank_activities(
            suitable_activities, request.weather_conditions, request.preferences
        )

        # Limit results
        return recommendations[: request.max_recommendations]

    async def rank_activities(
        self,
        activities: List[Activity],
        weather: WeatherConditions,
        preferences: ActivityPreferences,
    ) -> List[ActivityRecommendation]:
        """Rank activities based on weather and preferences."""
        recommendations = []

        for activity in activities:
            # Get weather requirements and calculate scores
            weather_req = await self.weather_matcher.get_weather_requirements(activity)
            weather_score = await self.weather_matcher.get_weather_score(
                activity, weather, weather_req
            )
            weather_suitability = (
                await self.weather_matcher.calculate_weather_suitability(
                    activity, weather, weather_req
                )
            )

            # Calculate preference score
            preference_score = await self.preference_matcher.calculate_preference_score(
                activity, preferences
            )

            # Calculate overall confidence score (weighted average)
            confidence_score = (weather_score * 0.6) + (preference_score * 0.4)

            # Get reasons and warnings
            preference_reasons = await self.preference_matcher.get_preference_reasons(
                activity, preferences
            )
            weather_warnings = await self.weather_matcher.generate_weather_warnings(
                activity, weather
            )

            # Generate preparation tips
            prep_tips = await self.generate_preparation_tips(activity, weather)

            recommendation = ActivityRecommendation(
                activity=activity,
                suitability=weather_suitability,
                confidence_score=confidence_score,
                weather_match_score=weather_score,
                preference_match_score=preference_score,
                reasons=preference_reasons,
                warnings=weather_warnings if weather_warnings else None,
                preparation_tips=prep_tips if prep_tips else None,
            )

            recommendations.append(recommendation)

        # Sort by confidence score (descending)
        recommendations.sort(key=lambda x: x.confidence_score, reverse=True)

        return recommendations

    async def get_indoor_alternatives(
        self, outdoor_activities: List[Activity], preferences: ActivityPreferences
    ) -> List[ActivityRecommendation]:
        """Get indoor alternatives for outdoor activities."""
        # Get all indoor activities
        all_activities = await self._get_available_activities()
        indoor_activities = [a for a in all_activities if a.indoor]

        # Filter by preferences
        suitable_indoor = await self.preference_matcher.filter_by_preferences(
            indoor_activities, preferences
        )

        # Create recommendations with neutral weather (since they're indoor)
        neutral_weather = WeatherConditions(
            temperature=20.0,
            humidity=50.0,
            wind_speed=0.0,
            precipitation=0.0,
            visibility=10000.0,
        )

        recommendations = await self.rank_activities(
            suitable_indoor, neutral_weather, preferences
        )

        return recommendations[:5]  # Return top 5 indoor alternatives

    async def generate_preparation_tips(
        self, activity: Activity, weather: WeatherConditions
    ) -> List[str]:
        """Generate preparation tips for an activity."""
        tips = []

        # General equipment tips
        if activity.equipment_needed:
            tips.append(f"Bring: {', '.join(activity.equipment_needed)}")

        # Weather-specific tips
        if not activity.indoor:
            if weather.temperature < 10:
                tips.append("Dress in warm layers")
            elif weather.temperature > 25:
                tips.append("Wear light, breathable clothing")

            if weather.precipitation > 0.1:
                tips.append("Bring waterproof gear")

            if weather.uv_index and weather.uv_index > 5:
                tips.append("Apply sunscreen and wear a hat")

            if weather.wind_speed > 10:
                tips.append("Secure loose items and dress for wind")

        # Activity-specific tips
        if activity.category == ActivityCategory.OUTDOOR_SPORTS:
            tips.append("Check local trail conditions")
            tips.append("Inform someone of your plans")

        if activity.safety_considerations:
            tips.extend(activity.safety_considerations)

        return tips

    async def _get_available_activities(self) -> List[Activity]:
        """Get available activities (mock implementation)."""
        # This would typically come from the database
        # For now, return a subset of activities for demonstration
        db = InMemoryActivityDatabase()
        return await db.get_all_activities()


class ActivityService(IActivityService):
    """High-level activity recommendation service."""

    def __init__(
        self, database: IActivityDatabase, recommendation_engine: IRecommendationEngine
    ):
        self.database = database
        self.recommendation_engine = recommendation_engine
        self._user_feedback: List[Dict[str, Any]] = []

    async def get_recommendations(self, request: ActivityRequest) -> ActivityResponse:
        """Get activity recommendations based on weather and preferences."""
        try:
            # Generate main recommendations
            recommendations = await self.recommendation_engine.generate_recommendations(
                request
            )

            # Generate indoor alternatives if requested
            indoor_alternatives = None
            if request.include_indoor_backup:
                outdoor_activities = [
                    r.activity for r in recommendations if not r.activity.indoor
                ]
                if outdoor_activities:
                    indoor_alternatives = (
                        await self.recommendation_engine.get_indoor_alternatives(
                            outdoor_activities, request.preferences
                        )
                    )

            # Generate weather summary
            weather_summary = self._generate_weather_summary(request.weather_conditions)

            # Generate general advice
            general_advice = self._generate_general_advice(
                request.weather_conditions, recommendations
            )

            return ActivityResponse(
                request=request,
                recommendations=recommendations,
                indoor_alternatives=indoor_alternatives,
                weather_summary=weather_summary,
                general_advice=general_advice,
                generated_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            raise

    async def get_quick_recommendations(
        self,
        weather: WeatherConditions,
        category: Optional[ActivityCategory] = None,
        indoor_only: bool = False,
    ) -> List[ActivityRecommendation]:
        """Get quick activity recommendations."""
        # Create basic preferences
        preferences = ActivityPreferences(
            preferred_categories=[category] if category else [],
            indoor_preference=True if indoor_only else None,
        )

        # Create request
        request = ActivityRequest(
            weather_conditions=weather, preferences=preferences, max_recommendations=5
        )

        response = await self.get_recommendations(request)
        return response.recommendations

    async def search_activities(
        self, query: str, filter_criteria: Optional[ActivityFilter] = None
    ) -> List[Activity]:
        """Search activities by text query and filters."""
        # Get all activities
        all_activities = await self.database.get_all_activities()

        # Apply filters if provided
        if filter_criteria:
            all_activities = await self.database.search_activities(filter_criteria)

        # Text search
        query_lower = query.lower()
        matching_activities = []

        for activity in all_activities:
            # Search in name and description
            if (
                query_lower in activity.name.lower()
                or query_lower in activity.description.lower()
            ):
                matching_activities.append(activity)

        return matching_activities

    async def get_activity_details(self, activity_id: str) -> Optional[Activity]:
        """Get detailed information about a specific activity."""
        return await self.database.get_activity_by_id(activity_id)

    async def get_weather_advice(
        self, weather: WeatherConditions, activity_id: str
    ) -> Dict[str, Any]:
        """Get weather-specific advice for an activity."""
        activity = await self.database.get_activity_by_id(activity_id)
        if not activity:
            return {"error": "Activity not found"}

        # Create weather matcher and get advice
        weather_matcher = WeatherMatcher()
        weather_req = await weather_matcher.get_weather_requirements(activity)
        suitability = await weather_matcher.calculate_weather_suitability(
            activity, weather, weather_req
        )
        warnings = await weather_matcher.generate_weather_warnings(activity, weather)

        # Generate preparation tips
        prep_tips = await self.recommendation_engine.generate_preparation_tips(
            activity, weather
        )

        return {
            "activity": activity,
            "weather_suitability": suitability.value,
            "warnings": warnings,
            "preparation_tips": prep_tips,
            "weather_conditions": asdict(weather),
        }

    async def get_seasonal_activities(
        self, season: str, preferences: Optional[ActivityPreferences] = None
    ) -> List[Activity]:
        """Get activities suitable for a specific season."""
        all_activities = await self.database.get_all_activities()

        # Filter by season if specified in activity
        seasonal_activities = [
            activity
            for activity in all_activities
            if not activity.seasonal_availability
            or season.lower() in activity.seasonal_availability
        ]

        # Apply preferences if provided
        if preferences:
            preference_matcher = PreferenceMatcher()
            seasonal_activities = await preference_matcher.filter_by_preferences(
                seasonal_activities, preferences
            )

        return seasonal_activities

    async def save_user_feedback(
        self,
        activity_id: str,
        weather_conditions: WeatherConditions,
        rating: float,
        feedback: Optional[str] = None,
    ) -> bool:
        """Save user feedback for improving recommendations."""
        try:
            feedback_entry = {
                "activity_id": activity_id,
                "weather_conditions": asdict(weather_conditions),
                "rating": rating,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat(),
            }

            self._user_feedback.append(feedback_entry)
            logger.info(f"Saved feedback for activity {activity_id}: rating {rating}")
            return True

        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return False

    async def get_trending_activities(
        self, weather: WeatherConditions, limit: int = 5
    ) -> List[Activity]:
        """Get trending activities for current weather."""
        # Simple implementation based on weather conditions
        all_activities = await self.database.get_all_activities()

        # Score activities based on weather suitability
        weather_matcher = WeatherMatcher()
        scored_activities = []

        for activity in all_activities:
            weather_req = await weather_matcher.get_weather_requirements(activity)
            score = await weather_matcher.get_weather_score(
                activity, weather, weather_req
            )
            scored_activities.append((activity, score))

        # Sort by score and return top activities
        scored_activities.sort(key=lambda x: x[1], reverse=True)
        return [activity for activity, score in scored_activities[:limit]]

    def _generate_weather_summary(self, weather: WeatherConditions) -> str:
        """Generate a summary of current weather conditions."""
        summary_parts = []

        # Temperature
        if weather.temperature < 0:
            summary_parts.append("freezing conditions")
        elif weather.temperature < 10:
            summary_parts.append("cold weather")
        elif weather.temperature < 20:
            summary_parts.append("cool conditions")
        elif weather.temperature < 25:
            summary_parts.append("pleasant weather")
        elif weather.temperature < 30:
            summary_parts.append("warm conditions")
        else:
            summary_parts.append("hot weather")

        # Precipitation
        if weather.precipitation > 5:
            summary_parts.append("heavy rain")
        elif weather.precipitation > 1:
            summary_parts.append("light rain")
        elif weather.precipitation > 0:
            summary_parts.append("possible drizzle")

        # Wind
        if weather.wind_speed > 20:
            summary_parts.append("strong winds")
        elif weather.wind_speed > 10:
            summary_parts.append("moderate winds")

        return f"Current conditions: {', '.join(summary_parts)}"

    def _generate_general_advice(
        self, weather: WeatherConditions, recommendations: List[ActivityRecommendation]
    ) -> List[str]:
        """Generate general advice based on weather and recommendations."""
        advice = []

        # Weather-based advice
        if weather.precipitation > 1:
            advice.append("Consider indoor activities due to rain")

        if weather.temperature > 30:
            advice.append("Stay hydrated and avoid prolonged sun exposure")

        if weather.temperature < 5:
            advice.append("Dress warmly for outdoor activities")

        # Recommendation-based advice
        if recommendations:
            top_recommendation = recommendations[0]
            if top_recommendation.confidence_score > 0.8:
                advice.append(f"Highly recommended: {top_recommendation.activity.name}")

        return advice


def create_activity_service() -> ActivityService:
    """Factory function to create a complete activity service."""
    database = InMemoryActivityDatabase()
    weather_matcher = WeatherMatcher()
    preference_matcher = PreferenceMatcher()
    recommendation_engine = RecommendationEngine(weather_matcher, preference_matcher)

    return ActivityService(database, recommendation_engine)
