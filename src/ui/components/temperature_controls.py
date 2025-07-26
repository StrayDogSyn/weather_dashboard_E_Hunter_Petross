"""Temperature controls component for the Weather Dashboard.

This module provides temperature unit switching, display controls,
and temperature-related utilities with glassmorphic styling.
"""

import tkinter as tk
from enum import Enum
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional

from ..animations.effects import AnimationHelper
from ..styles.glassmorphic import GlassmorphicFrame, GlassmorphicStyle
from ..widgets.enhanced_button import ButtonFactory
from ..widgets.modern_button import IconButton, ModernButton
from .responsive_layout import ResponsiveLayoutManager, ResponsiveSpacing


class TemperatureUnit(Enum):
    """Temperature unit enumeration."""

    FAHRENHEIT = "F"
    CELSIUS = "C"
    KELVIN = "K"


class TemperatureControls(GlassmorphicFrame):
    """Temperature controls widget with unit switching and display options."""

    def __init__(
        self,
        parent,
        initial_unit: TemperatureUnit = TemperatureUnit.FAHRENHEIT,
        on_unit_change: Optional[Callable[[TemperatureUnit], None]] = None,
        show_feels_like: bool = True,
        show_heat_index: bool = True,
        **kwargs,
    ):
        """Initialize temperature controls.

        Args:
            parent: Parent widget
            initial_unit: Initial temperature unit
            on_unit_change: Callback for unit changes
            show_feels_like: Whether to show "feels like" temperature
            show_heat_index: Whether to show heat index
            **kwargs: Additional frame configuration
        """
        super().__init__(parent, **kwargs)

        self.style = GlassmorphicStyle()
        self.animation = AnimationHelper()

        # Initialize responsive layout components
        self.responsive_layout = ResponsiveLayoutManager()
        self.button_factory = ButtonFactory()
        self.spacing = ResponsiveSpacing()

        # State
        self.current_unit = initial_unit
        self.on_unit_change = on_unit_change
        self.show_feels_like = show_feels_like
        self.show_heat_index = show_heat_index

        # Temperature data
        self.current_temp: Optional[float] = None
        self.feels_like_temp: Optional[float] = None
        self.heat_index: Optional[float] = None
        self.wind_chill: Optional[float] = None

        # UI Components
        self.unit_buttons: Dict[TemperatureUnit, ModernButton] = {}
        self.temp_display: Optional[tk.Label] = None
        self.feels_like_display: Optional[tk.Label] = None
        self.heat_index_display: Optional[tk.Label] = None
        self.wind_chill_display: Optional[tk.Label] = None
        self.temp_range_display: Optional[tk.Label] = None

        # Additional controls
        self.precision_var = tk.IntVar(value=0)  # Decimal places
        self.show_symbol_var = tk.BooleanVar(value=True)

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the temperature controls interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Main container with responsive spacing
        main_frame = tk.Frame(self, bg=self.style.colors["surface"])
        main_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=self.spacing.container_padding,
            pady=self.spacing.element_spacing,
        )
        main_frame.grid_columnconfigure(1, weight=1)

        # Unit selector section
        self._create_unit_selector(main_frame)

        # Temperature display section
        self._create_temperature_display(main_frame)

        # Additional controls section
        self._create_additional_controls(main_frame)

    def _create_unit_selector(self, parent) -> None:
        """Create temperature unit selector.

        Args:
            parent: Parent widget
        """
        unit_frame = GlassmorphicFrame(parent)
        unit_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, self.spacing.element_spacing),
            pady=self.spacing.element_spacing,
        )

        # Unit selector label
        unit_label = tk.Label(
            unit_frame,
            text="Temperature Unit:",
            font=self.style.fonts["caption"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        )
        unit_label.grid(
            row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5)
        )

        # Unit buttons
        for i, unit in enumerate(TemperatureUnit):
            button = ModernButton(
                unit_frame,
                text=f"°{unit.value}",
                command=lambda u=unit: self._change_unit(u),
                style_variant="secondary" if unit != self.current_unit else "primary",
            )
            button.grid(
                row=1,
                column=i,
                padx=self.spacing.button_spacing,
                pady=(0, 10),
                sticky="ew",
            )
            self.unit_buttons[unit] = button

            # Configure column weight
            unit_frame.grid_columnconfigure(i, weight=1)

    def _create_temperature_display(self, parent) -> None:
        """Create temperature display section.

        Args:
            parent: Parent widget
        """
        display_frame = GlassmorphicFrame(parent)
        display_frame.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, self.spacing.element_spacing),
            pady=self.spacing.element_spacing,
        )
        display_frame.grid_columnconfigure(0, weight=1)

        # Main temperature display
        self.temp_display = tk.Label(
            display_frame,
            text="--°",
            font=self.style.fonts["temperature"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
            anchor="center",
        )
        self.temp_display.grid(row=0, column=0, pady=(10, 5))

        # Secondary temperature displays
        secondary_frame = tk.Frame(display_frame, bg=self.style.colors["surface"])
        secondary_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        secondary_frame.grid_columnconfigure((0, 1), weight=1)

        if self.show_feels_like:
            feels_like_frame = tk.Frame(
                secondary_frame, bg=self.style.colors["surface"]
            )
            feels_like_frame.grid(row=0, column=0, sticky="ew", padx=(0, 5))

            tk.Label(
                feels_like_frame,
                text="Feels like:",
                font=self.style.fonts["caption"],
                bg=self.style.colors["surface"],
                fg=self.style.colors["text_secondary"],
            ).pack()

            self.feels_like_display = tk.Label(
                feels_like_frame,
                text="--°",
                font=self.style.fonts["body_bold"],
                bg=self.style.colors["surface"],
                fg=self.style.colors["accent"],
            )
            self.feels_like_display.pack()

        if self.show_heat_index:
            heat_index_frame = tk.Frame(
                secondary_frame, bg=self.style.colors["surface"]
            )
            heat_index_frame.grid(row=0, column=1, sticky="ew", padx=(5, 0))

            tk.Label(
                heat_index_frame,
                text="Heat Index:",
                font=self.style.fonts["caption"],
                bg=self.style.colors["surface"],
                fg=self.style.colors["text_secondary"],
            ).pack()

            self.heat_index_display = tk.Label(
                heat_index_frame,
                text="--°",
                font=self.style.fonts["body_bold"],
                bg=self.style.colors["surface"],
                fg=self.style.colors["warning"],
            )
            self.heat_index_display.pack()

    def _create_additional_controls(self, parent) -> None:
        """Create additional temperature controls.

        Args:
            parent: Parent widget
        """
        controls_frame = GlassmorphicFrame(parent)
        controls_frame.grid(
            row=0, column=2, sticky="ew", pady=self.spacing.element_spacing
        )

        # Precision control
        precision_frame = tk.Frame(controls_frame, bg=self.style.colors["surface"])
        precision_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        tk.Label(
            precision_frame,
            text="Precision:",
            font=self.style.fonts["caption"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        ).pack(anchor="w")

        precision_scale = tk.Scale(
            precision_frame,
            from_=0,
            to=2,
            orient="horizontal",
            variable=self.precision_var,
            command=self._on_precision_change,
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
            highlightthickness=0,
            troughcolor=self.style.colors["surface_secondary"],
            activebackground=self.style.colors["accent"],
        )
        precision_scale.pack(fill="x")

        # Show symbol toggle
        symbol_check = tk.Checkbutton(
            controls_frame,
            text="Show °Symbol",
            variable=self.show_symbol_var,
            command=self._on_symbol_toggle,
            font=self.style.fonts["caption"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
            selectcolor=self.style.colors["accent"],
            activebackground=self.style.colors["surface"],
            activeforeground=self.style.colors["text_primary"],
        )
        symbol_check.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))

    def _change_unit(self, new_unit: TemperatureUnit) -> None:
        """Change temperature unit.

        Args:
            new_unit: New temperature unit
        """
        if new_unit == self.current_unit:
            return

        old_unit = self.current_unit
        self.current_unit = new_unit

        # Update button styles
        for unit, button in self.unit_buttons.items():
            if unit == new_unit:
                button.set_style_variant("primary")
                self.animation.pulse(button)
            else:
                button.set_style_variant("secondary")

        # Convert existing temperatures
        if self.current_temp is not None:
            self.current_temp = self._convert_temperature(
                self.current_temp, old_unit, new_unit
            )
        if self.feels_like_temp is not None:
            self.feels_like_temp = self._convert_temperature(
                self.feels_like_temp, old_unit, new_unit
            )
        if self.heat_index is not None:
            self.heat_index = self._convert_temperature(
                self.heat_index, old_unit, new_unit
            )
        if self.wind_chill is not None:
            self.wind_chill = self._convert_temperature(
                self.wind_chill, old_unit, new_unit
            )

        # Update displays
        self._update_displays()

        # Notify callback
        if self.on_unit_change:
            self.on_unit_change(new_unit)

    def _convert_temperature(
        self, temp, from_unit: TemperatureUnit, to_unit: TemperatureUnit
    ):
        """Convert temperature between units.

        Args:
            temp: Temperature value (float or Temperature object)
            from_unit: Source unit
            to_unit: Target unit

        Returns:
            Converted temperature (same type as input)
        """
        if from_unit == to_unit:
            return temp

        # Extract temperature value if it's a Temperature object
        temp_value = temp.value if hasattr(temp, "value") else temp

        # Convert to Celsius first
        if from_unit == TemperatureUnit.FAHRENHEIT:
            celsius = (temp_value - 32) * 5 / 9
        elif from_unit == TemperatureUnit.KELVIN:
            celsius = temp_value - 273.15
        else:  # Already Celsius
            celsius = temp_value

        # Convert from Celsius to target
        if to_unit == TemperatureUnit.FAHRENHEIT:
            converted_value = celsius * 9 / 5 + 32
        elif to_unit == TemperatureUnit.KELVIN:
            converted_value = celsius + 273.15
        else:  # Target is Celsius
            converted_value = celsius

        # Return same type as input
        if hasattr(temp, "value"):
            # Create new Temperature object with converted value
            from src.models.weather_models import Temperature
            from src.models.weather_models import TemperatureUnit as ModelTempUnit

            # Map UI enum to model enum
            unit_map = {
                TemperatureUnit.CELSIUS: ModelTempUnit.CELSIUS,
                TemperatureUnit.FAHRENHEIT: ModelTempUnit.FAHRENHEIT,
                TemperatureUnit.KELVIN: ModelTempUnit.KELVIN,
            }
            return Temperature(value=converted_value, unit=unit_map[to_unit])
        else:
            return converted_value

    def _format_temperature(self, temp) -> str:
        """Format temperature for display.

        Args:
            temp: Temperature value (float or Temperature object)

        Returns:
            Formatted temperature string
        """
        if temp is None:
            return "--°" if self.show_symbol_var.get() else "--"

        # Extract temperature value if it's a Temperature object
        temp_value = temp.value if hasattr(temp, "value") else temp

        precision = self.precision_var.get()
        temp_str = f"{temp_value: .{precision}f}"

        if self.show_symbol_var.get():
            temp_str += f"°{self.current_unit.value}"

        return temp_str

    def _update_displays(self) -> None:
        """Update all temperature displays."""
        # Main temperature
        if self.temp_display:
            temp_text = self._format_temperature(self.current_temp)
            temp_value = (
                self.current_temp.value
                if hasattr(self.current_temp, "value")
                else self.current_temp
            )
            temp_color = self.style.get_temperature_color(temp_value or 0)
            self.temp_display.config(text=temp_text, fg=temp_color)

        # Feels like temperature
        if self.feels_like_display:
            feels_like_text = self._format_temperature(self.feels_like_temp)
            self.feels_like_display.config(text=feels_like_text)

        # Heat index
        if self.heat_index_display:
            heat_index_text = self._format_temperature(self.heat_index)
            self.heat_index_display.config(text=heat_index_text)

    def _on_precision_change(self, value: str) -> None:
        """Handle precision change.

        Args:
            value: New precision value
        """
        self._update_displays()

    def _on_symbol_toggle(self) -> None:
        """Handle symbol display toggle."""
        self._update_displays()

    def set_temperature(
        self,
        temp: float,
        feels_like: Optional[float] = None,
        heat_index: Optional[float] = None,
        wind_chill: Optional[float] = None,
    ) -> None:
        """Set temperature values.

        Args:
            temp: Main temperature
            feels_like: Feels like temperature
            heat_index: Heat index temperature
            wind_chill: Wind chill temperature
        """
        self.current_temp = temp
        self.feels_like_temp = feels_like
        self.heat_index = heat_index
        self.wind_chill = wind_chill

        self._update_displays()

        # Apply animation to main display
        if self.temp_display:
            temp_value = temp.value if hasattr(temp, "value") else temp
            self.animation.text_glow(
                self.temp_display, self.style.get_temperature_color(temp_value)
            )

    def get_current_unit(self) -> TemperatureUnit:
        """Get current temperature unit.

        Returns:
            Current temperature unit
        """
        return self.current_unit

    def get_temperature_data(self) -> Dict[str, Any]:
        """Get all temperature data.

        Returns:
            Dictionary containing temperature data
        """
        return {
            "current_temp": self.current_temp,
            "feels_like": self.feels_like_temp,
            "heat_index": self.heat_index,
            "wind_chill": self.wind_chill,
            "unit": self.current_unit.value,
            "precision": self.precision_var.get(),
            "show_symbol": self.show_symbol_var.get(),
        }

    def set_temperature_range(self, min_temp: float, max_temp: float) -> None:
        """Set temperature range display.

        Args:
            min_temp: Minimum temperature
            max_temp: Maximum temperature
        """
        if not hasattr(self, "temp_range_display") or not self.temp_range_display:
            # Create range display if it doesn't exist
            range_frame = tk.Frame(self, bg=self.style.colors["surface"])
            range_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

            self.temp_range_display = tk.Label(
                range_frame,
                text="",
                font=self.style.fonts["caption"],
                bg=self.style.colors["surface"],
                fg=self.style.colors["text_secondary"],
            )
            self.temp_range_display.pack()

        # Format range text
        min_text = self._format_temperature(min_temp)
        max_text = self._format_temperature(max_temp)
        range_text = f"Range: {min_text} - {max_text}"

        self.temp_range_display.config(text=range_text)

    def clear_temperature(self) -> None:
        """Clear all temperature displays."""
        self.current_temp = None
        self.feels_like_temp = None
        self.heat_index = None
        self.wind_chill = None

        self._update_displays()

    def set_loading_state(self, loading: bool) -> None:
        """Set loading state for temperature controls.

        Args:
            loading: Whether controls are in loading state
        """
        if loading:
            # Disable unit buttons
            for button in self.unit_buttons.values():
                button.set_enabled(False)

            # Show loading in main display
            if self.temp_display:
                self.temp_display.config(text="Loading...")
                self.animation.pulse(self.temp_display)
        else:
            # Enable unit buttons
            for button in self.unit_buttons.values():
                button.set_enabled(True)

            # Update displays
            self._update_displays()

    def get_conversion_info(self) -> Dict[str, str]:
        """Get temperature conversion information.

        Returns:
            Dictionary with conversion formulas and info
        """
        return {
            "fahrenheit_to_celsius": "(°F - 32) × 5/9",
            "celsius_to_fahrenheit": "°C × 9/5 + 32",
            "celsius_to_kelvin": "°C + 273.15",
            "kelvin_to_celsius": "K - 273.15",
            "current_unit": self.current_unit.value,
            "absolute_zero_f": "-459.67°F",
            "absolute_zero_c": "-273.15°C",
            "absolute_zero_k": "0K",
        }

    def update_responsive_layout(self) -> None:
        """Update layout based on current window size."""
        if hasattr(self, "responsive_layout"):
            self.responsive_layout.update_layout()

            # Update spacing values
            self.spacing = ResponsiveSpacing()

            # Update button styles based on screen size
            for button in self.unit_buttons.values():
                if hasattr(button, "update_responsive_style"):
                    button.update_responsive_style()
