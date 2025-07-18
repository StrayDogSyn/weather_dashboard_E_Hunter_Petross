"""
Enhanced City Comparison Service with Team Data Support.

This service extends the original comparison service to utilize team data
for comparing cities instead of making API calls.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any

from ..models.capstone_models import WeatherComparison
from ..models.weather_models import CurrentWeather
from .weather_service import WeatherService
from ..services.team_data_service import TeamDataService


class TeamCityComparisonService:
    """Enhanced service for comparing weather between cities using team data."""

    def __init__(self, weather_service: WeatherService):
        """Initialize the comparison service."""
        self.weather_service = weather_service
        self.team_data_service = TeamDataService()
        self.logger = logging.getLogger(__name__)
        self.use_team_data = True  # Flag to enable/disable team data usage

    def compare_cities(self, city1: str, city2: str) -> Optional[WeatherComparison]:
        """
        Compare weather conditions between two cities using team data.

        Args:
            city1: Name of the first city
            city2: Name of the second city

        Returns:
            WeatherComparison object or None if comparison failed
        """
        try:
            self.logger.info(f"Comparing weather between {city1} and {city2} using team data")

            # Try to get weather data from team data first
            weather1 = None
            weather2 = None

            if self.use_team_data:
                weather1 = self.team_data_service.get_city_weather_from_team_data(city1)
                weather2 = self.team_data_service.get_city_weather_from_team_data(city2)

            # Fall back to API if team data is not available
            if not weather1:
                self.logger.info(f"Falling back to API for {city1}")
                weather1 = self.weather_service.get_current_weather(city1)

            if not weather2:
                self.logger.info(f"Falling back to API for {city2}")
                weather2 = self.weather_service.get_current_weather(city2)

            if not weather1 or not weather2:
                self.logger.error("Failed to get weather data for one or both cities")
                return None

            # Create comparison
            comparison = WeatherComparison(
                city1_weather=weather1, 
                city2_weather=weather2
            )

            self.logger.info(f"Successfully compared {city1} and {city2}")
            return comparison

        except Exception as e:
            self.logger.error(f"Error comparing cities {city1} and {city2}: {e}")
            return None

    def generate_team_comparison_summary(self, comparison: WeatherComparison) -> str:
        """
        Generate an enhanced comparison summary including team data insights.

        Args:
            comparison: WeatherComparison object

        Returns:
            Formatted comparison summary with team data insights
        """
        city1 = comparison.city1_weather.location.display_name
        city2 = comparison.city2_weather.location.display_name

        temp_diff = abs(comparison.temperature_difference)
        humidity_diff = abs(comparison.humidity_difference)

        summary = []
        summary.append(f"🌍 Team Weather Comparison: {city1} vs {city2}")
        summary.append("=" * 70)
        summary.append("")

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

        # Add team data insights
        summary.append("")
        summary.append("📊 Team Data Insights:")
        team_insights = self._get_team_insights(city1, city2)
        for insight in team_insights:
            summary.append(f"   • {insight}")

        summary.append("")
        summary.append("📈 Data Source: Team Weather Dataset")
        summary.append(f"⏰ Comparison Time: {comparison.comparison_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

        return "\n".join(summary)

    def _get_team_insights(self, city1: str, city2: str) -> list[str]:
        """
        Get additional insights from team data analysis.

        Args:
            city1: First city name
            city2: Second city name

        Returns:
            List of insight strings
        """
        insights = []
        
        try:
            cities_analysis = self.team_data_service.get_cities_analysis()
            team_summary = self.team_data_service.get_team_summary()

            # City-specific insights
            if city1 in cities_analysis:
                city1_data = cities_analysis[city1]
                insights.append(f"{city1} average temperature: {city1_data.get('avg_temperature', 'N/A')}°C")
                insights.append(f"{city1} dominant condition: {city1_data.get('dominant_condition', 'N/A').title()}")

            if city2 in cities_analysis:
                city2_data = cities_analysis[city2]
                insights.append(f"{city2} average temperature: {city2_data.get('avg_temperature', 'N/A')}°C")
                insights.append(f"{city2} dominant condition: {city2_data.get('dominant_condition', 'N/A').title()}")

            # Global team insights
            if team_summary:
                total_cities = team_summary.get('total_cities', 0)
                global_avg = team_summary.get('avg_temperature_global', 0)
                insights.append(f"Team dataset includes {total_cities} cities")
                insights.append(f"Global average temperature: {global_avg:.1f}°C")

        except Exception as e:
            self.logger.warning(f"Could not generate team insights: {e}")
            insights.append("Team analysis data not available")

        return insights

    def get_detailed_team_comparison(self, comparison: WeatherComparison) -> Dict[str, Any]:
        """
        Get detailed comparison data including team data context.

        Args:
            comparison: WeatherComparison object

        Returns:
            Dictionary with detailed comparison data and team insights
        """
        base_comparison = {
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
            "data_source": "team_data"
        }

        # Add team data insights
        try:
            cities_analysis = self.team_data_service.get_cities_analysis()
            team_summary = self.team_data_service.get_team_summary()

            base_comparison["team_insights"] = {
                "cities_analysis": cities_analysis,
                "team_summary": team_summary,
                "available_cities": self.team_data_service.get_available_cities()
            }
        except Exception as e:
            self.logger.warning(f"Could not include team insights: {e}")

        return base_comparison

    def get_available_team_cities(self) -> list[str]:
        """
        Get list of cities available in team data.

        Returns:
            List of city names from team dataset
        """
        return self.team_data_service.get_available_cities()

    def create_sample_data_if_needed(self) -> bool:
        """
        Create sample team data if no data exists.

        Returns:
            True if sample data was created or already exists
        """
        available_cities = self.team_data_service.get_available_cities()
        if not available_cities:
            self.logger.info("No team data found, creating sample data")
            return self.team_data_service.create_sample_team_data()
        return True

    def toggle_team_data_usage(self, use_team_data: bool) -> None:
        """
        Toggle between team data and API usage.

        Args:
            use_team_data: True to use team data, False to use API
        """
        self.use_team_data = use_team_data
        self.logger.info(f"Team data usage {'enabled' if use_team_data else 'disabled'}")

    def get_team_data_status(self) -> Dict[str, Any]:
        """
        Get status information about team data availability and GitHub source.

        Returns:
            Dictionary with team data status and source information
        """
        try:
            # Get GitHub repository information
            repo_info = self.team_data_service.get_github_repo_info()
            
            available_cities = self.team_data_service.get_available_cities()
            team_summary = self.team_data_service.get_team_summary()
            
            return {
                "team_data_enabled": self.use_team_data,
                "cities_available": len(available_cities),
                "city_list": available_cities,
                "data_loaded": bool(available_cities),
                "data_source": {
                    "type": "GitHub Repository",
                    "repository": repo_info["repository"],
                    "csv_url": repo_info["csv_url"],
                    "json_url": repo_info["json_url"]
                },
                "team_summary": team_summary,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting team data status: {e}")
            return {
                "team_data_enabled": self.use_team_data,
                "cities_available": 0,
                "city_list": [],
                "data_loaded": False,
                "data_source": {
                    "type": "GitHub Repository",
                    "repository": "StrayDogSyn/New_Team_Dashboard"
                },
                "error": str(e)
            }

    def refresh_team_data(self) -> bool:
        """
        Refresh team data from GitHub repository.

        Returns:
            True if data was refreshed successfully
        """
        try:
            self.logger.info("Refreshing team data from GitHub repository...")
            success = self.team_data_service.refresh_team_data()
            
            if success:
                self.logger.info("Team data refreshed successfully")
            else:
                self.logger.warning("Failed to refresh team data from GitHub")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error refreshing team data: {e}")
            return False
