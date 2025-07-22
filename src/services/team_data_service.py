"""
Team Data Service for Weather Dashboard.

This service provides functionality to load and utilize team weather data
from the GitHub repository for the Compare Cities feature instead of making API calls.
"""

import json
import logging
import os
import urllib.error
import urllib.request
from datetime import datetime
from glob import glob
from typing import Any, Dict, List, Optional

import pandas as pd

from ..models.weather_models import (
    AtmosphericPressure,
    CurrentWeather,
    Location,
    Temperature,
    TemperatureUnit,
    WeatherCondition,
    Wind,
)


class TeamDataService:
    """Service for loading and processing team weather data from GitHub repository."""

    @staticmethod
    def _safe_float(val: Any) -> float:
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    def __init__(self):
        """Initialize the team data service."""
        self.logger = logging.getLogger(__name__)
        self.exports_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "exports"
        )
        self.team_data_cache: Optional[pd.DataFrame] = None
        self.cities_analysis_cache: Optional[Dict[str, Any]] = None
        self.team_summary_cache: Optional[Dict[str, Any]] = None

        # GitHub repository URLs for team data
        self.github_repo_base = "https://raw.githubusercontent.com/StrayDogSyn/New_Team_Dashboard/main/exports"
        self.csv_filename = "team_weather_data_20250717_204218.csv"
        self.json_filename = "team_compare_cities_data_20250717_204218.json"

    def load_team_data(self) -> bool:
        """
        Load team weather data from GitHub repository exports.

        Returns:
            True if data was loaded successfully, False otherwise
        """
        try:
            # Create exports directory if it doesn't exist
            os.makedirs(self.exports_dir, exist_ok=True)

            # Download and load CSV data from GitHub
            csv_url = f"{self.github_repo_base}/{self.csv_filename}"
            csv_local_path = os.path.join(self.exports_dir, self.csv_filename)

            self.logger.info(f"Downloading team data from: {csv_url}")

            try:
                urllib.request.urlretrieve(csv_url, csv_local_path)
                self.logger.info(f"Successfully downloaded CSV to: {csv_local_path}")

                # Load the CSV data
                self.team_data_cache = pd.read_csv(csv_local_path)

                # Convert timestamp column to datetime with flexible parsing
                if "timestamp" not in self.team_data_cache.columns:
                    try:
                        # Try multiple timestamp formats
                        self.team_data_cache["timestamp"] = pd.to_datetime(
                            self.team_data_cache["timestamp"],
                            format="mixed",
                            errors="coerce",
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not parse timestamps: {e}")
                        # Create a default timestamp for all entries
                        self.team_data_cache["timestamp"] = pd.to_datetime(
                            datetime.now()
                        )

            except urllib.error.URLError as e:
                self.logger.error(f"Failed to download CSV from GitHub: {e}")
                # Try to load local file if download fails
                local_csv_files = glob(
                    os.path.join(self.exports_dir, "team_weather_data_*.csv")
                )
                if local_csv_files:
                    latest_csv = max(local_csv_files, key=os.path.getctime)
                    self.logger.info(f"Using local CSV file: {latest_csv}")
                    self.team_data_cache = pd.read_csv(latest_csv)
                else:
                    self.logger.warning("No local CSV files found either")
                    return False

            # Download and load JSON analysis data from GitHub
            json_url = f"{self.github_repo_base}/{self.json_filename}"
            json_local_path = os.path.join(self.exports_dir, self.json_filename)

            try:
                urllib.request.urlretrieve(json_url, json_local_path)
                self.logger.info(f"Successfully downloaded JSON to: {json_local_path}")

                with open(json_local_path, "r") as f:
                    analysis_data = json.load(f)
                    self.cities_analysis_cache = analysis_data.get(
                        "cities_analysis", {}
                    )
                    self.team_summary_cache = analysis_data.get("team_summary", {})

            except urllib.error.URLError as e:
                self.logger.error(f"Failed to download JSON from GitHub: {e}")
                # Try to load local JSON file if download fails
                local_json_files = glob(
                    os.path.join(self.exports_dir, "team_compare_cities_data_*.json")
                )
                if local_json_files:
                    latest_json = max(local_json_files, key=os.path.getctime)
                    self.logger.info(f"Using local JSON file: {latest_json}")

                    with open(latest_json, "r") as f:
                        analysis_data = json.load(f)
                        self.cities_analysis_cache = analysis_data.get(
                            "cities_analysis", {}
                        )
                        self.team_summary_cache = analysis_data.get("team_summary", {})
                else:
                    self.logger.warning(
                        "No local JSON files found, continuing without analysis data"
                    )

            return True

        except Exception as e:
            self.logger.error(f"Error loading team data: {e}")
            return False

    def get_city_weather_from_team_data(
        self, city_name: str
    ) -> Optional[CurrentWeather]:
        """
        Get weather data for a city from team data instead of API.

        Args:
            city_name: Name of the city to get weather for

        Returns:
            CurrentWeather object or None if city not found
        """
        if self.team_data_cache is None:
            if not self.load_team_data():
                return None

        try:
            # Ensure team_data_cache is not None
            if self.team_data_cache is None:
                return None

            # Search for city in team data (case-insensitive)
            city_data = self.team_data_cache[
                self.team_data_cache["city"].str.lower() == city_name.lower()
            ]

            if city_data.empty:
                self.logger.warning(f"City '{city_name}' not found in team data")
                return None

            # Get the most recent data for the city
            if "timestamp" in city_data.columns:
                latest_data = city_data.sort_values("timestamp").iloc[-1]
            else:
                latest_data = city_data.iloc[-1]

            # Helper to safely convert values, handling NaN and conversion errors
            def safe_float(val, default=0.0):
                try:
                    if pd.isna(val):
                        return default
                    return float(val)
                except Exception:
                    return default

            def safe_int(val, default=0):
                try:
                    if pd.isna(val):
                        return default
                    return int(float(val))
                except Exception:
                    return default

            latitude = latest_data.get("latitude", 0.0)
            longitude = latest_data.get("longitude", 0.0)
            country = latest_data.get("country", "Unknown")

            location = Location(
                name=latest_data["city"],
                country=country,
                latitude=safe_float(latitude, 0.0),
                longitude=safe_float(longitude, 0.0),
            )

            temp_value = safe_float(latest_data.get("temperature", 0.0), 0.0)
            temperature = Temperature(
                value=temp_value,
                unit=TemperatureUnit.CELSIUS,
                feels_like=temp_value + 1.0,
            )

            pressure = AtmosphericPressure(
                value=safe_float(latest_data.get("pressure", 1013.25), 1013.25)
            )

            wind = Wind(
                speed=safe_float(latest_data.get("wind_speed", 0.0), 0.0),
                direction=safe_int(latest_data.get("wind_direction", 0.0), 0),
            )

            condition_str = str(latest_data.get("condition", "clear")).lower()
            condition = self._map_condition_string(condition_str)

            humidity = safe_int(latest_data.get("humidity", 50), 50)

            weather = CurrentWeather(
                location=location,
                temperature=temperature,
                condition=condition,
                description=latest_data.get("description", condition_str.title()),
                humidity=humidity,
                pressure=pressure,
                wind=wind,
                timestamp=datetime.now(),
            )

            self.logger.info(
                f"Successfully created weather data for {city_name} from team data"
            )
            return weather

        except Exception as e:
            self.logger.error(f"Error creating weather data for {city_name}: {e}")
            return None

    def _map_condition_string(self, condition_str: str) -> WeatherCondition:
        """
        Map condition string to WeatherCondition enum.

        Args:
            condition_str: Weather condition as string

        Returns:
            Corresponding WeatherCondition enum value
        """
        condition_mapping = {
            "clear": WeatherCondition.CLEAR,
            "sunny": WeatherCondition.CLEAR,
            "clouds": WeatherCondition.CLOUDS,
            "cloudy": WeatherCondition.CLOUDS,
            "partly cloudy": WeatherCondition.CLOUDS,
            "overcast": WeatherCondition.CLOUDS,
            "rain": WeatherCondition.RAIN,
            "rainy": WeatherCondition.RAIN,
            "drizzle": WeatherCondition.DRIZZLE,
            "snow": WeatherCondition.SNOW,
            "snowy": WeatherCondition.SNOW,
            "thunderstorm": WeatherCondition.THUNDERSTORM,
            "storm": WeatherCondition.THUNDERSTORM,
            "mist": WeatherCondition.MIST,
            "fog": WeatherCondition.MIST,
            "haze": WeatherCondition.MIST,
        }

        return condition_mapping.get(condition_str.lower(), WeatherCondition.CLEAR)

    def get_available_cities(self) -> List[str]:
        """
        Get list of cities available in team data.

        Returns:
            List of city names
        """
        if self.team_data_cache is None:
            if not self.load_team_data():
                return []

        try:
            if self.team_data_cache is None:
                return []
            return sorted(self.team_data_cache["city"].unique().tolist())
        except Exception as e:
            self.logger.error(f"Error getting available cities: {e}")
            return []

    def get_team_summary(self) -> Dict[str, Any]:
        """
        Get team weather data summary.

        Returns:
            Dictionary containing team summary data
        """
        if self.team_summary_cache is None:
            self.load_team_data()

        return self.team_summary_cache or {}

    def get_cities_analysis(self) -> Dict[str, Any]:
        """
        Get cities analysis data.

        Returns:
            Dictionary containing cities analysis data
        """
        if self.cities_analysis_cache is None:
            self.load_team_data()

        return self.cities_analysis_cache or {}

    def refresh_team_data(self) -> bool:
        """
        Force refresh team data from GitHub repository.

        Returns:
            True if data was refreshed successfully
        """
        # Clear caches
        self.team_data_cache = None
        self.cities_analysis_cache = None
        self.team_summary_cache = None

        # Reload data from GitHub
        return self.load_team_data()

    def get_github_repo_info(self) -> Dict[str, str]:
        """
        Get information about the GitHub repository data source.

        Returns:
            Dictionary with repository information
        """
        return {
            "repository": "StrayDogSyn/New_Team_Dashboard",
            "base_url": self.github_repo_base,
            "csv_file": self.csv_filename,
            "json_file": self.json_filename,
            "csv_url": f"{self.github_repo_base}/{self.csv_filename}",
            "json_url": f"{self.github_repo_base}/{self.json_filename}",
        }

    def create_sample_team_data(self) -> bool:
        """
        Create sample team data files for demonstration based on GitHub repository data.

        Returns:
            True if sample data was created successfully
        """
        try:
            # First try to load actual team data from GitHub
            if self.load_team_data():
                self.logger.info("Team data already loaded from GitHub repository")
                return True

            # If GitHub data is not available, create sample data based on repository cities
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Sample CSV data based on cities available in the GitHub repository
            sample_data = [
                {
                    "city": "Austin",
                    "country": "US",
                    "latitude": 30.2672,
                    "longitude": -97.7431,
                    "temperature": 35.5,
                    "humidity": 72,
                    "pressure": 1010.2,
                    "wind_speed": 8.5,
                    "wind_direction": 180.0,
                    "condition": "clear",
                    "description": "Clear sky",
                    "weather_main": "Clear",
                    "member_name": "Eric",
                    "timestamp": "2025-07-17T20:42:18",
                },
                {
                    "city": "Providence",
                    "country": "US",
                    "latitude": 41.8240,
                    "longitude": -71.4128,
                    "temperature": 25.2,
                    "humidity": 65,
                    "pressure": 1015.5,
                    "wind_speed": 12.0,
                    "wind_direction": 225.0,
                    "condition": "clouds",
                    "description": "Few clouds",
                    "weather_main": "Few",
                    "member_name": "Shomari",
                    "timestamp": "2025-07-17T20:42:18",
                },
                {
                    "city": "Rawlins",
                    "country": "US",
                    "latitude": 41.7911,
                    "longitude": -107.2387,
                    "temperature": 22.8,
                    "humidity": 45,
                    "pressure": 1018.1,
                    "wind_speed": 15.2,
                    "wind_direction": 270.0,
                    "condition": "clear",
                    "description": "Clear sky",
                    "weather_main": "Clear",
                    "member_name": "TeamMember1",
                    "timestamp": "2025-07-17T20:42:18",
                },
                {
                    "city": "Ontario",
                    "country": "US",
                    "latitude": 44.0267,
                    "longitude": -117.0194,
                    "temperature": 32.1,
                    "humidity": 35,
                    "pressure": 1012.7,
                    "wind_speed": 6.3,
                    "wind_direction": 90.0,
                    "condition": "clear",
                    "description": "Sunny",
                    "weather_main": "Clear",
                    "member_name": "TeamMember2",
                    "timestamp": "2025-07-17T20:42:18",
                },
                {
                    "city": "New York",
                    "country": "US",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "temperature": 23.5,
                    "humidity": 68,
                    "pressure": 1013.2,
                    "wind_speed": 9.0,
                    "wind_direction": 180.0,
                    "condition": "clouds",
                    "description": "Scattered clouds",
                    "weather_main": "Scattered",
                    "member_name": "TeamMember3",
                    "timestamp": "2025-07-17T20:42:18",
                },
                {
                    "city": "Miami",
                    "country": "US",
                    "latitude": 25.7617,
                    "longitude": -80.1918,
                    "temperature": 28.4,
                    "humidity": 78,
                    "pressure": 1008.5,
                    "wind_speed": 5.1,
                    "wind_direction": 120.0,
                    "condition": "rain",
                    "description": "Light rain",
                    "weather_main": "Light",
                    "member_name": "TeamMember4",
                    "timestamp": "2025-07-17T20:42:18",
                },
                {
                    "city": "New Jersey",
                    "country": "US",
                    "latitude": 40.0583,
                    "longitude": -74.4057,
                    "temperature": 22.3,
                    "humidity": 62,
                    "pressure": 1014.8,
                    "wind_speed": 7.8,
                    "wind_direction": 200.0,
                    "condition": "clouds",
                    "description": "Partly cloudy",
                    "weather_main": "Few",
                    "member_name": "TeamMember5",
                    "timestamp": "2025-07-17T20:42:18",
                },
            ]

            # Create CSV file
            df = pd.DataFrame(sample_data)
            csv_filename = f"team_weather_data_{timestamp}.csv"
            csv_path = os.path.join(self.exports_dir, csv_filename)

            # Ensure exports directory exists
            os.makedirs(self.exports_dir, exist_ok=True)

            df.to_csv(csv_path, index=False)
            self.logger.info(f"Created sample CSV: {csv_path}")

            # Sample JSON analysis data
            analysis_data = {
                "cities_analysis": {
                    str(city_data["city"]): {
                        "avg_temperature": self._safe_float(city_data["temperature"]),
                        "avg_humidity": self._safe_float(city_data["humidity"]),
                        "dominant_condition": (
                            str(city_data.get("weather_main", "")).lower()
                            if isinstance(city_data.get("weather_main", ""), str)
                            else ""
                        ),
                        "records": 30,  # Simulated record count
                        "members": [str(city_data["member_name"])],
                    }
                    for city_data in sample_data
                    if isinstance(city_data, dict)
                },
                "team_summary": {
                    "total_cities": len(sample_data),
                    "avg_temperature_global": sum(
                        self._safe_float(d["temperature"]) for d in sample_data
                    )
                    / len(sample_data),
                    "temperature_range": {
                        "min": min(
                            self._safe_float(d["temperature"]) for d in sample_data
                        ),
                        "max": max(
                            self._safe_float(d["temperature"]) for d in sample_data
                        ),
                    },
                    "most_common_condition": "clear",
                    "data_timestamp": timestamp,
                    "total_members": len(
                        set(str(d["member_name"]) for d in sample_data)
                    ),
                    "total_records": len(sample_data) * 30,  # Simulated
                },
            }

            # Create JSON file
            json_filename = f"team_compare_cities_data_{timestamp}.json"
            json_path = os.path.join(self.exports_dir, json_filename)
            with open(json_path, "w") as f:
                json.dump(analysis_data, f, indent=2)
            self.logger.info(f"Created sample JSON: {json_path}")

            return True

        except Exception as e:
            self.logger.error(f"Error creating sample data: {e}")
            return False
