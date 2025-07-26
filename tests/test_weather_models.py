"""
Unit tests for weather models and data structures.

Tests the core domain models including Location, CurrentWeather,
WeatherForecast, and related data validation.
"""

import os

# Import the models to test
import sys
import unittest
from datetime import datetime, timedelta
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.models.weather_models import (
    AtmosphericPressure,
    CurrentWeather,
    Location,
    Precipitation,
    Temperature,
    TemperatureUnit,
    WeatherCondition,
    WeatherForecast,
    WeatherForecastDay,
    Wind,
)


class TestLocationModel(unittest.TestCase):
    """Test cases for the Location model."""

    def setUp(self):
        """Set up test data."""
        self.valid_location_data = {
            "name": "New York",
            "country": "US",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

    def test_valid_location_creation(self):
        """Test creating a valid location."""
        location = Location(**self.valid_location_data)

        self.assertEqual(location.name, "New York")
        self.assertEqual(location.country, "US")
        self.assertEqual(location.latitude, 40.7128)
        self.assertEqual(location.longitude, -74.0060)

    def test_invalid_latitude_raises_error(self):
        """Test that invalid latitude raises ValueError."""
        invalid_data = self.valid_location_data.copy()
        invalid_data["latitude"] = 95.0  # Invalid latitude > 90

        with self.assertRaises(ValueError) as context:
            Location(**invalid_data)

        self.assertIn("Invalid latitude", str(context.exception))

    def test_invalid_longitude_raises_error(self):
        """Test that invalid longitude raises ValueError."""
        invalid_data = self.valid_location_data.copy()
        invalid_data["longitude"] = 185.0  # Invalid longitude > 180

        with self.assertRaises(ValueError) as context:
            Location(**invalid_data)

        self.assertIn("Invalid longitude", str(context.exception))

    def test_location_equality(self):
        """Test location equality comparison."""
        location1 = Location(**self.valid_location_data)
        location2 = Location(**self.valid_location_data)

        self.assertEqual(location1, location2)

    def test_location_display_name(self):
        """Test location display name property."""
        location = Location(**self.valid_location_data)
        display_name = location.display_name

        self.assertEqual(display_name, "New York, US")


class TestTemperatureModel(unittest.TestCase):
    """Test cases for the Temperature model."""

    def test_celsius_to_fahrenheit_conversion(self):
        """Test temperature conversion from Celsius to Fahrenheit."""
        temp = Temperature(value=20.0, unit=TemperatureUnit.CELSIUS)
        fahrenheit = temp.to_fahrenheit()

        expected = (20.0 * 9 / 5) + 32
        self.assertAlmostEqual(fahrenheit, expected, places=1)

    def test_fahrenheit_to_celsius_conversion(self):
        """Test temperature conversion from Fahrenheit to Celsius."""
        temp = Temperature(value=68.0, unit=TemperatureUnit.FAHRENHEIT)
        celsius = temp.to_celsius()

        expected = (68.0 - 32) * 5 / 9
        self.assertAlmostEqual(celsius, expected, places=1)

    def test_temperature_string_representation(self):
        """Test temperature string representation."""
        temp_c = Temperature(value=20.0, unit=TemperatureUnit.CELSIUS)
        temp_f = Temperature(value=68.0, unit=TemperatureUnit.FAHRENHEIT)

        self.assertEqual(str(temp_c), "20.0°C")
        self.assertEqual(str(temp_f), "68.0°F")


class TestWindModel(unittest.TestCase):
    """Test cases for the Wind model."""

    def test_wind_direction_name(self):
        """Test wind direction name calculation."""
        wind_north = Wind(speed=10.0, direction=0)
        wind_east = Wind(speed=15.0, direction=90)
        wind_south = Wind(speed=12.0, direction=180)
        wind_west = Wind(speed=8.0, direction=270)

        self.assertEqual(wind_north.direction_name, "N")
        self.assertEqual(wind_east.direction_name, "E")
        self.assertEqual(wind_south.direction_name, "S")
        self.assertEqual(wind_west.direction_name, "W")

    def test_wind_without_direction(self):
        """Test wind without direction information."""
        wind = Wind(speed=10.0)

        self.assertEqual(wind.direction_name, "Unknown")


class TestCurrentWeatherModel(unittest.TestCase):
    """Test cases for the CurrentWeather model."""

    def setUp(self):
        """Set up test data."""
        self.location = Location(
            name="London", country="UK", latitude=51.5074, longitude=-0.1278
        )

        self.temperature = Temperature(
            value=15.5, unit=TemperatureUnit.CELSIUS, feels_like=16.2
        )

        self.pressure = AtmosphericPressure(value=1013.0)
        self.wind = Wind(speed=8.5, direction=180)

        self.valid_weather_data = {
            "location": self.location,
            "temperature": self.temperature,
            "condition": WeatherCondition.CLOUDS,
            "description": "Partly cloudy",
            "humidity": 65,
            "pressure": self.pressure,
            "wind": self.wind,
        }

    def test_valid_current_weather_creation(self):
        """Test creating valid current weather."""
        weather = CurrentWeather(**self.valid_weather_data)

        self.assertEqual(weather.location, self.location)
        self.assertEqual(weather.temperature, self.temperature)
        self.assertEqual(weather.humidity, 65)
        self.assertEqual(weather.condition, WeatherCondition.CLOUDS)

    def test_weather_timestamp_auto_set(self):
        """Test that timestamp is automatically set."""
        weather = CurrentWeather(**self.valid_weather_data)

        self.assertIsNotNone(weather.timestamp)
        self.assertIsInstance(weather.timestamp, datetime)

    def test_severe_weather_detection(self):
        """Test severe weather condition detection."""
        # Test thunderstorm (severe)
        severe_data = self.valid_weather_data.copy()
        severe_data["condition"] = WeatherCondition.THUNDERSTORM
        severe_weather = CurrentWeather(**severe_data)

        self.assertTrue(severe_weather.is_severe_weather)

        # Test normal conditions (not severe)
        normal_weather = CurrentWeather(**self.valid_weather_data)
        self.assertFalse(normal_weather.is_severe_weather)


class TestWeatherForecastModel(unittest.TestCase):
    """Test cases for the WeatherForecast model."""

    def setUp(self):
        """Set up test data."""
        self.location = Location(
            name="Paris", country="FR", latitude=48.8566, longitude=2.3522
        )

        # Create sample forecast days
        self.forecast_days = []
        for i in range(5):
            temp_high = Temperature(value=20.0 + i, unit=TemperatureUnit.CELSIUS)
            temp_low = Temperature(value=10.0 + i, unit=TemperatureUnit.CELSIUS)
            wind = Wind(speed=5.0 + i, direction=180)

            day = WeatherForecastDay(
                date=datetime.now() + timedelta(days=i),
                temperature_high=temp_high,
                temperature_low=temp_low,
                condition=WeatherCondition.CLEAR,
                description=f"Clear sky day {i+1}",
                humidity=60 + i,
                wind=wind,
                precipitation_chance=10 + i,
            )
            self.forecast_days.append(day)

        self.valid_forecast_data = {
            "location": self.location,
            "forecast_days": self.forecast_days,
        }

    def test_valid_forecast_creation(self):
        """Test creating valid weather forecast."""
        forecast = WeatherForecast(**self.valid_forecast_data)

        self.assertEqual(forecast.location, self.location)
        self.assertEqual(len(forecast.forecast_days), 5)
        self.assertIsInstance(forecast.timestamp, datetime)

    def test_forecast_days_count(self):
        """Test forecast days count property."""
        forecast = WeatherForecast(**self.valid_forecast_data)

        self.assertEqual(forecast.days_count, 5)

    def test_get_forecast_day(self):
        """Test getting forecast for specific day index."""
        forecast = WeatherForecast(**self.valid_forecast_data)

        day_2 = forecast.get_day(2)
        self.assertIsNotNone(day_2)
        if day_2:  # Check if not None before accessing attributes
            self.assertEqual(day_2.temperature_high.value, 22.0)

        # Test invalid index
        invalid_day = forecast.get_day(10)
        self.assertIsNone(invalid_day)


class TestPrecipitationModel(unittest.TestCase):
    """Test cases for the Precipitation model."""

    def test_total_precipitation_calculation(self):
        """Test total precipitation calculation."""
        precip = Precipitation(rain_1h=5.0, snow_1h=2.0)

        self.assertEqual(precip.total_precipitation, 7.0)

    def test_precipitation_with_none_values(self):
        """Test precipitation with None values."""
        precip = Precipitation(rain_1h=3.0)

        self.assertEqual(precip.total_precipitation, 3.0)


class TestWeatherEnums(unittest.TestCase):
    """Test cases for weather-related enums."""

    def test_weather_condition_enum_values(self):
        """Test WeatherCondition enum values."""
        self.assertEqual(WeatherCondition.CLEAR.value, "clear")
        self.assertEqual(WeatherCondition.RAIN.value, "rain")
        self.assertEqual(WeatherCondition.SNOW.value, "snow")

    def test_temperature_unit_enum_values(self):
        """Test TemperatureUnit enum values."""
        self.assertEqual(TemperatureUnit.CELSIUS.value, "metric")
        self.assertEqual(TemperatureUnit.FAHRENHEIT.value, "imperial")
        self.assertEqual(TemperatureUnit.KELVIN.value, "standard")

    def test_weather_condition_from_string(self):
        """Test creating WeatherCondition from string."""
        condition = WeatherCondition("rain")
        self.assertEqual(condition, WeatherCondition.RAIN)

    def test_invalid_weather_condition_raises_error(self):
        """Test that invalid weather condition raises ValueError."""
        with self.assertRaises(ValueError):
            WeatherCondition("invalid_condition")


if __name__ == "__main__":
    # Configure logging for tests
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # Create test loader
    loader = unittest.TestLoader()

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(loader.loadTestsFromTestCase(TestLocationModel))
    test_suite.addTest(loader.loadTestsFromTestCase(TestTemperatureModel))
    test_suite.addTest(loader.loadTestsFromTestCase(TestWindModel))
    test_suite.addTest(loader.loadTestsFromTestCase(TestCurrentWeatherModel))
    test_suite.addTest(loader.loadTestsFromTestCase(TestWeatherForecastModel))
    test_suite.addTest(loader.loadTestsFromTestCase(TestPrecipitationModel))
    test_suite.addTest(loader.loadTestsFromTestCase(TestWeatherEnums))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\nTest Results: ")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
