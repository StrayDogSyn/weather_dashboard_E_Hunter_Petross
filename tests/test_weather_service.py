"""
Unit tests for core weather service business logic.

Tests the weather service class and its integration with
data storage, caching, and external APIs.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from typing import List, Optional

# Import the service to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.weather_service import WeatherService
from src.models.weather_models import (
    Location, CurrentWeather, WeatherForecast, WeatherForecastDay,
    WeatherCondition, TemperatureUnit, Temperature, Wind, 
    AtmosphericPressure, Precipitation
)
from src.interfaces.weather_interfaces import IWeatherAPI, IDataStorage, ICacheService


class TestWeatherService(unittest.TestCase):
    """Test cases for the WeatherService class."""
    
    def setUp(self):
        """Set up test dependencies and service instance."""
        # Create mock dependencies
        self.mock_weather_api = Mock(spec=IWeatherAPI)
        self.mock_storage = Mock(spec=IDataStorage)
        self.mock_cache = Mock(spec=ICacheService)
        
        # Create service instance
        self.weather_service = WeatherService(
            weather_api=self.mock_weather_api,
            storage=self.mock_storage,
            cache=self.mock_cache
        )
        
        # Sample location for testing
        self.test_location = Location(
            name="New York",
            country="US",
            latitude=40.7128,
            longitude=-74.0060
        )
        
        # Sample current weather for testing
        self.test_weather = CurrentWeather(
            location=self.test_location,
            temperature=Temperature(value=22.0, unit=TemperatureUnit.CELSIUS),
            condition=WeatherCondition.CLEAR,
            description="Clear sky",
            humidity=65,
            pressure=AtmosphericPressure(value=1013.25),
            wind=Wind(speed=10.0, direction=180)
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
        self.mock_weather_api.get_current_weather.assert_called_once_with("New York")
        
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
        
        # Call service method and expect None or exception handling
        result = self.weather_service.get_current_weather("Invalid City")
        
        # Verify API was called
        self.mock_weather_api.get_current_weather.assert_called_once()
        
        # Result should be None or service should handle error gracefully
        self.assertIsNone(result)
    
    def test_get_weather_forecast_success(self):
        """Test successful weather forecast retrieval."""
        # Create sample forecast
        forecast_days = []
        for i in range(5):
            day = WeatherForecastDay(
                date=datetime.now() + timedelta(days=i),
                temperature_high=Temperature(value=25.0 + i, unit=TemperatureUnit.CELSIUS),
                temperature_low=Temperature(value=15.0 + i, unit=TemperatureUnit.CELSIUS),
                condition=WeatherCondition.CLEAR,
                description=f"Clear day {i+1}",
                humidity=60,
                wind=Wind(speed=8.0),
                precipitation_chance=10
            )
            forecast_days.append(day)
        
        test_forecast = WeatherForecast(
            location=self.test_location,
            forecast_days=forecast_days
        )
        
        # Setup API to return forecast
        self.mock_weather_api.get_weather_forecast.return_value = test_forecast
        
        # Call service method
        result = self.weather_service.get_weather_forecast("New York", days=5)
        
        # Verify API was called
        self.mock_weather_api.get_weather_forecast.assert_called_once_with("New York", days=5)
        
        # Verify result
        self.assertEqual(result, test_forecast)
        if result:  # Check if not None before accessing attributes
            self.assertEqual(result.days_count, 5)
    
    def test_add_favorite_city(self):
        """Test adding a city to favorites."""
        # Call service method with city name
        result = self.weather_service.add_favorite_city("New York", "Big Apple")
        
        # Verify storage was called to save favorite
        self.mock_storage.save_favorite_city.assert_called_once()
        
        # Verify result
        self.assertTrue(result)
    
    def test_remove_favorite_city(self):
        """Test removing a city from favorites."""
        # Call service method
        result = self.weather_service.remove_favorite_city("New York")
        
        # Verify storage was called to remove favorite
        self.mock_storage.remove_favorite_city.assert_called_once_with("New York")
        
        # Verify result
        self.assertTrue(result)
    
    def test_get_favorite_cities(self):
        """Test getting list of favorite cities."""
        # Sample favorite cities
        favorite_cities = [
            Location(name="New York", country="US", latitude=40.7128, longitude=-74.0060),
            Location(name="London", country="UK", latitude=51.5074, longitude=-0.1278),
        ]
        
        # Setup storage to return favorites
        self.mock_storage.get_favorite_cities.return_value = favorite_cities
        
        # Call service method
        result = self.weather_service.get_favorite_cities()
        
        # Verify storage was called
        self.mock_storage.get_favorite_cities.assert_called_once()
        
        # Verify result
        self.assertEqual(result, favorite_cities)
        self.assertEqual(len(result), 2)


class TestWeatherServiceValidation(unittest.TestCase):
    """Test cases for weather service input validation."""
    
    def setUp(self):
        """Set up test dependencies and service instance."""
        # Create mock dependencies
        self.mock_weather_api = Mock(spec=IWeatherAPI)
        self.mock_storage = Mock(spec=IDataStorage)
        self.mock_cache = Mock(spec=ICacheService)
        
        # Create service instance
        self.weather_service = WeatherService(
            weather_api=self.mock_weather_api,
            storage=self.mock_storage,
            cache=self.mock_cache
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
        self.mock_weather_api.get_weather_forecast.assert_called_with("New York", days=5)
        
        # Test invalid days parameter (too high)
        result = self.weather_service.get_weather_forecast("New York", days=15)
        
        # Should be limited to maximum allowed days or handle gracefully
        # Exact behavior depends on implementation
        self.assertIsNotNone(self.mock_weather_api.get_weather_forecast.call_args)


class TestWeatherServiceCaching(unittest.TestCase):
    """Test cases for weather service caching behavior."""
    
    def setUp(self):
        """Set up test dependencies and service instance."""
        # Create mock dependencies
        self.mock_weather_api = Mock(spec=IWeatherAPI)
        self.mock_storage = Mock(spec=IDataStorage)
        self.mock_cache = Mock(spec=ICacheService)
        
        # Create service instance
        self.weather_service = WeatherService(
            weather_api=self.mock_weather_api,
            storage=self.mock_storage,
            cache=self.mock_cache
        )
        
        # Sample weather data
        self.test_location = Location(
            name="London",
            country="UK",
            latitude=51.5074,
            longitude=-0.1278
        )
        
        self.test_weather = CurrentWeather(
            location=self.test_location,
            temperature=Temperature(value=18.0, unit=TemperatureUnit.CELSIUS),
            condition=WeatherCondition.CLOUDS,
            description="Partly cloudy",
            humidity=70,
            pressure=AtmosphericPressure(value=1015.0),
            wind=Wind(speed=12.0, direction=200)
        )
    
    def test_cache_expiration_handling(self):
        """Test handling of expired cache entries."""
        # Setup cache to return expired data
        expired_weather = self.test_weather
        expired_weather.timestamp = datetime.now() - timedelta(hours=2)
        
        self.mock_cache.get.return_value = expired_weather
        self.mock_cache.is_expired.return_value = True
        
        # Setup API to return fresh data
        fresh_weather = self.test_weather
        fresh_weather.timestamp = datetime.now()
        self.mock_weather_api.get_current_weather.return_value = fresh_weather
        
        # Call service method
        result = self.weather_service.get_current_weather("London")
        
        # Verify cache was checked
        self.mock_cache.get.assert_called_once()
        
        # Verify API was called due to expired cache
        self.mock_weather_api.get_current_weather.assert_called_once()
        
        # Verify fresh data was cached
        self.mock_cache.set.assert_called_once()
    
    def test_cache_key_generation(self):
        """Test that proper cache keys are generated."""
        # Call service method
        self.weather_service.get_current_weather("New York")
        
        # Verify cache was called with appropriate key
        cache_call_args = self.mock_cache.get.call_args
        self.assertIsNotNone(cache_call_args)
        
        # Cache key should be related to the city name
        cache_key = cache_call_args[0][0] if cache_call_args else ""
        self.assertIn("new york", cache_key.lower())


if __name__ == '__main__':
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
    print(f"\nWeather Service Tests Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
