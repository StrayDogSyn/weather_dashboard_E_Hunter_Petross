"""Weather Dashboard Application Package.

A professional-level, secure, and modular weather dashboard application
following clean architecture and separation of concerns principles.
"""

__version__ = "1.0.0"
__author__ = "E Hunter Petross"
__description__ = "A comprehensive weather dashboard with secure API integration"

# Import main application components
try:
    from .app_gui import WeatherDashboardGUI
    __all__ = ['WeatherDashboardGUI']
except ImportError:
    __all__ = []
