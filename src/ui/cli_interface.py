"""Command-line interface for the Weather Dashboard application."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..interfaces.weather_interfaces import IUserInterface
from ..models import CurrentWeather, WeatherForecast, FavoriteCity
from ..utils import (
    format_temperature, format_percentage, format_wind_speed,
    format_pressure, format_datetime, get_wind_direction_emoji
)
from ..config import config_manager

# Type aliases
WeatherData = CurrentWeather
ForecastData = WeatherForecast


class CliInterface(IUserInterface):
    """Command-line interface implementation."""
    
    def __init__(self):
        """Initialize CLI interface."""
        self.config = config_manager.config
        logging.info("CLI interface initialized")
    
    def display_weather(self, weather_data: WeatherData) -> None:
        """Display current weather data."""
        print(f"\n🌤️  Current Weather for {weather_data.location.display_name}")
        print("=" * 60)
        
        # Temperature
        temp_str = format_temperature(
            weather_data.temperature.value,
            "C" if weather_data.temperature.unit.value == "metric" else "F"
        )
        print(f"🌡️  Temperature: {temp_str}")
        
        if weather_data.temperature.feels_like:
            feels_like_str = format_temperature(
                weather_data.temperature.feels_like,
                "C" if weather_data.temperature.unit.value == "metric" else "F"
            )
            print(f"   Feels like: {feels_like_str}")
        
        # Condition
        print(f"☁️  Condition: {weather_data.description.title()}")
        
        # Humidity
        print(f"💧 Humidity: {format_percentage(weather_data.humidity)}")
        
        # Pressure
        print(f"📊 Pressure: {format_pressure(weather_data.pressure.value)}")
        
        # Wind
        wind_emoji = get_wind_direction_emoji(weather_data.wind.direction)
        wind_speed_str = format_wind_speed(weather_data.wind.speed)
        print(f"💨 Wind: {wind_speed_str} {wind_emoji}")
        
        if weather_data.wind.direction:
            print(f"   Direction: {weather_data.wind.direction_name} ({weather_data.wind.direction}°)")
        
        # Additional info
        if weather_data.visibility:
            print(f"👁️  Visibility: {weather_data.visibility:.1f} km")
        
        if weather_data.uv_index:
            print(f"☀️  UV Index: {weather_data.uv_index}")
        
        # Precipitation
        if weather_data.precipitation:
            if weather_data.precipitation.rain_1h:
                print(f"🌧️  Rain (1h): {weather_data.precipitation.rain_1h} mm")
            if weather_data.precipitation.snow_1h:
                print(f"❄️  Snow (1h): {weather_data.precipitation.snow_1h} mm")
        
        # Timestamp
        if weather_data.timestamp:
            time_str = format_datetime(weather_data.timestamp, "default")
            print(f"⏰ Updated: {time_str}")
        
        # Severe weather warning
        if weather_data.is_severe_weather:
            print(f"\n⚠️  SEVERE WEATHER WARNING!")
        
        print()
    
    def display_forecast(self, forecast_data: ForecastData) -> None:
        """Display forecast data."""
        print(f"\n📅 {forecast_data.days_count}-Day Forecast for {forecast_data.location.display_name}")
        print("=" * 70)
        
        for i, day in enumerate(forecast_data.forecast_days):
            date_str = format_datetime(day.date, "date_only")
            day_name = day.date.strftime("%A")
            
            high_temp = format_temperature(
                day.temperature_high.value,
                "C" if day.temperature_high.unit.value == "metric" else "F"
            )
            low_temp = format_temperature(
                day.temperature_low.value,
                "C" if day.temperature_low.unit.value == "metric" else "F"
            )
            
            print(f"Day {i+1} - {day_name}, {date_str}")
            print(f"   🌡️  High: {high_temp}  Low: {low_temp}")
            print(f"   ☁️  {day.description.title()}")
            print(f"   💧 Humidity: {format_percentage(day.humidity)}")
            print(f"   💨 Wind: {format_wind_speed(day.wind.speed)}")
            
            if day.precipitation_chance > 0:
                print(f"   🌧️  Precipitation: {day.precipitation_chance}%")
            
            print()
    
    def get_user_input(self, prompt: str) -> str:
        """Get input from user."""
        try:
            return input(f"{prompt}: ").strip()
        except (KeyboardInterrupt, EOFError):
            return ""
    
    def show_error(self, message: str) -> None:
        """Show error message to user."""
        print(f"❌ Error: {message}")
    
    def show_message(self, message: str) -> None:
        """Show message to user."""
        print(f"ℹ️  {message}")
    
    def show_welcome(self) -> None:
        """Show welcome message."""
        title = self.config.ui.window_title
        print(f"\n{title}")
        print("=" * len(title))
        print("Welcome to your personal weather dashboard!")
        print()
    
    def show_menu(self) -> None:
        """Show main menu options."""
        print("\nOptions:")
        print("1. Get current weather")
        print("2. Get weather forecast")
        print("3. Search locations")
        print("4. View favorite cities")
        print("5. Add favorite city")
        print("6. Remove favorite city")
        print("7. Weather for all favorites")
        print("8. Show configuration")
        print("9. Clear cache")
        print("10. Exit")
    
    def get_menu_choice(self) -> str:
        """Get menu choice from user."""
        return self.get_user_input("\nEnter your choice (1-10)")
    
    def display_locations(self, locations: List[Any]) -> None:
        """Display search results for locations."""
        if not locations:
            print("No locations found.")
            return
        
        print(f"\nFound {len(locations)} location(s):")
        print("-" * 40)
        
        for i, location in enumerate(locations, 1):
            print(f"{i}. {location.display_name}")
            print(f"   Coordinates: {location.latitude:.4f}, {location.longitude:.4f}")
    
    def display_favorite_cities(self, favorites: List[FavoriteCity]) -> None:
        """Display favorite cities."""
        if not favorites:
            print("\n⭐ No favorite cities added yet.")
            return
        
        print(f"\n⭐ Your Favorite Cities ({len(favorites)}):")
        print("-" * 50)
        
        for i, fav in enumerate(favorites, 1):
            print(f"{i}. {fav.display_name}")
            
            if fav.added_date:
                added_str = format_datetime(fav.added_date, "date_only")
                print(f"   Added: {added_str}")
            
            if fav.last_viewed:
                viewed_str = format_datetime(fav.last_viewed, "default")
                print(f"   Last viewed: {viewed_str}")
            
            print()
    
    def display_favorites_weather(self, weather_data: Dict[str, Optional[WeatherData]]) -> None:
        """Display weather for favorite cities."""
        if not weather_data:
            print("\n⭐ No favorite cities to show weather for.")
            return
        
        print(f"\n⭐ Weather for Your Favorite Cities")
        print("=" * 60)
        
        for city_name, weather in weather_data.items():
            print(f"\n📍 {city_name}:")
            
            if weather:
                temp_str = format_temperature(
                    weather.temperature.value,
                    "C" if weather.temperature.unit.value == "metric" else "F"
                )
                print(f"   🌡️  {temp_str} - {weather.description.title()}")
                print(f"   💧 {format_percentage(weather.humidity)} humidity")
            else:
                print("   ❌ Weather data unavailable")
    
    def display_config(self, debug_info: Dict[str, Any]) -> None:
        """Display configuration information."""
        print("\n🔧 Configuration:")
        print("-" * 30)
        
        for key, value in debug_info.items():
            if key != 'features_enabled':
                print(f"   {key}: {value}")
            else:
                print(f"   features_enabled:")
                for feature, enabled in value.items():
                    status = "✅" if enabled else "❌"
                    print(f"     {feature}: {status}")
    
    def display_cache_stats(self, stats: Dict[str, Any]) -> None:
        """Display cache statistics."""
        print("\n📊 Cache Statistics:")
        print("-" * 25)
        print(f"   Total entries: {stats.get('total_entries', 0)}")
        print(f"   Active entries: {stats.get('active_entries', 0)}")
        print(f"   Expired entries: {stats.get('expired_entries', 0)}")
        
        cache_keys = stats.get('cache_keys', [])
        if cache_keys:
            print(f"   Cache keys: {', '.join(cache_keys[:5])}")
            if len(cache_keys) > 5:
                print(f"   ... and {len(cache_keys) - 5} more")
    
    def confirm_action(self, message: str) -> bool:
        """Get confirmation from user."""
        response = self.get_user_input(f"{message} (y/N)")
        return response.lower() in ['y', 'yes']
