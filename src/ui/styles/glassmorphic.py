"""Glassmorphic design system for the Weather Dashboard.

This module provides a comprehensive glassmorphic design system with
enhanced visual features, color schemes, and styling utilities.
"""

import tkinter as tk
from typing import Optional


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
        """Get color based on temperature value.
        
        Args:
            temperature: Temperature value in the current unit
            
        Returns:
            Hex color string for the temperature
        """
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
        bg_color: Optional[str] = None,
        border_color: Optional[str] = None,
        elevated: bool = False,
        gradient: bool = False,
        blur_intensity: Optional[int] = None,
        **kwargs,
    ):
        """Initialize glassmorphic frame.
        
        Args:
            parent: Parent widget
            bg_color: Background color override
            border_color: Border color override
            elevated: Whether to show elevated appearance
            gradient: Whether to use gradient background
            blur_intensity: Blur effect intensity (0-10)
            **kwargs: Additional tkinter Frame arguments
        """
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