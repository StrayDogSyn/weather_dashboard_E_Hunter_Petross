"""Header component for the Weather Dashboard application.

This module provides the application header with branding, navigation,
and utility controls with glassmorphic styling and animations.
"""

import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import ttk
from typing import Any, Callable, Dict, Optional

from ..animations.effects import AnimationHelper
from ..styles.glassmorphic import GlassmorphicFrame, GlassmorphicStyle
from ..widgets.modern_button import IconButton, ModernButton
from .responsive_layout import ResponsiveSpacing
from .weather_icons import WeatherIcons


class ApplicationHeader(GlassmorphicFrame):
    """Application header with branding and controls."""

    def __init__(
        self,
        parent,
        on_settings: Optional[Callable] = None,
        on_refresh: Optional[Callable] = None,
        on_help: Optional[Callable] = None,
        **kwargs,
    ):
        """Initialize application header.

        Args:
            parent: Parent widget
            on_settings: Callback for settings button
            on_refresh: Callback for refresh button
            on_help: Callback for help button
            **kwargs: Additional frame configuration
        """
        super().__init__(parent, **kwargs)

        self.style = GlassmorphicStyle()
        self.animation = AnimationHelper()
        self.icons = WeatherIcons()
        # Use ResponsiveSpacing class attributes directly

        # Callbacks
        self.on_settings = on_settings
        self.on_refresh = on_refresh
        self.on_help = on_help

        # Components
        self.logo_label: Optional[tk.Label] = None
        self.title_label: Optional[tk.Label] = None
        self.tagline_label: Optional[tk.Label] = None
        self.clock_label: Optional[tk.Label] = None
        self.weather_icon_label: Optional[tk.Label] = None
        self.temp_display_label: Optional[tk.Label] = None

        # Toolbar buttons
        self.settings_button: Optional[IconButton] = None
        self.refresh_button: Optional[IconButton] = None
        self.help_button: Optional[IconButton] = None
        self.minimize_button: Optional[IconButton] = None
        self.maximize_button: Optional[IconButton] = None
        self.close_button: Optional[IconButton] = None

        # State
        self.current_temperature: Optional[float] = None
        self.current_condition: str = ""
        self.clock_running = False
        self.clock_thread: Optional[threading.Thread] = None

        self._setup_ui()
        self._start_clock()

    def _setup_ui(self) -> None:
        """Set up the header user interface."""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)

        # Main header container
        header_container = tk.Frame(self, bg=self.style.colors["surface"])
        header_container.grid(
            row=0, column=0, columnspan=3, sticky="ew", padx=15, pady=10
        )
        header_container.grid_columnconfigure(1, weight=1)

        # Left section (branding)
        self._create_branding_section(header_container)

        # Center section (title and tagline)
        self._create_title_section(header_container)

        # Right section (toolbar)
        self._create_toolbar_section(header_container)

        # Weather status bar
        self._create_weather_status_bar()

    def _create_branding_section(self, parent) -> None:
        """Create branding section with logo and weather icon.

        Args:
            parent: Parent widget
        """
        branding_frame = tk.Frame(parent, bg=self.style.colors["surface"])
        branding_frame.grid(row=0, column=0, sticky="w")

        # Justice emoji (as mentioned in original code)
        justice_label = tk.Label(
            branding_frame,
            text="⚖️",
            font=self.style.fonts["icon_small"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["accent"],
        )
        justice_label.pack(side="left", padx=(0, 8))

        # Weather logo/icon
        self.logo_label = tk.Label(
            branding_frame,
            text=self.icons.DEFAULT,
            font=self.style.fonts["icon_medium"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["accent"],
        )
        self.logo_label.pack(side="left", padx=(0, 10))

        # Apply logo animation
        self.animation.pulse(self.logo_label, duration=2000)

    def _create_title_section(self, parent) -> None:
        """Create title section with app name and tagline.

        Args:
            parent: Parent widget
        """
        title_frame = tk.Frame(parent, bg=self.style.colors["surface"])
        title_frame.grid(row=0, column=1, sticky="ew", padx=20)

        # Main title
        self.title_label = tk.Label(
            title_frame,
            text="Weather Dashboard",
            font=self.style.fonts["title"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
            anchor="w",
        )
        self.title_label.pack(anchor="w")

        # Tagline
        self.tagline_label = tk.Label(
            title_frame,
            text="Your Personal Weather Companion",
            font=self.style.fonts["caption"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
            anchor="w",
        )
        self.tagline_label.pack(anchor="w")

        # Apply title animation
        self.animation.text_glow(self.title_label, self.style.colors["accent"])

    def _create_toolbar_section(self, parent) -> None:
        """Create toolbar section with utility buttons.

        Args:
            parent: Parent widget
        """
        toolbar_frame = tk.Frame(parent, bg=self.style.colors["surface"])
        toolbar_frame.grid(row=0, column=2, sticky="e")

        # Clock display
        self.clock_label = tk.Label(
            toolbar_frame,
            text="",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        )
        self.clock_label.pack(side="left", padx=(0, 15))

        # Utility buttons
        button_frame = tk.Frame(toolbar_frame, bg=self.style.colors["surface"])
        button_frame.pack(side="left")

        # Help button
        self.help_button = IconButton(
            button_frame,
            icon="❓",
            command=self._handle_help,
            style_variant="secondary",
        )
        self.help_button.pack(side="left", padx=2)

        # Refresh button
        self.refresh_button = IconButton(
            button_frame,
            icon="🔄",
            command=self._handle_refresh,
            style_variant="secondary",
        )
        self.refresh_button.pack(side="left", padx=2)

        # Settings button
        self.settings_button = IconButton(
            button_frame,
            icon="⚙️",
            command=self._handle_settings,
            style_variant="secondary",
        )
        self.settings_button.pack(side="left", padx=2)

        # Window controls (optional)
        self._create_window_controls(button_frame)

    def _create_window_controls(self, parent) -> None:
        """Create window control buttons.

        Args:
            parent: Parent widget
        """
        controls_frame = tk.Frame(parent, bg=self.style.colors["surface"])
        controls_frame.pack(side="left", padx=(10, 0))

        # Minimize button
        self.minimize_button = IconButton(
            controls_frame,
            icon="➖",
            command=self._handle_minimize,
            style_variant="secondary",
        )
        self.minimize_button.pack(side="left", padx=1)

        # Maximize button
        self.maximize_button = IconButton(
            controls_frame,
            icon="⬜",
            command=self._handle_maximize,
            style_variant="secondary",
        )
        self.maximize_button.pack(side="left", padx=1)

        # Close button
        self.close_button = IconButton(
            controls_frame,
            icon="❌",
            command=self._handle_close,
            style_variant="secondary",
        )
        self.close_button.pack(side="left", padx=1)

    def _create_weather_status_bar(self) -> None:
        """Create weather status bar below main header."""
        status_frame = tk.Frame(self, bg=self.style.colors["surface_secondary"])
        status_frame.grid(
            row=1, column=0, columnspan=3, sticky="ew", padx=15, pady=(0, 5)
        )
        status_frame.grid_columnconfigure(1, weight=1)

        # Current weather icon
        self.weather_icon_label = tk.Label(
            status_frame,
            text=self.icons.DEFAULT,
            font=self.style.fonts["icon_small"],
            bg=self.style.colors["surface_secondary"],
            fg=self.style.colors["accent"],
        )
        self.weather_icon_label.grid(
            row=0,
            column=0,
            padx=(ResponsiveSpacing.MEDIUM, ResponsiveSpacing.SMALL),
            pady=ResponsiveSpacing.SMALL,
        )

        # Temperature display
        self.temp_display_label = tk.Label(
            status_frame,
            text="--°",
            font=self.style.fonts["body_bold"],
            bg=self.style.colors["surface_secondary"],
            fg=self.style.colors["text_primary"],
        )
        self.temp_display_label.grid(
            row=0,
            column=1,
            sticky="w",
            padx=ResponsiveSpacing.SMALL,
            pady=ResponsiveSpacing.SMALL,
        )

        # Status text
        status_text = tk.Label(
            status_frame,
            text="Ready for weather updates",
            font=self.style.fonts["caption"],
            bg=self.style.colors["surface_secondary"],
            fg=self.style.colors["text_secondary"],
        )
        status_text.grid(
            row=0,
            column=2,
            sticky="e",
            padx=(ResponsiveSpacing.SMALL, ResponsiveSpacing.MEDIUM),
            pady=ResponsiveSpacing.SMALL,
        )

    def _start_clock(self) -> None:
        """Start the clock display."""
        self.clock_running = True
        self.clock_thread = threading.Thread(target=self._update_clock, daemon=True)
        self.clock_thread.start()

    def _update_clock(self) -> None:
        """Update clock display in separate thread."""
        while self.clock_running:
            try:
                current_time = datetime.now().strftime("%I:%M:%S %p")
                if self.clock_label and self.clock_label.winfo_exists():
                    self.clock_label.config(text=current_time)
                time.sleep(1)
            except tk.TclError:
                # Widget destroyed, stop clock
                break
            except Exception:
                # Handle any other errors silently
                break

    def _handle_settings(self) -> None:
        """Handle settings button click."""
        self.animation.pulse(self.settings_button)
        if self.on_settings:
            self.on_settings()

    def _handle_refresh(self) -> None:
        """Handle refresh button click."""
        # Rotate animation for refresh
        self.animation.scale_effect(self.refresh_button, scale_factor=1.2)
        if self.on_refresh:
            self.on_refresh()

    def _handle_help(self) -> None:
        """Handle help button click."""
        self.animation.glow_effect(self.help_button, self.style.colors["accent"])
        if self.on_help:
            self.on_help()

    def _handle_minimize(self) -> None:
        """Handle minimize button click."""
        # Get root window and minimize
        root = self.winfo_toplevel()
        root.iconify()

    def _handle_maximize(self) -> None:
        """Handle maximize button click."""
        # Get root window and toggle maximize
        root = self.winfo_toplevel()
        if root.state() == "zoomed":
            root.state("normal")
            self.maximize_button.set_icon("⬜")
        else:
            root.state("zoomed")
            self.maximize_button.set_icon("🔳")

    def _handle_close(self) -> None:
        """Handle close button click."""
        # Get root window and close
        root = self.winfo_toplevel()
        root.quit()
        root.destroy()

    def update_weather_display(
        self, temperature, condition: str, unit: str = "F"
    ) -> None:
        """Update weather display in header.

        Args:
            temperature: Current temperature (float or Temperature object)
            condition: Weather condition
            unit: Temperature unit
        """
        self.current_temperature = temperature
        self.current_condition = condition

        # Extract temperature value if it's a Temperature object
        temp_value = temperature.value if hasattr(temperature, "value") else temperature

        # Update weather icon
        weather_icon = self.icons.get_icon(condition, temperature)
        if self.weather_icon_label:
            self.weather_icon_label.config(text=weather_icon)
            self.animation.pulse(self.weather_icon_label)

        # Update temperature display
        temp_text = f"{temp_value: .0f}°{unit}"
        temp_color = self.style.get_temperature_color(temp_value)
        if self.temp_display_label:
            self.temp_display_label.config(text=temp_text, fg=temp_color)
            self.animation.text_glow(self.temp_display_label, temp_color)

        # Update logo with weather-appropriate icon
        if self.logo_label:
            self.logo_label.config(text=weather_icon)

    def set_loading_state(self, loading: bool, message: str = "Loading...") -> None:
        """Set header loading state.

        Args:
            loading: Whether header is in loading state
            message: Loading message to display
        """
        if loading:
            # Show loading animation
            if self.refresh_button:
                self.refresh_button.set_loading(True, "")
                self.animation.pulse(self.refresh_button, duration=1000)

            # Update status
            if hasattr(self, "status_text"):
                self.status_text.config(text=message)
        else:
            # Stop loading animation
            if self.refresh_button:
                self.refresh_button.set_loading(False)

    def set_connection_status(self, connected: bool) -> None:
        """Set connection status indicator.

        Args:
            connected: Whether application is connected to weather service
        """
        if connected:
            pass  # Connection status handling - connected
        else:
            pass  # Connection status handling - disconnected

        # Update connection indicator (if exists)
        # This could be added to the status bar

    def show_notification(self, message: str, notification_type: str = "info") -> None:
        """Show notification in header.

        Args:
            message: Notification message
            notification_type: Type of notification ('info', 'success', 'warning', 'error')
        """
        # Create temporary notification label
        notification_frame = tk.Frame(self, bg=self.style.colors["surface"])
        notification_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=15)

        # Notification colors based on type
        colors = {
            "info": self.style.colors["accent"],
            "success": self.style.colors.get("success", "#4CAF50"),
            "warning": self.style.colors.get("warning", "#FF9800"),
            "error": self.style.colors.get("error", "#F44336"),
        }

        notification_label = tk.Label(
            notification_frame,
            text=message,
            font=self.style.fonts["caption"],
            bg=colors.get(notification_type, self.style.colors["accent"]),
            fg=self.style.colors["text_primary"],
            padx=10,
            pady=5,
        )
        notification_label.pack(fill="x")

        # Apply entrance animation
        self.animation.slide_in(notification_frame, direction="down")

        # Auto-hide after 3 seconds
        self.after(3000, lambda: self._hide_notification(notification_frame))

    def _hide_notification(self, notification_frame) -> None:
        """Hide notification frame.

        Args:
            notification_frame: Notification frame to hide
        """
        try:
            # Apply exit animation (using fade_in with reverse effect)
            self.animation.fade_in(notification_frame, duration=300)

            # Destroy after animation
            self.after(300, notification_frame.destroy)
        except tk.TclError:
            # Frame already destroyed
            pass

    def update_tagline(self, new_tagline: str) -> None:
        """Update header tagline.

        Args:
            new_tagline: New tagline text
        """
        if self.tagline_label:
            self.tagline_label.config(text=new_tagline)
            self.animation.text_glow(self.tagline_label, self.style.colors["accent"])

    def get_header_info(self) -> Dict[str, Any]:
        """Get current header information.

        Returns:
            Dictionary containing header state
        """
        return {
            "current_temperature": self.current_temperature,
            "current_condition": self.current_condition,
            "clock_running": self.clock_running,
            "current_time": datetime.now().isoformat(),
        }

    def cleanup(self) -> None:
        """Clean up header resources."""
        # Stop clock thread
        self.clock_running = False
        if self.clock_thread and self.clock_thread.is_alive():
            self.clock_thread.join(timeout=1)

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
