"""
Modern TKinter GUI with Glassmorphic Design for Weather Dashboard.

This module provides a modern, glassmorphic user interface using TKinter
with custom styling and modern visual elements including weather icons,
animations, and enhanced visual effects.
"""

# Modern UI imports with ttkbootstrap
import json
import logging
import threading
import tkinter as tk
import tkinter.font as tkFont
from datetime import date, datetime
from tkinter import messagebox, simpledialog, ttk
from typing import Any, Callable, Dict, List, Optional

# Bootstrap-inspired styling
import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import (
    PRIMARY, SECONDARY, SUCCESS, INFO, WARNING, DANGER, LIGHT, DARK
)

from src.config.config import config_manager
from src.interfaces.weather_interfaces import IUserInterface
from src.models.capstone_models import (
    ActivitySuggestion,
    JournalEntry,
    MoodType,
    WeatherComparison,
    WeatherPoem,
)
from src.models.weather_models import CurrentWeather, FavoriteCity, WeatherForecast


# Note: WeatherDashboard import will be added after class definition to avoid circular import


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
                color = (
                    f"#{color_intensity:02x}{color_intensity:02x}{color_intensity:02x}"
                )
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
    WEATHER_COOL = "#4488ff"  # Cool temperature
    WEATHER_COLD = "#4444ff"  # Cold temperature

    # Glassmorphic properties
    BLUR_RADIUS = 15
    TRANSPARENCY = 0.15
    BORDER_RADIUS = 16

    # Enhanced fonts
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"
    FONT_SIZE_XLARGE = 32  # For main temperature display
    FONT_SIZE_LARGE = 18
    FONT_SIZE_MEDIUM = 14
    FONT_SIZE_SMALL = 12
    FONT_SIZE_TINY = 10

    @classmethod
    def get_temperature_color(cls, temperature: float) -> str:
        """Get color based on temperature value."""
        if temperature >= 85:
            return cls.WEATHER_HOT
        elif temperature >= 70:
            return cls.WEATHER_WARM
        elif temperature >= 50:
            return cls.TEXT_PRIMARY
        elif temperature >= 32:
            return cls.WEATHER_COOL
        else:
            return cls.WEATHER_COLD


class GlassmorphicFrame(tk.Frame):
    """Custom frame with enhanced glassmorphic styling and 3D effects."""

    def __init__(
        self,
        parent,
        bg_color=None,
        border_color=None,
        elevated=False,
        gradient=False,
        blur_intensity=None,  # Added blur_intensity parameter
        **kwargs,
    ):
        # Remove blur_intensity from kwargs if it exists to avoid passing it to tkinter
        if "blur_intensity" in kwargs:
            blur_intensity = kwargs.pop("blur_intensity")

        super().__init__(parent, **kwargs)

        self.bg_color = bg_color or GlassmorphicStyle.GLASS_BG
        self.border_color = border_color or GlassmorphicStyle.GLASS_BORDER
        self.elevated = elevated
        self.gradient = gradient

        # Set blur intensity (higher value = more blur effect in border)
        blur_effect = 3  # Default
        if blur_intensity is not None:
            if blur_intensity > 10:
                blur_effect = 5  # High blur
            elif blur_intensity > 5:
                blur_effect = 4  # Medium blur

        # Enhanced styling with 3D effect and optional gradient
        if elevated:
            # Create elevated/raised appearance with shadow effect
            self.configure(
                bg=GlassmorphicStyle.GLASS_BG_LIGHT if gradient else self.bg_color,
                highlightbackground=GlassmorphicStyle.GLASS_BORDER_LIGHT,
                highlightcolor="#777777",
                highlightthickness=blur_effect,
                relief="raised",
                borderwidth=blur_effect,
            )
        else:
            # Enhanced standard glassmorphic styling with subtle 3D
            self.configure(
                bg=self.bg_color,
                highlightbackground=self.border_color,
                highlightcolor=GlassmorphicStyle.GLASS_BORDER_LIGHT,
                highlightthickness=2,
                relief="ridge",
                borderwidth=2,
            )


class ModernButton(tk.Button):
    """Modern styled button with enhanced hover effects, 3D appearance, and animations."""

    def __init__(self, parent, style="primary", icon=None, **kwargs):
        self.style = style
        self.icon = icon
        self.default_bg = self._get_bg_color()
        self.hover_bg = self._get_hover_color()
        self.is_hovered = False

        # Prepare button text with icon if provided
        text = kwargs.get("text", "")
        if self.icon:
            text = f"{self.icon} {text}"
            kwargs["text"] = text

        super().__init__(
            parent,
            bg=self.default_bg,
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_SMALL,
                "bold",
            ),
            relief="flat",  # Flat modern style
            borderwidth=0,  # No border for cleaner look
            padx=8,  # Reduced horizontal padding for more compact buttons
            pady=4,  # Reduced vertical padding for more compact look
            cursor="hand2",
            activebackground=self.hover_bg,
            activeforeground=GlassmorphicStyle.TEXT_PRIMARY,
            # Adding rounded corners effect with highlightbackground
            highlightbackground=self.default_bg,
            highlightcolor=self.default_bg,
            highlightthickness=1,
            **kwargs,
        )

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_click(self, event):
        """Handle button click for modern pressed effect with animation."""
        # Modern buttons use color and subtle scaling rather than relief changes
        click_color = self._get_click_color()
        self.configure(bg=click_color)
        # Add subtle shadow effect
        self.configure(highlightbackground=GlassmorphicStyle.GLASS_BORDER)

    def _on_release(self, event):
        """Handle button release to restore appearance with modern style."""
        self.configure(bg=self.hover_bg if self.is_hovered else self.default_bg)
        # Restore highlight to match background for seamless look
        self.configure(
            highlightbackground=self.hover_bg if self.is_hovered else self.default_bg
        )

    def _get_bg_color(self):
        if self.style == "primary":
            return GlassmorphicStyle.ACCENT
        elif self.style == "secondary":
            return GlassmorphicStyle.ACCENT_SECONDARY
        elif self.style == "success":
            return GlassmorphicStyle.SUCCESS
        elif self.style == "warning":
            return GlassmorphicStyle.WARNING
        elif self.style == "error":
            return GlassmorphicStyle.ERROR
        else:
            return GlassmorphicStyle.GLASS_BG

    def _get_hover_color(self):
        # Slightly lighter version of the base color
        base = self._get_bg_color()
        if base == GlassmorphicStyle.ACCENT:
            return GlassmorphicStyle.ACCENT_LIGHT
        elif base == GlassmorphicStyle.ACCENT_SECONDARY:
            return GlassmorphicStyle.ACCENT_SECONDARY_LIGHT
        elif base == GlassmorphicStyle.SUCCESS:
            return GlassmorphicStyle.SUCCESS_LIGHT
        elif base == GlassmorphicStyle.WARNING:
            return GlassmorphicStyle.WARNING_LIGHT
        elif base == GlassmorphicStyle.ERROR:
            return GlassmorphicStyle.ERROR_LIGHT
        else:
            return GlassmorphicStyle.GLASS_BG_LIGHT

    def _get_click_color(self):
        # Darker version for click effect
        base = self._get_bg_color()
        if base == GlassmorphicStyle.ACCENT:
            return GlassmorphicStyle.ACCENT_DARK
        elif base == GlassmorphicStyle.ACCENT_SECONDARY:
            return GlassmorphicStyle.ACCENT_SECONDARY_DARK
        else:
            return base

    def _on_enter(self, event):
        self.is_hovered = True
        self.configure(bg=self.hover_bg)
        # Add subtle glow effect with matching highlight for seamless rounded corners
        self.configure(highlightbackground=self.hover_bg, highlightcolor=self.hover_bg)
        # Subtle text brightening for modern feedback
        self.configure(fg="#ffffff")

    def _on_leave(self, event):
        self.is_hovered = False
        self.configure(bg=self.default_bg)
        # Match highlight to background for seamless look
        self.configure(
            highlightbackground=self.default_bg, highlightcolor=self.default_bg
        )
        # Restore normal text
        self.configure(fg=GlassmorphicStyle.TEXT_PRIMARY)


class BootstrapButton(ttk_bs.Button):
    """Modern Bootstrap-style button using ttkbootstrap."""

    def __init__(self, parent, style="primary", icon=None, **kwargs):
        # Prepare button text with icon if provided
        text = kwargs.get("text", "")
        if icon:
            text = f"{icon} {text}"
            kwargs["text"] = text
        
        # Initialize with ttkbootstrap - it inherits from ttk.Button
        super().__init__(parent, **kwargs)


class BootstrapFrame(ttk_bs.Frame):
    """Modern Bootstrap-style frame using ttkbootstrap."""
    
    def __init__(self, parent, style="", **kwargs):
        super().__init__(parent, **kwargs)


class BootstrapEntry(ttk_bs.Entry):
    """Modern Bootstrap-style entry using ttkbootstrap."""
    
    def __init__(self, parent, style="primary", **kwargs):
        super().__init__(parent, **kwargs)


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
                f"{temp_value:.1f}{temp_unit}"  # Fixed: removed extra degree symbol
            )
        else:
            temp_text = f"{temp_celsius:.1f}°C"
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
            text=f" {weather.wind.speed:.1f}",
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
                text=f" {weather.pressure.value:.0f} hPa",
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
                text=f" {weather.visibility:.1f}",
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


class ModernScrollableFrame(tk.Frame):
    """Scrollable frame with modern styling."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            self, bg=GlassmorphicStyle.BACKGROUND, highlightthickness=0
        )

        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(self.canvas, bg=GlassmorphicStyle.BACKGROUND)

        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack elements
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Bind mousewheel
        self.bind_mousewheel()

    def bind_mousewheel(self):
        """Bind mousewheel to canvas."""

        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.canvas.bind("<MouseWheel>", _on_mousewheel)


class WeatherDashboardGUI(IUserInterface):
    """Modern TKinter GUI for Weather Dashboard with glassmorphic design."""

    def __init__(self):
        """Initialize the GUI with ttkbootstrap styling."""
        # Initialize ttkbootstrap style first
        self.style = ttk_bs.Style(theme="superhero")  # Dark modern theme
        self.root = self.style.master
        
        self.config = config_manager.config
        self.logger = logging.getLogger(__name__)
        self.current_weather = None
        self.current_forecast_data = (
            None  # Store forecast data for temperature unit changes
        )
        self.temperature_unit = "C"  # Default to Celsius, can be "C" or "F"
        self.auto_refresh = False  # Auto-refresh state
        self.refresh_interval = (
            300000  # Default refresh interval: 5 minutes (in milliseconds)
        )
        self.refresh_timer = None  # Store the timer ID for auto-refresh
        
        # Initialize dashboard (import here to avoid circular import)
        from src.ui.dashboard import WeatherDashboard
        self.dashboard = WeatherDashboard(self.root)
        
        self.setup_window()
        self.setup_styles()
        self.create_layout()

        # Clean up any stray widgets
        self.cleanup_stray_widgets()

        # Callback storage
        self.callbacks = {}

        # Cleanup stray widgets on startup
        self.cleanup_stray_widgets()

    def setup_window(self):
        """Setup main window properties."""
        self.root.title("JTC Capstone - Team 5")
        self.root.geometry("1300x900")  # Increased height for better content fit
        self.root.minsize(1100, 700)  # Increased minimum size
        self.root.configure(bg=GlassmorphicStyle.BACKGROUND)

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1300 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1300x900+{x}+{y}")

        # Set up close handler to properly clean up
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_styles(self):
        """Setup custom styles."""
        style = ttk.Style()
        style.theme_use("clam")

        # Configure ttk styles for dark theme with enhanced 3D effects
        style.configure("TNotebook", background=GlassmorphicStyle.BACKGROUND)
        style.configure(
            "TNotebook.Tab",
            background=GlassmorphicStyle.GLASS_BG,
            foreground=GlassmorphicStyle.TEXT_SECONDARY,
            padding=[20, 12],  # Increased padding for better appearance
            relief="raised",  # 3D raised effect for tabs
            borderwidth=2,  # Border for 3D effect
            focuscolor="none",  # Remove focus outline
        )
        style.map(
            "TNotebook.Tab",
            background=[
                ("selected", GlassmorphicStyle.ACCENT),
                ("active", "#555555"),  # Hover effect
            ],
            foreground=[
                ("selected", GlassmorphicStyle.TEXT_PRIMARY),
                ("active", GlassmorphicStyle.TEXT_PRIMARY),
            ],
            relief=[
                ("selected", "sunken"),  # Pressed effect for active tab
                ("active", "raised"),
            ],
            borderwidth=[
                ("selected", 3),  # Thicker border for active tab
                ("active", 2),
            ],
        )

    def create_layout(self):
        """Create the main GUI layout."""
        # Header
        self.create_header()

        # Main content area with notebook
        self.create_main_content()

        # Status bar
        self.create_status_bar()

    def create_header(self):
        """Create compact header section with Justice Emoji and enhanced styling."""
        # Compact header frame with reduced padding
        header_frame = GlassmorphicFrame(self.root, elevated=True, gradient=True)
        header_frame.pack(fill=tk.X, padx=15, pady=(10, 5))

        # Main header container - compact single row
        main_header = tk.Frame(header_frame, bg=GlassmorphicStyle.GLASS_BG_LIGHT)
        main_header.pack(fill=tk.X, padx=15, pady=10)

        # Left side with compact logo and title layout
        left_container = tk.Frame(main_header, bg=GlassmorphicStyle.GLASS_BG_LIGHT)
        left_container.pack(side=tk.LEFT)

        # Compact horizontal icon layout
        icon_row = tk.Frame(left_container, bg=GlassmorphicStyle.GLASS_BG_LIGHT)
        icon_row.pack(side=tk.LEFT, padx=(0, 15))

        # Justice Emoji - compact size
        justice_emoji = tk.Label(
            icon_row,
            text="⚖️",
            font=(GlassmorphicStyle.FONT_FAMILY, 24),  # Smaller for compactness
            fg=GlassmorphicStyle.ACCENT_SECONDARY,
            bg=GlassmorphicStyle.GLASS_BG_LIGHT,
        )
        justice_emoji.pack(side=tk.LEFT, padx=(0, 5))

        # Weather icon next to Justice emoji
        weather_logo = tk.Label(
            icon_row,
            text="⛅",
            font=(GlassmorphicStyle.FONT_FAMILY, 20),  # Smaller for compactness
            fg=GlassmorphicStyle.ACCENT,
            bg=GlassmorphicStyle.GLASS_BG_LIGHT,
        )
        weather_logo.pack(side=tk.LEFT)

        # Compact title section - single column
        title_container = tk.Frame(left_container, bg=GlassmorphicStyle.GLASS_BG_LIGHT)
        title_container.pack(side=tk.LEFT)

        # Main title - reduced size for compactness
        title_main = tk.Label(
            title_container,
            text="JTC CAPSTONE • Team 5 Weather Dashboard",
            font=(GlassmorphicStyle.FONT_FAMILY, 18, "bold"),  # Single line title
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=GlassmorphicStyle.GLASS_BG_LIGHT,
        )
        title_main.pack(anchor=tk.W)

        # Compact tagline
        tagline = tk.Label(
            title_container,
            text="⚡ Justice Through Code & Climate ⚡",
            font=(GlassmorphicStyle.FONT_FAMILY, 11, "italic"),  # Smaller font
            fg=GlassmorphicStyle.ACCENT_SECONDARY_LIGHT,
            bg=GlassmorphicStyle.GLASS_BG_LIGHT,
        )
        tagline.pack(anchor=tk.W)

        # Right side container for buttons with modern layout
        right_container = tk.Frame(main_header, bg=GlassmorphicStyle.GLASS_BG_LIGHT)
        right_container.pack(side=tk.RIGHT, padx=20, pady=5)

        # Create a modern Bootstrap toolbar
        toolbar_frame = BootstrapFrame(right_container, style="dark")
        toolbar_frame.pack(pady=5)

        actions_frame = BootstrapFrame(toolbar_frame, style="dark")
        actions_frame.pack(padx=8, pady=5)

        # Search button
        self.search_btn = BootstrapButton(
            actions_frame,
            text="Search",
            icon="🔍",
            command=self.show_city_search,
            style="primary",
        )
        self.search_btn.pack(side=tk.LEFT, padx=2)

        # Modern separator using Bootstrap
        ttk_bs.Separator(actions_frame, orient='vertical').pack(
            side=tk.LEFT, fill=tk.Y, padx=3, pady=3
        )

        # Refresh and Auto-refresh as a logical group
        self.refresh_btn = BootstrapButton(
            actions_frame,
            text="Sync",
            icon="🔄",
            command=self.refresh_current_weather,
            style="info",
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=2)

        self.auto_refresh_btn = BootstrapButton(
            actions_frame,
            text="Auto",
            icon="⏱️",
            command=self.toggle_auto_refresh,
            style="success",
        )
        self.auto_refresh_btn.pack(side=tk.LEFT, padx=2)

        # Dashboard button
        self.dashboard_btn = BootstrapButton(
            actions_frame,
            text="Charts",
            icon="📊",
            command=self.show_dashboard,
            style="warning",
        )
        self.dashboard_btn.pack(side=tk.LEFT, padx=2)

        # Modern separator using Bootstrap
        ttk_bs.Separator(actions_frame, orient='vertical').pack(
            side=tk.LEFT, fill=tk.Y, padx=3, pady=3
        )

        # Temperature controls with Bootstrap styling
        temp_label = ttk_bs.Label(
            actions_frame,
            text="🌡️",
            font=(GlassmorphicStyle.FONT_FAMILY, 14),
        )
        temp_label.pack(side=tk.LEFT, padx=(0, 1))

        self.temp_toggle_btn = BootstrapButton(
            actions_frame,
            text="°C/°F",
            style="secondary",
            command=self.toggle_temperature_unit,
        )
        self.temp_toggle_btn.pack(side=tk.LEFT, padx=2)

        # Update toggle button text to show current unit
        self.update_temp_toggle_text()

        # Add impressive animation effects to the compact header elements
        AnimationHelper.pulse_effect(
            justice_emoji, GlassmorphicStyle.ACCENT_SECONDARY, 4000
        )
        AnimationHelper.pulse_effect(weather_logo, GlassmorphicStyle.ACCENT, 3500)
        AnimationHelper.text_glow_effect(title_main, GlassmorphicStyle.ACCENT, 3000)
        AnimationHelper.rainbow_text_effect(tagline, 5000)

    def create_main_content(self):
        """Create main content area with tabbed interface."""
        # Create Bootstrap-styled notebook (tabbed interface)
        self.notebook = ttk_bs.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 10))

        # Weather tab
        self.create_weather_tab()

        # Forecast tab
        self.create_forecast_tab()

        # Comparison tab
        self.create_comparison_tab()

        # Journal tab
        self.create_journal_tab()

        # Activities tab
        self.create_activities_tab()

        # Poetry tab
        self.create_poetry_tab()

        # Favorites tab
        self.create_favorites_tab()

    def create_weather_tab(self):
        """Create enhanced current weather tab with Bootstrap styling."""
        weather_frame = BootstrapFrame(self.notebook)
        self.notebook.add(weather_frame, text="🌤️ Current Weather")

        # Main weather card
        self.main_weather_card = WeatherCard(weather_frame, gui_ref=self)
        self.main_weather_card.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )

        # Enhanced side panel with controls and scrollbar
        side_panel = GlassmorphicFrame(weather_frame, elevated=True, gradient=True)
        side_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)

        # Create scrollable content area for the side panel
        canvas = tk.Canvas(
            side_panel,
            bg=GlassmorphicStyle.GLASS_BG_LIGHT,
            highlightthickness=0,
            width=300,  # Set fixed width for the side panel
        )
        scrollable_frame = tk.Frame(canvas, bg=GlassmorphicStyle.GLASS_BG_LIGHT)
        scrollbar = tk.Scrollbar(side_panel, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas_window = canvas.create_window(
            (0, 0), window=scrollable_frame, anchor="nw"
        )

        def configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update the width of the frame to match the canvas
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())

        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=canvas.winfo_width()),
        )

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

        # Header for side panel
        panel_header = tk.Frame(scrollable_frame, bg=GlassmorphicStyle.GLASS_BG_LIGHT)
        panel_header.pack(fill=tk.X, pady=(20, 15))

        header_icon = tk.Label(
            panel_header,
            text="🏙️",
            font=(GlassmorphicStyle.FONT_FAMILY, 24),
            fg=GlassmorphicStyle.ACCENT,
            bg=GlassmorphicStyle.GLASS_BG_LIGHT,
        )
        header_icon.pack()

        header_text = tk.Label(
            panel_header,
            text="City Search",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_LARGE,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=GlassmorphicStyle.GLASS_BG_LIGHT,
        )
        header_text.pack(pady=(5, 0))

        # City input section with enhanced styling
        input_section = GlassmorphicFrame(
            scrollable_frame, bg_color=GlassmorphicStyle.GLASS_BG_LIGHT
        )
        input_section.pack(fill=tk.X, padx=15, pady=(0, 15))

        input_label = tk.Label(
            input_section,
            text="Enter City:",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_MEDIUM,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_ACCENT,
            bg=input_section.bg_color,
        )
        input_label.pack(pady=(15, 5))

        self.city_entry = BootstrapEntry(input_section, style="primary")
        self.city_entry.pack(pady=(0, 15), padx=15, fill=tk.X, ipady=10)

        # Placeholder text functionality for Bootstrap entry
        self.city_entry.insert(0, "e.g., New York, London...")
        
        def on_entry_click(event):
            if self.city_entry.get() == "e.g., New York, London...":
                self.city_entry.delete(0, tk.END)

        def on_entry_leave(event):
            if not self.city_entry.get():
                self.city_entry.insert(0, "e.g., New York, London...")

        self.city_entry.bind("<FocusIn>", on_entry_click)
        self.city_entry.bind("<FocusOut>", on_entry_leave)

        # Action buttons with Bootstrap styling
        button_section = BootstrapFrame(scrollable_frame)
        button_section.pack(fill=tk.X, padx=15)

        # Get weather button
        self.get_weather_btn = BootstrapButton(
            button_section,
            text="Get Weather",
            icon="🌤️",
            style="primary",
            command=self.get_weather_for_city,
        )
        self.get_weather_btn.pack(fill=tk.X, pady=(0, 10))

        # Add to favorites button
        self.add_favorite_btn = BootstrapButton(
            button_section,
            text="Add to Favorites",
            icon="⭐",
            style="warning",
            command=self.add_to_favorites,
        )
        self.add_favorite_btn.pack(fill=tk.X, pady=(0, 10))

        # Quick access section
        quick_access = BootstrapFrame(scrollable_frame)
        quick_access.pack(fill=tk.X, padx=15, pady=(15, 0))

        quick_label = ttk_bs.Label(
            quick_access,
            text="Quick Actions",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_SMALL,
                "bold",
            ),
        )
        quick_label.pack(pady=(0, 10))

        # Current location button
        location_btn = BootstrapButton(
            quick_access,
            text="Current Location",
            icon="📍",
            style="success",
            command=self.get_current_location_weather,
        )
        location_btn.pack(fill=tk.X, pady=(0, 5))

        # Random city button
        random_btn = BootstrapButton(
            quick_access,
            text="Random City",
            icon="🎲",
            style="info",
            command=self.get_random_city_weather,
        )
        random_btn.pack(fill=tk.X)

        # Bind Enter key to city entry
        self.city_entry.bind("<Return>", lambda e: self.get_weather_for_city())

    def create_forecast_tab(self):
        """Create enhanced forecast tab with better layout."""
        forecast_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(forecast_frame, text="📅 Forecast")

        # Header with title and info
        header_frame = GlassmorphicFrame(forecast_frame, elevated=True, gradient=True)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Header content
        header_content = tk.Frame(header_frame, bg=header_frame.bg_color)
        header_content.pack(fill=tk.X, padx=20, pady=15)

        # Title with icon
        title_label = tk.Label(
            header_content,
            text="📅 7-Day Weather Forecast",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_LARGE,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=header_frame.bg_color,
        )
        title_label.pack(side=tk.LEFT)

        # Info label
        info_label = tk.Label(
            header_content,
            text="Detailed weather predictions for the upcoming week",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=header_frame.bg_color,
        )
        info_label.pack(side=tk.RIGHT)

        # Main forecast container
        forecast_container = GlassmorphicFrame(forecast_frame, elevated=True)
        forecast_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        # Scrollable forecast area with better organization
        self.forecast_scroll = ModernScrollableFrame(forecast_container)
        self.forecast_scroll.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

    def create_comparison_tab(self):
        """Create city comparison tab."""
        comparison_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(comparison_frame, text="🌍 Compare Cities")

        # Controls
        controls_frame = GlassmorphicFrame(comparison_frame, elevated=True)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # City inputs
        input_frame = tk.Frame(controls_frame, bg=controls_frame.bg_color)
        input_frame.pack(pady=20)

        tk.Label(
            input_frame,
            text="City 1:",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=controls_frame.bg_color,
        ).grid(row=0, column=0, padx=(20, 10), pady=5, sticky="e")

        self.city1_entry = BootstrapEntry(input_frame, width=20)
        self.city1_entry.grid(row=0, column=1, padx=10, pady=8, ipady=6)

        tk.Label(
            input_frame,
            text="City 2:",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=controls_frame.bg_color,
        ).grid(row=0, column=2, padx=(30, 10), pady=5, sticky="e")

        self.city2_entry = BootstrapEntry(input_frame, width=20)
        self.city2_entry.grid(row=0, column=3, padx=10, pady=8, ipady=6)

        self.compare_btn = ModernButton(
            input_frame, text="🌍 Compare", command=self.compare_cities
        )
        self.compare_btn.grid(row=0, column=4, padx=(20, 20), pady=5)

        # Comparison results
        self.comparison_results = GlassmorphicFrame(comparison_frame, elevated=True)
        self.comparison_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

    def create_journal_tab(self):
        """Create weather journal tab."""
        journal_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(journal_frame, text="📔 Journal")

        # Controls
        controls_frame = GlassmorphicFrame(journal_frame, elevated=True)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.new_entry_btn = ModernButton(
            controls_frame, text="📝 New Entry", command=self.create_journal_entry
        )
        self.new_entry_btn.pack(side=tk.LEFT, padx=20, pady=15)

        self.view_entries_btn = ModernButton(
            controls_frame,
            text="📖 View Entries",
            style="secondary",
            command=self.view_journal_entries,
        )
        self.view_entries_btn.pack(side=tk.LEFT, padx=10, pady=15)

        # Journal content
        self.journal_content = ModernScrollableFrame(journal_frame)
        self.journal_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

    def create_activities_tab(self):
        """Create activity suggestions tab."""
        activities_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(activities_frame, text="🎯 Activities")

        # Controls
        controls_frame = GlassmorphicFrame(activities_frame, elevated=True)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.get_activities_btn = ModernButton(
            controls_frame,
            text="🎯 Get Suggestions",
            command=self.get_activity_suggestions,
        )
        self.get_activities_btn.pack(side=tk.LEFT, padx=20, pady=15)

        # Activity filter buttons
        self.indoor_filter_btn = ModernButton(
            controls_frame,
            text="🏠 Indoor Only",
            style="secondary",
            command=lambda: self.filter_activities("indoor"),
        )
        self.indoor_filter_btn.pack(side=tk.LEFT, padx=10, pady=15)

        self.outdoor_filter_btn = ModernButton(
            controls_frame,
            text="🌞 Outdoor Only",
            style="secondary",
            command=lambda: self.filter_activities("outdoor"),
        )
        self.outdoor_filter_btn.pack(side=tk.LEFT, padx=10, pady=15)

        # Activities content
        self.activities_content = ModernScrollableFrame(activities_frame)
        self.activities_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

    def create_poetry_tab(self):
        """Create weather poetry tab."""
        poetry_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(poetry_frame, text="🎨 Poetry")

        # Controls
        controls_frame = GlassmorphicFrame(poetry_frame, elevated=True)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        # First row - Main generate buttons
        main_buttons_frame = tk.Frame(controls_frame, bg=controls_frame.bg_color)
        main_buttons_frame.pack(pady=(15, 5))

        self.generate_poetry_btn = ModernButton(
            main_buttons_frame,
            text="🎨 Generate Random Poetry",
            command=self.generate_poetry,
        )
        self.generate_poetry_btn.pack(side=tk.LEFT, padx=10)

        self.generate_collection_btn = ModernButton(
            main_buttons_frame,
            text="📚 Generate Collection",
            style="success",
            command=self.generate_poetry_collection,
        )
        self.generate_collection_btn.pack(side=tk.LEFT, padx=10)

        # Second row - Specific poetry type buttons
        specific_buttons_frame = tk.Frame(controls_frame, bg=controls_frame.bg_color)
        specific_buttons_frame.pack(pady=(5, 15))

        tk.Label(
            specific_buttons_frame,
            text="Generate Specific Type:",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=controls_frame.bg_color,
        ).pack(pady=(0, 5))

        buttons_row = tk.Frame(specific_buttons_frame, bg=controls_frame.bg_color)
        buttons_row.pack()

        self.haiku_btn = ModernButton(
            buttons_row,
            text="🌸 Haiku",
            style="secondary",
            command=lambda: self.generate_specific_poetry("haiku"),
        )
        self.haiku_btn.pack(side=tk.LEFT, padx=5)

        self.phrase_btn = ModernButton(
            buttons_row,
            text="💭 Phrase",
            style="secondary",
            command=lambda: self.generate_specific_poetry("phrase"),
        )
        self.phrase_btn.pack(side=tk.LEFT, padx=5)

        self.limerick_btn = ModernButton(
            buttons_row,
            text="🎵 Limerick",
            style="secondary",
            command=lambda: self.generate_specific_poetry("limerick"),
        )
        self.limerick_btn.pack(side=tk.LEFT, padx=5)

        # Poetry content
        self.poetry_content = GlassmorphicFrame(poetry_frame)
        self.poetry_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

    def create_favorites_tab(self):
        """Create favorites management tab."""
        favorites_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(favorites_frame, text="⭐ Favorites")

        # Controls
        controls_frame = GlassmorphicFrame(favorites_frame, elevated=True)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        self.refresh_favorites_btn = ModernButton(
            controls_frame, text="🔄 Refresh", command=self.refresh_favorites
        )
        self.refresh_favorites_btn.pack(side=tk.LEFT, padx=20, pady=15)

        self.view_all_weather_btn = ModernButton(
            controls_frame,
            text="🌍 View All Weather",
            style="secondary",
            command=self.view_all_favorites_weather,
        )
        self.view_all_weather_btn.pack(side=tk.LEFT, padx=10, pady=15)

        # Favorites content
        self.favorites_content = ModernScrollableFrame(favorites_frame)
        self.favorites_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

    def create_status_bar(self):
        """Create status bar."""
        self.status_frame = GlassmorphicFrame(self.root, elevated=True)
        self.status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.status_label = tk.Label(
            self.status_frame,
            text="Ready",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.status_frame.bg_color,
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=8)

        # Weather update time
        self.update_time_label = tk.Label(
            self.status_frame,
            text="",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.status_frame.bg_color,
        )
        self.update_time_label.pack(side=tk.RIGHT, padx=15, pady=8)

    # Interface implementation methods
    def display_weather(self, weather_data: CurrentWeather) -> None:
        """Display current weather data."""
        self.current_weather = weather_data
        self.main_weather_card.update_weather(weather_data)
        self.update_status(f"Weather updated for {weather_data.location.display_name}")

        # Update dashboard with new weather data
        if hasattr(self, 'dashboard'):
            self.dashboard.update_weather_data(weather_data)

        # Update timestamp
        if weather_data.timestamp:
            time_str = weather_data.timestamp.strftime("%H:%M")
            self.update_time_label.configure(text=f"Updated: {time_str}")

    def display_forecast(self, forecast_data: WeatherForecast) -> None:
        """Display forecast data with enhanced grid layout."""
        # Store forecast data for temperature unit changes
        self.current_forecast_data = forecast_data

        # Update dashboard with new forecast data
        if hasattr(self, 'dashboard'):
            self.dashboard.update_forecast_data(forecast_data)

        # Clear existing forecast
        for widget in self.forecast_scroll.scrollable_frame.winfo_children():
            widget.destroy()

        # Create main container for grid layout
        main_container = tk.Frame(
            self.forecast_scroll.scrollable_frame, bg=GlassmorphicStyle.BACKGROUND
        )
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create forecast cards in a responsive grid
        num_days = len(forecast_data.forecast_days)

        # For better layout, use 3 columns for desktop view to fill window better
        max_cols = 3

        for i, day in enumerate(forecast_data.forecast_days):
            row = i // max_cols
            col = i % max_cols

            day_card = self.create_forecast_card(main_container, day, i)
            day_card.grid(
                row=row, column=col, padx=12, pady=10, sticky="nsew", ipadx=3, ipady=3
            )

        # Configure grid weights for responsive behavior
        for col in range(max_cols):
            main_container.grid_columnconfigure(col, weight=1)
        for row in range((num_days + max_cols - 1) // max_cols):
            main_container.grid_rowconfigure(row, weight=1)

    def create_forecast_card(self, parent, day_data, index):
        """Create an enhanced forecast day card with better visual design."""
        card = GlassmorphicFrame(parent, elevated=True, gradient=True)
        card.configure(
            width=350, height=200
        )  # Slightly smaller width for 3-column layout

        # Main card container
        card_content = tk.Frame(card, bg=card.bg_color)
        card_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        # Top section - Date and weather icon
        top_section = tk.Frame(card_content, bg=card.bg_color)
        top_section.pack(fill=tk.X, pady=(0, 10))

        # Date section (left side)
        date_section = tk.Frame(top_section, bg=card.bg_color)
        date_section.pack(side=tk.LEFT, fill=tk.Y)

        # Day name
        day_name = day_data.date.strftime("%A")
        day_label = tk.Label(
            date_section,
            text=day_name,
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_LARGE,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=card.bg_color,
        )
        day_label.pack(anchor=tk.W)

        # Date
        date_str = day_data.date.strftime("%B %d")
        date_label = tk.Label(
            date_section,
            text=date_str,
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            fg=GlassmorphicStyle.TEXT_ACCENT,
            bg=card.bg_color,
        )
        date_label.pack(anchor=tk.W)

        # Weather icon (right side)
        icon = WeatherIcons.get_icon(
            day_data.description, day_data.temperature_high.value
        )
        icon_label = tk.Label(
            top_section,
            text=icon,
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                42,
            ),  # Slightly smaller for 3-column layout
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=card.bg_color,
        )
        icon_label.pack(side=tk.RIGHT)

        # Middle section - Temperature range
        temp_section = GlassmorphicFrame(
            card_content, bg_color=GlassmorphicStyle.GLASS_BG_LIGHT
        )
        temp_section.pack(fill=tk.X, pady=(0, 10))

        temp_content = tk.Frame(temp_section, bg=temp_section.bg_color)
        temp_content.pack(padx=15, pady=10)

        # Convert temperatures to current unit
        high_temp_celsius = day_data.temperature_high.to_celsius()
        low_temp_celsius = day_data.temperature_low.to_celsius()

        high_temp_value, temp_unit = self.convert_temperature(high_temp_celsius)
        low_temp_value, _ = self.convert_temperature(low_temp_celsius)

        # High temperature
        high_temp_frame = tk.Frame(temp_content, bg=temp_section.bg_color)
        high_temp_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            high_temp_frame,
            text="HIGH",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_TINY,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_TERTIARY,
            bg=temp_section.bg_color,
        ).pack()

        high_temp_color = GlassmorphicStyle.get_temperature_color(high_temp_value)
        tk.Label(
            high_temp_frame,
            text=f"{high_temp_value:.0f}°{temp_unit[-1]}",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_LARGE,
                "bold",
            ),
            fg=high_temp_color,
            bg=temp_section.bg_color,
        ).pack()

        # Separator
        tk.Label(
            temp_content,
            text="|",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_LARGE),
            fg=GlassmorphicStyle.TEXT_TERTIARY,
            bg=temp_section.bg_color,
        ).pack(side=tk.LEFT, padx=20)

        # Low temperature
        low_temp_frame = tk.Frame(temp_content, bg=temp_section.bg_color)
        low_temp_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(
            low_temp_frame,
            text="LOW",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_TINY,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_TERTIARY,
            bg=temp_section.bg_color,
        ).pack()

        low_temp_color = GlassmorphicStyle.get_temperature_color(low_temp_value)
        tk.Label(
            low_temp_frame,
            text=f"{low_temp_value:.0f}°{temp_unit[-1]}",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_LARGE,
                "bold",
            ),
            fg=low_temp_color,
            bg=temp_section.bg_color,
        ).pack()

        # Bottom section - Weather condition
        condition_frame = tk.Frame(card_content, bg=card.bg_color)
        condition_frame.pack(fill=tk.X)

        condition_label = tk.Label(
            condition_frame,
            text=day_data.description.title(),
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_MEDIUM,
                "italic",
            ),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=card.bg_color,
            justify=tk.CENTER,
        )
        condition_label.pack()

        # Add subtle animation for the icon
        AnimationHelper.fade_in(icon_label)

        return card

    def get_user_input(self, prompt: str) -> str:
        """Get input from user via dialog."""
        return simpledialog.askstring("Input", prompt) or ""

    def show_error(self, message: str) -> None:
        """Show error message."""
        messagebox.showerror("Error", message)
        self.update_status(f"Error: {message}", is_error=True)

    def show_message(self, message: str) -> None:
        """Show information message."""
        messagebox.showinfo("Information", message)
        self.update_status(message)

    def update_status(self, message: str, is_error: bool = False):
        """Update status bar."""
        color = (
            GlassmorphicStyle.ERROR if is_error else GlassmorphicStyle.TEXT_SECONDARY
        )
        self.status_label.configure(text=message, fg=color)

        # Auto-clear status after 5 seconds
        self.root.after(
            5000,
            lambda: self.status_label.configure(
                text="Ready", fg=GlassmorphicStyle.TEXT_SECONDARY
            ),
        )

    def cleanup_stray_widgets(self):
        """Clean up any stray widgets that might be showing in the UI."""
        # Iterate through all children of the root window
        for widget in self.root.winfo_children():
            # If it's a warning-colored widget with "Auto-Refresh" text, remove it
            if isinstance(widget, (tk.Label, tk.Button, tk.Frame)):
                if hasattr(widget, "cget"):
                    try:
                        bg_color = widget.cget("bg")
                        if bg_color in ("#f59e0b", "#fbbf24"):  # Warning colors
                            text = (
                                widget.cget("text") if hasattr(widget, "cget") else ""
                            )
                            if "Auto-Refresh" in text:
                                widget.destroy()
                    except (tk.TclError, AttributeError):
                        pass

                # Recursively check children
                if hasattr(widget, "winfo_children"):
                    for child in widget.winfo_children():
                        if hasattr(child, "cget"):
                            try:
                                bg_color = child.cget("bg")
                                if bg_color in ("#f59e0b", "#fbbf24"):  # Warning colors
                                    text = (
                                        child.cget("text")
                                        if hasattr(child, "cget")
                                        else ""
                                    )
                                    if "Auto-Refresh" in text:
                                        child.destroy()
                            except (tk.TclError, AttributeError):
                                pass

    # GUI-specific methods
    def get_weather_for_city(self):
        """Get weather for entered city."""
        city = self.city_entry.get().strip()
        if not city:
            self.show_error("Please enter a city name")
            return

        if "get_weather" in self.callbacks:
            self.callbacks["get_weather"](city)

    def refresh_current_weather(self):
        """Refresh current weather."""
        if self.current_weather and "get_weather" in self.callbacks:
            self.callbacks["get_weather"](self.current_weather.location.name)

    def show_city_search(self):
        """Show city search dialog."""
        city = simpledialog.askstring("Search", "Enter city name to search:")
        if city and "search_locations" in self.callbacks:
            self.callbacks["search_locations"](city)

    def add_to_favorites(self):
        """Add current city to favorites."""
        if self.current_weather and "add_favorite" in self.callbacks:
            self.callbacks["add_favorite"](self.current_weather.location.name)

    def compare_cities(self):
        """Compare two cities."""
        city1 = self.city1_entry.get().strip()
        city2 = self.city2_entry.get().strip()

        if not city1 or not city2:
            self.show_error("Please enter both city names")
            return

        if "compare_cities" in self.callbacks:
            self.callbacks["compare_cities"](city1, city2)

    def create_journal_entry(self):
        """Create new journal entry."""
        if "create_journal" in self.callbacks:
            self.callbacks["create_journal"]()

    def view_journal_entries(self):
        """View journal entries."""
        if "view_journal" in self.callbacks:
            self.callbacks["view_journal"]()

    def get_activity_suggestions(self):
        """Get activity suggestions."""
        if "get_activities" in self.callbacks:
            self.callbacks["get_activities"]()

    def filter_activities(self, activity_type):
        """Filter activities by type."""
        if "filter_activities" in self.callbacks:
            self.callbacks["filter_activities"](activity_type)

    def generate_poetry(self):
        """Generate weather poetry."""
        if "generate_poetry" in self.callbacks:
            self.callbacks["generate_poetry"]()

    def generate_specific_poetry(self, poetry_type):
        """Generate specific type of poetry."""
        if "generate_specific_poetry" in self.callbacks:
            self.callbacks["generate_specific_poetry"](poetry_type)

    def generate_poetry_collection(self):
        """Generate a collection of different poetry types."""
        if "generate_poetry_collection" in self.callbacks:
            self.callbacks["generate_poetry_collection"]()

    def refresh_favorites(self):
        """Refresh favorites list."""
        if "refresh_favorites" in self.callbacks:
            self.callbacks["refresh_favorites"]()

    def view_all_favorites_weather(self):
        """View weather for all favorites."""
        if "view_favorites_weather" in self.callbacks:
            self.callbacks["view_favorites_weather"]()

    def set_callback(self, event_name: str, callback: Callable):
        """Set callback for GUI events."""
        self.callbacks[event_name] = callback

    def run(self):
        """Start the GUI event loop."""
        self.root.mainloop()

    def quit(self):
        """Quit the application."""
        self.root.quit()
        self.root.destroy()

    # Display methods for capstone features
    def display_weather_comparison(self, comparison: WeatherComparison) -> None:
        """Display weather comparison."""
        # Clear existing results
        for widget in self.comparison_results.winfo_children():
            widget.destroy()

        city1 = comparison.city1_weather
        city2 = comparison.city2_weather

        # Title
        title_label = tk.Label(
            self.comparison_results,
            text="Weather Comparison Results",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_LARGE,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=self.comparison_results.bg_color,
        )
        title_label.pack(pady=(20, 10))

        # Create comparison cards
        comparison_frame = tk.Frame(
            self.comparison_results, bg=self.comparison_results.bg_color
        )
        comparison_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        # City 1 card
        card1 = WeatherCard(comparison_frame, gui_ref=self)
        card1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        card1.update_weather(city1)

        # VS label
        vs_label = tk.Label(
            comparison_frame,
            text="VS",
            font=(GlassmorphicStyle.FONT_FAMILY, 20, "bold"),
            fg=GlassmorphicStyle.ACCENT,
            bg=self.comparison_results.bg_color,
        )
        vs_label.pack(side=tk.LEFT, padx=20)

        # City 2 card
        card2 = WeatherCard(comparison_frame, gui_ref=self)
        card2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        card2.update_weather(city2)

        # Comparison summary
        summary_frame = tk.Frame(
            self.comparison_results, bg=self.comparison_results.bg_color
        )
        summary_frame.pack(fill=tk.X, padx=20, pady=20)

        better_city = comparison.better_weather_city
        summary_text = f"🏆 Better overall weather: {better_city}"

        summary_label = tk.Label(
            summary_frame,
            text=summary_text,
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_MEDIUM,
                "bold",
            ),
            fg=GlassmorphicStyle.SUCCESS,
            bg=self.comparison_results.bg_color,
        )
        summary_label.pack()

    def display_activity_suggestions(self, suggestions: ActivitySuggestion) -> None:
        """Display activity suggestions."""
        # Clear existing content
        for widget in self.activities_content.scrollable_frame.winfo_children():
            widget.destroy()

        if not suggestions.suggested_activities:
            no_activities_label = tk.Label(
                self.activities_content.scrollable_frame,
                text="No suitable activities found for current weather conditions.",
                font=(
                    GlassmorphicStyle.FONT_FAMILY,
                    GlassmorphicStyle.FONT_SIZE_MEDIUM,
                ),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg=GlassmorphicStyle.BACKGROUND,
            )
            no_activities_label.pack(pady=50)
            return

        # Top recommendation
        if suggestions.top_suggestion:
            top_activity, top_score = suggestions.suggested_activities[0]

            top_frame = GlassmorphicFrame(self.activities_content.scrollable_frame)
            top_frame.pack(fill=tk.X, padx=10, pady=10)

            tk.Label(
                top_frame,
                text="🏆 TOP RECOMMENDATION",
                font=(
                    GlassmorphicStyle.FONT_FAMILY,
                    GlassmorphicStyle.FONT_SIZE_MEDIUM,
                    "bold",
                ),
                fg=GlassmorphicStyle.SUCCESS,
                bg=top_frame.bg_color,
            ).pack(pady=(15, 5))

            tk.Label(
                top_frame,
                text=top_activity.name,
                font=(
                    GlassmorphicStyle.FONT_FAMILY,
                    GlassmorphicStyle.FONT_SIZE_LARGE,
                    "bold",
                ),
                fg=GlassmorphicStyle.TEXT_PRIMARY,
                bg=top_frame.bg_color,
            ).pack()

            tk.Label(
                top_frame,
                text=top_activity.description,
                font=(
                    GlassmorphicStyle.FONT_FAMILY,
                    GlassmorphicStyle.FONT_SIZE_MEDIUM,
                ),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg=top_frame.bg_color,
            ).pack(pady=(5, 10))

            tk.Label(
                top_frame,
                text=f"Suitability Score: {top_score:.1f}/10",
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
                fg=GlassmorphicStyle.ACCENT,
                bg=top_frame.bg_color,
            ).pack(pady=(0, 15))

        # All suggestions
        all_frame = GlassmorphicFrame(self.activities_content.scrollable_frame)
        all_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        tk.Label(
            all_frame,
            text="💡 All Suggestions",
            font=(
                GlassmorphicStyle.FONT_FAMILY,
                GlassmorphicStyle.FONT_SIZE_MEDIUM,
                "bold",
            ),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=all_frame.bg_color,
        ).pack(pady=(15, 10))

        for i, (activity, score) in enumerate(suggestions.suggested_activities[1:], 2):
            activity_frame = tk.Frame(all_frame, bg=all_frame.bg_color)
            activity_frame.pack(fill=tk.X, padx=20, pady=2)

            icon = "🏠" if activity.indoor else "🌞"

            tk.Label(
                activity_frame,
                text=f"{i}. {icon} {activity.name}",
                font=(
                    GlassmorphicStyle.FONT_FAMILY,
                    GlassmorphicStyle.FONT_SIZE_MEDIUM,
                ),
                fg=GlassmorphicStyle.TEXT_PRIMARY,
                bg=all_frame.bg_color,
            ).pack(side=tk.LEFT)

            tk.Label(
                activity_frame,
                text=f"Score: {score:.1f}",
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
                fg=GlassmorphicStyle.ACCENT,
                bg=all_frame.bg_color,
            ).pack(side=tk.RIGHT)

    def display_weather_poem(self, poem) -> None:
        """Display weather poem in the poetry tab with enhanced visual styling."""
        # Clear existing poetry content
        for widget in self.poetry_content.winfo_children():
            widget.destroy()

        # Create a gradient background canvas for the poem
        poem_container = GlassmorphicFrame(
            self.poetry_content,
            bg_color="#1d1d2b",
            border_color="#3a3a4a",
            elevated=True,
            gradient=True,
            blur_intensity=20,
        )
        poem_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        # Inner decorative frame with more padding and visual appeal
        poem_frame = tk.Frame(poem_container, bg="#1d1d2b", padx=20, pady=20)
        poem_frame.pack(fill=tk.BOTH, expand=True)

        # Create decorative elements
        # Top decorative element
        top_decor = tk.Frame(poem_frame, height=3, bg=GlassmorphicStyle.ACCENT_LIGHT)
        top_decor.pack(fill=tk.X, pady=(0, 20))

        # Poem type and title with enhanced styling
        if hasattr(poem, "poem_type"):
            # Enhanced icons with more visual appeal
            type_icons = {"haiku": "🌸", "phrase": "�", "limerick": "🎵"}
            icon = type_icons.get(getattr(poem, "poem_type", ""), "✨")

            # Use .title if it exists, else fallback to .poem_type or class name

            if hasattr(poem, "title"):
                title_text = f"{icon} {poem.title} {icon}"
            elif hasattr(poem, "poem_type"):
                title_text = f"{icon} {poem.poem_type.title()} {icon}"
            else:
                title_text = f"{icon} Weather Poetry {icon}"
        else:
            title_text = (
                poem.title if hasattr(poem, "title") else "✨ Weather Poetry ✨"
            )

        # Modern font for title with larger size
        title_label = tk.Label(
            poem_frame,
            text=title_text,
            font=("Georgia", 22, "bold"),  # More elegant font with increased size
            fg="#80a0ff",  # Softer blue for better aesthetics

            bg="#1d1d2b",
            justify=tk.CENTER,
        )
        title_label.pack(pady=(0, 20), fill=tk.X)

        # Poem text
        poem_text = poem.text if hasattr(poem, "text") else str(poem)

        # Create a decorative frame for the poem text
        poem_text_frame = tk.Frame(
            poem_frame,
            bg="#252535",
            bd=2,
            relief="solid",
            highlightbackground="#3d3d4d",
            highlightcolor="#4a9eff",
            highlightthickness=1,
        )
        poem_text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        # Inner padding frame
        padding_frame = tk.Frame(poem_text_frame, bg="#252535", padx=20, pady=20)
        padding_frame.pack(fill=tk.BOTH, expand=True)

        # Adjust height based on poem type for better display
        poem_height = 10  # Increased default height for better readability
        if hasattr(poem, "poem_type"):
            if poem.poem_type == "haiku":
                poem_height = 12  # Increased for better spacing
            elif poem.poem_type == "limerick":
                poem_height = 14  # Increased for better spacing

        # Text widget with enhanced styling for the poem content
        text_widget = tk.Text(
            padding_frame,
            font=("Palatino Linotype", 20),  # More elegant, larger font
            fg="#ffffff",  # Bright white for contrast
            bg="#252535",  # Slightly lighter than background for contrast
            relief="flat",
            borderwidth=0,
            wrap=tk.WORD,
            height=poem_height,
            padx=10,
            pady=10,
            state=tk.DISABLED,
            cursor="arrow",
        )

        # Configure text widget appearance with subtle glow effect
        text_widget.configure(
            highlightthickness=0,
            selectbackground="#6a8eff",  # Softer selection color
            selectforeground="#ffffff",
        )

        # Insert poem text with proper formatting
        text_widget.configure(state=tk.NORMAL)

        # Center-align the text
        text_widget.tag_configure("center", justify="center")

        # Use formatted_text for haikus (line breaks instead of slashes)
        if (
            hasattr(poem, "poem_type")
            and poem.poem_type == "haiku"
            and hasattr(poem, "formatted_text")
        ):
            text_widget.insert(tk.END, poem.formatted_text, "center")
        # Format limerick text with line breaks at / characters
        elif hasattr(poem, "poem_type") and poem.poem_type == "limerick":
            limerick_lines = poem_text.split(" / ")
            formatted_limerick = "\n".join(limerick_lines)
            text_widget.insert(tk.END, formatted_limerick, "center")
        else:
            text_widget.insert(tk.END, poem_text, "center")

        text_widget.configure(state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Bottom decorative element
        bottom_decor = tk.Frame(poem_frame, height=3, bg=GlassmorphicStyle.ACCENT_LIGHT)
        bottom_decor.pack(fill=tk.X, pady=(20, 10))

        # Poem metadata with enhanced styling
        if hasattr(poem, "created_at") and poem.created_at:
            timestamp = poem.created_at.strftime("%B %d, %Y at %I:%M %p")
            meta_frame = tk.Frame(poem_frame, bg="#1d1d2b")
            meta_frame.pack(fill=tk.X, pady=(5, 0))

            meta_label = tk.Label(
                meta_frame,
                text=f"✦ Created: {timestamp} ✦",
                font=("Georgia", 12, "italic"),  # Elegant font for metadata
                fg="#8090a0",  # Softer color for metadata
                bg="#1d1d2b",
                justify=tk.CENTER,
            )
            meta_label.pack(fill=tk.X)

        self.update_status("Poetry displayed with enhanced styling!")

    def display_weather_poem_collection(self, poems) -> None:
        """Display a collection of weather poems with enhanced visual styling."""
        # Clear existing poetry content
        for widget in self.poetry_content.winfo_children():
            widget.destroy()

        # Create scrollable area with enhanced styling
        collection_scroll = ModernScrollableFrame(
            self.poetry_content, bg_color="#151525"  # Darker background for contrast
        )
        collection_scroll.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Collection header with decorative elements
        header_frame = GlassmorphicFrame(
            collection_scroll.scrollable_frame,
            bg_color="#202035",
            border_color="#353555",
            elevated=True,
        )
        header_frame.pack(fill=tk.X, pady=(0, 25), padx=10)

        # Top decorative line
        tk.Frame(header_frame, height=3, bg="#5a80ff").pack(fill=tk.X)

        # Title with enhanced styling
        title_label = tk.Label(
            header_frame,
            text="✨ Poetry Collection ✨",
            font=("Georgia", 24, "bold"),  # More elegant, larger font
            fg="#90b0ff",  # Softer blue for better aesthetics
            bg="#202035",
            justify=tk.CENTER,
        )
        title_label.pack(pady=(15, 5))

        subtitle_label = tk.Label(
            header_frame,
            text=f"A curated collection of {len(poems)} weather-inspired poems",
            font=("Georgia", 14, "italic"),
            fg="#a0a0c0",  # Softer color for subtitle
            bg="#202035",
            justify=tk.CENTER,
        )
        subtitle_label.pack(pady=(0, 15))

        # Bottom decorative line
        tk.Frame(header_frame, height=3, bg="#5a80ff").pack(fill=tk.X)

        # Display each poem in a separate card with enhanced styling
        for i, poem in enumerate(poems):
            # Create poem card with gradient effect
            poem_card = GlassmorphicFrame(
                collection_scroll.scrollable_frame,
                bg_color="#1d1d2b",
                border_color="#3d3d5d",
                elevated=True,
                gradient=True,
                blur_intensity=15,
            )
            poem_card.pack(fill=tk.X, pady=15, padx=10)

            # Poem header with decorative element
            poem_header = tk.Frame(poem_card, bg="#1d1d2b")
            poem_header.pack(fill=tk.X, padx=15)

            # Top mini-decoration
            tk.Frame(poem_header, height=2, bg=GlassmorphicStyle.ACCENT_LIGHT).pack(
                fill=tk.X, pady=(15, 10)
            )

            # Poem type and title with enhanced icons
            if hasattr(poem, "poem_type"):
                type_icons = {"haiku": "🌸", "phrase": "💫", "limerick": "🎵"}
                icon = type_icons.get(poem.poem_type, "✨")

                # Use title if exists, else use poem_type
                if hasattr(poem, "title") and poem.title:
                    title_text = f"{icon} {poem.title} {icon}"
                else:
                    title_text = f"{icon} {poem.poem_type.title()} {icon}"
            else:
                title_text = (
                    poem.title
                    if hasattr(poem, "title")
                    else f"✨ Weather Poetry {i+1} ✨"
                )

            # Elegant title styling
            title_label = tk.Label(
                poem_header,
                text=title_text,
                font=("Georgia", 18, "bold"),  # More elegant, larger font
                fg="#80a0ff",  # Softer blue for better aesthetics
                bg="#1d1d2b",
                justify=tk.CENTER,
            )
            title_label.pack(pady=(0, 10))

            # Poem text
            poem_text = poem.text if hasattr(poem, "text") else str(poem)

            # Create decorated frame for the poem content
            poem_content_frame = tk.Frame(
                poem_card,
                bg="#252535",
                bd=1,
                relief="solid",
                highlightbackground="#3d3d4d",
                highlightcolor="#4a9eff",
                highlightthickness=1,
            )
            poem_content_frame.pack(fill=tk.X, padx=15, pady=10)

            # Inner padding frame
            inner_padding = tk.Frame(poem_content_frame, bg="#252535", padx=15, pady=15)
            inner_padding.pack(fill=tk.X)

            # Adjust height based on poem type for better display
            poem_height = 8  # Increased default height for better readability
            if hasattr(poem, "poem_type"):
                if poem.poem_type == "haiku":
                    poem_height = 10
                elif poem.poem_type == "limerick":
                    poem_height = 12

            # Text widget with enhanced styling
            text_widget = tk.Text(
                inner_padding,
                font=("Palatino Linotype", 16),  # More elegant, larger font
                fg="#ffffff",  # Bright white for better contrast
                bg="#252535",
                relief="flat",
                borderwidth=0,
                wrap=tk.WORD,
                height=poem_height,
                padx=10,
                pady=5,
                state=tk.DISABLED,
                cursor="arrow",
            )

            # Configure text widget appearance
            text_widget.configure(
                highlightthickness=0,
                selectbackground="#6a8eff",  # Softer selection color
                selectforeground="#ffffff",
            )

            # Center alignment
            text_widget.tag_configure("center", justify="center")

            # Insert poem text with proper formatting
            text_widget.configure(state=tk.NORMAL)

            # Use formatted_text for haikus and limericks
            if hasattr(poem, "poem_type") and hasattr(poem, "formatted_text"):
                if poem.poem_type in ["haiku", "limerick"]:
                    text_widget.insert(tk.END, poem.formatted_text, "center")
                else:
                    text_widget.insert(tk.END, poem_text, "center")
            # Format limerick text with line breaks at / characters
            elif hasattr(poem, "poem_type") and poem.poem_type == "limerick":
                limerick_lines = poem_text.split(" / ")
                formatted_limerick = "\n".join(limerick_lines)
                text_widget.insert(tk.END, formatted_limerick, "center")
            else:
                text_widget.insert(tk.END, poem_text, "center")

            text_widget.configure(state=tk.DISABLED)
            text_widget.pack(fill=tk.X)

            # Bottom decoration
            bottom_frame = tk.Frame(poem_card, bg="#1d1d2b")
            bottom_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
            tk.Frame(bottom_frame, height=2, bg=GlassmorphicStyle.ACCENT_LIGHT).pack(
                fill=tk.X, pady=(10, 0)
            )

        self.update_status(
            f"Poetry collection displayed with enhanced styling! ({len(poems)} poems)"
        )

    def toggle_temperature_unit(self):
        """Toggle between Celsius and Fahrenheit."""
        self.temperature_unit = "F" if self.temperature_unit == "C" else "C"
        self.update_temp_toggle_text()
        self.refresh_temperature_displays()

    def update_temp_toggle_text(self):
        """Update the temperature toggle button text."""
        if self.temperature_unit == "C":
            self.temp_toggle_btn.configure(text="°C/°F")
        else:
            self.temp_toggle_btn.configure(text="°F/°C")

    def refresh_temperature_displays(self):
        """Refresh all temperature displays with new unit."""
        # Refresh main weather card if current weather is displayed
        if self.current_weather:
            self.main_weather_card.update_weather(self.current_weather)

        # Refresh forecast if available
        self.refresh_forecast_temperatures()

        # Refresh comparison if available
        self.refresh_comparison_temperatures()

    def refresh_forecast_temperatures(self):
        """Refresh forecast temperature displays."""
        # Clear and recreate forecast cards if forecast data exists
        if hasattr(self, "current_forecast_data") and self.current_forecast_data:
            self.display_forecast(self.current_forecast_data)

    def refresh_comparison_temperatures(self):
        """Refresh comparison temperature displays."""
        # This will be called when comparison data is available
        # The comparison display will be updated with the correct temperature unit
        pass

    def convert_temperature(self, temp_celsius: float) -> tuple[float, str]:
        """Convert temperature to the current unit.

        Args:
            temp_celsius: Temperature in Celsius

        Returns:
            Tuple of (converted_temperature, unit_symbol)
        """
        if self.temperature_unit == "F":
            temp_fahrenheit = (temp_celsius * 9 / 5) + 32
            return temp_fahrenheit, "°F"
        else:
            return temp_celsius, "°C"

    def get_random_city_weather(self):
        """Get weather for a random city for demonstration purposes."""
        import random

        # List of interesting cities around the world
        cities = [
            "Tokyo",
            "London",
            "Paris",
            "New York",
            "Sydney",
            "Dubai",
            "Singapore",
            "Rome",
            "Barcelona",
            "Amsterdam",
            "Bangkok",
            "San Francisco",
            "Toronto",
            "Berlin",
            "Vienna",
            "Prague",
            "Stockholm",
            "Copenhagen",
            "Helsinki",
            "Reykjavik",
        ]

        random_city = random.choice(cities)

        # Clear the entry and set the random city
        self.city_entry.delete(0, tk.END)
        self.city_entry.insert(0, random_city)

        # Get the weather for the random city
        self.get_weather_for_city()

    def get_current_location_weather(self):
        """Get weather for current detected location."""
        try:
            # Show loading message
            self.status_label.configure(
                text="Detecting location...", fg=GlassmorphicStyle.ACCENT
            )
            self.root.update()

            # Call the location weather callback
            if "get_current_location_weather" in self.callbacks:
                self.callbacks["get_current_location_weather"]()
            else:
                self.show_error("Location detection service not available")

        except Exception as e:
            logging.error(f"Error in location detection: {e}")
            self.show_error(f"Location detection failed: {str(e)}")

    def toggle_auto_refresh(self):
        """Toggle auto-refresh functionality with Bootstrap styling."""
        self.auto_refresh = not self.auto_refresh
        if self.auto_refresh:
            self.start_auto_refresh()
            # Update Bootstrap button for active state
            self.auto_refresh_btn.configure(text="⏱️ ON")
            # Change to success style for active state
            self.auto_refresh_btn.configure(style="success")
            self.update_status("Auto-refresh enabled (5 minutes)")
        else:
            self.stop_auto_refresh()
            # Restore original Bootstrap styling
            self.auto_refresh_btn.configure(text="⏱️ Auto")
            # Change back to info style
            self.auto_refresh_btn.configure(style="info")
            self.update_status("Auto-refresh disabled")

    def start_auto_refresh(self):
        """Start the auto-refresh timer."""
        self.refresh_current_weather()  # Refresh immediately
        self.refresh_timer = self.root.after(
            self.refresh_interval, self.start_auto_refresh
        )

    def stop_auto_refresh(self):
        """Stop the auto-refresh timer."""
        if self.refresh_timer:
            self.root.after_cancel(self.refresh_timer)
            self.refresh_timer = None

    def on_close(self):
        """Clean up and close the application."""
        self.stop_auto_refresh()  # Stop auto-refresh timer
        self.root.destroy()

    def show_dashboard(self):
        """Show the weather visualization dashboard."""
        try:
            # Update dashboard with current weather data
            if self.current_weather:
                self.dashboard.update_weather_data(self.current_weather)
            
            # Update forecast data if available
            if self.current_forecast_data:
                self.dashboard.update_forecast_data(self.current_forecast_data)
            
            # Show the dashboard
            self.dashboard.show_dashboard()
            self.update_status("Dashboard opened - Use Ctrl+1-4 for charts, Ctrl+D to toggle")
        except Exception as e:
            self.logger.error(f"Error opening dashboard: {e}")
            self.show_error(f"Failed to open dashboard: {str(e)}")


class ResponsiveLayout:
    """Helper class for responsive layout management."""
    
    @staticmethod
    def create_card_grid(parent, cards_per_row=2, spacing=10):
        """Create a responsive grid layout for cards."""
        container = BootstrapFrame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=spacing, pady=spacing)
        return container
    
    @staticmethod
    def create_button_toolbar(parent, buttons_config, spacing=5):
        """Create a modern button toolbar with proper spacing."""
        toolbar = BootstrapFrame(parent)
        toolbar.pack(fill=tk.X, pady=spacing)
        
        for config in buttons_config:
            btn = BootstrapButton(
                toolbar,
                text=config.get("text", ""),
                icon=config.get("icon", ""),
                style=config.get("style", "primary"),
                command=config.get("command", None)
            )
            btn.pack(side=tk.LEFT, padx=spacing)
            
            # Add separator if specified
            if config.get("separator", False):
                ttk_bs.Separator(toolbar, orient='vertical').pack(
                    side=tk.LEFT, fill=tk.Y, padx=spacing
                )
        
        return toolbar
    
    @staticmethod
    def create_info_card(parent, title, content, icon="ℹ️"):
        """Create a modern information card with Bootstrap styling."""
        card = ttk_bs.LabelFrame(parent, text=f"{icon} {title}", padding=15)
        card.pack(fill=tk.X, pady=10)
        
        content_label = ttk_bs.Label(
            card,
            text=content,
            font=("Segoe UI", 11),
            wraplength=400
        )
        content_label.pack(anchor=tk.W)
        
        return card


class ModernLayoutMixin:
    """Mixin to add modern layout capabilities to GUI classes."""
    
    def create_modern_sidebar(self, parent, width=300):
        """Create a modern sidebar with Bootstrap styling."""
        sidebar = BootstrapFrame(parent)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # Add scrolling capability
        canvas = tk.Canvas(sidebar, width=width, highlightthickness=0)
        scrollbar = ttk_bs.Scrollbar(sidebar, orient="vertical", command=canvas.yview)
        scrollable_frame = BootstrapFrame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        return scrollable_frame
    
    def create_modern_card(self, parent, title, icon="📄"):
        """Create a modern card layout with Bootstrap styling."""
        card = ttk_bs.LabelFrame(parent, text=f"{icon} {title}", padding=20)
        card.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        return card
