"""Presentation layer for Weather Dashboard.

This package contains all user interface components including
GUI and CLI applications, following the MVP (Model-View-Presenter)
architectural pattern.
"""

from .gui_app import WeatherDashboardGUIApp
from .cli_app import WeatherDashboardCLIApp

__all__ = [
    "WeatherDashboardGUIApp",
    "WeatherDashboardCLIApp",
]