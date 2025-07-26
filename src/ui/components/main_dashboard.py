"""Main dashboard component for the Weather Dashboard application.

This module provides the main tabbed interface and coordinates between
different weather dashboard sections and components.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Dict, Any, Callable
import logging

from ..styles.glassmorphic import GlassmorphicStyle, GlassmorphicFrame
from .weather_card import WeatherCard
from .search_panel import SearchPanel
from ..widgets.modern_button import ModernButton, IconButton
from ..animations.effects import AnimationHelper
from ...models.weather_models import WeatherData
from ...core.weather_service import WeatherService


class MainDashboard(GlassmorphicFrame):
    """Main dashboard with tabbed interface for weather information."""

    def __init__(self, parent, weather_service: Optional[WeatherService] = None, **kwargs):
        """Initialize main dashboard.
        
        Args:
            parent: Parent widget
            weather_service: Weather service instance
            **kwargs: Additional frame configuration
        """
        super().__init__(parent, **kwargs)
        
        self.style = GlassmorphicStyle()
        self.animation = AnimationHelper()
        self.logger = logging.getLogger(__name__)
        
        # Services
        self.weather_service = weather_service
        
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
        
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the main dashboard user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Main container
        main_container = tk.Frame(self, bg=self.style.colors['background'])
        main_container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
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
        left_panel = GlassmorphicFrame(parent, padding=10)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)
        
        # Configure fixed width for left panel
        left_panel.config(width=350)
        left_panel.grid_propagate(False)
        
        # Search panel
        self.search_panel = SearchPanel(
            left_panel,
            on_search=self._handle_search,
            on_favorite_add=self._handle_favorite_add
        )
        self.search_panel.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Weather card
        self.weather_card = WeatherCard(left_panel)
        self.weather_card.grid(row=1, column=0, sticky="nsew")

    def _create_right_panel(self, parent) -> None:
        """Create right panel with tabbed content.
        
        Args:
            parent: Parent widget
        """
        right_panel = GlassmorphicFrame(parent, padding=10)
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
        style.theme_use('clam')
        
        # Configure notebook styling
        style.configure(
            'Custom.TNotebook',
            background=self.style.colors['surface'],
            borderwidth=0,
            tabmargins=[2, 5, 2, 0]
        )
        
        style.configure(
            'Custom.TNotebook.Tab',
            background=self.style.colors['surface'],
            foreground=self.style.colors['text_primary'],
            padding=[12, 8],
            font=self.style.fonts['body']
        )
        
        style.map(
            'Custom.TNotebook.Tab',
            background=[
                ('selected', self.style.colors['accent']),
                ('active', self.style.colors['surface_hover'])
            ],
            foreground=[
                ('selected', self.style.colors['text_primary']),
                ('active', self.style.colors['text_primary'])
            ]
        )
        
        # Create notebook
        self.notebook = ttk.Notebook(parent, style='Custom.TNotebook')
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

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
        self.current_tab = tk.Frame(
            self.notebook,
            bg=self.style.colors['surface']
        )
        self.notebook.add(self.current_tab, text="🌤️ Current")
        
        # Current weather content
        content_frame = GlassmorphicFrame(self.current_tab, padding=20)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text="Current Weather Details",
            font=self.style.fonts['heading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Placeholder for detailed current weather info
        self._create_current_weather_details(content_frame)

    def _create_current_weather_details(self, parent) -> None:
        """Create detailed current weather information.
        
        Args:
            parent: Parent widget
        """
        details_frame = tk.Frame(parent, bg=self.style.colors['surface'])
        details_frame.pack(fill="both", expand=True)
        details_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Extended weather details will be populated here
        placeholder_label = tk.Label(
            details_frame,
            text="Select a location to view detailed weather information",
            font=self.style.fonts['body'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_secondary'],
            wraplength=400
        )
        placeholder_label.grid(row=0, column=0, columnspan=2, pady=50)

    def _create_forecast_tab(self) -> None:
        """Create forecast tab."""
        self.forecast_tab = tk.Frame(
            self.notebook,
            bg=self.style.colors['surface']
        )
        self.notebook.add(self.forecast_tab, text="📅 Forecast")
        
        # Forecast content
        content_frame = GlassmorphicFrame(self.forecast_tab, padding=20)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = tk.Label(
            content_frame,
            text="Weather Forecast",
            font=self.style.fonts['heading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        # Placeholder for forecast content
        placeholder_label = tk.Label(
            content_frame,
            text="7-day weather forecast will be displayed here",
            font=self.style.fonts['body'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_secondary']
        )
        placeholder_label.pack(pady=50)

    def _create_comparison_tab(self) -> None:
        """Create comparison tab."""
        self.comparison_tab = tk.Frame(
            self.notebook,
            bg=self.style.colors['surface']
        )
        self.notebook.add(self.comparison_tab, text="⚖️ Compare")
        
        content_frame = GlassmorphicFrame(self.comparison_tab, padding=20)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = tk.Label(
            content_frame,
            text="City Weather Comparison",
            font=self.style.fonts['heading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        placeholder_label = tk.Label(
            content_frame,
            text="Compare weather between multiple cities",
            font=self.style.fonts['body'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_secondary']
        )
        placeholder_label.pack(pady=50)

    def _create_journal_tab(self) -> None:
        """Create weather journal tab."""
        self.journal_tab = tk.Frame(
            self.notebook,
            bg=self.style.colors['surface']
        )
        self.notebook.add(self.journal_tab, text="📔 Journal")
        
        content_frame = GlassmorphicFrame(self.journal_tab, padding=20)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = tk.Label(
            content_frame,
            text="Weather Journal",
            font=self.style.fonts['heading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        placeholder_label = tk.Label(
            content_frame,
            text="Track weather patterns and personal observations",
            font=self.style.fonts['body'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_secondary']
        )
        placeholder_label.pack(pady=50)

    def _create_activities_tab(self) -> None:
        """Create activities tab."""
        self.activities_tab = tk.Frame(
            self.notebook,
            bg=self.style.colors['surface']
        )
        self.notebook.add(self.activities_tab, text="🏃 Activities")
        
        content_frame = GlassmorphicFrame(self.activities_tab, padding=20)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = tk.Label(
            content_frame,
            text="Weather-Based Activities",
            font=self.style.fonts['heading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        placeholder_label = tk.Label(
            content_frame,
            text="Discover activities based on current weather conditions",
            font=self.style.fonts['body'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_secondary']
        )
        placeholder_label.pack(pady=50)

    def _create_poetry_tab(self) -> None:
        """Create poetry tab."""
        self.poetry_tab = tk.Frame(
            self.notebook,
            bg=self.style.colors['surface']
        )
        self.notebook.add(self.poetry_tab, text="🎭 Poetry")
        
        content_frame = GlassmorphicFrame(self.poetry_tab, padding=20)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = tk.Label(
            content_frame,
            text="Weather Poetry",
            font=self.style.fonts['heading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        placeholder_label = tk.Label(
            content_frame,
            text="AI-generated poetry inspired by current weather",
            font=self.style.fonts['body'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_secondary']
        )
        placeholder_label.pack(pady=50)

    def _create_voice_tab(self) -> None:
        """Create voice assistant tab."""
        self.voice_tab = tk.Frame(
            self.notebook,
            bg=self.style.colors['surface']
        )
        self.notebook.add(self.voice_tab, text="🎤 Voice")
        
        content_frame = GlassmorphicFrame(self.voice_tab, padding=20)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = tk.Label(
            content_frame,
            text="Voice Assistant",
            font=self.style.fonts['heading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        placeholder_label = tk.Label(
            content_frame,
            text="Voice-controlled weather queries and commands",
            font=self.style.fonts['body'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_secondary']
        )
        placeholder_label.pack(pady=50)

    def _create_favorites_tab(self) -> None:
        """Create favorites tab."""
        self.favorites_tab = tk.Frame(
            self.notebook,
            bg=self.style.colors['surface']
        )
        self.notebook.add(self.favorites_tab, text="⭐ Favorites")
        
        content_frame = GlassmorphicFrame(self.favorites_tab, padding=20)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title_label = tk.Label(
            content_frame,
            text="Favorite Locations",
            font=self.style.fonts['heading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary']
        )
        title_label.pack(anchor="w", pady=(0, 20))
        
        placeholder_label = tk.Label(
            content_frame,
            text="Quick access to your favorite weather locations",
            font=self.style.fonts['body'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_secondary']
        )
        placeholder_label.pack(pady=50)

    def _handle_search(self, city: str) -> None:
        """Handle weather search request.
        
        Args:
            city: City name to search for
        """
        self.logger.info(f"Searching weather for: {city}")
        
        if not self.weather_service:
            self.logger.error("Weather service not available")
            return
        
        # Set loading state
        self.set_loading_state(True)
        
        try:
            # Get weather data (this would be async in a real implementation)
            # For now, we'll create a placeholder
            self._simulate_weather_fetch(city)
            
        except Exception as e:
            self.logger.error(f"Error fetching weather: {e}")
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
        
        self.logger.info(f"Updated weather data for {weather_data.location.city}")

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
        if self.search_panel and hasattr(self.search_panel, 'search_button'):
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
            'current_tab': self.get_current_tab(),
            'is_loading': self.is_loading,
            'has_weather_data': self.current_weather is not None
        }
        
        # Add search panel state
        if self.search_panel:
            state['search_data'] = self.search_panel.export_search_data()
        
        # Add weather card state
        if self.weather_card and self.current_weather:
            state['weather_data'] = self.weather_card.export_weather_data()
        
        return state