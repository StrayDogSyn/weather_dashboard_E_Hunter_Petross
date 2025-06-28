"""
City Comparison Service for Weather Dashboard.

This service provides functionality to compare weather conditions between two cities.
"""

import logging
from datetime import datetime
from typing import Optional, Tuple

from ..models.capstone_models import WeatherComparison
from ..models.weather_models import CurrentWeather
from .weather_service import WeatherService


class CityComparisonService:
    """Service for comparing weather between two cities."""

    def __init__(self, weather_service: WeatherService):
        """Initialize the comparison service."""
        self.weather_service = weather_service
        self.logger = logging.getLogger(__name__)

    def compare_cities(self, city1: str, city2: str) -> Optional[WeatherComparison]:
        """
        Compare weather conditions between two cities.

        Args:
            city1: Name of the first city
            city2: Name of the second city

        Returns:
            WeatherComparison object or None if comparison failed
        """
        try:
            self.logger.info(f"Comparing weather between {city1} and {city2}")

            # Get weather for both cities
            weather1 = self.weather_service.get_current_weather(city1)
            weather2 = self.weather_service.get_current_weather(city2)

            if not weather1 or not weather2:
                self.logger.error("Failed to get weather data for one or both cities")
                return None

            # Create comparison
            comparison = WeatherComparison(
                city1_weather=weather1, city2_weather=weather2
            )

            self.logger.info(f"Successfully compared {city1} and {city2}")
            return comparison

        except Exception as e:
            self.logger.error(f"Error comparing cities {city1} and {city2}: {e}")
            return None

    def generate_comparison_summary(self, comparison: WeatherComparison) -> str:
        """
        Generate a text summary of the weather comparison.

        Args:
            comparison: WeatherComparison object

        Returns:
            Formatted comparison summary
        """
        city1 = comparison.city1_weather.location.display_name
        city2 = comparison.city2_weather.location.display_name

        temp_diff = abs(comparison.temperature_difference)
        humidity_diff = abs(comparison.humidity_difference)

        summary = []
        summary.append(f"🌍 Weather Comparison: {city1} vs {city2}")
        summary.append("=" * 60)

        # Temperature comparison
        if comparison.temperature_difference > 0:
            summary.append(f"🌡️  {city1} is {temp_diff:.1f}°C warmer than {city2}")
        elif comparison.temperature_difference < 0:
            summary.append(f"🌡️  {city2} is {temp_diff:.1f}°C warmer than {city1}")
        else:
            summary.append(f"🌡️  Both cities have the same temperature")

        # Humidity comparison
        if comparison.humidity_difference > 0:
            summary.append(f"💧 {city1} is {humidity_diff}% more humid than {city2}")
        elif comparison.humidity_difference < 0:
            summary.append(f"💧 {city2} is {humidity_diff}% more humid than {city1}")
        else:
            summary.append(f"💧 Both cities have the same humidity")

        # Weather conditions
        summary.append(f"☁️  {city1}: {comparison.city1_weather.description.title()}")
        summary.append(f"☁️  {city2}: {comparison.city2_weather.description.title()}")

        # Overall better weather
        summary.append(f"🏆 Better weather: {comparison.better_weather_city}")

        return "\n".join(summary)

    def get_detailed_comparison(self, comparison: WeatherComparison) -> dict:
        """
        Get detailed comparison data as a dictionary.

        Args:
            comparison: WeatherComparison object

        Returns:
            Dictionary with detailed comparison data
        """
        return {
            "city1": {
                "name": comparison.city1_weather.location.display_name,
                "temperature": comparison.city1_weather.temperature.to_celsius(),
                "temperature_f": comparison.city1_weather.temperature.to_fahrenheit(),
                "feels_like": comparison.city1_weather.temperature.feels_like,
                "humidity": comparison.city1_weather.humidity,
                "condition": comparison.city1_weather.condition.value,
                "description": comparison.city1_weather.description,
                "wind_speed": comparison.city1_weather.wind.speed,
                "wind_direction": comparison.city1_weather.wind.direction_name,
                "pressure": comparison.city1_weather.pressure.value,
            },
            "city2": {
                "name": comparison.city2_weather.location.display_name,
                "temperature": comparison.city2_weather.temperature.to_celsius(),
                "temperature_f": comparison.city2_weather.temperature.to_fahrenheit(),
                "feels_like": comparison.city2_weather.temperature.feels_like,
                "humidity": comparison.city2_weather.humidity,
                "condition": comparison.city2_weather.condition.value,
                "description": comparison.city2_weather.description,
                "wind_speed": comparison.city2_weather.wind.speed,
                "wind_direction": comparison.city2_weather.wind.direction_name,
                "pressure": comparison.city2_weather.pressure.value,
            },
            "differences": {
                "temperature": comparison.temperature_difference,
                "humidity": comparison.humidity_difference,
                "warmer_city": comparison.warmer_city,
                "better_weather": comparison.better_weather_city,
            },
            "timestamp": comparison.comparison_timestamp.isoformat(),
        }
