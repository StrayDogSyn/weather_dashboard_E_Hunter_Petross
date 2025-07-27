"""Weather card component for displaying current weather information.

This module provides a comprehensive weather display card with glassmorphic styling,
animations, and detailed weather information presentation.
"""

import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Any, Dict, Optional

from ...models.weather_models import WeatherData
from ..animations.effects import AnimationHelper
from ..styles.glassmorphic import GlassmorphicFrame, GlassmorphicStyle
from .responsive_layout import ResponsiveSpacing
from .weather_icons import WeatherIcons


class WeatherCard(GlassmorphicFrame):
    """Weather information display card with glassmorphic styling."""

    def __init__(self, parent, **kwargs):
        """Initialize weather card.

        Args:
            parent: Parent widget
            **kwargs: Additional frame configuration
        """
        super().__init__(parent, **kwargs)

        self.style = GlassmorphicStyle()
        self.icons = WeatherIcons()
        self.animation = AnimationHelper()
        # Use ResponsiveSpacing class attributes directly

        # Weather data storage
        self.current_weather: Optional[WeatherData] = None

        # UI components
        self.main_temp_label: Optional[tk.Label] = None
        self.condition_label: Optional[tk.Label] = None
        self.location_label: Optional[tk.Label] = None
        self.icon_label: Optional[tk.Label] = None
        self.details_frame: Optional[tk.Frame] = None
        self.last_updated_label: Optional[tk.Label] = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the weather card user interface."""
        # Configure grid weights
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container
        main_container = tk.Frame(self, bg=self.style.colors["surface"])
        main_container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        main_container.grid_columnconfigure(1, weight=1)

        # Weather icon section
        icon_frame = tk.Frame(main_container, bg=self.style.colors["surface"])
        icon_frame.grid(row=0, column=0, sticky="nw", padx=(0, 20))

        self.icon_label = tk.Label(
            icon_frame,
            text=self.icons.DEFAULT,
            font=self.style.fonts["icon_large"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        self.icon_label.pack()

        # Main weather info section
        info_frame = tk.Frame(main_container, bg=self.style.colors["surface"])
        info_frame.grid(row=0, column=1, sticky="nsew")
        info_frame.grid_columnconfigure(0, weight=1)

        # Location
        self.location_label = tk.Label(
            info_frame,
            text="Select a location",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
            anchor="w",
        )
        self.location_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # Main temperature
        self.main_temp_label = tk.Label(
            info_frame,
            text="--°",
            font=self.style.fonts["temperature"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["accent"],
            anchor="w",
        )
        self.main_temp_label.grid(row=1, column=0, sticky="ew")

        # Weather condition
        self.condition_label = tk.Label(
            info_frame,
            text="No data available",
            font=self.style.fonts["subheading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
            anchor="w",
        )
        self.condition_label.grid(row=2, column=0, sticky="ew", pady=(5, 10))

        # Weather details section
        self._create_details_section(main_container)

        # Last updated section
        self.last_updated_label = tk.Label(
            main_container,
            text="",
            font=self.style.fonts["caption"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_disabled"],
            anchor="e",
        )
        self.last_updated_label.grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0)
        )

    def _create_details_section(self, parent) -> None:
        """Create weather details section.

        Args:
            parent: Parent widget for details section
        """
        self.details_frame = GlassmorphicFrame(parent, padding=15)
        self.details_frame.grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(20, 0)
        )
        self.details_frame.grid_columnconfigure((0, 1), weight=1)

        # Details will be populated when weather data is updated
        self._create_detail_placeholders()

    def _create_detail_placeholders(self) -> None:
        """Create placeholder labels for weather details."""
        if not self.details_frame:
            return

        # Left column details
        left_frame = tk.Frame(self.details_frame, bg=self.style.colors["surface"])
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Right column details
        right_frame = tk.Frame(self.details_frame, bg=self.style.colors["surface"])
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        # Store detail labels for updates
        self.detail_labels = {}

        # Left column items
        left_items = [
            ("💧", "Humidity", "--"),
            ("🌪️", "Wind", "--"),
        ]

        # Right column items
        right_items = [
            ("🌡️", "Pressure", "--"),
            ("👁️", "Visibility", "--"),
        ]

        # Create left column details
        for i, (icon, label, value) in enumerate(left_items):
            self._create_detail_row(left_frame, i, icon, label, value, f"left_{i}")

        # Create right column details
        for i, (icon, label, value) in enumerate(right_items):
            self._create_detail_row(right_frame, i, icon, label, value, f"right_{i}")

    def _create_detail_row(
        self, parent, row: int, icon: str, label: str, value: str, key: str
    ) -> None:
        """Create a single detail row.

        Args:
            parent: Parent widget
            row: Grid row number
            icon: Icon for the detail
            label: Label text
            value: Value text
            key: Key for storing label reference
        """
        detail_frame = tk.Frame(parent, bg=self.style.colors["surface"])
        detail_frame.grid(row=row, column=0, sticky="ew", pady=5)
        detail_frame.grid_columnconfigure(1, weight=1)

        # Icon
        icon_label = tk.Label(
            detail_frame,
            text=icon,
            font=self.style.fonts["icon_small"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        icon_label.grid(row=0, column=0, padx=(0, ResponsiveSpacing.SMALL))

        # Label and value container
        text_frame = tk.Frame(detail_frame, bg=self.style.colors["surface"])
        text_frame.grid(row=0, column=1, sticky="ew")

        # Label
        label_widget = tk.Label(
            text_frame,
            text=label,
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
            anchor="w",
        )
        label_widget.pack(anchor="w")

        # Value
        value_widget = tk.Label(
            text_frame,
            text=value,
            font=self.style.fonts["body_bold"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
            anchor="w",
        )
        value_widget.pack(anchor="w")

        # Store reference for updates
        self.detail_labels[key] = {
            "label": label_widget,
            "value": value_widget,
            "icon": icon_label,
        }

    def update_weather(self, weather_data: WeatherData) -> None:
        """Update weather card with new weather data.

        Args:
            weather_data: Weather data to display
        """
        self.current_weather = weather_data

        # Update main information
        self._update_main_info(weather_data)

        # Update details
        self._update_details(weather_data)

        # Update last updated time
        self._update_timestamp()

        # Apply entrance animation
        self.animation.fade_in(self, duration=500)

    def _update_main_info(self, weather_data: WeatherData) -> None:
        """Update main weather information.

        Args:
            weather_data: Weather data to display
        """
        # Update location
        location_text = f"{weather_data.location.name}"
        if weather_data.location.country:
            location_text += f", {weather_data.location.country}"
        self.location_label.config(text=location_text)

        # Update temperature with color coding
        temp_value = (
            weather_data.temperature.value
            if hasattr(weather_data.temperature, "value")
            else weather_data.temperature
        )
        temp_text = f"{temp_value: .0f}°"
        temp_color = self.style.get_temperature_color(temp_value)
        self.main_temp_label.config(text=temp_text, fg=temp_color)

        # Update condition
        self.condition_label.config(text=weather_data.condition)

        # Update weather icon
        weather_icon = self.icons.get_icon(
            weather_data.condition, weather_data.temperature
        )
        self.icon_label.config(text=weather_icon)

        # Apply glow effect to temperature
        self.animation.text_glow(self.main_temp_label, temp_color)

    def _update_details(self, weather_data: WeatherData) -> None:
        """Update weather details section.

        Args:
            weather_data: Weather data to display
        """
        if not self.detail_labels:
            return

        # Update humidity
        if "left_0" in self.detail_labels:
            humidity_text = (
                f"{weather_data.humidity}%" if weather_data.humidity else "--"
            )
            self.detail_labels["left_0"]["value"].config(text=humidity_text)

        # Update wind
        if "left_1" in self.detail_labels:
            wind_text = "--"
            if weather_data.wind and weather_data.wind.speed:
                wind_text = f"{weather_data.wind.speed} mph"
                if weather_data.wind.direction:
                    wind_text += f" {weather_data.wind.direction_name}"
            self.detail_labels["left_1"]["value"].config(text=wind_text)

        # Update pressure
        if "right_0" in self.detail_labels:
            pressure_text = (
                f"{weather_data.pressure.value} hPa" if weather_data.pressure else "--"
            )
            self.detail_labels["right_0"]["value"].config(text=pressure_text)

        # Update visibility
        if "right_1" in self.detail_labels:
            visibility_text = (
                f"{weather_data.visibility} mi" if weather_data.visibility else "--"
            )
            self.detail_labels["right_1"]["value"].config(text=visibility_text)

    def _update_timestamp(self) -> None:
        """Update last updated timestamp."""
        current_time = datetime.now().strftime("%I:%M %p")
        self.last_updated_label.config(text=f"Last updated: {current_time}")

    def clear_weather(self) -> None:
        """Clear weather data and reset to default state."""
        self.current_weather = None

        # Reset main information
        self.location_label.config(text="Select a location")
        self.main_temp_label.config(text="--°", fg=self.style.colors["accent"])
        self.condition_label.config(text="No data available")
        self.icon_label.config(text=self.icons.DEFAULT)

        # Reset details
        for detail_key, detail_widgets in self.detail_labels.items():
            detail_widgets["value"].config(text="--")

        # Clear timestamp
        self.last_updated_label.config(text="")

    def set_loading_state(self, loading: bool) -> None:
        """Set weather card to loading state.

        Args:
            loading: Whether card is in loading state
        """
        if loading:
            self.location_label.config(text="Loading...")
            self.main_temp_label.config(text="--°")
            self.condition_label.config(text="Fetching weather data...")
            self.icon_label.config(text="⏳")

            # Apply pulse animation
            self.animation.pulse(self.icon_label)
        else:
            if not self.current_weather:
                self.clear_weather()

    def get_weather_summary(self) -> str:
        """Get a text summary of current weather.

        Returns:
            Weather summary string
        """
        if not self.current_weather:
            return "No weather data available"

        weather = self.current_weather
        temp_value = (
            weather.temperature.value
            if hasattr(weather.temperature, "value")
            else weather.temperature
        )
        summary_parts = [
            f"Current weather in {weather.location.name}: ",
            f"Temperature: {temp_value: .0f}°",
            f"Condition: {weather.condition}",
        ]

        if weather.humidity:
            summary_parts.append(f"Humidity: {weather.humidity}%")

        if weather.wind and weather.wind.speed:
            wind_info = f"Wind: {weather.wind.speed} mph"
            if weather.wind.direction:
                wind_info += f" {weather.wind.direction_name}"
            summary_parts.append(wind_info)

        return "\n".join(summary_parts)

    def export_weather_data(self) -> Optional[Dict[str, Any]]:
        """Export current weather data as dictionary.

        Returns:
            Weather data dictionary or None if no data
        """
        if not self.current_weather:
            return None

        temp_value = (
            self.current_weather.temperature.value
            if hasattr(self.current_weather.temperature, "value")
            else self.current_weather.temperature
        )
        return {
            "location": {
                "city": self.current_weather.location.name,
                "country": self.current_weather.location.country,
                "latitude": self.current_weather.location.latitude,
                "longitude": self.current_weather.location.longitude,
            },
            "current": {
                "temperature": temp_value,
                "condition": self.current_weather.condition,
                "humidity": self.current_weather.humidity,
                "wind_speed": (
                    self.current_weather.wind.speed
                    if self.current_weather.wind
                    else None
                ),
                "wind_direction": (
                    self.current_weather.wind.direction
                    if self.current_weather.wind
                    else None
                ),
                "pressure": (
                    self.current_weather.pressure.value
                    if self.current_weather.pressure
                    else None
                ),
                "visibility": self.current_weather.visibility,
            },
            "timestamp": datetime.now().isoformat(),
        }
