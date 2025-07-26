"""
UI Styling Module for Weather Dashboard.

This module contains all styling-related classes including weather icons,
glassmorphic design styles, and animation helpers.
"""

import tkinter as tk
from typing import Optional


class WeatherIcons:
    """Weather condition icons using Unicode characters."""

    CLEAR = "☀️"
    PARTLY_CLOUDY = "⛅"
    CLOUDY = "☁️"
    OVERCAST = "☁️"
    RAIN = "🌧️"
    HEAVY_RAIN = "⛈️"
    SNOW = "❄️"
    FOG = "🌫️"
    WIND = "💨"
    HOT = "🔥"
    COLD = "🧊"
    DEFAULT = "🌤️"

    @classmethod
    def get_icon(cls, condition: str, temperature: Optional[float] = None) -> str:
        """Get appropriate weather icon for condition."""
        condition_lower = condition.lower()

        # Temperature-based icons
        if temperature is not None:
            if temperature > 85:
                return cls.HOT
            elif temperature < 32:
                return cls.COLD

        # Condition-based icons
        if "clear" in condition_lower or "sunny" in condition_lower:
            return cls.CLEAR
        elif "partly" in condition_lower or "scattered" in condition_lower:
            return cls.PARTLY_CLOUDY
        elif "overcast" in condition_lower:
            return cls.OVERCAST
        elif "cloudy" in condition_lower or "cloud" in condition_lower:
            return cls.CLOUDY
        elif "rain" in condition_lower or "shower" in condition_lower:
            if "heavy" in condition_lower or "storm" in condition_lower:
                return cls.HEAVY_RAIN
            return cls.RAIN
        elif "snow" in condition_lower or "blizzard" in condition_lower:
            return cls.SNOW
        elif "fog" in condition_lower or "mist" in condition_lower:
            return cls.FOG
        elif "wind" in condition_lower:
            return cls.WIND
        else:
            return cls.DEFAULT


class GlassmorphicStyle:
    """Custom styling for glassmorphic design with enhanced visual features."""

    # Enhanced color scheme with gradients
    BACKGROUND = "#0a0a0a"  # Deeper dark base
    BACKGROUND_SECONDARY = "#1a1a1a"  # Secondary dark
    GLASS_BG = "#1e1e1e"  # Enhanced glass background
    GLASS_BG_LIGHT = "#2a2a2a"  # Lighter glass variant
    GLASS_BORDER = "#404040"  # More visible glass border
    GLASS_BORDER_LIGHT = "#555555"  # Lighter border variant

    # Enhanced accent colors
    ACCENT = "#4a9eff"  # Blue accent
    ACCENT_DARK = "#2563eb"  # Darker blue
    ACCENT_LIGHT = "#60a5fa"  # Lighter blue
    ACCENT_SECONDARY = "#ff6b4a"  # Orange accent
    ACCENT_SECONDARY_DARK = "#ea580c"  # Darker orange
    ACCENT_SECONDARY_LIGHT = "#fb7c56"  # Lighter orange

    # Text colors
    TEXT_PRIMARY = "#ffffff"  # White text
    TEXT_SECONDARY = "#b0b0b0"  # Gray text
    TEXT_TERTIARY = "#808080"  # Darker gray text
    TEXT_ACCENT = "#4a9eff"  # Accent colored text

    # Status colors
    SUCCESS = "#22c55e"  # Green
    SUCCESS_LIGHT = "#4ade80"  # Light green
    WARNING = "#f59e0b"  # Amber
    WARNING_LIGHT = "#fbbf24"  # Light amber
    ERROR = "#ef4444"  # Red
    ERROR_LIGHT = "#f87171"  # Light red

    # Weather-specific colors
    WEATHER_HOT = "#ff4444"  # Hot temperature
    WEATHER_WARM = "#ff8844"  # Warm temperature
    WEATHER_MILD = "#44aa44"  # Mild temperature
    WEATHER_COOL = "#4488ff"  # Cool temperature
    WEATHER_COLD = "#8844ff"  # Cold temperature

    # Font configuration
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"
    FONT_SIZE_XLARGE = 32  # For main temperature display
    FONT_SIZE_LARGE = 18
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_SMALL = 12
    FONT_SIZE_TINY = 10

    @classmethod
    def get_temperature_color(cls, temperature: float) -> str:
        """Get color for temperature based on value."""
        if temperature >= 85:
            return cls.WEATHER_HOT
        elif temperature >= 75:
            return cls.WEATHER_WARM
        elif temperature >= 60:
            return cls.WEATHER_MILD
        elif temperature >= 40:
            return cls.WEATHER_COOL
        else:
            return cls.WEATHER_COLD


class AnimationHelper:
    """Helper class for creating smooth animations."""

    @staticmethod
    def fade_in(widget, duration=500):
        """Fade in animation for widget."""
        widget.configure(fg=GlassmorphicStyle.TEXT_SECONDARY)
        steps = 20
        step_time = duration // steps

        def animate_step(step):
            if step <= steps:
                # Calculate alpha value (simulated with color intensity)
                alpha = step / steps
                color_intensity = int(176 + (255 - 176) * alpha)  # From gray to white
                color = f"#{color_intensity: 02x}{color_intensity: 02x}{color_intensity: 02x}"
                widget.configure(fg=color)
                widget.after(step_time, lambda: animate_step(step + 1))
            else:
                widget.configure(fg=GlassmorphicStyle.TEXT_PRIMARY)

        animate_step(0)

    @staticmethod
    def pulse_effect(widget, color=None, duration=1000):
        """Create a pulsing effect on widget."""
        original_bg = widget.cget("bg")
        pulse_color = color or GlassmorphicStyle.ACCENT

        def pulse_step(increasing=True, step=0):
            if step < 50:
                # Calculate intermediate color
                ratio = step / 50.0 if increasing else (50 - step) / 50.0
                # Simple color interpolation (in real implementation, would be more sophisticated)
                widget.configure(bg=pulse_color if ratio > 0.5 else original_bg)
                widget.after(duration // 100, lambda: pulse_step(increasing, step + 1))
            elif increasing:
                pulse_step(False, 0)
            else:
                widget.configure(bg=original_bg)
                # Repeat pulse
                widget.after(duration, lambda: pulse_step(True, 0))

        pulse_step()

    @staticmethod
    def text_glow_effect(widget, glow_color=None, duration=2000):
        """Create a text glow effect by cycling through related colors."""
        glow_color = glow_color or GlassmorphicStyle.ACCENT
        original_color = widget.cget("fg")

        # Create a list of colors for the glow effect
        glow_colors = [
            original_color,
            glow_color,
            GlassmorphicStyle.TEXT_PRIMARY,
            glow_color,
            original_color,
        ]

        def cycle_colors(color_index=0, step=0):
            if step >= len(glow_colors):
                step = 0

            widget.configure(fg=glow_colors[step])
            widget.after(
                duration // len(glow_colors),
                lambda: cycle_colors(color_index, (step + 1) % len(glow_colors)),
            )

        cycle_colors()

    @staticmethod
    def rainbow_text_effect(widget, duration=3000):
        """Create a subtle rainbow effect on text."""
        colors = [
            GlassmorphicStyle.ACCENT,
            GlassmorphicStyle.ACCENT_SECONDARY,
            GlassmorphicStyle.SUCCESS,
            GlassmorphicStyle.WARNING,
            GlassmorphicStyle.TEXT_PRIMARY,
        ]

        def cycle_rainbow(color_index=0):
            widget.configure(fg=colors[color_index])
            next_index = (color_index + 1) % len(colors)
            widget.after(duration // len(colors), lambda: cycle_rainbow(next_index))

        cycle_rainbow()
