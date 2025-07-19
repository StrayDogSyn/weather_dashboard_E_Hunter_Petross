"""
Enhanced City Comparison Service for Weather Dashboard.

This service provides comprehensive functionality to compare weather conditions 
between cities using both API data and team data sources with intelligent fallback.
"""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from ..models.capstone_models import WeatherComparison
from ..models.weather_models import CurrentWeather
from .weather_service import WeatherService
from ..services.team_data_service import TeamDataService


class EnhancedCityComparisonService:
    """Enhanced service for comparing weather between cities with multiple data sources."""

    def __init__(self, weather_service: WeatherService):
        """Initialize the enhanced comparison service."""
        self.weather_service = weather_service
        self.team_data_service = TeamDataService()
        self.logger = logging.getLogger(__name__)
        self.prefer_team_data = True  # Flag to prefer team data over API
        self._team_data_loaded = False

    def _ensure_team_data_loaded(self) -> bool:
        """Ensure team data is loaded, load if necessary."""
        if not self._team_data_loaded:
            self._team_data_loaded = self.team_data_service.load_team_data()
        return self._team_data_loaded

    def compare_cities(self, city1: str, city2: str) -> Optional[WeatherComparison]:
        """
        Compare weather conditions between two cities using the best available data source.

        Args:
            city1: Name of the first city
            city2: Name of the second city

        Returns:
            WeatherComparison object or None if comparison failed
        """
        try:
            self.logger.info(f"Comparing weather between {city1} and {city2}")

            # Get weather data for both cities using intelligent source selection
            weather1 = self._get_weather_data(city1)
            weather2 = self._get_weather_data(city2)

            if not weather1 or not weather2:
                self.logger.error("Failed to get weather data for one or both cities")
                return None

            # Create and return comparison
            comparison = WeatherComparison(
                city1_weather=weather1, 
                city2_weather=weather2
            )
            
            self.logger.info(f"Successfully created comparison between {city1} and {city2}")
            return comparison

        except Exception as e:
            self.logger.error(f"Error comparing cities {city1} and {city2}: {e}")
            return None

    def _get_weather_data(self, city: str) -> Optional[CurrentWeather]:
        """
        Get weather data for a city using the best available source.
        
        Args:
            city: Name of the city
            
        Returns:
            CurrentWeather object or None if failed
        """
        # Try team data first if preferred and available
        if self.prefer_team_data and self._ensure_team_data_loaded():
            weather_data = self.team_data_service.get_city_weather_from_team_data(city)
            if weather_data:
                self.logger.debug(f"Using team data for {city}")
                return weather_data

        # Fall back to API data
        try:
            weather_data = self.weather_service.get_current_weather(city)
            if weather_data:
                self.logger.debug(f"Using API data for {city}")
                return weather_data
        except Exception as e:
            self.logger.warning(f"API request failed for {city}: {e}")

        return None

    def compare_multiple_cities(self, cities: List[str]) -> Dict[str, Optional[CurrentWeather]]:
        """
        Compare weather conditions for multiple cities.

        Args:
            cities: List of city names

        Returns:
            Dictionary mapping city names to weather data
        """
        results = {}
        for city in cities:
            try:
                weather_data = self._get_weather_data(city)
                results[city] = weather_data
                if weather_data:
                    self.logger.debug(f"Successfully retrieved data for {city}")
                else:
                    self.logger.warning(f"Failed to retrieve data for {city}")
            except Exception as e:
                self.logger.error(f"Error getting data for {city}: {e}")
                results[city] = None

        return results

    def get_comparison_analysis(self, city1: str, city2: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed comparison analysis between two cities.

        Args:
            city1: Name of the first city
            city2: Name of the second city

        Returns:
            Analysis dictionary or None if comparison failed
        """
        comparison = self.compare_cities(city1, city2)
        if not comparison:
            return None

        try:
            analysis = {
                "temperature_difference": comparison.temperature_difference,
                "warmer_city": comparison.warmer_city,
                "humidity_difference": comparison.humidity_difference,
                "better_weather_city": comparison.better_weather_city,
                "city1_name": comparison.city1_weather.location.display_name,
                "city2_name": comparison.city2_weather.location.display_name,
                "city1_temperature": comparison.city1_weather.temperature.to_celsius(),
                "city2_temperature": comparison.city2_weather.temperature.to_celsius(),
                "timestamp": datetime.now().isoformat(),
                "data_sources": {
                    city1: "team_data" if self._is_from_team_data(city1) else "api",
                    city2: "team_data" if self._is_from_team_data(city2) else "api"
                }
            }
            return analysis
        except Exception as e:
            self.logger.error(f"Error creating comparison analysis: {e}")
            return None

    def _is_from_team_data(self, city: str) -> bool:
        """Check if city data comes from team data source."""
        if not self._ensure_team_data_loaded():
            return False
        return self.team_data_service.get_city_weather_from_team_data(city) is not None

    def export_comparison(self, city1: str, city2: str, format: str = "json") -> Optional[str]:
        """
        Export comparison data in specified format.

        Args:
            city1: Name of the first city
            city2: Name of the second city
            format: Export format ("json" or "csv")

        Returns:
            File path of exported data or None if failed
        """
        try:
            analysis = self.get_comparison_analysis(city1, city2)
            if not analysis:
                return None

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format.lower() == "json":
                import json
                import os
                
                exports_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'exports')
                os.makedirs(exports_dir, exist_ok=True)
                
                filename = f"comparison_{city1}_{city2}_{timestamp}.json"
                filepath = os.path.join(exports_dir, filename)
                
                with open(filepath, 'w') as f:
                    json.dump(analysis, f, indent=2)
                
                self.logger.info(f"Exported comparison to {filepath}")
                return filepath
            
            # Add CSV export if needed
            elif format.lower() == "csv":
                # Implementation for CSV export can be added here
                pass
                
        except Exception as e:
            self.logger.error(f"Error exporting comparison: {e}")
            return None

    def set_data_source_preference(self, prefer_team_data: bool):
        """
        Set preference for data source.

        Args:
            prefer_team_data: True to prefer team data, False to prefer API
        """
        self.prefer_team_data = prefer_team_data
        self.logger.info(f"Data source preference set to: {'team_data' if prefer_team_data else 'api'}")

    def get_available_cities(self) -> Dict[str, List[str]]:
        """
        Get list of available cities from both data sources.

        Returns:
            Dictionary with 'team_data' and 'api' keys containing city lists
        """
        result = {
            "team_data": [],
            "api": []  # API can handle any city, so this would be extensive
        }

        # Get cities from team data
        if self._ensure_team_data_loaded():
            result["team_data"] = self.team_data_service.get_available_cities()

        # For API, we could maintain a list of popular cities or let users try any city
        result["api"] = [
            "New York", "London", "Paris", "Tokyo", "Sydney", "Toronto", 
            "Berlin", "Mumbai", "Beijing", "Los Angeles", "Chicago", "Miami"
        ]

        return result
