"""
Composite Weather Service with fallback support.

This service combines multiple weather APIs for better reliability.
Primary: OpenWeatherMap, Fallback: WeatherAPI.com
"""

import logging
from typing import List
from typing import Optional

from ..interfaces.weather_interfaces import IWeatherAPI
from ..models.weather_models import CurrentWeather
from ..models.weather_models import Location
from ..models.weather_models import WeatherForecast
from .weather_api import OpenWeatherMapAPI
from .weatherapi_service import WeatherAPIService


class CompositeWeatherService(IWeatherAPI):
    """Weather service with primary and fallback APIs."""

    def __init__(
        self, openweather_api_key: str, weatherapi_api_key: Optional[str] = None
    ):
        """
        Initialize composite weather service.

        Args:
            openweather_api_key: OpenWeatherMap API key
            weatherapi_api_key: WeatherAPI.com API key (optional)
        """
        self.logger = logging.getLogger(__name__)

        # Primary service (OpenWeatherMap)
        self.primary_service = OpenWeatherMapAPI(openweather_api_key)

        # Fallback service (WeatherAPI.com)
        self.fallback_service = None
        if weatherapi_api_key:
            try:
                self.fallback_service = WeatherAPIService(weatherapi_api_key)
                self.logger.info(
                    "Fallback weather service (WeatherAPI.com) initialized"
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize fallback service: {e}")
        else:
            self.logger.info(
                "No fallback API key provided - running with primary service only"
            )

    def get_current_weather(
        self, city: str, units: str = "metric"
    ) -> Optional[CurrentWeather]:
        """
        Get current weather with fallback support.

        Args:
            city: City name
            units: Temperature units

        Returns:
            CurrentWeather or None if both services fail
        """
        # Try primary service first (OpenWeatherMap)
        try:
            self.logger.debug(f"Trying primary service (OpenWeatherMap) for {city}")
            weather = self.primary_service.get_current_weather(city, units)
            if weather:
                self.logger.debug(f"Primary service succeeded for {city}")
                return weather
            else:
                self.logger.warning(f"Primary service failed for {city}")
        except Exception as e:
            self.logger.warning(f"Primary service error for {city}: {e}")

        # Try fallback service if primary fails
        if self.fallback_service:
            try:
                self.logger.info(f"Trying fallback service (WeatherAPI.com) for {city}")
                weather = self.fallback_service.get_current_weather(city, units)
                if weather:
                    self.logger.info(f"Fallback service succeeded for {city}")
                    return weather
                else:
                    self.logger.error(f"Fallback service also failed for {city}")
            except Exception as e:
                self.logger.error(f"Fallback service error for {city}: {e}")
        else:
            self.logger.warning(f"No fallback service available for {city}")

        self.logger.error(f"All weather services failed for {city}")
        return None

    def get_forecast(
        self, city: str, days: int = 5, units: str = "metric"
    ) -> Optional[WeatherForecast]:
        """
        Get weather forecast with fallback support.

        Args:
            city: City name
            days: Number of forecast days
            units: Temperature units

        Returns:
            WeatherForecast or None if both services fail
        """
        # Try primary service first (OpenWeatherMap)
        try:
            self.logger.debug(f"Trying primary service forecast for {city}")
            forecast = self.primary_service.get_forecast(city, days, units)
            if forecast:
                self.logger.debug(f"Primary service forecast succeeded for {city}")
                return forecast
            else:
                self.logger.warning(f"Primary service forecast failed for {city}")
        except Exception as e:
            self.logger.warning(f"Primary service forecast error for {city}: {e}")

        # Try fallback service if primary fails
        if self.fallback_service:
            try:
                self.logger.info(f"Trying fallback service forecast for {city}")
                # WeatherAPI free tier only supports 3 days
                fallback_days = min(days, 3)
                forecast = self.fallback_service.get_forecast(
                    city, fallback_days, units
                )
                if forecast:
                    self.logger.info(f"Fallback service forecast succeeded for {city}")
                    return forecast
                else:
                    self.logger.error(
                        f"Fallback service forecast also failed for {city}"
                    )
            except Exception as e:
                self.logger.error(f"Fallback service forecast error for {city}: {e}")
        else:
            self.logger.warning(f"No fallback service available for forecast: {city}")

        self.logger.error(f"All forecast services failed for {city}")
        return None

    def search_locations(self, query: str, limit: int = 5) -> List[Location]:
        """
        Search for locations with fallback support.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of Location objects
        """
        # Try primary service first
        try:
            self.logger.debug(f"Trying primary service location search for {query}")
            locations = self.primary_service.search_locations(query, limit)
            if locations:
                self.logger.debug(
                    f"Primary service location search succeeded for {query}"
                )
                return locations
        except Exception as e:
            self.logger.warning(
                f"Primary service location search error for {query}: {e}"
            )

        # Try fallback service if primary fails
        if self.fallback_service:
            try:
                self.logger.info(f"Trying fallback service location search for {query}")
                locations = self.fallback_service.search_locations(query, limit)
                if locations:
                    self.logger.info(
                        f"Fallback service location search succeeded for {query}"
                    )
                    return locations
            except Exception as e:
                self.logger.error(
                    f"Fallback service location search error for {query}: {e}"
                )

        return []

    def get_current_weather_by_coordinates(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> Optional[CurrentWeather]:
        """
        Get current weather by coordinates with fallback support.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Temperature units

        Returns:
            CurrentWeather or None if both services fail
        """
        # Try primary service first
        try:
            self.logger.debug(
                f"Trying primary service coordinates weather for {latitude}, {longitude}"
            )
            weather = self.primary_service.get_current_weather_by_coordinates(
                latitude, longitude, units
            )
            if weather:
                self.logger.debug(
                    f"Primary service coordinates weather succeeded for {latitude}, {longitude}"
                )
                return weather
        except Exception as e:
            self.logger.warning(
                f"Primary service coordinates weather error for {latitude}, {longitude}: {e}"
            )

        # Try fallback service if primary fails
        if self.fallback_service:
            try:
                self.logger.info(
                    f"Trying fallback service coordinates weather for {latitude}, {longitude}"
                )
                weather = self.fallback_service.get_current_weather_by_coordinates(
                    latitude, longitude, units
                )
                if weather:
                    self.logger.info(
                        f"Fallback service coordinates weather succeeded for {latitude}, {longitude}"
                    )
                    return weather
            except Exception as e:
                self.logger.error(
                    f"Fallback service coordinates weather error for {latitude}, {longitude}: {e}"
                )

        return None

    def get_forecast_by_coordinates(
        self, latitude: float, longitude: float, days: int = 5, units: str = "metric"
    ) -> Optional[WeatherForecast]:
        """
        Get weather forecast by coordinates with fallback support.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of forecast days
            units: Temperature units

        Returns:
            WeatherForecast or None if both services fail
        """
        # Try primary service first
        try:
            self.logger.debug(
                f"Trying primary service coordinates forecast for {latitude}, {longitude}"
            )
            forecast = self.primary_service.get_forecast_by_coordinates(
                latitude, longitude, days, units
            )
            if forecast:
                self.logger.debug(
                    f"Primary service coordinates forecast succeeded for {latitude}, {longitude}"
                )
                return forecast
        except Exception as e:
            self.logger.warning(
                f"Primary service coordinates forecast error for {latitude}, {longitude}: {e}"
            )

        # Try fallback service if primary fails
        if self.fallback_service:
            try:
                self.logger.info(
                    f"Trying fallback service coordinates forecast for {latitude}, {longitude}"
                )
                fallback_days = min(days, 3)
                forecast = self.fallback_service.get_forecast_by_coordinates(
                    latitude, longitude, fallback_days, units
                )
                if forecast:
                    self.logger.info(
                        f"Fallback service coordinates forecast succeeded for {latitude}, {longitude}"
                    )
                    return forecast
            except Exception as e:
                self.logger.error(
                    f"Fallback service coordinates forecast error for {latitude}, {longitude}: {e}"
                )

        return None

    def get_service_status(self) -> dict:
        """
        Get status of all weather services.

        Returns:
            Dictionary with service status information
        """
        status = {
            "primary_service": "OpenWeatherMap",
            "primary_available": self.primary_service is not None,
            "fallback_service": "WeatherAPI.com" if self.fallback_service else None,
            "fallback_available": self.fallback_service is not None,
            "total_services": 1 + (1 if self.fallback_service else 0),
        }
        return status
