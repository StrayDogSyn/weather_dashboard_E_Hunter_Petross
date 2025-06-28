"""
Enhanced configuration management for the Weather Dashboard application.

This module provides a modern, type-safe configuration system with validation,
environment variable support, and proper error handling following security
best practices.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class APIConfiguration:
    """API configuration settings."""

    api_key: str = field(default_factory=lambda: os.getenv("OPENWEATHER_API_KEY", ""))
    base_url: str = "https://api.openweathermap.org/data/2.5"
    forecast_url: str = "https://api.openweathermap.org/data/2.5/forecast"
    geocoding_url: str = "https://api.openweathermap.org/geo/1.0"
    timeout: int = field(
        default_factory=lambda: int(os.getenv("WEATHER_API_TIMEOUT", "10"))
    )
    max_retries: int = field(
        default_factory=lambda: int(os.getenv("WEATHER_MAX_RETRIES", "3"))
    )
    rate_limit_per_minute: int = field(
        default_factory=lambda: int(os.getenv("WEATHER_RATE_LIMIT_PER_MINUTE", "60"))
    )

    # Alternative APIs for future expansion
    weatherapi_key: str = field(default_factory=lambda: os.getenv("WEATHERAPI_KEY", ""))
    visualcrossing_key: str = field(
        default_factory=lambda: os.getenv("VISUALCROSSING_API_KEY", "")
    )


@dataclass
class UIConfiguration:
    """UI configuration settings."""

    theme: str = field(default_factory=lambda: os.getenv("WEATHER_THEME", "darkly"))
    window_title: str = field(
        default_factory=lambda: os.getenv("WEATHER_WINDOW_TITLE", "🌤️ Weather Dashboard")
    )
    min_size: tuple = field(
        default_factory=lambda: _parse_size(os.getenv("WEATHER_MIN_SIZE", "800,600"))
    )
    default_size: tuple = field(
        default_factory=lambda: _parse_size(
            os.getenv("WEATHER_DEFAULT_SIZE", "1200,800")
        )
    )
    update_interval: int = field(
        default_factory=lambda: int(os.getenv("WEATHER_UPDATE_INTERVAL", "30000"))
    )
    enable_animations: bool = field(
        default_factory=lambda: os.getenv("WEATHER_ENABLE_ANIMATIONS", "true").lower()
        == "true"
    )


@dataclass
class DataConfiguration:
    """Data management configuration."""

    cache_enabled: bool = True
    cache_duration: int = field(
        default_factory=lambda: int(os.getenv("WEATHER_CACHE_DURATION", "300"))
    )
    auto_refresh: bool = field(
        default_factory=lambda: os.getenv("WEATHER_AUTO_REFRESH", "false").lower()
        == "true"
    )
    auto_refresh_interval: int = field(
        default_factory=lambda: int(os.getenv("WEATHER_AUTO_REFRESH_INTERVAL", "300"))
    )
    max_history_entries: int = field(
        default_factory=lambda: int(os.getenv("WEATHER_MAX_HISTORY_ENTRIES", "1000"))
    )
    export_format: str = field(
        default_factory=lambda: os.getenv("WEATHER_EXPORT_FORMAT", "json")
    )
    backup_enabled: bool = field(
        default_factory=lambda: os.getenv("WEATHER_BACKUP_ENABLED", "true").lower()
        == "true"
    )


@dataclass
class LoggingConfiguration:
    """Logging configuration settings."""

    log_level: str = field(
        default_factory=lambda: os.getenv("WEATHER_LOG_LEVEL", "INFO").upper()
    )
    log_to_file: bool = True
    log_to_console: bool = True
    max_log_size: int = 10  # MB
    log_retention_days: int = 30
    performance_logging: bool = field(
        default_factory=lambda: os.getenv("WEATHER_PERFORMANCE_LOGGING", "true").lower()
        == "true"
    )
    api_logging: bool = field(
        default_factory=lambda: os.getenv("WEATHER_API_LOGGING", "true").lower()
        == "true"
    )
    ui_logging: bool = field(
        default_factory=lambda: os.getenv("WEATHER_UI_LOGGING", "false").lower()
        == "true"
    )


@dataclass
class SecurityConfiguration:
    """Security configuration settings."""

    mask_api_keys: bool = field(
        default_factory=lambda: os.getenv("WEATHER_MASK_API_KEYS", "true").lower()
        == "true"
    )
    log_api_responses: bool = field(
        default_factory=lambda: os.getenv("WEATHER_LOG_API_RESPONSES", "false").lower()
        == "true"
    )
    privacy_mode: bool = field(
        default_factory=lambda: os.getenv("WEATHER_PRIVACY_MODE", "false").lower()
        == "true"
    )


@dataclass
class FeatureConfiguration:
    """Feature flags configuration."""

    enable_ml_predictions: bool = field(
        default_factory=lambda: os.getenv(
            "WEATHER_ENABLE_ML_PREDICTIONS", "false"
        ).lower()
        == "true"
    )
    enable_weather_alerts: bool = field(
        default_factory=lambda: os.getenv(
            "WEATHER_ENABLE_WEATHER_ALERTS", "true"
        ).lower()
        == "true"
    )
    enable_location_services: bool = field(
        default_factory=lambda: os.getenv(
            "WEATHER_ENABLE_LOCATION_SERVICES", "false"
        ).lower()
        == "true"
    )


@dataclass
class ApplicationConfiguration:
    """Main application configuration."""

    api: APIConfiguration = field(default_factory=APIConfiguration)
    ui: UIConfiguration = field(default_factory=UIConfiguration)
    data: DataConfiguration = field(default_factory=DataConfiguration)
    logging: LoggingConfiguration = field(default_factory=LoggingConfiguration)
    security: SecurityConfiguration = field(default_factory=SecurityConfiguration)
    features: FeatureConfiguration = field(default_factory=FeatureConfiguration)

    # User preferences
    default_city: str = field(
        default_factory=lambda: os.getenv("WEATHER_DEFAULT_CITY", "New York")
    )
    favorite_cities: list = field(default_factory=list)
    temperature_unit: str = "metric"  # metric, imperial, standard
    debug_mode: bool = field(
        default_factory=lambda: os.getenv("WEATHER_DEBUG", "false").lower() == "true"
    )


def _parse_size(size_str: str) -> tuple:
    """Parse size string like '800,600' to tuple (800, 600)."""
    try:
        width, height = size_str.split(",")
        return (int(width.strip()), int(height.strip()))
    except (ValueError, AttributeError):
        return (1200, 800)  # Default size


class ConfigurationManager:
    """Professional configuration management system with security features."""

    def __init__(self, config_file: str = "settings.json"):
        """Initialize the configuration manager."""
        self.config_file = Path(config_file)
        self.config = ApplicationConfiguration()
        self._load_configuration()
        self._validate_configuration()

    def _load_configuration(self) -> None:
        """Load configuration from file and environment variables."""
        try:
            # Environment variables are already loaded in dataclass defaults

            # Load from file if it exists (for non-sensitive settings)
            if self.config_file.exists():
                self._load_from_file()
            else:
                print(
                    f"Configuration file {self.config_file} not found, using defaults"
                )
                self._create_default_config()

        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Using default configuration")

    def _load_from_file(self) -> None:
        """Load non-sensitive configuration from JSON file."""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Only load non-sensitive settings from file
            # API keys and secrets should always come from environment variables
            if "ui" in data:
                for key, value in data["ui"].items():
                    if hasattr(self.config.ui, key) and not key.startswith("api"):
                        setattr(self.config.ui, key, value)

            if "data" in data:
                for key, value in data["data"].items():
                    if hasattr(self.config.data, key):
                        setattr(self.config.data, key, value)

            # Load user preferences
            if "default_city" in data:
                self.config.default_city = data["default_city"]
            if "favorite_cities" in data:
                self.config.favorite_cities = data["favorite_cities"]
            if "temperature_unit" in data:
                self.config.temperature_unit = data["temperature_unit"]

            print(f"Configuration loaded from {self.config_file}")

        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading configuration file: {e}")

    def _create_default_config(self) -> None:
        """Create a default configuration file."""
        try:
            config_data = {
                "ui": {
                    "theme": self.config.ui.theme,
                    "window_title": self.config.ui.window_title,
                    "min_size": self.config.ui.min_size,
                    "default_size": self.config.ui.default_size,
                },
                "data": {
                    "cache_duration": self.config.data.cache_duration,
                    "auto_refresh": self.config.data.auto_refresh,
                    "export_format": self.config.data.export_format,
                },
                "default_city": self.config.default_city,
                "favorite_cities": self.config.favorite_cities,
                "temperature_unit": self.config.temperature_unit,
                "_readme": "This file contains non-sensitive settings only. API keys and secrets should be in .env file.",
            }

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)

            print(f"Default configuration created: {self.config_file}")

        except Exception as e:
            print(f"Error creating default configuration: {e}")

    def _validate_configuration(self) -> None:
        """Validate configuration values."""
        errors = []
        warnings = []

        # Validate API configuration
        if not self.config.api.api_key:
            warnings.append("OpenWeatherMap API key is not configured")
        elif len(self.config.api.api_key) < 32:
            errors.append("API key appears to be invalid (too short)")

        if self.config.api.timeout < 1 or self.config.api.timeout > 60:
            errors.append("API timeout must be between 1 and 60 seconds")

        # Validate temperature unit
        if self.config.temperature_unit not in ["metric", "imperial", "standard"]:
            errors.append(
                "Temperature unit must be 'metric', 'imperial', or 'standard'"
            )

        # Validate logging configuration
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.config.logging.log_level not in valid_log_levels:
            print(f"Invalid log level '{self.config.logging.log_level}', using INFO")
            self.config.logging.log_level = "INFO"

        # Show warnings
        for warning in warnings:
            print(f"⚠️  Warning: {warning}")

        # Show errors
        if errors:
            print(f"❌ Configuration validation errors:")
            for error in errors:
                print(f"   - {error}")

    def get_masked_api_key(self) -> str:
        """Get masked API key for logging purposes."""
        if not self.config.api.api_key:
            return "Not configured"
        if self.config.security.mask_api_keys:
            return (
                f"{self.config.api.api_key[:8]}..."
                if len(self.config.api.api_key) > 8
                else "***"
            )
        return self.config.api.api_key

    def save_configuration(self) -> None:
        """Save current configuration to file (excluding sensitive data)."""
        try:
            config_data = {
                "ui": {
                    "theme": self.config.ui.theme,
                    "window_title": self.config.ui.window_title,
                    "min_size": self.config.ui.min_size,
                    "default_size": self.config.ui.default_size,
                    "update_interval": self.config.ui.update_interval,
                    "enable_animations": self.config.ui.enable_animations,
                },
                "data": {
                    "cache_duration": self.config.data.cache_duration,
                    "auto_refresh": self.config.data.auto_refresh,
                    "auto_refresh_interval": self.config.data.auto_refresh_interval,
                    "export_format": self.config.data.export_format,
                    "backup_enabled": self.config.data.backup_enabled,
                },
                "logging": {
                    "log_level": self.config.logging.log_level,
                    "performance_logging": self.config.logging.performance_logging,
                    "api_logging": self.config.logging.api_logging,
                    "ui_logging": self.config.logging.ui_logging,
                },
                "features": {
                    "enable_ml_predictions": self.config.features.enable_ml_predictions,
                    "enable_weather_alerts": self.config.features.enable_weather_alerts,
                    "enable_location_services": self.config.features.enable_location_services,
                },
                "default_city": self.config.default_city,
                "favorite_cities": self.config.favorite_cities,
                "temperature_unit": self.config.temperature_unit,
                "_readme": "This file contains non-sensitive settings only. API keys and secrets should be in .env file.",
                "_last_updated": str(Path.cwd()),
            }

            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)

            print(f"Configuration saved to {self.config_file}")

        except Exception as e:
            print(f"Error saving configuration: {e}")

    def update_setting(self, category: str, key: str, value: Any) -> bool:
        """Update a specific setting."""
        try:
            if category == "ui" and hasattr(self.config.ui, key):
                setattr(self.config.ui, key, value)
            elif category == "data" and hasattr(self.config.data, key):
                setattr(self.config.data, key, value)
            elif category == "features" and hasattr(self.config.features, key):
                setattr(self.config.features, key, value)
            elif hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"Invalid setting: {category}.{key}")
                return False

            self._validate_configuration()
            self.save_configuration()
            print(f"Setting updated: {category}.{key} = {value}")
            return True

        except Exception as e:
            print(f"Error updating setting {category}.{key}: {e}")
            return False

    def get_debug_info(self) -> Dict[str, Any]:
        """Get configuration debug information."""
        return {
            "api_key_configured": bool(self.config.api.api_key),
            "api_key_masked": self.get_masked_api_key(),
            "default_city": self.config.default_city,
            "theme": self.config.ui.theme,
            "log_level": self.config.logging.log_level,
            "debug_mode": self.config.debug_mode,
            "features_enabled": {
                "ml_predictions": self.config.features.enable_ml_predictions,
                "weather_alerts": self.config.features.enable_weather_alerts,
                "location_services": self.config.features.enable_location_services,
            },
        }

    # Properties for backward compatibility
    @property
    def api_key(self) -> str:
        """Get the API key."""
        return self.config.api.api_key

    @property
    def current_city(self) -> str:
        """Get the current default city."""
        return self.config.default_city

    @property
    def current_theme(self) -> str:
        """Get the current theme."""
        return self.config.ui.theme


def validate_config() -> bool:
    """Validate that required configuration is present."""
    config_manager = ConfigurationManager()

    if not config_manager.config.api.api_key:
        print("⚠️  Warning: OpenWeatherMap API key not configured")
        print("   Please set OPENWEATHER_API_KEY in your .env file")
        print("   or environment variables")
        return False

    print(f"✅ Configuration valid - API key: {config_manager.get_masked_api_key()}")
    return True


def setup_environment() -> None:
    """Set up the application environment."""
    # Create necessary directories
    directories = ["data", "logs", "cache", "exports"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Copy .env.example to .env and add your API key")

        env_example = Path(".env.example")
        if env_example.exists():
            try:
                import shutil

                shutil.copy(env_example, env_file)
                print("✅ Created .env file from .env.example template")
                print("   Please edit .env and add your API key")
            except Exception as e:
                print(f"   Could not copy .env.example: {e}")

    print("Application environment initialized")


# Global configuration instance
config_manager = ConfigurationManager()

# Backward compatibility aliases
WeatherAPIConfig = config_manager.config.api
AppConfig = config_manager.config.data
UIConfig = config_manager.config.ui

# Configuration information for UI display
APP_CONFIG = {
    "title": config_manager.config.ui.window_title,
    "min_size": config_manager.config.ui.min_size,
    "default_size": config_manager.config.ui.default_size,
    "update_interval": config_manager.config.ui.update_interval,
}


# Error configuration
class ErrorConfig:
    """Error handling configuration."""

    MAX_RETRIES = config_manager.config.api.max_retries
    RETRY_DELAY = 2  # seconds
    TIMEOUT = config_manager.config.api.timeout

    ERROR_MESSAGES = {
        "api_key_missing": "Please set your weather API key in the .env file",
        "network_error": "Unable to connect to weather service",
        "city_not_found": "City not found. Please check the spelling",
        "rate_limit": "API rate limit exceeded. Please try again later",
    }


if __name__ == "__main__":
    # Test configuration system
    print("=== Weather Dashboard Configuration Test ===")
    debug_info = config_manager.get_debug_info()

    for key, value in debug_info.items():
        print(f"{key}: {value}")

    print("\n=== Environment Setup ===")
    setup_environment()
