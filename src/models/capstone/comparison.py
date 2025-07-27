"""Weather comparison models and strategies."""

import json
import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from uuid import UUID
from uuid import uuid4

from ..weather_models import CurrentWeather
from .base import AIEnhancedModel
from .base import ModelProtocol


class ComparisonStrategy(ABC):
    """Abstract base class for weather comparison strategies."""

    @abstractmethod
    def compare(
        self, weather1: CurrentWeather, weather2: CurrentWeather
    ) -> Dict[str, Any]:
        """Compare two weather conditions using specific strategy."""
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this comparison strategy."""
        pass

    def get_recommendations(self, comparison_result: Dict[str, Any]) -> List[str]:
        """Get recommendations based on comparison results."""
        return []


class DefaultComparisonStrategy(ComparisonStrategy):
    """Default comparison strategy focusing on general comfort metrics."""

    def compare(
        self, weather1: CurrentWeather, weather2: CurrentWeather
    ) -> Dict[str, Any]:
        """Compare weather using general comfort metrics."""
        temp1 = weather1.temperature.to_celsius()
        temp2 = weather2.temperature.to_celsius()

        result = {
            "temperature_difference": abs(temp1 - temp2),
            "humidity_difference": abs(weather1.humidity - weather2.humidity),
            "pressure_difference": abs(
                weather1.pressure.value - weather2.pressure.value
            ),
            "wind_difference": abs(weather1.wind.speed - weather2.wind.speed),
            "condition_similarity": weather1.condition == weather2.condition,
            "comfort_winner": self._determine_comfort_winner(weather1, weather2),
            "detailed_analysis": self._generate_detailed_analysis(weather1, weather2),
        }

        return result

    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "General Comfort Comparison"

    def _determine_comfort_winner(
        self, weather1: CurrentWeather, weather2: CurrentWeather
    ) -> str:
        """Determine which location has more comfortable weather."""
        score1 = self._calculate_comfort_score(weather1)
        score2 = self._calculate_comfort_score(weather2)

        if score1 > score2:
            return weather1.location.display_name
        elif score2 > score1:
            return weather2.location.display_name
        else:
            return "Tie"

    def _calculate_comfort_score(self, weather: CurrentWeather) -> float:
        """Calculate comfort score for weather conditions."""
        temp_celsius = weather.temperature.to_celsius()

        # Ideal temperature range: 18-24°C
        temp_score = max(0, 100 - abs(temp_celsius - 21) * 5)

        # Ideal humidity range: 40-60%
        humidity_score = max(0, 100 - abs(weather.humidity - 50) * 2)

        # Lower wind is generally more comfortable
        wind_score = max(0, 100 - weather.wind.speed * 3)

        # Weather condition bonuses/penalties
        condition_score = {
            "clear": 100,
            "clouds": 80,
            "rain": 40,
            "snow": 60,
            "thunderstorm": 20,
            "drizzle": 50,
            "mist": 70,
        }.get(weather.condition.value.lower(), 60)

        return (temp_score + humidity_score + wind_score + condition_score) / 4

    def _generate_detailed_analysis(
        self, weather1: CurrentWeather, weather2: CurrentWeather
    ) -> Dict[str, str]:
        """Generate detailed analysis of the comparison."""
        temp1 = weather1.temperature.to_celsius()
        temp2 = weather2.temperature.to_celsius()

        analysis = {}

        # Temperature analysis
        if abs(temp1 - temp2) > 10:
            warmer = (
                weather1.location.display_name
                if temp1 > temp2
                else weather2.location.display_name
            )
            analysis["temperature"] = f"{warmer} is significantly warmer"
        else:
            analysis["temperature"] = "Temperatures are similar"

        # Humidity analysis
        if abs(weather1.humidity - weather2.humidity) > 20:
            more_humid = (
                weather1.location.display_name
                if weather1.humidity > weather2.humidity
                else weather2.location.display_name
            )
            analysis["humidity"] = f"{more_humid} is more humid"
        else:
            analysis["humidity"] = "Humidity levels are comparable"

        # Condition analysis
        if weather1.condition == weather2.condition:
            analysis["conditions"] = "Both locations have similar weather conditions"
        else:
            analysis["conditions"] = (
                f"{weather1.location.display_name} has {weather1.condition.value}, {weather2.location.display_name} has {weather2.condition.value}"
            )

        return analysis


class OutdoorActivityStrategy(ComparisonStrategy):
    """Comparison strategy focused on outdoor activity suitability."""

    def compare(
        self, weather1: CurrentWeather, weather2: CurrentWeather
    ) -> Dict[str, Any]:
        """Compare weather for outdoor activity suitability."""
        score1 = self._calculate_outdoor_score(weather1)
        score2 = self._calculate_outdoor_score(weather2)

        result = {
            "outdoor_score_1": score1,
            "outdoor_score_2": score2,
            "better_for_outdoor": (
                weather1.location.display_name
                if score1 > score2
                else weather2.location.display_name
            ),
            "activity_recommendations": self._get_activity_recommendations(
                weather1, weather2
            ),
            "weather_warnings": self._get_weather_warnings(weather1, weather2),
        }

        return result

    def get_strategy_name(self) -> str:
        """Get strategy name."""
        return "Outdoor Activity Focused"

    def _calculate_outdoor_score(self, weather: CurrentWeather) -> float:
        """Calculate outdoor activity suitability score."""
        temp_celsius = weather.temperature.to_celsius()

        # Temperature scoring (optimal: 15-25°C)
        if 15 <= temp_celsius <= 25:
            temp_score = 100
        elif 10 <= temp_celsius < 15 or 25 < temp_celsius <= 30:
            temp_score = 80
        elif 5 <= temp_celsius < 10 or 30 < temp_celsius <= 35:
            temp_score = 60
        else:
            temp_score = 20

        # Weather condition scoring for outdoor activities
        condition_scores = {
            "clear": 100,
            "clouds": 85,
            "mist": 70,
            "drizzle": 30,
            "rain": 10,
            "snow": 40,
            "thunderstorm": 0,
        }
        condition_score = condition_scores.get(weather.condition.value.lower(), 50)

        # Wind scoring (moderate wind is good, too much is bad)
        if weather.wind.speed <= 10:
            wind_score = 100
        elif weather.wind.speed <= 20:
            wind_score = 80
        elif weather.wind.speed <= 30:
            wind_score = 50
        else:
            wind_score = 20

        return (temp_score + condition_score + wind_score) / 3

    def _get_activity_recommendations(
        self, weather1: CurrentWeather, weather2: CurrentWeather
    ) -> Dict[str, List[str]]:
        """Get activity recommendations for each location."""
        recommendations = {}

        for weather in [weather1, weather2]:
            location = weather.location.display_name
            temp = weather.temperature.to_celsius()
            condition = weather.condition.value.lower()

            activities = []

            if condition == "clear" and 15 <= temp <= 25:
                activities.extend(["hiking", "cycling", "picnic", "outdoor sports"])
            elif condition == "clear" and temp > 25:
                activities.extend(
                    ["swimming", "water sports", "early morning exercise"]
                )
            elif condition == "clouds":
                activities.extend(["walking", "photography", "sightseeing"])
            elif condition in ["rain", "drizzle"]:
                activities.extend(["indoor activities", "museums", "cafes"])
            elif condition == "snow":
                activities.extend(
                    ["winter sports", "snow activities", "cozy indoor time"]
                )

            recommendations[location] = activities

        return recommendations

    def _get_weather_warnings(
        self, weather1: CurrentWeather, weather2: CurrentWeather
    ) -> Dict[str, List[str]]:
        """Get weather warnings for each location."""
        warnings = {}

        for weather in [weather1, weather2]:
            location = weather.location.display_name
            temp = weather.temperature.to_celsius()
            condition = weather.condition.value.lower()
            wind_speed = weather.wind.speed

            location_warnings = []

            if temp < 0:
                location_warnings.append("Freezing temperatures - dress warmly")
            elif temp > 35:
                location_warnings.append("Very hot - stay hydrated and seek shade")

            if wind_speed > 25:
                location_warnings.append("Strong winds - be cautious outdoors")

            if condition == "thunderstorm":
                location_warnings.append("Thunderstorm - avoid outdoor activities")
            elif condition == "rain":
                location_warnings.append("Rainy conditions - bring umbrella")

            warnings[location] = location_warnings

        return warnings


@dataclass
class WeatherComparison(AIEnhancedModel, ModelProtocol):
    """Enhanced weather comparison with flexible strategies."""

    city1_weather: CurrentWeather
    city2_weather: CurrentWeather
    strategy: ComparisonStrategy = field(default_factory=DefaultComparisonStrategy)
    comparison_id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=datetime.now)
    comparison_results: Optional[Dict[str, Any]] = field(default=None, init=False)
    ai_analysis: Optional[str] = field(default=None, init=False)

    def __post_init__(self):
        """Initialize the comparison after creation."""
        super().__init__()
        if self.comparison_results is None:
            self.comparison_results = self.strategy.compare(
                self.city1_weather, self.city2_weather
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "comparison_id": str(self.comparison_id),
            "timestamp": self.timestamp.isoformat(),
            "city1_weather": asdict(self.city1_weather),
            "city2_weather": asdict(self.city2_weather),
            "strategy_name": self.strategy.get_strategy_name(),
            "comparison_results": self.comparison_results,
            "ai_analysis": self.ai_analysis,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeatherComparison":
        """Create from dictionary."""
        # This would need proper implementation based on your needs
        raise NotImplementedError("from_dict method needs implementation")

    def validate(self) -> bool:
        """Validate the comparison data."""
        return (
            self.city1_weather is not None
            and self.city2_weather is not None
            and self.strategy is not None
            and self.comparison_results is not None
        )

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

    def get_summary(self) -> str:
        """Get a human-readable summary of the comparison."""
        if not self.comparison_results:
            return "No comparison results available"

        city1_name = self.city1_weather.location.display_name
        city2_name = self.city2_weather.location.display_name

        summary_parts = [
            f"Weather Comparison: {city1_name} vs {city2_name}",
            f"Strategy: {self.strategy.get_strategy_name()}",
            f"Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        # Add specific results based on strategy type
        if isinstance(self.strategy, DefaultComparisonStrategy):
            winner = self.comparison_results.get("comfort_winner", "Unknown")
            summary_parts.append(f"More comfortable: {winner}")
        elif isinstance(self.strategy, OutdoorActivityStrategy):
            better = self.comparison_results.get("better_for_outdoor", "Unknown")
            summary_parts.append(f"Better for outdoor activities: {better}")

        return "\n".join(summary_parts)

    def switch_strategy(self, new_strategy: ComparisonStrategy) -> None:
        """Switch to a different comparison strategy and recalculate."""
        self.strategy = new_strategy
        self.comparison_results = self.strategy.compare(
            self.city1_weather, self.city2_weather
        )
        self.ai_analysis = None  # Clear AI analysis as it may no longer be valid
