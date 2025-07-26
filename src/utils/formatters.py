"""Utility functions for the Weather Dashboard application."""

import logging
import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple


def validate_city_name(city: str) -> bool:
    """
    Validate city name format.

    Args:
        city: City name to validate

    Returns:
        True if valid, False otherwise
    """
    if not city or not isinstance(city, str):
        return False

    # Remove extra whitespace
    city = city.strip()

    # Check length
    if len(city) < 2 or len(city) > 100:
        return False

    # Allow letters, spaces, hyphens, apostrophes, periods, and unicode characters
    # This pattern allows international city names with accents and special characters
    pattern = r"^[a-zA-ZÀ-ÿ\u0100-\u017F\u0180-\u024F\u1E00-\u1EFF\s\-\'.]+$"
    return bool(re.match(pattern, city))


def clean_city_name(city: str) -> str:
    """
    Clean and format city name.

    Args:
        city: Raw city name

    Returns:
        Cleaned city name
    """
    if not city:
        return ""

    # Remove extra whitespace
    city = city.strip()

    # Remove multiple spaces
    city = re.sub(r"\s+", " ", city)

    # Capitalize words
    city = city.title()

    return city


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate geographic coordinates.

    Args:
        latitude: Latitude value
        longitude: Longitude value

    Returns:
        True if valid, False otherwise
    """
    try:
        lat = float(latitude)
        lon = float(longitude)

        return -90 <= lat <= 90 and -180 <= lon <= 180
    except (ValueError, TypeError):
        return False


def format_temperature(temp: float, unit: str = "C", decimal_places: int = 1) -> str:
    """
    Format temperature with unit.

    Args:
        temp: Temperature value
        unit: Temperature unit (C, F, K)
        decimal_places: Number of decimal places

    Returns:
        Formatted temperature string
    """
    unit_symbols = {"C": "°C", "F": "°F", "K": "K"}

    symbol = unit_symbols.get(unit.upper(), "°C")
    return f"{temp: .{decimal_places}f}{symbol}"


def format_percentage(value: float, decimal_places: int = 0) -> str:
    """
    Format percentage value.

    Args:
        value: Percentage value
        decimal_places: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value: .{decimal_places}f}%"


def format_wind_speed(speed: float, unit: str = "km/h") -> str:
    """
    Format wind speed with unit.

    Args:
        speed: Wind speed value
        unit: Speed unit

    Returns:
        Formatted wind speed string
    """
    return f"{speed: .1f} {unit}"


def format_pressure(pressure: float, unit: str = "hPa") -> str:
    """
    Format atmospheric pressure.

    Args:
        pressure: Pressure value
        unit: Pressure unit

    Returns:
        Formatted pressure string
    """
    # Format to preserve decimal places as given
    if pressure == int(pressure):
        return f"{pressure: .1f} {unit}"
    else:
        # Use the original precision
        return f"{pressure: g} {unit}"


def format_visibility(visibility: float, unit: str = "km") -> str:
    """
    Format visibility distance.

    Args:
        visibility: Visibility distance
        unit: Distance unit

    Returns:
        Formatted visibility string
    """
    return f"{visibility: .1f} {unit}"


def parse_date_string(date_str: str) -> Optional[datetime]:
    """
    Parse date string into datetime object.

    Args:
        date_str: Date string in various formats

    Returns:
        Datetime object or None if parsing fails
    """
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%d/%m/%Y",
        "%m/%d/%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    logging.warning(f"Could not parse date string: {date_str}")
    return None


def format_datetime(dt: datetime, format_type: str = "default") -> str:
    """
    Format datetime for display.

    Args:
        dt: Datetime object
        format_type: Format type (default, short, long, time_only)

    Returns:
        Formatted datetime string
    """
    formats = {
        "default": "%Y-%m-%d %H:%M",
        "short": "%m/%d %H:%M",
        "long": "%A, %B %d, %Y at %I:%M %p",
        "time_only": "%H:%M",
        "date_only": "%Y-%m-%d",
    }

    fmt = formats.get(format_type, formats["default"])
    return dt.strftime(fmt)


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Float value or default
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        Integer value or default
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def is_severe_weather_condition(
    condition: str, wind_speed: float = 0, precipitation: float = 0
) -> bool:
    """
    Determine if weather conditions are severe.

    Args:
        condition: Weather condition
        wind_speed: Wind speed
        precipitation: Precipitation amount

    Returns:
        True if conditions are severe
    """
    severe_conditions = ["thunderstorm", "snow", "tornado", "hurricane"]

    return (
        condition.lower() in severe_conditions
        or wind_speed > 50  # Strong wind (km/h)
        or precipitation > 10  # Heavy precipitation (mm)
    )


def calculate_heat_index(temp_celsius: float, humidity: int) -> Optional[float]:
    """
    Calculate heat index (feels like temperature).

    Args:
        temp_celsius: Temperature in Celsius
        humidity: Relative humidity percentage

    Returns:
        Heat index in Celsius or None if not applicable
    """
    # Convert to Fahrenheit for calculation
    temp_f = temp_celsius * 9 / 5 + 32

    # Heat index is only meaningful above 80°F (26.7°C)
    if temp_f < 80:
        return None

    try:
        # Simplified heat index formula
        hi = (
            -42.379
            + 2.04901523 * temp_f
            + 10.14333127 * humidity
            - 0.22475541 * temp_f * humidity
            - 6.83783e-3 * temp_f**2
            - 5.481717e-2 * humidity**2
            + 1.22874e-3 * temp_f**2 * humidity
            + 8.5282e-4 * temp_f * humidity**2
            - 1.99e-6 * temp_f**2 * humidity**2
        )

        # Convert back to Celsius
        return (hi - 32) * 5 / 9

    except Exception:
        return None


def get_wind_direction_emoji(direction_degrees: Optional[int]) -> str:
    """
    Get wind direction emoji.

    Args:
        direction_degrees: Wind direction in degrees

    Returns:
        Wind direction emoji
    """
    if direction_degrees is None:
        return "🌪️"

    # Normalize to 0-360
    direction = direction_degrees % 360

    if 337.5 <= direction or direction < 22.5:
        return "⬆️"  # North
    elif 22.5 <= direction < 67.5:
        return "↗️"  # Northeast
    elif 67.5 <= direction < 112.5:
        return "➡️"  # East
    elif 112.5 <= direction < 157.5:
        return "↘️"  # Southeast
    elif 157.5 <= direction < 202.5:
        return "⬇️"  # South
    elif 202.5 <= direction < 247.5:
        return "↙️"  # Southwest
    elif 247.5 <= direction < 292.5:
        return "⬅️"  # West
    elif 292.5 <= direction < 337.5:
        return "↖️"  # Northwest
    else:
        return "🌪️"
