"""UI Components module for Weather Dashboard.

This module contains reusable UI components for the weather dashboard application.
"""

from .header import ApplicationHeader
from .main_dashboard import MainDashboard
from .search_panel import SearchPanel
from .temperature_controls import TemperatureControls, TemperatureUnit
from .weather_card import WeatherCard
from .weather_icons import WeatherIcons

# Import ModernEntry from the parent components.py if it exists
try:
    from ..components import ModernEntry
except ImportError:
    # Create a placeholder if the import fails
    class ModernEntry:
        pass


__all__ = [
    "WeatherIcons",
    "WeatherCard",
    "SearchPanel",
    "ApplicationHeader",
    "TemperatureControls",
    "TemperatureUnit",
    "MainDashboard",
    "ModernEntry",
]
