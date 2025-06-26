"""Main application controller for the Weather Dashboard."""

import logging
import sys
from typing import Optional
from datetime import datetime, date

from .core import WeatherService
from .core.comparison_service import CityComparisonService
from .core.journal_service import WeatherJournalService
from .core.activity_service import ActivitySuggestionService
from .services import OpenWeatherMapAPI, FileDataStorage, MemoryCacheService
from .services.poetry_service import WeatherPoetryService
from .ui import CliInterface
from .config import config_manager, validate_config, setup_environment
from .utils import validate_city_name, sanitize_input
from .models.capstone_models import MoodType


class WeatherDashboardApp:
    """Main Weather Dashboard Application Controller."""
    
    def __init__(self):
        """Initialize the weather dashboard application."""
        self.config_valid = False
        self.ui: Optional[CliInterface] = None
        self.weather_service: Optional[WeatherService] = None
        
        # Capstone services
        self.comparison_service: Optional[CityComparisonService] = None
        self.journal_service: Optional[WeatherJournalService] = None
        self.activity_service: Optional[ActivitySuggestionService] = None
        self.poetry_service: Optional[WeatherPoetryService] = None
        
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
            
            # Initialize capstone services
            self.comparison_service = CityComparisonService(self.weather_service)
            self.journal_service = WeatherJournalService(storage)
            self.activity_service = ActivitySuggestionService()
            self.poetry_service = WeatherPoetryService()
            
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
                self.ui.show_main_menu()
                choice = self.ui.get_enhanced_menu_choice()
                
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
                    self._handle_city_comparison()
                elif choice == '11':
                    self._handle_weather_journal()
                elif choice == '12':
                    self._handle_activity_suggestions()
                elif choice == '13':
                    self._handle_weather_poetry()
                elif choice == '14':
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
    
    # Capstone Feature Handlers
    
    def _handle_city_comparison(self):
        """Handle city comparison feature."""
        assert self.ui is not None and self.comparison_service is not None
        
        city1, city2 = self.ui.get_cities_for_comparison()
        if not city1 or not city2:
            return
        
        if not validate_city_name(city1) or not validate_city_name(city2):
            self.ui.show_error("Invalid city name format")
            return
        
        self.ui.show_message(f"Comparing weather between {city1} and {city2}...")
        comparison = self.comparison_service.compare_cities(city1, city2)
        
        if comparison:
            self.ui.display_weather_comparison(comparison)
        else:
            self.ui.show_error("Could not retrieve weather data for comparison")
    
    def _handle_weather_journal(self):
        """Handle weather journal feature."""
        assert self.ui is not None and self.journal_service is not None and self.weather_service is not None
        
        while True:
            choice = self.ui.show_journal_menu()
            
            if choice == '1':
                self._create_journal_entry()
            elif choice == '2':
                self._view_recent_entries()
            elif choice == '3':
                self._view_entry_by_date()
            elif choice == '4':
                self._search_journal_entries()
            elif choice == '5':
                self._show_mood_statistics()
            elif choice == '6':
                self._export_journal()
            elif choice == '7':
                break
            else:
                self.ui.show_error("Invalid choice. Please try again.")
    
    def _create_journal_entry(self):
        """Create a new journal entry."""
        assert self.ui is not None and self.journal_service is not None and self.weather_service is not None
        
        # Get current weather for user's location or ask for city
        city = self.ui.get_user_input("Enter city name for weather context")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        # Display current weather
        self.ui.display_weather(weather)
        
        # Get journal entry data
        mood, notes, activities = self.ui.get_journal_entry_data()
        
        # Create entry
        entry = self.journal_service.create_entry(weather, mood, notes, activities)
        self.ui.show_message("✅ Journal entry created successfully!")
        self.ui.display_journal_entry(entry)
    
    def _view_recent_entries(self):
        """View recent journal entries."""
        assert self.ui is not None and self.journal_service is not None
        
        entries = self.journal_service.get_recent_entries(10)
        self.ui.display_journal_entries(entries)
    
    def _view_entry_by_date(self):
        """View journal entry by specific date."""
        assert self.ui is not None and self.journal_service is not None
        
        date_str = self.ui.get_date_input()
        if not date_str:
            entry_date = date.today()
        else:
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                self.ui.show_error("Invalid date format. Use YYYY-MM-DD")
                return
        
        entry = self.journal_service.get_entry_by_date(entry_date)
        if entry:
            self.ui.display_journal_entry(entry)
        else:
            self.ui.show_message(f"No journal entry found for {entry_date}")
    
    def _search_journal_entries(self):
        """Search journal entries."""
        assert self.ui is not None and self.journal_service is not None
        
        query = self.ui.get_search_query()
        if not query:
            return
        
        entries = self.journal_service.search_entries(query)
        if entries:
            self.ui.display_journal_entries(entries)
        else:
            self.ui.show_message(f"No entries found matching '{query}'")
    
    def _show_mood_statistics(self):
        """Show mood statistics."""
        assert self.ui is not None and self.journal_service is not None
        
        stats = self.journal_service.get_mood_statistics()
        if stats:
            self.ui.show_statistics(stats)
        else:
            self.ui.show_message("No mood data available yet")
    
    def _export_journal(self):
        """Export journal to text file."""
        assert self.ui is not None and self.journal_service is not None
        
        filename = f"weather_journal_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        content = self.journal_service.export_entries_to_text(filename)
        self.ui.show_message(f"✅ Journal exported to {filename}")
    
    def _handle_activity_suggestions(self):
        """Handle activity suggestions feature."""
        assert self.ui is not None and self.activity_service is not None and self.weather_service is not None
        
        while True:
            choice = self.ui.show_activity_menu()
            
            if choice == '1':
                self._get_activity_suggestions()
            elif choice == '2':
                self._get_indoor_activities()
            elif choice == '3':
                self._get_outdoor_activities()
            elif choice == '4':
                self._show_activity_details()
            elif choice == '5':
                break
            else:
                self.ui.show_error("Invalid choice. Please try again.")
    
    def _get_activity_suggestions(self):
        """Get activity suggestions for current weather."""
        assert self.ui is not None and self.activity_service is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name for activity suggestions")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        suggestions = self.activity_service.get_activity_suggestions(weather)
        self.ui.display_activity_suggestions(suggestions)
    
    def _get_indoor_activities(self):
        """Get indoor activity suggestions."""
        assert self.ui is not None and self.activity_service is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        indoor_activities = self.activity_service.get_indoor_activities(weather)
        
        print(f"\n🏠 Indoor Activities for {weather.location.display_name}")
        print("-" * 40)
        if indoor_activities:
            for i, (activity, score) in enumerate(indoor_activities, 1):
                print(f"{i}. {activity.name} (Score: {score:.1f})")
                print(f"   {activity.description}")
        else:
            print("No indoor activities found.")
    
    def _get_outdoor_activities(self):
        """Get outdoor activity suggestions."""
        assert self.ui is not None and self.activity_service is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        outdoor_activities = self.activity_service.get_outdoor_activities(weather)
        
        print(f"\n🌞 Outdoor Activities for {weather.location.display_name}")
        print("-" * 40)
        if outdoor_activities:
            for i, (activity, score) in enumerate(outdoor_activities, 1):
                print(f"{i}. {activity.name} (Score: {score:.1f})")
                print(f"   {activity.description}")
        else:
            print("No suitable outdoor activities found for current conditions.")
    
    def _show_activity_details(self):
        """Show detailed activity report."""
        assert self.ui is not None and self.activity_service is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name for detailed activity report")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        report = self.activity_service.create_activity_report(weather)
        print(report)
    
    def _handle_weather_poetry(self):
        """Handle weather poetry feature."""
        assert self.ui is not None and self.poetry_service is not None and self.weather_service is not None
        
        while True:
            choice = self.ui.show_poetry_menu()
            
            if choice == '1':
                self._generate_random_poem()
            elif choice == '2':
                self._generate_haiku()
            elif choice == '3':
                self._generate_fun_phrase()
            elif choice == '4':
                self._generate_limerick()
            elif choice == '5':
                self._generate_poetry_collection()
            elif choice == '6':
                break
            else:
                self.ui.show_error("Invalid choice. Please try again.")
    
    def _generate_random_poem(self):
        """Generate a random weather poem."""
        assert self.ui is not None and self.poetry_service is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name for weather poetry")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        poem = self.poetry_service.generate_weather_poetry(weather, "random")
        self.ui.display_weather_poem(poem)
    
    def _generate_haiku(self):
        """Generate a weather haiku."""
        assert self.ui is not None and self.poetry_service is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name for weather haiku")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        poem = self.poetry_service.generate_haiku(weather)
        self.ui.display_weather_poem(poem)
    
    def _generate_fun_phrase(self):
        """Generate a fun weather phrase."""
        assert self.ui is not None and self.poetry_service is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name for weather phrase")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        poem = self.poetry_service.generate_fun_phrase(weather)
        self.ui.display_weather_poem(poem)
    
    def _generate_limerick(self):
        """Generate a weather limerick."""
        assert self.ui is not None and self.poetry_service is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name for weather limerick")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        poem = self.poetry_service.generate_limerick(weather)
        self.ui.display_weather_poem(poem)
    
    def _generate_poetry_collection(self):
        """Generate a collection of weather poems."""
        assert self.ui is not None and self.poetry_service is not None and self.weather_service is not None
        
        city = self.ui.get_user_input("Enter city name for poetry collection")
        if not city:
            return
        
        weather = self.weather_service.get_current_weather(city)
        if not weather:
            self.ui.show_error(f"Could not get weather data for {city}")
            return
        
        poems = self.poetry_service.create_poetry_collection(weather, 3)
        self.ui.display_poetry_collection(poems)
    

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
