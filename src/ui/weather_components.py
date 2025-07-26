"""
Weather-specific UI Components for Weather Dashboard.

This module contains weather-specific UI components including WeatherCard
and related weather display components.
"""

import tkinter as tk
from typing import Optional

from .styling import WeatherIcons, GlassmorphicStyle, AnimationHelper
from .components import GlassmorphicFrame
from src.models.weather_models import CurrentWeather


class WeatherCard(GlassmorphicFrame):
    """Enhanced weather information card with improved visual features."""

    def __init__(self, parent, gui_ref=None, **kwargs):
        super().__init__(parent, elevated=True, gradient=True, **kwargs)
        self.gui_ref = gui_ref  # Reference to main GUI for temperature unit
        self.setup_layout()

    def setup_layout(self):
        """Setup the enhanced card layout with better visual hierarchy."""
        # Main container with reduced padding for better fit
        main_container = tk.Frame(self, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Title with icon
        title_frame = tk.Frame(main_container, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        self.title_label = tk.Label(
            title_frame,
            text="🌤️ Weather",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_LARGE,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=self.bg_color,
        )
        self.title_label.pack()

        # Content frame with center alignment
        self.content_frame = tk.Frame(main_container, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

    def update_weather(self, weather: CurrentWeather):
        """Update the card with weather data and enhanced visuals."""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Weather icon (large and prominent)
        temp_celsius = weather.temperature.to_celsius()
        icon = WeatherIcons.get_icon(weather.description, temp_celsius)
        icon_label = tk.Label(
            self.content_frame,
            text=icon,
            font=(GlassmorphicStyle.FONT_FAMILY, 56),  # Slightly smaller icon
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=self.bg_color,
        )
        icon_label.pack(pady=(5, 10))  # Reduced padding

        # Location with enhanced styling
        location_label = tk.Label(
            self.content_frame,
            text=weather.location.display_name,
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_LARGE,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_ACCENT,
            bg=self.bg_color,
        )
        location_label.pack(pady=(0, 8))  # Reduced padding

        # Temperature with color-coded display
        if self.gui_ref:
            temp_value, temp_unit = self.gui_ref.convert_temperature(temp_celsius)
            temp_text = (
                f"{temp_value: .1f}{temp_unit}"  # Fixed: removed extra degree symbol
            )
        else:
            temp_text = f"{temp_celsius: .1f}°C"
            temp_value = temp_celsius

        # Get temperature color based on value
        temp_color = GlassmorphicStyle.get_temperature_color(temp_value)

        temp_label = tk.Label(
            self.content_frame,
            text=temp_text,
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_XLARGE,
                "bold",
            ),
            fg=temp_color,
            bg=self.bg_color,
        )
        temp_label.pack(pady=(0, 3))  # Reduced padding

        # Condition with better formatting
        condition_label = tk.Label(
            self.content_frame,
            text=weather.description.title(),
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_MEDIUM,
                "italic",
            ),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color,
        )
        condition_label.pack(pady=(0, 15))  # Reduced padding

        # Enhanced weather details in a grid-like layout
        details_frame = GlassmorphicFrame(
            self.content_frame, bg_color=GlassmorphicStyle.GLASS_BG_LIGHT
        )
        details_frame.pack(fill=tk.X, pady=(5, 0))  # Reduced top padding

        # Create two columns for details
        left_details = tk.Frame(details_frame, bg=details_frame.bg_color)
        left_details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        right_details = tk.Frame(details_frame, bg=details_frame.bg_color)
        right_details.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Humidity with enhanced styling
        humidity_frame = tk.Frame(left_details, bg=details_frame.bg_color)
        humidity_frame.pack(fill=tk.X, pady=(0, 8))  # Reduced spacing

        humidity_icon = tk.Label(
            humidity_frame,
            text="💧",
            font=(GlassmorphicStyle.FONT_FAMILY, 20),
            fg=GlassmorphicStyle.ACCENT,
            bg=details_frame.bg_color,
        )
        humidity_icon.pack(side=tk.LEFT)

        humidity_label = tk.Label(
            humidity_frame,
            text=f" {weather.humidity}%",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_MEDIUM,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=details_frame.bg_color,
        )
        humidity_label.pack(side=tk.LEFT)

        humidity_desc = tk.Label(
            humidity_frame,
            text=" Humidity",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_TERTIARY,
            bg=details_frame.bg_color,
        )
        humidity_desc.pack(side=tk.LEFT)

        # Wind with enhanced styling
        wind_frame = tk.Frame(right_details, bg=details_frame.bg_color)
        wind_frame.pack(fill=tk.X, pady=(0, 8))  # Reduced spacing

        wind_icon = tk.Label(
            wind_frame,
            text="💨",
            font=(GlassmorphicStyle.FONT_FAMILY, 20),
            fg=GlassmorphicStyle.ACCENT_SECONDARY,
            bg=details_frame.bg_color,
        )
        wind_icon.pack(side=tk.LEFT)

        wind_label = tk.Label(
            wind_frame,
            text=f" {weather.wind.speed: .1f}",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_MEDIUM,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=details_frame.bg_color,
        )
        wind_label.pack(side=tk.LEFT)

        wind_desc = tk.Label(
            wind_frame,
            text=" km/h Wind",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_TERTIARY,
            bg=details_frame.bg_color,
        )
        wind_desc.pack(side=tk.LEFT)

        # Add pressure if available
        if hasattr(weather, "pressure") and weather.pressure:
            pressure_frame = tk.Frame(left_details, bg=details_frame.bg_color)
            pressure_frame.pack(fill=tk.X)

            pressure_icon = tk.Label(
                pressure_frame,
                text="🌡️",
                font=(GlassmorphicStyle.FONT_FAMILY, 20),
                fg=GlassmorphicStyle.SUCCESS,
                bg=details_frame.bg_color,
            )
            pressure_icon.pack(side=tk.LEFT)

            pressure_label = tk.Label(
                pressure_frame,
                text=f" {weather.pressure.value: .0f} hPa",
                font=(
                    GlassmorphicStyle.FONT_FAMILY,
                    GlassmorphicStyle.FONT_SIZE_MEDIUM,
                    "bold",
                ),
                fg=GlassmorphicStyle.TEXT_PRIMARY,
                bg=details_frame.bg_color,
            )
            pressure_label.pack(side=tk.LEFT)

            pressure_desc = tk.Label(
                pressure_frame,
                text=" hPa",
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
                fg=GlassmorphicStyle.TEXT_TERTIARY,
                bg=details_frame.bg_color,
            )
            pressure_desc.pack(side=tk.LEFT)

        # Add visibility if available
        if hasattr(weather, "visibility") and weather.visibility:
            visibility_frame = tk.Frame(right_details, bg=details_frame.bg_color)
            visibility_frame.pack(fill=tk.X)

            visibility_icon = tk.Label(
                visibility_frame,
                text="👁️",
                font=(GlassmorphicStyle.FONT_FAMILY, 20),
                fg=GlassmorphicStyle.WARNING,
                bg=details_frame.bg_color,
            )
            visibility_icon.pack(side=tk.LEFT)

            visibility_label = tk.Label(
                visibility_frame,
                text=f" {weather.visibility: .1f}",
                font=(
                    GlassmorphicStyle.FONT_FAMILY,
                    GlassmorphicStyle.FONT_SIZE_MEDIUM,
                    "bold",
                ),
                fg=GlassmorphicStyle.TEXT_PRIMARY,
                bg=details_frame.bg_color,
            )
            visibility_label.pack(side=tk.LEFT)

            visibility_desc = tk.Label(
                visibility_frame,
                text=" km",
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
                fg=GlassmorphicStyle.TEXT_TERTIARY,
                bg=details_frame.bg_color,
            )
            visibility_desc.pack(side=tk.LEFT)

        # Apply fade-in animation to the main elements
        AnimationHelper.fade_in(icon_label)
        AnimationHelper.fade_in(temp_label)

        # Apply subtle pulse effect to temperature for emphasis
        if temp_value > 85 or temp_value < 32:  # Extreme temperatures
            AnimationHelper.pulse_effect(temp_label, temp_color)
