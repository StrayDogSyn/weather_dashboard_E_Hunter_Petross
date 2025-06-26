"""
Weather Dashboard - Main Application
A comprehensive weather dashboard application

Author: E Hunter Petross
Project: Weather Dashboard Capstone
"""

import os
import sys
import logging
from datetime import datetime
from typing import Optional, Dict, Any

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from config import config_manager, validate_config, setup_environment

class WeatherDashboard:
    """Main Weather Dashboard Application Class"""
    
    def __init__(self):
        """Initialize the weather dashboard"""
        self.config_valid = False
        self.weather_data = {}
        self.favorite_cities = []
        
        # Setup environment first
        setup_environment()
        
        # Setup logging
        self.setup_logging()
        
        # Validate configuration
        self.config_valid = validate_config()
        
        # Create data directory if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        logging.info("Weather Dashboard initialized")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, config_manager.config.logging.log_level)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('weather_dashboard.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def get_current_weather(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Get current weather for a specific city
        
        Args:
            city (str): City name
            
        Returns:
            Dict containing weather data or None if error
        """
        if not self.config_valid:
            logging.error("Configuration not valid - cannot fetch weather data")
            return None
        
        # TODO: Implement API call to weather service
        # This is a placeholder for now
        logging.info(f"Fetching current weather for {city}")
        
        # Placeholder data structure
        placeholder_data = {
            "city": city,
            "temperature": 22,
            "humidity": 65,
            "description": "Clear sky",
            "icon": "01d",
            "timestamp": datetime.now().isoformat()
        }
        
        return placeholder_data
    
    def get_forecast(self, city: str, days: int = 5) -> Optional[Dict[str, Any]]:
        """
        Get weather forecast for a specific city
        
        Args:
            city (str): City name
            days (int): Number of days for forecast
            
        Returns:
            Dict containing forecast data or None if error
        """
        if not self.config_valid:
            logging.error("Configuration not valid - cannot fetch forecast data")
            return None
        
        # TODO: Implement API call for forecast
        logging.info(f"Fetching {days}-day forecast for {city}")
        
        # Placeholder forecast data
        forecast_data = {
            "city": city,
            "days": days,
            "forecast": [
                {
                    "date": datetime.now().isoformat(),
                    "high": 25,
                    "low": 18,
                    "description": "Partly cloudy",
                    "icon": "02d"
                }
                # TODO: Add more days
            ]
        }
        
        return forecast_data
    
    def add_favorite_city(self, city: str):
        """Add a city to favorites"""
        if city not in self.favorite_cities:
            self.favorite_cities.append(city)
            logging.info(f"Added {city} to favorites")
    
    def remove_favorite_city(self, city: str):
        """Remove a city from favorites"""
        if city in self.favorite_cities:
            self.favorite_cities.remove(city)
            logging.info(f"Removed {city} from favorites")
    
    def save_data(self, data: Dict[str, Any], filename: str):
        """Save data to file in data directory"""
        filepath = os.path.join("data", filename)
        try:
            import json
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info(f"Data saved to {filepath}")
        except Exception as e:
            logging.error(f"Error saving data to {filepath}: {e}")
    
    def load_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load data from file in data directory"""
        filepath = os.path.join("data", filename)
        try:
            import json
            with open(filepath, 'r') as f:
                data = json.load(f)
            logging.info(f"Data loaded from {filepath}")
            return data
        except FileNotFoundError:
            logging.warning(f"File not found: {filepath}")
            return None
        except Exception as e:
            logging.error(f"Error loading data from {filepath}: {e}")
            return None
    
    def run(self):
        """Main application entry point"""
        logging.info("Starting Weather Dashboard")
        
        if not self.config_valid:
            print("⚠️  Configuration Error:")
            print("Please set up your weather API key before running the application.")
            print("1. Get a free API key from https://openweathermap.org/api")
            print("2. Copy .env.example to .env")
            print("3. Edit .env and set OPENWEATHER_API_KEY=your_actual_api_key")
            print("4. Restart the application")
            return
        
        # For now, just run a simple CLI demo
        self.run_cli_demo()
    
    def run_cli_demo(self):
        """Run a simple command-line demo"""
        print(f"\n🌤️  Welcome to {config_manager.config.ui.window_title}!")
        print("=" * 50)
        
        # Show configuration status
        debug_info = config_manager.get_debug_info()
        print(f"📍 Default city: {debug_info['default_city']}")
        print(f"🔑 API key: {debug_info['api_key_masked']}")
        print(f"🎨 Theme: {debug_info['theme']}")
        
        while True:
            print("\nOptions:")
            print("1. Get current weather")
            print("2. Get weather forecast")
            print("3. View favorite cities")
            print("4. Add favorite city")
            print("5. Show configuration")
            print("6. Exit")
            
            choice = input("\nEnter your choice (1-6): ").strip()
            
            if choice == '1':
                city = input("Enter city name: ").strip()
                if city:
                    weather = self.get_current_weather(city)
                    if weather:
                        print(f"\n🌡️  Current weather in {weather['city']}:")
                        print(f"   Temperature: {weather['temperature']}°C")
                        print(f"   Humidity: {weather['humidity']}%")
                        print(f"   Description: {weather['description']}")
            
            elif choice == '2':
                city = input("Enter city name: ").strip()
                if city:
                    forecast = self.get_forecast(city)
                    if forecast:
                        print(f"\n📅 Weather forecast for {forecast['city']}:")
                        for day in forecast['forecast']:
                            print(f"   {day['date'][:10]}: {day['high']}°/{day['low']}° - {day['description']}")
            
            elif choice == '3':
                if self.favorite_cities:
                    print(f"\n⭐ Favorite cities: {', '.join(self.favorite_cities)}")
                else:
                    print("\n⭐ No favorite cities added yet.")
            
            elif choice == '4':
                city = input("Enter city name to add to favorites: ").strip()
                if city:
                    self.add_favorite_city(city)
                    print(f"✅ Added {city} to favorites!")
            
            elif choice == '5':
                print("\n🔧 Configuration:")
                debug_info = config_manager.get_debug_info()
                for key, value in debug_info.items():
                    if key != 'features_enabled':
                        print(f"   {key}: {value}")
                    else:
                        print(f"   features_enabled:")
                        for feature, enabled in value.items():
                            print(f"     {feature}: {enabled}")
            
            elif choice == '6':
                print("\n👋 Thank you for using Weather Dashboard!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main entry point"""
    try:
        app = WeatherDashboard()
        app.run()
    except KeyboardInterrupt:
        print("\n\n👋 Application stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    main()