"""Validation utilities for the Weather Dashboard application."""

import re
import logging
from typing import Optional, List, Any, Dict
from datetime import datetime


class ValidationError(Exception):
    """Custom validation error."""
    pass


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Remove whitespace
    api_key = api_key.strip()
    
    # Check length (OpenWeatherMap keys are typically 32 characters)
    if len(api_key) < 16 or len(api_key) > 64:
        return False
    
    # Check for alphanumeric characters
    return api_key.isalnum()


def validate_temperature_range(temp: float, unit: str = "C") -> bool:
    """
    Validate temperature is within reasonable range.
    
    Args:
        temp: Temperature value
        unit: Temperature unit (C, F, K)
        
    Returns:
        True if within reasonable range
    """
    try:
        temp = float(temp)
        
        # Convert to Celsius for validation
        if unit.upper() == "F":
            temp = (temp - 32) * 5/9
        elif unit.upper() == "K":
            temp = temp - 273.15
        
        # Reasonable Earth temperature range: -89°C to +60°C
        # (-89°C is Antarctica record, +60°C is extreme heat)
        return -89 <= temp <= 60
        
    except (ValueError, TypeError):
        return False


def validate_humidity(humidity: Any) -> bool:
    """
    Validate humidity percentage.
    
    Args:
        humidity: Humidity value
        
    Returns:
        True if valid (0-100%)
    """
    try:
        hum = float(humidity)
        return 0 <= hum <= 100
    except (ValueError, TypeError):
        return False


def validate_pressure(pressure: Any) -> bool:
    """
    Validate atmospheric pressure.
    
    Args:
        pressure: Pressure value in hPa
        
    Returns:
        True if within reasonable range
    """
    try:
        press = float(pressure)
        # Reasonable pressure range: 870-1085 hPa
        return 870 <= press <= 1085
    except (ValueError, TypeError):
        return False


def validate_wind_speed(speed: Any) -> bool:
    """
    Validate wind speed.
    
    Args:
        speed: Wind speed value
        
    Returns:
        True if within reasonable range
    """
    try:
        ws = float(speed)
        # Reasonable wind speed range: 0-200 km/h
        return 0 <= ws <= 200
    except (ValueError, TypeError):
        return False


def validate_wind_direction(direction: Any) -> bool:
    """
    Validate wind direction.
    
    Args:
        direction: Wind direction in degrees
        
    Returns:
        True if valid (0-360 degrees)
    """
    try:
        dir_deg = float(direction)
        return 0 <= dir_deg <= 360
    except (ValueError, TypeError):
        return False


def validate_visibility(visibility: Any) -> bool:
    """
    Validate visibility distance.
    
    Args:
        visibility: Visibility in km
        
    Returns:
        True if within reasonable range
    """
    try:
        vis = float(visibility)
        # Reasonable visibility range: 0-50 km
        return 0 <= vis <= 50
    except (ValueError, TypeError):
        return False


def validate_uv_index(uv: Any) -> bool:
    """
    Validate UV index.
    
    Args:
        uv: UV index value
        
    Returns:
        True if within valid range
    """
    try:
        uv_val = float(uv)
        # UV index range: 0-16+
        return 0 <= uv_val <= 20
    except (ValueError, TypeError):
        return False


def validate_precipitation(precip: Any) -> bool:
    """
    Validate precipitation amount.
    
    Args:
        precip: Precipitation in mm
        
    Returns:
        True if within reasonable range
    """
    try:
        prec = float(precip)
        # Reasonable precipitation range: 0-200 mm
        return 0 <= prec <= 200
    except (ValueError, TypeError):
        return False


def validate_weather_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate complete weather data structure.
    
    Args:
        data: Weather data dictionary
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check required fields
    required_fields = ['city', 'temperature', 'humidity', 'description']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate temperature
    if 'temperature' in data and not validate_temperature_range(data['temperature']):
        errors.append("Invalid temperature value")
    
    # Validate humidity
    if 'humidity' in data and not validate_humidity(data['humidity']):
        errors.append("Invalid humidity value")
    
    # Validate pressure
    if 'pressure' in data and not validate_pressure(data['pressure']):
        errors.append("Invalid pressure value")
    
    # Validate wind speed
    if 'wind_speed' in data and not validate_wind_speed(data['wind_speed']):
        errors.append("Invalid wind speed value")
    
    # Validate wind direction
    if 'wind_direction' in data and not validate_wind_direction(data['wind_direction']):
        errors.append("Invalid wind direction value")
    
    # Validate visibility
    if 'visibility' in data and not validate_visibility(data['visibility']):
        errors.append("Invalid visibility value")
    
    # Validate UV index
    if 'uv_index' in data and not validate_uv_index(data['uv_index']):
        errors.append("Invalid UV index value")
    
    # Validate precipitation
    if 'precipitation' in data and not validate_precipitation(data['precipitation']):
        errors.append("Invalid precipitation value")
    
    return errors


def sanitize_input(text: str, max_length: int = 100) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove potentially dangerous characters
    # Allow letters, numbers, spaces, and common punctuation
    sanitized = re.sub(r'[^\w\s\-.,\'\"()]+', '', text)
    
    return sanitized


def validate_forecast_days(days: Any) -> bool:
    """
    Validate forecast days parameter.
    
    Args:
        days: Number of forecast days
        
    Returns:
        True if valid (1-16 days typically)
    """
    try:
        day_count = int(days)
        return 1 <= day_count <= 16
    except (ValueError, TypeError):
        return False


def validate_units(units: str) -> bool:
    """
    Validate temperature units parameter.
    
    Args:
        units: Units string
        
    Returns:
        True if valid units
    """
    valid_units = ['metric', 'imperial', 'standard', 'kelvin']
    return units.lower() in valid_units


def validate_config_value(key: str, value: Any) -> bool:
    """
    Validate configuration values.
    
    Args:
        key: Configuration key
        value: Configuration value
        
    Returns:
        True if valid
    """
    validators = {
        'api_key': lambda v: validate_api_key(str(v)) if v else False,
        'timeout': lambda v: isinstance(v, (int, float)) and 1 <= v <= 60,
        'max_retries': lambda v: isinstance(v, int) and 0 <= v <= 10,
        'cache_duration': lambda v: isinstance(v, int) and 0 <= v <= 3600,
        'update_interval': lambda v: isinstance(v, int) and 1000 <= v <= 300000,
        'log_level': lambda v: str(v).upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    }
    
    validator = validators.get(key)
    if validator:
        try:
            return validator(value)
        except Exception as e:
            logging.warning(f"Validation error for {key}: {e}")
            return False
    
    # Default validation - just check if value exists
    return value is not None


class WeatherDataValidator:
    """Weather data validation class."""
    
    def __init__(self, strict: bool = False):
        """
        Initialize validator.
        
        Args:
            strict: Whether to use strict validation
        """
        self.strict = strict
        self.errors: List[str] = []
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate weather data.
        
        Args:
            data: Weather data to validate
            
        Returns:
            True if valid, False otherwise
        """
        self.errors.clear()
        
        # Validate structure
        if not isinstance(data, dict):
            self.errors.append("Data must be a dictionary")
            return False
        
        # Validate individual fields
        errors = validate_weather_data(data)
        self.errors.extend(errors)
        
        return len(self.errors) == 0
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.errors.copy()
    
    def is_valid(self, data: Dict[str, Any]) -> bool:
        """Check if data is valid without storing errors."""
        return self.validate(data)
