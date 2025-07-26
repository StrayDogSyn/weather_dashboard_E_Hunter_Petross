"""Presentation layer for Weather Dashboard.

This package contains all user interface components including
GUI and CLI applications, following the MVP (Model-View-Presenter)
architectural pattern.
"""

from .cli_app import WeatherDashboardCLIApp
from .gui_app import WeatherDashboardGUIApp

__all__ = [
    "WeatherDashboardGUIApp",
    "WeatherDashboardCLIApp",
]
