#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cortana Voice Assistant Service for Weather Dashboard

This service integrates the Cortana voice assistant with the Weather Dashboard
application, providing voice-based weather queries and responses.
"""

import logging
import os
import sys
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# Add configs directory to path for importing ConfigManager
sys.path.append(str(Path(__file__).parent.parent.parent / "configs" / "cortana"))

try:
    from config_manager import ConfigManager
except ImportError:
    logging.warning("Cortana ConfigManager not available. Voice features will be disabled.")
    ConfigManager = None

from ..models.weather_models import CurrentWeather, WeatherForecast
from ..interfaces.weather_interfaces import IWeatherAPI


class CortanaVoiceService:
    """Cortana Voice Assistant Service for Weather Dashboard."""
    
    def __init__(self, weather_service: Optional[IWeatherAPI] = None):
        """Initialize the Cortana voice service.
        
        Args:
            weather_service: Weather service for fetching weather data
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.weather_service = weather_service
        self.config_manager: Optional[ConfigManager] = None
        self.config: Dict[str, Any] = {}
        self.is_enabled = False
        self.voice_commands: Dict[str, Callable] = {}
        
        # Initialize Cortana configuration
        self._initialize_cortana_config()
        
        # Setup voice commands
        self._setup_voice_commands()
        
        self.logger.info(f"Cortana Voice Service initialized (enabled: {self.is_enabled})")
    
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
                self.logger.info("Cortana configuration loaded and validated successfully")
            else:
                self.logger.error("Cortana configuration validation failed")
                self.logger.error(f"Validation errors: {self.config_manager.validation_errors}")
                
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
        
        return self.config.get("voice", {}).get("profile", "en-US_Standard")
    
    def get_personality_traits(self) -> List[str]:
        """Get the personality traits for responses.
        
        Returns:
            List[str]: List of personality traits
        """
        if not self.is_voice_enabled():
            return []
        
        return self.config.get("personality", {}).get("traits", ["helpful", "curious", "witty"])
    
    def process_voice_command(self, command: str, city: Optional[str] = None) -> str:
        """Process a voice command and return a response.
        
        Args:
            command: Voice command to process
            city: Optional city name for weather queries
            
        Returns:
            str: Response text
        """
        if not self.is_voice_enabled():
            return "Voice assistant is not available. Please check the configuration."
        
        command = command.lower().strip()
        
        # Find matching command
        for cmd_key, handler in self.voice_commands.items():
            if cmd_key.replace("_", " ") in command or cmd_key in command:
                try:
                    return handler(city)
                except Exception as e:
                    self.logger.error(f"Error processing voice command '{command}': {e}")
                    return "I'm sorry, I encountered an error processing your request."
        
        # Default response for unrecognized commands
        return self._generate_help_response()
    
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
                wind_direction = getattr(weather, 'wind_direction', 'unknown')
                return f"The wind in {city} is {wind_speed} m/s from the {wind_direction}."
            else:
                return f"I couldn't find wind information for {city}."
        except Exception as e:
            self.logger.error(f"Error fetching wind information for {city}: {e}")
            return f"I'm sorry, I couldn't get the wind information for {city} right now."
    
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
        privacy_mode = "enabled" if self.config.get("privacy", {}).get("enable_privacy_mode", False) else "disabled"
        
        return (f"Cortana voice assistant is active. "
                f"Voice profile: {voice_profile}. "
                f"Personality: {personality}. "
                f"Privacy mode: {privacy_mode}.")
    
    def _format_weather_response(self, weather: CurrentWeather) -> str:
        """Format weather data into a natural language response.
        
        Args:
            weather: Current weather data
            
        Returns:
            str: Formatted weather response
        """
        personality = self.get_personality_traits()
        
        # Base response
        response = (f"The weather in {weather.location.name} is {weather.description}. "
                   f"The temperature is {weather.temperature}°C, feeling like {weather.feels_like}°C. "
                   f"Humidity is {weather.humidity}%, and wind speed is {weather.wind_speed} m/s.")
        
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
            day_name = ["Today", "Tomorrow", "Day after tomorrow"][i] if i < 3 else f"Day {i+1}"
            response += (f"{day_name}: {day.description}, "
                        f"high of {day.max_temp}°C, low of {day.min_temp}°C. ")
        
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
            "status"
        ]
        
        response = "I can help you with weather information. Here are some commands you can try: "
        response += ", ".join(commands)
        response += ". Just say the command followed by a city name."
        
        return response
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get a summary of the current Cortana configuration.
        
        Returns:
            Dict[str, Any]: Configuration summary
        """
        if not self.is_voice_enabled():
            return {"enabled": False, "reason": "Configuration not available"}
        
        return {
            "enabled": True,
            "voice_profile": self.get_voice_profile(),
            "personality_traits": self.get_personality_traits(),
            "privacy_mode": self.config.get("privacy", {}).get("enable_privacy_mode", False),
            "log_level": self.config.get("logging", {}).get("level", "INFO"),
            "environment": self.config.get("deployment", {}).get("environment", "dev"),
            "last_validated": self.config.get("validation", {}).get("last_validated", "never"),
            "validation_status": self.config.get("validation", {}).get("validation_status", "unknown")
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


# Factory function for creating Cortana voice service
def create_cortana_voice_service(weather_service: Optional[IWeatherAPI] = None) -> CortanaVoiceService:
    """Create and return a Cortana voice service instance.
    
    Args:
        weather_service: Weather service for fetching weather data
        
    Returns:
        CortanaVoiceService: Configured Cortana voice service
    """
    return CortanaVoiceService(weather_service=weather_service)