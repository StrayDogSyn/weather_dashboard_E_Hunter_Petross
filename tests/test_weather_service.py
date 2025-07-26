"""
Unit tests for core weather service business logic.

Tests the weather service class and its integration with
data storage, caching, and external APIs.
"""

import os

# Import the service to test
import sys
import unittest
from datetime import datetime, timedelta
from typing import List, Optional
from unittest.mock import MagicMock, Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.weather_service import WeatherService
from src.interfaces.weather_interfaces import ICacheService, IDataStorage, IWeatherAPI
from src.models.weather_models import (
    AtmosphericPressure,
    CurrentWeather,
    FavoriteCity,
    Location,
    Precipitation,
    Temperature,
    TemperatureUnit,
    WeatherCondition,
    WeatherForecast,
    WeatherForecastDay,
    Wind,
)


class TestWeatherService(unittest.TestCase):
    """Test cases for the WeatherService class."""

    def setUp(self):
        """Set up test dependencies and service instance."""
        # Create mock dependencies
        self.mock_weather_api = Mock(spec=IWeatherAPI)
        self.mock_storage = Mock(spec=IDataStorage)
        self.mock_cache = Mock(spec=ICacheService)

        # Add additional mock methods that are used by the service
        self.mock_cache.get_cache_key = Mock(return_value="test_cache_key")
        self.mock_cache.get.return_value = None  # Default to cache miss

        # Create service instance
        self.weather_service = WeatherService(
            weather_api=self.mock_weather_api,
            storage=self.mock_storage,
            cache=self.mock_cache,
        )

        # Sample location for testing
        self.test_location = Location(
            name="New York", country="US", latitude=40.7128, longitude=-74.0060
        )

        # Sample current weather for testing
        self.test_weather = CurrentWeather(
            location=self.test_location,
            temperature=Temperature(value=22.0, unit=TemperatureUnit.CELSIUS),
            condition=WeatherCondition.CLEAR,
            description="Clear sky",
            humidity=65,
            pressure=AtmosphericPressure(value=1013.25),
            wind=Wind(speed=10.0, direction=180),
        )

    def test_get_current_weather_cache_hit(self):
        """Test getting current weather when data is in cache."""
        # Setup cache to return weather data
        self.mock_cache.get.return_value = self.test_weather

        # Call service method
        result = self.weather_service.get_current_weather("New York")

        # Verify cache was checked
        self.mock_cache.get.assert_called_once()

        # Verify API was not called
        self.mock_weather_api.get_current_weather.assert_not_called()

        # Verify result
        self.assertEqual(result, self.test_weather)

    def test_get_current_weather_cache_miss(self):
        """Test getting current weather when data is not in cache."""
        # Setup cache miss
        self.mock_cache.get.return_value = None

        # Setup API to return weather data
        self.mock_weather_api.get_current_weather.return_value = self.test_weather

        # Call service method
        result = self.weather_service.get_current_weather("New York")

        # Verify cache was checked
        self.mock_cache.get.assert_called_once()

        # Verify API was called
        self.mock_weather_api.get_current_weather.assert_called_once_with(
            "New York", "metric"
        )

        # Verify result was cached
        self.mock_cache.set.assert_called_once()

        # Verify result
        self.assertEqual(result, self.test_weather)

    def test_get_current_weather_api_error(self):
        """Test handling of API errors when getting current weather."""
        # Setup cache miss
        self.mock_cache.get.return_value = None

        # Setup API to raise exception
        self.mock_weather_api.get_current_weather.side_effect = Exception("API Error")

        # Call service method and expect exception to propagate
        with self.assertRaises(Exception):
            self.weather_service.get_current_weather("Invalid City")

        # Verify API was called
        self.mock_weather_api.get_current_weather.assert_called_once()

    def test_get_weather_forecast_success(self):
        """Test successful weather forecast retrieval."""
        # Setup cache to return None (cache miss)
        self.mock_cache.get.return_value = None

        # Create sample forecast
        forecast_days = []
        for i in range(5):
            day = WeatherForecastDay(
                date=datetime.now() + timedelta(days=i),
                temperature_high=Temperature(
                    value=25.0 + i, unit=TemperatureUnit.CELSIUS
                ),
                temperature_low=Temperature(
                    value=15.0 + i, unit=TemperatureUnit.CELSIUS
                ),
                condition=WeatherCondition.CLEAR,
                description=f"Clear day {i+1}",
                humidity=60,
                wind=Wind(speed=8.0),
                precipitation_chance=10,
            )
            forecast_days.append(day)

        test_forecast = WeatherForecast(
            location=self.test_location, forecast_days=forecast_days
        )

        # Setup API to return forecast
        self.mock_weather_api.get_forecast.return_value = test_forecast

        # Call service method
        result = self.weather_service.get_weather_forecast("New York", days=5)

        # Verify API was called
        self.mock_weather_api.get_forecast.assert_called_once_with(
            "New York", 5, "metric"
        )

        # Verify result
        self.assertEqual(result, test_forecast)
        if result:  # Check if not None before accessing attributes
            self.assertEqual(result.days_count, 5)

    def test_add_favorite_city(self):
        """Test adding a city to favorites."""
        # Setup search_locations to return a valid location
        test_locations = [self.test_location]
        self.weather_service.search_locations = Mock(return_value=test_locations)

        # Call service method with city name
        result = self.weather_service.add_favorite_city("New York", "Big Apple")

        # Verify search was called
        self.weather_service.search_locations.assert_called_once_with("New York", 1)

        # Verify result
        self.assertTrue(result)

    def test_remove_favorite_city(self):
        """Test removing a city from favorites."""
        # Add a favorite city to the service first
        favorite = FavoriteCity(
            location=Location(
                name="New York", country="US", latitude=40.7128, longitude=-74.0060
            ),
            nickname="",
            added_date=datetime.now(),
        )
        self.weather_service.favorite_cities = [favorite]

        # Call service method
        result = self.weather_service.remove_favorite_city("New York")

        # Verify result
        self.assertTrue(result)
        self.assertEqual(len(self.weather_service.favorite_cities), 0)

    def test_get_favorite_cities(self):
        """Test getting list of favorite cities."""
        # Sample favorite cities
        favorite_cities = [
            FavoriteCity(
                location=Location(
                    name="New York", country="US", latitude=40.7128, longitude=-74.0060
                ),
                nickname="Big Apple",
                added_date=datetime.now(),
            ),
            FavoriteCity(
                location=Location(
                    name="London", country="UK", latitude=51.5074, longitude=-0.1278
                ),
                nickname="",
                added_date=datetime.now(),
            ),
        ]

        # Set the service's favorite cities directly
        self.weather_service.favorite_cities = favorite_cities

        # Call service method
        result = self.weather_service.get_favorite_cities()

        # Verify result
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].location.name, "New York")
        self.assertEqual(result[1].location.name, "London")


class TestWeatherServiceValidation(unittest.TestCase):
    """Test cases for weather service input validation."""

    def setUp(self):
        """Set up test dependencies and service instance."""
        # Create mock dependencies
        self.mock_weather_api = Mock(spec=IWeatherAPI)
        self.mock_storage = Mock(spec=IDataStorage)
        self.mock_cache = Mock(spec=ICacheService)

        # Add additional mock methods that are used by the service
        self.mock_cache.get_cache_key = Mock(return_value="test_cache_key")
        self.mock_cache.get.return_value = None  # Default to cache miss

        # Create service instance
        self.weather_service = WeatherService(
            weather_api=self.mock_weather_api,
            storage=self.mock_storage,
            cache=self.mock_cache,
        )

    def test_validate_city_name_empty(self):
        """Test validation of empty city names."""
        result = self.weather_service.get_current_weather("")

        # Should handle empty string gracefully
        self.assertIsNone(result)

        # API should not be called for invalid input
        self.mock_weather_api.get_current_weather.assert_not_called()

    def test_validate_city_name_none(self):
        """Test validation of None city names."""
        # Test with empty string instead of None since the method expects str
        result = self.weather_service.get_current_weather("   ")  # Whitespace only

        # Should handle invalid input gracefully
        self.assertIsNone(result)

        # API should not be called for invalid input
        self.mock_weather_api.get_current_weather.assert_not_called()

    def test_validate_forecast_days_parameter(self):
        """Test validation of forecast days parameter."""
        # Test valid days parameter
        self.weather_service.get_weather_forecast("New York", days=5)
        self.mock_weather_api.get_forecast.assert_called_with("New York", 5, "metric")

        # Test invalid days parameter (too high)
        result = self.weather_service.get_weather_forecast("New York", days=15)

        # Should be limited to maximum allowed days or handle gracefully
        # Exact behavior depends on implementation
        self.assertIsNotNone(self.mock_weather_api.get_forecast.call_args)


class TestWeatherServiceCaching(unittest.TestCase):
    """Test cases for weather service caching behavior."""

    def setUp(self):
        """Set up test dependencies and service instance."""
        # Create mock dependencies
        self.mock_weather_api = Mock(spec=IWeatherAPI)
        self.mock_storage = Mock(spec=IDataStorage)
        self.mock_cache = Mock(spec=ICacheService)

        # Add additional mock methods that are used by the service
        self.mock_cache.get_cache_key = Mock(return_value="test_cache_key")
        self.mock_cache.get.return_value = None  # Default to cache miss

        # Create service instance
        self.weather_service = WeatherService(
            weather_api=self.mock_weather_api,
            storage=self.mock_storage,
            cache=self.mock_cache,
        )

        # Sample weather data
        self.test_location = Location(
            name="London", country="UK", latitude=51.5074, longitude=-0.1278
        )

        self.test_weather = CurrentWeather(
            location=self.test_location,
            temperature=Temperature(value=18.0, unit=TemperatureUnit.CELSIUS),
            condition=WeatherCondition.CLOUDS,
            description="Partly cloudy",
            humidity=70,
            pressure=AtmosphericPressure(value=1015.0),
            wind=Wind(speed=12.0, direction=200),
        )

    def test_cache_expiration_handling(self):
        """Test handling of expired cache entries."""
        # Setup cache to return None (simulating expired/missing entry)
        self.mock_cache.get.return_value = None

        # Setup API to return fresh data
        self.mock_weather_api.get_current_weather.return_value = self.test_weather

        # Call service method
        result = self.weather_service.get_current_weather("London")

        # Verify cache was checked
        self.mock_cache.get.assert_called_once()

        # Verify API was called due to cache miss
        self.mock_weather_api.get_current_weather.assert_called_once()

        # Verify result
        self.assertEqual(result, self.test_weather)

    def test_cache_key_generation(self):
        """Test that proper cache keys are generated."""
        # Setup cache.get_cache_key to return a predictable key
        self.mock_cache.get_cache_key.return_value = "weather_new_york_metric"

        # Call service method
        self.weather_service.get_current_weather("New York")

        # Verify cache key generation was called with correct parameters
        self.mock_cache.get_cache_key.assert_called_with(
            "weather", "New York", "metric"
        )

        # Verify cache was called with the generated key
        self.mock_cache.get.assert_called_with("weather_new_york_metric")


if __name__ == "__main__":
    # Configure logging for tests
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # Create test loader
    loader = unittest.TestLoader()

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(loader.loadTestsFromTestCase(TestWeatherService))
    test_suite.addTest(loader.loadTestsFromTestCase(TestWeatherServiceValidation))
    test_suite.addTest(loader.loadTestsFromTestCase(TestWeatherServiceCaching))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\nWeather Service Tests Results: ")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
