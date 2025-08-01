"""Dependency Injection Container for Weather Dashboard.

This module provides a centralized dependency injection container
following the Dependency Inversion Principle.
"""

import logging
import os
from typing import Any, Dict, Optional, Type, TypeVar

from src.core.activity_service import ActivitySuggestionService
from src.core.enhanced_comparison_service import EnhancedCityComparisonService
from src.core.journal_service import WeatherJournalService
from src.core.weather_service import WeatherService
from src.infrastructure.config_manager import ConfigManager
from src.services.cache_service import MemoryCacheService
from src.services.composite_weather_service import CompositeWeatherService
from src.services.cortana_voice_service import CortanaVoiceService
from src.services.poetry_service import WeatherPoetryService
from src.services.storage_factory import DataStorageFactory
from src.services.weather_api import OpenWeatherMapAPI
from src.shared.exceptions import DependencyInjectionError

T = TypeVar("T")


class DependencyContainer:
    """Dependency injection container for managing service instances."""

    def __init__(self):
        """Initialize the dependency container."""
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
        self._initialized = False

    def initialize(self) -> None:
        """Initialize all services and dependencies."""
        if self._initialized:
            return

        try:
            self._register_core_services()
            self._register_business_services()
            self._register_infrastructure_services()
            self._initialized = True
            self._logger.info("Dependency container initialized successfully")
        except Exception as e:
            self._logger.error(f"Failed to initialize dependency container: {e}")
            raise DependencyInjectionError(f"Container initialization failed: {e}")

    def _register_core_services(self) -> None:
        """Register core infrastructure services."""
        # Cache service
        self._singletons["cache_service"] = MemoryCacheService()

        # Storage service
        self._singletons["storage_service"] = DataStorageFactory.create_storage()

        # Configuration manager
        config_manager = ConfigManager()
        config_manager.load_config()
        self._singletons["config_manager"] = config_manager

        # Weather API service
        config = config_manager.get_config()
        openweather_api_key = config.weather_api.api_key
        weatherapi_api_key = os.getenv("WEATHERAPI_API_KEY")

        if weatherapi_api_key:
            self._singletons["weather_api"] = CompositeWeatherService(
                openweather_api_key, weatherapi_api_key
            )
        else:
            self._singletons["weather_api"] = OpenWeatherMapAPI()

    def _register_business_services(self) -> None:
        """Register business logic services."""
        # Weather service
        self._singletons["weather_service"] = WeatherService(
            self._singletons["weather_api"],
            self._singletons["storage_service"],
            self._singletons["cache_service"],
        )

        # Comparison service
        self._singletons["comparison_service"] = EnhancedCityComparisonService(
            self._singletons["weather_service"]
        )

        # Journal service
        self._singletons["journal_service"] = WeatherJournalService(
            self._singletons["storage_service"]
        )

        # Activity service
        self._singletons["activity_service"] = ActivitySuggestionService()

        # Poetry service
        from ..interfaces.poetry_interfaces import PoetryGenerationConfig

        poetry_config = PoetryGenerationConfig(
            api_key="",  # Will be configured later or use environment variable
            model_name="gpt-4",
            max_tokens=500,
            temperature=0.8,
        )
        self._singletons["poetry_service"] = WeatherPoetryService(poetry_config)

    def _register_infrastructure_services(self) -> None:
        """Register infrastructure services."""
        # Cortana voice service
        self._singletons["cortana_service"] = CortanaVoiceService(
            self._singletons["weather_api"]
        )

    def get(self, service_name: str) -> Any:
        """Get a service instance by name.

        Args:
            service_name: Name of the service to retrieve

        Returns:
            Service instance

        Raises:
            DependencyInjectionError: If service not found
        """
        if not self._initialized:
            raise DependencyInjectionError("Container not initialized")

        if service_name in self._singletons:
            return self._singletons[service_name]

        if service_name in self._services:
            return self._services[service_name]()

        raise DependencyInjectionError(f"Service '{service_name}' not registered")

    def get_typed(self, service_type: Type[T]) -> T:
        """Get a service instance by type.

        Args:
            service_type: Type of the service to retrieve

        Returns:
            Service instance of the specified type

        Raises:
            DependencyInjectionError: If service not found
        """
        service_name = self._get_service_name_by_type(service_type)
        return self.get(service_name)

    def get_service(self, service_type: Type[T]) -> T:
        """Get a service instance by type (alias for get_typed).

        Args:
            service_type: Type of the service to retrieve

        Returns:
            Service instance of the specified type

        Raises:
            DependencyInjectionError: If service not found
        """
        return self.get_typed(service_type)

    def _get_service_name_by_type(self, service_type: Type) -> str:
        """Get service name by type.

        Args:
            service_type: Type to look up

        Returns:
            Service name

        Raises:
            DependencyInjectionError: If type mapping not found
        """
        # Import interface types
        from ..business.interfaces import (
            IActivitySuggestionService,
            ICityComparisonService,
            ICortanaVoiceService,
            IWeatherJournalService,
            IWeatherPoetryService,
            IWeatherService,
        )

        type_mappings = {
            # Concrete types
            WeatherService: "weather_service",
            EnhancedCityComparisonService: "comparison_service",
            WeatherJournalService: "journal_service",
            ActivitySuggestionService: "activity_service",
            WeatherPoetryService: "poetry_service",
            CortanaVoiceService: "cortana_service",
            MemoryCacheService: "cache_service",
            # Interface types
            IWeatherService: "weather_service",
            ICityComparisonService: "comparison_service",
            IWeatherJournalService: "journal_service",
            IActivitySuggestionService: "activity_service",
            IWeatherPoetryService: "poetry_service",
            ICortanaVoiceService: "cortana_service",
        }

        if service_type in type_mappings:
            return type_mappings[service_type]

        raise DependencyInjectionError(f"No mapping found for type {service_type}")

    def register_singleton(self, service_name: str, instance: Any) -> None:
        """Register a singleton service instance.

        Args:
            service_name: Name of the service
            instance: Service instance
        """
        self._singletons[service_name] = instance
        self._logger.debug(f"Registered singleton service: {service_name}")

    def register_factory(self, service_name: str, factory_func: callable) -> None:
        """Register a factory function for creating service instances.

        Args:
            service_name: Name of the service
            factory_func: Factory function that creates the service
        """
        self._services[service_name] = factory_func
        self._logger.debug(f"Registered factory service: {service_name}")

    def is_registered(self, service_name: str) -> bool:
        """Check if a service is registered.

        Args:
            service_name: Name of the service

        Returns:
            True if service is registered, False otherwise
        """
        return service_name in self._singletons or service_name in self._services

    def get_registered_services(self) -> list[str]:
        """Get list of all registered service names.

        Returns:
            List of registered service names
        """
        return list(self._singletons.keys()) + list(self._services.keys())

    def cleanup(self) -> None:
        """Clean up all services and resources."""
        for service_name, service in self._singletons.items():
            if hasattr(service, "cleanup"):
                try:
                    service.cleanup()
                    self._logger.debug(f"Cleaned up service: {service_name}")
                except Exception as e:
                    self._logger.error(f"Error cleaning up {service_name}: {e}")

        self._singletons.clear()
        self._services.clear()
        self._initialized = False
        self._logger.info("Dependency container cleaned up")


# Global container instance
_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """Get the global dependency container instance.

    Returns:
        Global dependency container
    """
    global _container
    if _container is None:
        _container = DependencyContainer()
        _container.initialize()
    return _container


def reset_container() -> None:
    """Reset the global dependency container."""
    global _container
    if _container:
        _container.cleanup()
    _container = None
