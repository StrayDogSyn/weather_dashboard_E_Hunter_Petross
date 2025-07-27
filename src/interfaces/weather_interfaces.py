"""Weather service interfaces for the Weather Dashboard application."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..models.weather_models import CurrentWeather, Location, WeatherForecast

# Type aliases for cleaner interfaces
WeatherData = CurrentWeather
ForecastData = WeatherForecast
LocationData = Location


class IWeatherAPI(ABC):
    """Interface for weather API services (synchronous)."""

    @abstractmethod
    def get_current_weather(
        self, city: str, units: str = "metric"
    ) -> Optional[WeatherData]:
        """
        Get current weather for a city.

        Args:
            city: City name
            units: Temperature units (metric, imperial, standard)

        Returns:
            WeatherData or None if error
        """
        pass

    @abstractmethod
    def get_forecast(
        self, city: str, days: int = 5, units: str = "metric"
    ) -> Optional[ForecastData]:
        """
        Get weather forecast for a city.

        Args:
            city: City name
            days: Number of days for forecast
            units: Temperature units

        Returns:
            ForecastData or None if error
        """
        pass

    @abstractmethod
    def search_locations(self, query: str, limit: int = 5) -> List[LocationData]:
        """
        Search for locations by name.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of LocationData
        """
        pass

    @abstractmethod
    def get_current_weather_by_coordinates(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> Optional[WeatherData]:
        """
        Get current weather for specific coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Temperature units (metric, imperial, standard)

        Returns:
            WeatherData or None if error
        """
        pass

    @abstractmethod
    def get_forecast_by_coordinates(
        self, latitude: float, longitude: float, days: int = 5, units: str = "metric"
    ) -> Optional[ForecastData]:
        """
        Get weather forecast for specific coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days for forecast
            units: Temperature units

        Returns:
            ForecastData or None if error
        """
        pass


class IAsyncWeatherAPI(ABC):
    """Interface for async weather API services."""

    @abstractmethod
    async def get_current_weather(
        self, city: str, units: str = "metric"
    ) -> Optional[WeatherData]:
        """
        Get current weather for a city asynchronously.

        Args:
            city: City name
            units: Temperature units (metric, imperial, standard)

        Returns:
            WeatherData or None if error
        """
        pass

    @abstractmethod
    async def get_forecast(
        self, city: str, days: int = 5, units: str = "metric"
    ) -> Optional[ForecastData]:
        """
        Get weather forecast for a city asynchronously.

        Args:
            city: City name
            days: Number of days for forecast
            units: Temperature units

        Returns:
            ForecastData or None if error
        """
        pass

    @abstractmethod
    async def search_locations(self, query: str, limit: int = 5) -> List[LocationData]:
        """
        Search for locations by name asynchronously.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of LocationData
        """
        pass

    @abstractmethod
    async def get_current_weather_by_coordinates(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> Optional[WeatherData]:
        """
        Get current weather for specific coordinates asynchronously.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Temperature units (metric, imperial, standard)

        Returns:
            WeatherData or None if error
        """
        pass

    @abstractmethod
    async def get_forecast_by_coordinates(
        self, latitude: float, longitude: float, days: int = 5, units: str = "metric"
    ) -> Optional[ForecastData]:
        """
        Get weather forecast for specific coordinates asynchronously.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days for forecast
            units: Temperature units

        Returns:
            ForecastData or None if error
        """
        pass


class IDataStorage(ABC):
    """Interface for data storage services."""

    @abstractmethod
    def save_data(self, data: Dict[str, Any], filename: str) -> bool:
        """Save data to storage."""
        pass

    @abstractmethod
    def load_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load data from storage."""
        pass

    @abstractmethod
    def delete_data(self, filename: str) -> bool:
        """Delete data from storage."""
        pass


class ICacheService(ABC):
    """Interface for caching services."""

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set cached value with TTL."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete cached value."""
        pass

    @abstractmethod
    def clear(self) -> bool:
        """Clear all cached values."""
        pass

    def get_cache_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments."""
        key_parts = [str(prefix)]
        key_parts.extend(str(arg) for arg in args)
        return ":".join(key_parts)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": 0,
            "active_entries": 0,
            "expired_entries": 0,
            "cache_keys": [],
        }


class IUserInterface(ABC):
    """Interface for user interface components."""

    @abstractmethod
    def display_weather(self, weather_data: WeatherData) -> None:
        """Display current weather data."""
        pass

    @abstractmethod
    def display_forecast(self, forecast_data: ForecastData) -> None:
        """Display forecast data."""
        pass

    @abstractmethod
    def get_user_input(self, prompt: str) -> str:
        """Get input from user."""
        pass

    @abstractmethod
    def show_error(self, message: str) -> None:
        """Show error message to user."""
        pass

    @abstractmethod
    def show_message(self, message: str) -> None:
        """Show message to user."""
        pass

    @abstractmethod
    def display_weather_poem(self, poem) -> None:
        """Display weather poem."""
        pass
