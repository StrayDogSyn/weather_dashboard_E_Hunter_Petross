"""
Modern TKinter GUI with Glassmorphic Design for Weather Dashboard.

This module provides a modern, glassmorphic user interface using TKinter
with custom styling and modern visual elements.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkFont
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, date
import threading
# Removed PIL import for now - can be added back later for advanced features
import json

from src.interfaces.weather_interfaces import IUserInterface
from models import CurrentWeather, WeatherForecast, FavoriteCity
from models.capstone_models import (
    WeatherComparison, JournalEntry, ActivitySuggestion, WeatherPoem, MoodType
)
from config import config_manager


class GlassmorphicStyle:
    """Custom styling for glassmorphic design."""
    
    # Color scheme
    BACKGROUND = "#0f0f0f"  # Dark base
    GLASS_BG = "#1a1a1a"   # Glass background
    GLASS_BORDER = "#333333"  # Glass border
    ACCENT = "#4a9eff"     # Blue accent
    ACCENT_SECONDARY = "#ff6b4a"  # Orange accent
    TEXT_PRIMARY = "#ffffff"   # White text
    TEXT_SECONDARY = "#b0b0b0"  # Gray text
    SUCCESS = "#4ade80"    # Green
    WARNING = "#fbbf24"    # Yellow
    ERROR = "#ef4444"      # Red
    
    # Glassmorphic properties
    BLUR_RADIUS = 10
    TRANSPARENCY = 0.1
    BORDER_RADIUS = 12
    
    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_LARGE = 16
    FONT_SIZE_MEDIUM = 12
    FONT_SIZE_SMALL = 10


class GlassmorphicFrame(tk.Frame):
    """Custom frame with glassmorphic styling."""
    
    def __init__(self, parent, bg_color=None, border_color=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.bg_color = bg_color or GlassmorphicStyle.GLASS_BG
        self.border_color = border_color or GlassmorphicStyle.GLASS_BORDER
        
        self.configure(
            bg=self.bg_color,
            highlightbackground=self.border_color,
            highlightcolor=self.border_color,
            highlightthickness=1,
            relief="flat"
        )


class ModernButton(tk.Button):
    """Modern styled button with hover effects."""
    
    def __init__(self, parent, style="primary", **kwargs):
        self.style = style
        self.default_bg = self._get_bg_color()
        self.hover_bg = self._get_hover_color()
        
        super().__init__(
            parent,
            bg=self.default_bg,
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=10,
            cursor="hand2",
            **kwargs
        )
        
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
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
            return "#5ba3ff"
        elif base == GlassmorphicStyle.ACCENT_SECONDARY:
            return "#ff7a5a"
        elif base == GlassmorphicStyle.SUCCESS:
            return "#5de690"
        elif base == GlassmorphicStyle.WARNING:
            return "#fcc534"
        elif base == GlassmorphicStyle.ERROR:
            return "#f56565"
        else:
            return "#2a2a2a"
    
    def _on_enter(self, event):
        self.configure(bg=self.hover_bg)
    
    def _on_leave(self, event):
        self.configure(bg=self.default_bg)


class WeatherCard(GlassmorphicFrame):
    """Weather information card with glassmorphic styling."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_layout()
    
    def setup_layout(self):
        """Setup the card layout."""
        # Title
        self.title_label = tk.Label(
            self,
            text="Weather",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_LARGE, "bold"),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=self.bg_color
        )
        self.title_label.pack(pady=(10, 5))
        
        # Content frame
        self.content_frame = tk.Frame(self, bg=self.bg_color)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
    
    def update_weather(self, weather: CurrentWeather):
        """Update the card with weather data."""
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Location
        location_label = tk.Label(
            self.content_frame,
            text=weather.location.display_name,
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM, "bold"),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=self.bg_color
        )
        location_label.pack(pady=(0, 10))
        
        # Temperature
        temp_text = f"{weather.temperature.to_celsius():.1f}°C"
        temp_label = tk.Label(
            self.content_frame,
            text=temp_text,
            font=(GlassmorphicStyle.FONT_FAMILY, 24, "bold"),
            fg=GlassmorphicStyle.ACCENT,
            bg=self.bg_color
        )
        temp_label.pack()
        
        # Condition
        condition_label = tk.Label(
            self.content_frame,
            text=weather.description.title(),
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color
        )
        condition_label.pack(pady=(5, 10))
        
        # Additional info
        info_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        info_frame.pack(fill=tk.X)
        
        # Humidity
        humidity_label = tk.Label(
            info_frame,
            text=f"💧 {weather.humidity}%",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color
        )
        humidity_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Wind
        wind_label = tk.Label(
            info_frame,
            text=f"💨 {weather.wind.speed}km/h",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color
        )
        wind_label.pack(side=tk.LEFT)


class ModernScrollableFrame(tk.Frame):
    """Scrollable frame with modern styling."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            self,
            bg=GlassmorphicStyle.BACKGROUND,
            highlightthickness=0
        )
        
        self.scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.canvas.yview
        )
        
        self.scrollable_frame = tk.Frame(
            self.canvas,
            bg=GlassmorphicStyle.BACKGROUND
        )
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
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
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind("<MouseWheel>", _on_mousewheel)


class WeatherDashboardGUI(IUserInterface):
    """Modern TKinter GUI for Weather Dashboard with glassmorphic design."""
    
    def __init__(self):
        """Initialize the GUI."""
        self.root = tk.Tk()
        self.config = config_manager.config
        self.current_weather = None
        self.setup_window()
        self.setup_styles()
        self.create_layout()
        
        # Callback storage
        self.callbacks = {}
        
    def setup_window(self):
        """Setup main window properties."""
        self.root.title("Weather Dashboard")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        self.root.configure(bg=GlassmorphicStyle.BACKGROUND)
        
        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def setup_styles(self):
        """Setup custom styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure ttk styles for dark theme
        style.configure('TNotebook', background=GlassmorphicStyle.BACKGROUND)
        style.configure('TNotebook.Tab', 
                       background=GlassmorphicStyle.GLASS_BG,
                       foreground=GlassmorphicStyle.TEXT_SECONDARY,
                       padding=[20, 10])
        style.map('TNotebook.Tab',
                 background=[('selected', GlassmorphicStyle.ACCENT)],
                 foreground=[('selected', GlassmorphicStyle.TEXT_PRIMARY)])
    
    def create_layout(self):
        """Create the main GUI layout."""
        # Header
        self.create_header()
        
        # Main content area with notebook
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create header section."""
        header_frame = GlassmorphicFrame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🌤️ Weather Dashboard",
            font=(GlassmorphicStyle.FONT_FAMILY, 24, "bold"),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=header_frame.bg_color
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Quick actions
        actions_frame = tk.Frame(header_frame, bg=header_frame.bg_color)
        actions_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.refresh_btn = ModernButton(
            actions_frame,
            text="🔄 Refresh",
            command=self.refresh_current_weather
        )
        self.refresh_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.search_btn = ModernButton(
            actions_frame,
            text="🔍 Search City",
            command=self.show_city_search
        )
        self.search_btn.pack(side=tk.RIGHT)
    
    def create_main_content(self):
        """Create main content area with tabbed interface."""
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
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
        """Create current weather tab."""
        weather_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(weather_frame, text="🌤️ Current Weather")
        
        # Main weather card
        self.main_weather_card = WeatherCard(weather_frame)
        self.main_weather_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Side panel with controls
        side_panel = GlassmorphicFrame(weather_frame)
        side_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=10)
        
        # City input
        tk.Label(
            side_panel,
            text="Enter City:",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=side_panel.bg_color
        ).pack(pady=(20, 5))
        
        self.city_entry = tk.Entry(
            side_panel,
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            bg=GlassmorphicStyle.GLASS_BG,
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            relief="flat",
            borderwidth=1
        )
        self.city_entry.pack(pady=(0, 10), padx=20, fill=tk.X)
        
        # Get weather button
        self.get_weather_btn = ModernButton(
            side_panel,
            text="Get Weather",
            command=self.get_weather_for_city
        )
        self.get_weather_btn.pack(pady=10)
        
        # Add to favorites button
        self.add_favorite_btn = ModernButton(
            side_panel,
            text="⭐ Add to Favorites",
            style="secondary",
            command=self.add_to_favorites
        )
        self.add_favorite_btn.pack(pady=5)
        
        # Bind Enter key to city entry
        self.city_entry.bind("<Return>", lambda e: self.get_weather_for_city())
    
    def create_forecast_tab(self):
        """Create forecast tab."""
        forecast_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(forecast_frame, text="📅 Forecast")
        
        # Scrollable forecast area
        self.forecast_scroll = ModernScrollableFrame(forecast_frame)
        self.forecast_scroll.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_comparison_tab(self):
        """Create city comparison tab."""
        comparison_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(comparison_frame, text="🌍 Compare Cities")
        
        # Controls
        controls_frame = GlassmorphicFrame(comparison_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # City inputs
        input_frame = tk.Frame(controls_frame, bg=controls_frame.bg_color)
        input_frame.pack(pady=20)
        
        tk.Label(
            input_frame,
            text="City 1:",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=controls_frame.bg_color
        ).grid(row=0, column=0, padx=(20, 10), pady=5, sticky="e")
        
        self.city1_entry = tk.Entry(
            input_frame,
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            bg=GlassmorphicStyle.GLASS_BG,
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            relief="flat",
            width=20
        )
        self.city1_entry.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(
            input_frame,
            text="City 2:",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=controls_frame.bg_color
        ).grid(row=0, column=2, padx=(30, 10), pady=5, sticky="e")
        
        self.city2_entry = tk.Entry(
            input_frame,
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            bg=GlassmorphicStyle.GLASS_BG,
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            relief="flat",
            width=20
        )
        self.city2_entry.grid(row=0, column=3, padx=10, pady=5)
        
        self.compare_btn = ModernButton(
            input_frame,
            text="🌍 Compare",
            command=self.compare_cities
        )
        self.compare_btn.grid(row=0, column=4, padx=(20, 20), pady=5)
        
        # Comparison results
        self.comparison_results = GlassmorphicFrame(comparison_frame)
        self.comparison_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
    
    def create_journal_tab(self):
        """Create weather journal tab."""
        journal_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(journal_frame, text="📔 Journal")
        
        # Controls
        controls_frame = GlassmorphicFrame(journal_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.new_entry_btn = ModernButton(
            controls_frame,
            text="📝 New Entry",
            command=self.create_journal_entry
        )
        self.new_entry_btn.pack(side=tk.LEFT, padx=20, pady=15)
        
        self.view_entries_btn = ModernButton(
            controls_frame,
            text="📖 View Entries",
            style="secondary",
            command=self.view_journal_entries
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
        controls_frame = GlassmorphicFrame(activities_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.get_activities_btn = ModernButton(
            controls_frame,
            text="🎯 Get Suggestions",
            command=self.get_activity_suggestions
        )
        self.get_activities_btn.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Activity filter buttons
        self.indoor_filter_btn = ModernButton(
            controls_frame,
            text="🏠 Indoor Only",
            style="secondary",
            command=lambda: self.filter_activities("indoor")
        )
        self.indoor_filter_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        self.outdoor_filter_btn = ModernButton(
            controls_frame,
            text="🌞 Outdoor Only",
            style="secondary",
            command=lambda: self.filter_activities("outdoor")
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
        controls_frame = GlassmorphicFrame(poetry_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.generate_poetry_btn = ModernButton(
            controls_frame,
            text="🎨 Generate Poetry",
            command=self.generate_poetry
        )
        self.generate_poetry_btn.pack(side=tk.LEFT, padx=20, pady=15)
        
        self.haiku_btn = ModernButton(
            controls_frame,
            text="🌸 Haiku",
            style="secondary",
            command=lambda: self.generate_specific_poetry("haiku")
        )
        self.haiku_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        self.phrase_btn = ModernButton(
            controls_frame,
            text="💭 Phrase",
            style="secondary",
            command=lambda: self.generate_specific_poetry("phrase")
        )
        self.phrase_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        # Poetry content
        self.poetry_content = GlassmorphicFrame(poetry_frame)
        self.poetry_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
    
    def create_favorites_tab(self):
        """Create favorites management tab."""
        favorites_frame = tk.Frame(self.notebook, bg=GlassmorphicStyle.BACKGROUND)
        self.notebook.add(favorites_frame, text="⭐ Favorites")
        
        # Controls
        controls_frame = GlassmorphicFrame(favorites_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.refresh_favorites_btn = ModernButton(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_favorites
        )
        self.refresh_favorites_btn.pack(side=tk.LEFT, padx=20, pady=15)
        
        self.view_all_weather_btn = ModernButton(
            controls_frame,
            text="🌍 View All Weather",
            style="secondary",
            command=self.view_all_favorites_weather
        )
        self.view_all_weather_btn.pack(side=tk.LEFT, padx=10, pady=15)
        
        # Favorites content
        self.favorites_content = ModernScrollableFrame(favorites_frame)
        self.favorites_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
    
    def create_status_bar(self):
        """Create status bar."""
        self.status_frame = GlassmorphicFrame(self.root)
        self.status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Ready",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.status_frame.bg_color
        )
        self.status_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Weather update time
        self.update_time_label = tk.Label(
            self.status_frame,
            text="",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.status_frame.bg_color
        )
        self.update_time_label.pack(side=tk.RIGHT, padx=15, pady=8)
    
    # Interface implementation methods
    def display_weather(self, weather_data: CurrentWeather) -> None:
        """Display current weather data."""
        self.current_weather = weather_data
        self.main_weather_card.update_weather(weather_data)
        self.update_status(f"Weather updated for {weather_data.location.display_name}")
        
        # Update timestamp
        if weather_data.timestamp:
            time_str = weather_data.timestamp.strftime("%H:%M")
            self.update_time_label.configure(text=f"Updated: {time_str}")
    
    def display_forecast(self, forecast_data: WeatherForecast) -> None:
        """Display forecast data."""
        # Clear existing forecast
        for widget in self.forecast_scroll.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create forecast cards
        for i, day in enumerate(forecast_data.forecast_days):
            day_card = self.create_forecast_card(self.forecast_scroll.scrollable_frame, day, i)
            day_card.pack(fill=tk.X, padx=10, pady=5)
    
    def create_forecast_card(self, parent, day_data, index):
        """Create a forecast day card."""
        card = GlassmorphicFrame(parent)
        
        # Day header
        day_name = day_data.date.strftime("%A")
        date_str = day_data.date.strftime("%m/%d")
        
        header_label = tk.Label(
            card,
            text=f"{day_name}, {date_str}",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM, "bold"),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=card.bg_color
        )
        header_label.pack(pady=(10, 5))
        
        # Temperature range
        temp_frame = tk.Frame(card, bg=card.bg_color)
        temp_frame.pack()
        
        high_temp = f"{day_data.temperature_high.to_celsius():.1f}°C"
        low_temp = f"{day_data.temperature_low.to_celsius():.1f}°C"
        
        tk.Label(
            temp_frame,
            text=f"H: {high_temp}",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            fg=GlassmorphicStyle.ACCENT,
            bg=card.bg_color
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(
            temp_frame,
            text=f"L: {low_temp}",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=card.bg_color
        ).pack(side=tk.LEFT, padx=10)
        
        # Condition
        condition_label = tk.Label(
            card,
            text=day_data.description.title(),
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=card.bg_color
        )
        condition_label.pack(pady=(5, 10))
        
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
        color = GlassmorphicStyle.ERROR if is_error else GlassmorphicStyle.TEXT_SECONDARY
        self.status_label.configure(text=message, fg=color)
        
        # Auto-clear status after 5 seconds
        self.root.after(5000, lambda: self.status_label.configure(
            text="Ready", 
            fg=GlassmorphicStyle.TEXT_SECONDARY
        ))
    
    # GUI-specific methods
    def get_weather_for_city(self):
        """Get weather for entered city."""
        city = self.city_entry.get().strip()
        if not city:
            self.show_error("Please enter a city name")
            return
        
        if 'get_weather' in self.callbacks:
            self.callbacks['get_weather'](city)
    
    def refresh_current_weather(self):
        """Refresh current weather."""
        if self.current_weather and 'get_weather' in self.callbacks:
            self.callbacks['get_weather'](self.current_weather.location.name)
    
    def show_city_search(self):
        """Show city search dialog."""
        city = simpledialog.askstring("Search", "Enter city name to search:")
        if city and 'search_locations' in self.callbacks:
            self.callbacks['search_locations'](city)
    
    def add_to_favorites(self):
        """Add current city to favorites."""
        if self.current_weather and 'add_favorite' in self.callbacks:
            self.callbacks['add_favorite'](self.current_weather.location.name)
    
    def compare_cities(self):
        """Compare two cities."""
        city1 = self.city1_entry.get().strip()
        city2 = self.city2_entry.get().strip()
        
        if not city1 or not city2:
            self.show_error("Please enter both city names")
            return
        
        if 'compare_cities' in self.callbacks:
            self.callbacks['compare_cities'](city1, city2)
    
    def create_journal_entry(self):
        """Create new journal entry."""
        if 'create_journal' in self.callbacks:
            self.callbacks['create_journal']()
    
    def view_journal_entries(self):
        """View journal entries."""
        if 'view_journal' in self.callbacks:
            self.callbacks['view_journal']()
    
    def get_activity_suggestions(self):
        """Get activity suggestions."""
        if 'get_activities' in self.callbacks:
            self.callbacks['get_activities']()
    
    def filter_activities(self, activity_type):
        """Filter activities by type."""
        if 'filter_activities' in self.callbacks:
            self.callbacks['filter_activities'](activity_type)
    
    def generate_poetry(self):
        """Generate weather poetry."""
        if 'generate_poetry' in self.callbacks:
            self.callbacks['generate_poetry']()
    
    def generate_specific_poetry(self, poetry_type):
        """Generate specific type of poetry."""
        if 'generate_specific_poetry' in self.callbacks:
            self.callbacks['generate_specific_poetry'](poetry_type)
    
    def refresh_favorites(self):
        """Refresh favorites list."""
        if 'refresh_favorites' in self.callbacks:
            self.callbacks['refresh_favorites']()
    
    def view_all_favorites_weather(self):
        """View weather for all favorites."""
        if 'view_favorites_weather' in self.callbacks:
            self.callbacks['view_favorites_weather']()
    
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
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_LARGE, "bold"),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=self.comparison_results.bg_color
        )
        title_label.pack(pady=(20, 10))
        
        # Create comparison cards
        comparison_frame = tk.Frame(self.comparison_results, bg=self.comparison_results.bg_color)
        comparison_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # City 1 card
        card1 = WeatherCard(comparison_frame)
        card1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        card1.update_weather(city1)
        
        # VS label
        vs_label = tk.Label(
            comparison_frame,
            text="VS",
            font=(GlassmorphicStyle.FONT_FAMILY, 20, "bold"),
            fg=GlassmorphicStyle.ACCENT,
            bg=self.comparison_results.bg_color
        )
        vs_label.pack(side=tk.LEFT, padx=20)
        
        # City 2 card
        card2 = WeatherCard(comparison_frame)
        card2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        card2.update_weather(city2)
        
        # Comparison summary
        summary_frame = tk.Frame(self.comparison_results, bg=self.comparison_results.bg_color)
        summary_frame.pack(fill=tk.X, padx=20, pady=20)
        
        better_city = comparison.better_weather_city
        summary_text = f"🏆 Better overall weather: {better_city}"
        
        summary_label = tk.Label(
            summary_frame,
            text=summary_text,
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM, "bold"),
            fg=GlassmorphicStyle.SUCCESS,
            bg=self.comparison_results.bg_color
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
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg=GlassmorphicStyle.BACKGROUND
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
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM, "bold"),
                fg=GlassmorphicStyle.SUCCESS,
                bg=top_frame.bg_color
            ).pack(pady=(15, 5))
            
            tk.Label(
                top_frame,
                text=top_activity.name,
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_LARGE, "bold"),
                fg=GlassmorphicStyle.TEXT_PRIMARY,
                bg=top_frame.bg_color
            ).pack()
            
            tk.Label(
                top_frame,
                text=top_activity.description,
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg=top_frame.bg_color
            ).pack(pady=(5, 10))
            
            tk.Label(
                top_frame,
                text=f"Suitability Score: {top_score:.1f}/10",
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
                fg=GlassmorphicStyle.ACCENT,
                bg=top_frame.bg_color
            ).pack(pady=(0, 15))
        
        # All suggestions
        all_frame = GlassmorphicFrame(self.activities_content.scrollable_frame)
        all_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(
            all_frame,
            text="💡 All Suggestions",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM, "bold"),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=all_frame.bg_color
        ).pack(pady=(15, 10))
        
        for i, (activity, score) in enumerate(suggestions.suggested_activities[1:], 2):
            activity_frame = tk.Frame(all_frame, bg=all_frame.bg_color)
            activity_frame.pack(fill=tk.X, padx=20, pady=2)
            
            icon = "🏠" if activity.indoor else "🌞"
            
            tk.Label(
                activity_frame,
                text=f"{i}. {icon} {activity.name}",
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
                fg=GlassmorphicStyle.TEXT_PRIMARY,
                bg=all_frame.bg_color
            ).pack(side=tk.LEFT)
            
            tk.Label(
                activity_frame,
                text=f"Score: {score:.1f}",
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
                fg=GlassmorphicStyle.ACCENT,
                bg=all_frame.bg_color
            ).pack(side=tk.RIGHT)
    
    def display_weather_poem(self, poem: WeatherPoem) -> None:
        """Display weather poem."""
        # Clear existing content
        for widget in self.poetry_content.winfo_children():
            widget.destroy()
        
        # Poem type title
        if poem.poem_type == "haiku":
            title = "🌸 Weather Haiku"
        elif poem.poem_type == "phrase":
            title = "💭 Weather Wisdom"
        elif poem.poem_type == "limerick":
            title = "🎵 Weather Limerick"
        else:
            title = "🎨 Weather Poetry"
        
        title_label = tk.Label(
            self.poetry_content,
            text=title,
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_LARGE, "bold"),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=self.poetry_content.bg_color
        )
        title_label.pack(pady=(20, 10))
        
        # Poem text
        if poem.poem_type == "haiku" and " / " in poem.text:
            lines = poem.text.split(" / ")
            for line in lines:
                line_label = tk.Label(
                    self.poetry_content,
                    text=line,
                    font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
                    fg=GlassmorphicStyle.TEXT_SECONDARY,
                    bg=self.poetry_content.bg_color
                )
                line_label.pack()
        else:
            poem_label = tk.Label(
                self.poetry_content,
                text=poem.text,
                font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_MEDIUM),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg=self.poetry_content.bg_color,
                wraplength=400,
                justify=tk.CENTER
            )
            poem_label.pack(pady=20)
        
        # Inspiration info
        info_label = tk.Label(
            self.poetry_content,
            text=f"📍 Inspired by: {poem.weather_condition.value.title()} weather\n🌡️ Temperature: {poem.temperature_range.title()}",
            font=(GlassmorphicStyle.FONT_FAMILY, GlassmorphicStyle.FONT_SIZE_SMALL),
            fg=GlassmorphicStyle.ACCENT,
            bg=self.poetry_content.bg_color,
            justify=tk.CENTER
        )
        info_label.pack(pady=(20, 0))
