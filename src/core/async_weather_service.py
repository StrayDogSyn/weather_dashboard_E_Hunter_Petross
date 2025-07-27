"""Async Weather Service - Refactored with proper async/await patterns."""

import asyncio
import json
import logging
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import BaseModel, ValidationError

from src.interfaces.weather_interfaces import IAsyncWeatherAPI, ICacheService, IDataStorage
from src.models.weather_models import (
    CurrentWeather,
    FavoriteCity,
    Location,
    WeatherForecast,
)
from src.services.location_service import LocationDetectionService
from src.utils.formatters import clean_city_name, validate_city_name
from src.utils.validators import WeatherDataValidator, sanitize_input

# Type aliases
WeatherData = CurrentWeather
ForecastData = WeatherForecast
LocationData = Location


class WeatherAPIError(Exception):
    """Custom exception for weather API errors."""

    pass


class RetryConfig:
    """Configuration for retry logic with exponential backoff."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt with exponential backoff."""
        delay = self.base_delay * (self.backoff_factor**attempt)
        return min(delay, self.max_delay)


class WeatherDataSchema(BaseModel):
    """Pydantic schema for validating weather API responses."""

    class Config:
        extra = "allow"  # Allow extra fields from API

    # Required fields for current weather
    name: str
    sys: Dict[str, Any]
    coord: Dict[str, float]
    main: Dict[str, float]
    weather: List[Dict[str, Any]]
    dt: int

    # Optional fields
    wind: Optional[Dict[str, Any]] = None
    rain: Optional[Dict[str, Any]] = None
    snow: Optional[Dict[str, Any]] = None
    visibility: Optional[int] = None


class ForecastDataSchema(BaseModel):
    """Pydantic schema for validating forecast API responses."""

    class Config:
        extra = "allow"

    city: Dict[str, Any]
    list: List[Dict[str, Any]]
    cnt: int


class AsyncWeatherService:
    """Async weather service with proper error handling and retry logic."""

    def __init__(
        self,
        weather_api: IAsyncWeatherAPI,
        storage: IDataStorage,
        cache: ICacheService,
        retry_config: Optional[RetryConfig] = None,
    ):
        """
        Initialize async weather service.

        Args:
            weather_api: Async weather API implementation
            storage: Data storage implementation
            cache: Cache service implementation
            retry_config: Retry configuration for API calls
        """
        self.weather_api = weather_api
        self.storage = storage
        self.cache = cache
        self.validator = WeatherDataValidator()
        self.location_service = LocationDetectionService()
        self.retry_config = retry_config or RetryConfig()

        # Load favorite cities
        self.favorite_cities: List[FavoriteCity] = self._load_favorite_cities()

        logging.info("Async weather service initialized")

    async def get_current_weather(
        self, city: str, units: str = "metric", use_cache: bool = True
    ) -> Optional[WeatherData]:
        """
        Get current weather for a city with caching and retry logic.

        Args:
            city: City name
            units: Temperature units
            use_cache: Whether to use cached data

        Returns:
            Weather data or None if error
        """
        # Validate and clean city name
        if not validate_city_name(city):
            logging.error(f"Invalid city name: {city}")
            return None

        city = clean_city_name(city)

        # Check cache first
        cache_key = self.cache.get_cache_key("weather", city, units)
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logging.debug(f"Returning cached weather data for {city}")
                return cached_data

        # Fetch from API with retry logic
        logging.info(f"Fetching current weather for {city}")

        try:
            weather_data = await self._retry_api_call(
                self.weather_api.get_current_weather, city, units
            )

            if weather_data:
                # Validate data
                if not self._validate_weather_data(weather_data):
                    logging.error(f"Invalid weather data received for {city}")
                    return None

                # Cache the result
                if use_cache:
                    self.cache.set(cache_key, weather_data, ttl=300)  # 5 minutes

                # Save to storage for history
                await self._save_weather_history(weather_data)

                logging.info(f"Successfully retrieved weather for {city}")
                return weather_data
            else:
                logging.error(f"Failed to retrieve weather for {city}")
                return None

        except WeatherAPIError as e:
            logging.error(f"Weather API error for {city}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error getting weather for {city}: {e}")
            return None

    async def get_weather_forecast(
        self, city: str, days: int = 5, units: str = "metric", use_cache: bool = True
    ) -> Optional[ForecastData]:
        """
        Get weather forecast for a city with caching and retry logic.

        Args:
            city: City name
            days: Number of forecast days
            units: Temperature units
            use_cache: Whether to use cached data

        Returns:
            Forecast data or None if error
        """
        # Validate inputs
        if not validate_city_name(city):
            logging.error(f"Invalid city name: {city}")
            return None

        if not (1 <= days <= 16):
            logging.error(f"Invalid forecast days: {days}")
            return None

        city = clean_city_name(city)

        # Check cache first
        cache_key = self.cache.get_cache_key("forecast", city, days, units)
        if use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data:
                logging.debug(f"Returning cached forecast data for {city}")
                return cached_data

        # Fetch from API with retry logic
        logging.info(f"Fetching {days}-day forecast for {city}")

        try:
            forecast_data = await self._retry_api_call(
                self.weather_api.get_forecast, city, days, units
            )

            if forecast_data:
                # Validate data
                if not self._validate_forecast_data(forecast_data):
                    logging.error(f"Invalid forecast data received for {city}")
                    return None

                # Cache the result
                if use_cache:
                    self.cache.set(cache_key, forecast_data, ttl=600)  # 10 minutes

                logging.info(f"Successfully retrieved forecast for {city}")
                return forecast_data
            else:
                logging.error(f"Failed to retrieve forecast for {city}")
                return None

        except WeatherAPIError as e:
            logging.error(f"Weather API error for forecast {city}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error getting forecast for {city}: {e}")
            return None

    async def search_locations(self, query: str, limit: int = 5) -> List[LocationData]:
        """
        Search for locations by name with retry logic.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of locations
        """
        if not query or len(query.strip()) < 2:
            logging.warning("Search query too short")
            return []

        query = sanitize_input(query.strip())

        # Check cache first
        cache_key = self.cache.get_cache_key("location_search", query, limit)
        cached_results = self.cache.get(cache_key)
        if cached_results:
            logging.debug(f"Returning cached location search for: {query}")
            return cached_results

        # Search via API with retry logic
        logging.info(f"Searching locations for: {query}")

        try:
            locations = await self._retry_api_call(
                self.weather_api.search_locations, query, limit
            )

            # Cache results
            if locations:
                self.cache.set(cache_key, locations, ttl=3600)  # 1 hour

            return locations or []

        except WeatherAPIError as e:
            logging.error(f"Weather API error searching locations for {query}: {e}")
            return []
        except Exception as e:
            logging.error(f"Unexpected error searching locations for {query}: {e}")
            return []

    async def get_current_location_weather(
        self, units: str = "metric", use_cache: bool = True
    ) -> Optional[WeatherData]:
        """
        Get weather for current detected location with async location detection.

        Args:
            units: Temperature units (metric, imperial, standard)
            use_cache: Whether to use cache

        Returns:
            WeatherData or None if error
        """
        logging.info("Attempting to detect current location")

        try:
            # Get current location coordinates using location service
            location_data = await self._get_current_location_async()

            if not location_data:
                logging.error("Failed to detect current location")
                return None

            latitude, longitude, city_name = location_data
            logging.info(f"Location detected: {city_name} ({latitude}, {longitude})")

            # Generate cache key
            cache_key = self.cache.get_cache_key(
                "weather_coords", str(latitude), str(longitude), units
            )

            # Check cache
            if use_cache:
                cached_data = self.cache.get(cache_key)
                if cached_data:
                    logging.info(f"Using cached weather for {city_name}")
                    return cached_data

            # Fetch from API with retry logic
            logging.info(
                f"Fetching current weather for {city_name} at coordinates ({latitude}, {longitude})"
            )

            weather_data = await self._retry_api_call(
                self.weather_api.get_current_weather_by_coordinates,
                latitude,
                longitude,
                units,
            )

            if weather_data:
                # Validate data
                if not self._validate_weather_data(weather_data):
                    logging.error(
                        f"Invalid weather data received for coordinates ({latitude}, {longitude})"
                    )
                    return None

                # Cache the result
                if use_cache:
                    self.cache.set(cache_key, weather_data, ttl=300)  # 5 minutes

                logging.info(
                    f"Successfully retrieved weather for {weather_data.location.name}"
                )
                return weather_data
            else:
                logging.error(
                    f"Failed to retrieve weather for coordinates ({latitude}, {longitude})"
                )
                return None

        except Exception as e:
            logging.error(f"Error in current location weather: {e}")
            return None

    async def _retry_api_call(self, func, *args, **kwargs):
        """
        Execute API call with exponential backoff retry logic.

        Args:
            func: Async function to call
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            WeatherAPIError: If all retries fail
        """
        last_exception = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                if attempt > 0:
                    logging.info(f"API call succeeded on attempt {attempt + 1}")
                return result

            except aiohttp.ClientTimeout as e:
                last_exception = e
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    logging.warning(
                        f"API timeout (attempt {attempt + 1}/{self.retry_config.max_retries + 1}), "
                        f"retrying in {delay:.1f}s..."
                    )
                    await asyncio.sleep(delay)
                    continue

            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self.retry_config.max_retries:
                    delay = self.retry_config.get_delay(attempt)
                    logging.warning(
                        f"API client error (attempt {attempt + 1}/{self.retry_config.max_retries + 1}), "
                        f"retrying in {delay:.1f}s...: {e}"
                    )
                    await asyncio.sleep(delay)
                    continue

            except Exception as e:
                last_exception = e
                logging.error(f"Unexpected error in API call: {e}")
                break

        # All retries failed
        raise WeatherAPIError(
            f"API call failed after {self.retry_config.max_retries + 1} attempts: {last_exception}"
        )

    def _validate_weather_data(self, weather_data: WeatherData) -> bool:
        """
        Validate weather data against expected schema.

        Args:
            weather_data: Weather data to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            if not weather_data or not weather_data.location:
                return False

            if not weather_data.temperature or weather_data.temperature.value is None:
                return False

            if not weather_data.condition:
                return False

            # Validate temperature range (reasonable bounds)
            temp_value = weather_data.temperature.value
            if temp_value < -100 or temp_value > 70:  # Celsius bounds
                logging.warning(f"Temperature out of reasonable range: {temp_value}°C")
                return False

            # Validate humidity
            if weather_data.humidity is not None:
                if weather_data.humidity < 0 or weather_data.humidity > 100:
                    logging.warning(f"Humidity out of range: {weather_data.humidity}%")
                    return False

            return True

        except Exception as e:
            logging.error(f"Error validating weather data: {e}")
            return False

    def _validate_forecast_data(self, forecast_data: ForecastData) -> bool:
        """
        Validate forecast data against expected schema.

        Args:
            forecast_data: Forecast data to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            if not forecast_data or not forecast_data.location:
                return False

            if not forecast_data.forecast_days or len(forecast_data.forecast_days) == 0:
                return False

            # Validate each forecast day
            for day in forecast_data.forecast_days:
                if not day.date or not day.temperature_high or not day.temperature_low:
                    return False

                # Check temperature consistency
                if day.temperature_high.value < day.temperature_low.value:
                    logging.warning(f"High temp lower than low temp on {day.date}")
                    return False

            return True

        except Exception as e:
            logging.error(f"Error validating forecast data: {e}")
            return False

    async def _get_current_location_async(self):
        """
        Async wrapper for location detection.

        Returns:
            Location data tuple or None
        """
        # Run location detection in thread pool since it's sync
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.location_service.get_current_location
        )

    async def _save_weather_history(self, weather_data: WeatherData) -> None:
        """
        Async save weather data to history for analytics.

        Args:
            weather_data: Weather data to save
        """
        try:
            # Run storage operations in thread pool since they're sync
            loop = asyncio.get_event_loop()

            # Load existing history
            history = await loop.run_in_executor(
                None, self.storage.load_data, "weather_history.json"
            ) or {"entries": []}

            # Add new entry
            entry = {
                "city": weather_data.location.name,
                "country": weather_data.location.country,
                "temperature": weather_data.temperature.value,
                "condition": weather_data.condition.value,
                "timestamp": (
                    weather_data.timestamp.isoformat()
                    if weather_data.timestamp
                    else datetime.now().isoformat()
                ),
            }

            history["entries"].append(entry)

            # Keep only last 1000 entries
            if len(history["entries"]) > 1000:
                history["entries"] = history["entries"][-1000:]

            history["last_updated"] = datetime.now().isoformat()

            # Save back to storage
            await loop.run_in_executor(
                None, self.storage.save_data, history, "weather_history.json"
            )

        except Exception as e:
            logging.error(f"Error saving weather history: {e}")

    def _load_favorite_cities(self) -> List[FavoriteCity]:
        """
        Load favorite cities from storage (sync for initialization).

        Returns:
            List of favorite cities
        """
        try:
            data = self.storage.load_data("favorite_cities.json")
            if not data or "cities" not in data:
                return []

            favorites = []
            for city_data in data["cities"]:
                try:
                    location = Location(
                        name=city_data["location"]["name"],
                        country=city_data["location"]["country"],
                        latitude=city_data["location"]["latitude"],
                        longitude=city_data["location"]["longitude"],
                    )

                    favorite = FavoriteCity(
                        location=location,
                        nickname=city_data.get("nickname"),
                        added_date=(
                            datetime.fromisoformat(city_data["added_date"])
                            if city_data.get("added_date")
                            else datetime.now()
                        ),
                        last_viewed=(
                            datetime.fromisoformat(city_data["last_viewed"])
                            if city_data.get("last_viewed")
                            else None
                        ),
                    )

                    favorites.append(favorite)

                except Exception as e:
                    logging.error(f"Error loading favorite city data: {e}")
                    continue

            logging.info(f"Loaded {len(favorites)} favorite cities")
            return favorites

        except Exception as e:
            logging.error(f"Error loading favorite cities: {e}")
            return []

    # Additional async methods for favorites management
    async def add_favorite_city_async(
        self, city: str, nickname: Optional[str] = None
    ) -> bool:
        """
        Async version of add favorite city.

        Args:
            city: City name
            nickname: Optional nickname

        Returns:
            True if successful
        """
        if not validate_city_name(city):
            logging.error(f"Invalid city name: {city}")
            return False

        city = clean_city_name(city)

        # Check if already in favorites
        for fav in self.favorite_cities:
            if fav.location.name.lower() == city.lower():
                logging.warning(f"City already in favorites: {city}")
                return False

        # Search for location to get coordinates
        locations = await self.search_locations(city, 1)
        if not locations:
            logging.error(f"Could not find location for: {city}")
            return False

        location = locations[0]

        # Create favorite city
        favorite = FavoriteCity(
            location=location, nickname=nickname, added_date=datetime.now()
        )

        self.favorite_cities.append(favorite)
        await self._save_favorite_cities_async()

        logging.info(f"Added {city} to favorites")
        return True

    async def _save_favorite_cities_async(self) -> bool:
        """
        Async save favorite cities to storage.

        Returns:
            True if successful
        """
        try:
            cities_data = []
            for fav in self.favorite_cities:
                city_data = {
                    "location": {
                        "name": fav.location.name,
                        "country": fav.location.country,
                        "latitude": fav.location.latitude,
                        "longitude": fav.location.longitude,
                    },
                    "nickname": fav.nickname,
                    "added_date": (
                        fav.added_date.isoformat() if fav.added_date else None
                    ),
                    "last_viewed": (
                        fav.last_viewed.isoformat() if fav.last_viewed else None
                    ),
                }
                cities_data.append(city_data)

            data = {"cities": cities_data, "last_updated": datetime.now().isoformat()}

            # Run storage operation in thread pool
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(
                None, self.storage.save_data, data, "favorite_cities.json"
            )

            if success:
                logging.debug("Favorite cities saved")
            return success

        except Exception as e:
            logging.error(f"Error saving favorite cities: {e}")
            return False

    async def get_weather_for_favorites_async(
        self, units: str = "metric"
    ) -> Dict[str, Optional[WeatherData]]:
        """
        Async get current weather for all favorite cities.

        Args:
            units: Temperature units

        Returns:
            Dictionary mapping city names to weather data
        """
        results = {}

        # Use asyncio.gather for concurrent requests
        tasks = []
        city_names = []

        for favorite in self.favorite_cities:
            city_name = favorite.location.name
            task = self.get_current_weather(city_name, units)
            tasks.append(task)
            city_names.append(favorite.display_name)

        if tasks:
            weather_results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, (city_name, weather_data) in enumerate(
                zip(city_names, weather_results)
            ):
                if isinstance(weather_data, Exception):
                    logging.error(
                        f"Error getting weather for {city_name}: {weather_data}"
                    )
                    results[city_name] = None
                else:
                    results[city_name] = weather_data

                    # Mark as viewed
                    if weather_data and i < len(self.favorite_cities):
                        self.favorite_cities[i].mark_viewed()

            if self.favorite_cities:
                await self._save_favorite_cities_async()

        return results
