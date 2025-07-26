"""Weather icons and icon management for the Weather Dashboard.

This module provides weather condition icons using Unicode characters
and utilities for selecting appropriate icons based on weather conditions.
"""

from typing import Optional, Union, TYPE_CHECKING
from src.models.weather_models import WeatherCondition

if TYPE_CHECKING:
    from src.models.weather_models import Temperature


class WeatherIcons:
    """Weather condition icons using Unicode characters."""

    # Primary weather icons
    CLEAR = "☀️"
    PARTLY_CLOUDY = "⛅"
    CLOUDY = "☁️"
    OVERCAST = "☁️"
    RAIN = "🌧️"
    HEAVY_RAIN = "⛈️"
    SNOW = "❄️"
    FOG = "🌫️"
    WIND = "💨"
    HOT = "🔥"
    COLD = "🧊"
    DEFAULT = "🌤️"
    
    # Additional weather icons
    THUNDERSTORM = "⛈️"
    DRIZZLE = "🌦️"
    SLEET = "🌨️"
    HAIL = "🧊"
    TORNADO = "🌪️"
    HURRICANE = "🌀"
    SANDSTORM = "🌪️"
    MIST = "🌫️"
    HAZE = "😶‍🌫️"
    
    # Time-based icons
    SUNRISE = "🌅"
    SUNSET = "🌇"
    NIGHT_CLEAR = "🌙"
    NIGHT_CLOUDY = "☁️"
    
    # Seasonal icons
    SPRING = "🌸"
    SUMMER = "☀️"
    AUTUMN = "🍂"
    WINTER = "❄️"

    @classmethod
    def get_icon(cls, condition: Union[str, WeatherCondition], temperature: Optional[Union[float, 'Temperature']] = None) -> str:
        """Get appropriate weather icon for condition.
        
        Args:
            condition: Weather condition description (string) or WeatherCondition enum
            temperature: Temperature value (optional, for temperature-based icons) - can be float or Temperature object
            
        Returns:
            Unicode weather icon string
        """
        # Handle WeatherCondition enum
        if isinstance(condition, WeatherCondition):
            condition_str = condition.value
        else:
            condition_str = str(condition)
        
        condition_lower = condition_str.lower()

        # Temperature-based icons (takes precedence)
        if temperature is not None:
            # Handle Temperature object by extracting the value
            temp_value = temperature.value if hasattr(temperature, 'value') else temperature
            if temp_value > 85:
                return cls.HOT
            elif temp_value < 32:
                return cls.COLD

        # Condition-based icons
        if "clear" in condition_lower or "sunny" in condition_lower:
            return cls.CLEAR
        elif "partly" in condition_lower or "scattered" in condition_lower:
            return cls.PARTLY_CLOUDY
        elif "overcast" in condition_lower:
            return cls.OVERCAST
        elif "cloudy" in condition_lower or "cloud" in condition_lower:
            return cls.CLOUDY
        elif "thunderstorm" in condition_lower or "thunder" in condition_lower:
            return cls.THUNDERSTORM
        elif "rain" in condition_lower or "shower" in condition_lower:
            if "heavy" in condition_lower or "storm" in condition_lower:
                return cls.HEAVY_RAIN
            elif "drizzle" in condition_lower or "light" in condition_lower:
                return cls.DRIZZLE
            return cls.RAIN
        elif "snow" in condition_lower or "blizzard" in condition_lower:
            if "sleet" in condition_lower:
                return cls.SLEET
            return cls.SNOW
        elif "fog" in condition_lower or "mist" in condition_lower:
            if "mist" in condition_lower:
                return cls.MIST
            return cls.FOG
        elif "haze" in condition_lower:
            return cls.HAZE
        elif "wind" in condition_lower:
            return cls.WIND
        elif "tornado" in condition_lower:
            return cls.TORNADO
        elif "hurricane" in condition_lower or "cyclone" in condition_lower:
            return cls.HURRICANE
        elif "hail" in condition_lower:
            return cls.HAIL
        else:
            return cls.DEFAULT

    @classmethod
    def get_time_based_icon(cls, condition: str, is_night: bool = False) -> str:
        """Get weather icon considering time of day.
        
        Args:
            condition: Weather condition description
            is_night: Whether it's nighttime
            
        Returns:
            Unicode weather icon string
        """
        condition_lower = condition.lower()
        
        if is_night:
            if "clear" in condition_lower:
                return cls.NIGHT_CLEAR
            elif "cloud" in condition_lower:
                return cls.NIGHT_CLOUDY
        
        # Fall back to regular icon selection
        return cls.get_icon(condition)

    @classmethod
    def get_seasonal_icon(cls, season: str) -> str:
        """Get seasonal weather icon.
        
        Args:
            season: Season name ('spring', 'summer', 'autumn', 'winter')
            
        Returns:
            Unicode seasonal icon string
        """
        season_lower = season.lower()
        
        if season_lower in ['spring', 'spr']:
            return cls.SPRING
        elif season_lower in ['summer', 'sum']:
            return cls.SUMMER
        elif season_lower in ['autumn', 'fall', 'aut']:
            return cls.AUTUMN
        elif season_lower in ['winter', 'win']:
            return cls.WINTER
        else:
            return cls.DEFAULT

    @classmethod
    def get_all_icons(cls) -> dict:
        """Get all available weather icons.
        
        Returns:
            Dictionary mapping icon names to Unicode characters
        """
        return {
            'clear': cls.CLEAR,
            'partly_cloudy': cls.PARTLY_CLOUDY,
            'cloudy': cls.CLOUDY,
            'overcast': cls.OVERCAST,
            'rain': cls.RAIN,
            'heavy_rain': cls.HEAVY_RAIN,
            'thunderstorm': cls.THUNDERSTORM,
            'drizzle': cls.DRIZZLE,
            'snow': cls.SNOW,
            'sleet': cls.SLEET,
            'fog': cls.FOG,
            'mist': cls.MIST,
            'haze': cls.HAZE,
            'wind': cls.WIND,
            'hot': cls.HOT,
            'cold': cls.COLD,
            'tornado': cls.TORNADO,
            'hurricane': cls.HURRICANE,
            'hail': cls.HAIL,
            'sunrise': cls.SUNRISE,
            'sunset': cls.SUNSET,
            'night_clear': cls.NIGHT_CLEAR,
            'night_cloudy': cls.NIGHT_CLOUDY,
            'spring': cls.SPRING,
            'summer': cls.SUMMER,
            'autumn': cls.AUTUMN,
            'winter': cls.WINTER,
            'default': cls.DEFAULT,
        }

    @classmethod
    def get_icon_description(cls, icon: str) -> str:
        """Get description for a weather icon.
        
        Args:
            icon: Unicode weather icon
            
        Returns:
            Human-readable description of the icon
        """
        icon_descriptions = {
            cls.CLEAR: "Clear sky",
            cls.PARTLY_CLOUDY: "Partly cloudy",
            cls.CLOUDY: "Cloudy",
            cls.OVERCAST: "Overcast",
            cls.RAIN: "Rain",
            cls.HEAVY_RAIN: "Heavy rain",
            cls.THUNDERSTORM: "Thunderstorm",
            cls.DRIZZLE: "Light rain",
            cls.SNOW: "Snow",
            cls.SLEET: "Sleet",
            cls.FOG: "Fog",
            cls.MIST: "Mist",
            cls.HAZE: "Haze",
            cls.WIND: "Windy",
            cls.HOT: "Hot weather",
            cls.COLD: "Cold weather",
            cls.TORNADO: "Tornado",
            cls.HURRICANE: "Hurricane",
            cls.HAIL: "Hail",
            cls.SUNRISE: "Sunrise",
            cls.SUNSET: "Sunset",
            cls.NIGHT_CLEAR: "Clear night",
            cls.NIGHT_CLOUDY: "Cloudy night",
            cls.SPRING: "Spring weather",
            cls.SUMMER: "Summer weather",
            cls.AUTUMN: "Autumn weather",
            cls.WINTER: "Winter weather",
            cls.DEFAULT: "Weather",
        }
        
        return icon_descriptions.get(icon, "Unknown weather condition")