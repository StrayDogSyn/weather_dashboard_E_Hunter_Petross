"""Unit tests for the PoetryService.

This module contains comprehensive tests for the poetry generation service,
including tests for caching, AI generation, template fallback, and error handling.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.services.poetry_service import (
    PoetryService,
    PoetryCache,
    AzureOpenAIPoetryGenerator,
    TemplatePoetryGenerator,
    create_poetry_service
)
from src.interfaces.poetry_interfaces import (
    PoetryRequest,
    PoetryResponse,
    PoetryStyle,
    PoetryMood,
    PoetryGenerationConfig
)
from src.core.exceptions import ServiceError, ValidationError


class TestPoetryCache:
    """Test cases for PoetryCache."""

    @pytest.fixture
    def cache(self):
        """Create a poetry cache instance."""
        return PoetryCache(max_size=10, ttl_minutes=1)

    @pytest.fixture
    def sample_request(self):
        """Create a sample poetry request."""
        return PoetryRequest(
            location="Test City",
            weather_condition="sunny",
            temperature=25.0,
            style=PoetryStyle.HAIKU,
            mood=PoetryMood.JOYFUL
        )

    @pytest.fixture
    def sample_response(self):
        """Create a sample poetry response."""
        return PoetryResponse(
            poem="Test haiku here\nWith beautiful imagery\nNature's gift to us",
            style=PoetryStyle.HAIKU,
            mood=PoetryMood.JOYFUL,
            location="Test City",
            weather_condition="sunny",
            temperature=25.0,
            generated_at=datetime.now(),
            generator="test",
            metadata={"test": True}
        )

    @pytest.mark.asyncio
    async def test_cache_miss(self, cache, sample_request):
        """Test cache miss scenario."""
        result = await cache.get(sample_request)
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_hit(self, cache, sample_request, sample_response):
        """Test cache hit scenario."""
        # Set cache entry
        await cache.set(sample_request, sample_response)

        # Retrieve from cache
        result = await cache.get(sample_request)

        assert result is not None
        assert result.poem == sample_response.poem
        assert result.style == sample_response.style
        assert result.location == sample_response.location

    @pytest.mark.asyncio
    async def test_cache_expiry(self, sample_request, sample_response):
        """Test cache entry expiry."""
        # Create cache with very short TTL
        cache = PoetryCache(max_size=10, ttl_minutes=0.01)  # ~0.6 seconds

        # Set cache entry
        await cache.set(sample_request, sample_response)

        # Should hit immediately
        result = await cache.get(sample_request)
        assert result is not None

        # Wait for expiry
        await asyncio.sleep(1)

        # Should miss after expiry
        result = await cache.get(sample_request)
        assert result is None

    @pytest.mark.asyncio
    async def test_cache_lru_eviction(self, cache, sample_response):
        """Test LRU eviction when cache is full."""
        # Fill cache to capacity
        for i in range(10):
            request = PoetryRequest(
                location=f"City {i}",
                weather_condition="sunny",
                temperature=25.0,
                style=PoetryStyle.HAIKU,
                mood=PoetryMood.JOYFUL
            )
            await cache.set(request, sample_response)

        # Add one more entry (should evict oldest)
        new_request = PoetryRequest(
            location="New City",
            weather_condition="sunny",
            temperature=25.0,
            style=PoetryStyle.HAIKU,
            mood=PoetryMood.JOYFUL
        )
        await cache.set(new_request, sample_response)

        # First entry should be evicted
        first_request = PoetryRequest(
            location="City 0",
            weather_condition="sunny",
            temperature=25.0,
            style=PoetryStyle.HAIKU,
            mood=PoetryMood.JOYFUL
        )
        result = await cache.get(first_request)
        assert result is None

        # New entry should be present
        result = await cache.get(new_request)
        assert result is not None

    @pytest.mark.asyncio
    async def test_cache_clear(self, cache, sample_request, sample_response):
        """Test cache clearing."""
        # Set cache entry
        await cache.set(sample_request, sample_response)

        # Verify entry exists
        result = await cache.get(sample_request)
        assert result is not None

        # Clear cache
        await cache.clear()

        # Verify entry is gone
        result = await cache.get(sample_request)
        assert result is None


class TestTemplatePoetryGenerator:
    """Test cases for TemplatePoetryGenerator."""

    @pytest.fixture
    def generator(self):
        """Create a template poetry generator."""
        return TemplatePoetryGenerator()

    @pytest.fixture
    def sample_request(self):
        """Create a sample poetry request."""
        return PoetryRequest(
            location="Test City",
            weather_condition="clear",
            temperature=25.0,
            style=PoetryStyle.HAIKU,
            mood=PoetryMood.JOYFUL
        )

    @pytest.mark.asyncio
    async def test_generate_haiku(self, generator, sample_request):
        """Test haiku generation from templates."""
        response = await generator.generate_poem(sample_request)

        assert response.poem is not None
        assert len(response.poem) > 0
        assert response.style == PoetryStyle.HAIKU
        assert response.generator == "template"
        assert response.metadata["template_used"] is True

    @pytest.mark.asyncio
    async def test_generate_limerick(self, generator):
        """Test limerick generation from templates."""
        request = PoetryRequest(
            location="Test City",
            weather_condition="clear",
            temperature=25.0,
            style=PoetryStyle.LIMERICK,
            mood=PoetryMood.JOYFUL
        )

        response = await generator.generate_poem(request)

        assert response.poem is not None
        assert len(response.poem) > 0
        assert response.style == PoetryStyle.LIMERICK
        assert response.generator == "template"

    @pytest.mark.asyncio
    async def test_fallback_poem(self, generator):
        """Test fallback poem generation for unknown conditions."""
        request = PoetryRequest(
            location="Test City",
            weather_condition="unknown_condition",
            temperature=25.0,
            style=PoetryStyle.FREE_VERSE,
            mood=PoetryMood.JOYFUL
        )

        response = await generator.generate_poem(request)

        assert response.poem is not None
        assert len(response.poem) > 0
        assert "Test City" in response.poem


class TestAzureOpenAIPoetryGenerator:
    """Test cases for AzureOpenAIPoetryGenerator."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return PoetryGenerationConfig(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_key="test-key",
            model_name="gpt-4",
            temperature=0.7,
            max_tokens=200
        )

    @pytest.fixture
    def sample_request(self):
        """Create a sample poetry request."""
        return PoetryRequest(
            location="Test City",
            weather_condition="sunny",
            temperature=25.0,
            style=PoetryStyle.HAIKU,
            mood=PoetryMood.JOYFUL
        )

    def test_invalid_config(self):
        """Test generator creation with invalid config."""
        with pytest.raises(ValidationError):
            AzureOpenAIPoetryGenerator(PoetryGenerationConfig(
                azure_openai_endpoint="",
                azure_openai_key=""
            ))

    @pytest.mark.asyncio
    @patch('src.services.poetry_service.AsyncAzureOpenAI')
    async def test_successful_generation(self, mock_client_class, config, sample_request):
        """Test successful poem generation."""
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        # Mock the response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Beautiful haiku\nGenerated by AI model\nWeather poetry"
        mock_response.usage.total_tokens = 50

        mock_client.chat.completions.create.return_value = mock_response

        # Create generator and test
        generator = AzureOpenAIPoetryGenerator(config)
        response = await generator.generate_poem(sample_request)

        assert response.poem == "Beautiful haiku\nGenerated by AI model\nWeather poetry"
        assert response.generator == "azure_openai"
        assert response.metadata["tokens_used"] == 50

    @pytest.mark.asyncio
    @patch('src.services.poetry_service.AsyncAzureOpenAI')
    async def test_api_error_handling(self, mock_client_class, config, sample_request):
        """Test API error handling."""
        # Mock the OpenAI client to raise an error
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client

        from openai import APIError
        mock_client.chat.completions.create.side_effect = APIError("API Error")

        # Create generator and test
        generator = AzureOpenAIPoetryGenerator(config)

        with pytest.raises(ServiceError):
            await generator.generate_poem(sample_request)


class TestPoetryService:
    """Test cases for PoetryService."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return PoetryGenerationConfig(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_key="test-key",
            model_name="gpt-4",
            use_ai_generation=True
        )

    @pytest.fixture
    def service(self, config):
        """Create a poetry service instance."""
        return PoetryService(config)

    @pytest.fixture
    def sample_request(self):
        """Create a sample poetry request."""
        return PoetryRequest(
            location="Test City",
            weather_condition="sunny",
            temperature=25.0,
            style=PoetryStyle.HAIKU,
            mood=PoetryMood.JOYFUL
        )

    def test_request_validation(self, service):
        """Test request validation."""
        # Test empty location
        with pytest.raises(ValidationError, match="Location is required"):
            service._validate_request(PoetryRequest(
                location="",
                weather_condition="sunny",
                temperature=25.0,
                style=PoetryStyle.HAIKU,
                mood=PoetryMood.JOYFUL
            ))

        # Test invalid temperature
        with pytest.raises(ValidationError, match="Temperature must be between"):
            service._validate_request(PoetryRequest(
                location="Test City",
                weather_condition="sunny",
                temperature=150.0,
                style=PoetryStyle.HAIKU,
                mood=PoetryMood.JOYFUL
            ))

    @pytest.mark.asyncio
    async def test_generate_multiple_poems_validation(self, service, sample_request):
        """Test validation for multiple poem generation."""
        with pytest.raises(ValidationError, match="Count must be between 1 and 10"):
            await service.generate_multiple_poems(sample_request, count=0)

        with pytest.raises(ValidationError, match="Count must be between 1 and 10"):
            await service.generate_multiple_poems(sample_request, count=15)

    @pytest.mark.asyncio
    @patch('src.services.poetry_service.AzureOpenAIPoetryGenerator')
    async def test_ai_generation_with_fallback(self, mock_ai_generator_class, service, sample_request):
        """Test AI generation with template fallback."""
        # Mock AI generator to fail
        mock_ai_generator = AsyncMock()
        mock_ai_generator.generate_poem.side_effect = ServiceError("AI failed")
        mock_ai_generator_class.return_value = mock_ai_generator

        # Should fallback to template generation
        response = await service.generate_poetry(sample_request)

        assert response is not None
        assert response.generator == "template"

    @pytest.mark.asyncio
    async def test_cache_integration(self, service, sample_request):
        """Test caching integration."""
        # Mock both generators to return predictable results
        with patch.object(service.ai_generator, 'generate_poem') as mock_ai, \
             patch.object(service.template_generator, 'generate_poem'):

            mock_response = PoetryResponse(
                poem="Test poem",
                style=sample_request.style,
                mood=sample_request.mood,
                location=sample_request.location,
                weather_condition=sample_request.weather_condition,
                temperature=sample_request.temperature,
                generated_at=datetime.now(),
                generator="test",
                metadata={}
            )

            mock_ai.return_value = mock_response

            # First call should generate
            response1 = await service.generate_poetry(sample_request)
            assert mock_ai.called

            # Reset mock
            mock_ai.reset_mock()

            # Second call should use cache
            response2 = await service.generate_poetry(sample_request)
            assert not mock_ai.called  # Should not call AI again
            assert response1.poem == response2.poem


class TestFactoryFunction:
    """Test cases for the factory function."""

    def test_create_poetry_service(self):
        """Test poetry service creation via factory function."""
        service = create_poetry_service(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_key="test-key",
            model_name="gpt-4",
            use_ai_generation=True
        )

        assert isinstance(service, PoetryService)
        assert service.config.azure_openai_endpoint == "https://test.openai.azure.com/"
        assert service.config.azure_openai_key == "test-key"
        assert service.config.model_name == "gpt-4"
        assert service.config.use_ai_generation is True


# Integration test
class TestPoetryServiceIntegration:
    """Integration tests for the complete poetry service."""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_end_to_end_template_generation(self):
        """Test end-to-end poetry generation using templates only."""
        # Create service without AI
        service = create_poetry_service(
            azure_openai_endpoint="https://test.openai.azure.com/",
            azure_openai_key="test-key",
            use_ai_generation=False
        )

        request = PoetryRequest(
            location="Integration Test City",
            weather_condition="clear",
            temperature=22.0,
            style=PoetryStyle.HAIKU,
            mood=PoetryMood.PEACEFUL
        )

        response = await service.generate_poetry(request)

        assert response is not None
        assert response.poem is not None
        assert len(response.poem) > 0
        assert response.generator == "template"
        assert response.location == request.location
        assert response.style == request.style
        assert response.mood == request.mood


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
