#!/usr/bin/env python3
"""
Setup verification script for Weather Dashboard
Verifies all dependencies and imports are working correctly.
"""

import sys
from pathlib import Path

def test_imports():
    """Test all critical imports"""
    print("🔍 Testing core imports...")
    
    try:
        # Test Python standard library
        import json
        import os
        import datetime
        print("✅ Standard library imports: OK")
        
        # Test third-party dependencies
        import requests
        import pandas as pd
        from dotenv import load_dotenv
        from loguru import logger
        import pydantic
        import ttkbootstrap
        print("✅ Third-party dependencies: OK")
        
        # Test our application imports
        from src.config.config import WeatherDashboardConfig
        from src.models.weather_models import CurrentWeather, Location
        from src.services.weather_api import OpenWeatherMapAPI
        from src.core.weather_service import WeatherService
        from src.ui.cli_interface import CLIInterface
        print("✅ Application imports: OK")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("\n🔍 Testing configuration...")
    
    try:
        from src.config.config import load_config
        config = load_config()
        print(f"✅ Configuration loaded: {type(config).__name__}")
        print(f"   - API Key: {'✅ Present' if config.api_key else '❌ Missing'}")
        print(f"   - Default City: {config.default_city}")
        print(f"   - Theme: {config.theme}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_models():
    """Test domain models"""
    print("\n🔍 Testing domain models...")
    
    try:
        from src.models.weather_models import Location, Temperature, CurrentWeather
        from datetime import datetime
        
        # Test Location
        location = Location(name="Test City", country="TC", lat=0.0, lon=0.0)
        print(f"✅ Location model: {location.name}")
        
        # Test Temperature
        temp = Temperature(celsius=20.0)
        print(f"✅ Temperature model: {temp.celsius}°C = {temp.fahrenheit}°F")
        
        # Test CurrentWeather
        weather = CurrentWeather(
            location=location,
            temperature=temp,
            description="Clear sky",
            humidity=60,
            pressure=1013.25,
            visibility=10.0,
            timestamp=datetime.now()
        )
        print(f"✅ Weather model: {weather.description}")
        
        return True
    except Exception as e:
        print(f"❌ Model error: {e}")
        return False

def main():
    """Main verification function"""
    print("🌤️ Weather Dashboard Setup Verification")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_imports()
    all_tests_passed &= test_configuration()
    all_tests_passed &= test_models()
    
    # Summary
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("🎉 All verification tests passed!")
        print("✅ Your Weather Dashboard setup is ready to use.")
        print("\nTo run the application:")
        print("   python main.py")
        print("\nTo run tests:")
        print("   python -m pytest tests/ -v")
    else:
        print("❌ Some verification tests failed.")
        print("Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
