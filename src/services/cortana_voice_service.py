#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cortana Voice Assistant Service for Weather Dashboard

This service integrates the Cortana voice assistant with the Weather Dashboard
application, providing voice-based weather queries and responses using
Bot Framework-inspired patterns and advanced NLU capabilities.
"""

import asyncio
import logging
import os
import sys
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from ..business.interfaces import ICacheService, ICortanaVoiceService, IStorageService
from ..interfaces.weather_interfaces import IWeatherAPI
from ..models.weather_models import CurrentWeather, WeatherForecast
from .voice_command_processor import CommandResponse, VoiceCommandProcessor

# Add configs directory to path for importing ConfigManager
sys.path.append(str(Path(__file__).parent.parent.parent / "configs" / "cortana"))

try:
    from config_manager import ConfigManager
except ImportError:
    logging.warning(
        "Cortana ConfigManager not available. Voice features will be disabled."
    )
    ConfigManager = None


class CortanaVoiceService(ICortanaVoiceService):
    """Cortana Voice Assistant Service for Weather Dashboard with Bot Framework patterns."""

    def __init__(
        self,
        weather_service: Optional[IWeatherAPI] = None,
        cache_service: Optional[ICacheService] = None,
        storage_service: Optional[IStorageService] = None,
    ):
        """Initialize the Cortana voice service.

        Args:
            weather_service: Weather service for fetching weather data
            cache_service: Cache service for performance optimization
            storage_service: Storage service for user preferences
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # Services
        self.weather_service = weather_service
        self.cache_service = cache_service
        self.storage_service = storage_service

        # Configuration
        self.config_manager: Optional[ConfigManager] = None
        self.config: Dict[str, Any] = {}
        self.is_enabled = False

        # Voice processing
        self.command_processor = VoiceCommandProcessor(
            weather_service=weather_service,
            cache_service=cache_service,
            storage_service=storage_service,
        )

        # Voice profiles and settings
        self.available_voice_profiles = [
            "en-US_Standard",
            "en-US_Neural",
            "en-GB_Standard",
            "en-AU_Standard",
            "en-CA_Standard",
        ]
        self.current_voice_profile = "en-US_Standard"

        # Speech synthesis settings
        self.speech_rate = 1.0
        self.speech_volume = 0.8
        self.speech_pitch = 0.0

        # Legacy command mappings for backward compatibility
        self.voice_commands: Dict[str, Callable] = {}

        # Initialize Cortana configuration
        self._initialize_cortana_config()

        # Setup voice commands
        self._setup_voice_commands()

        self.logger.info(
            f"Cortana Voice Service initialized (enabled: {self.is_enabled})"
        )

    def _initialize_cortana_config(self) -> None:
        """Initialize Cortana configuration."""
        if ConfigManager is None:
            self.logger.warning("ConfigManager not available. Voice features disabled.")
            return

        try:
            self.config_manager = ConfigManager()
            self.config = self.config_manager.config

            # Validate configuration
            if self.config_manager.validate():
                self.is_enabled = True
                self.logger.info(
                    "Cortana configuration loaded and validated successfully"
                )
            else:
                self.logger.error("Cortana configuration validation failed")
                self.logger.error(
                    f"Validation errors: {self.config_manager.validation_errors}"
                )

        except Exception as e:
            self.logger.error(f"Failed to initialize Cortana configuration: {e}")

    def _setup_voice_commands(self) -> None:
        """Setup voice command mappings."""
        self.voice_commands = {
            "get_weather": self._handle_weather_query,
            "get_forecast": self._handle_forecast_query,
            "get_temperature": self._handle_temperature_query,
            "get_humidity": self._handle_humidity_query,
            "get_wind": self._handle_wind_query,
            "help": self._handle_help_query,
            "status": self._handle_status_query,
        }

    def is_voice_enabled(self) -> bool:
        """Check if voice functionality is enabled.

        Returns:
            bool: True if voice is enabled, False otherwise
        """
        return self.is_enabled and self.config_manager is not None

    def get_voice_profile(self) -> str:
        """Get the current voice profile.

        Returns:
            str: Voice profile name
        """
        if not self.is_voice_enabled():
            return "disabled"

        # Use current voice profile or fall back to config
        return self.current_voice_profile or self.config.get("voice", {}).get(
            "profile", "en-US_Standard"
        )

    def get_personality_traits(self) -> List[str]:
        """Get the personality traits for responses.

        Returns:
            List[str]: List of personality traits
        """
        if not self.is_voice_enabled():
            return []

        return self.config.get("personality", {}).get(
            "traits", ["helpful", "curious", "witty"]
        )

    async def process_voice_command(
        self, command: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process a voice command and return a response.

        Args:
            command: Voice command to process
            context: Optional conversation context

        Returns:
            str: Response text
        """
        if not self.is_voice_enabled():
            return "Voice assistant is not available. Please check the configuration."

        try:
            # Use the advanced command processor
            response = await self.command_processor.process_command(command, context)

            # Log the interaction
            self.logger.info(
                f"Processed command: '{command}' -> Success: {response.success}"
            )

            # Format response with suggestions if available
            message = response.message
            if response.suggestions and not response.success:
                message += "\n\nSuggestions: " + ", ".join(response.suggestions)

            return message

        except Exception as e:
            self.logger.error(f"Error processing voice command '{command}': {e}")
            return "I'm sorry, I encountered an error processing your request. Please try again."

    def process_voice_command_sync(
        self, command: str, city: Optional[str] = None
    ) -> str:
        """Synchronous wrapper for voice command processing (backward compatibility).

        Args:
            command: Voice command to process
            city: Optional city name for weather queries

        Returns:
            str: Response text
        """
        context = {"city": city} if city else None

        # Run async method in event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an event loop, create a task
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run, self.process_voice_command(command, context)
                    )
                    return future.result(timeout=10)
            else:
                return loop.run_until_complete(
                    self.process_voice_command(command, context)
                )
        except Exception as e:
            self.logger.error(f"Error in sync voice command processing: {e}")
            return asyncio.run(self.process_voice_command(command, context))

    def _handle_weather_query(self, city: Optional[str] = None) -> str:
        """Handle weather query command.

        Args:
            city: City name for weather query

        Returns:
            str: Weather response
        """
        if not city:
            return "Please specify a city name for the weather query."

        if not self.weather_service:
            return "Weather service is not available."

        try:
            weather = self.weather_service.get_current_weather(city)
            if weather:
                return self._format_weather_response(weather)
            else:
                return f"I couldn't find weather information for {city}. Please check the city name."
        except Exception as e:
            self.logger.error(f"Error fetching weather for {city}: {e}")
            return f"I'm sorry, I couldn't get the weather for {city} right now."

    def _handle_forecast_query(self, city: Optional[str] = None) -> str:
        """Handle forecast query command.

        Args:
            city: City name for forecast query

        Returns:
            str: Forecast response
        """
        if not city:
            return "Please specify a city name for the forecast query."

        if not self.weather_service:
            return "Weather service is not available."

        try:
            forecast = self.weather_service.get_forecast(city)
            if forecast:
                return self._format_forecast_response(forecast)
            else:
                return f"I couldn't find forecast information for {city}. Please check the city name."
        except Exception as e:
            self.logger.error(f"Error fetching forecast for {city}: {e}")
            return f"I'm sorry, I couldn't get the forecast for {city} right now."

    def _handle_temperature_query(self, city: Optional[str] = None) -> str:
        """Handle temperature query command.

        Args:
            city: City name for temperature query

        Returns:
            str: Temperature response
        """
        if not city:
            return "Please specify a city name for the temperature query."

        if not self.weather_service:
            return "Weather service is not available."

        try:
            weather = self.weather_service.get_current_weather(city)
            if weather:
                temp = weather.temperature
                feels_like = weather.feels_like
                return f"The temperature in {city} is {temp}°C, and it feels like {feels_like}°C."
            else:
                return f"I couldn't find temperature information for {city}."
        except Exception as e:
            self.logger.error(f"Error fetching temperature for {city}: {e}")
            return f"I'm sorry, I couldn't get the temperature for {city} right now."

    def _handle_humidity_query(self, city: Optional[str] = None) -> str:
        """Handle humidity query command.

        Args:
            city: City name for humidity query

        Returns:
            str: Humidity response
        """
        if not city:
            return "Please specify a city name for the humidity query."

        if not self.weather_service:
            return "Weather service is not available."

        try:
            weather = self.weather_service.get_current_weather(city)
            if weather:
                humidity = weather.humidity
                return f"The humidity in {city} is {humidity}%."
            else:
                return f"I couldn't find humidity information for {city}."
        except Exception as e:
            self.logger.error(f"Error fetching humidity for {city}: {e}")
            return f"I'm sorry, I couldn't get the humidity for {city} right now."

    def _handle_wind_query(self, city: Optional[str] = None) -> str:
        """Handle wind query command.

        Args:
            city: City name for wind query

        Returns:
            str: Wind response
        """
        if not city:
            return "Please specify a city name for the wind query."

        if not self.weather_service:
            return "Weather service is not available."

        try:
            weather = self.weather_service.get_current_weather(city)
            if weather:
                wind_speed = weather.wind_speed
                wind_direction = getattr(weather, "wind_direction", "unknown")
                return (
                    f"The wind in {city} is {wind_speed} m/s from the {wind_direction}."
                )
            else:
                return f"I couldn't find wind information for {city}."
        except Exception as e:
            self.logger.error(f"Error fetching wind information for {city}: {e}")
            return (
                f"I'm sorry, I couldn't get the wind information for {city} right now."
            )

    def _handle_help_query(self, city: Optional[str] = None) -> str:
        """Handle help query command.

        Returns:
            str: Help response
        """
        return self._generate_help_response()

    def _handle_status_query(self, city: Optional[str] = None) -> str:
        """Handle status query command.

        Returns:
            str: Status response
        """
        if not self.is_voice_enabled():
            return "Cortana voice assistant is currently disabled."

        voice_profile = self.get_voice_profile()
        personality = ", ".join(self.get_personality_traits())
        privacy_mode = (
            "enabled"
            if self.config.get("privacy", {}).get("enable_privacy_mode", False)
            else "disabled"
        )

        return (
            f"Cortana voice assistant is active. "
            f"Voice profile: {voice_profile}. "
            f"Personality: {personality}. "
            f"Privacy mode: {privacy_mode}."
        )

    def _format_weather_response(self, weather: CurrentWeather) -> str:
        """Format weather data into a natural language response.

        Args:
            weather: Current weather data

        Returns:
            str: Formatted weather response
        """
        personality = self.get_personality_traits()

        # Base response
        response = (
            f"The weather in {weather.location.name} is {weather.description}. "
            f"The temperature is {weather.temperature}°C, feeling like {weather.feels_like}°C. "
            f"Humidity is {weather.humidity}%, and wind speed is {weather.wind_speed} m/s."
        )

        # Add personality-based additions
        if "witty" in personality:
            if weather.temperature > 30:
                response += " It's quite toasty out there!"
            elif weather.temperature < 0:
                response += " Brrr, it's freezing!"
            elif "rain" in weather.description.lower():
                response += " Don't forget your umbrella!"

        if "helpful" in personality:
            if weather.humidity > 80:
                response += " It's quite humid, so you might feel warmer than the actual temperature."
            elif weather.wind_speed > 10:
                response += " It's quite windy, so dress accordingly."

        return response

    def _format_forecast_response(self, forecast: WeatherForecast) -> str:
        """Format forecast data into a natural language response.

        Args:
            forecast: Weather forecast data

        Returns:
            str: Formatted forecast response
        """
        if not forecast.daily_forecasts:
            return "I couldn't get the forecast information."

        # Get first few days of forecast
        days = forecast.daily_forecasts[:3]  # First 3 days

        response = f"Here's the forecast for {forecast.location.name}: "

        for i, day in enumerate(days):
            day_name = (
                ["Today", "Tomorrow", "Day after tomorrow"][i]
                if i < 3
                else f"Day {i+1}"
            )
            response += (
                f"{day_name}: {day.description}, "
                f"high of {day.max_temp}°C, low of {day.min_temp}°C. "
            )

        return response.strip()

    def _generate_help_response(self) -> str:
        """Generate help response with available commands.

        Returns:
            str: Help response
        """
        commands = [
            "get weather for [city]",
            "get forecast for [city]",
            "get temperature for [city]",
            "get humidity for [city]",
            "get wind for [city]",
            "help",
            "status",
        ]

        response = "I can help you with weather information. Here are some commands you can try: "
        response += ", ".join(commands)
        response += ". Just say the command followed by a city name."

        return response

    # ICortanaVoiceService interface implementation

    async def speech_to_text(self, audio_data: bytes) -> str:
        """Convert speech audio to text.

        Args:
            audio_data: Audio data in bytes

        Returns:
            Recognized text
        """
        # Placeholder implementation - in a real scenario, this would integrate
        # with Azure Speech Services or another STT provider
        self.logger.warning("Speech-to-text not implemented - returning placeholder")
        return "placeholder recognized text"

    async def text_to_speech(self, text: str) -> bytes:
        """Convert text to speech audio.

        Args:
            text: Text to convert to speech

        Returns:
            Audio data in bytes
        """
        # Placeholder implementation - in a real scenario, this would integrate
        # with Azure Speech Services or another TTS provider
        self.logger.info(f"Text-to-speech request: '{text[:50]}...'")
        return b"placeholder audio data"

    def get_available_voice_profiles(self) -> List[str]:
        """Get list of available voice profiles.

        Returns:
            List of voice profile names
        """
        return self.available_voice_profiles.copy()

    async def configure_voice_settings(self, settings: Dict[str, Any]) -> bool:
        """Configure voice settings.

        Args:
            settings: Voice settings dictionary

        Returns:
            True if configuration was successful
        """
        try:
            if "voice_profile" in settings:
                profile = settings["voice_profile"]
                if profile in self.available_voice_profiles:
                    self.current_voice_profile = profile
                    self.logger.info(f"Voice profile changed to: {profile}")
                else:
                    self.logger.warning(f"Invalid voice profile: {profile}")
                    return False

            if "speech_rate" in settings:
                rate = float(settings["speech_rate"])
                if 0.5 <= rate <= 2.0:
                    self.speech_rate = rate
                else:
                    self.logger.warning(f"Invalid speech rate: {rate}")
                    return False

            if "speech_volume" in settings:
                volume = float(settings["speech_volume"])
                if 0.0 <= volume <= 1.0:
                    self.speech_volume = volume
                else:
                    self.logger.warning(f"Invalid speech volume: {volume}")
                    return False

            if "speech_pitch" in settings:
                pitch = float(settings["speech_pitch"])
                if -1.0 <= pitch <= 1.0:
                    self.speech_pitch = pitch
                else:
                    self.logger.warning(f"Invalid speech pitch: {pitch}")
                    return False

            # Store settings if storage service is available
            if self.storage_service:
                await self.storage_service.store_user_preference_async(
                    "voice_settings",
                    {
                        "voice_profile": self.current_voice_profile,
                        "speech_rate": self.speech_rate,
                        "speech_volume": self.speech_volume,
                        "speech_pitch": self.speech_pitch,
                    },
                )

            return True

        except Exception as e:
            self.logger.error(f"Error configuring voice settings: {e}")
            return False

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current Cortana configuration.

        Returns:
            Dict[str, Any]: Configuration summary
        """
        if not self.is_voice_enabled():
            return {"enabled": False, "reason": "Configuration not available"}

        return {
            "enabled": True,
            "voice_profile": self.current_voice_profile,
            "personality_traits": self.get_personality_traits(),
            "privacy_mode": self.config.get("privacy", {}).get(
                "enable_privacy_mode", False
            ),
            "log_level": self.config.get("logging", {}).get("level", "INFO"),
            "environment": self.config.get("deployment", {}).get("environment", "dev"),
            "last_validated": self.config.get("validation", {}).get(
                "last_validated", "never"
            ),
            "validation_status": self.config.get("validation", {}).get(
                "validation_status", "unknown"
            ),
            "speech_settings": {
                "rate": self.speech_rate,
                "volume": self.speech_volume,
                "pitch": self.speech_pitch,
            },
            "available_profiles": self.available_voice_profiles,
        }

    def reload_configuration(self) -> bool:
        """Reload the Cortana configuration.

        Returns:
            bool: True if reload was successful, False otherwise
        """
        try:
            self._initialize_cortana_config()
            self.logger.info("Cortana configuration reloaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reload Cortana configuration: {e}")
            return False

    def set_default_location(self, location: str) -> None:
        """Set default location for voice commands.

        Args:
            location: Default location name
        """
        self.command_processor.set_default_location(location)
        self.logger.info(f"Default location set to: {location}")

    def get_voice_help(self) -> str:
        """Get voice command help text.

        Returns:
            Help text for voice commands
        """
        return self._generate_help_response()

    async def get_conversation_context(self) -> Dict[str, Any]:
        """Get current conversation context.

        Returns:
            Conversation context dictionary
        """
        return self.command_processor.get_conversation_context()

    async def clear_conversation_context(self) -> None:
        """Clear conversation context."""
        self.command_processor.clear_conversation_context()


# Factory function for creating Cortana voice service
def create_cortana_voice_service(
    weather_service: Optional[IWeatherAPI] = None,
    cache_service: Optional[ICacheService] = None,
    storage_service: Optional[IStorageService] = None,
) -> CortanaVoiceService:
    """Create and return a Cortana voice service instance.

    Args:
        weather_service: Weather service for fetching weather data
        cache_service: Cache service for performance optimization
        storage_service: Storage service for user preferences

    Returns:
        CortanaVoiceService: Configured Cortana voice service
    """
    return CortanaVoiceService(
        weather_service=weather_service,
        cache_service=cache_service,
        storage_service=storage_service,
    )
