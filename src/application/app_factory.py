"""Application factory for Weather Dashboard.

This module provides the main application factory that orchestrates
the creation and configuration of the entire application using
dependency injection and proper separation of concerns.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from ..infrastructure.config_manager import ConfigManager
from ..shared.constants import DATE_FORMAT
from ..shared.constants import DEFAULT_LOG_LEVEL
from ..shared.constants import LOG_FORMAT
from ..shared.constants import LOGS_DIR
from ..shared.exceptions import ConfigurationError
from ..shared.exceptions import DependencyInjectionError
from ..shared.exceptions import WeatherDashboardError
from .dependency_container import DependencyContainer


class WeatherDashboardAppFactory:
    """Factory class for creating and configuring the Weather Dashboard application."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the application factory.

        Args:
            config_path: Optional path to configuration file
        """
        self._config_path = config_path
        self._container: Optional[DependencyContainer] = None
        self._config_manager: Optional[ConfigManager] = None
        self._logger: Optional[logging.Logger] = None
        self._is_initialized = False

    def initialize(self) -> None:
        """Initialize the application factory and all dependencies.

        Raises:
            ConfigurationError: If configuration loading fails
            DependencyInjectionError: If dependency setup fails
        """
        try:
            # Step 1: Setup basic logging
            self._setup_basic_logging()
            self._logger.info("Starting Weather Dashboard application initialization")

            # Step 2: Load configuration
            self._load_configuration()

            # Step 3: Setup proper logging with configuration
            self._setup_logging()

            # Step 4: Initialize dependency container
            self._initialize_container()

            # Step 5: Register all services
            self._register_services()

            self._is_initialized = True
            self._logger.info("Application initialization completed successfully")

        except Exception as e:
            if self._logger:
                self._logger.error(f"Application initialization failed: {e}")
            raise WeatherDashboardError(
                f"Failed to initialize application: {e}", "INIT_ERROR"
            ) from e

    def create_gui_application(self):
        """Create and return the GUI application instance.

        Returns:
            WeatherDashboardGUIApp: Configured GUI application

        Raises:
            DependencyInjectionError: If application is not initialized
        """
        if not self._is_initialized:
            raise DependencyInjectionError(
                "Application factory must be initialized before creating GUI application"
            )

        try:
            # Import here to avoid circular imports
            from ..presentation.gui_app import WeatherDashboardGUIApp

            # Create GUI application with dependency container
            gui_app = WeatherDashboardGUIApp(self._container)

            self._logger.info("GUI application created successfully")
            return gui_app

        except Exception as e:
            self._logger.error(f"Failed to create GUI application: {e}")
            raise DependencyInjectionError(
                f"Failed to create GUI application: {e}"
            ) from e

    def create_cli_application(self):
        """Create and return the CLI application instance.

        Returns:
            WeatherDashboardCLIApp: Configured CLI application

        Raises:
            DependencyInjectionError: If application is not initialized
        """
        if not self._is_initialized:
            raise DependencyInjectionError(
                "Application factory must be initialized before creating CLI application"
            )

        try:
            # Import here to avoid circular imports
            from ..presentation.cli_app import WeatherDashboardCLIApp

            # Create CLI application with dependency container
            cli_app = WeatherDashboardCLIApp(self._container)

            self._logger.info("CLI application created successfully")
            return cli_app

        except Exception as e:
            self._logger.error(f"Failed to create CLI application: {e}")
            raise DependencyInjectionError(
                f"Failed to create CLI application: {e}"
            ) from e

    def get_container(self) -> DependencyContainer:
        """Get the dependency injection container.

        Returns:
            DependencyContainer: The configured container

        Raises:
            DependencyInjectionError: If application is not initialized
        """
        if not self._is_initialized or not self._container:
            raise DependencyInjectionError(
                "Application factory must be initialized before accessing container"
            )
        return self._container

    def shutdown(self) -> None:
        """Shutdown the application and cleanup resources."""
        if self._logger:
            self._logger.info("Shutting down Weather Dashboard application")

        if self._container:
            try:
                self._container.cleanup()
            except Exception as e:
                if self._logger:
                    self._logger.error(f"Error during container cleanup: {e}")

        self._is_initialized = False

        if self._logger:
            self._logger.info("Application shutdown completed")

    def _setup_basic_logging(self) -> None:
        """Setup basic logging for initialization."""
        logging.basicConfig(
            level=getattr(logging, DEFAULT_LOG_LEVEL),
            format=LOG_FORMAT,
            datefmt=DATE_FORMAT,
        )
        self._logger = logging.getLogger(self.__class__.__name__)

    def _load_configuration(self) -> None:
        """Load application configuration.

        Raises:
            ConfigurationError: If configuration loading fails
        """
        try:
            self._config_manager = ConfigManager(self._config_path)
            self._config_manager.load_config()
            self._logger.info("Configuration loaded successfully")

        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {e}") from e

    def _setup_logging(self) -> None:
        """Setup logging with configuration."""
        try:
            # Get logging configuration from config manager
            log_config = self._config_manager.get_logging_config()

            # Setup file logging
            log_dir = Path(LOGS_DIR)
            log_dir.mkdir(exist_ok=True)

            # Configure root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(
                getattr(logging, log_config.get("level", DEFAULT_LOG_LEVEL))
            )

            # Clear existing handlers
            root_logger.handlers.clear()

            # Add console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)

            # Add file handler
            file_handler = logging.FileHandler(
                log_dir / "weather_dashboard.log", encoding="utf-8"
            )
            file_handler.setLevel(
                getattr(logging, log_config.get("level", DEFAULT_LOG_LEVEL))
            )
            file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)

            # Update logger reference
            self._logger = logging.getLogger(self.__class__.__name__)
            self._logger.info("Logging configuration updated")

        except Exception as e:
            self._logger.warning(f"Failed to setup advanced logging: {e}")
            # Continue with basic logging

    def _initialize_container(self) -> None:
        """Initialize the dependency injection container.

        Raises:
            DependencyInjectionError: If container initialization fails
        """
        try:
            self._container = DependencyContainer()
            self._container.initialize()
            self._logger.info("Dependency container initialized")

        except Exception as e:
            raise DependencyInjectionError(
                f"Failed to initialize dependency container: {e}"
            ) from e

    def _register_services(self) -> None:
        """Register all application services with the container.

        Raises:
            DependencyInjectionError: If service registration fails
        """
        try:
            # Core infrastructure services are already registered in container.initialize()

            # Register business logic services
            self._register_business_services()

            # Register presentation services
            self._register_presentation_services()

            self._logger.info("All services registered successfully")

        except Exception as e:
            raise DependencyInjectionError(f"Failed to register services: {e}") from e

    def _register_business_services(self) -> None:
        """Register business logic services."""
        # Business services are registered in the container's initialize method
        # This method can be extended for additional business service registration
        pass

    def _register_presentation_services(self) -> None:
        """Register presentation layer services."""
        # Presentation services will be registered when needed
        # This method can be extended for additional presentation service registration
        pass


def create_application(config_path: Optional[str] = None) -> WeatherDashboardAppFactory:
    """Create and initialize a Weather Dashboard application factory.

    Args:
        config_path: Optional path to configuration file

    Returns:
        WeatherDashboardAppFactory: Initialized application factory

    Raises:
        WeatherDashboardError: If application creation fails
    """
    factory = WeatherDashboardAppFactory(config_path)
    factory.initialize()
    return factory
