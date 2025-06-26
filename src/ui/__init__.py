"""UI package for the Weather Dashboard application."""

from .cli_interface import CliInterface
from .gui_interface import WeatherDashboardGUI

__all__ = [
    'CliInterface',
    'WeatherDashboardGUI'
]
