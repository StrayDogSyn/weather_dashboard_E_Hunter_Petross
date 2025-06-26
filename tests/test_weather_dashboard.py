"""Tests for the Weather Dashboard application."""

import unittest
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.models import Location, Temperature, TemperatureUnit, CurrentWeather
from src.utils import validate_city_name, clean_city_name, format_temperature
from src.services import MemoryCacheService, FileDataStorage


class TestModels(unittest.TestCase):
    """Test domain models."""
    
    def test_location_creation(self):
        """Test location creation and validation."""
        location = Location(
            name="London",
            country="GB",
            latitude=51.5074,
            longitude=-0.1278
        )
        
        self.assertEqual(location.display_name, "London, GB")
        self.assertEqual(location.latitude, 51.5074)
        self.assertEqual(location.longitude, -0.1278)
    
    def test_location_invalid_coordinates(self):
        """Test location with invalid coordinates."""
        with self.assertRaises(ValueError):
            Location(
                name="Invalid",
                country="XX",
                latitude=91.0,  # Invalid latitude
                longitude=0.0
            )
    
    def test_temperature_conversion(self):
        """Test temperature conversions."""
        temp = Temperature(20.0, TemperatureUnit.CELSIUS)
        
        self.assertEqual(temp.to_celsius(), 20.0)
        self.assertAlmostEqual(temp.to_fahrenheit(), 68.0, places=1)
        
        # Test Fahrenheit to Celsius
        temp_f = Temperature(68.0, TemperatureUnit.FAHRENHEIT)
        self.assertAlmostEqual(temp_f.to_celsius(), 20.0, places=1)


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_validate_city_name(self):
        """Test city name validation."""
        # Valid names
        self.assertTrue(validate_city_name("London"))
        self.assertTrue(validate_city_name("New York"))
        self.assertTrue(validate_city_name("Saint-Denis"))
        self.assertTrue(validate_city_name("O'Brien"))
        
        # Invalid names
        self.assertFalse(validate_city_name(""))
        self.assertFalse(validate_city_name("X"))  # Too short
        self.assertFalse(validate_city_name("City123"))  # Numbers
        self.assertFalse(validate_city_name("City@#$"))  # Special chars
    
    def test_clean_city_name(self):
        """Test city name cleaning."""
        self.assertEqual(clean_city_name("  london  "), "London")
        self.assertEqual(clean_city_name("new york"), "New York")
        self.assertEqual(clean_city_name("PARIS"), "Paris")
    
    def test_format_temperature(self):
        """Test temperature formatting."""
        self.assertEqual(format_temperature(20.5, "C"), "20.5°C")
        self.assertEqual(format_temperature(68.0, "F"), "68.0°F")
        self.assertEqual(format_temperature(293.15, "K"), "293.1K")


class TestServices(unittest.TestCase):
    """Test service implementations."""
    
    def test_memory_cache_service(self):
        """Test memory cache service."""
        cache = MemoryCacheService()
        
        # Test set and get
        self.assertTrue(cache.set("test_key", "test_value", 10))
        self.assertEqual(cache.get("test_key"), "test_value")
        
        # Test non-existent key
        self.assertIsNone(cache.get("non_existent"))
        
        # Test delete
        self.assertTrue(cache.delete("test_key"))
        self.assertIsNone(cache.get("test_key"))
        
        # Test clear
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        self.assertTrue(cache.clear())
        self.assertIsNone(cache.get("key1"))
        self.assertIsNone(cache.get("key2"))
    
    def test_cache_key_generation(self):
        """Test cache key generation."""
        cache = MemoryCacheService()
        
        key = cache.get_cache_key("weather", "London", "metric")
        self.assertEqual(key, "weather:London:metric")
        
        key = cache.get_cache_key("forecast", "Paris", 5, "imperial")
        self.assertEqual(key, "forecast:Paris:5:imperial")
    
    def test_file_data_storage(self):
        """Test file data storage."""
        import tempfile
        import shutil
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            storage = FileDataStorage(temp_dir)
            
            test_data = {"test": "data", "number": 42}
            
            # Test save
            self.assertTrue(storage.save_data(test_data, "test_file"))
            
            # Test load
            loaded_data = storage.load_data("test_file")
            self.assertEqual(loaded_data, test_data)
            
            # Test file exists
            self.assertTrue(storage.file_exists("test_file"))
            self.assertFalse(storage.file_exists("non_existent"))
            
            # Test delete
            self.assertTrue(storage.delete_data("test_file"))
            self.assertFalse(storage.file_exists("test_file"))
            
        finally:
            # Clean up
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestConfiguration(unittest.TestCase):
    """Test configuration management."""
    
    def test_config_import(self):
        """Test that configuration can be imported."""
        try:
            from src.config import config_manager
            self.assertIsNotNone(config_manager)
        except ImportError as e:
            self.fail(f"Failed to import configuration: {e}")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
