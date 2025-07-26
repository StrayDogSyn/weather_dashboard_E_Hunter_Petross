"""
Unit tests for validation utilities and data formatters.

Tests basic validation functions and data formatting utilities
that are actually available in the Weather Dashboard application.
"""

import os

# Import the validators and formatters to test
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.utils.formatters import (
    clean_city_name,
    format_pressure,
    format_temperature,
    format_wind_speed,
    validate_city_name,
    validate_coordinates,
)
from src.utils.validators import (
    ValidationError,
    validate_api_key,
    validate_temperature_range,
)


class TestAPIKeyValidation(unittest.TestCase):
    """Test cases for API key validation."""

    def test_valid_api_key(self):
        """Test validation of valid API keys."""
        valid_keys = [
            "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",  # 32 chars
            "abc123def456ghi789jkl012mno345pqr",  # 32 chars alphanumeric
            "1234567890abcdef",  # 16 chars (minimum)
        ]

        for key in valid_keys:
            with self.subTest(key=key):
                self.assertTrue(validate_api_key(key))

    def test_invalid_api_key(self):
        """Test validation of invalid API keys."""
        invalid_keys = [
            "",  # Empty string
            "short",  # Too short
            "a" * 65,  # Too long
            "abc123-def456",  # Contains dash
            "abc123 def456",  # Contains space
            "abc123def456!@#",  # Contains special characters
        ]

        for key in invalid_keys:
            with self.subTest(key=key):
                self.assertFalse(validate_api_key(key))

    def test_api_key_whitespace_handling(self):
        """Test API key validation handles whitespace."""
        key_with_spaces = "  a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6  "
        self.assertTrue(validate_api_key(key_with_spaces))


class TestTemperatureValidation(unittest.TestCase):
    """Test cases for temperature validation."""

    def test_valid_temperatures_celsius(self):
        """Test validation of valid Celsius temperatures."""
        valid_temps = [-50.0, -10.5, 0.0, 25.5, 45.0]

        for temp in valid_temps:
            with self.subTest(temp=temp):
                self.assertTrue(validate_temperature_range(temp, "C"))

    def test_valid_temperatures_fahrenheit(self):
        """Test validation of valid Fahrenheit temperatures."""
        valid_temps = [-58.0, 32.0, 75.5, 100.0, 113.0]

        for temp in valid_temps:
            with self.subTest(temp=temp):
                self.assertTrue(validate_temperature_range(temp, "F"))

    def test_invalid_extreme_temperatures(self):
        """Test validation of extremely unrealistic temperatures."""
        extreme_temps = [-100.0, 70.0, 150.0]  # Unrealistic for earth

        for temp in extreme_temps:
            with self.subTest(temp=temp):
                self.assertFalse(validate_temperature_range(temp, "C"))


class TestCityNameValidation(unittest.TestCase):
    """Test cases for city name validation."""

    def test_valid_city_names(self):
        """Test validation of valid city names."""
        valid_names = [
            "New York",
            "Los Angeles",
            "San Francisco",
            "St. Louis",
            "Washington D.C.",
            "São Paulo",
            "Zürich",
            "München",
        ]

        for name in valid_names:
            with self.subTest(name=name):
                self.assertTrue(validate_city_name(name))

    def test_invalid_city_names(self):
        """Test validation of invalid city names."""
        invalid_names = [
            "",  # Empty string
            "A",  # Too short
            "X" * 101,  # Too long
            "123",  # Only numbers
            "!@#$%",  # Only special characters
            "   ",  # Only whitespace
        ]

        for name in invalid_names:
            with self.subTest(name=name):
                self.assertFalse(validate_city_name(name))

    def test_city_name_edge_cases(self):
        """Test city name validation edge cases."""
        # Names with valid special characters
        self.assertTrue(validate_city_name("St. John's"))
        self.assertTrue(validate_city_name("Coeur d'Alene"))

    def test_clean_city_name(self):
        """Test city name cleaning functionality."""
        # Test title case formatting
        self.assertEqual(clean_city_name("new york"), "New York")
        self.assertEqual(clean_city_name("LOS ANGELES"), "Los Angeles")
        self.assertEqual(clean_city_name("saN frAnCiScO"), "San Francisco")

        # Test whitespace handling
        self.assertEqual(clean_city_name("  new   york  "), "New York")
        self.assertEqual(clean_city_name(""), "")


class TestCoordinatesValidation(unittest.TestCase):
    """Test cases for coordinate validation."""

    def test_valid_coordinates(self):
        """Test validation of valid latitude/longitude pairs."""
        valid_coords = [
            (0.0, 0.0),  # Equator, Prime Meridian
            (40.7128, -74.0060),  # New York
            (-33.8688, 151.2093),  # Sydney
            (90.0, 180.0),  # North Pole, International Date Line
            (-90.0, -180.0),  # South Pole
        ]

        for lat, lon in valid_coords:
            with self.subTest(lat=lat, lon=lon):
                self.assertTrue(validate_coordinates(lat, lon))

    def test_invalid_coordinates(self):
        """Test validation of invalid latitude/longitude pairs."""
        invalid_coords = [
            (91.0, 0.0),  # Invalid latitude > 90
            (-91.0, 0.0),  # Invalid latitude < -90
            (0.0, 181.0),  # Invalid longitude > 180
            (0.0, -181.0),  # Invalid longitude < -180
            (95.5, 185.3),  # Both invalid
        ]

        for lat, lon in invalid_coords:
            with self.subTest(lat=lat, lon=lon):
                self.assertFalse(validate_coordinates(lat, lon))


class TestDataFormatters(unittest.TestCase):
    """Test cases for data formatting utilities."""

    def test_temperature_formatting(self):
        """Test temperature formatting."""
        # Celsius
        self.assertEqual(format_temperature(25.5, "C"), "25.5°C")
        self.assertEqual(format_temperature(0, "C"), "0.0°C")

        # Fahrenheit
        self.assertEqual(format_temperature(77.0, "F"), "77.0°F")

        # With decimal places
        self.assertEqual(format_temperature(25.567, "C", 1), "25.6°C")
        self.assertEqual(format_temperature(25.567, "C", 2), "25.57°C")

    def test_wind_speed_formatting(self):
        """Test wind speed formatting."""
        self.assertEqual(format_wind_speed(10.5), "10.5 km/h")
        self.assertEqual(format_wind_speed(0), "0.0 km/h")
        self.assertEqual(format_wind_speed(25.75), "25.8 km/h")

    def test_pressure_formatting(self):
        """Test pressure formatting."""
        self.assertEqual(format_pressure(1013.25), "1013.25 hPa")
        self.assertEqual(format_pressure(1000), "1000.0 hPa")


class TestValidationErrorHandling(unittest.TestCase):
    """Test cases for validation error handling."""

    def test_validation_error_creation(self):
        """Test ValidationError creation and messages."""
        error_message = "Invalid temperature value"
        error = ValidationError(error_message)

        self.assertEqual(str(error), error_message)
        self.assertIsInstance(error, Exception)


if __name__ == "__main__":
    # Configure logging for tests
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # Create test loader
    loader = unittest.TestLoader()

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test cases
    test_suite.addTest(loader.loadTestsFromTestCase(TestAPIKeyValidation))
    test_suite.addTest(loader.loadTestsFromTestCase(TestTemperatureValidation))
    test_suite.addTest(loader.loadTestsFromTestCase(TestCityNameValidation))
    test_suite.addTest(loader.loadTestsFromTestCase(TestCoordinatesValidation))
    test_suite.addTest(loader.loadTestsFromTestCase(TestDataFormatters))
    test_suite.addTest(loader.loadTestsFromTestCase(TestValidationErrorHandling))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\nValidation Tests Results: ")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
