"""
GUI Application Controller for Weather Dashboard.

This module provides the main application controller for the GUI version
of the Weather Dashboard with all capstone features.
"""

import logging
import threading

from src.config.config import config_manager, setup_environment, validate_config
from src.core.activity_service import ActivitySuggestionService
from src.core.comparison_service import CityComparisonService
from src.core.journal_service import WeatherJournalService
from src.core.weather_service import WeatherService
from src.models.capstone_models import MoodType
from src.services.cache_service import MemoryCacheService
from src.services.data_storage import FileDataStorage
from src.services.poetry_service import WeatherPoetryService
from src.services.weather_api import OpenWeatherMapAPI
from src.ui.gui_interface import WeatherDashboardGUI
from src.utils.formatters import validate_city_name
from src.utils.validators import sanitize_input


class WeatherDashboardGUIApp:
    """GUI Weather Dashboard Application Controller."""

    def __init__(self):
        """Initialize the GUI weather dashboard application."""
        self.config_valid = False
        self.gui: WeatherDashboardGUI = None  # type: ignore
        self.weather_service: WeatherService = None  # type: ignore

        # Capstone services
        self.comparison_service: CityComparisonService = None  # type: ignore
        self.journal_service: WeatherJournalService = None  # type: ignore
        self.activity_service: ActivitySuggestionService = None  # type: ignore
        self.poetry_service: WeatherPoetryService = None  # type: ignore

        # Setup environment first
        setup_environment()

        # Setup logging
        self._setup_logging()

        # Validate configuration
        self.config_valid = validate_config()

        if self.config_valid:
            self._initialize_services()
            if self.gui:  # Only setup callbacks if GUI was successfully initialized
                self._setup_gui_callbacks()

        logging.info("GUI Weather Dashboard application initialized")

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
        """Initialize all services."""
        try:
            # Initialize services
            weather_api = OpenWeatherMapAPI()

            # Use storage factory to create appropriate storage implementation
            from .services.storage_factory import DataStorageFactory

            storage = DataStorageFactory.create_storage()

            cache = MemoryCacheService()

            # Initialize core service
            self.weather_service = WeatherService(weather_api, storage, cache)

            # Initialize capstone services
            self.comparison_service = CityComparisonService(self.weather_service)
            self.journal_service = WeatherJournalService(storage)
            self.activity_service = ActivitySuggestionService()
            self.poetry_service = WeatherPoetryService()

            # Initialize GUI
            self.gui = WeatherDashboardGUI()

            logging.info("All GUI services initialized successfully")

        except Exception as e:
            logging.error(f"Error initializing GUI services: {e}")
            self.config_valid = False

    def _setup_gui_callbacks(self):
        """Setup GUI event callbacks."""
        if not self.gui:
            return

        # Weather callbacks
        self.gui.set_callback("get_weather", self._handle_get_weather)
        self.gui.set_callback("search_locations", self._handle_search_locations)
        self.gui.set_callback("add_favorite", self._handle_add_favorite)
        self.gui.set_callback(
            "get_current_location_weather", self._handle_current_location_weather
        )

        # Comparison callback
        self.gui.set_callback("compare_cities", self._handle_compare_cities)

        # Journal callbacks
        self.gui.set_callback("create_journal", self._handle_create_journal)
        self.gui.set_callback("view_journal", self._handle_view_journal)

        # Activity callbacks
        self.gui.set_callback("get_activities", self._handle_get_activities)
        self.gui.set_callback("filter_activities", self._handle_filter_activities)

        # Poetry callbacks
        self.gui.set_callback("generate_poetry", self._handle_generate_poetry)
        self.gui.set_callback(
            "generate_specific_poetry", self._handle_generate_specific_poetry
        )
        self.gui.set_callback(
            "generate_poetry_collection", self._handle_generate_poetry_collection
        )

        # Favorites callbacks
        self.gui.set_callback("refresh_favorites", self._handle_refresh_favorites)
        self.gui.set_callback(
            "view_favorites_weather", self._handle_view_favorites_weather
        )

        # Current location callback
        self.gui.set_callback(
            "get_current_location_weather", self._handle_current_location_weather
        )

    def run(self):
        """Main application entry point."""
        logging.info("Starting GUI Weather Dashboard")

        if not self.config_valid:
            self._show_config_error()
            return

        if not self.gui or not self.weather_service:
            print("❌ Application services not properly initialized")
            return

        # Load default city weather if configured
        default_city = config_manager.config.default_city
        if default_city:
            self._handle_get_weather(default_city)

        # Start GUI
        self.gui.run()

    def _show_config_error(self):
        """Show configuration error message."""
        error_msg = (
            "Configuration Error:\n\n"
            "Please set up your weather API key before running the application.\n\n"
            "1. Get a free API key from https://openweathermap.org/api\n"
            "2. Copy .env.example to .env\n"
            "3. Edit .env and set OPENWEATHER_API_KEY=your_actual_api_key\n"
            "4. Restart the application"
        )

        if self.gui:
            self.gui.show_error(error_msg)
        else:
            print(error_msg)

    def _safe_gui_call(self, method_name: str, *args, **kwargs):
        """Safely call a GUI method if GUI is available."""
        if self.gui and hasattr(self.gui, method_name):
            method = getattr(self.gui, method_name)
            return method(*args, **kwargs)
        return None

    def _safe_service_call(self, service_name: str, method_name: str, *args, **kwargs):
        """Safely call a service method if service is available."""
        service = getattr(self, service_name, None)
        if service and hasattr(service, method_name):
            method = getattr(service, method_name)
            return method(*args, **kwargs)
        return None

    def _ensure_gui_initialized(self):
        """Ensure GUI and services are properly initialized."""
        if not self.gui or not self.weather_service:
            raise RuntimeError("GUI or services not properly initialized")
        return self.gui, self.weather_service

    # GUI Event Handlers

    def _handle_get_weather(self, city: str):
        """Handle get weather request."""
        if not self.gui or not self.weather_service:
            return

        def get_weather_async():
            try:
                if not self.gui or not self.weather_service:
                    return

                if not validate_city_name(city):
                    self.gui.show_error("Invalid city name format")
                    return

                city_clean = sanitize_input(city)
                self.gui.update_status(f"Fetching weather for {city_clean}...")

                weather = self.weather_service.get_current_weather(city_clean)

                if weather:
                    # Update GUI on main thread
                    if self.gui:
                        self.gui.root.after(
                            0, lambda: self.gui.display_weather(weather)
                        )

                        # Also get forecast
                        forecast = self.weather_service.get_weather_forecast(city_clean)
                        if forecast:
                            self.gui.root.after(
                                0, lambda: self.gui.display_forecast(forecast)
                            )
                else:
                    if self.gui:
                        self.gui.root.after(
                            0,
                            lambda: self.gui.show_error(
                                f"Could not retrieve weather for {city_clean}"
                            ),
                        )

            except Exception as e:
                logging.error(f"Error getting weather: {e}")
                if self.gui:
                    self.gui.root.after(
                        0,
                        lambda exc=e: self.gui.show_error(
                            f"Error getting weather: {exc}"
                        ),
                    )

        # Run in background thread to prevent GUI freezing
        threading.Thread(target=get_weather_async, daemon=True).start()

    def _handle_search_locations(self, query: str):
        """Handle search locations request."""

        def search_async():
            try:
                if len(query) < 2:
                    if self.gui:
                        self.gui.show_error("Search query too short")
                    return

                query_clean = sanitize_input(query)
                if self.gui:
                    self.gui.update_status(f"Searching for locations: {query_clean}")

                locations = None
                if self.weather_service:
                    locations = self.weather_service.search_locations(query_clean)

                if locations:
                    # Show results in a simple message for now
                    results = "\n".join(
                        [f"• {loc.display_name}" for loc in locations[:5]]
                    )
                    if self.gui:
                        self.gui.root.after(
                            0,
                            lambda: self.gui.show_message(
                                f"Found locations:\n{results}"
                            ),
                        )
                else:
                    if self.gui:
                        self.gui.root.after(
                            0, lambda: self.gui.show_message("No locations found")
                        )

            except Exception as e:
                logging.error(f"Error searching locations: {e}")
                if self.gui:
                    self.gui.root.after(
                        0, lambda exc=e: self.gui.show_error(f"Error searching: {exc}")
                    )

        threading.Thread(target=search_async, daemon=True).start()

    def _handle_add_favorite(self, city: str):
        """Handle add favorite request."""

        def add_favorite_async():
            try:
                if not validate_city_name(city):
                    self.gui.show_error("Invalid city name format")
                    return

                self.gui.update_status(f"Adding {city} to favorites...")
                success = self.weather_service.add_favorite_city(city)

                if success:
                    self.gui.root.after(
                        0,
                        lambda: self.gui.show_message(f"✅ Added {city} to favorites!"),
                    )
                else:
                    self.gui.root.after(
                        0,
                        lambda: self.gui.show_error(
                            f"Could not add {city} to favorites"
                        ),
                    )

            except Exception as e:
                logging.error(f"Error adding favorite: {e}")
                if self.gui:
                    self.gui.root.after(
                        0,
                        lambda exc=e: self.gui.show_error(
                            f"Error adding favorite: {exc}"
                        ),
                    )

        threading.Thread(target=add_favorite_async, daemon=True).start()

    def _handle_compare_cities(self, city1: str, city2: str):
        """Handle city comparison request."""

        def compare_async():
            try:
                if not validate_city_name(city1) or not validate_city_name(city2):
                    self.gui.show_error("Invalid city name format")
                    return

                self.gui.update_status(f"Comparing {city1} and {city2}...")
                comparison = self.comparison_service.compare_cities(city1, city2)

                if comparison:
                    self.gui.root.after(
                        0, lambda: self.gui.display_weather_comparison(comparison)
                    )
                else:
                    self.gui.root.after(
                        0,
                        lambda: self.gui.show_error(
                            "Could not retrieve weather data for comparison"
                        ),
                    )

            except Exception as e:
                logging.error(f"Error comparing cities: {e}")
                self.gui.root.after(
                    0,
                    lambda exc=e: self.gui.show_error(f"Error comparing cities: {exc}"),
                )

        threading.Thread(target=compare_async, daemon=True).start()

    def _handle_create_journal(self):
        """Handle create journal entry request."""
        try:
            # Get current weather context
            if not self.gui.current_weather:
                self.gui.show_error(
                    "Please get weather data first to create a journal entry"
                )
                return

            # Simple dialog for journal entry (could be enhanced with custom dialog)
            mood_input = self.gui.get_user_input(
                (
                    "Enter your mood (1-10): 1=happy, 2=sad, 3=energetic, "
                    "4=relaxed, 5=excited, 6=peaceful, 7=anxious, 8=content, "
                    "9=motivated, 10=cozy"
                )
            )
            if not mood_input:
                return

            try:
                mood_index = int(mood_input) - 1
                moods = list(MoodType)
                if 0 <= mood_index < len(moods):
                    mood = moods[mood_index]
                else:
                    mood = MoodType.CONTENT
            except ValueError:
                mood = MoodType.CONTENT

            notes = self.gui.get_user_input(
                "Write your thoughts about today's weather:"
            )
            if not notes:
                return

            activities_input = self.gui.get_user_input(
                "What activities did you do today? (comma-separated):"
            )
            activities = (
                [
                    activity.strip()
                    for activity in activities_input.split(",")
                    if activity.strip()
                ]
                if activities_input
                else []
            )

            # Create entry
            entry = self.journal_service.create_entry(
                self.gui.current_weather, mood, notes, activities
            )
            self.gui.show_message(
                f"✅ Journal entry created for {entry.formatted_date}!"
            )

        except Exception as e:
            logging.error(f"Error creating journal entry: {e}")
            self.gui.show_error(f"Error creating journal entry: {e}")

    def _handle_view_journal(self):
        """Handle view journal entries request."""
        try:
            entries = self.journal_service.get_recent_entries(10)

            if not entries:
                self.gui.show_message("No journal entries found.")
                return

            # Format entries for display
            entries_text = "\n".join(
                [
                    f"📅 {entry.formatted_date} | {entry.location}\n"
                    f"   {entry.mood_emoji} {entry.mood.value.title()} | "
                    f"{entry.weather_summary}\n"
                    f"   📝 {entry.notes[:60]}"
                    f"{'...' if len(entry.notes) > 60 else ''}\n"
                    for entry in entries
                ]
            )

            self.gui.show_message(f"Recent Journal Entries:\n\n{entries_text}")

        except Exception as e:
            logging.error(f"Error viewing journal: {e}")
            self.gui.show_error(f"Error viewing journal: {e}")

    def _handle_get_activities(self):
        """Handle get activity suggestions request."""

        def get_activities_async():
            try:
                if not self.gui.current_weather:
                    self.gui.show_error(
                        "Please get weather data first to get activity suggestions"
                    )
                    return

                self.gui.update_status("Getting activity suggestions...")
                suggestions = self.activity_service.get_activity_suggestions(
                    self.gui.current_weather
                )

                self.gui.root.after(
                    0, lambda: self.gui.display_activity_suggestions(suggestions)
                )

            except Exception as e:
                logging.error(f"Error getting activities: {e}")
                self.gui.root.after(
                    0,
                    lambda exc=e: self.gui.show_error(
                        f"Error getting activities: {exc}"
                    ),
                )

        threading.Thread(target=get_activities_async, daemon=True).start()

    def _handle_filter_activities(self, activity_type: str):
        """Handle filter activities request."""
        try:
            if not self.gui.current_weather:
                self.gui.show_error("Please get weather data first")
                return

            if activity_type == "indoor":
                activities = self.activity_service.get_indoor_activities(
                    self.gui.current_weather
                )
            elif activity_type == "outdoor":
                activities = self.activity_service.get_outdoor_activities(
                    self.gui.current_weather
                )
            else:
                return

            # Format activities for display
            if activities:
                activities_text = "\n".join(
                    [
                        f"{'🏠' if activity.indoor else '🌞'} {activity.name} "
                        f"(Score: {score:.1f})\n"
                        f"   {activity.description}"
                        for activity, score in activities[:10]
                    ]
                )
                self.gui.show_message(
                    f"{activity_type.title()} Activities:\n\n{activities_text}"
                )
            else:
                self.gui.show_message(
                    f"No {activity_type} activities found for current conditions."
                )

        except Exception as e:
            logging.error(f"Error filtering activities: {e}")
            self.gui.show_error(f"Error filtering activities: {e}")

    def _handle_generate_poetry(self):
        """Handle generate poetry request."""

        def generate_poetry_async():
            try:
                if not self.gui.current_weather:
                    self.gui.show_error(
                        "Please get weather data first to generate poetry"
                    )
                    return

                self.gui.update_status("Generating weather poetry...")
                poem = self.poetry_service.generate_weather_poetry(
                    self.gui.current_weather, "random"
                )

                self.gui.root.after(0, lambda: self.gui.display_weather_poem(poem))

            except Exception as e:
                logging.error(f"Error generating poetry: {e}")
                self.gui.root.after(
                    0,
                    lambda exc=e: self.gui.show_error(
                        f"Error generating poetry: {exc}"
                    ),
                )

        threading.Thread(target=generate_poetry_async, daemon=True).start()

    def _handle_generate_specific_poetry(self, poetry_type: str):
        """Handle generate specific poetry type request."""

        def generate_specific_async():
            try:
                if not self.gui.current_weather:
                    self.gui.show_error(
                        "Please get weather data first to generate poetry"
                    )
                    return

                self.gui.update_status(f"Generating {poetry_type}...")
                poem = self.poetry_service.generate_weather_poetry(
                    self.gui.current_weather, poetry_type
                )

                self.gui.root.after(0, lambda: self.gui.display_weather_poem(poem))

            except Exception as e:
                logging.error(f"Error generating {poetry_type}: {e}")
                self.gui.root.after(
                    0,
                    lambda exc=e, ptype=poetry_type: self.gui.show_error(
                        f"Error generating {ptype}: {exc}"
                    ),
                )

        threading.Thread(target=generate_specific_async, daemon=True).start()

    def _handle_generate_poetry_collection(self):
        """Handle generate poetry collection request."""

        def generate_collection_async():
            try:
                if not self.gui.current_weather:
                    self.gui.show_error(
                        "Please get weather data first to generate poetry collection"
                    )
                    return

                self.gui.update_status("Generating poetry collection...")
                collection = self.poetry_service.create_poetry_collection(
                    self.gui.current_weather, 3
                )

                self.gui.root.after(
                    0, lambda: self.gui.display_weather_poem_collection(collection)
                )

            except Exception as e:
                logging.error(f"Error generating poetry collection: {e}")
                self.gui.root.after(
                    0,
                    lambda exc=e: self.gui.show_error(
                        f"Error generating poetry collection: {exc}"
                    ),
                )

        threading.Thread(target=generate_collection_async, daemon=True).start()

    def _handle_refresh_favorites(self):
        """Handle refresh favorites request."""

        def refresh_async():
            try:
                self.gui.update_status("Refreshing favorites...")
                favorites = self.weather_service.get_favorite_cities()

                # Format favorites for display
                if favorites:
                    favorites_text = "\n".join(
                        [f"⭐ {fav.display_name}" for fav in favorites]
                    )
                    self.gui.root.after(
                        0,
                        lambda: self.gui.show_message(
                            f"Favorite Cities:\n\n{favorites_text}"
                        ),
                    )
                else:
                    self.gui.root.after(
                        0,
                        lambda: self.gui.show_message("No favorite cities added yet."),
                    )

            except Exception as e:
                logging.error(f"Error refreshing favorites: {e}")
                self.gui.root.after(
                    0,
                    lambda exc=e: self.gui.show_error(
                        f"Error refreshing favorites: {exc}"
                    ),
                )

        threading.Thread(target=refresh_async, daemon=True).start()

    def _handle_view_favorites_weather(self):
        """Handle view all favorites weather request."""

        def view_favorites_weather_async():
            try:
                favorites = self.weather_service.get_favorite_cities()
                if not favorites:
                    self.gui.show_message("No favorite cities added yet.")
                    return

                self.gui.update_status("Fetching weather for all favorites...")
                weather_data = self.weather_service.get_weather_for_favorites()

                # Format weather data for display
                weather_text = []
                for city_name, weather in weather_data.items():
                    if weather:
                        temp = weather.temperature.to_celsius()
                        weather_text.append(
                            f"📍 {city_name}: {temp:.1f}°C - "
                            f"{weather.description.title()}"
                        )
                    else:
                        weather_text.append(f"📍 {city_name}: Weather data unavailable")

                self.gui.root.after(
                    0,
                    lambda: self.gui.show_message(
                        "Weather for Favorites:\n\n" + "\n".join(weather_text)
                    ),
                )

            except Exception as e:
                logging.error(f"Error viewing favorites weather: {e}")
                self.gui.root.after(
                    0,
                    lambda exc=e: self.gui.show_error(
                        f"Error viewing favorites weather: {exc}"
                    ),
                )

        threading.Thread(target=view_favorites_weather_async, daemon=True).start()

    def _handle_current_location_weather(self):
        """Handle request for current location weather."""
        logging.info("Handling current location weather request")

        # Start weather retrieval in a separate thread
        threading.Thread(
            target=self._fetch_current_location_weather,
            daemon=True,
        ).start()

    def _fetch_current_location_weather(self):
        """Fetch current location weather in background thread."""
        try:
            # Get weather data for current location
            weather_data = self.weather_service.get_current_location_weather()

            if weather_data:
                # Update the UI with the weather data
                self.gui.root.after(0, lambda: self.gui.display_weather(weather_data))
            else:
                # Show error message
                self.gui.root.after(
                    0,
                    lambda: self.gui.show_error(
                        "Could not detect location or retrieve weather data"
                    ),
                )

        except Exception as e:
            logging.error(f"Error in fetch_current_location_weather: {e}")
            self.gui.root.after(
                0,
                lambda exc=e: self.gui.show_error(
                    f"Error retrieving weather: {str(exc)}"
                ),
            )


def main_gui():
    """Main entry point for GUI application."""
    try:
        app = WeatherDashboardGUIApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main_gui()
