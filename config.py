"""
Configuration settings for Weather Dashboard
Contains API keys, URLs, and application settings
"""

import os
from typing import Dict, Any

# API Configuration
class WeatherAPIConfig:
    """Configuration for weather API services"""
    
    # OpenWeatherMap API (free tier available)
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
    OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    # Alternative APIs (for future expansion)
    WEATHERAPI_KEY = os.getenv('WEATHERAPI_KEY', '')
    WEATHERAPI_BASE_URL = "https://api.weatherapi.com/v1"

# Application Configuration
class AppConfig:
    """Main application configuration"""
    
    # Default settings
    DEFAULT_CITY = "New York"
    DEFAULT_UNITS = "metric"  # metric, imperial, standard
    REFRESH_INTERVAL = 300  # seconds (5 minutes)
    
    # Data storage
    DATA_DIR = "data"
    CACHE_DURATION = 600  # seconds (10 minutes)
    
    # Display settings
    THEME = "light"  # light, dark
    LANGUAGE = "en"
    
    # Features to enable/disable
    FEATURES = {
        "current_weather": True,
        "forecast": True,
        "weather_map": True,
        "historical_data": False,  # Premium feature
        "alerts": True,
        "favorites": True
    }

# UI Configuration
class UIConfig:
    """User interface configuration"""
    
    WINDOW_TITLE = "Weather Dashboard"
    WINDOW_SIZE = (1200, 800)
    MIN_WINDOW_SIZE = (800, 600)
    
    # Colors (for custom theming)
    COLORS = {
        "primary": "#2196F3",
        "secondary": "#FF9800", 
        "success": "#4CAF50",
        "warning": "#FF5722",
        "background": "#FFFFFF",
        "text": "#333333"
    }

# Error handling
class ErrorConfig:
    """Error handling configuration"""
    
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # seconds
    TIMEOUT = 10  # seconds
    
    ERROR_MESSAGES = {
        "api_key_missing": "Please set your weather API key in the configuration",
        "network_error": "Unable to connect to weather service",
        "city_not_found": "City not found. Please check the spelling",
        "rate_limit": "API rate limit exceeded. Please try again later"
    }

# Development settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        'weather_api': WeatherAPIConfig.__dict__,
        'app': AppConfig.__dict__,
        'ui': UIConfig.__dict__,
        'error': ErrorConfig.__dict__,
        'debug': DEBUG,
        'log_level': LOG_LEVEL
    }

def validate_config() -> bool:
    """Validate that required configuration is present"""
    if WeatherAPIConfig.OPENWEATHER_API_KEY == 'your_api_key_here':
        print("Warning: Please set your OpenWeatherMap API key")
        return False
    return True