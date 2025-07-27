"""Voice Command Processor for Cortana Weather Assistant.

This module implements Bot Framework-inspired command processing patterns
for natural language weather queries and voice interactions.
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from ..business.interfaces import ICacheService, IStorageService, IWeatherService


class CommandType(Enum):
    """Voice command types."""

    WEATHER_CURRENT = "weather_current"
    WEATHER_FORECAST = "weather_forecast"
    WEATHER_HOURLY = "weather_hourly"
    LOCATION_SET = "location_set"
    HELP = "help"
    UNKNOWN = "unknown"


class ConfidenceLevel(Enum):
    """Command recognition confidence levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class VoiceCommand:
    """Structured voice command representation."""

    command_type: CommandType
    confidence: ConfidenceLevel
    parameters: Dict[str, Any]
    original_text: str
    processed_text: str
    entities: Dict[str, Any]


@dataclass
class CommandResponse:
    """Structured command response."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    follow_up_questions: Optional[List[str]] = None


class VoiceCommandProcessor:
    """Advanced voice command processor with NLU capabilities."""

    def __init__(
        self,
        weather_service: Optional[IWeatherService] = None,
        cache_service: Optional[ICacheService] = None,
        storage_service: Optional[IStorageService] = None,
    ):
        """Initialize voice command processor.

        Args:
            weather_service: Weather service for data retrieval
            cache_service: Cache service for performance optimization
            storage_service: Storage service for user preferences
        """
        self.logger = logging.getLogger(__name__)

        # Services
        self.weather_service = weather_service
        self.cache_service = cache_service
        self.storage_service = storage_service

        # Command patterns
        self.command_patterns = self._initialize_command_patterns()

        # Entity extractors
        self.entity_extractors = self._initialize_entity_extractors()

        # Default location
        self.default_location = "New York"

        # Conversation context
        self.conversation_context = {}

    def _initialize_command_patterns(self) -> Dict[CommandType, List[str]]:
        """Initialize command recognition patterns.

        Returns:
            Dictionary mapping command types to regex patterns
        """
        return {
            CommandType.WEATHER_CURRENT: [
                r"(?:what'?s|how'?s|tell me|get|show|check).*?(?:the )?(?:current )?weather.*?(?:in|for|at) ([\w\s,]+?)(?:\?|$|today|now|currently)",
                r"(?:weather|temperature|conditions?).*?(?:in|for|at) ([\w\s,]+?)(?:\?|$|today|now|currently)",
                r"(?:current|today'?s|right now) weather.*?(?:in|for|at) ([\w\s,]+?)(?:\?|$)",
                r"(?:what'?s|how'?s) (?:the )?(?:weather|temperature) (?:like )?(?:in|for|at) ([\w\s,]+?)(?:\?|$)",
                r"(?:is it|will it be) (?:hot|cold|warm|cool|sunny|rainy|cloudy|snowy) (?:in|at) ([\w\s,]+?)(?:\?|$)",
            ],
            CommandType.WEATHER_FORECAST: [
                r"(?:what'?s|how'?s|tell me|get|show|check).*?(?:the )?(?:weather )?forecast.*?(?:in|for|at) ([\w\s,]+?)(?:\?|$)",
                r"(?:forecast|prediction).*?(?:in|for|at) ([\w\s,]+?)(?:\?|$)",
                r"(?:tomorrow|next \d+ days?|this week|weekend) weather.*?(?:in|for|at) ([\w\s,]+?)(?:\?|$)",
                r"(?:will it|is it going to) (?:rain|snow|be sunny|be cloudy) (?:tomorrow|this week) (?:in|at) ([\w\s,]+?)(?:\?|$)",
            ],
            CommandType.WEATHER_HOURLY: [
                r"(?:hourly|hour by hour) (?:weather|forecast).*?(?:in|for|at) ([\w\s,]+?)(?:\?|$)",
                r"(?:weather|forecast) (?:for )?(?:the )?(?:next|coming) (?:few )?hours?.*?(?:in|for|at) ([\w\s,]+?)(?:\?|$)",
                r"(?:what'?s|how'?s) (?:the )?weather (?:going to be )?(?:for )?(?:the )?(?:next|coming) hours?.*?(?:in|for|at) ([\w\s,]+?)(?:\?|$)",
            ],
            CommandType.LOCATION_SET: [
                r"(?:set|change|update) (?:my )?(?:location|city) to ([\w\s,]+?)(?:\?|$)",
                r"(?:i'?m|i am) (?:in|at|from) ([\w\s,]+?)(?:\?|$)",
                r"(?:my location is|i live in) ([\w\s,]+?)(?:\?|$)",
            ],
            CommandType.HELP: [
                r"(?:help|what can you do|commands?|how to use)",
                r"(?:what|how) (?:can|do) (?:i|you) (?:ask|say|do)(?:\?|$)",
                r"(?:show|list) (?:commands?|options|help)(?:\?|$)",
            ],
        }

    def _initialize_entity_extractors(self) -> Dict[str, callable]:
        """Initialize entity extraction functions.

        Returns:
            Dictionary mapping entity types to extraction functions
        """
        return {
            "location": self._extract_location,
            "time": self._extract_time,
            "weather_condition": self._extract_weather_condition,
            "temperature_unit": self._extract_temperature_unit,
        }

    async def process_command(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> CommandResponse:
        """Process voice command with advanced NLU.

        Args:
            text: Voice command text
            context: Optional conversation context

        Returns:
            Structured command response
        """
        try:
            # Update conversation context
            if context:
                self.conversation_context.update(context)

            # Parse and classify command
            command = await self._parse_command(text)

            # Log command processing
            self.logger.info(
                f"Processing command: {command.command_type.value} with confidence {command.confidence.value}"
            )

            # Route to appropriate handler
            response = await self._route_command(command)

            # Cache successful responses
            if response.success and self.cache_service:
                cache_key = f"voice_command:{hash(text)}"
                await self.cache_service.set_async(
                    cache_key, response, ttl=300
                )  # 5 minutes

            return response

        except Exception as e:
            self.logger.error(f"Error processing voice command '{text}': {e}")
            return CommandResponse(
                success=False,
                message="I'm sorry, I encountered an error processing your request. Please try again.",
                suggestions=[
                    "Try rephrasing your question",
                    "Check your internet connection",
                ],
            )

    async def _parse_command(self, text: str) -> VoiceCommand:
        """Parse and classify voice command.

        Args:
            text: Raw voice command text

        Returns:
            Structured voice command
        """
        # Normalize text
        processed_text = self._normalize_text(text)

        # Extract entities
        entities = await self._extract_entities(processed_text)

        # Classify command type
        command_type, confidence, parameters = await self._classify_command(
            processed_text, entities
        )

        return VoiceCommand(
            command_type=command_type,
            confidence=confidence,
            parameters=parameters,
            original_text=text,
            processed_text=processed_text,
            entities=entities,
        )

    def _normalize_text(self, text: str) -> str:
        """Normalize input text for processing.

        Args:
            text: Raw input text

        Returns:
            Normalized text
        """
        # Convert to lowercase
        text = text.lower().strip()

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Handle common contractions
        contractions = {
            "what's": "what is",
            "how's": "how is",
            "it's": "it is",
            "i'm": "i am",
            "won't": "will not",
            "can't": "cannot",
            "don't": "do not",
            "isn't": "is not",
            "aren't": "are not",
            "wasn't": "was not",
            "weren't": "were not",
            "haven't": "have not",
            "hasn't": "has not",
            "hadn't": "had not",
            "wouldn't": "would not",
            "shouldn't": "should not",
            "couldn't": "could not",
        }

        for contraction, expansion in contractions.items():
            text = text.replace(contraction, expansion)

        return text

    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract entities from normalized text.

        Args:
            text: Normalized text

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        for entity_type, extractor in self.entity_extractors.items():
            try:
                entity_value = extractor(text)
                if entity_value:
                    entities[entity_type] = entity_value
            except Exception as e:
                self.logger.warning(f"Error extracting {entity_type}: {e}")

        return entities

    async def _classify_command(
        self, text: str, entities: Dict[str, Any]
    ) -> Tuple[CommandType, ConfidenceLevel, Dict[str, Any]]:
        """Classify command type and extract parameters.

        Args:
            text: Normalized text
            entities: Extracted entities

        Returns:
            Tuple of (command_type, confidence, parameters)
        """
        best_match = None
        best_confidence = ConfidenceLevel.LOW
        best_parameters = {}

        for command_type, patterns in self.command_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Calculate confidence based on match quality
                    confidence = self._calculate_confidence(text, pattern, match)

                    # Extract parameters from match groups
                    parameters = self._extract_parameters(match, entities)

                    # Update best match if this is better
                    if self._is_better_match(confidence, best_confidence):
                        best_match = command_type
                        best_confidence = confidence
                        best_parameters = parameters

        return best_match or CommandType.UNKNOWN, best_confidence, best_parameters

    def _calculate_confidence(
        self, text: str, pattern: str, match: re.Match
    ) -> ConfidenceLevel:
        """Calculate confidence level for pattern match.

        Args:
            text: Input text
            pattern: Matched pattern
            match: Regex match object

        Returns:
            Confidence level
        """
        # Calculate match coverage
        match_length = len(match.group(0))
        text_length = len(text)
        coverage = match_length / text_length

        # Determine confidence based on coverage and specificity
        if coverage > 0.8:
            return ConfidenceLevel.HIGH
        elif coverage > 0.5:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW

    def _is_better_match(
        self, new_confidence: ConfidenceLevel, current_confidence: ConfidenceLevel
    ) -> bool:
        """Determine if new match is better than current best.

        Args:
            new_confidence: New match confidence
            current_confidence: Current best confidence

        Returns:
            True if new match is better
        """
        confidence_order = [
            ConfidenceLevel.LOW,
            ConfidenceLevel.MEDIUM,
            ConfidenceLevel.HIGH,
        ]
        return confidence_order.index(new_confidence) > confidence_order.index(
            current_confidence
        )

    def _extract_parameters(
        self, match: re.Match, entities: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract parameters from regex match and entities.

        Args:
            match: Regex match object
            entities: Extracted entities

        Returns:
            Dictionary of extracted parameters
        """
        parameters = {}

        # Extract location from match groups
        if match.groups():
            location = match.group(1).strip()
            if location:
                parameters["location"] = self._clean_location(location)

        # Add entities as parameters
        parameters.update(entities)

        # Use default location if none specified
        if "location" not in parameters:
            parameters["location"] = self.default_location

        return parameters

    def _clean_location(self, location: str) -> str:
        """Clean and normalize location string.

        Args:
            location: Raw location string

        Returns:
            Cleaned location string
        """
        # Remove common trailing words
        trailing_words = ["please", "today", "now", "currently", "right now"]
        for word in trailing_words:
            if location.lower().endswith(f" {word}"):
                location = location[: -len(f" {word}")]

        # Capitalize properly
        return location.title().strip()

    # Entity extraction methods
    def _extract_location(self, text: str) -> Optional[str]:
        """Extract location from text.

        Args:
            text: Input text

        Returns:
            Extracted location or None
        """
        # Common location patterns
        patterns = [
            r"(?:in|for|at) ([\w\s,]+?)(?:\s|$|\?|today|now|currently)",
            r"([\w\s,]+?) weather",
            r"weather (?:in|for|at) ([\w\s,]+?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 1:  # Avoid single characters
                    return self._clean_location(location)

        return None

    def _extract_time(self, text: str) -> Optional[str]:
        """Extract time reference from text.

        Args:
            text: Input text

        Returns:
            Extracted time reference or None
        """
        time_patterns = [
            r"(today|now|currently|right now)",
            r"(tomorrow|next day)",
            r"(this week|next week|weekend)",
            r"(next \d+ days?)",
            r"(hourly|hour by hour|next (?:few )?hours?)",
        ]

        for pattern in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).lower()

        return None

    def _extract_weather_condition(self, text: str) -> Optional[str]:
        """Extract weather condition from text.

        Args:
            text: Input text

        Returns:
            Extracted weather condition or None
        """
        conditions = [
            "sunny",
            "cloudy",
            "rainy",
            "snowy",
            "stormy",
            "foggy",
            "hot",
            "cold",
            "warm",
            "cool",
            "humid",
            "dry",
            "clear",
            "overcast",
            "partly cloudy",
            "mostly sunny",
        ]

        for condition in conditions:
            if condition in text.lower():
                return condition

        return None

    def _extract_temperature_unit(self, text: str) -> Optional[str]:
        """Extract temperature unit from text.

        Args:
            text: Input text

        Returns:
            Extracted temperature unit or None
        """
        if "celsius" in text.lower() or "°c" in text.lower():
            return "celsius"
        elif "fahrenheit" in text.lower() or "°f" in text.lower():
            return "fahrenheit"
        elif "kelvin" in text.lower() or "k" in text.lower():
            return "kelvin"

        return None

    async def _route_command(self, command: VoiceCommand) -> CommandResponse:
        """Route command to appropriate handler.

        Args:
            command: Parsed voice command

        Returns:
            Command response
        """
        handlers = {
            CommandType.WEATHER_CURRENT: self._handle_current_weather,
            CommandType.WEATHER_FORECAST: self._handle_weather_forecast,
            CommandType.WEATHER_HOURLY: self._handle_hourly_weather,
            CommandType.LOCATION_SET: self._handle_location_set,
            CommandType.HELP: self._handle_help,
            CommandType.UNKNOWN: self._handle_unknown,
        }

        handler = handlers.get(command.command_type, self._handle_unknown)
        return await handler(command)

    async def _handle_current_weather(self, command: VoiceCommand) -> CommandResponse:
        """Handle current weather request.

        Args:
            command: Voice command

        Returns:
            Command response
        """
        if not self.weather_service:
            return CommandResponse(
                success=False,
                message="Weather service is not available.",
                suggestions=["Check your internet connection", "Try again later"],
            )

        location = command.parameters.get("location", self.default_location)

        try:
            # Get current weather data
            weather_data = await self.weather_service.get_current_weather_async(
                location
            )

            if not weather_data:
                return CommandResponse(
                    success=False,
                    message=f"I couldn't find weather information for {location}. Please check the location name.",
                    suggestions=[
                        "Try a different city name",
                        "Include country or state",
                    ],
                )

            # Format response message
            message = self._format_current_weather_response(weather_data, location)

            return CommandResponse(
                success=True,
                message=message,
                data=weather_data,
                follow_up_questions=[
                    f"Would you like the forecast for {location}?",
                    "Do you want hourly weather updates?",
                ],
            )

        except Exception as e:
            self.logger.error(f"Error getting current weather for {location}: {e}")
            return CommandResponse(
                success=False,
                message=f"I encountered an error getting weather for {location}. Please try again.",
                suggestions=["Check the location name", "Try again in a moment"],
            )

    async def _handle_weather_forecast(self, command: VoiceCommand) -> CommandResponse:
        """Handle weather forecast request.

        Args:
            command: Voice command

        Returns:
            Command response
        """
        if not self.weather_service:
            return CommandResponse(
                success=False, message="Weather service is not available."
            )

        location = command.parameters.get("location", self.default_location)

        try:
            # Get forecast data
            forecast_data = await self.weather_service.get_forecast_async(location)

            if not forecast_data:
                return CommandResponse(
                    success=False,
                    message=f"I couldn't find forecast information for {location}.",
                )

            # Format response message
            message = self._format_forecast_response(forecast_data, location)

            return CommandResponse(success=True, message=message, data=forecast_data)

        except Exception as e:
            self.logger.error(f"Error getting forecast for {location}: {e}")
            return CommandResponse(
                success=False,
                message=f"I encountered an error getting the forecast for {location}.",
            )

    async def _handle_hourly_weather(self, command: VoiceCommand) -> CommandResponse:
        """Handle hourly weather request.

        Args:
            command: Voice command

        Returns:
            Command response
        """
        location = command.parameters.get("location", self.default_location)

        # For now, redirect to current weather with hourly context
        return CommandResponse(
            success=True,
            message=f"Hourly weather for {location} is not yet available. Here's the current weather instead.",
            suggestions=["Ask for current weather", "Ask for the forecast"],
        )

    async def _handle_location_set(self, command: VoiceCommand) -> CommandResponse:
        """Handle location setting request.

        Args:
            command: Voice command

        Returns:
            Command response
        """
        location = command.parameters.get("location")

        if not location:
            return CommandResponse(
                success=False,
                message="I didn't understand which location you want to set. Please try again.",
                suggestions=[
                    "Say 'set my location to New York'",
                    "Try 'I'm in London'",
                ],
            )

        # Update default location
        self.default_location = location

        # Store in user preferences if storage service is available
        if self.storage_service:
            try:
                await self.storage_service.store_user_preference_async(
                    "default_location", location
                )
            except Exception as e:
                self.logger.warning(f"Failed to store location preference: {e}")

        return CommandResponse(
            success=True,
            message=f"I've set your location to {location}. I'll use this for weather queries.",
            follow_up_questions=[f"Would you like the current weather for {location}?"],
        )

    async def _handle_help(self, command: VoiceCommand) -> CommandResponse:
        """Handle help request.

        Args:
            command: Voice command

        Returns:
            Command response
        """
        help_message = (
            "I'm your weather assistant! Here's what you can ask me:\n\n"
            "• Current weather: 'What's the weather in New York?'\n"
            "• Forecast: 'Show me the forecast for London'\n"
            "• Set location: 'Set my location to Paris'\n"
            "• General queries: 'Is it raining in Tokyo?'\n\n"
            "You can speak naturally - I'll understand!"
        )

        return CommandResponse(
            success=True,
            message=help_message,
            suggestions=[
                "Ask about weather in your city",
                "Set your default location",
                "Get a weather forecast",
            ],
        )

    async def _handle_unknown(self, command: VoiceCommand) -> CommandResponse:
        """Handle unknown command.

        Args:
            command: Voice command

        Returns:
            Command response
        """
        return CommandResponse(
            success=False,
            message="I'm not sure what you're asking for. I can help with weather information.",
            suggestions=[
                "Ask about current weather",
                "Request a weather forecast",
                "Say 'help' for more options",
            ],
        )

    def _format_current_weather_response(
        self, weather_data: Dict[str, Any], location: str
    ) -> str:
        """Format current weather response message.

        Args:
            weather_data: Weather data dictionary
            location: Location name

        Returns:
            Formatted response message
        """
        try:
            temp = weather_data.get("temperature", "Unknown")
            condition = weather_data.get("condition", "Unknown")
            humidity = weather_data.get("humidity", "Unknown")
            wind_speed = weather_data.get("wind_speed", "Unknown")

            message = f"The current weather in {location} is {condition} with a temperature of {temp}°F."

            if humidity != "Unknown":
                message += f" Humidity is {humidity}%."

            if wind_speed != "Unknown":
                message += f" Wind speed is {wind_speed} mph."

            return message

        except Exception as e:
            self.logger.error(f"Error formatting weather response: {e}")
            return f"I found weather information for {location}, but had trouble formatting it."

    def _format_forecast_response(
        self, forecast_data: Dict[str, Any], location: str
    ) -> str:
        """Format forecast response message.

        Args:
            forecast_data: Forecast data dictionary
            location: Location name

        Returns:
            Formatted response message
        """
        try:
            # Extract forecast information
            days = forecast_data.get("forecast", [])

            if not days:
                return (
                    f"I found forecast data for {location}, but it appears to be empty."
                )

            message = f"Here's the forecast for {location}:\n\n"

            for i, day in enumerate(days[:3]):  # Show first 3 days
                date = day.get("date", f"Day {i+1}")
                high = day.get("high_temp", "Unknown")
                low = day.get("low_temp", "Unknown")
                condition = day.get("condition", "Unknown")

                message += f"{date}: {condition}, High {high}°F, Low {low}°F\n"

            return message.strip()

        except Exception as e:
            self.logger.error(f"Error formatting forecast response: {e}")
            return f"I found forecast information for {location}, but had trouble formatting it."

    def set_default_location(self, location: str) -> None:
        """Set default location for commands.

        Args:
            location: Default location name
        """
        self.default_location = location
        self.logger.info(f"Default location set to: {location}")

    def get_conversation_context(self) -> Dict[str, Any]:
        """Get current conversation context.

        Returns:
            Conversation context dictionary
        """
        return self.conversation_context.copy()

    def clear_conversation_context(self) -> None:
        """Clear conversation context."""
        self.conversation_context.clear()
        self.logger.info("Conversation context cleared")
