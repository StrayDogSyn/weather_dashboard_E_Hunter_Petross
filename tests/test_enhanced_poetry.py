#!/usr/bin/env python3
"""
Test script to verify the enhanced poetry service functionality.
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_poetry_service():
    """Test the enhanced poetry service with template-based generation."""

    try:
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
        from src.services.poetry_service import WeatherPoetryService

        # Create a mock weather object
        location = Location(
            name="Test City", country="US", latitude=40.7128, longitude=-74.0060
        )
        temperature = Temperature(value=22.0, unit=TemperatureUnit.CELSIUS)
        pressure = AtmosphericPressure(value=1013.25)
        wind = Wind(speed=5.0)

        weather = CurrentWeather(
            location=location,
            temperature=temperature,
            condition=WeatherCondition.CLEAR,
            description="clear sky",
            humidity=50,
            timestamp=datetime.now(),
            pressure=pressure,
            wind=wind,
            precipitation=None,
            visibility=10.0,
        )

        # Initialize the poetry service
        poetry_service = WeatherPoetryService()

        print("🌟 Testing Enhanced Weather Poetry Service")
        print("=" * 50)
        print(
            f"AI Enhancement: {'Enabled' if poetry_service.ai_enabled else 'Disabled (template-based)'}"
        )
        print()

        # Test different poetry types
        print("📝 Testing Haiku Generation:")
        haiku = poetry_service.generate_haiku(weather)
        print(f"Type: {haiku.poem_type}")
        print(f"Text: {haiku.text}")
        print()

        print("💭 Testing Fun Phrase Generation:")
        phrase = poetry_service.generate_fun_phrase(weather)
        print(f"Type: {phrase.poem_type}")
        print(f"Text: {phrase.text}")
        print()

        print("🎵 Testing Limerick Generation:")
        limerick = poetry_service.generate_limerick(weather)
        print(f"Type: {limerick.poem_type}")
        print(f"Text: {limerick.text}")
        print()

        print("🎲 Testing Random Poetry:")
        random_poem = poetry_service.generate_weather_poetry(weather, "random")
        print(f"Type: {random_poem.poem_type}")
        print(f"Text: {random_poem.text}")
        print()

        print("📚 Testing Poetry Collection:")
        collection = poetry_service.create_poetry_collection(weather, count=3)
        for i, poem in enumerate(collection, 1):
            print(f"{i}. {poem.poem_type.title()}: {poem.text}")

        print("\n✅ Poetry service test completed successfully!")

    except Exception as e:
        print(f"❌ Error testing poetry service: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_poetry_service()
