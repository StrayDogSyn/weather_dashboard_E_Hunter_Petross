"""Command-line interface for the Weather Dashboard application."""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..interfaces.weather_interfaces import IUserInterface
from ..models import CurrentWeather, WeatherForecast, FavoriteCity
from ..models.capstone_models import (
    WeatherComparison, JournalEntry, ActivitySuggestion, WeatherPoem, MoodType
)
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
    
    def show_main_menu(self) -> None:
        """Show enhanced main menu with capstone features."""
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
        print("")
        print("🌟 Capstone Features:")
        print("10. Compare two cities")
        print("11. Weather journal")
        print("12. Activity suggestions")
        print("13. Weather poetry")
        print("14. Exit")

    def get_enhanced_menu_choice(self) -> str:
        """Get menu choice from user for enhanced menu."""
        return self.get_user_input("\nEnter your choice (1-14)")

    # City Comparison Feature
    def display_weather_comparison(self, comparison: WeatherComparison) -> None:
        """Display weather comparison between two cities."""
        city1 = comparison.city1_weather
        city2 = comparison.city2_weather
        
        print(f"\n🌍 Weather Comparison")
        print("=" * 60)
        
        # Header with city names
        print(f"🏙️  {city1.location.display_name:<25} vs {city2.location.display_name}")
        print("-" * 60)
        
        # Temperature comparison
        temp1 = f"{city1.temperature.to_celsius():.1f}°C"
        temp2 = f"{city2.temperature.to_celsius():.1f}°C"
        temp_diff = abs(comparison.temperature_difference)
        
        print(f"🌡️  Temperature:     {temp1:<15} {temp2:<15}")
        if comparison.temperature_difference > 0:
            print(f"    ➡️  {city1.location.name} is {temp_diff:.1f}°C warmer")
        elif comparison.temperature_difference < 0:
            print(f"    ➡️  {city2.location.name} is {temp_diff:.1f}°C warmer")
        else:
            print(f"    ➡️  Same temperature")
        
        # Condition comparison
        print(f"☁️  Condition:       {city1.description.title():<15} {city2.description.title():<15}")
        
        # Humidity comparison
        print(f"💧 Humidity:        {city1.humidity}%{'':<12} {city2.humidity}%")
        if comparison.humidity_difference != 0:
            humid_diff = abs(comparison.humidity_difference)
            if comparison.humidity_difference > 0:
                print(f"    ➡️  {city1.location.name} is {humid_diff}% more humid")
            else:
                print(f"    ➡️  {city2.location.name} is {humid_diff}% more humid")
        
        # Wind comparison
        print(f"💨 Wind:            {city1.wind.speed}km/h {city1.wind.direction_name:<8} {city2.wind.speed}km/h {city2.wind.direction_name}")
        
        # Pressure comparison
        print(f"🌪️  Pressure:        {city1.pressure.value}hPa{'':<8} {city2.pressure.value}hPa")
        
        print("-" * 60)
        print(f"🏆 Better weather overall: {comparison.better_weather_city}")

    def get_cities_for_comparison(self) -> tuple[str, str]:
        """Get two city names for comparison."""
        print("\n🌍 City Weather Comparison")
        print("-" * 30)
        city1 = self.get_user_input("Enter first city name")
        if not city1:
            return "", ""
        
        city2 = self.get_user_input("Enter second city name")
        if not city2:
            return "", ""
        
        return city1, city2

    # Weather Journal Feature
    def display_journal_entry(self, entry: JournalEntry) -> None:
        """Display a single journal entry."""
        print(f"\n📔 Journal Entry - {entry.formatted_date}")
        print("-" * 40)
        print(f"📍 Location: {entry.location}")
        print(f"🌤️  Weather: {entry.weather_summary} ({entry.temperature:.1f}°C)")
        print(f"😊 Mood: {entry.mood_emoji} {entry.mood.value.title()}")
        print(f"📝 Notes: {entry.notes}")
        
        if entry.activities:
            print(f"🎯 Activities: {', '.join(entry.activities)}")
        
        print(f"📅 Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')}")

    def display_journal_entries(self, entries: list[JournalEntry]) -> None:
        """Display multiple journal entries."""
        if not entries:
            print("\n📔 No journal entries found.")
            return
        
        print(f"\n📔 Journal Entries ({len(entries)} found)")
        print("=" * 50)
        
        for entry in entries:
            print(f"📅 {entry.formatted_date} | {entry.location}")
            print(f"   {entry.mood_emoji} {entry.mood.value.title()} | {entry.weather_summary}")
            print(f"   📝 {entry.notes[:60]}{'...' if len(entry.notes) > 60 else ''}")
            print()

    def get_journal_entry_data(self) -> tuple[MoodType, str, list[str]]:
        """Get journal entry data from user."""
        print("\n📔 Create Weather Journal Entry")
        print("-" * 35)
        
        # Show mood options
        print("How are you feeling today?")
        moods = list(MoodType)
        for i, mood in enumerate(moods, 1):
            print(f"{i:2}. {mood.value.title()}")
        
        mood_choice = self.get_user_input(f"\nChoose mood (1-{len(moods)})")
        try:
            mood_index = int(mood_choice) - 1
            if 0 <= mood_index < len(moods):
                selected_mood = moods[mood_index]
            else:
                selected_mood = MoodType.CONTENT  # Default
        except ValueError:
            selected_mood = MoodType.CONTENT  # Default
        
        # Get notes
        notes = self.get_user_input("Write your thoughts about today's weather")
        
        # Get activities
        activities_input = self.get_user_input("What activities did you do today? (comma-separated)")
        activities = [activity.strip() for activity in activities_input.split(',') if activity.strip()]
        
        return selected_mood, notes, activities

    def show_journal_menu(self) -> str:
        """Show journal menu options."""
        print("\n📔 Weather Journal")
        print("-" * 20)
        print("1. Create today's entry")
        print("2. View recent entries")
        print("3. View entry by date")
        print("4. Search entries")
        print("5. Mood statistics")
        print("6. Export journal")
        print("7. Back to main menu")
        
        return self.get_user_input("Choose option (1-7)")

    # Activity Suggestions Feature
    def display_activity_suggestions(self, suggestions: ActivitySuggestion) -> None:
        """Display activity suggestions."""
        weather = suggestions.weather
        
        print(f"\n🎯 Activity Suggestions for {weather.location.display_name}")
        print("=" * 60)
        print(f"🌤️  Current Weather: {weather.description.title()}")
        print(f"🌡️  Temperature: {weather.temperature}")
        print(f"💨 Wind: {weather.wind.speed}km/h")
        print()
        
        if not suggestions.suggested_activities:
            print("😕 No suitable activities found for current conditions.")
            return
        
        # Top suggestion
        if suggestions.top_suggestion:
            top_activity, top_score = suggestions.suggested_activities[0]
            print(f"🏆 TOP RECOMMENDATION")
            print(f"   {top_activity.name}")
            print(f"   {top_activity.description}")
            print(f"   Suitability Score: {top_score:.1f}/10")
            print()
        
        # All suggestions
        print("💡 All Suggestions:")
        for i, (activity, score) in enumerate(suggestions.suggested_activities, 1):
            indoor_icon = "🏠" if activity.indoor else "🌞"
            print(f"{i:2}. {indoor_icon} {activity.name} (Score: {score:.1f})")
            if i == 1:  # Show description for top suggestion
                print(f"       {activity.description}")

    def show_activity_menu(self) -> str:
        """Show activity suggestions menu."""
        print("\n🎯 Activity Suggestions")
        print("-" * 25)
        print("1. Get suggestions for current weather")
        print("2. View indoor activities only")
        print("3. View outdoor activities only")
        print("4. Activity details")
        print("5. Back to main menu")
        
        return self.get_user_input("Choose option (1-5)")

    # Weather Poetry Feature
    def display_weather_poem(self, poem: WeatherPoem) -> None:
        """Display a weather poem."""
        if poem.poem_type == "haiku":
            print("\n🌸 Weather Haiku")
            print("-" * 20)
            lines = poem.text.split(" / ")
            for line in lines:
                print(f"   {line}")
        elif poem.poem_type == "phrase":
            print("\n💭 Weather Wisdom")
            print("-" * 20)
            print(f"   {poem.text}")
        elif poem.poem_type == "limerick":
            print("\n🎵 Weather Limerick")
            print("-" * 20)
            lines = poem.text.split(" / ")
            for line in lines:
                print(f"   {line}")
        
        print(f"\n   📍 Inspired by: {poem.weather_condition.value.title()} weather")
        print(f"   🌡️  Temperature: {poem.temperature_range.title()}")

    def display_poetry_collection(self, poems: list[WeatherPoem]) -> None:
        """Display a collection of weather poems."""
        print(f"\n🎨 Weather Poetry Collection ({len(poems)} poems)")
        print("=" * 50)
        
        for i, poem in enumerate(poems, 1):
            self.display_weather_poem(poem)
            if i < len(poems):
                print("\n" + "~" * 30)

    def show_poetry_menu(self) -> str:
        """Show poetry menu options."""
        print("\n🎨 Weather Poetry")
        print("-" * 18)
        print("1. Generate random poem")
        print("2. Generate haiku")
        print("3. Generate fun phrase")
        print("4. Generate limerick")
        print("5. Poetry collection")
        print("6. Back to main menu")
        
        return self.get_user_input("Choose option (1-6)")

    def show_statistics(self, stats: dict) -> None:
        """Display various statistics."""
        print("\n📊 Statistics")
        print("-" * 15)
        for key, value in stats.items():
            if isinstance(value, dict):
                print(f"{key.replace('_', ' ').title()}:")
                for sub_key, sub_value in value.items():
                    print(f"  {sub_key}: {sub_value}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")

    def get_date_input(self) -> str:
        """Get date input from user."""
        return self.get_user_input("Enter date (YYYY-MM-DD) or press Enter for today")

    def get_search_query(self) -> str:
        """Get search query from user."""
        return self.get_user_input("Enter search terms")
    
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
