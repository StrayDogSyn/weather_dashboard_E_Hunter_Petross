"""Interfaces for poetry generation services."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from src.models.weather_models import WeatherData


class PoetryStyle(Enum):
    """Available poetry styles for weather-based generation."""

    HAIKU = "haiku"
    SONNET = "sonnet"
    FREE_VERSE = "free_verse"
    LIMERICK = "limerick"
    WEATHER_REPORT = "weather_report"
    INSPIRATIONAL = "inspirational"


class PoetryMood(Enum):
    """Mood settings for poetry generation."""

    CHEERFUL = "cheerful"
    MELANCHOLIC = "melancholic"
    DRAMATIC = "dramatic"
    PEACEFUL = "peaceful"
    ENERGETIC = "energetic"
    ROMANTIC = "romantic"
    HUMOROUS = "humorous"


@dataclass
class PoetryRequest:
    """Request configuration for poetry generation."""

    weather_data: WeatherData
    style: PoetryStyle = PoetryStyle.FREE_VERSE
    mood: PoetryMood = PoetryMood.PEACEFUL
    max_lines: Optional[int] = None
    include_weather_details: bool = True
    custom_theme: Optional[str] = None
    language: str = "en"


@dataclass
class PoetryResponse:
    """Generated poetry response with metadata."""

    poem: str
    title: str
    style: PoetryStyle
    mood: PoetryMood
    weather_location: str
    generation_time: float
    word_count: int
    line_count: int
    metadata: Dict[str, Any]


@dataclass
class PoetryGenerationConfig:
    """Configuration for poetry generation service."""

    api_key: str
    endpoint: Optional[str] = None
    model_name: str = "gpt-4"
    max_tokens: int = 500
    temperature: float = 0.8
    top_p: float = 0.9
    frequency_penalty: float = 0.3
    presence_penalty: float = 0.3
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


class IPoetryGenerator(ABC):
    """Interface for AI-powered poetry generation services."""

    @abstractmethod
    async def generate_poem(self, request: PoetryRequest) -> Optional[PoetryResponse]:
        """Generate a poem based on weather data and style preferences.

        Args:
            request: Poetry generation request with weather data and preferences

        Returns:
            Generated poetry response or None if generation fails

        Raises:
            PoetryGenerationError: If generation fails after retries
            ValidationError: If request parameters are invalid
        """
        pass

    @abstractmethod
    async def generate_weather_haiku(self, weather_data: WeatherData) -> Optional[str]:
        """Generate a simple haiku for weather data.

        Args:
            weather_data: Current weather information

        Returns:
            Generated haiku as string or None if generation fails
        """
        pass

    @abstractmethod
    async def get_available_styles(self) -> List[PoetryStyle]:
        """Get list of supported poetry styles.

        Returns:
            List of available poetry styles
        """
        pass

    @abstractmethod
    async def validate_request(self, request: PoetryRequest) -> bool:
        """Validate poetry generation request.

        Args:
            request: Poetry generation request to validate

        Returns:
            True if request is valid, False otherwise
        """
        pass

    @abstractmethod
    async def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about poetry generation usage.

        Returns:
            Dictionary containing generation statistics
        """
        pass


class IPoetryCache(ABC):
    """Interface for caching generated poetry."""

    @abstractmethod
    async def get_cached_poem(
        self, weather_key: str, style: PoetryStyle, mood: PoetryMood
    ) -> Optional[PoetryResponse]:
        """Retrieve cached poem for weather conditions and style.

        Args:
            weather_key: Unique key representing weather conditions
            style: Poetry style
            mood: Poetry mood

        Returns:
            Cached poetry response or None if not found
        """
        pass

    @abstractmethod
    async def cache_poem(
        self,
        weather_key: str,
        style: PoetryStyle,
        mood: PoetryMood,
        response: PoetryResponse,
        ttl: int = 3600,
    ) -> bool:
        """Cache generated poem.

        Args:
            weather_key: Unique key representing weather conditions
            style: Poetry style
            mood: Poetry mood
            response: Poetry response to cache
            ttl: Time to live in seconds

        Returns:
            True if caching successful, False otherwise
        """
        pass

    @abstractmethod
    async def clear_cache(self) -> bool:
        """Clear all cached poems.

        Returns:
            True if clearing successful, False otherwise
        """
        pass


class IPoetryService(ABC):
    """High-level interface for poetry service operations."""

    @abstractmethod
    async def create_weather_poem(
        self,
        weather_data: WeatherData,
        style: PoetryStyle = PoetryStyle.FREE_VERSE,
        mood: PoetryMood = PoetryMood.PEACEFUL,
        use_cache: bool = True,
    ) -> Optional[PoetryResponse]:
        """Create a weather-inspired poem.

        Args:
            weather_data: Current weather information
            style: Desired poetry style
            mood: Desired poetry mood
            use_cache: Whether to use cached results

        Returns:
            Generated poetry response or None if creation fails
        """
        pass

    @abstractmethod
    async def create_daily_weather_haiku(
        self, weather_data: WeatherData
    ) -> Optional[str]:
        """Create a simple daily weather haiku.

        Args:
            weather_data: Current weather information

        Returns:
            Generated haiku string or None if creation fails
        """
        pass

    @abstractmethod
    async def get_poem_history(
        self, location: Optional[str] = None, limit: int = 10
    ) -> List[PoetryResponse]:
        """Get history of generated poems.

        Args:
            location: Filter by location (optional)
            limit: Maximum number of poems to return

        Returns:
            List of previously generated poems
        """
        pass

    @abstractmethod
    async def save_favorite_poem(
        self, poem_id: str, user_notes: Optional[str] = None
    ) -> bool:
        """Save a poem as favorite.

        Args:
            poem_id: Unique identifier of the poem
            user_notes: Optional user notes about the poem

        Returns:
            True if saving successful, False otherwise
        """
        pass

    @abstractmethod
    async def get_favorite_poems(self) -> List[PoetryResponse]:
        """Get user's favorite poems.

        Returns:
            List of favorite poems
        """
        pass
