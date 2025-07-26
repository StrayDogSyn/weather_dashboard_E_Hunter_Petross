"""Business service interfaces for Weather Dashboard.

This module defines all the interfaces (contracts) for business services
following the Interface Segregation Principle and Dependency Inversion Principle.
"""

from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Tuple


class IWeatherService(ABC):
    """Interface for weather-related operations."""

    @abstractmethod
    async def get_current_weather(
        self, city: str, country: str = None
    ) -> Dict[str, Any]:
        """Get current weather for a city.

        Args:
            city: City name
            country: Optional country code

        Returns:
            Dictionary containing current weather data
        """
        pass

    @abstractmethod
    async def get_weather_forecast(
        self, city: str, days: int = 7, country: str = None
    ) -> List[Dict[str, Any]]:
        """Get weather forecast for a city.

        Args:
            city: City name
            days: Number of forecast days
            country: Optional country code

        Returns:
            List of forecast data dictionaries
        """
        pass

    @abstractmethod
    async def search_cities(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for cities matching the query.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of city data dictionaries
        """
        pass

    @abstractmethod
    async def get_weather_by_coordinates(
        self, latitude: float, longitude: float
    ) -> Dict[str, Any]:
        """Get weather by geographic coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate

        Returns:
            Dictionary containing weather data
        """
        pass


class ICityComparisonService(ABC):
    """Interface for city comparison operations."""

    @abstractmethod
    async def compare_cities(
        self, cities: List[str], metrics: List[str] = None
    ) -> Dict[str, Any]:
        """Compare weather data between multiple cities.

        Args:
            cities: List of city names to compare
            metrics: Optional list of specific metrics to compare

        Returns:
            Dictionary containing comparison data
        """
        pass

    @abstractmethod
    async def get_comparison_history(
        self, cities: List[str], start_date: date, end_date: date
    ) -> Dict[str, Any]:
        """Get historical comparison data for cities.

        Args:
            cities: List of city names
            start_date: Start date for comparison
            end_date: End date for comparison

        Returns:
            Dictionary containing historical comparison data
        """
        pass

    @abstractmethod
    def get_available_metrics(self) -> List[str]:
        """Get list of available comparison metrics.

        Returns:
            List of metric names
        """
        pass


class IWeatherJournalService(ABC):
    """Interface for weather journal operations."""

    @abstractmethod
    async def create_entry(
        self, city: str, content: str, weather_data: Dict[str, Any] = None
    ) -> str:
        """Create a new journal entry.

        Args:
            city: City name for the entry
            content: Journal entry content
            weather_data: Optional weather data to associate

        Returns:
            Entry ID
        """
        pass

    @abstractmethod
    async def get_entry(self, entry_id: str) -> Dict[str, Any]:
        """Get a journal entry by ID.

        Args:
            entry_id: Entry identifier

        Returns:
            Dictionary containing entry data
        """
        pass

    @abstractmethod
    async def get_entries_by_city(
        self, city: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get journal entries for a specific city.

        Args:
            city: City name
            limit: Maximum number of entries

        Returns:
            List of entry dictionaries
        """
        pass

    @abstractmethod
    async def get_entries_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Dict[str, Any]]:
        """Get journal entries within a date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of entry dictionaries
        """
        pass

    @abstractmethod
    async def update_entry(self, entry_id: str, content: str) -> bool:
        """Update a journal entry.

        Args:
            entry_id: Entry identifier
            content: New content

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a journal entry.

        Args:
            entry_id: Entry identifier

        Returns:
            True if successful
        """
        pass


class IActivitySuggestionService(ABC):
    """Interface for activity suggestion operations."""

    @abstractmethod
    async def get_suggestions(
        self, weather_data: Dict[str, Any], preferences: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Get activity suggestions based on weather.

        Args:
            weather_data: Current weather data
            preferences: Optional user preferences

        Returns:
            List of activity suggestion dictionaries
        """
        pass

    @abstractmethod
    async def get_suggestions_by_category(
        self, category: str, weather_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get activity suggestions for a specific category.

        Args:
            category: Activity category
            weather_data: Current weather data

        Returns:
            List of activity suggestion dictionaries
        """
        pass

    @abstractmethod
    def get_available_categories(self) -> List[str]:
        """Get list of available activity categories.

        Returns:
            List of category names
        """
        pass

    @abstractmethod
    async def rate_suggestion(self, suggestion_id: str, rating: int) -> bool:
        """Rate an activity suggestion.

        Args:
            suggestion_id: Suggestion identifier
            rating: Rating value (1-5)

        Returns:
            True if successful
        """
        pass


class IWeatherPoetryService(ABC):
    """Interface for weather poetry generation."""

    @abstractmethod
    async def generate_poem(
        self, weather_data: Dict[str, Any], style: str = "haiku"
    ) -> str:
        """Generate a poem based on weather data.

        Args:
            weather_data: Current weather data
            style: Poetry style (haiku, limerick, etc.)

        Returns:
            Generated poem text
        """
        pass

    @abstractmethod
    def get_available_styles(self) -> List[str]:
        """Get list of available poetry styles.

        Returns:
            List of style names
        """
        pass

    @abstractmethod
    async def save_poem(
        self, poem: str, weather_data: Dict[str, Any], style: str
    ) -> str:
        """Save a generated poem.

        Args:
            poem: Poem text
            weather_data: Associated weather data
            style: Poetry style

        Returns:
            Poem ID
        """
        pass

    @abstractmethod
    async def get_saved_poems(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get saved poems.

        Args:
            limit: Maximum number of poems

        Returns:
            List of poem dictionaries
        """
        pass


class ICortanaVoiceService(ABC):
    """Interface for Cortana voice assistant operations."""

    @abstractmethod
    async def process_voice_command(self, audio_data: bytes) -> Dict[str, Any]:
        """Process voice command and return response.

        Args:
            audio_data: Audio data bytes

        Returns:
            Dictionary containing command result
        """
        pass

    @abstractmethod
    async def text_to_speech(self, text: str, voice_profile: str = None) -> bytes:
        """Convert text to speech audio.

        Args:
            text: Text to convert
            voice_profile: Optional voice profile

        Returns:
            Audio data bytes
        """
        pass

    @abstractmethod
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech audio to text.

        Args:
            audio_data: Audio data bytes

        Returns:
            Transcribed text
        """
        pass

    @abstractmethod
    def get_available_voice_profiles(self) -> List[str]:
        """Get list of available voice profiles.

        Returns:
            List of voice profile names
        """
        pass

    @abstractmethod
    async def configure_voice_settings(self, settings: Dict[str, Any]) -> bool:
        """Configure voice assistant settings.

        Args:
            settings: Voice settings dictionary

        Returns:
            True if successful
        """
        pass


class ICacheService(ABC):
    """Interface for caching operations."""

    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries.

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        pass


class IStorageService(ABC):
    """Interface for data storage operations."""

    @abstractmethod
    async def save(self, collection: str, data: Dict[str, Any], key: str = None) -> str:
        """Save data to storage.

        Args:
            collection: Collection/table name
            data: Data to save
            key: Optional key for the data

        Returns:
            Data key/ID
        """
        pass

    @abstractmethod
    async def load(self, collection: str, key: str) -> Optional[Dict[str, Any]]:
        """Load data from storage.

        Args:
            collection: Collection/table name
            key: Data key/ID

        Returns:
            Loaded data or None if not found
        """
        pass

    @abstractmethod
    async def query(
        self, collection: str, filters: Dict[str, Any] = None, limit: int = None
    ) -> List[Dict[str, Any]]:
        """Query data from storage.

        Args:
            collection: Collection/table name
            filters: Optional query filters
            limit: Optional result limit

        Returns:
            List of matching data
        """
        pass

    @abstractmethod
    async def update(self, collection: str, key: str, data: Dict[str, Any]) -> bool:
        """Update data in storage.

        Args:
            collection: Collection/table name
            key: Data key/ID
            data: Updated data

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def delete(self, collection: str, key: str) -> bool:
        """Delete data from storage.

        Args:
            collection: Collection/table name
            key: Data key/ID

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    async def exists(self, collection: str, key: str) -> bool:
        """Check if data exists in storage.

        Args:
            collection: Collection/table name
            key: Data key/ID

        Returns:
            True if data exists
        """
        pass
