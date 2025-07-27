"""
Enhanced Domain Models for the Weather Dashboard Application.

This module contains enhanced core business entities and value objects with
AI integration, design patterns, and advanced functionality for weather data.

Enhancements:
- AI-powered weather analysis and insights
- Factory and Builder patterns for complex object creation
- Validation and error handling
- Rich metadata and analytics
- Extensible architecture for future enhancements
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union
from uuid import UUID, uuid4

# Type aliases for cleaner interfaces
WeatherData = "CurrentWeather"
ForecastData = "WeatherForecast"
LocationData = "Location"


# Enhanced protocols for extensibility
class WeatherAnalyzer(Protocol):
    """Protocol for weather analysis components."""

    def analyze_weather(self, weather: "CurrentWeather") -> Dict[str, Any]:
        """Analyze weather data and return insights."""
        ...


class AIEnhancedWeatherModel(ABC):
    """Abstract base class for AI-enhanced weather models."""

    @abstractmethod
    def generate_ai_insights(
        self, gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI insights for this weather model."""
        pass

    def _call_gemini_api(self, prompt: str, api_key: str) -> Optional[str]:
        """Call Gemini API for AI insights."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text.strip() if response.text else None
        except Exception as e:
            logging.warning(f"Gemini API call failed: {e}")
            return None


class WeatherCondition(Enum):
    """Enhanced weather condition categories with metadata."""

    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    DRIZZLE = "drizzle"
    MIST = "mist"
    FOG = "fog"
    HAZE = "haze"

    @property
    def emoji(self) -> str:
        """Get emoji representation of weather condition."""
        emoji_map = {
            "clear": "☀️",
            "clouds": "☁️",
            "rain": "🌧️",
            "snow": "❄️",
            "thunderstorm": "⛈️",
            "drizzle": "🌦️",
            "mist": "🌫️",
            "fog": "🌫️",
            "haze": "🌫️",
        }
        return emoji_map.get(self.value, "🌤️")

    @property
    def severity_level(self) -> int:
        """Get severity level (0-10, higher is more severe)."""
        severity_map = {
            "clear": 0,
            "clouds": 1,
            "haze": 2,
            "mist": 3,
            "fog": 4,
            "drizzle": 5,
            "rain": 6,
            "snow": 7,
            "thunderstorm": 9,
        }
        return severity_map.get(self.value, 2)

    @property
    def is_precipitation(self) -> bool:
        """Check if condition involves precipitation."""
        return self.value in ["rain", "snow", "drizzle", "thunderstorm"]

    @property
    def visibility_impact(self) -> str:
        """Get visibility impact description."""
        impact_map = {
            "clear": "excellent",
            "clouds": "good",
            "haze": "moderate",
            "mist": "reduced",
            "fog": "poor",
            "drizzle": "moderate",
            "rain": "reduced",
            "snow": "poor",
            "thunderstorm": "very_poor",
        }
        return impact_map.get(self.value, "moderate")


class TemperatureUnit(Enum):
    """Enhanced temperature unit options with conversion utilities."""

    CELSIUS = "metric"
    FAHRENHEIT = "imperial"
    KELVIN = "standard"

    @property
    def symbol(self) -> str:
        """Get temperature unit symbol."""
        symbol_map = {"metric": "°C", "imperial": "°F", "standard": "K"}
        return symbol_map.get(self.value, "°C")

    @property
    def display_name(self) -> str:
        """Get display name for temperature unit."""
        name_map = {"metric": "Celsius", "imperial": "Fahrenheit", "standard": "Kelvin"}
        return name_map.get(self.value, "Celsius")

    @classmethod
    def from_symbol(cls, symbol: str) -> "TemperatureUnit":
        """Create temperature unit from symbol."""
        symbol_map = {
            "°C": cls.CELSIUS,
            "°F": cls.FAHRENHEIT,
            "K": cls.KELVIN,
            "C": cls.CELSIUS,
            "F": cls.FAHRENHEIT,
        }
        return symbol_map.get(symbol, cls.CELSIUS)


@dataclass
class Location(AIEnhancedWeatherModel):
    """Enhanced geographic location with validation and utilities."""

    name: str
    country: str
    latitude: float
    longitude: float
    id: UUID = field(default_factory=uuid4)
    timezone: Optional[str] = None
    elevation: Optional[float] = None  # meters above sea level
    population: Optional[int] = None
    region: Optional[str] = None  # state/province
    country_code: Optional[str] = None  # ISO country code
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        """Validate location data and set defaults."""
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")

        # Auto-set country code if not provided
        if not self.country_code and self.country:
            self.country_code = self._get_country_code(self.country)

    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        if self.region:
            return f"{self.name}, {self.region}, {self.country}"
        return f"{self.name}, {self.country}"

    @property
    def coordinates(self) -> Tuple[float, float]:
        """Get coordinates as (latitude, longitude) tuple."""
        return (self.latitude, self.longitude)

    @property
    def hemisphere(self) -> str:
        """Get hemisphere (northern/southern)."""
        return "northern" if self.latitude >= 0 else "southern"

    def distance_to(self, other: "Location") -> float:
        """Calculate distance to another location in kilometers using Haversine formula."""
        import math

        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(
            math.radians,
            [self.latitude, self.longitude, other.latitude, other.longitude],
        )

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in kilometers
        r = 6371
        return c * r

    def is_nearby(self, other: "Location", threshold_km: float = 50.0) -> bool:
        """Check if another location is within threshold distance."""
        return self.distance_to(other) <= threshold_km

    def _get_country_code(self, country: str) -> str:
        """Get ISO country code from country name (simplified mapping)."""
        country_codes = {
            "united states": "US",
            "canada": "CA",
            "united kingdom": "GB",
            "germany": "DE",
            "france": "FR",
            "japan": "JP",
            "australia": "AU",
            "brazil": "BR",
            "india": "IN",
            "china": "CN",
        }
        return country_codes.get(country.lower(), "XX")

    def generate_ai_insights(
        self, gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI insights about this location."""
        if not gemini_api_key:
            return {"status": "no_api_key", "insights": []}

        prompt = f"""Provide interesting facts and insights about {self.display_name}.
Focus on:
- Climate characteristics
- Geography and notable features
- Travel and tourism highlights
- Cultural significance

Return as JSON with keys: climate, geography, tourism, culture."""

        ai_response = self._call_gemini_api(prompt, gemini_api_key)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return {"status": "success", "raw_insights": ai_response}

        return {"status": "api_failed", "insights": []}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self.name,
            "country": self.country,
            "country_code": self.country_code,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "elevation": self.elevation,
            "population": self.population,
            "hemisphere": self.hemisphere,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Temperature:
    """Represents temperature with unit information."""

    value: float
    unit: TemperatureUnit
    feels_like: Optional[float] = None

    def to_celsius(self) -> float:
        """Convert temperature to Celsius."""
        if self.unit == TemperatureUnit.CELSIUS:
            return self.value
        elif self.unit == TemperatureUnit.FAHRENHEIT:
            return (self.value - 32) * 5 / 9
        else:  # Kelvin
            return self.value - 273.15

    def to_fahrenheit(self) -> float:
        """Convert temperature to Fahrenheit."""
        if self.unit == TemperatureUnit.FAHRENHEIT:
            return self.value
        elif self.unit == TemperatureUnit.CELSIUS:
            return (self.value * 9 / 5) + 32
        else:  # Kelvin
            return (self.value - 273.15) * 9 / 5 + 32

    def __str__(self) -> str:
        """String representation of temperature."""
        symbol = (
            "°C"
            if self.unit == TemperatureUnit.CELSIUS
            else "°F" if self.unit == TemperatureUnit.FAHRENHEIT else "K"
        )
        return f"{self.value: .1f}{symbol}"

    def __format__(self, format_spec: str) -> str:
        """Format temperature value for f-strings."""
        # If no format spec, return string representation
        if not format_spec:
            return str(self)

        # For numeric format specs, format just the value
        try:
            return format(self.value, format_spec)
        except (ValueError, TypeError):
            # Fallback to string representation
            return str(self)


@dataclass
class Wind:
    """Represents wind information."""

    speed: float
    direction: Optional[int] = None  # degrees
    gust: Optional[float] = None

    @property
    def direction_name(self) -> str:
        """Get wind direction name."""
        if self.direction is None:
            return "Unknown"

        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]
        index = round(self.direction / 22.5) % 16
        return directions[index]


@dataclass
class Precipitation:
    """Represents precipitation information."""

    rain_1h: Optional[float] = None  # mm
    rain_3h: Optional[float] = None  # mm
    snow_1h: Optional[float] = None  # mm
    snow_3h: Optional[float] = None  # mm

    @property
    def total_precipitation(self) -> float:
        """Get total precipitation in mm."""
        total = 0.0
        if self.rain_1h:
            total += self.rain_1h
        if self.snow_1h:
            total += self.snow_1h
        return total


@dataclass
class AtmosphericPressure:
    """Represents atmospheric pressure."""

    value: float  # hPa
    sea_level: Optional[float] = None  # hPa
    ground_level: Optional[float] = None  # hPa


@dataclass
class CurrentWeather(AIEnhancedWeatherModel):
    """Enhanced current weather conditions with AI insights and analytics."""

    location: Location
    temperature: Temperature
    condition: WeatherCondition
    description: str
    humidity: int  # percentage
    pressure: AtmosphericPressure
    wind: Wind
    id: UUID = field(default_factory=uuid4)
    precipitation: Optional[Precipitation] = None
    visibility: Optional[float] = None  # km
    uv_index: Optional[float] = None
    air_quality_index: Optional[int] = None
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    moon_phase: Optional[str] = None
    timestamp: Optional[datetime] = None
    data_source: str = "unknown"
    confidence_score: float = 1.0  # 0.0 to 1.0

    def __post_init__(self):
        """Set timestamp if not provided and validate data."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

        # Validate humidity
        if not (0 <= self.humidity <= 100):
            raise ValueError(f"Invalid humidity: {self.humidity}%")

        # Validate UV index
        if self.uv_index is not None and self.uv_index < 0:
            raise ValueError(f"Invalid UV index: {self.uv_index}")

    @property
    def is_severe_weather(self) -> bool:
        """Check if weather conditions are severe."""
        return (
            self.condition in [WeatherCondition.THUNDERSTORM, WeatherCondition.SNOW]
            or (self.wind.speed > 50)  # Strong wind
            or (
                self.precipitation is not None
                and self.precipitation.total_precipitation > 10
            )  # Heavy precipitation
            or (self.uv_index is not None and self.uv_index >= 8)  # Very high UV
        )

    @property
    def comfort_level(self) -> str:
        """Get human comfort level based on conditions."""
        temp_c = self.temperature.to_celsius()

        # Temperature comfort
        if temp_c < 0:
            temp_comfort = "very_cold"
        elif temp_c < 10:
            temp_comfort = "cold"
        elif temp_c < 20:
            temp_comfort = "cool"
        elif temp_c < 26:
            temp_comfort = "comfortable"
        elif temp_c < 30:
            temp_comfort = "warm"
        else:
            temp_comfort = "hot"

        # Humidity comfort
        if self.humidity < 30:
            humidity_comfort = "dry"
        elif self.humidity < 60:
            humidity_comfort = "comfortable"
        else:
            humidity_comfort = "humid"

        # Overall comfort
        if temp_comfort == "comfortable" and humidity_comfort == "comfortable":
            return "very_comfortable"
        elif temp_comfort in ["cool", "warm"] and humidity_comfort != "humid":
            return "comfortable"
        elif temp_comfort in ["cold", "hot"] or humidity_comfort == "humid":
            return "uncomfortable"
        else:
            return "very_uncomfortable"

    @property
    def feels_like_description(self) -> str:
        """Get human-readable description of how it feels."""
        temp_c = self.temperature.to_celsius()
        feels_like = self.temperature.feels_like or temp_c

        if feels_like > temp_c + 3:
            return "feels warmer due to humidity"
        elif feels_like < temp_c - 3:
            return "feels cooler due to wind chill"
        else:
            return "feels like actual temperature"

    @property
    def activity_suitability(self) -> Dict[str, str]:
        """Get activity suitability ratings."""
        temp_c = self.temperature.to_celsius()

        # Base suitability on temperature and conditions
        outdoor_rating = "good"
        if temp_c < 0 or temp_c > 35:
            outdoor_rating = "poor"
        elif temp_c < 5 or temp_c > 30:
            outdoor_rating = "fair"
        elif self.is_severe_weather:
            outdoor_rating = "poor"
        elif self.condition.is_precipitation:
            outdoor_rating = "fair"

        indoor_rating = "excellent" if self.condition.is_precipitation else "good"

        return {
            "outdoor_activities": outdoor_rating,
            "indoor_activities": indoor_rating,
            "water_activities": (
                "good" if 20 <= temp_c <= 30 and not self.is_severe_weather else "poor"
            ),
            "winter_sports": (
                "excellent" if self.condition == WeatherCondition.SNOW else "poor"
            ),
        }

    @property
    def air_quality_description(self) -> str:
        """Get air quality description."""
        if self.air_quality_index is None:
            return "unknown"

        aqi = self.air_quality_index
        if aqi <= 50:
            return "good"
        elif aqi <= 100:
            return "moderate"
        elif aqi <= 150:
            return "unhealthy for sensitive groups"
        elif aqi <= 200:
            return "unhealthy"
        elif aqi <= 300:
            return "very unhealthy"
        else:
            return "hazardous"

    def generate_ai_insights(
        self, gemini_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate AI insights about current weather conditions."""
        if not gemini_api_key:
            return {"status": "no_api_key", "insights": []}

        prompt = f"""Analyze the current weather conditions for {self.location.display_name}:
        
Temperature: {self.temperature}
Condition: {self.condition.value} - {self.description}
Humidity: {self.humidity}%
Wind: {self.wind.speed} km/h from {self.wind.direction_name}
Pressure: {self.pressure.value} hPa
Visibility: {self.visibility or 'unknown'} km
UV Index: {self.uv_index or 'unknown'}

Provide insights about:
1. What this weather means for daily activities
2. Health and safety considerations
3. What to expect in the next few hours
4. Recommendations for clothing and preparations

Format as JSON with keys: activities, health_safety, short_term_outlook, recommendations."""

        ai_response = self._call_gemini_api(prompt, gemini_api_key)
        if ai_response:
            try:
                insights = json.loads(ai_response)
                insights["generated_at"] = datetime.now(timezone.utc).isoformat()
                return insights
            except json.JSONDecodeError:
                return {
                    "status": "success",
                    "raw_insights": ai_response,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }

        return {"status": "api_failed", "insights": []}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "location": self.location.to_dict(),
            "temperature": {
                "value": self.temperature.value,
                "unit": self.temperature.unit.value,
                "feels_like": self.temperature.feels_like,
            },
            "condition": self.condition.value,
            "description": self.description,
            "humidity": self.humidity,
            "pressure": {
                "value": self.pressure.value,
                "sea_level": self.pressure.sea_level,
                "ground_level": self.pressure.ground_level,
            },
            "wind": {
                "speed": self.wind.speed,
                "direction": self.wind.direction,
                "gust": self.wind.gust,
            },
            "visibility": self.visibility,
            "uv_index": self.uv_index,
            "air_quality_index": self.air_quality_index,
            "sunrise": self.sunrise.isoformat() if self.sunrise else None,
            "sunset": self.sunset.isoformat() if self.sunset else None,
            "moon_phase": self.moon_phase,
            "timestamp": self.timestamp.isoformat(),
            "data_source": self.data_source,
            "confidence_score": self.confidence_score,
            "is_severe_weather": self.is_severe_weather,
            "comfort_level": self.comfort_level,
            "activity_suitability": self.activity_suitability,
        }


@dataclass
class WeatherForecastDay:
    """Represents a single day in weather forecast."""

    date: datetime
    temperature_high: Temperature
    temperature_low: Temperature
    condition: WeatherCondition
    description: str
    humidity: int
    wind: Wind
    precipitation_chance: int  # percentage
    precipitation: Optional[Precipitation] = None


@dataclass
class WeatherForecast:
    """Represents multi-day weather forecast."""

    location: Location
    forecast_days: List[WeatherForecastDay]
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

    @property
    def days_count(self) -> int:
        """Get number of forecast days."""
        return len(self.forecast_days)

    def get_day(self, index: int) -> Optional[WeatherForecastDay]:
        """Get forecast for specific day."""
        if 0 <= index < len(self.forecast_days):
            return self.forecast_days[index]
        return None


@dataclass
class WeatherAlert:
    """Represents weather alert/warning."""

    title: str
    description: str
    severity: str  # "minor", "moderate", "severe", "extreme"
    start_time: datetime
    end_time: datetime
    areas: List[str]

    @property
    def is_active(self) -> bool:
        """Check if alert is currently active."""
        now = datetime.now()
        return self.start_time <= now <= self.end_time

    @property
    def is_severe(self) -> bool:
        """Check if alert is severe or extreme."""
        return self.severity in ["severe", "extreme"]


@dataclass
class FavoriteCity:
    """Represents a user's favorite city."""

    location: Location
    nickname: Optional[str] = None
    added_date: Optional[datetime] = None
    last_viewed: Optional[datetime] = None

    def __post_init__(self):
        """Set added_date if not provided."""
        if self.added_date is None:
            self.added_date = datetime.now()

    @property
    def display_name(self) -> str:
        """Get display name (nickname or location name)."""
        return self.nickname if self.nickname else self.location.display_name

    def mark_viewed(self):
        """Mark as recently viewed."""
        self.last_viewed = datetime.now()


# Value objects for API responses
@dataclass
class APIResponse:
    """Base class for API responses."""

    success: bool
    timestamp: Optional[datetime] = None
    source: str = "unknown"  # API source name

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class WeatherAPIResponse(APIResponse):
    """Weather API response wrapper."""

    data: Optional[CurrentWeather] = None
    error_message: Optional[str] = None
    rate_limit_remaining: Optional[int] = None


@dataclass
class ForecastAPIResponse(APIResponse):
    """Forecast API response wrapper."""

    data: Optional[WeatherForecast] = None
    error_message: Optional[str] = None
    rate_limit_remaining: Optional[int] = None


# Factory and Builder Patterns
class WeatherFactory:
    """Factory for creating weather-related objects."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize factory with optional AI capabilities."""
        self.gemini_api_key = gemini_api_key
        self.logger = logging.getLogger(__name__)

    def create_location(
        self, name: str, country: str, latitude: float, longitude: float, **kwargs
    ) -> Location:
        """Create a Location with optional enhancements."""
        location = Location(
            name=name, country=country, latitude=latitude, longitude=longitude, **kwargs
        )

        # Add AI insights if API key available
        if self.gemini_api_key:
            try:
                location.generate_ai_insights(self.gemini_api_key)
                self.logger.info(
                    f"Generated AI insights for location: {location.display_name}"
                )
            except Exception as e:
                self.logger.warning(f"Failed to generate AI insights for location: {e}")

        return location

    def create_current_weather(
        self,
        location: Location,
        temperature_value: float,
        temperature_unit: TemperatureUnit,
        condition: WeatherCondition,
        description: str,
        humidity: int,
        pressure_value: float,
        wind_speed: float,
        **kwargs,
    ) -> CurrentWeather:
        """Create CurrentWeather with all required components."""
        temperature = Temperature(
            temperature_value, temperature_unit, kwargs.get("feels_like")
        )
        pressure = AtmosphericPressure(
            pressure_value,
            kwargs.get("sea_level_pressure"),
            kwargs.get("ground_level_pressure"),
        )
        wind = Wind(wind_speed, kwargs.get("wind_direction"), kwargs.get("wind_gust"))

        # Handle precipitation if provided
        precipitation = None
        if any(key in kwargs for key in ["rain_1h", "rain_3h", "snow_1h", "snow_3h"]):
            precipitation = Precipitation(
                kwargs.get("rain_1h"),
                kwargs.get("rain_3h"),
                kwargs.get("snow_1h"),
                kwargs.get("snow_3h"),
            )

        weather = CurrentWeather(
            location=location,
            temperature=temperature,
            condition=condition,
            description=description,
            humidity=humidity,
            pressure=pressure,
            wind=wind,
            precipitation=precipitation,
            visibility=kwargs.get("visibility"),
            uv_index=kwargs.get("uv_index"),
            air_quality_index=kwargs.get("air_quality_index"),
            sunrise=kwargs.get("sunrise"),
            sunset=kwargs.get("sunset"),
            moon_phase=kwargs.get("moon_phase"),
            data_source=kwargs.get("data_source", "factory"),
            confidence_score=kwargs.get("confidence_score", 1.0),
        )

        # Add AI insights if API key available
        if self.gemini_api_key:
            try:
                weather.generate_ai_insights(self.gemini_api_key)
                self.logger.info(
                    f"Generated AI insights for weather: {location.display_name}"
                )
            except Exception as e:
                self.logger.warning(f"Failed to generate AI insights for weather: {e}")

        return weather


class CurrentWeatherBuilder:
    """Builder pattern for creating complex CurrentWeather objects."""

    def __init__(self):
        """Initialize builder."""
        self._location: Optional[Location] = None
        self._temperature_value: Optional[float] = None
        self._temperature_unit: TemperatureUnit = TemperatureUnit.CELSIUS
        self._feels_like: Optional[float] = None
        self._condition: Optional[WeatherCondition] = None
        self._description: str = ""
        self._humidity: int = 50
        self._pressure_value: float = 1013.25
        self._wind_speed: float = 0.0
        self._wind_direction: Optional[int] = None
        self._visibility: Optional[float] = None
        self._uv_index: Optional[float] = None
        self._data_source: str = "builder"
        self._gemini_api_key: Optional[str] = None

    def with_location(self, location: Location) -> "CurrentWeatherBuilder":
        """Set location."""
        self._location = location
        return self

    def with_temperature(
        self,
        value: float,
        unit: TemperatureUnit = TemperatureUnit.CELSIUS,
        feels_like: Optional[float] = None,
    ) -> "CurrentWeatherBuilder":
        """Set temperature details."""
        self._temperature_value = value
        self._temperature_unit = unit
        self._feels_like = feels_like
        return self

    def with_condition(
        self, condition: WeatherCondition, description: str = ""
    ) -> "CurrentWeatherBuilder":
        """Set weather condition."""
        self._condition = condition
        self._description = description or condition.value
        return self

    def with_atmosphere(
        self, humidity: int, pressure: float
    ) -> "CurrentWeatherBuilder":
        """Set atmospheric conditions."""
        self._humidity = humidity
        self._pressure_value = pressure
        return self

    def with_wind(
        self, speed: float, direction: Optional[int] = None
    ) -> "CurrentWeatherBuilder":
        """Set wind conditions."""
        self._wind_speed = speed
        self._wind_direction = direction
        return self

    def with_visibility(self, visibility: float) -> "CurrentWeatherBuilder":
        """Set visibility."""
        self._visibility = visibility
        return self

    def with_uv_index(self, uv_index: float) -> "CurrentWeatherBuilder":
        """Set UV index."""
        self._uv_index = uv_index
        return self

    def with_data_source(self, source: str) -> "CurrentWeatherBuilder":
        """Set data source."""
        self._data_source = source
        return self

    def with_ai_enhancement(self, api_key: str) -> "CurrentWeatherBuilder":
        """Enable AI enhancement."""
        self._gemini_api_key = api_key
        return self

    def build(self) -> CurrentWeather:
        """Build the CurrentWeather object."""
        if not self._location:
            raise ValueError("Location is required")
        if self._temperature_value is None:
            raise ValueError("Temperature is required")
        if not self._condition:
            raise ValueError("Weather condition is required")

        factory = WeatherFactory(self._gemini_api_key)
        return factory.create_current_weather(
            location=self._location,
            temperature_value=self._temperature_value,
            temperature_unit=self._temperature_unit,
            condition=self._condition,
            description=self._description,
            humidity=self._humidity,
            pressure_value=self._pressure_value,
            wind_speed=self._wind_speed,
            feels_like=self._feels_like,
            wind_direction=self._wind_direction,
            visibility=self._visibility,
            uv_index=self._uv_index,
            data_source=self._data_source,
        )


# Convenience functions
def create_location_from_dict(
    data: Dict[str, Any], gemini_api_key: Optional[str] = None
) -> Location:
    """Create Location from dictionary data."""
    factory = WeatherFactory(gemini_api_key)
    return factory.create_location(
        name=data["name"],
        country=data["country"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        **{
            k: v
            for k, v in data.items()
            if k not in ["name", "country", "latitude", "longitude"]
        },
    )


def create_weather_from_api_response(
    response_data: Dict[str, Any], gemini_api_key: Optional[str] = None
) -> CurrentWeather:
    """Create CurrentWeather from API response data."""
    factory = WeatherFactory(gemini_api_key)

    # Extract location data
    location = factory.create_location(
        name=response_data.get("name", "Unknown"),
        country=response_data.get("sys", {}).get("country", "Unknown"),
        latitude=response_data.get("coord", {}).get("lat", 0.0),
        longitude=response_data.get("coord", {}).get("lon", 0.0),
    )

    # Extract weather data
    main = response_data.get("main", {})
    weather = response_data.get("weather", [{}])[0]
    wind_data = response_data.get("wind", {})

    return factory.create_current_weather(
        location=location,
        temperature_value=main.get("temp", 20.0),
        temperature_unit=TemperatureUnit.CELSIUS,
        condition=WeatherCondition(weather.get("main", "clear").lower()),
        description=weather.get("description", ""),
        humidity=main.get("humidity", 50),
        pressure_value=main.get("pressure", 1013.25),
        wind_speed=wind_data.get("speed", 0.0),
        feels_like=main.get("feels_like"),
        wind_direction=wind_data.get("deg"),
        visibility=(
            response_data.get("visibility", 0) / 1000
            if response_data.get("visibility")
            else None
        ),  # Convert m to km
        uv_index=response_data.get("uvi"),
        data_source="openweathermap",
    )
