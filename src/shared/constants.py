"""Application-wide constants for Weather Dashboard.

This module contains all constants used throughout the application
to ensure consistency and easy maintenance.
"""

from typing import Final

# Cache Configuration
DEFAULT_CACHE_TTL: Final[int] = 300  # 5 minutes in seconds
WEATHER_CACHE_TTL: Final[int] = 600  # 10 minutes for weather data
FORECAST_CACHE_TTL: Final[int] = 1800  # 30 minutes for forecast data
CITY_CACHE_TTL: Final[int] = 86400  # 24 hours for city data

# API Configuration
API_TIMEOUT: Final[int] = 30  # seconds
MAX_RETRIES: Final[int] = 3
RETRY_DELAY: Final[float] = 1.0  # seconds
RATE_LIMIT_DELAY: Final[float] = 0.1  # seconds between requests

# Weather Configuration
MAX_FORECAST_DAYS: Final[int] = 7
DEFAULT_TEMPERATURE_UNIT: Final[str] = "celsius"
SUPPORTED_UNITS: Final[tuple] = ("celsius", "fahrenheit", "kelvin")
DEFAULT_CITY: Final[str] = "London"

# UI Configuration
DEFAULT_WINDOW_WIDTH: Final[int] = 1200
DEFAULT_WINDOW_HEIGHT: Final[int] = 800
MIN_WINDOW_WIDTH: Final[int] = 800
MIN_WINDOW_HEIGHT: Final[int] = 600
ANIMATION_DURATION: Final[int] = 300  # milliseconds
REFRESH_INTERVAL: Final[int] = 60000  # milliseconds (1 minute)

# Data Validation
MAX_CITY_NAME_LENGTH: Final[int] = 100
MAX_JOURNAL_ENTRY_LENGTH: Final[int] = 5000
MAX_ACTIVITY_SUGGESTIONS: Final[int] = 10
MAX_POETRY_LENGTH: Final[int] = 1000
MAX_FAVORITES_COUNT: Final[int] = 50

# File Paths
CONFIG_DIR: Final[str] = "config"
DATA_DIR: Final[str] = "data"
LOGS_DIR: Final[str] = "logs"
CACHE_DIR: Final[str] = "cache"
TEMP_DIR: Final[str] = "temp"

# File Extensions
CONFIG_FILE_EXT: Final[str] = ".yaml"
DATA_FILE_EXT: Final[str] = ".json"
LOG_FILE_EXT: Final[str] = ".log"
CACHE_FILE_EXT: Final[str] = ".cache"

# Logging Configuration
DEFAULT_LOG_LEVEL: Final[str] = "INFO"
LOG_FORMAT: Final[str] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
MAX_LOG_FILE_SIZE: Final[int] = 10 * 1024 * 1024  # 10 MB
MAX_LOG_FILES: Final[int] = 5

# Database Configuration
DEFAULT_DB_NAME: Final[str] = "weather_dashboard.db"
DB_CONNECTION_TIMEOUT: Final[int] = 30
DB_QUERY_TIMEOUT: Final[int] = 10
MAX_DB_CONNECTIONS: Final[int] = 10

# Voice Assistant Configuration
VOICE_TIMEOUT: Final[int] = 5  # seconds
VOICE_SAMPLE_RATE: Final[int] = 16000
VOICE_CHANNELS: Final[int] = 1
VOICE_CHUNK_SIZE: Final[int] = 1024

# Weather Conditions
WEATHER_CONDITIONS: Final[dict] = {
    "clear": ["clear", "sunny", "fair"],
    "cloudy": ["cloudy", "overcast", "partly cloudy"],
    "rainy": ["rain", "drizzle", "shower", "thunderstorm"],
    "snowy": ["snow", "sleet", "blizzard", "flurries"],
    "foggy": ["fog", "mist", "haze"],
    "windy": ["windy", "breezy", "gusty"]
}

# Temperature Ranges (Celsius)
TEMPERATURE_RANGES: Final[dict] = {
    "freezing": (-50, 0),
    "cold": (0, 10),
    "cool": (10, 20),
    "mild": (20, 25),
    "warm": (25, 30),
    "hot": (30, 40),
    "extreme": (40, 60)
}

# Activity Categories
ACTIVITY_CATEGORIES: Final[tuple] = (
    "outdoor",
    "indoor",
    "sports",
    "cultural",
    "relaxation",
    "adventure",
    "social",
    "educational"
)

# Poetry Styles
POETRY_STYLES: Final[tuple] = (
    "haiku",
    "limerick",
    "sonnet",
    "free_verse",
    "acrostic",
    "cinquain"
)

# Error Messages
ERROR_MESSAGES: Final[dict] = {
    "network_error": "Network connection failed. Please check your internet connection.",
    "api_error": "Weather service is temporarily unavailable. Please try again later.",
    "validation_error": "Invalid input provided. Please check your data and try again.",
    "config_error": "Configuration error detected. Please check your settings.",
    "storage_error": "Data storage operation failed. Please try again.",
    "cache_error": "Cache operation failed. Data may not be up to date.",
    "ui_error": "User interface error occurred. Please restart the application.",
    "service_error": "Service operation failed. Please try again later."
}

# Success Messages
SUCCESS_MESSAGES: Final[dict] = {
    "data_saved": "Data saved successfully.",
    "data_loaded": "Data loaded successfully.",
    "cache_cleared": "Cache cleared successfully.",
    "config_updated": "Configuration updated successfully.",
    "export_completed": "Data export completed successfully.",
    "import_completed": "Data import completed successfully."
}

# HTTP Status Codes
HTTP_STATUS: Final[dict] = {
    "OK": 200,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "TOO_MANY_REQUESTS": 429,
    "INTERNAL_SERVER_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503
}

# Regular Expressions
REGEX_PATTERNS: Final[dict] = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "city_name": r"^[a-zA-Z\s\-'.,]{1,100}$",
    "coordinates": r"^-?\d{1,3}\.\d{1,6},-?\d{1,3}\.\d{1,6}$",
    "temperature": r"^-?\d{1,3}(\.\d{1,2})?$",
    "date": r"^\d{4}-\d{2}-\d{2}$",
    "time": r"^\d{2}:\d{2}(:\d{2})?$"
}