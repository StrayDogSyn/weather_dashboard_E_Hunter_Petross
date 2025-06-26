"""Main application controller for the Weather Dashboard."""

import logging
import sys
from typing import Optional

from .core import WeatherService
from .services import OpenWeatherMapAPI, FileDataStorage, MemoryCacheService
from .ui import CliInterface
from .config import config_manager, validate_config, setup_environment
from .utils import validate_city_name, sanitize_input


class WeatherDashboardApp:
    """Main Weather Dashboard Application Controller."""
    
    def __init__(self):
        """Initialize the weather dashboard application."""
        self.config_valid = False
        self.ui: Optional[CliInterface] = None
        self.weather_service: Optional[WeatherService] = None
        
        # Setup environment first
        setup_environment()
        
        # Setup logging
        self._setup_logging()
        
        # Validate configuration
        self.config_valid = validate_config()
        
        if self.config_valid:
            self._initialize_services()
        
        logging.info("Weather Dashboard application initialized")
    
    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, config_manager.config.logging.log_level)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('weather_dashboard.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def _initialize_services(self):
        """Initialize all services."""
        try:
            # Initialize services
            weather_api = OpenWeatherMapAPI()
            storage = FileDataStorage()
            cache = MemoryCacheService()
            
            # Initialize core service
            self.weather_service = WeatherService(weather_api, storage, cache)
            
            # Initialize UI
            self.ui = CliInterface()
            
            logging.info("All services initialized successfully")
            
        except Exception as e:
            logging.error(f"Error initializing services: {e}")
            self.config_valid = False
    
    def run(self):
        """Main application entry point."""
        logging.info("Starting Weather Dashboard")
        
        if not self.config_valid:
            self._show_config_error()
            return
        
        if not self.ui or not self.weather_service:
            print("❌ Application services not properly initialized")
            return
        
        # Run main application loop
        self._run_main_loop()
    
    def _show_config_error(self):
        """Show configuration error message."""
        print("⚠️  Configuration Error:")
        print("Please set up your weather API key before running the application.")
        print("1. Get a free API key from https://openweathermap.org/api")
        print("2. Copy .env.example to .env")
        print("3. Edit .env and set OPENWEATHER_API_KEY=your_actual_api_key")
        print("4. Restart the application")
    
    def _run_main_loop(self):
        """Run the main application loop."""
        # Type checking assertions
        assert self.ui is not None, "UI not initialized"
        assert self.weather_service is not None, "Weather service not initialized"
        
        self.ui.show_welcome()
        
        # Show configuration status
        debug_info = config_manager.get_debug_info()
        print(f"📍 Default city: {debug_info['default_city']}")
        print(f"🔑 API key: {debug_info['api_key_masked']}")
        print(f"🎨 Theme: {debug_info['theme']}")
        
        while True:
            try:
                self.ui.show_menu()
                choice = self.ui.get_menu_choice()
                
                if choice == '1':
                    self._handle_current_weather()
                elif choice == '2':
                    self._handle_forecast()
                elif choice == '3':
                    self._handle_search_locations()
                elif choice == '4':
                    self._handle_view_favorites()
                elif choice == '5':
                    self._handle_add_favorite()
                elif choice == '6':
                    self._handle_remove_favorite()
                elif choice == '7':
                    self._handle_favorites_weather()
                elif choice == '8':
                    self._handle_show_config()
                elif choice == '9':
                    self._handle_clear_cache()
                elif choice == '10':
                    self._handle_exit()
                    break
                else:
                    self.ui.show_error("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Application stopped by user")
                break
            except Exception as e:
                logging.error(f"Unexpected error in main loop: {e}")
                self.ui.show_error(f"An unexpected error occurred: {e}")
    
    def _handle_current_weather(self):
        """Handle current weather request."""
        assert self.ui is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name")
        if not city:
            return
        
        if not validate_city_name(city):
            self.ui.show_error("Invalid city name format")
            return
        
        self.ui.show_message(f"Fetching current weather for {city}...")
        weather = self.weather_service.get_current_weather(city)
        
        if weather:
            self.ui.display_weather(weather)
            self.weather_service.mark_city_viewed(city)
        else:
            self.ui.show_error(f"Could not retrieve weather data for {city}")
    
    def _handle_forecast(self):
        """Handle forecast request."""
        assert self.ui is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name")
        if not city:
            return
        
        if not validate_city_name(city):
            self.ui.show_error("Invalid city name format")
            return
        
        days_str = self.ui.get_user_input("Number of forecast days (1-16, default 5)")
        try:
            days = int(days_str) if days_str else 5
            if not (1 <= days <= 16):
                raise ValueError()
        except ValueError:
            self.ui.show_error("Invalid number of days. Using default (5)")
            days = 5
        
        self.ui.show_message(f"Fetching {days}-day forecast for {city}...")
        forecast = self.weather_service.get_weather_forecast(city, days)
        
        if forecast:
            self.ui.display_forecast(forecast)
            self.weather_service.mark_city_viewed(city)
        else:
            self.ui.show_error(f"Could not retrieve forecast data for {city}")
    
    def _handle_search_locations(self):
        """Handle location search request."""
        assert self.ui is not None and self.weather_service is not None
        
        query = self.ui.get_user_input("Enter search query")
        if not query:
            return
        
        query = sanitize_input(query)
        if len(query) < 2:
            self.ui.show_error("Search query too short")
            return
        
        self.ui.show_message(f"Searching for locations: {query}")
        locations = self.weather_service.search_locations(query)
        
        self.ui.display_locations(locations)
    
    def _handle_view_favorites(self):
        """Handle view favorites request."""
        assert self.ui is not None and self.weather_service is not None
        
        favorites = self.weather_service.get_favorite_cities()
        self.ui.display_favorite_cities(favorites)
    
    def _handle_add_favorite(self):
        """Handle add favorite request."""
        assert self.ui is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name to add to favorites")
        if not city:
            return
        
        if not validate_city_name(city):
            self.ui.show_error("Invalid city name format")
            return
        
        nickname = self.ui.get_user_input("Enter nickname (optional)")
        nickname = nickname if nickname else None
        
        self.ui.show_message(f"Adding {city} to favorites...")
        success = self.weather_service.add_favorite_city(city, nickname)
        
        if success:
            display_name = nickname if nickname else city
            self.ui.show_message(f"✅ Added {display_name} to favorites!")
        else:
            self.ui.show_error(f"Could not add {city} to favorites")
    
    def _handle_remove_favorite(self):
        """Handle remove favorite request."""
        assert self.ui is not None and self.weather_service is not None
        
        favorites = self.weather_service.get_favorite_cities()
        if not favorites:
            self.ui.show_message("No favorite cities to remove.")
            return
        
        self.ui.display_favorite_cities(favorites)
        
        city = self.ui.get_user_input("Enter city name or nickname to remove")
        if not city:
            return
        
        if self.ui.confirm_action(f"Remove {city} from favorites?"):
            success = self.weather_service.remove_favorite_city(city)
            
            if success:
                self.ui.show_message(f"✅ Removed {city} from favorites!")
            else:
                self.ui.show_error(f"Could not find {city} in favorites")
    
    def _handle_favorites_weather(self):
        """Handle weather for all favorites request."""
        assert self.ui is not None and self.weather_service is not None
        
        favorites = self.weather_service.get_favorite_cities()
        if not favorites:
            self.ui.show_message("No favorite cities added yet.")
            return
        
        self.ui.show_message("Fetching weather for all favorite cities...")
        weather_data = self.weather_service.get_weather_for_favorites()
        
        self.ui.display_favorites_weather(weather_data)
    
    def _handle_show_config(self):
        """Handle show configuration request."""
        assert self.ui is not None and self.weather_service is not None
        
        debug_info = config_manager.get_debug_info()
        self.ui.display_config(debug_info)
        
        # Also show cache stats
        cache_stats = self.weather_service.get_cache_stats()
        self.ui.display_cache_stats(cache_stats)
    
    def _handle_clear_cache(self):
        """Handle clear cache request."""
        assert self.ui is not None and self.weather_service is not None
        
        if self.ui.confirm_action("Clear all cached data?"):
            success = self.weather_service.clear_cache()
            
            if success:
                self.ui.show_message("✅ Cache cleared successfully!")
            else:
                self.ui.show_error("Failed to clear cache")
    
    def _handle_exit(self):
        """Handle exit request."""
        assert self.ui is not None
        
        self.ui.show_message("👋 Thank you for using Weather Dashboard!")
        
        # Cleanup
        if self.weather_service:
            cache_stats = self.weather_service.get_cache_stats()
            logging.info(f"Final cache stats: {cache_stats}")


def main():
    """Main entry point."""
    try:
        app = WeatherDashboardApp()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    main()
