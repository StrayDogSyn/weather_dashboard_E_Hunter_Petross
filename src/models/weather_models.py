"""
Domain models for the Weather Dashboard application.

This module contains the core business entities and value objects that represent
the fundamental concepts in the weather domain.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Type aliases for cleaner interfaces
WeatherData = "CurrentWeather"
ForecastData = "WeatherForecast"
LocationData = "Location"


class WeatherCondition(Enum):
    """Weather condition categories."""

    CLEAR = "clear"
    CLOUDS = "clouds"
    RAIN = "rain"
    SNOW = "snow"
    THUNDERSTORM = "thunderstorm"
    DRIZZLE = "drizzle"
    MIST = "mist"
    FOG = "fog"
    HAZE = "haze"


class TemperatureUnit(Enum):
    """Temperature unit options."""

    CELSIUS = "metric"
    FAHRENHEIT = "imperial"
    KELVIN = "standard"


@dataclass
class Location:
    """Represents a geographic location."""

    name: str
    country: str
    latitude: float
    longitude: float

    def __post_init__(self):
        """Validate location data."""
        if not (-90 <= self.latitude <= 90):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (-180 <= self.longitude <= 180):
            raise ValueError(f"Invalid longitude: {self.longitude}")

    @property
    def display_name(self) -> str:
        """Get formatted display name."""
        return f"{self.name}, {self.country}"


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
        return f"{self.value:.1f}{symbol}"


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
class CurrentWeather:
    """Represents current weather conditions."""

    location: Location
    temperature: Temperature
    condition: WeatherCondition
    description: str
    humidity: int  # percentage
    pressure: AtmosphericPressure
    wind: Wind
    precipitation: Optional[Precipitation] = None
    visibility: Optional[float] = None  # km
    uv_index: Optional[float] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now()

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
        )


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
