"""Main dashboard component for the Weather Dashboard application.

This module provides the main tabbed interface and coordinates between
different weather dashboard sections and components.
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, Optional

from ...core.weather_service import WeatherService
from ...models.weather_models import WeatherData
from ..animations.effects import AnimationHelper
from ..styles.glassmorphic import GlassmorphicFrame, GlassmorphicStyle
from ..widgets.enhanced_button import ButtonFactory
from ..widgets.modern_button import IconButton, ModernButton
from .responsive_layout import ResponsiveLayoutManager, ResponsiveSpacing
from .search_panel import SearchPanel
from .weather_card import WeatherCard


class MainDashboard(GlassmorphicFrame):
    """Main dashboard with tabbed interface for weather information."""

    def __init__(
        self,
        parent,
        weather_service: Optional[WeatherService] = None,
        on_search: Optional[Callable[[str], None]] = None,
        on_add_favorite: Optional[Callable[[str], None]] = None,
        on_tab_change: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        """Initialize main dashboard.

        Args:
            parent: Parent widget
            weather_service: Weather service instance
            on_search: Callback for search actions
            on_add_favorite: Callback for adding favorites
            on_tab_change: Callback for tab changes
            **kwargs: Additional frame configuration
        """
        super().__init__(parent, **kwargs)

        self.style = GlassmorphicStyle()
        self.animation = AnimationHelper()
        self.logger = logging.getLogger(__name__)

        # Initialize responsive layout components
        self.button_factory = ButtonFactory()

        # Services
        self.weather_service = weather_service
        self.poetry_service = None
        self.journal_service = None
        self.activity_service = None
        self.comparison_service = None
        self.voice_service = None

        # Components
        self.weather_card: Optional[WeatherCard] = None
        self.search_panel: Optional[SearchPanel] = None
        self.notebook: Optional[ttk.Notebook] = None

        # Tabs
        self.current_tab: Optional[tk.Frame] = None
        self.forecast_tab: Optional[tk.Frame] = None
        self.comparison_tab: Optional[tk.Frame] = None
        self.journal_tab: Optional[tk.Frame] = None
        self.activities_tab: Optional[tk.Frame] = None
        self.poetry_tab: Optional[tk.Frame] = None
        self.voice_tab: Optional[tk.Frame] = None
        self.favorites_tab: Optional[tk.Frame] = None

        # State
        self.current_weather: Optional[WeatherData] = None
        self.is_loading = False

        # Callbacks
        self.on_weather_update: Optional[Callable[[WeatherData], None]] = None
        self.on_location_change: Optional[Callable[[str], None]] = None
        self.on_search_callback = on_search
        self.on_add_favorite_callback = on_add_favorite
        self.on_tab_change_callback = on_tab_change

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the main dashboard user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main container with responsive spacing
        main_container = tk.Frame(self, bg=self.style.colors["background"])
        main_container.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=ResponsiveSpacing.CONTAINER_PADDING,
            pady=ResponsiveSpacing.CONTAINER_PADDING,
        )
        main_container.grid_columnconfigure(1, weight=1)
        main_container.grid_rowconfigure(0, weight=1)

        # Left panel (search and weather card)
        self._create_left_panel(main_container)

        # Right panel (tabbed content)
        self._create_right_panel(main_container)

    def _create_left_panel(self, parent) -> None:
        """Create left panel with search and weather card.

        Args:
            parent: Parent widget
        """
        left_panel = GlassmorphicFrame(parent, padding=ResponsiveSpacing.ELEMENT_SPACING)
        left_panel.grid(
            row=0, column=0, sticky="nsew", padx=(0, ResponsiveSpacing.ELEMENT_SPACING)
        )
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)

        # Configure fixed width for left panel
        left_panel.config(width=350)
        left_panel.grid_propagate(False)

        # Search panel
        self.search_panel = SearchPanel(
            left_panel,
            on_search=self._handle_search,
            on_favorite_add=self._handle_favorite_add,
        )
        self.search_panel.grid(
            row=0, column=0, sticky="ew", pady=(0, ResponsiveSpacing.ELEMENT_SPACING)
        )

        # Weather card
        self.weather_card = WeatherCard(left_panel)
        self.weather_card.grid(row=1, column=0, sticky="nsew")

    def _create_right_panel(self, parent) -> None:
        """Create right panel with tabbed content.

        Args:
            parent: Parent widget
        """
        right_panel = GlassmorphicFrame(parent, padding=ResponsiveSpacing.ELEMENT_SPACING)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(0, weight=1)

        # Create notebook for tabs
        self._create_notebook(right_panel)

        # Create all tabs
        self._create_all_tabs()

    def _create_notebook(self, parent) -> None:
        """Create notebook widget for tabs.

        Args:
            parent: Parent widget
        """
        # Configure ttk style for notebook
        style = ttk.Style()
        style.theme_use("clam")

        # Configure notebook styling
        style.configure(
            "Custom.TNotebook",
            background=self.style.colors["surface"],
            borderwidth=0,
            tabmargins=[2, 5, 2, 0],
        )

        style.configure(
            "Custom.TNotebook.Tab",
            background=self.style.colors["surface"],
            foreground=self.style.colors["text_primary"],
            padding=[12, 8],
            font=self.style.fonts["body"],
        )

        style.map(
            "Custom.TNotebook.Tab",
            background=[
                ("selected", self.style.colors["accent"]),
                ("active", self.style.colors["surface_hover"]),
            ],
            foreground=[
                ("selected", self.style.colors["text_primary"]),
                ("active", self.style.colors["text_primary"]),
            ],
        )

        # Create notebook
        self.notebook = ttk.Notebook(parent, style="Custom.TNotebook")
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Bind events
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def initialize_services(self, container) -> None:
        """Initialize services from the dependency container.

        Args:
            container: Dependency injection container with all services
        """
        try:
            # Import interface types
            from ...business.interfaces import (
                IWeatherService,
                IWeatherPoetryService,
                IWeatherJournalService,
                IActivitySuggestionService,
                ICityComparisonService,
                ICortanaVoiceService,
            )
            
            # Inject services
            self.weather_service = container.get_service(IWeatherService)
            self.poetry_service = container.get_service(IWeatherPoetryService)
            self.journal_service = container.get_service(IWeatherJournalService)
            self.activity_service = container.get_service(IActivitySuggestionService)
            self.comparison_service = container.get_service(ICityComparisonService)
            self.voice_service = container.get_service(ICortanaVoiceService)
            
            # Connect search panel to weather service
            if hasattr(self.search_panel, 'set_weather_service'):
                self.search_panel.set_weather_service(self.weather_service)
                
        except Exception as e:
            print(f"Failed to initialize services in MainDashboard: {e}")

    def _create_all_tabs(self) -> None:
        """Create all dashboard tabs."""
        # Current Weather Tab
        self._create_current_tab()

        # Forecast Tab
        self._create_forecast_tab()

        # Comparison Tab
        self._create_comparison_tab()

        # Journal Tab
        self._create_journal_tab()

        # Activities Tab
        self._create_activities_tab()

        # Poetry Tab
        self._create_poetry_tab()

        # Voice Assistant Tab
        self._create_voice_tab()

        # Favorites Tab
        self._create_favorites_tab()

    def _create_current_tab(self) -> None:
        """Create current weather tab."""
        self.current_tab = tk.Frame(self.notebook, bg=self.style.colors["surface"])
        self.notebook.add(self.current_tab, text="🌤️ Current")

        # Current weather content
        content_frame = GlassmorphicFrame(self.current_tab, padding=20)
        content_frame.pack(
            fill="both", expand=True, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.MEDIUM
        )

        # Title
        title_label = tk.Label(
            content_frame,
            text="Current Weather Details",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Placeholder for detailed current weather info
        self._create_current_weather_details(content_frame)

    def _create_current_weather_details(self, parent) -> None:
        """Create detailed current weather information.

        Args:
            parent: Parent widget
        """
        details_frame = tk.Frame(parent, bg=self.style.colors["surface"])
        details_frame.pack(fill="both", expand=True)
        details_frame.grid_columnconfigure((0, 1), weight=1)

        # Extended weather details will be populated here
        placeholder_label = tk.Label(
            details_frame,
            text="Select a location to view detailed weather information",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
            wraplength=400,
        )
        placeholder_label.grid(row=0, column=0, columnspan=2, pady=50)

    def _create_forecast_tab(self) -> None:
        """Create forecast tab."""
        self.forecast_tab = tk.Frame(self.notebook, bg=self.style.colors["surface"])
        self.notebook.add(self.forecast_tab, text="📅 Forecast")

        # Forecast content
        content_frame = GlassmorphicFrame(self.forecast_tab, padding=20)
        content_frame.pack(
            fill="both", expand=True, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.MEDIUM
        )

        title_label = tk.Label(
            content_frame,
            text="Weather Forecast",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, 20))

        # Placeholder for forecast content
        placeholder_label = tk.Label(
            content_frame,
            text="7-day weather forecast will be displayed here",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        )
        placeholder_label.pack(pady=50)

    def _create_comparison_tab(self) -> None:
        """Create comparison tab."""
        self.comparison_tab = tk.Frame(self.notebook, bg=self.style.colors["surface"])
        self.notebook.add(self.comparison_tab, text="⚖️ Compare")

        content_frame = GlassmorphicFrame(self.comparison_tab, padding=20)
        content_frame.pack(
            fill="both", expand=True, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.MEDIUM
        )

        title_label = tk.Label(
            content_frame,
            text="City Weather Comparison",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, 20))

        placeholder_label = tk.Label(
            content_frame,
            text="Compare weather between multiple cities",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        )
        placeholder_label.pack(pady=50)

    def _create_journal_tab(self) -> None:
        """Create weather journal tab."""
        self.journal_tab = tk.Frame(self.notebook, bg=self.style.colors["surface"])
        self.notebook.add(self.journal_tab, text="📔 Journal")

        content_frame = GlassmorphicFrame(self.journal_tab, padding=20)
        content_frame.pack(
            fill="both", expand=True, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.MEDIUM
        )

        title_label = tk.Label(
            content_frame,
            text="Weather Journal",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, 20))

        placeholder_label = tk.Label(
            content_frame,
            text="Track weather patterns and personal observations",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        )
        placeholder_label.pack(pady=50)

    def _create_activities_tab(self) -> None:
        """Create activities tab."""
        self.activities_tab = tk.Frame(self.notebook, bg=self.style.colors["surface"])
        self.notebook.add(self.activities_tab, text="🏃 Activities")

        content_frame = GlassmorphicFrame(self.activities_tab, padding=20)
        content_frame.pack(
            fill="both", expand=True, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.MEDIUM
        )

        title_label = tk.Label(
            content_frame,
            text="Weather-Based Activities",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, 20))

        placeholder_label = tk.Label(
            content_frame,
            text="Discover activities based on current weather conditions",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        )
        placeholder_label.pack(pady=50)

    def _create_poetry_tab(self) -> None:
        """Create poetry tab."""
        self.poetry_tab = tk.Frame(self.notebook, bg=self.style.colors["surface"])
        self.notebook.add(self.poetry_tab, text="🎭 Poetry")

        content_frame = GlassmorphicFrame(self.poetry_tab, padding=20)
        content_frame.pack(
            fill="both", expand=True, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.MEDIUM
        )

        title_label = tk.Label(
            content_frame,
            text="Weather Poetry",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, 20))

        placeholder_label = tk.Label(
            content_frame,
            text="AI-generated poetry inspired by current weather",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        )
        placeholder_label.pack(pady=50)

    def _create_voice_tab(self) -> None:
        """Create voice assistant tab."""
        self.voice_tab = tk.Frame(self.notebook, bg=self.style.colors["surface"])
        self.notebook.add(self.voice_tab, text="🎤 Voice")

        content_frame = GlassmorphicFrame(self.voice_tab, padding=20)
        content_frame.pack(
            fill="both", expand=True, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.MEDIUM
        )

        title_label = tk.Label(
            content_frame,
            text="Voice Assistant",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, 20))

        placeholder_label = tk.Label(
            content_frame,
            text="Voice-controlled weather queries and commands",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        )
        placeholder_label.pack(pady=50)

    def _create_favorites_tab(self) -> None:
        """Create favorites tab."""
        self.favorites_tab = tk.Frame(self.notebook, bg=self.style.colors["surface"])
        self.notebook.add(self.favorites_tab, text="⭐ Favorites")

        content_frame = GlassmorphicFrame(self.favorites_tab, padding=20)
        content_frame.pack(
            fill="both", expand=True, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.MEDIUM
        )

        title_label = tk.Label(
            content_frame,
            text="Favorite Locations",
            font=self.style.fonts["heading"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_primary"],
        )
        title_label.pack(anchor="w", pady=(0, 20))

        placeholder_label = tk.Label(
            content_frame,
            text="Quick access to your favorite weather locations",
            font=self.style.fonts["body"],
            bg=self.style.colors["surface"],
            fg=self.style.colors["text_secondary"],
        )
        placeholder_label.pack(pady=50)

    def _handle_search(self, city: str) -> None:
        """Handle weather search request.

        Args:
            city: City name to search for
        """
        self.logger.info(f"Searching weather for: {city}")

        # Call the search callback if provided
        if self.on_search_callback:
            self.on_search_callback(city)
        elif not self.weather_service:
            self.logger.error("Weather service not available")
            return
        else:
            # Set loading state
            self.set_loading_state(True)

            try:
                # Use actual weather service
                self._fetch_weather_data(city)

            except Exception as e:
                self.logger.error(f"Error fetching weather: {e}")
                self.set_loading_state(False)

    def _fetch_weather_data(self, city: str) -> None:
        """Fetch weather data using the weather service.

        Args:
            city: City name
        """
        try:
            # Get current weather
            weather_data = self.weather_service.get_current_weather(city)
            
            if weather_data:
                # Update the dashboard with real weather data
                self.update_weather_data(weather_data)
                
                # Call location change callback
                if self.on_location_change:
                    self.on_location_change(city)
                    
                # Get forecast data if available
                try:
                    forecast_data = self.weather_service.get_forecast(city)
                    if forecast_data:
                        self.update_forecast_data(forecast_data)
                except Exception as e:
                    self.logger.warning(f"Failed to get forecast data: {e}")
            else:
                self.logger.warning(f"No weather data returned for {city}")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch weather data: {e}")
            # Show error to user
            if hasattr(self, 'show_error'):
                self.show_error(f"Failed to get weather for {city}: {e}")
        finally:
            self.set_loading_state(False)

    def _simulate_weather_fetch(self, city: str) -> None:
        """Simulate weather data fetching.

        Args:
            city: City name
        """
        # This would be replaced with actual weather service call
        # For now, create placeholder weather data

        # Simulate loading delay
        self.after(1000, lambda: self._handle_weather_response(city))

    def _handle_weather_response(self, city: str) -> None:
        """Handle weather service response.

        Args:
            city: City name that was searched
        """
        # This would handle actual weather data
        # For now, just clear loading state
        self.set_loading_state(False)

        # Call location change callback
        if self.on_location_change:
            self.on_location_change(city)

    def _handle_favorite_add(self, city: str) -> None:
        """Handle adding city to favorites.

        Args:
            city: City name to add to favorites
        """
        self.logger.info(f"Added to favorites: {city}")

        # Call the add favorite callback if provided
        if self.on_add_favorite_callback:
            self.on_add_favorite_callback(city)

        # Update favorites tab if needed
        # This would refresh the favorites display

    def _on_tab_changed(self, event) -> None:
        """Handle tab change event.

        Args:
            event: Tab change event
        """
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text")
        self.logger.debug(f"Tab changed to: {tab_text}")

        # Call the tab change callback if provided
        if self.on_tab_change_callback:
            # Extract just the tab name without emoji
            tab_name = tab_text.split()[-1].lower() if tab_text else ""
            self.on_tab_change_callback(tab_name)

        # Apply tab change animation
        current_frame = self.notebook.nametowidget(selected_tab)
        self.animation.fade_in(current_frame, duration=300)

    def update_weather_data(self, weather_data: WeatherData) -> None:
        """Update dashboard with new weather data.

        Args:
            weather_data: New weather data
        """
        self.current_weather = weather_data

        # Update weather card
        if self.weather_card:
            self.weather_card.update_weather(weather_data)

        # Call update callback
        if self.on_weather_update:
            self.on_weather_update(weather_data)

        self.logger.info(f"Updated weather data for {weather_data.location.name}")

    def set_loading_state(self, loading: bool) -> None:
        """Set dashboard loading state.

        Args:
            loading: Whether dashboard is loading
        """
        self.is_loading = loading

        # Update weather card loading state
        if self.weather_card:
            self.weather_card.set_loading_state(loading)

        # Disable/enable search during loading
        if self.search_panel and hasattr(self.search_panel, "search_button"):
            self.search_panel.search_button.set_enabled(not loading)
            if loading:
                self.search_panel.search_button.set_loading(True, "Searching...")
            else:
                self.search_panel.search_button.set_loading(False)

    def clear_weather_data(self) -> None:
        """Clear current weather data."""
        self.current_weather = None

        if self.weather_card:
            self.weather_card.clear_weather()

    def update_forecast_data(self, forecast):
        """Update dashboard with new forecast data.

        Args:
            forecast: Weather forecast data
        """
        self.logger.info("Updating forecast data in main dashboard")
        # Store forecast data for future use
        # This method can be expanded to update forecast-related UI components

    def on_temperature_unit_change(self, new_unit):
        """Handle temperature unit change.

        Args:
            new_unit: New temperature unit
        """
        self.logger.info(f"Temperature unit changed to: {new_unit.value}")

        # Update weather card if it exists and has weather data
        if self.weather_card and self.current_weather:
            # Refresh the weather card display with new unit
            self.weather_card.update_weather(self.current_weather)

        # Update any other components that display temperature
        # This can be expanded as more temperature-displaying components are added

    def get_current_tab(self) -> str:
        """Get currently selected tab name.

        Returns:
            Current tab name
        """
        if self.notebook:
            selected_tab = self.notebook.select()
            return self.notebook.tab(selected_tab, "text")
        return ""

    def switch_to_tab(self, tab_name: str) -> None:
        """Switch to specified tab.

        Args:
            tab_name: Name of tab to switch to
        """
        if not self.notebook:
            return

        # Find tab by name
        for tab_id in self.notebook.tabs():
            if tab_name in self.notebook.tab(tab_id, "text"):
                self.notebook.select(tab_id)
                break

    def export_dashboard_state(self) -> Dict[str, Any]:
        """Export current dashboard state.

        Returns:
            Dictionary containing dashboard state
        """
        state = {
            "current_tab": self.get_current_tab(),
            "is_loading": self.is_loading,
            "has_weather_data": self.current_weather is not None,
        }

        # Add search panel state
        if self.search_panel:
            state["search_data"] = self.search_panel.export_search_data()

        # Add weather card state
        if self.weather_card and self.current_weather:
            state["weather_data"] = self.weather_card.export_weather_data()

        return state

    def update_responsive_layout(self) -> None:
        """Update layout based on current window size."""
        if hasattr(self, "responsive_layout"):
            self.responsive_layout.update_layout()

            # Spacing values are accessed directly from ResponsiveSpacing class

            # Trigger layout updates for child components
            if self.search_panel and hasattr(
                self.search_panel, "update_responsive_layout"
            ):
                self.search_panel.update_responsive_layout()

            if self.weather_card and hasattr(
                self.weather_card, "update_responsive_layout"
            ):
                self.weather_card.update_responsive_layout()
