"""Poetry Service Implementation for Weather Dashboard.

This module provides an asynchronous poetry generation service that creates
weather-inspired poems using Azure OpenAI and other AI services.
"""

import asyncio
import logging
import random
from dataclasses import asdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import openai
from openai import AsyncAzureOpenAI

from ..interfaces.poetry_interfaces import (
    IPoetryCache,
    IPoetryGenerator,
    IPoetryService,
    PoetryGenerationConfig,
    PoetryMood,
    PoetryRequest,
    PoetryResponse,
    PoetryStyle,
)
from ..models.weather_models import CurrentWeather, WeatherCondition
from ..shared.exceptions import ServiceError, ValidationError


class PoetryCache(IPoetryCache):
    """In-memory cache implementation for poetry."""

    def __init__(self, max_size: int = 1000, ttl_minutes: int = 60):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._max_size = max_size
        self._ttl = timedelta(minutes=ttl_minutes)
        self.logger = logging.getLogger(__name__)

    def _generate_key(self, request: PoetryRequest) -> str:
        """Generate cache key from poetry request."""
        return f"{request.location}_{request.style.value}_{request.mood.value}_{request.weather_condition}"

    async def get(self, request: PoetryRequest) -> Optional[PoetryResponse]:
        """Get cached poetry response."""
        key = self._generate_key(request)

        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check if entry has expired
        if datetime.now() - entry["timestamp"] > self._ttl:
            del self._cache[key]
            return None

        self.logger.debug(f"Cache hit for key: {key}")
        return PoetryResponse(**entry["response"])

    async def set(self, request: PoetryRequest, response: PoetryResponse) -> None:
        """Cache poetry response."""
        key = self._generate_key(request)

        # Implement LRU eviction if cache is full
        if len(self._cache) >= self._max_size:
            oldest_key = min(
                self._cache.keys(), key=lambda k: self._cache[k]["timestamp"]
            )
            del self._cache[oldest_key]

        self._cache[key] = {"response": asdict(response), "timestamp": datetime.now()}

        self.logger.debug(f"Cached response for key: {key}")

    async def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self.logger.info("Poetry cache cleared")

    # Interface methods required by IPoetryCache
    async def get_cached_poem(
        self, weather_key: str, style: PoetryStyle, mood: PoetryMood
    ) -> Optional[PoetryResponse]:
        """Retrieve cached poem for weather conditions and style."""
        # Create a mock request to use existing get method
        from dataclasses import dataclass

        @dataclass
        class MockRequest:
            location: str = weather_key
            style: PoetryStyle = style
            mood: PoetryMood = mood
            weather_condition: str = ""

        return await self.get(MockRequest())

    async def cache_poem(
        self,
        weather_key: str,
        style: PoetryStyle,
        mood: PoetryMood,
        response: PoetryResponse,
        ttl: int = 3600,
    ) -> bool:
        """Cache generated poem."""
        try:
            from dataclasses import dataclass

            @dataclass
            class MockRequest:
                location: str = weather_key
                style: PoetryStyle = style
                mood: PoetryMood = mood
                weather_condition: str = ""

            await self.set(MockRequest(), response)
            return True
        except Exception as e:
            self.logger.error(f"Failed to cache poem: {e}")
            return False

    async def clear_cache(self) -> bool:
        """Clear all cached poems."""
        try:
            await self.clear()
            return True
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return False


class AzureOpenAIPoetryGenerator(IPoetryGenerator):
    """Azure OpenAI implementation for poetry generation."""

    def __init__(self, config: PoetryGenerationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize Azure OpenAI client
        if not hasattr(config, "azure_openai_endpoint") or not hasattr(
            config, "azure_openai_key"
        ):
            # Use fallback values for basic functionality
            self.client = None
            self.logger.warning(
                "Azure OpenAI credentials not configured, using template fallback"
            )
        else:
            self.client = AsyncAzureOpenAI(
                azure_endpoint=config.azure_openai_endpoint,
                api_key=config.azure_openai_key,
                api_version=getattr(
                    config, "azure_openai_api_version", "2024-02-15-preview"
                ),
            )

    async def generate_poem(self, request: PoetryRequest) -> PoetryResponse:
        """Generate a poem using Azure OpenAI."""
        if not self.client:
            raise ServiceError("Azure OpenAI client not configured")

        try:
            prompt = self._build_prompt(request)

            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(request.style),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.3,
            )

            if not response.choices or not response.choices[0].message.content:
                raise ServiceError("Empty response from Azure OpenAI")

            poem_text = response.choices[0].message.content.strip()

            return PoetryResponse(
                poem=poem_text,
                style=request.style,
                mood=request.mood,
                location=request.location,
                weather_condition=request.weather_condition,
                temperature=request.temperature,
                generated_at=datetime.now(),
                generator="azure_openai",
                metadata={
                    "model": self.config.model_name,
                    "temperature": self.config.temperature,
                    "tokens_used": response.usage.total_tokens if response.usage else 0,
                },
            )

        except openai.APIError as e:
            self.logger.error(f"Azure OpenAI API error: {e}")
            raise ServiceError(f"Poetry generation failed: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in poetry generation: {e}")
            raise ServiceError(f"Poetry generation failed: {e}")

    def _get_system_prompt(self, style: PoetryStyle) -> str:
        """Get system prompt based on poetry style."""
        prompts = {
            PoetryStyle.HAIKU: (
                "You are a master haiku poet specializing in weather-inspired poetry. "
                "Create beautiful haikus that follow the traditional 5-7-5 syllable pattern. "
                "Focus on capturing the essence and mood of weather conditions with vivid imagery."
            ),
            PoetryStyle.LIMERICK: (
                "You are a playful limerick writer who creates humorous weather-themed poems. "
                "Follow the AABBA rhyme scheme and create entertaining, light-hearted verses "
                "that bring joy and laughter while describing weather conditions."
            ),
            PoetryStyle.FREE_VERSE: (
                "You are a contemporary poet who writes expressive free verse about weather. "
                "Create flowing, emotional poetry without strict meter or rhyme constraints. "
                "Focus on vivid imagery and emotional resonance with weather phenomena."
            ),
            PoetryStyle.SONNET: (
                "You are a classical sonnet writer specializing in weather poetry. "
                "Create 14-line sonnets with proper rhyme scheme (Shakespearean or Petrarchan) "
                "that eloquently capture the beauty and power of weather conditions."
            ),
        }
        return prompts.get(style, prompts[PoetryStyle.FREE_VERSE])

    def _build_prompt(self, request: PoetryRequest) -> str:
        """Build the user prompt for poetry generation."""
        mood_descriptors = {
            PoetryMood.JOYFUL: "joyful and uplifting",
            PoetryMood.MELANCHOLIC: "melancholic and contemplative",
            PoetryMood.PEACEFUL: "peaceful and serene",
            PoetryMood.ENERGETIC: "energetic and vibrant",
            PoetryMood.MYSTERIOUS: "mysterious and enigmatic",
            PoetryMood.ROMANTIC: "romantic and tender",
        }

        prompt_parts = [
            f"Write a {request.style.value.replace('_', ' ')} about the weather in {request.location}.",
            f"Current conditions: {request.weather_condition}",
            f"Temperature: {request.temperature}°C",
            f"Mood: {mood_descriptors.get(request.mood, 'expressive')}",
        ]

        if request.additional_context:
            prompt_parts.append(f"Additional context: {request.additional_context}")

        prompt_parts.extend(
            [
                "\nMake the poem vivid, emotionally resonant, and true to the specified style.",
                "Return only the poem text, no additional commentary.",
            ]
        )

        return "\n".join(prompt_parts)

    # Additional interface methods required by IPoetryGenerator
    async def generate_weather_haiku(self, weather_data) -> Optional[str]:
        """Generate a simple haiku for weather data."""
        try:
            # Create a haiku request
            request = PoetryRequest(
                weather_data=weather_data,
                style=PoetryStyle.HAIKU,
                mood=PoetryMood.PEACEFUL,
            )
            response = await self.generate_poem(request)
            return response.poem if response else None
        except Exception as e:
            self.logger.error(f"Failed to generate haiku: {e}")
            return None

    async def get_available_styles(self) -> List[PoetryStyle]:
        """Get list of supported poetry styles."""
        return list(PoetryStyle)

    async def validate_request(self, request: PoetryRequest) -> bool:
        """Validate poetry generation request."""
        try:
            return (
                request.weather_data is not None
                and isinstance(request.style, PoetryStyle)
                and isinstance(request.mood, PoetryMood)
            )
        except Exception:
            return False

    async def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about poetry generation usage."""
        return {
            "generator_type": "azure_openai",
            "model_name": self.config.model_name,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "available_styles": [style.value for style in PoetryStyle],
            "available_moods": [mood.value for mood in PoetryMood],
        }


class TemplatePoetryGenerator(IPoetryGenerator):
    """Fallback template-based poetry generator."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_templates()

    def _load_templates(self):
        """Load poetry templates."""
        self.templates = {
            PoetryStyle.HAIKU: {
                "clear": [
                    "Bright sun overhead\nWarms the earth with golden rays\nPerfect day unfolds",
                    "Azure sky stretches\nNot a cloud to mar the view\nNature's masterpiece",
                ],
                "rain": [
                    "Gentle drops descend\nNourishing the thirsty earth\nLife begins anew",
                    "Rain taps on windows\nRhythmic song of nature's tears\nPeaceful melody",
                ],
                "snow": [
                    "Snowflakes dance and swirl\nBlanketing the world in white\nWinter's gentle touch",
                    "Silent snow falling\nTransforming the landscape pure\nMagic in the air",
                ],
            },
            PoetryStyle.LIMERICK: {
                "clear": [
                    "The sun in the sky shines so bright\nMaking everything bathed in light\nNot a cloud to be seen\nThe most beautiful scene\nA truly magnificent sight!"
                ],
                "rain": [
                    "The rain comes down with a patter\nMaking a rhythmical chatter\nEach drop is a gift\nGiving spirits a lift\nThough umbrellas do matter!"
                ],
            },
        }

    async def generate_poem(self, request: PoetryRequest) -> PoetryResponse:
        """Generate a poem using templates."""
        try:
            condition_key = request.weather_condition.lower()
            style_templates = self.templates.get(request.style, {})
            condition_templates = style_templates.get(
                condition_key, style_templates.get("clear", [])
            )

            if not condition_templates:
                # Generate a simple fallback
                poem_text = self._generate_fallback_poem(request)
            else:
                poem_text = random.choice(condition_templates)

            return PoetryResponse(
                poem=poem_text,
                style=request.style,
                mood=request.mood,
                location=request.location,
                weather_condition=request.weather_condition,
                temperature=request.temperature,
                generated_at=datetime.now(),
                generator="template",
                metadata={"template_used": True},
            )

        except Exception as e:
            self.logger.error(f"Template generation error: {e}")
            raise ServiceError(f"Template poetry generation failed: {e}")

    def _generate_fallback_poem(self, request: PoetryRequest) -> str:
        """Generate a simple fallback poem."""
        if request.style == PoetryStyle.HAIKU:
            return f"Weather in {request.location[:10]}\nBrings its own special beauty\nNature's gift to us"
        else:
            return (
                f"The weather in {request.location} today brings its own special charm."
            )

    # Additional interface methods required by IPoetryGenerator
    async def generate_weather_haiku(self, weather_data) -> Optional[str]:
        """Generate a simple haiku for weather data."""
        try:
            request = PoetryRequest(
                weather_data=weather_data,
                style=PoetryStyle.HAIKU,
                mood=PoetryMood.PEACEFUL,
            )
            response = await self.generate_poem(request)
            return response.poem if response else None
        except Exception as e:
            self.logger.error(f"Failed to generate haiku: {e}")
            return None

    async def get_available_styles(self) -> List[PoetryStyle]:
        """Get list of supported poetry styles."""
        return list(self.templates.keys())

    async def validate_request(self, request: PoetryRequest) -> bool:
        """Validate poetry generation request."""
        try:
            return (
                request.weather_data is not None
                and isinstance(request.style, PoetryStyle)
                and isinstance(request.mood, PoetryMood)
            )
        except Exception:
            return False

    async def get_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about poetry generation usage."""
        return {
            "generator_type": "template",
            "available_styles": list(self.templates.keys()),
            "template_count": sum(
                len(templates) for templates in self.templates.values()
            ),
        }


class PoetryService(IPoetryService):
    """Main poetry service implementation."""

    def __init__(self, config: PoetryGenerationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.cache = PoetryCache()
        self.ai_generator = AzureOpenAIPoetryGenerator(config)
        self.template_generator = TemplatePoetryGenerator()

        # Storage for poem history and favorites
        self._poem_history: List[PoetryResponse] = []
        self._favorite_poems: List[PoetryResponse] = []

    async def generate_poetry(self, request: PoetryRequest) -> PoetryResponse:
        """Generate weather-inspired poetry."""
        try:
            # Validate request
            self._validate_request(request)

            # Check cache first
            cached_response = await self.cache.get(request)
            if cached_response:
                self.logger.info(f"Returning cached poetry for {request.location}")
                return cached_response

            # Try AI generation first
            response = None
            use_ai = getattr(self.config, "use_ai_generation", False)
            if use_ai:
                try:
                    response = await self.ai_generator.generate_poem(request)
                    self.logger.info(f"Generated AI poetry for {request.location}")
                except ServiceError as e:
                    self.logger.warning(
                        f"AI generation failed, falling back to templates: {e}"
                    )

            # Fallback to template generation
            if not response:
                response = await self.template_generator.generate_poem(request)
                self.logger.info(f"Generated template poetry for {request.location}")

            # Cache the response
            await self.cache.set(request, response)

            return response

        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Poetry generation failed: {e}")
            raise ServiceError(f"Failed to generate poetry: {e}")

    async def generate_multiple_poems(
        self, request: PoetryRequest, count: int = 3
    ) -> List[PoetryResponse]:
        """Generate multiple poems with different styles."""
        if count <= 0 or count > 10:
            raise ValidationError("Count must be between 1 and 10")

        poems = []
        styles = list(PoetryStyle)

        for i in range(count):
            # Vary the style for each poem
            style = styles[i % len(styles)]
            poem_request = PoetryRequest(
                location=request.location,
                weather_condition=request.weather_condition,
                temperature=request.temperature,
                style=style,
                mood=request.mood,
                additional_context=request.additional_context,
            )

            try:
                poem = await self.generate_poetry(poem_request)
                poems.append(poem)
            except ServiceError as e:
                self.logger.warning(f"Failed to generate poem {i+1}: {e}")
                continue

        if not poems:
            raise ServiceError("Failed to generate any poems")

        return poems

    async def clear_cache(self) -> None:
        """Clear the poetry cache."""
        await self.cache.clear()
        self.logger.info("Poetry cache cleared")

    # Implementation of IPoetryService abstract methods
    async def create_weather_poem(
        self,
        weather_data,
        style: PoetryStyle = PoetryStyle.FREE_VERSE,
        mood: PoetryMood = PoetryMood.PEACEFUL,
        use_cache: bool = True,
    ) -> Optional[PoetryResponse]:
        """Create a weather-inspired poem."""
        try:
            # Convert weather_data to PoetryRequest
            request = PoetryRequest(
                location=getattr(weather_data, "location", "Unknown"),
                weather_condition=getattr(weather_data, "condition", "clear"),
                temperature=getattr(weather_data, "temperature", 20),
                style=style,
                mood=mood,
            )

            response = await self.generate_poetry(request)

            # Add to history
            self._poem_history.append(response)

            return response
        except Exception as e:
            self.logger.error(f"Failed to create weather poem: {e}")
            return None

    async def create_daily_weather_haiku(self, weather_data) -> Optional[str]:
        """Create a simple daily weather haiku."""
        try:
            request = PoetryRequest(
                location=getattr(weather_data, "location", "Unknown"),
                weather_condition=getattr(weather_data, "condition", "clear"),
                temperature=getattr(weather_data, "temperature", 20),
                style=PoetryStyle.HAIKU,
                mood=PoetryMood.PEACEFUL,
            )

            response = await self.generate_poetry(request)
            return response.poem if response else None
        except Exception as e:
            self.logger.error(f"Failed to create daily haiku: {e}")
            return None

    async def get_poem_history(
        self, location: Optional[str] = None, limit: int = 10
    ) -> List[PoetryResponse]:
        """Get history of generated poems."""
        history = self._poem_history

        # Filter by location if specified
        if location:
            history = [p for p in history if p.location.lower() == location.lower()]

        # Apply limit
        return history[-limit:] if limit > 0 else history

    async def save_favorite_poem(
        self, poem_id: str, user_notes: Optional[str] = None
    ) -> bool:
        """Save a poem as favorite."""
        try:
            # Find poem in history by ID (using generated_at as ID for simplicity)
            for poem in self._poem_history:
                if str(poem.generated_at) == poem_id:
                    # Add user notes to metadata if provided
                    if user_notes:
                        poem.metadata["user_notes"] = user_notes

                    # Add to favorites if not already there
                    if poem not in self._favorite_poems:
                        self._favorite_poems.append(poem)

                    self.logger.info(f"Saved poem as favorite: {poem_id}")
                    return True

            self.logger.warning(f"Poem not found for ID: {poem_id}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to save favorite poem: {e}")
            return False

    async def get_favorite_poems(self) -> List[PoetryResponse]:
        """Get user's favorite poems."""
        return self._favorite_poems.copy()

    def _validate_request(self, request: PoetryRequest) -> None:
        """Validate poetry request."""
        if not request.location or len(request.location.strip()) == 0:
            raise ValidationError("Location is required")

        if not request.weather_condition:
            raise ValidationError("Weather condition is required")

        if request.temperature is None:
            raise ValidationError("Temperature is required")

        if request.temperature < -100 or request.temperature > 100:
            raise ValidationError(
                "Temperature must be between -100 and 100 degrees Celsius"
            )


# Factory function for easy service creation
def create_poetry_service(
    azure_openai_endpoint: str,
    azure_openai_key: str,
    model_name: str = "gpt-4",
    use_ai_generation: bool = True,
) -> PoetryService:
    """Create a configured poetry service instance."""
    config = PoetryGenerationConfig(
        azure_openai_endpoint=azure_openai_endpoint,
        azure_openai_key=azure_openai_key,
        model_name=model_name,
        use_ai_generation=use_ai_generation,
    )
    return PoetryService(config)


# Alias for backward compatibility
WeatherPoetryService = PoetryService
