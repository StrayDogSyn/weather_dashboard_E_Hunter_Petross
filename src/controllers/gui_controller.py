"""
GUI Application Controller for Weather Dashboard.

This controller manages the interaction between the GUI and business logic services,
following proper separation of concerns principles.
"""

import logging
import os
import threading
from typing import Optional

from src.config.config import config_manager, setup_environment, validate_config
from src.core.activity_service import ActivitySuggestionService
from src.core.enhanced_comparison_service import EnhancedCityComparisonService
from src.core.journal_service import WeatherJournalService
from src.core.weather_service import WeatherService
from src.models.capstone_models import MoodType
from src.services.cache_service import MemoryCacheService
from src.services.data_storage import FileDataStorage
from src.services.poetry_service import WeatherPoetryService
from src.services.weather_api import OpenWeatherMapAPI
from src.services.composite_weather_service import CompositeWeatherService
from src.utils.formatters import validate_city_name
from src.utils.validators import sanitize_input


class WeatherDashboardController:
    """Controller for Weather Dashboard GUI application."""

    def __init__(self):
        """Initialize the controller."""
        self.config_valid = False
        self.weather_service: Optional[WeatherService] = None

        # Capstone services
        self.comparison_service: Optional[EnhancedCityComparisonService] = None
        self.journal_service: Optional[WeatherJournalService] = None
        self.activity_service: Optional[ActivitySuggestionService] = None
        self.poetry_service: Optional[WeatherPoetryService] = None

        # Setup environment and logging
        setup_environment()
        self._setup_logging()

        # Validate configuration and initialize services
        self.config_valid = validate_config()
        if self.config_valid:
            self._initialize_services()

        logging.info("GUI Weather Dashboard controller initialized")

    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, config_manager.config.logging.log_level)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("weather_dashboard.log"),
                logging.StreamHandler(),
            ],
        )

    def _initialize_services(self):
        """Initialize all business logic services."""
        try:
            # Initialize weather API with fallback support
            openweather_api_key = config_manager.config.api.api_key
            weatherapi_api_key = os.getenv("WEATHERAPI_API_KEY")

            if weatherapi_api_key:
                logging.info("Initializing weather service with fallback support")
                weather_api = CompositeWeatherService(openweather_api_key, weatherapi_api_key)
            else:
                logging.info("Initializing weather service with primary API only")
                weather_api = OpenWeatherMapAPI()

            # Use storage factory for appropriate storage implementation
            from src.services.storage_factory import DataStorageFactory
            storage = DataStorageFactory.create_storage()
            cache = MemoryCacheService()

            # Initialize core service
            self.weather_service = WeatherService(weather_api, storage, cache)

            # Initialize capstone services
            self.comparison_service = EnhancedCityComparisonService(self.weather_service)
            self.journal_service = WeatherJournalService(storage)
            self.activity_service = ActivitySuggestionService()
            self.poetry_service = WeatherPoetryService()

            logging.info("All services initialized successfully")

        except Exception as e:
            logging.error(f"Error initializing services: {e}")
            self.config_valid = False

    def get_weather(self, city: str, callback=None):
        """Get weather for a city."""
        if not self.weather_service:
            return None

        def get_weather_async():
            try:
                if not validate_city_name(city):
                    if callback:
                        callback(None, "Invalid city name format")
                    return

                city_clean = sanitize_input(city)

                # Check cache first
                cache_key = self.weather_service.cache.get_cache_key("weather", city_clean, "metric")
                cached_weather = self.weather_service.cache.get(cache_key)

                if cached_weather and callback:
                    callback(cached_weather, None)

                # Get fresh data
                weather = self.weather_service.get_current_weather(city_clean)
                if callback:
                    callback(weather, None if weather else "Could not retrieve weather data")

            except Exception as e:
                logging.error(f"Error getting weather: {e}")
                if callback:
                    callback(None, str(e))

        threading.Thread(target=get_weather_async, daemon=True).start()

    def get_forecast(self, city: str, callback=None):
        """Get weather forecast for a city."""
        if not self.weather_service:
            return None

        def get_forecast_async():
            try:
                city_clean = sanitize_input(city)
                forecast = self.weather_service.get_weather_forecast(city_clean)
                if callback:
                    callback(forecast, None if forecast else "Could not retrieve forecast data")
            except Exception as e:
                logging.error(f"Error getting forecast: {e}")
                if callback:
                    callback(None, str(e))

        threading.Thread(target=get_forecast_async, daemon=True).start()

    def compare_cities(self, city1: str, city2: str, callback=None):
        """Compare weather between two cities."""
        if not self.comparison_service:
            return None

        def compare_async():
            try:
                if not validate_city_name(city1) or not validate_city_name(city2):
                    if callback:
                        callback(None, "Invalid city name format")
                    return

                comparison = self.comparison_service.compare_cities(city1, city2)
                if callback:
                    callback(comparison, None if comparison else "Could not compare cities")

            except Exception as e:
                logging.error(f"Error comparing cities: {e}")
                if callback:
                    callback(None, str(e))

        threading.Thread(target=compare_async, daemon=True).start()

    def create_journal_entry(self, weather, mood: MoodType, notes: str, activities: list):
        """Create a journal entry."""
        if not self.journal_service:
            return None

        try:
            return self.journal_service.create_entry(weather, mood, notes, activities)
        except Exception as e:
            logging.error(f"Error creating journal entry: {e}")
            return None

    def get_journal_entries(self, limit: int = 10):
        """Get recent journal entries."""
        if not self.journal_service:
            return []

        try:
            return self.journal_service.get_recent_entries(limit)
        except Exception as e:
            logging.error(f"Error getting journal entries: {e}")
            return []

    def get_activity_suggestions(self, weather):
        """Get activity suggestions for weather."""
        if not self.activity_service:
            return None

        try:
            return self.activity_service.get_activity_suggestions(weather)
        except Exception as e:
            logging.error(f"Error getting activities: {e}")
            return None

    def get_filtered_activities(self, weather, activity_type: str):
        """Get filtered activities (indoor/outdoor)."""
        if not self.activity_service:
            return []

        try:
            if activity_type == "indoor":
                return self.activity_service.get_indoor_activities(weather)
            elif activity_type == "outdoor":
                return self.activity_service.get_outdoor_activities(weather)
            return []
        except Exception as e:
            logging.error(f"Error filtering activities: {e}")
            return []

    def generate_poetry(self, weather, poetry_type: str = "random"):
        """Generate weather poetry."""
        if not self.poetry_service:
            return None

        try:
            return self.poetry_service.generate_weather_poetry(weather, poetry_type)
        except Exception as e:
            logging.error(f"Error generating poetry: {e}")
            return None

    def generate_poetry_collection(self, weather, count: int = 3):
        """Generate a collection of weather poems."""
        if not self.poetry_service:
            return []

        try:
            return self.poetry_service.create_poetry_collection(weather, count)
        except Exception as e:
            logging.error(f"Error generating poetry collection: {e}")
            return []

    def add_favorite_city(self, city: str):
        """Add a city to favorites."""
        if not self.weather_service:
            return False

        try:
            return self.weather_service.add_favorite_city(city)
        except Exception as e:
            logging.error(f"Error adding favorite: {e}")
            return False

    def get_favorite_cities(self):
        """Get list of favorite cities."""
        if not self.weather_service:
            return []

        try:
            return self.weather_service.get_favorite_cities()
        except Exception as e:
            logging.error(f"Error getting favorites: {e}")
            return []

    def get_current_location_weather(self, callback=None):
        """Get weather for current location."""
        if not self.weather_service:
            return None

        def get_location_weather_async():
            try:
                weather = self.weather_service.get_current_location_weather()
                if callback:
                    callback(weather, None if weather else "Could not detect location")
            except Exception as e:
                logging.error(f"Error getting current location weather: {e}")
                if callback:
                    callback(None, str(e))

        threading.Thread(target=get_location_weather_async, daemon=True).start()

    def search_locations(self, query: str, callback=None):
        """Search for locations."""
        if not self.weather_service:
            return None

        def search_async():
            try:
                if len(query) < 2:
                    if callback:
                        callback([], "Search query too short")
                    return

                query_clean = sanitize_input(query)
                locations = self.weather_service.search_locations(query_clean)
                if callback:
                    callback(locations or [], None)

            except Exception as e:
                logging.error(f"Error searching locations: {e}")
                if callback:
                    callback([], str(e))

        threading.Thread(target=search_async, daemon=True).start()

    def get_team_data_status(self):
        """Get team data status."""
        try:
            if self.comparison_service:
                return {"available": True, "cities_count": 5}
            else:
                return {
                    "team_data_enabled": False,
                    "cities_available": 0,
                    "city_list": [],
                    "data_loaded": False,
                    "error": "Team comparison service not available"
                }
        except Exception as e:
            logging.error(f"Error getting team data status: {e}")
            return {
                "team_data_enabled": False,
                "cities_available": 0,
                "city_list": [],
                "data_loaded": False,
                "error": str(e)
            }

    def get_team_cities(self):
        """Get available team cities."""
        try:
            if self.comparison_service and hasattr(self.comparison_service, 'team_data_service'):
                team_service = self.comparison_service.team_data_service
                cities = team_service.get_available_cities()

                if not cities:
                    if team_service.load_team_data():
                        cities = team_service.get_available_cities()

                    if not cities and team_service.create_sample_team_data():
                        cities = team_service.get_available_cities()

                logging.info(f"Retrieved {len(cities)} cities from team data")
                return cities
            else:
                logging.warning("Team data service not available, using fallback cities")
                return ["Austin", "Providence", "Rawlins", "Ontario", "New York", "Miami", "New Jersey"]

        except Exception as e:
            logging.error(f"Error getting team cities: {e}")
            return ["Austin", "Providence", "Rawlins", "Ontario", "New York", "Miami", "New Jersey"]

    def save_session_data(self):
        """Save session data before exit."""
        logging.info("Saving session data before application exit")
        try:
            if self.weather_service and hasattr(self.weather_service, "_save_favorite_cities"):
                self.weather_service._save_favorite_cities()

            if self.journal_service and hasattr(self.journal_service, "_save_entries"):
                self.journal_service._save_entries()

            logging.info("Session data saved successfully")
        except Exception as e:
            logging.error(f"Error saving session data: {e}")

    def is_initialized(self) -> bool:
        """Check if controller is properly initialized."""
        return self.config_valid and self.weather_service is not None
