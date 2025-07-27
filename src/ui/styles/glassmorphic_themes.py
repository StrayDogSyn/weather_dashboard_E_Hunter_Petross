#!/usr/bin/env python3
"""
Glassmorphic Theme Implementation for Weather Dashboard

This module provides glassmorphic styling with blurred/frosted backgrounds
using black, hunter green, and silver accents for a modern, translucent UI.

Author: Cortana Builder Assistant
Compatible with: Bot Framework, Azure Cognitive Services
"""

import colorsys
import tkinter as tk
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, Tuple


class GlassTheme(Enum):
    """Available glassmorphic themes."""

    MIDNIGHT_FOREST = "midnight_forest"
    SILVER_MIST = "silver_mist"
    FOREST_SHADOW = "forest_shadow"
    ADAPTIVE = "adaptive"  # Changes based on weather conditions


class GlassOpacity(Enum):
    """Standard opacity levels for glass elements."""

    SUBTLE = 0.08
    LIGHT = 0.12
    MEDIUM = 0.18
    STRONG = 0.25
    MODAL = 0.35


@dataclass
class ColorPalette:
    """Color palette for glassmorphic themes."""

    # Base colors
    background: str
    surface: str
    overlay: str

    # Glass backgrounds
    glass_primary: str
    glass_secondary: str
    glass_accent: str

    # Text colors
    text_primary: str
    text_secondary: str
    text_accent: str
    text_muted: str

    # Accent colors
    hunter_green: str
    hunter_green_light: str
    hunter_green_dark: str
    silver: str
    silver_light: str
    silver_dark: str

    # Interactive states
    hover: str
    active: str
    focus: str
    disabled: str

    # Borders
    border_subtle: str
    border_accent: str
    border_focus: str


class GlassmorphicStyleManager:
    """Manages glassmorphic styling for the weather dashboard."""

    def __init__(self, theme: GlassTheme = GlassTheme.MIDNIGHT_FOREST):
        self.current_theme = theme
        self._palettes = self._initialize_palettes()
        self._weather_adaptations = self._initialize_weather_adaptations()

    def _initialize_palettes(self) -> Dict[GlassTheme, ColorPalette]:
        """Initialize color palettes for all themes."""
        return {
            GlassTheme.MIDNIGHT_FOREST: ColorPalette(
                # Base colors
                background="#0a0a0a",
                surface="#1a1a1a",
                overlay="#0f0f0f",
                # Glass backgrounds (approximated for Tkinter)
                glass_primary="#1a2820",  # rgba(20, 40, 30, 0.15) approximation
                glass_secondary="#2d5541",  # rgba(45, 85, 65, 0.12) approximation
                glass_accent="#1f1f1f",  # rgba(192, 192, 192, 0.08) approximation
                # Text colors
                text_primary="#E5E5E5",
                text_secondary="#A0A0A0",
                text_accent="#4A7C59",
                text_muted="#707070",
                # Accent colors
                hunter_green="#355E3B",
                hunter_green_light="#4A7C59",
                hunter_green_dark="#2C4A32",
                silver="#C0C0C0",
                silver_light="#E5E5E5",
                silver_dark="#A0A0A0",
                # Interactive states
                hover="#2C4A32",
                active="#4A7C59",
                focus="#5A9B6A",
                disabled="#404040",
                # Borders
                border_subtle="#303030",
                border_accent="#4A7C59",
                border_focus="#6AB77A",
            ),
            GlassTheme.SILVER_MIST: ColorPalette(
                # Base colors
                background="#0f0f0f",
                surface="#1f1f1f",
                overlay="#151515",
                # Glass backgrounds
                glass_primary="#2a2a2a",  # Silver-tinted glass
                glass_secondary="#1a2820",  # Hunter green panels
                glass_accent="#353535",  # Brighter silver
                # Text colors
                text_primary="#F0F0F0",
                text_secondary="#B0B0B0",
                text_accent="#355E3B",
                text_muted="#808080",
                # Accent colors (same as Midnight Forest)
                hunter_green="#355E3B",
                hunter_green_light="#4A7C59",
                hunter_green_dark="#2C4A32",
                silver="#C0C0C0",
                silver_light="#E5E5E5",
                silver_dark="#A0A0A0",
                # Interactive states
                hover="#C0C0C0",
                active="#E5E5E5",
                focus="#F0F0F0",
                disabled="#505050",
                # Borders
                border_subtle="#404040",
                border_accent="#C0C0C0",
                border_focus="#E5E5E5",
            ),
            GlassTheme.FOREST_SHADOW: ColorPalette(
                # Base colors
                background="#000000",
                surface="#141414",
                overlay="#0a0a0a",
                # Glass backgrounds
                glass_primary="#1a2820",  # Hunter green glass
                glass_secondary="#1a1a1a",  # Black glass cards
                glass_accent="#2a2a2a",  # Silver modals
                # Text colors (enhanced contrast)
                text_primary="#F0F0F0",
                text_secondary="#B0B0B0",
                text_accent="#5A9B6A",
                text_muted="#707070",
                # Accent colors
                hunter_green="#355E3B",
                hunter_green_light="#5A9B6A",
                hunter_green_dark="#2C4A32",
                silver="#C0C0C0",
                silver_light="#E5E5E5",
                silver_dark="#A0A0A0",
                # Interactive states
                hover="#2C4A32",
                active="#5A9B6A",
                focus="#6AB77A",
                disabled="#303030",
                # Borders
                border_subtle="#252525",
                border_accent="#5A9B6A",
                border_focus="#7AC98F",
            ),
        }

    def _initialize_weather_adaptations(self) -> Dict[str, Dict[str, str]]:
        """Initialize weather-based color adaptations."""
        return {
            "hot": {
                "glass_tint": "#4D1F1F",  # Red tint
                "accent_color": "#FF6B6B",
                "text_accent": "#FFB3B3",
            },
            "warm": {
                "glass_tint": "#4D3D1F",  # Orange tint
                "accent_color": "#FFD700",
                "text_accent": "#FFE55C",
            },
            "mild": {
                "glass_tint": "#1F4D2A",  # Green tint
                "accent_color": "#4A7C59",
                "text_accent": "#6AB77A",
            },
            "cool": {
                "glass_tint": "#1F3D4D",  # Blue tint
                "accent_color": "#87CEEB",
                "text_accent": "#B0E0E6",
            },
            "cold": {
                "glass_tint": "#2A2A2A",  # Silver tint
                "accent_color": "#C0C0C0",
                "text_accent": "#E5E5E5",
            },
        }

    def get_current_palette(self) -> ColorPalette:
        """Get the current color palette."""
        return self._palettes[self.current_theme]

    def switch_theme(self, theme: GlassTheme) -> None:
        """Switch to a different theme."""
        self.current_theme = theme

    def get_weather_adapted_colors(self, temperature_celsius: float) -> Dict[str, str]:
        """Get weather-adapted colors based on temperature."""
        temp_range = self._get_temperature_range(temperature_celsius)
        return self._weather_adaptations.get(
            temp_range, self._weather_adaptations["mild"]
        )

    def _get_temperature_range(self, temp_c: float) -> str:
        """Determine temperature range category."""
        if temp_c >= 30:
            return "hot"
        elif temp_c >= 24:
            return "warm"
        elif temp_c >= 18:
            return "mild"
        elif temp_c >= 10:
            return "cool"
        else:
            return "cold"

    def blend_colors(self, color1: str, color2: str, ratio: float = 0.5) -> str:
        """Blend two hex colors with given ratio."""
        # Convert hex to RGB
        rgb1 = tuple(int(color1[i : i + 2], 16) for i in (1, 3, 5))
        rgb2 = tuple(int(color2[i : i + 2], 16) for i in (1, 3, 5))

        # Blend colors
        blended = tuple(int(rgb1[i] * (1 - ratio) + rgb2[i] * ratio) for i in range(3))

        # Convert back to hex
        return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"

    def adjust_opacity_simulation(
        self, base_color: str, background_color: str, opacity: float
    ) -> str:
        """Simulate opacity by blending with background color."""
        return self.blend_colors(background_color, base_color, opacity)


class GlassWidget:
    """Base class for glassmorphic widgets."""

    def __init__(self, style_manager: GlassmorphicStyleManager):
        self.style_manager = style_manager
        self.palette = style_manager.get_current_palette()

    def get_glass_frame_config(self, glass_type: str = "primary") -> Dict[str, Any]:
        """Get configuration for glass frame."""
        glass_colors = {
            "primary": self.palette.glass_primary,
            "secondary": self.palette.glass_secondary,
            "accent": self.palette.glass_accent,
        }

        return {
            "bg": glass_colors.get(glass_type, self.palette.glass_primary),
            "highlightbackground": self.palette.border_subtle,
            "highlightthickness": 1,
            "relief": "flat",
            "bd": 0,
        }

    def get_glass_button_config(self, style: str = "default") -> Dict[str, Any]:
        """Get configuration for glass button."""
        base_config = {
            "bg": self.palette.glass_secondary,
            "fg": self.palette.text_primary,
            "activebackground": self.palette.hover,
            "activeforeground": self.palette.text_primary,
            "relief": "flat",
            "bd": 1,
            "highlightbackground": self.palette.border_accent,
            "font": ("Segoe UI", 10),
            "cursor": "hand2",
            "padx": 15,
            "pady": 8,
        }

        if style == "accent":
            base_config.update(
                {
                    "bg": self.palette.hunter_green,
                    "activebackground": self.palette.hunter_green_light,
                    "highlightbackground": self.palette.border_focus,
                }
            )
        elif style == "silver":
            base_config.update(
                {
                    "bg": self.palette.silver_dark,
                    "activebackground": self.palette.silver,
                    "fg": self.palette.background,
                }
            )

        return base_config

    def get_glass_label_config(self, text_type: str = "primary") -> Dict[str, Any]:
        """Get configuration for glass label."""
        text_colors = {
            "primary": self.palette.text_primary,
            "secondary": self.palette.text_secondary,
            "accent": self.palette.text_accent,
            "muted": self.palette.text_muted,
        }

        return {
            "bg": self.palette.glass_primary,
            "fg": text_colors.get(text_type, self.palette.text_primary),
            "font": ("Segoe UI", 10),
            "relief": "flat",
            "bd": 0,
        }


class WeatherGlassCard(tk.Frame, GlassWidget):
    """Glassmorphic weather card component."""

    def __init__(
        self,
        parent,
        style_manager: GlassmorphicStyleManager,
        weather_data=None,
        **kwargs,
    ):
        GlassWidget.__init__(self, style_manager)

        # Apply weather-based adaptations if weather data is provided
        if weather_data and hasattr(weather_data, "temperature"):
            adapted_colors = self.style_manager.get_weather_adapted_colors(
                weather_data.temperature
            )
            glass_bg = self.style_manager.blend_colors(
                self.palette.glass_primary, adapted_colors["glass_tint"], 0.3
            )
        else:
            glass_bg = self.palette.glass_primary

        frame_config = self.get_glass_frame_config()
        frame_config["bg"] = glass_bg
        frame_config.update(kwargs)

        tk.Frame.__init__(self, parent, **frame_config)

        # Add subtle inner border effect
        self._create_inner_border()

    def _create_inner_border(self):
        """Create inner border effect for depth."""
        inner_frame = tk.Frame(
            self,
            bg=self.palette.glass_primary,
            highlightbackground=self.palette.border_subtle,
            highlightthickness=1,
            relief="flat",
        )
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        return inner_frame


class GlassButton(tk.Button, GlassWidget):
    """Enhanced glassmorphic button with hover effects."""

    def __init__(
        self,
        parent,
        style_manager: GlassmorphicStyleManager,
        style: str = "default",
        **kwargs,
    ):
        GlassWidget.__init__(self, style_manager)

        button_config = self.get_glass_button_config(style)
        button_config.update(kwargs)

        tk.Button.__init__(self, parent, **button_config)

        # Store original colors for hover effects
        self.original_bg = button_config["bg"]
        self.hover_bg = button_config["activebackground"]

        # Bind hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        """Handle mouse enter event."""
        self.configure(bg=self.hover_bg)

    def _on_leave(self, event):
        """Handle mouse leave event."""
        self.configure(bg=self.original_bg)


class GlassPanel(tk.Frame, GlassWidget):
    """Large glassmorphic panel for dashboard sections."""

    def __init__(
        self,
        parent,
        style_manager: GlassmorphicStyleManager,
        panel_type: str = "default",
        elevated: bool = False,
        **kwargs,
    ):
        GlassWidget.__init__(self, style_manager)

        # Determine glass type based on panel type
        glass_type = "primary"
        if panel_type == "forecast":
            glass_type = "secondary"
        elif panel_type == "metrics":
            glass_type = "accent"

        frame_config = self.get_glass_frame_config(glass_type)

        # Add elevation effect
        if elevated:
            frame_config["highlightthickness"] = 2
            frame_config["highlightbackground"] = self.palette.border_accent

        frame_config.update(kwargs)
        tk.Frame.__init__(self, parent, **frame_config)

        # Add gradient effect simulation
        self.container = self  # Default container is self
        if elevated:
            self._create_elevation_effect()

    def get_container(self):
        """Get the container where child widgets should be placed."""
        return getattr(self, "container", self)

    def _create_elevation_effect(self):
        """Create elevation effect with gradient simulation using grid layout."""
        # Configure grid weights for proper expansion
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top highlight
        top_highlight = tk.Frame(self, bg=self.palette.silver_light, height=1)
        top_highlight.grid(row=0, column=0, sticky="ew")

        # Main content area (where child widgets will be placed)
        self.content_frame = tk.Frame(self, bg=self.cget("bg"))
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Bottom shadow
        bottom_shadow = tk.Frame(self, bg=self.palette.background, height=1)
        bottom_shadow.grid(row=2, column=0, sticky="ew")

        # Override the default container for child widgets
        self.container = self.content_frame


class GlassModal(tk.Toplevel, GlassWidget):
    """Glassmorphic modal dialog."""

    def __init__(
        self,
        parent,
        style_manager: GlassmorphicStyleManager,
        title: str = "Modal",
        **kwargs,
    ):
        GlassWidget.__init__(self, style_manager)

        tk.Toplevel.__init__(self, parent, **kwargs)

        # Configure modal window
        self.title(title)
        self.configure(bg=self.palette.overlay)
        self.transient(parent)
        self.grab_set()

        # Create glass content frame
        self.content_frame = GlassPanel(self, style_manager, elevated=True)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Center the modal
        self._center_modal(parent)

    def _center_modal(self, parent):
        """Center the modal on the parent window."""
        self.update_idletasks()

        # Get parent window position and size
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        # Get modal size
        modal_width = self.winfo_reqwidth()
        modal_height = self.winfo_reqheight()

        # Calculate center position
        x = parent_x + (parent_width - modal_width) // 2
        y = parent_y + (parent_height - modal_height) // 2

        self.geometry(f"+{x}+{y}")


# Example usage and integration
class GlassmorphicThemeDemo:
    """Demonstration of glassmorphic themes."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Glassmorphic Weather Dashboard")
        self.root.geometry("800x600")

        # Initialize style manager
        self.style_manager = GlassmorphicStyleManager(GlassTheme.MIDNIGHT_FOREST)
        palette = self.style_manager.get_current_palette()

        # Configure root window
        self.root.configure(bg=palette.background)

        self._create_demo_ui()

    def _create_demo_ui(self):
        """Create demonstration UI."""
        palette = self.style_manager.get_current_palette()

        # Main container
        main_frame = GlassPanel(self.root, self.style_manager, elevated=True)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Title
        title_label = tk.Label(
            main_frame,
            text="🌤️ Glassmorphic Weather Dashboard",
            font=("Segoe UI", 16, "bold"),
            **GlassWidget(self.style_manager).get_glass_label_config("primary"),
        )
        title_label.pack(pady=20)

        # Weather cards container
        cards_frame = tk.Frame(main_frame, bg=palette.glass_primary)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Sample weather cards
        for i, (city, temp) in enumerate(
            [("Seattle", 18), ("Phoenix", 35), ("Denver", 5)]
        ):
            card = WeatherGlassCard(
                cards_frame,
                self.style_manager,
                weather_data=type("Weather", (), {"temperature": temp})(),
            )
            card.pack(fill=tk.X, pady=5)

            # Card content
            city_label = tk.Label(
                card,
                text=f"📍 {city}",
                font=("Segoe UI", 12, "bold"),
                **GlassWidget(self.style_manager).get_glass_label_config("accent"),
            )
            city_label.pack(anchor=tk.W, padx=15, pady=(10, 5))

            temp_label = tk.Label(
                card,
                text=f"🌡️ {temp}°C",
                font=("Segoe UI", 14),
                **GlassWidget(self.style_manager).get_glass_label_config("primary"),
            )
            temp_label.pack(anchor=tk.W, padx=15, pady=(0, 10))

        # Control buttons
        button_frame = tk.Frame(main_frame, bg=palette.glass_primary)
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        # Theme switching buttons
        for theme in GlassTheme:
            if theme != GlassTheme.ADAPTIVE:
                btn = GlassButton(
                    button_frame,
                    self.style_manager,
                    text=theme.value.replace("_", " ").title(),
                    command=lambda t=theme: self._switch_theme(t),
                    style=(
                        "accent"
                        if theme == self.style_manager.current_theme
                        else "default"
                    ),
                )
                btn.pack(side=tk.LEFT, padx=5)

    def _switch_theme(self, theme: GlassTheme):
        """Switch to a different theme and refresh UI."""
        self.style_manager.switch_theme(theme)
        # In a real application, you would refresh all UI components here
        print(f"Switched to theme: {theme.value}")

    def run(self):
        """Run the demonstration."""
        self.root.mainloop()


if __name__ == "__main__":
    # Run demonstration
    demo = GlassmorphicThemeDemo()
    demo.run()
