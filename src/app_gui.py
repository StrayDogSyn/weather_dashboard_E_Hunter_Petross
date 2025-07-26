"""
GUI Application Entry Point for Weather Dashboard.

This module provides the main application entry point for the GUI version
of the Weather Dashboard, properly separated from business logic.
"""

import logging
import threading
from typing import Optional

from src.config.config import config_manager, setup_environment, validate_config
from src.controllers.gui_controller import WeatherDashboardController
from src.ui.gui_interface import WeatherDashboardGUI
from src.models.capstone_models import MoodType, ActivitySuggestion


class WeatherDashboardGUIApp:
    """GUI Weather Dashboard Application Entry Point."""

    def __init__(self):
        """Initialize the GUI application."""
        self.controller: Optional[WeatherDashboardController] = None
        self.gui: Optional[WeatherDashboardGUI] = None

        # Setup environment first
        setup_environment()

        # Setup logging
        self._setup_logging()

        # Validate configuration
        self.config_valid = validate_config()

        # Initialize controller (handles all business logic)
        self.controller = WeatherDashboardController()

        if self.controller.is_initialized():
            # Initialize GUI (handles only presentation)
            self.gui = WeatherDashboardGUI()

            # Setup event bindings
            if hasattr(self.gui, 'setup_event_bindings'):
                self.gui.setup_event_bindings()

            # Setup GUI callbacks to use controller
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

    def _setup_gui_callbacks(self):
        """Setup GUI event callbacks to use the controller."""
        if not self.gui or not self.controller:
            return

        # Weather callbacks
        self.gui.set_callback("get_weather", self._handle_get_weather)
        self.gui.set_callback("search_locations", self._handle_search_locations)
        self.gui.set_callback("add_favorite", self._handle_add_favorite)
        self.gui.set_callback(
            "get_current_location_weather", self._handle_current_location_weather
        )

        # Comparison callbacks
        self.gui.set_callback("compare_cities", self._handle_compare_cities)

        # Team data callbacks
        self.gui.set_callback(
            "get_team_data_status", self._handle_get_team_data_status
        )
        self.gui.set_callback("refresh_team_data", self._handle_refresh_team_data)
        self.gui.set_callback("get_team_cities", self._handle_get_team_cities)

        # Journal callbacks
        self.gui.set_callback("create_journal", self._handle_create_journal)
        self.gui.set_callback("view_journal", self._handle_view_journal)

        # Activity callbacks
        self.gui.set_callback("get_activities", self._handle_get_activities)
        self.gui.set_callback(
            "filter_activities", self._handle_filter_activities
        )

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

        # Application exit callback
        self.gui.set_callback("on_app_exit", self._handle_app_exit)

        # Refresh city dropdowns
        if hasattr(self.gui, 'refresh_city_dropdowns_after_callbacks'):
            self.gui.refresh_city_dropdowns_after_callbacks()

    def run(self):
        """Main application entry point."""
        logging.info("Starting GUI Weather Dashboard")

        if not self.controller or not self.controller.is_initialized():
            self._show_config_error()
            return

        if not self.gui:
            print("❌ GUI not properly initialized")
            return

        # Load default city weather if configured
        from src.config.config import config_manager
        default_city = config_manager.config.default_city
        if default_city:
            self._handle_get_weather(default_city)

        # Start GUI
        self.gui.run()

    def _show_config_error(self):
        """Show configuration error message."""
        error_msg = (
            "Configuration Error:\\n\\n"
            "Please set up your weather API key before running the application.\\n\\n"
            "1. Get a free API key from https://openweathermap.org/api\\n"
            "2. Copy .env.example to .env\\n"
            "3. Edit .env and set OPENWEATHER_API_KEY=your_actual_api_key\\n"
            "4. Restart the application"
        )

        if self.gui:
            self.gui.show_error(error_msg)
        else:
            print(error_msg)

    # GUI Event Handlers (delegate to controller)

    def _handle_get_weather(self, city: str):
        """Handle get weather request."""
        if not self.controller or not self.gui:
            return

        def weather_callback(weather, error):
            if error:
                self.gui.root.after(0, lambda: self.gui.show_warning(error))
            elif weather:
                self.gui.root.after(0, lambda: self.gui.display_weather(weather))
                # Get forecast in parallel
                self.controller.get_forecast(city, self._forecast_callback)

        self.gui.update_status(f"Fetching weather for {city}...")
        self.controller.get_weather(city, weather_callback)

    def _forecast_callback(self, forecast, error):
        """Callback for forecast data."""
        if forecast and self.gui:
            self.gui.root.after(0, lambda: self.gui.display_forecast(forecast))

    def _handle_search_locations(self, query: str):
        """Handle search locations request."""
        if not self.controller or not self.gui:
            return

        def search_callback(locations, error):
            if error:
                self.gui.root.after(0, lambda: self.gui.show_error(error))
            elif locations:
                results = "\\n".join([f"• {loc.display_name}" for loc in locations[:5]])
                self.gui.root.after(0, lambda: self.gui.show_message(f"Found locations: \\n{results}"))
            else:
                self.gui.root.after(0, lambda: self.gui.show_message("No locations found"))

        self.gui.update_status(f"Searching for locations: {query}")
        self.controller.search_locations(query, search_callback)

    def _handle_add_favorite(self, city: str):
        """Handle add favorite request."""
        if not self.controller or not self.gui:
            return

        def add_favorite_async():
            success = self.controller.add_favorite_city(city)
            if success:
                self.gui.root.after(0, lambda: self.gui.show_message(f"✅ Added {city} to favorites!"))
            else:
                self.gui.root.after(0, lambda: self.gui.show_error(f"Could not add {city} to favorites"))

        self.gui.update_status(f"Adding {city} to favorites...")
        threading.Thread(target=add_favorite_async, daemon=True).start()

    def _handle_compare_cities(self, city1: str, city2: str):
        """Handle city comparison request."""
        if not self.controller or not self.gui:
            return

        def comparison_callback(comparison, error):
            if error:
                self.gui.root.after(0, lambda: self.gui.show_warning(error))
            elif comparison:
                self.gui.root.after(0, lambda: self.gui.display_weather_comparison(comparison))

        self.gui.update_status(f"Comparing {city1} and {city2}...")
        self.controller.compare_cities(city1, city2, comparison_callback)

    def _handle_get_team_data_status(self):
        """Handle team data status request."""
        if not self.controller:
            return {"team_data_enabled": False, "error": "Controller not available"}
        return self.controller.get_team_data_status()

    def _handle_refresh_team_data(self):
        """Handle team data refresh request."""
        if not self.controller:
            return {"error": "Controller not available"}
        return self.controller.refresh_team_data()

    def _handle_get_team_cities(self):
        """Handle request for available team cities."""
        if not self.controller:
            return []
        return self.controller.get_team_cities()

    def _handle_create_journal(self):
        """Handle create journal entry request."""
        if not self.controller or not self.gui:
            return

        try:
            if not self.gui.current_weather:
                self.gui.show_error("Please get weather data first to create a journal entry")
                return

            # Get mood input
            mood_input = self.gui.get_user_input(
                "Enter your mood (1-10): 1=happy, 2=sad, 3=energetic, "
                "4=relaxed, 5=excited, 6=peaceful, 7=anxious, 8=content, "
                "9=motivated, 10=cozy"
            )
            if not mood_input:
                return

            try:
                mood_index = int(mood_input) - 1
                moods = list(MoodType)
                mood = moods[mood_index] if 0 <= mood_index < len(moods) else MoodType.CONTENT
            except ValueError:
                mood = MoodType.CONTENT

            # Get notes
            notes = self.gui.get_user_input("Write your thoughts about today's weather:")
            if not notes:
                return

            # Get activities
            activities_input = self.gui.get_user_input(
                "What activities did you do today? (comma-separated):"
            )
            activities = [
                activity.strip() for activity in activities_input.split(",") if activity.strip()
            ] if activities_input else []

            # Create entry
            entry = self.controller.create_journal_entry(
                self.gui.current_weather, mood, notes, activities
            )
            if entry:
                self.gui.show_message(f"✅ Journal entry created for {entry.formatted_date}!")
            else:
                self.gui.show_error("Failed to create journal entry")

        except Exception as e:
            logging.error(f"Error creating journal entry: {e}")
            self.gui.show_error(f"Error creating journal entry: {e}")

    def _handle_view_journal(self):
        """Handle view journal entries request."""
        if not self.controller or not self.gui:
            return

        try:
            entries = self.controller.get_journal_entries(10)

            if not entries:
                self.gui.show_message("No journal entries found.")
                return

            # Format entries for display
            entries_text = "\\n".join([
                f"📅 {entry.formatted_date} | {entry.location}\\n"
                f"   {entry.mood_emoji} {entry.mood.value.title()} | "
                f"{entry.weather_summary}\\n"
                f"   📝 {entry.notes[:60]}"
                f"{'...' if len(entry.notes) > 60 else ''}\\n"
                for entry in entries
            ])

            self.gui.show_message(f"Recent Journal Entries: \\n\\n{entries_text}")

        except Exception as e:
            logging.error(f"Error viewing journal: {e}")
            self.gui.show_error(f"Error viewing journal: {e}")

    def _handle_get_activities(self):
        """Handle get activity suggestions request."""
        if not self.controller or not self.gui:
            return

        def get_activities_async():
            try:
                if not self.gui.current_weather:
                    self.gui.root.after(0, lambda: self.gui.display_no_weather_message_activities())
                    return

                suggestions = self.controller.get_activity_suggestions(self.gui.current_weather)
                if suggestions:
                    self.gui.root.after(0, lambda: self.gui.display_activity_suggestions(suggestions))
                else:
                    self.gui.root.after(0, lambda: self.gui.display_activity_error("No suggestions available"))

            except Exception as e:
                logging.error(f"Error getting activities: {e}")
                error_msg = f"Error getting activities: {e}"
                self.gui.root.after(0, lambda: self.gui.display_activity_error(error_msg))

        self.gui.update_status("Getting activity suggestions...")
        threading.Thread(target=get_activities_async, daemon=True).start()

    def _handle_filter_activities(self, activity_type: str):
        """Handle filter activities request."""
        if not self.controller or not self.gui:
            return

        try:
            if not self.gui.current_weather:
                self.gui.display_no_weather_message_activities()
                return

            activities = self.controller.get_filtered_activities(self.gui.current_weather, activity_type)

            # Create ActivitySuggestion object for display
            filtered_suggestion = ActivitySuggestion(
                weather=self.gui.current_weather,
                suggested_activities=activities[:10] if activities else [],
            )

            self.gui.display_activity_suggestions(filtered_suggestion)

        except Exception as e:
            logging.error(f"Error filtering activities: {e}")
            self.gui.display_activity_error(f"Error filtering activities: {e}")

    def _handle_generate_poetry(self):
        """Handle generate poetry request."""
        if not self.controller or not self.gui:
            return

        def generate_poetry_async():
            try:
                if not self.gui.current_weather:
                    self.gui.show_error("Please get weather data first to generate poetry")
                    return

                poem = self.controller.generate_poetry(self.gui.current_weather, "random")
                if poem:
                    self.gui.root.after(0, lambda: self.gui.display_weather_poem(poem))
                else:
                    self.gui.root.after(0, lambda: self.gui.show_error("Failed to generate poetry"))

            except Exception as e:
                logging.error(f"Error generating poetry: {e}")
                error_msg = f"Error generating poetry: {e}"
                self.gui.root.after(0, lambda: self.gui.show_error(error_msg))

        self.gui.update_status("Generating weather poetry...")
        threading.Thread(target=generate_poetry_async, daemon=True).start()

    def _handle_generate_specific_poetry(self, poetry_type: str):
        """Handle generate specific poetry type request."""
        if not self.controller or not self.gui:
            return

        def generate_specific_async():
            try:
                if not self.gui.current_weather:
                    self.gui.show_error("Please get weather data first to generate poetry")
                    return

                poem = self.controller.generate_poetry(self.gui.current_weather, poetry_type)
                if poem:
                    self.gui.root.after(0, lambda: self.gui.display_weather_poem(poem))
                else:
                    self.gui.root.after(0, lambda: self.gui.show_error(f"Failed to generate {poetry_type}"))

            except Exception as e:
                logging.error(f"Error generating {poetry_type}: {e}")
                error_msg = f"Error generating {poetry_type}: {e}"
                self.gui.root.after(0, lambda: self.gui.show_error(error_msg))

        self.gui.update_status(f"Generating {poetry_type}...")
        threading.Thread(target=generate_specific_async, daemon=True).start()

    def _handle_generate_poetry_collection(self):
        """Handle generate poetry collection request."""
        if not self.controller or not self.gui:
            return

        def generate_collection_async():
            try:
                if not self.gui.current_weather:
                    self.gui.show_error("Please get weather data first to generate poetry collection")
                    return

                collection = self.controller.generate_poetry_collection(self.gui.current_weather, 3)
                if collection:
                    self.gui.root.after(0, lambda: self.gui.display_weather_poem_collection(collection))
                else:
                    self.gui.root.after(0, lambda: self.gui.show_error("Failed to generate poetry collection"))

            except Exception as e:
                logging.error(f"Error generating poetry collection: {e}")
                error_msg = f"Error generating poetry collection: {e}"
                self.gui.root.after(0, lambda: self.gui.show_error(error_msg))

        self.gui.update_status("Generating poetry collection...")
        threading.Thread(target=generate_collection_async, daemon=True).start()

    def _handle_refresh_favorites(self):
        """Handle refresh favorites request."""
        if not self.controller or not self.gui:
            return

        def refresh_async():
            try:
                favorites = self.controller.get_favorite_cities()

                if favorites:
                    favorites_text = "\\n".join([f"⭐ {fav.display_name}" for fav in favorites])
                    self.gui.root.after(0, lambda: self.gui.show_message(f"Favorite Cities: \\n\\n{favorites_text}"))
                else:
                    self.gui.root.after(0, lambda: self.gui.show_message("No favorite cities added yet."))

            except Exception as e:
                logging.error(f"Error refreshing favorites: {e}")
                error_msg = f"Error refreshing favorites: {e}"
                self.gui.root.after(0, lambda: self.gui.show_error(error_msg))

        self.gui.update_status("Refreshing favorites...")
        threading.Thread(target=refresh_async, daemon=True).start()

    def _handle_view_favorites_weather(self):
        """Handle view all favorites weather request."""
        if not self.controller or not self.gui:
            return

        def view_favorites_weather_async():
            try:
                favorites = self.controller.get_favorite_cities()
                if not favorites:
                    self.gui.show_message("No favorite cities added yet.")
                    return

                # Note: This would need to be implemented in the controller
                # For now, show favorites list
                favorites_text = "\\n".join([f"📍 {fav.display_name}" for fav in favorites])
                self.gui.root.after(0, lambda: self.gui.show_message(f"Favorite Cities: \\n\\n{favorites_text}"))

            except Exception as e:
                logging.error(f"Error viewing favorites: {e}")
                error_msg = f"Error viewing favorites: {e}"
                self.gui.root.after(0, lambda: self.gui.show_error(error_msg))

        self.gui.update_status("Fetching weather for all favorites...")
        threading.Thread(target=view_favorites_weather_async, daemon=True).start()

    def _handle_current_location_weather(self):
        """Handle request for current location weather."""
        if not self.controller or not self.gui:
            return

        def location_callback(weather, error):
            if error:
                self.gui.root.after(0, lambda: self.gui.show_error(error))
            elif weather:
                self.gui.root.after(0, lambda: self.gui.display_weather(weather))

        logging.info("Handling current location weather request")
        self.controller.get_current_location_weather(location_callback)

    def _handle_app_exit(self):
        """Handle application exit."""
        if self.controller:
            self.controller.save_session_data()


def main_gui():
    """Main entry point for GUI application."""
    try:
        app = WeatherDashboardGUIApp()
        app.run()
    except KeyboardInterrupt:
        print("\\n\\n👋 Application stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main_gui()
