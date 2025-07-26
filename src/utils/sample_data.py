"""Sample data for fallback when API is slow or unavailable."""

from datetime import datetime

from src.models.weather_models import (
    AtmosphericPressure,
    CurrentWeather,
    Location,
    Temperature,
    TemperatureUnit,
    WeatherCondition,
    Wind,
)


def get_sample_weather_data(city_name: str = "New York") -> CurrentWeather:
    """
    Generate sample weather data for immediate display while API loads.

    Args:
        city_name: Name of the city for the sample data

    Returns:
        Sample CurrentWeather object
    """
    return CurrentWeather(
        location=Location(
            name=city_name, country="US", latitude=40.7128, longitude=-74.0060
        ),
        condition=WeatherCondition.CLEAR,
        temperature=Temperature(
            value=22.0, unit=TemperatureUnit.CELSIUS, feels_like=24.0
        ),
        humidity=55,  # percentage
        pressure=AtmosphericPressure(
            value=1013.25, sea_level=1013.25, ground_level=1013.25
        ),
        wind=Wind(speed=3.2, direction=180, gust=None),
        visibility=10.0,  # km
        description="Clear sky",
        timestamp=datetime.now(),
    )
