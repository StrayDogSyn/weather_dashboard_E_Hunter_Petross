"""Weather Dashboard Application Package.

A professional-level, secure, and modular weather dashboard application
following clean architecture and separation of concerns principles.
"""

__version__ = "1.0.0"
__author__ = "E Hunter Petross"
__description__ = "A comprehensive weather dashboard with secure API integration"

from .app import WeatherDashboardApp, main

__all__ = [
    'WeatherDashboardApp',
    'main'
]
