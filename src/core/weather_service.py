"""Core business logic for the Weather Dashboard application."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from src.interfaces.weather_interfaces import ICacheService, IDataStorage, IWeatherAPI
from src.models.weather_models import (
    CurrentWeather,
    FavoriteCity,
    Location,
    WeatherForecast,
)
from src.utils.formatters import clean_city_name, validate_city_name
from src.utils.validators import WeatherDataValidator, sanitize_input

# Type aliases
WeatherData = CurrentWeather
ForecastData = WeatherForecast
LocationData = Location


class WeatherService:
    """Core weather service implementing business logic."""

    def __init__(
        self, weather_api: IWeatherAPI, storage: IDataStorage, cache: ICacheService
    ):
        """
        Initialize weather service.

        Args:
            weather_api: Weather API implementation
            storage: Data storage implementation
            cache: Cache service implementation
        """
        self.weather_api = weather_api
        self.storage = storage
        self.cache = cache
        self.validator = WeatherDataValidator()

        # Load favorite cities
        self.favorite_cities: List[FavoriteCity] = self._load_favorite_cities()

        logging.info("Weather service initialized")

    def get_current_weather(
        self, city: str, units: str = "metric", use_cache: bool = True
    ) -> Optional[WeatherData]:
        """
        Get current weather for a city with caching.

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

        # Fetch from API
        logging.info(f"Fetching current weather for {city}")
        weather_data = self.weather_api.get_current_weather(city, units)

        if weather_data:
            # Cache the result
            if use_cache:
                self.cache.set(cache_key, weather_data, ttl=300)  # 5 minutes

            # Save to storage for history
            self._save_weather_history(weather_data)

            logging.info(f"Successfully retrieved weather for {city}")
            return weather_data
        else:
            logging.error(f"Failed to retrieve weather for {city}")
            return None

    def get_weather_forecast(
        self, city: str, days: int = 5, units: str = "metric", use_cache: bool = True
    ) -> Optional[ForecastData]:
        """
        Get weather forecast for a city with caching.

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

        # Fetch from API
        logging.info(f"Fetching {days}-day forecast for {city}")
        forecast_data = self.weather_api.get_forecast(city, days, units)

        if forecast_data:
            # Cache the result
            if use_cache:
                self.cache.set(cache_key, forecast_data, ttl=600)  # 10 minutes

            logging.info(f"Successfully retrieved forecast for {city}")
            return forecast_data
        else:
            logging.error(f"Failed to retrieve forecast for {city}")
            return None

    def search_locations(self, query: str, limit: int = 5) -> List[LocationData]:
        """
        Search for locations by name.

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

        # Search via API
        logging.info(f"Searching locations for: {query}")
        locations = self.weather_api.search_locations(query, limit)

        # Cache results
        if locations:
            self.cache.set(cache_key, locations, ttl=3600)  # 1 hour

        return locations

    def add_favorite_city(self, city: str, nickname: Optional[str] = None) -> bool:
        """
        Add a city to favorites.

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
        locations = self.search_locations(city, 1)
        if not locations:
            logging.error(f"Could not find location for: {city}")
            return False

        location = locations[0]

        # Create favorite city
        favorite = FavoriteCity(
            location=location, nickname=nickname, added_date=datetime.now()
        )

        self.favorite_cities.append(favorite)
        self._save_favorite_cities()

        logging.info(f"Added {city} to favorites")
        return True

    def remove_favorite_city(self, city: str) -> bool:
        """
        Remove a city from favorites.

        Args:
            city: City name or nickname

        Returns:
            True if successful
        """
        city = city.strip()

        for i, fav in enumerate(self.favorite_cities):
            if fav.location.name.lower() == city.lower() or (
                fav.nickname and fav.nickname.lower() == city.lower()
            ):

                removed_city = self.favorite_cities.pop(i)
                self._save_favorite_cities()

                logging.info(f"Removed {removed_city.display_name} from favorites")
                return True

        logging.warning(f"City not found in favorites: {city}")
        return False

    def get_favorite_cities(self) -> List[FavoriteCity]:
        """Get list of favorite cities."""
        return self.favorite_cities.copy()

    def mark_city_viewed(self, city: str) -> None:
        """Mark a favorite city as recently viewed."""
        for fav in self.favorite_cities:
            if fav.location.name.lower() == city.lower():
                fav.mark_viewed()
                self._save_favorite_cities()
                break

    def get_weather_for_favorites(
        self, units: str = "metric"
    ) -> Dict[str, Optional[WeatherData]]:
        """
        Get current weather for all favorite cities.

        Args:
            units: Temperature units

        Returns:
            Dictionary mapping city names to weather data
        """
        results = {}

        for favorite in self.favorite_cities:
            city_name = favorite.location.name
            weather_data = self.get_current_weather(city_name, units)
            results[favorite.display_name] = weather_data

            # Mark as viewed
            if weather_data:
                favorite.mark_viewed()

        if self.favorite_cities:
            self._save_favorite_cities()

        return results

    def clear_cache(self) -> bool:
        """Clear all cached data."""
        success = self.cache.clear()
        if success:
            logging.info("Weather service cache cleared")
        return success

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()

    def _load_favorite_cities(self) -> List[FavoriteCity]:
        """Load favorite cities from storage."""
        try:
            data = self.storage.load_data("favorite_cities.json")
            if not data or "cities" not in data:
                return []

            favorites = []
            for city_data in data["cities"]:
                try:
                    from ..models import Location

                    location = Location(
                        name=city_data["location"]["name"],
                        country=city_data["location"]["country"],
                        latitude=city_data["location"]["latitude"],
                        longitude=city_data["location"]["longitude"],
                    )

                    favorite = FavoriteCity(
                        location=location,
                        nickname=city_data.get("nickname"),
                        added_date=datetime.fromisoformat(city_data["added_date"]),
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

    def _save_favorite_cities(self) -> bool:
        """Save favorite cities to storage."""
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

            success = self.storage.save_data(data, "favorite_cities.json")
            if success:
                logging.debug("Favorite cities saved")
            return success

        except Exception as e:
            logging.error(f"Error saving favorite cities: {e}")
            return False

    def _save_weather_history(self, weather_data: WeatherData) -> None:
        """Save weather data to history for analytics."""
        try:
            # Load existing history
            history = self.storage.load_data("weather_history.json") or {"entries": []}

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
            self.storage.save_data(history, "weather_history.json")

        except Exception as e:
            logging.error(f"Error saving weather history: {e}")
