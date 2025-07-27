#!/usr/bin/env python3
"""
Glassmorphic Theme Integration for Existing Weather Dashboard

This module provides integration utilities to apply glassmorphic themes
to existing Tkinter components in the weather dashboard.

Author: Cortana Builder Assistant
Compatible with: Bot Framework, Azure Cognitive Services
"""

import tkinter as tk
from tkinter import ttk
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from .glassmorphic_themes import GlassButton
from .glassmorphic_themes import GlassmorphicStyleManager
from .glassmorphic_themes import GlassPanel
from .glassmorphic_themes import GlassTheme
from .glassmorphic_themes import GlassWidget
from .glassmorphic_themes import WeatherGlassCard


class DashboardThemeIntegrator:
    """Integrates glassmorphic themes with existing dashboard components."""

    def __init__(self, style_manager: GlassmorphicStyleManager):
        self.style_manager = style_manager
        self.palette = style_manager.get_current_palette()
        self._applied_widgets = []

    def apply_theme_to_window(self, window: tk.Tk) -> None:
        """Apply glassmorphic theme to main window."""
        window.configure(bg=self.palette.background)

        # Configure window properties for glass effect
        try:
            # Windows-specific transparency (if supported)
            window.wm_attributes("-alpha", 0.98)
        except tk.TclError:
            pass  # Transparency not supported on this platform

    def convert_frame_to_glass(
        self, frame: tk.Frame, glass_type: str = "primary", elevated: bool = False
    ) -> GlassPanel:
        """Convert existing frame to glassmorphic panel."""
        parent = frame.master
        pack_info = frame.pack_info()
        grid_info = frame.grid_info()
        place_info = frame.place_info()

        # Create new glass panel
        glass_panel = GlassPanel(
            parent, self.style_manager, panel_type=glass_type, elevated=elevated
        )

        # Copy geometry management
        if pack_info:
            glass_panel.pack(**pack_info)
        elif grid_info:
            glass_panel.grid(**grid_info)
        elif place_info:
            glass_panel.place(**place_info)

        # Move children from old frame to new glass panel
        children = list(frame.children.values())
        for child in children:
            child.master = glass_panel

        # Destroy old frame
        frame.destroy()

        self._applied_widgets.append(glass_panel)
        return glass_panel

    def convert_button_to_glass(
        self, button: tk.Button, style: str = "default"
    ) -> GlassButton:
        """Convert existing button to glassmorphic button."""
        parent = button.master
        text = button.cget("text")
        command = button.cget("command")

        # Get geometry info
        pack_info = button.pack_info()
        grid_info = button.grid_info()
        place_info = button.place_info()

        # Create new glass button
        glass_button = GlassButton(
            parent, self.style_manager, text=text, command=command, style=style
        )

        # Apply geometry
        if pack_info:
            glass_button.pack(**pack_info)
        elif grid_info:
            glass_button.grid(**grid_info)
        elif place_info:
            glass_button.place(**place_info)

        # Destroy old button
        button.destroy()

        self._applied_widgets.append(glass_button)
        return glass_button

    def apply_glass_styling_to_label(
        self, label: tk.Label, text_type: str = "primary"
    ) -> None:
        """Apply glassmorphic styling to existing label."""
        glass_config = GlassWidget(self.style_manager).get_glass_label_config(text_type)
        label.configure(**glass_config)
        self._applied_widgets.append(label)

    def create_weather_card_from_data(
        self, parent: tk.Widget, weather_data: Dict[str, Any]
    ) -> WeatherGlassCard:
        """Create a glassmorphic weather card from weather data."""
        # Create mock weather object for temperature adaptation
        weather_obj = type(
            "Weather", (), {"temperature": weather_data.get("temperature", 20)}
        )()

        card = WeatherGlassCard(parent, self.style_manager, weather_data=weather_obj)

        # Populate card with weather information
        self._populate_weather_card(card, weather_data)

        self._applied_widgets.append(card)
        return card

    def _populate_weather_card(
        self, card: WeatherGlassCard, weather_data: Dict[str, Any]
    ) -> None:
        """Populate weather card with data."""
        glass_widget = GlassWidget(self.style_manager)

        # City name
        if "city" in weather_data:
            city_label = tk.Label(
                card,
                text=f"📍 {weather_data['city']}",
                font=("Segoe UI", 14, "bold"),
                **glass_widget.get_glass_label_config("accent"),
            )
            city_label.pack(anchor=tk.W, padx=15, pady=(15, 5))

        # Temperature
        if "temperature" in weather_data:
            temp_label = tk.Label(
                card,
                text=f"🌡️ {weather_data['temperature']}°C",
                font=("Segoe UI", 16),
                **glass_widget.get_glass_label_config("primary"),
            )
            temp_label.pack(anchor=tk.W, padx=15, pady=2)

        # Weather condition
        if "condition" in weather_data:
            condition_label = tk.Label(
                card,
                text=f"☁️ {weather_data['condition']}",
                font=("Segoe UI", 12),
                **glass_widget.get_glass_label_config("secondary"),
            )
            condition_label.pack(anchor=tk.W, padx=15, pady=2)

        # Humidity
        if "humidity" in weather_data:
            humidity_label = tk.Label(
                card,
                text=f"💧 Humidity: {weather_data['humidity']}%",
                font=("Segoe UI", 10),
                **glass_widget.get_glass_label_config("muted"),
            )
            humidity_label.pack(anchor=tk.W, padx=15, pady=2)

        # Wind speed
        if "wind_speed" in weather_data:
            wind_label = tk.Label(
                card,
                text=f"💨 Wind: {weather_data['wind_speed']} km/h",
                font=("Segoe UI", 10),
                **glass_widget.get_glass_label_config("muted"),
            )
            wind_label.pack(anchor=tk.W, padx=15, pady=(2, 15))

    def create_forecast_panel(
        self, parent: tk.Widget, forecast_data: List[Dict[str, Any]]
    ) -> GlassPanel:
        """Create a glassmorphic forecast panel."""
        panel = GlassPanel(
            parent, self.style_manager, panel_type="forecast", elevated=True
        )

        # Title
        title_label = tk.Label(
            panel,
            text="📅 5-Day Forecast",
            font=("Segoe UI", 14, "bold"),
            **GlassWidget(self.style_manager).get_glass_label_config("accent"),
        )
        title_label.pack(pady=(15, 10))

        # Forecast items
        for day_data in forecast_data[:5]:  # Limit to 5 days
            day_frame = tk.Frame(
                panel,
                **GlassWidget(self.style_manager).get_glass_frame_config("secondary"),
            )
            day_frame.pack(fill=tk.X, padx=15, pady=2)

            # Day name
            day_label = tk.Label(
                day_frame,
                text=day_data.get("day", "Unknown"),
                font=("Segoe UI", 10, "bold"),
                width=10,
                **GlassWidget(self.style_manager).get_glass_label_config("primary"),
            )
            day_label.pack(side=tk.LEFT, padx=5, pady=5)

            # Temperature range
            temp_label = tk.Label(
                day_frame,
                text=f"{day_data.get('high', '--')}°/{day_data.get('low', '--')}°",
                font=("Segoe UI", 10),
                width=8,
                **GlassWidget(self.style_manager).get_glass_label_config("secondary"),
            )
            temp_label.pack(side=tk.LEFT, padx=5, pady=5)

            # Condition
            condition_label = tk.Label(
                day_frame,
                text=day_data.get("condition", "Unknown"),
                font=("Segoe UI", 10),
                **GlassWidget(self.style_manager).get_glass_label_config("muted"),
            )
            condition_label.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self._applied_widgets.append(panel)
        return panel

    def create_metrics_panel(
        self, parent: tk.Widget, metrics_data: Dict[str, Any]
    ) -> GlassPanel:
        """Create a glassmorphic metrics panel."""
        panel = GlassPanel(
            parent, self.style_manager, panel_type="metrics", elevated=True
        )

        # Title
        title_label = tk.Label(
            panel,
            text="📊 Weather Metrics",
            font=("Segoe UI", 14, "bold"),
            **GlassWidget(self.style_manager).get_glass_label_config("accent"),
        )
        title_label.pack(pady=(15, 10))

        # Metrics grid
        metrics_frame = tk.Frame(
            panel, **GlassWidget(self.style_manager).get_glass_frame_config("secondary")
        )
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # Configure grid
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)

        row = 0
        for metric_name, metric_value in metrics_data.items():
            # Metric name
            name_label = tk.Label(
                metrics_frame,
                text=f"{metric_name}:",
                font=("Segoe UI", 10),
                anchor=tk.W,
                **GlassWidget(self.style_manager).get_glass_label_config("secondary"),
            )
            name_label.grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)

            # Metric value
            value_label = tk.Label(
                metrics_frame,
                text=str(metric_value),
                font=("Segoe UI", 10, "bold"),
                anchor=tk.E,
                **GlassWidget(self.style_manager).get_glass_label_config("primary"),
            )
            value_label.grid(row=row, column=1, sticky=tk.E, padx=10, pady=5)

            row += 1

        self._applied_widgets.append(panel)
        return panel

    def create_theme_selector(self, parent: tk.Widget) -> GlassPanel:
        """Create a theme selector panel."""
        panel = GlassPanel(parent, self.style_manager, elevated=True)

        # Get the container for child widgets
        panel_container = panel.get_container()
        
        # Title
        title_label = tk.Label(
            panel_container,
            text="🎨 Theme Selection",
            font=("Segoe UI", 12, "bold"),
            **GlassWidget(self.style_manager).get_glass_label_config("accent"),
        )
        title_label.pack(pady=(10, 5))

        # Theme buttons
        button_frame = tk.Frame(
            panel_container, **GlassWidget(self.style_manager).get_glass_frame_config("primary")
        )
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        for theme in GlassTheme:
            if theme != GlassTheme.ADAPTIVE:
                btn_style = (
                    "accent" if theme == self.style_manager.current_theme else "default"
                )
                btn = GlassButton(
                    button_frame,
                    self.style_manager,
                    text=theme.value.replace("_", " ").title(),
                    command=lambda t=theme: self._switch_theme(t),
                    style=btn_style,
                )
                btn.pack(side=tk.LEFT, padx=2, pady=5)

        self._applied_widgets.append(panel)
        return panel

    def _switch_theme(self, theme: GlassTheme) -> None:
        """Switch theme and refresh all applied widgets."""
        self.style_manager.switch_theme(theme)
        self.palette = self.style_manager.get_current_palette()

        # Refresh all applied widgets
        self.refresh_all_widgets()

    def refresh_all_widgets(self) -> None:
        """Refresh styling for all applied widgets."""
        for widget in self._applied_widgets:
            if hasattr(widget, "style_manager"):
                widget.style_manager = self.style_manager
                widget.palette = self.style_manager.get_current_palette()
                # Trigger widget refresh if method exists
                if hasattr(widget, "refresh_styling"):
                    widget.refresh_styling()

    def apply_adaptive_weather_theme(
        self, temperature: float, condition: str = ""
    ) -> None:
        """Apply adaptive theme based on current weather."""
        adapted_colors = self.style_manager.get_weather_adapted_colors(temperature)

        # Update palette with adapted colors
        palette = self.style_manager.get_current_palette()

        # Create temporary adapted palette
        adapted_palette = type(palette)(
            **{
                **palette.__dict__,
                **{
                    "glass_primary": self.style_manager.blend_colors(
                        palette.glass_primary, adapted_colors["glass_tint"], 0.3
                    ),
                    "text_accent": adapted_colors["text_accent"],
                    "hunter_green": adapted_colors["accent_color"],
                },
            }
        )

        # Apply to style manager temporarily
        _ = self.style_manager._palettes[self.style_manager.current_theme]
        self.style_manager._palettes[self.style_manager.current_theme] = adapted_palette

        # Refresh widgets
        self.refresh_all_widgets()

        # Restore original palette after a delay (in a real app, you'd manage this differently)
        # self.style_manager._palettes[self.style_manager.current_theme] = original_palette


class GlassmorphicDashboardExample:
    """Example implementation of glassmorphic dashboard."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Glassmorphic Weather Dashboard")
        self.root.geometry("1000x700")

        # Initialize theme system
        self.style_manager = GlassmorphicStyleManager(GlassTheme.MIDNIGHT_FOREST)
        self.integrator = DashboardThemeIntegrator(self.style_manager)

        # Apply theme to window
        self.integrator.apply_theme_to_window(self.root)

        # Sample data
        self.weather_data = {
            "city": "Seattle",
            "temperature": 18,
            "condition": "Partly Cloudy",
            "humidity": 65,
            "wind_speed": 12,
        }

        self.forecast_data = [
            {"day": "Today", "high": 22, "low": 15, "condition": "Sunny"},
            {"day": "Tomorrow", "high": 20, "low": 13, "condition": "Cloudy"},
            {"day": "Wednesday", "high": 18, "low": 11, "condition": "Rainy"},
            {"day": "Thursday", "high": 25, "low": 16, "condition": "Sunny"},
            {"day": "Friday", "high": 23, "low": 14, "condition": "Partly Cloudy"},
        ]

        self.metrics_data = {
            "UV Index": "6 (High)",
            "Visibility": "10 km",
            "Pressure": "1013 hPa",
            "Dew Point": "12°C",
        }

        self._create_dashboard()

    def _create_dashboard(self):
        """Create the main dashboard interface."""
        # Main container
        main_container = GlassPanel(self.root, self.style_manager, elevated=True)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get the container for child widgets
        container = main_container.get_container()

        # Header
        header_frame = tk.Frame(
            container,
            **GlassWidget(self.style_manager).get_glass_frame_config("primary"),
        )
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        title_label = tk.Label(
            header_frame,
            text="🌤️ Glassmorphic Weather Dashboard",
            font=("Segoe UI", 18, "bold"),
            **GlassWidget(self.style_manager).get_glass_label_config("accent"),
        )
        title_label.pack(pady=15)

        # Content area
        content_frame = tk.Frame(
            container,
            **GlassWidget(self.style_manager).get_glass_frame_config("primary"),
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left column
        left_column = tk.Frame(
            content_frame,
            **GlassWidget(self.style_manager).get_glass_frame_config("primary"),
        )
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Current weather card
        weather_card = self.integrator.create_weather_card_from_data(
            left_column, self.weather_data
        )
        weather_card.pack(fill=tk.X, pady=(0, 10))

        # Metrics panel
        metrics_panel = self.integrator.create_metrics_panel(
            left_column, self.metrics_data
        )
        metrics_panel.pack(fill=tk.BOTH, expand=True)

        # Right column
        right_column = tk.Frame(
            content_frame,
            **GlassWidget(self.style_manager).get_glass_frame_config("primary"),
        )
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Forecast panel
        forecast_panel = self.integrator.create_forecast_panel(
            right_column, self.forecast_data
        )
        forecast_panel.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Theme selector
        theme_panel = self.integrator.create_theme_selector(right_column)
        theme_panel.pack(fill=tk.X)

        # Footer with action buttons
        footer_frame = tk.Frame(
            container,
            **GlassWidget(self.style_manager).get_glass_frame_config("primary"),
        )
        footer_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        # Action buttons
        refresh_btn = GlassButton(
            footer_frame,
            self.style_manager,
            text="🔄 Refresh Weather",
            command=self._refresh_weather,
            style="accent",
        )
        refresh_btn.pack(side=tk.LEFT, padx=5, pady=10)

        settings_btn = GlassButton(
            footer_frame,
            self.style_manager,
            text="⚙️ Settings",
            command=self._open_settings,
            style="silver",
        )
        settings_btn.pack(side=tk.LEFT, padx=5, pady=10)

        adaptive_btn = GlassButton(
            footer_frame,
            self.style_manager,
            text="🎨 Adaptive Theme",
            command=self._apply_adaptive_theme,
            style="default",
        )
        adaptive_btn.pack(side=tk.RIGHT, padx=5, pady=10)

    def _refresh_weather(self):
        """Simulate weather refresh."""
        print("Refreshing weather data...")
        # In a real app, this would fetch new weather data

    def _open_settings(self):
        """Open settings modal."""
        from .glassmorphic_themes import GlassModal

        modal = GlassModal(self.root, self.style_manager, title="Settings")
        modal.geometry("400x300")

        # Add settings content
        settings_label = tk.Label(
            modal.content_frame,
            text="⚙️ Dashboard Settings",
            font=("Segoe UI", 14, "bold"),
            **GlassWidget(self.style_manager).get_glass_label_config("accent"),
        )
        settings_label.pack(pady=20)

        # Close button
        close_btn = GlassButton(
            modal.content_frame,
            self.style_manager,
            text="Close",
            command=modal.destroy,
            style="silver",
        )
        close_btn.pack(pady=10)

    def _apply_adaptive_theme(self):
        """Apply adaptive theme based on current weather."""
        self.integrator.apply_adaptive_weather_theme(
            self.weather_data["temperature"], self.weather_data["condition"]
        )
        print(f"Applied adaptive theme for {self.weather_data['temperature']}°C")

    def run(self):
        """Run the dashboard."""
        self.root.mainloop()


if __name__ == "__main__":
    # Run the glassmorphic dashboard example
    dashboard = GlassmorphicDashboardExample()
    dashboard.run()
