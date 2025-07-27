"""Configuration Manager for Weather Dashboard.

This module provides centralized configuration management with
validation, environment variable support, and default values.
"""

import configparser
import json
import logging
import os
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from ..shared.constants import CONFIG_FILE_PATH
from ..shared.constants import DEFAULT_API_TIMEOUT
from ..shared.constants import DEFAULT_CACHE_TTL
from ..shared.constants import DEFAULT_DATABASE_PATH
from ..shared.constants import DEFAULT_LOG_LEVEL
from ..shared.exceptions import ConfigurationError


@dataclass
class WeatherAPIConfig:
    """Weather API configuration."""

    api_key: str = ""
    base_url: str = "https://api.openweathermap.org/data/2.5"
    timeout: int = DEFAULT_API_TIMEOUT
    rate_limit: int = 60  # requests per minute
    units: str = "metric"  # metric, imperial, kelvin


@dataclass
class DatabaseConfig:
    """Database configuration."""

    path: str = DEFAULT_DATABASE_PATH
    backup_enabled: bool = True
    backup_interval: int = 3600  # seconds
    max_backups: int = 5
    connection_timeout: int = 30


@dataclass
class CacheConfig:
    """Cache configuration."""

    enabled: bool = True
    ttl: int = DEFAULT_CACHE_TTL
    max_size: int = 1000
    cleanup_interval: int = 300  # seconds
    persistence_enabled: bool = True


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = DEFAULT_LOG_LEVEL
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "logs/weather_dashboard.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_enabled: bool = True


@dataclass
class UIConfig:
    """UI configuration."""

    theme: str = "default"
    window_width: int = 1200
    window_height: int = 800
    auto_refresh: bool = True
    refresh_interval: int = 300  # seconds
    show_tooltips: bool = True
    animation_enabled: bool = True


@dataclass
class VoiceConfig:
    """Voice assistant configuration."""

    enabled: bool = False
    voice_profile: str = "en-US_Standard"
    personality_traits: List[str] = field(
        default_factory=lambda: ["helpful", "curious", "witty"]
    )
    enable_privacy_mode: bool = True
    log_level: str = "INFO"
    integrations: List[str] = field(default_factory=list)
    security_scopes: List[str] = field(default_factory=list)
    deploy_environment: str = "dev"


@dataclass
class AppConfig:
    """Main application configuration."""

    weather_api: WeatherAPIConfig = field(default_factory=WeatherAPIConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)

    # Application metadata
    app_name: str = "Weather Dashboard"
    app_version: str = "1.0.0"
    debug_mode: bool = False
    development_mode: bool = False


class ConfigManager:
    """Centralized configuration manager.

    Handles loading, validation, and management of application configuration
    from multiple sources including files, environment variables, and defaults.
    """

    def __init__(self, config_file: Optional[str] = None):
        """Initialize the configuration manager.

        Args:
            config_file: Optional path to configuration file
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._config_file = config_file or CONFIG_FILE_PATH
        self._config: Optional[AppConfig] = None
        self._loaded = False

        # Environment variable mappings
        self._env_mappings = {
            "OPENWEATHER_API_KEY": "weather_api.api_key",
            "WEATHER_API_KEY": "weather_api.api_key",  # Fallback
            "WEATHER_API_URL": "weather_api.base_url",
            "WEATHER_DATABASE_PATH": "database.path",
            "DATABASE_PATH": "database.path",  # Fallback
            "LOG_LEVEL": "logging.level",
            "DEBUG_MODE": "debug_mode",
            "DEVELOPMENT_MODE": "development_mode",
            "CACHE_ENABLED": "cache.enabled",
            "CACHE_TTL": "cache.ttl",
            "UI_THEME": "ui.theme",
            "VOICE_ENABLED": "voice.enabled",
            "VOICE_PROFILE": "voice.voice_profile",
            "VOICE_PRIVACY_MODE": "voice.enable_privacy_mode",
        }

    def load_config(self) -> AppConfig:
        """Load configuration from all sources.

        Returns:
            Loaded and validated configuration

        Raises:
            ConfigurationError: If configuration loading or validation fails
        """
        try:
            self._logger.info("Loading application configuration")

            # Start with default configuration
            self._config = AppConfig()

            # Load from file if it exists
            if os.path.exists(self._config_file):
                self._load_from_file()
            else:
                self._logger.warning(
                    f"Configuration file not found: {self._config_file}"
                )

            # Override with environment variables
            self._load_from_environment()

            # Validate configuration
            self._validate_config()

            # Create necessary directories
            self._create_directories()

            self._loaded = True
            self._logger.info("Configuration loaded successfully")

            return self._config

        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration: {e}", "ConfigManager", "load_config"
            ) from e

    def _load_from_file(self) -> None:
        """Load configuration from file.

        Supports JSON and INI formats based on file extension.
        """
        try:
            config_path = Path(self._config_file)

            if config_path.suffix.lower() == ".json":
                self._load_from_json()
            elif config_path.suffix.lower() in [".ini", ".cfg"]:
                self._load_from_ini()
            else:
                self._logger.warning(
                    f"Unsupported config file format: {config_path.suffix}"
                )

        except Exception as e:
            self._logger.error(f"Failed to load config from file: {e}")
            raise

    def _load_from_json(self) -> None:
        """Load configuration from JSON file."""
        with open(self._config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)

        self._apply_config_data(config_data)

    def _load_from_ini(self) -> None:
        """Load configuration from INI file."""
        config = configparser.ConfigParser()
        config.read(self._config_file)

        # Convert INI structure to nested dict
        config_data = {}
        for section_name in config.sections():
            section = config[section_name]
            config_data[section_name] = dict(section)

        self._apply_config_data(config_data)

    def _apply_config_data(self, config_data: Dict[str, Any]) -> None:
        """Apply configuration data to the config object.

        Args:
            config_data: Configuration data dictionary
        """
        for key, value in config_data.items():
            if isinstance(value, dict) and hasattr(self._config, key):
                # Handle nested dataclass objects
                nested_obj = getattr(self._config, key)
                if hasattr(nested_obj, "__dataclass_fields__"):
                    # Apply each field individually to preserve the dataclass structure
                    for nested_key, nested_value in value.items():
                        self._set_nested_value(
                            self._config, f"{key}.{nested_key}", nested_value
                        )
                else:
                    self._set_nested_value(self._config, key, value)
            else:
                self._set_nested_value(self._config, key, value)

    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        for env_var, config_path in self._env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string values to appropriate types
                converted_value = self._convert_env_value(env_value)
                self._set_nested_value(self._config, config_path, converted_value)
                self._logger.debug(
                    f"Set {config_path} from environment variable {env_var}"
                )

    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """Convert environment variable string to appropriate type.

        Args:
            value: String value from environment variable

        Returns:
            Converted value
        """
        # Boolean conversion
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        elif value.lower() in ("false", "no", "0", "off"):
            return False

        # Numeric conversion
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _set_nested_value(self, obj: Any, path: str, value: Any) -> None:
        """Set a nested value using dot notation.

        Args:
            obj: Object to set value on
            path: Dot-separated path (e.g., 'weather_api.api_key')
            value: Value to set
        """
        parts = path.split(".")
        current = obj

        for part in parts[:-1]:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return  # Path doesn't exist, skip

        final_part = parts[-1]
        if hasattr(current, final_part):
            setattr(current, final_part, value)

    def _validate_config(self) -> None:
        """Validate the loaded configuration.

        Raises:
            ConfigurationError: If validation fails
        """
        errors = []

        # Validate weather API configuration
        if not self._config.weather_api.api_key:
            errors.append("Weather API key is required")

        if self._config.weather_api.timeout <= 0:
            errors.append("Weather API timeout must be positive")

        # Validate database configuration
        if not self._config.database.path:
            errors.append("Database path is required")

        # Validate cache configuration
        if self._config.cache.ttl <= 0:
            errors.append("Cache TTL must be positive")

        if self._config.cache.max_size <= 0:
            errors.append("Cache max size must be positive")

        # Validate logging configuration
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self._config.logging.level not in valid_log_levels:
            errors.append(f"Invalid log level: {self._config.logging.level}")

        # Validate UI configuration
        if self._config.ui.window_width <= 0 or self._config.ui.window_height <= 0:
            errors.append("UI window dimensions must be positive")

        # Validate voice configuration
        if self._config.voice.enabled:
            valid_profiles = ["en-US_Standard", "en-GB_Standard", "custom"]
            if self._config.voice.voice_profile not in valid_profiles:
                errors.append(
                    f"Invalid voice profile: {self._config.voice.voice_profile}"
                )

            valid_environments = ["dev", "staging", "prod"]
            if self._config.voice.deploy_environment not in valid_environments:
                errors.append(
                    f"Invalid deploy environment: {self._config.voice.deploy_environment}"
                )

        if errors:
            raise ConfigurationError(
                f"Configuration validation failed: {'; '.join(errors)}",
                "ConfigManager",
                "validate_config",
            )

    def _create_directories(self) -> None:
        """Create necessary directories based on configuration."""
        directories = [
            os.path.dirname(self._config.database.path),
            os.path.dirname(self._config.logging.file_path),
        ]

        for directory in directories:
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    self._logger.debug(f"Created directory: {directory}")
                except OSError as e:
                    self._logger.warning(f"Failed to create directory {directory}: {e}")

    def get_config(self) -> AppConfig:
        """Get the current configuration.

        Returns:
            Current configuration

        Raises:
            ConfigurationError: If configuration is not loaded
        """
        if not self._loaded or self._config is None:
            raise ConfigurationError(
                "Configuration not loaded. Call load_config() first.",
                "ConfigManager",
                "get_config",
            )

        return self._config

    def save_config(self, config_file: Optional[str] = None) -> None:
        """Save current configuration to file.

        Args:
            config_file: Optional path to save configuration to

        Raises:
            ConfigurationError: If saving fails
        """
        if not self._loaded or self._config is None:
            raise ConfigurationError(
                "No configuration to save", "ConfigManager", "save_config"
            )

        save_path = config_file or self._config_file

        try:
            # Convert config to dictionary
            config_dict = self._config_to_dict(self._config)

            # Ensure directory exists
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Save as JSON
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=2, default=str)

            self._logger.info(f"Configuration saved to: {save_path}")

        except Exception as e:
            raise ConfigurationError(
                f"Failed to save configuration: {e}", "ConfigManager", "save_config"
            ) from e

    def _config_to_dict(self, config: AppConfig) -> Dict[str, Any]:
        """Convert configuration object to dictionary.

        Args:
            config: Configuration object

        Returns:
            Configuration as dictionary
        """
        result = {}

        for field_name in config.__dataclass_fields__:
            field_value = getattr(config, field_name)

            if hasattr(field_value, "__dataclass_fields__"):
                # Nested dataclass
                result[field_name] = self._config_to_dict(field_value)
            else:
                result[field_name] = field_value

        return result

    def update_config(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values.

        Args:
            updates: Dictionary of configuration updates

        Raises:
            ConfigurationError: If update fails
        """
        if not self._loaded or self._config is None:
            raise ConfigurationError(
                "Configuration not loaded", "ConfigManager", "update_config"
            )

        try:
            for path, value in updates.items():
                self._set_nested_value(self._config, path, value)

            # Re-validate after updates
            self._validate_config()

            self._logger.info("Configuration updated successfully")

        except Exception as e:
            raise ConfigurationError(
                f"Failed to update configuration: {e}", "ConfigManager", "update_config"
            ) from e

    def get_logging_config(self) -> LoggingConfig:
        """Get the logging configuration.

        Returns:
            Logging configuration

        Raises:
            ConfigurationError: If configuration is not loaded
        """
        if not self._loaded or self._config is None:
            raise ConfigurationError(
                "Configuration not loaded. Call load_config() first.",
                "ConfigManager",
                "get_logging_config",
            )

        return self._config.logging

    @property
    def is_loaded(self) -> bool:
        """Check if configuration is loaded."""
        return self._loaded

    @property
    def config_file(self) -> str:
        """Get the configuration file path."""
        return self._config_file
