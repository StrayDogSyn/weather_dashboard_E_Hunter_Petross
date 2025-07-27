"""Optimized Team Data Service for Weather Dashboard.

This service provides high-performance functionality to load and utilize team weather data
from the GitHub repository for the Compare Cities feature with caching, async support,
and robust error handling.
"""

import asyncio
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta
from functools import lru_cache
from glob import glob
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen

import pandas as pd
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import validator

from ..models.weather_models import AtmosphericPressure
from ..models.weather_models import CurrentWeather
from ..models.weather_models import Location
from ..models.weather_models import Temperature
from ..models.weather_models import TemperatureUnit
from ..models.weather_models import WeatherCondition
from ..models.weather_models import Wind


class TeamDataConfig(BaseModel):
    """Configuration model for team data service."""

    model_config = ConfigDict(frozen=True)

    github_repo_base: str = Field(
        default="https://raw.githubusercontent.com/StrayDogSyn/New_Team_Dashboard/main/exports",
        description="Base URL for GitHub repository exports",
    )
    csv_filename: str = Field(
        default="team_weather_data_20250717_204218.csv",
        description="CSV filename for weather data",
    )
    json_filename: str = Field(
        default="team_compare_cities_data_20250717_204218.json",
        description="JSON filename for analysis data",
    )
    cache_ttl_seconds: int = Field(
        default=3600, description="Cache time-to-live in seconds"
    )
    max_retries: int = Field(default=3, description="Maximum number of retry attempts")
    request_timeout: int = Field(default=30, description="Request timeout in seconds")

    @validator("cache_ttl_seconds")
    def validate_cache_ttl(cls, v):
        if v < 60:
            raise ValueError("Cache TTL must be at least 60 seconds")
        return v


class CacheEntry(BaseModel):
    """Cache entry with timestamp for TTL validation."""

    data: Any
    timestamp: datetime
    ttl_seconds: int

    @property
    def is_expired(self) -> bool:
        return datetime.now() - self.timestamp > timedelta(seconds=self.ttl_seconds)


class DataValidator:
    """Validates and cleans team data."""

    @staticmethod
    def safe_float(val: Any, default: float = 0.0) -> float:
        """Safely convert value to float with default fallback."""
        try:
            if pd.isna(val):
                return default
            return float(val)
        except (TypeError, ValueError, AttributeError):
            return default

    @staticmethod
    def safe_int(val: Any, default: int = 0) -> int:
        """Safely convert value to int with default fallback."""
        try:
            if pd.isna(val):
                return default
            return int(float(val))
        except (TypeError, ValueError, AttributeError):
            return default

    @staticmethod
    def validate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean DataFrame with required columns."""
        required_columns = ["city"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Clean and standardize data
        df = df.copy()
        if "city" in df.columns:
            df["city"] = df["city"].astype(str).str.strip()

        # Handle timestamp column
        if "timestamp" in df.columns:
            try:
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            except Exception:
                df["timestamp"] = pd.to_datetime(datetime.now())
        else:
            df["timestamp"] = pd.to_datetime(datetime.now())

        return df


class OptimizedTeamDataService:
    """High-performance service for loading and processing team weather data.

    Features:
    - Intelligent caching with TTL
    - Async support for better scalability
    - Robust error handling with retries
    - Data validation and schema enforcement
    - Memory-efficient data processing
    - Comprehensive monitoring and logging
    """

    def __init__(self, config: Optional[TeamDataConfig] = None):
        """Initialize the optimized team data service.

        Args:
            config: Configuration object, uses defaults if None
        """
        self.config = config or TeamDataConfig()
        self.logger = logging.getLogger(__name__)

        # Setup directories
        self.exports_dir = Path(__file__).parent.parent.parent / "exports"
        self.exports_dir.mkdir(exist_ok=True)

        # Initialize caches
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

        # Metrics
        self._metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "download_attempts": 0,
            "download_successes": 0,
            "errors": 0,
        }

        # Thread pool for I/O operations
        self._executor = ThreadPoolExecutor(max_workers=4)

        self.logger.info("OptimizedTeamDataService initialized with caching enabled")

    def get_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics."""
        cache_total = self._metrics["cache_hits"] + self._metrics["cache_misses"]
        hit_rate = self._metrics["cache_hits"] / cache_total if cache_total > 0 else 0

        return {
            **self._metrics,
            "cache_hit_rate": hit_rate,
            "cache_size": len(self._cache),
            "config": self.config.model_dump(),
        }

    async def _get_cached_or_fetch(self, key: str, fetch_func) -> Any:
        """Get data from cache or fetch using provided function."""
        async with self._lock:
            # Check cache first
            if key in self._cache and not self._cache[key].is_expired:
                self._metrics["cache_hits"] += 1
                self.logger.debug(f"Cache hit for key: {key}")
                return self._cache[key].data

            # Cache miss or expired
            self._metrics["cache_misses"] += 1
            self.logger.debug(f"Cache miss for key: {key}")

            try:
                # Fetch new data
                data = await fetch_func()

                # Cache the result
                self._cache[key] = CacheEntry(
                    data=data,
                    timestamp=datetime.now(),
                    ttl_seconds=self.config.cache_ttl_seconds,
                )

                return data

            except Exception as e:
                self._metrics["errors"] += 1
                self.logger.error(f"Failed to fetch data for key {key}: {e}")
                raise

    async def _download_with_retry(self, url: str, local_path: Path) -> bool:
        """Download file with exponential backoff retry logic."""
        for attempt in range(self.config.max_retries):
            try:
                self._metrics["download_attempts"] += 1

                # Create request with proper headers
                request = Request(url)
                request.add_header("User-Agent", "WeatherDashboard/1.0")

                with urlopen(request, timeout=self.config.request_timeout) as response:
                    local_path.write_bytes(response.read())

                self._metrics["download_successes"] += 1
                self.logger.info(f"Successfully downloaded: {url}")
                return True

            except (HTTPError, URLError, OSError) as e:
                wait_time = 2**attempt
                self.logger.warning(
                    f"Download attempt {attempt + 1} failed for {url}: {e}. "
                    f"Retrying in {wait_time}s..."
                )

                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(
                        f"Failed to download {url} after {self.config.max_retries} attempts"
                    )
                    return False

        return False

    async def _load_csv_data(self) -> pd.DataFrame:
        """Load and validate CSV data with fallback to local files."""
        csv_url = f"{self.config.github_repo_base}/{self.config.csv_filename}"
        csv_local_path = self.exports_dir / self.config.csv_filename

        # Try to download from GitHub
        download_success = await self._download_with_retry(csv_url, csv_local_path)

        # If download failed, try local files
        if not download_success:
            local_csv_files = list(self.exports_dir.glob("team_weather_data_*.csv"))
            if local_csv_files:
                csv_local_path = max(local_csv_files, key=lambda p: p.stat().st_ctime)
                self.logger.info(f"Using local CSV file: {csv_local_path}")
            else:
                raise FileNotFoundError("No CSV data available locally or remotely")

        # Load and validate data
        df = await asyncio.get_event_loop().run_in_executor(
            self._executor, pd.read_csv, csv_local_path
        )

        return DataValidator.validate_dataframe(df)

    async def _load_json_data(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Load and validate JSON analysis data with fallback to local files."""
        json_url = f"{self.config.github_repo_base}/{self.config.json_filename}"
        json_local_path = self.exports_dir / self.config.json_filename

        # Try to download from GitHub
        download_success = await self._download_with_retry(json_url, json_local_path)

        # If download failed, try local files
        if not download_success:
            local_json_files = list(
                self.exports_dir.glob("team_compare_cities_data_*.json")
            )
            if local_json_files:
                json_local_path = max(local_json_files, key=lambda p: p.stat().st_ctime)
                self.logger.info(f"Using local JSON file: {json_local_path}")
            else:
                self.logger.warning("No JSON analysis data available")
                return {}, {}

        # Load JSON data
        def load_json():
            with open(json_local_path, "r", encoding="utf-8") as f:
                return json.load(f)

        analysis_data = await asyncio.get_event_loop().run_in_executor(
            self._executor, load_json
        )

        cities_analysis = analysis_data.get("cities_analysis", {})
        team_summary = analysis_data.get("team_summary", {})

        return cities_analysis, team_summary

    async def load_team_data(self) -> bool:
        """Load team weather data with async support and caching.

        Returns:
            True if data was loaded successfully, False otherwise
        """
        try:
            # Load CSV and JSON data concurrently
            csv_task = self._get_cached_or_fetch("csv_data", self._load_csv_data)
            json_task = self._get_cached_or_fetch("json_data", self._load_json_data)

            csv_data, (cities_analysis, team_summary) = await asyncio.gather(
                csv_task, json_task, return_exceptions=True
            )

            # Handle any exceptions
            if isinstance(csv_data, Exception):
                self.logger.error(f"Failed to load CSV data: {csv_data}")
                return False

            if isinstance(cities_analysis, Exception):
                self.logger.warning(f"Failed to load JSON data: {cities_analysis}")
                cities_analysis, team_summary = {}, {}

            # Cache individual components for faster access
            self._cache["team_data"] = CacheEntry(
                data=csv_data,
                timestamp=datetime.now(),
                ttl_seconds=self.config.cache_ttl_seconds,
            )

            self._cache["cities_analysis"] = CacheEntry(
                data=cities_analysis,
                timestamp=datetime.now(),
                ttl_seconds=self.config.cache_ttl_seconds,
            )

            self._cache["team_summary"] = CacheEntry(
                data=team_summary,
                timestamp=datetime.now(),
                ttl_seconds=self.config.cache_ttl_seconds,
            )

            self.logger.info("Team data loaded successfully")
            return True

        except Exception as e:
            self._metrics["errors"] += 1
            self.logger.error(f"Error loading team data: {e}")
            return False

    async def get_city_weather_from_team_data(
        self, city_name: str
    ) -> Optional[CurrentWeather]:
        """Get weather data for a city from team data with async support.

        Args:
            city_name: Name of the city to get weather for

        Returns:
            CurrentWeather object or None if city not found
        """
        try:
            # Ensure data is loaded
            team_data = await self._get_cached_or_fetch(
                "team_data", self._load_csv_data
            )

            # Search for city (case-insensitive, optimized)
            city_mask = team_data["city"].str.lower() == city_name.lower()
            city_data = team_data[city_mask]

            if city_data.empty:
                self.logger.warning(f"City '{city_name}' not available in team data")
                return None

            # Get most recent data efficiently
            if "timestamp" in city_data.columns:
                latest_data = city_data.loc[city_data["timestamp"].idxmax()]
            else:
                latest_data = city_data.iloc[-1]

            # Extract and validate data using optimized validators
            location = Location(
                name=str(latest_data["city"]),
                country=str(latest_data.get("country", "Unknown")),
                latitude=DataValidator.safe_float(latest_data.get("latitude"), 0.0),
                longitude=DataValidator.safe_float(latest_data.get("longitude"), 0.0),
            )

            temp_value = DataValidator.safe_float(latest_data.get("temperature"), 0.0)
            temperature = Temperature(
                value=temp_value,
                unit=TemperatureUnit.CELSIUS,
                feels_like=temp_value + 1.0,  # Simple feels-like calculation
            )

            pressure = AtmosphericPressure(
                value=DataValidator.safe_float(latest_data.get("pressure"), 1013.25)
            )

            wind = Wind(
                speed=DataValidator.safe_float(latest_data.get("wind_speed"), 0.0),
                direction=DataValidator.safe_int(latest_data.get("wind_direction"), 0),
            )

            condition_str = str(latest_data.get("condition", "clear")).lower()
            condition = self._map_condition_string(condition_str)

            humidity = DataValidator.safe_int(latest_data.get("humidity"), 50)

            weather = CurrentWeather(
                location=location,
                temperature=temperature,
                condition=condition,
                description=str(latest_data.get("description", condition_str.title())),
                humidity=humidity,
                pressure=pressure,
                wind=wind,
                timestamp=datetime.now(),
            )

            self.logger.info(f"Retrieved weather data for {city_name} from team data")
            return weather

        except Exception as e:
            self._metrics["errors"] += 1
            self.logger.error(f"Error creating weather data for {city_name}: {e}")
            return None

    @lru_cache(maxsize=128)
    def _map_condition_string(self, condition_str: str) -> WeatherCondition:
        """Map condition string to WeatherCondition enum with caching.

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

    async def get_available_cities(self) -> List[str]:
        """Get list of cities available in team data with caching.

        Returns:
            List of city names
        """
        try:
            team_data = await self._get_cached_or_fetch(
                "team_data", self._load_csv_data
            )
            cities = sorted(team_data["city"].unique().tolist())
            return cities
        except Exception as e:
            self._metrics["errors"] += 1
            self.logger.error(f"Error getting available cities: {e}")
            return []

    async def get_team_summary(self) -> Dict[str, Any]:
        """Get team weather data summary with async support.

        Returns:
            Dictionary containing team summary data
        """
        try:
            _, team_summary = await self._get_cached_or_fetch(
                "json_data", self._load_json_data
            )
            return team_summary
        except Exception as e:
            self._metrics["errors"] += 1
            self.logger.error(f"Error getting team summary: {e}")
            return {}

    async def get_cities_analysis(self) -> Dict[str, Any]:
        """Get cities analysis data with async support.

        Returns:
            Dictionary containing cities analysis data
        """
        try:
            cities_analysis, _ = await self._get_cached_or_fetch(
                "json_data", self._load_json_data
            )
            return cities_analysis
        except Exception as e:
            self._metrics["errors"] += 1
            self.logger.error(f"Error getting cities analysis: {e}")
            return {}

    async def refresh_team_data(self) -> bool:
        """Force refresh team data from GitHub repository.

        Returns:
            True if data was refreshed successfully
        """
        try:
            # Clear all caches
            async with self._lock:
                self._cache.clear()
                self.logger.info("Cache cleared for refresh")

            # Reload data from GitHub
            success = await self.load_team_data()
            if success:
                self.logger.info("Team data refreshed successfully")
            return success

        except Exception as e:
            self._metrics["errors"] += 1
            self.logger.error(f"Error refreshing team data: {e}")
            return False

    def get_github_repo_info(self) -> Dict[str, str]:
        """Get information about the GitHub repository data source.

        Returns:
            Dictionary with repository information
        """
        return {
            "repository": "StrayDogSyn/New_Team_Dashboard",
            "base_url": self.config.github_repo_base,
            "csv_file": self.config.csv_filename,
            "json_file": self.config.json_filename,
            "csv_url": f"{self.config.github_repo_base}/{self.config.csv_filename}",
            "json_url": f"{self.config.github_repo_base}/{self.config.json_filename}",
            "cache_ttl": self.config.cache_ttl_seconds,
            "max_retries": self.config.max_retries,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the service.

        Returns:
            Health status information
        """
        start_time = time.time()

        try:
            # Test data loading
            cities = await self.get_available_cities()

            # Calculate response time
            response_time = time.time() - start_time

            status = {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "cities_available": len(cities),
                "cache_entries": len(self._cache),
                "metrics": self.get_metrics(),
                "timestamp": datetime.now().isoformat(),
            }

            return status

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "timestamp": datetime.now().isoformat(),
            }

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self._executor.shutdown(wait=True)

    async def create_sample_team_data(self) -> bool:
        """Create sample team data files for demonstration based on GitHub repository data.

        Returns:
            True if sample data was created successfully
        """
        try:
            # First try to load actual team data from GitHub
            if await self.load_team_data():
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
            csv_path = self.exports_dir / csv_filename

            # Ensure exports directory exists
            self.exports_dir.mkdir(exist_ok=True)

            await asyncio.get_event_loop().run_in_executor(
                self._executor, df.to_csv, csv_path, False
            )
            self.logger.info(f"Created sample CSV: {csv_path}")

            # Sample JSON analysis data
            analysis_data = {
                "cities_analysis": {
                    str(city_data["city"]): {
                        "avg_temperature": DataValidator.safe_float(
                            city_data["temperature"]
                        ),
                        "avg_humidity": DataValidator.safe_float(city_data["humidity"]),
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
                        DataValidator.safe_float(d["temperature"]) for d in sample_data
                    )
                    / len(sample_data),
                    "temperature_range": {
                        "min": min(
                            DataValidator.safe_float(d["temperature"])
                            for d in sample_data
                        ),
                        "max": max(
                            DataValidator.safe_float(d["temperature"])
                            for d in sample_data
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
            json_path = self.exports_dir / json_filename

            def write_json():
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(analysis_data, f, indent=2, ensure_ascii=False)

            await asyncio.get_event_loop().run_in_executor(self._executor, write_json)
            self.logger.info(f"Created sample JSON: {json_path}")

            return True

        except Exception as e:
            self._metrics["errors"] += 1
            self.logger.error(f"Error creating sample data: {e}")
            return False


# Backward compatibility alias
TeamDataService = OptimizedTeamDataService
