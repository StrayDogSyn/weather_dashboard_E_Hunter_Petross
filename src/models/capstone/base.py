"""Base classes and core interfaces for capstone models."""

import json
import logging
from abc import ABC
from abc import abstractmethod
from dataclasses import asdict
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Protocol
from uuid import UUID

import google.generativeai as genai


class ModelProtocol(Protocol):
    """Protocol for all capstone models with common operations."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        ...

    def to_json(self) -> str:
        """Convert model to JSON string."""
        ...

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelProtocol":
        """Create model from dictionary."""
        ...

    def validate(self) -> bool:
        """Validate model data."""
        ...


class AIEnhancedModel(ABC):
    """Base class for models with AI enhancement capabilities."""

    def __init__(self):
        """Initialize AI-enhanced model."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._ai_cache = {}

    @abstractmethod
    def get_ai_prompt(self) -> str:
        """Generate AI prompt for content generation."""
        pass

    async def generate_ai_content(
        self, prompt: Optional[str] = None, model_name: str = "gemini-pro"
    ) -> str:
        """Generate AI content using Gemini."""
        try:
            if prompt is None:
                prompt = self.get_ai_prompt()

            # Check cache first
            cache_key = hash(prompt)
            if cache_key in self._ai_cache:
                self.logger.debug("Using cached AI response")
                return self._ai_cache[cache_key]

            # Generate content
            model = genai.GenerativeModel(model_name)
            response = await model.generate_content_async(prompt)

            if response and response.text:
                content = response.text.strip()
                self._ai_cache[cache_key] = content
                return content
            else:
                self.logger.warning("Empty response from AI model")
                return "AI content generation failed"

        except Exception as e:
            self.logger.error(f"AI content generation error: {e}")
            return f"Error generating content: {str(e)}"

    def clear_ai_cache(self):
        """Clear the AI response cache."""
        self._ai_cache.clear()


class ExtensibleEnum(Enum):
    """Base class for enums that can be dynamically extended."""

    @classmethod
    def add_value(cls, name: str, value: str) -> None:
        """Dynamically add a new enum value."""
        setattr(cls, name.upper(), value)

    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all enum values as strings."""
        return [item.value for item in cls]

    @classmethod
    def get_display_names(cls) -> Dict[str, str]:
        """Get human-readable display names."""
        return {item.name: item.value.replace("_", " ").title() for item in cls}

    def __str__(self) -> str:
        """String representation of enum value."""
        return self.value
