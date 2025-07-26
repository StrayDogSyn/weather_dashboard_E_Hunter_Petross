"""Refactored Weather Dashboard GUI with glassmorphic design.

This module provides a comprehensive weather dashboard interface with:
- Modern glassmorphic styling and animations
- Real-time weather data display
- Interactive charts and forecasts
- Voice assistant integration
- Customizable themes and layouts

Refactored for better separation of concerns and maintainability.
"""

import json
import logging
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog, ttk
from typing import Any, Callable, Dict, List, Optional

import ttkbootstrap as ttk_bs
from ttkbootstrap.constants import DANGER, DARK, INFO, LIGHT, PRIMARY, SECONDARY

from src.config.config import config_manager
from src.interfaces.weather_interfaces import IUserInterface
from src.models.capstone_models import (
    ActivitySuggestion,
    JournalEntry,
    MoodType,
    WeatherComparison,
    WeatherPoem,
)
from src.models.weather_models import (
    CurrentWeather,
    FavoriteCity,
    Location,
    WeatherForecast,
)
from src.services.sound_service import (
    SoundType,
    get_sound_service,
    play_sound,
    play_weather_sound,
)

from .animations.effects import AnimationHelper
from .components import ModernEntry
from .components.header import ApplicationHeader
from .components.main_dashboard import MainDashboard
from .components.responsive_layout import ResponsiveLayoutManager, ResponsiveSpacing
from .components.search_panel import SearchPanel
from .components.temperature_controls import TemperatureControls, TemperatureUnit
from .components.weather_card import WeatherCard
from .components.weather_icons import WeatherIcons

# Import WeatherDashboard to avoid circular import issues
from .dashboard import WeatherDashboard

# Import refactored components
from .styles.glassmorphic import GlassmorphicFrame, GlassmorphicStyle
from .widgets.enhanced_button import ButtonFactory
from .widgets.modern_button import IconButton, ModernButton

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherDashboardGUI(IUserInterface):
    """Main Weather Dashboard GUI application with refactored components."""

    def __init__(self):
        """Initialize the Weather Dashboard GUI."""
        # Initialize ttkbootstrap style
        self.style = ttk_bs.Style(theme="darkly")

        # Load configuration
        self.config = config_manager

        # Set up logging
        self.logger = logging.getLogger(__name__)

        # Initialize styling and animation helpers first
        self.glassmorphic_style = GlassmorphicStyle()
        self.animation_helper = AnimationHelper()
        self.weather_icons = WeatherIcons()

        # Initialize responsive layout manager
        self.responsive_layout = ResponsiveLayoutManager()
        self.button_factory = ButtonFactory()

        # Initialize main window
        self.root = ttk_bs.Window(themename="darkly")
        self.setup_window()

        # Initialize weather dashboard (will be set later to avoid circular import)
        self.weather_dashboard = None

        # Initialize callbacks dictionary
        self.callbacks: Dict[str, Callable] = {}

        # UI Components
        self.header: Optional[ApplicationHeader] = None
        self.main_dashboard: Optional[MainDashboard] = None
        self.temperature_controls: Optional[TemperatureControls] = None

        # State management
        self.current_weather: Optional[CurrentWeather] = None
        self.forecast_data: Optional[WeatherForecast] = None
        self.favorite_cities: List[FavoriteCity] = []
        self.is_loading = False

        # Threading
        self.update_thread: Optional[threading.Thread] = None
        self.stop_updates = threading.Event()

        # Setup UI
        self.setup_styles()
        self.create_layout()

        # Initialize sound service
        self.sound_service = get_sound_service()

        # Load saved data
        self.load_saved_data()

        # Start periodic updates
        self.start_periodic_updates()

    def setup_window(self) -> None:
        """Configure the main window."""
        self.root.title("Weather Dashboard - Your Personal Weather Companion")

        # Set window to fullscreen
        self.root.state("zoomed")  # Windows fullscreen
        self.root.minsize(1200, 800)

        # Configure window properties
        self.root.configure(bg=self.glassmorphic_style.BACKGROUND)

        # Center window on screen (fallback if fullscreen fails)
        self.center_window()

        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Bind window events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Configure>", self.on_window_resize)

        # Initialize responsive layout with window
        self.responsive_layout.set_window(self.root)

    def center_window(self) -> None:
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self) -> None:
        """Configure custom styles for the application."""
        # Configure ttk styles to match glassmorphic theme
        style = ttk.Style()

        # Configure notebook style
        style.configure(
            "Custom.TNotebook",
            background=self.glassmorphic_style.GLASS_BG,
            borderwidth=0,
            tabmargins=[2, 5, 2, 0],
        )

        style.configure(
            "Custom.TNotebook.Tab",
            background=self.glassmorphic_style.GLASS_BG_LIGHT,
            foreground=self.glassmorphic_style.TEXT_PRIMARY,
            padding=[20, 10],
            borderwidth=1,
            relief="solid",
        )

        style.map(
            "Custom.TNotebook.Tab",
            background=[
                ("selected", self.glassmorphic_style.ACCENT),
                ("active", self.glassmorphic_style.GLASS_BG),
            ],
            foreground=[
                ("selected", self.glassmorphic_style.TEXT_PRIMARY),
                ("active", self.glassmorphic_style.TEXT_PRIMARY),
            ],
        )

    def create_layout(self) -> None:
        """Create the main application layout with responsive design."""
        # Get responsive spacing
        spacing = self.responsive_layout.get_spacing()

        # Create header
        self.header = ApplicationHeader(
            self.root,
            on_settings=self.show_settings,
            on_refresh=self.refresh_weather,
            on_help=self.show_help,
        )
        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=spacing.container_padding,
            pady=(spacing.container_padding, 0),
        )

        # Create main content area with responsive layout
        main_content = GlassmorphicFrame(self.root)
        main_content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=spacing.container_padding,
            pady=spacing.container_padding,
        )
        main_content.grid_rowconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=1)

        # Store main content for responsive updates
        self.main_content = main_content

        # Create temperature controls with responsive layout
        self.temperature_controls = TemperatureControls(
            main_content,
            initial_unit=TemperatureUnit.FAHRENHEIT,
            on_unit_change=self.on_temperature_unit_change,
        )
        self.temperature_controls.grid(
            row=0,
            column=0,
            sticky="ns",
            padx=(spacing.element_padding, spacing.element_spacing),
            pady=spacing.element_padding,
        )

        # Create main dashboard with responsive layout
        self.main_dashboard = MainDashboard(
            main_content,
            on_search=self.search_weather,
            on_add_favorite=self.add_favorite_city,
            on_tab_change=self.on_tab_change,
        )
        self.main_dashboard.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(spacing.element_spacing, spacing.element_padding),
            pady=spacing.element_padding,
        )

        # Apply responsive layout management
        self.responsive_layout.add_component(self.header, "header")
        self.responsive_layout.add_component(self.temperature_controls, "sidebar")
        self.responsive_layout.add_component(self.main_dashboard, "main")

        # Apply entrance animations
        self.animation_helper.slide_in(self.header, direction="down")
        self.animation_helper.fade_in(main_content)

    def set_weather_dashboard(self, dashboard) -> None:
        """Set the weather dashboard instance (to avoid circular imports).

        Args:
            dashboard: WeatherDashboard instance
        """
        self.weather_dashboard = dashboard
        # Note: MainDashboard doesn't have set_weather_dashboard method
        # This method is currently unused but kept for potential future use

    def set_callback(self, name: str, callback: Callable) -> None:
        """Set a callback function for the specified name.

        Args:
            name: Name of the callback
            callback: Callback function to set
        """
        self.callbacks[name] = callback

    def get_callback(self, name: str) -> Optional[Callable]:
        """Get a callback function by name.

        Args:
            name: Name of the callback

        Returns:
            The callback function if found, None otherwise
        """
        return self.callbacks.get(name)

    def update_status(self, message: str) -> None:
        """Update the status message in the UI.

        Args:
            message: Status message to display
        """
        if self.header:
            # Update header status if available
            try:
                self.header.update_status(message)
            except AttributeError:
                # Header doesn't have update_status method, log the message instead
                self.logger.info(f"Status: {message}")
        else:
            # Log the status message if no header available
            self.logger.info(f"Status: {message}")

    # Weather-related methods
    def search_weather(self, city: str) -> None:
        """Search for weather in a specific city.

        Args:
            city: City name to search for
        """
        if not city.strip():
            self.show_error("Please enter a city name")
            return

        self.set_loading_state(True, f"Searching weather for {city}...")

        # Run search in separate thread
        search_thread = threading.Thread(
            target=self._search_weather_thread, args=(city,), daemon=True
        )
        search_thread.start()

    def _search_weather_thread(self, city: str) -> None:
        """Search for weather in separate thread.

        Args:
            city: City name to search for
        """
        try:
            if self.weather_dashboard:
                # Get weather data
                weather_data = self.weather_dashboard.get_weather(city)

                # Update UI in main thread
                self.root.after(0, lambda: self._update_weather_display(weather_data))

                # Play success sound
                play_sound(SoundType.SUCCESS)

        except Exception as e:
            self.logger.error(f"Error searching weather: {e}")
            error_msg = f"Error getting weather data: {str(e)}"
            self.root.after(0, lambda: self.show_error(error_msg))
            play_sound(SoundType.ERROR)
        finally:
            self.root.after(0, lambda: self.set_loading_state(False))

    def _update_weather_display(self, weather_data: CurrentWeather) -> None:
        """Update weather display with new data.

        Args:
            weather_data: Current weather data
        """
        self.current_weather = weather_data

        # Update header
        if self.header:
            self.header.update_weather_display(
                weather_data.temperature,
                weather_data.condition,
                self.temperature_controls.get_current_unit().value,
            )

        # Update temperature controls
        if self.temperature_controls:
            self.temperature_controls.set_temperature(
                weather_data.temperature,
                feels_like=getattr(weather_data, "feels_like", None),
                heat_index=getattr(weather_data, "heat_index", None),
            )

        # Update main dashboard
        if self.main_dashboard:
            self.main_dashboard.update_weather_data(weather_data)

        # Show notification
        if self.header:
            self.header.show_notification(
                f"Weather updated for {weather_data.location.name}", "success"
            )

    def refresh_weather(self) -> None:
        """Refresh current weather data."""
        if self.current_weather:
            self.search_weather(self.current_weather.location.name)
        else:
            self.show_info("No current weather data to refresh")

    def add_favorite_city(self, city: str) -> None:
        """Add a city to favorites.

        Args:
            city: City name to add
        """
        if not city.strip():
            return

        # Check if already in favorites
        if any(
            fav.location.name.lower() == city.lower() for fav in self.favorite_cities
        ):
            self.show_warning(f"{city} is already in your favorites")
            return

        # Create a basic location object for the city
        # Note: This creates a minimal location without coordinates
        # In a real implementation, you might want to geocode the city name
        location = Location(name=city, country="", latitude=0.0, longitude=0.0)

        # Add to favorites
        favorite = FavoriteCity(location=location, added_date=datetime.now())
        self.favorite_cities.append(favorite)

        # Update main dashboard
        if self.main_dashboard:
            self.main_dashboard.update_favorites(self.favorite_cities)

        # Save favorites
        self.save_favorites()

        # Show notification
        if self.header:
            self.header.show_notification(f"{city} added to favorites", "success")

        play_sound(SoundType.SUCCESS)

    def on_temperature_unit_change(self, new_unit: TemperatureUnit) -> None:
        """Handle temperature unit change.

        Args:
            new_unit: New temperature unit
        """
        # Update header display
        if self.header and self.current_weather:
            self.header.update_weather_display(
                self.current_weather.temperature,
                self.current_weather.condition,
                new_unit.value,
            )

        # Update main dashboard
        if self.main_dashboard:
            self.main_dashboard.on_temperature_unit_change(new_unit)

        # Save preference
        self.config.set("temperature_unit", new_unit.value)

    def on_tab_change(self, tab_name: str) -> None:
        """Handle tab change in main dashboard.

        Args:
            tab_name: Name of the selected tab
        """
        self.logger.info(f"Tab changed to: {tab_name}")

        # Play tab change sound
        play_sound(SoundType.BUTTON_CLICK)

        # Update header tagline based on tab
        taglines = {
            "current": "Current Weather Conditions",
            "forecast": "Weather Forecast & Trends",
            "comparison": "Compare Weather Across Cities",
            "journal": "Weather Journal & Memories",
            "activities": "Weather-Based Activity Suggestions",
            "poetry": "Weather-Inspired Poetry",
            "voice": "Voice Assistant & Commands",
            "favorites": "Your Favorite Cities",
        }

        if self.header and tab_name in taglines:
            self.header.update_tagline(taglines[tab_name])

    # UI State Management
    def set_loading_state(self, loading: bool, message: str = "Loading...") -> None:
        """Set application loading state.

        Args:
            loading: Whether app is in loading state
            message: Loading message to display
        """
        self.is_loading = loading

        # Update header
        if self.header:
            self.header.set_loading_state(loading, message)

        # Update main dashboard
        if self.main_dashboard:
            self.main_dashboard.set_loading_state(loading)

        # Update temperature controls
        if self.temperature_controls:
            self.temperature_controls.set_loading_state(loading)

    # Dialog methods
    def show_settings(self) -> None:
        """Show settings dialog."""
        # Create settings dialog (placeholder)
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("600x400")
        settings_window.configure(bg=self.glassmorphic_style.BACKGROUND)

        # Center dialog
        settings_window.transient(self.root)
        settings_window.grab_set()

        # Add settings content (placeholder)
        label = tk.Label(
            settings_window,
            text="Settings Dialog\n(To be implemented)",
            font=(
                self.glassmorphic_style.FONT_FAMILY,
                self.glassmorphic_style.FONT_SIZE_LARGE,
                "bold",
            ),
            bg=self.glassmorphic_style.BACKGROUND,
            fg=self.glassmorphic_style.TEXT_PRIMARY,
        )
        label.pack(expand=True)

        play_sound(SoundType.BUTTON_CLICK)

    def show_help(self) -> None:
        """Show help dialog."""
        help_text = """
Weather Dashboard Help

🌤️ Current Weather: View real-time weather conditions
📊 Forecast: See upcoming weather predictions
🔄 Comparison: Compare weather across multiple cities
📝 Journal: Record weather-related memories
🎯 Activities: Get weather-based activity suggestions
🎭 Poetry: Enjoy weather-inspired poetry
🎤 Voice: Use voice commands for hands-free control
⭐ Favorites: Quick access to your favorite cities

Tips:
• Use the search bar to find weather for any city
• Click the temperature unit buttons to switch between °F, °C, and K
• Add cities to favorites for quick access
• Use voice commands for hands-free operation
"""

        messagebox.showinfo("Help - Weather Dashboard", help_text)
        play_sound(SoundType.INFO)

    def show_error(self, message: str) -> None:
        """Show error message.

        Args:
            message: Error message to display
        """
        messagebox.showerror("Error", message)
        if self.header:
            self.header.show_notification(message, "error")

    def show_warning(self, message: str) -> None:
        """Show warning message.

        Args:
            message: Warning message to display
        """
        messagebox.showwarning("Warning", message)
        if self.header:
            self.header.show_notification(message, "warning")

    def show_info(self, message: str) -> None:
        """Show info message.

        Args:
            message: Info message to display
        """
        messagebox.showinfo("Information", message)
        if self.header:
            self.header.show_notification(message, "info")

    # Data persistence
    def load_saved_data(self) -> None:
        """Load saved application data."""
        try:
            # Load favorite cities
            favorites_data = self.config.get("favorite_cities", [])
            self.favorite_cities = []
            for fav in favorites_data:
                # Create a basic location object
                location = Location(
                    name=fav.get("name", ""), country="", latitude=0.0, longitude=0.0
                )
                favorite = FavoriteCity(
                    location=location,
                    added_date=datetime.fromisoformat(
                        fav.get("added_date", datetime.now().isoformat())
                    ),
                )
                self.favorite_cities.append(favorite)

            # Load temperature unit preference
            unit_str = self.config.get("temperature_unit", "F")
            try:
                unit = TemperatureUnit(unit_str)
                if self.temperature_controls:
                    self.temperature_controls._change_unit(unit)
            except ValueError:
                pass  # Use default unit

        except Exception as e:
            self.logger.error(f"Error loading saved data: {e}")

    def save_favorites(self) -> None:
        """Save favorite cities to configuration."""
        try:
            favorites_data = [
                {
                    "name": fav.location.name,
                    "added_date": (
                        fav.added_date.isoformat()
                        if fav.added_date
                        else datetime.now().isoformat()
                    ),
                }
                for fav in self.favorite_cities
            ]
            self.config.set("favorite_cities", favorites_data)
        except Exception as e:
            self.logger.error(f"Error saving favorites: {e}")

    # Periodic updates
    def start_periodic_updates(self) -> None:
        """Start periodic weather updates."""

        def update_loop():
            while not self.stop_updates.is_set():
                try:
                    # Update every 30 minutes
                    if self.stop_updates.wait(1800):  # 30 minutes
                        break

                    # Refresh current weather if available
                    if self.current_weather and not self.is_loading:
                        self.root.after(0, self.refresh_weather)

                except Exception as e:
                    self.logger.error(f"Error in update loop: {e}")

        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()

    # Event handlers
    def on_window_resize(self, event) -> None:
        """Handle window resize event.

        Args:
            event: Resize event
        """
        if event.widget == self.root:
            # Update responsive layout
            self.responsive_layout.update_layout()

            # Update component layouts based on new size
            if self.main_dashboard:
                self.main_dashboard.update_responsive_layout()

            if self.temperature_controls:
                self.temperature_controls.update_responsive_layout()

    def on_closing(self) -> None:
        """Handle application closing."""
        try:
            # Stop periodic updates
            self.stop_updates.set()
            if self.update_thread and self.update_thread.is_alive():
                self.update_thread.join(timeout=1)

            # Save current state
            self.save_favorites()

            # Cleanup components
            if self.header:
                self.header.cleanup()

            # Close application
            self.root.quit()
            self.root.destroy()

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            self.root.destroy()

    # Interface implementation methods
    def display_weather(self, weather: CurrentWeather) -> None:
        """Display weather data (IUserInterface implementation).

        Args:
            weather: Current weather data
        """
        self._update_weather_display(weather)

    def display_forecast(self, forecast: WeatherForecast) -> None:
        """Display forecast data (IUserInterface implementation).

        Args:
            forecast: Weather forecast data
        """
        self.forecast_data = forecast
        if self.main_dashboard:
            self.main_dashboard.update_forecast_data(forecast)

    def display_error(self, error: str) -> None:
        """Display error message (IUserInterface implementation).

        Args:
            error: Error message
        """
        self.show_error(error)

    def get_user_input(self, prompt: str) -> str:
        """Get user input (IUserInterface implementation).

        Args:
            prompt: Input prompt

        Returns:
            User input string
        """
        return simpledialog.askstring("Input", prompt) or ""

    def show_message(self, message: str) -> None:
        """Show message to user (IUserInterface implementation).

        Args:
            message: Message to display
        """
        self.show_info(message)

    def display_weather_poem(self, poem) -> None:
        """Display weather poem (IUserInterface implementation).

        Args:
            poem: Weather poem to display
        """
        try:
            # WeatherPoem already imported at module level
            from ..services.poetry_service import WeatherPoetryService

            if isinstance(poem, WeatherPoem):
                # Format the poem for display
                poetry_service = WeatherPoetryService()
                formatted_poem = poetry_service.format_poetry_display(poem)

                # Show in a message dialog with custom title
                title = f"🎭 Weather Poetry - {poem.poem_type.title()}"
                messagebox.showinfo(title, formatted_poem)

                # Also update the poetry tab if available
                if self.main_dashboard and hasattr(self.main_dashboard, "poetry_tab"):
                    self._update_poetry_tab(formatted_poem)
            else:
                # Handle string poems or other formats
                messagebox.showinfo("🎭 Weather Poetry", str(poem))

        except Exception as e:
            self.logger.error(f"Error displaying weather poem: {e}")
            messagebox.showinfo("🎭 Weather Poetry", str(poem))

    def _update_poetry_tab(self, formatted_poem: str) -> None:
        """Update the poetry tab with new poem content.

        Args:
            formatted_poem: Formatted poem text
        """
        try:
            if self.main_dashboard and hasattr(self.main_dashboard, "poetry_tab"):
                # Clear existing content and add new poem
                for widget in self.main_dashboard.poetry_tab.winfo_children():
                    if hasattr(widget, "winfo_children"):
                        for child in widget.winfo_children():
                            if (
                                isinstance(child, tk.Label)
                                and "poetry" in str(child.cget("text")).lower()
                            ):
                                child.config(text=formatted_poem)
                                break
        except Exception as e:
            self.logger.error(f"Error updating poetry tab: {e}")

    def run(self) -> None:
        """Run the GUI application."""
        try:
            self.logger.info("Starting Weather Dashboard GUI")
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"Error running GUI: {e}")
            raise
        finally:
            self.logger.info("Weather Dashboard GUI stopped")


# WeatherDashboard now imported at top of file


def create_gui() -> WeatherDashboardGUI:
    """Create and return a new GUI instance.

    Returns:
        WeatherDashboardGUI instance
    """
    return WeatherDashboardGUI()


if __name__ == "__main__":
    # Create and run GUI
    gui = create_gui()
    gui.run()
