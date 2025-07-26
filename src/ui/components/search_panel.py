"""Search panel component for city weather search functionality.

This module provides a comprehensive search interface with autocomplete,
recent searches, favorites management, and glassmorphic styling.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional, Dict, Any
import json
import os
from datetime import datetime

from ..styles.glassmorphic import GlassmorphicStyle, GlassmorphicFrame
from ..widgets.modern_button import ModernButton, IconButton
from ..animations.effects import AnimationHelper


class SearchPanel(GlassmorphicFrame):
    """City search panel with autocomplete and favorites."""

    def __init__(self, parent, on_search: Optional[Callable[[str], None]] = None,
                 on_favorite_add: Optional[Callable[[str], None]] = None,
                 **kwargs):
        """Initialize search panel.
        
        Args:
            parent: Parent widget
            on_search: Callback for search action
            on_favorite_add: Callback for adding to favorites
            **kwargs: Additional frame configuration
        """
        super().__init__(parent, **kwargs)
        
        self.style = GlassmorphicStyle()
        self.animation = AnimationHelper()
        
        # Callbacks
        self.on_search = on_search
        self.on_favorite_add = on_favorite_add
        
        # Data storage
        self.recent_searches: List[str] = []
        self.favorites: List[str] = []
        self.search_suggestions: List[str] = []
        
        # UI components
        self.search_entry: Optional[tk.Entry] = None
        self.search_button: Optional[ModernButton] = None
        self.favorite_button: Optional[IconButton] = None
        self.suggestions_listbox: Optional[tk.Listbox] = None
        self.recent_frame: Optional[tk.Frame] = None
        self.favorites_frame: Optional[tk.Frame] = None
        
        # State
        self.current_search = ""
        self.placeholder_text = "Enter city name..."
        self.is_placeholder_active = True
        
        # Load saved data
        self._load_saved_data()
        
        # Setup UI
        self._setup_ui()
        
        # Load popular cities for suggestions
        self._load_popular_cities()

    def _setup_ui(self) -> None:
        """Set up the search panel user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Main container
        main_container = tk.Frame(self, bg=self.style.colors['surface'])
        main_container.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="🔍 City Search",
            font=self.style.fonts['heading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary'],
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        # Search input section
        self._create_search_input(main_container, row=1)
        
        # Suggestions section
        self._create_suggestions_section(main_container, row=2)
        
        # Recent searches section
        self._create_recent_searches(main_container, row=3)
        
        # Favorites section
        self._create_favorites_section(main_container, row=4)

    def _create_search_input(self, parent, row: int) -> None:
        """Create search input section.
        
        Args:
            parent: Parent widget
            row: Grid row number
        """
        input_frame = tk.Frame(parent, bg=self.style.colors['surface'])
        input_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Search entry
        self.search_entry = tk.Entry(
            input_frame,
            font=self.style.fonts['body'],
            bg=self.style.colors['input_bg'],
            fg=self.style.colors['text_secondary'],
            insertbackground=self.style.colors['accent'],
            relief='flat',
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=self.style.colors['accent'],
            highlightbackground=self.style.colors['border']
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        # Set placeholder
        self._set_placeholder()
        
        # Bind events
        self.search_entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.search_entry.bind('<KeyRelease>', self._on_key_release)
        self.search_entry.bind('<Return>', self._on_search_enter)
        
        # Button frame
        button_frame = tk.Frame(input_frame, bg=self.style.colors['surface'])
        button_frame.grid(row=0, column=1)
        
        # Search button
        self.search_button = IconButton(
            button_frame,
            icon="🔍",
            text="Search",
            command=self._perform_search,
            style_variant="primary"
        )
        self.search_button.pack(side="left", padx=(0, 5))
        
        # Favorite button
        self.favorite_button = IconButton(
            button_frame,
            icon="⭐",
            text="",
            command=self._add_to_favorites,
            style_variant="secondary"
        )
        self.favorite_button.pack(side="left")

    def _create_suggestions_section(self, parent, row: int) -> None:
        """Create suggestions dropdown section.
        
        Args:
            parent: Parent widget
            row: Grid row number
        """
        suggestions_frame = tk.Frame(parent, bg=self.style.colors['surface'])
        suggestions_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        suggestions_frame.grid_columnconfigure(0, weight=1)
        
        # Suggestions listbox (initially hidden)
        self.suggestions_listbox = tk.Listbox(
            suggestions_frame,
            font=self.style.fonts['body'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary'],
            selectbackground=self.style.colors['accent'],
            selectforeground=self.style.colors['text_primary'],
            relief='flat',
            borderwidth=1,
            highlightthickness=0,
            height=0  # Initially hidden
        )
        self.suggestions_listbox.grid(row=0, column=0, sticky="ew")
        self.suggestions_listbox.bind('<Double-Button-1>', self._on_suggestion_select)
        self.suggestions_listbox.bind('<Return>', self._on_suggestion_select)

    def _create_recent_searches(self, parent, row: int) -> None:
        """Create recent searches section.
        
        Args:
            parent: Parent widget
            row: Grid row number
        """
        if not self.recent_searches:
            return
        
        recent_label = tk.Label(
            parent,
            text="📋 Recent Searches",
            font=self.style.fonts['subheading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary'],
            anchor="w"
        )
        recent_label.grid(row=row, column=0, sticky="ew", pady=(10, 5))
        
        self.recent_frame = tk.Frame(parent, bg=self.style.colors['surface'])
        self.recent_frame.grid(row=row+1, column=0, sticky="ew", pady=(0, 10))
        
        self._populate_recent_searches()

    def _create_favorites_section(self, parent, row: int) -> None:
        """Create favorites section.
        
        Args:
            parent: Parent widget
            row: Grid row number
        """
        favorites_label = tk.Label(
            parent,
            text="⭐ Favorites",
            font=self.style.fonts['subheading'],
            bg=self.style.colors['surface'],
            fg=self.style.colors['text_primary'],
            anchor="w"
        )
        favorites_label.grid(row=row, column=0, sticky="ew", pady=(10, 5))
        
        self.favorites_frame = tk.Frame(parent, bg=self.style.colors['surface'])
        self.favorites_frame.grid(row=row+1, column=0, sticky="ew")
        
        self._populate_favorites()

    def _set_placeholder(self) -> None:
        """Set placeholder text in search entry."""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, self.placeholder_text)
        self.search_entry.config(fg=self.style.colors['text_disabled'])
        self.is_placeholder_active = True

    def _clear_placeholder(self) -> None:
        """Clear placeholder text from search entry."""
        if self.is_placeholder_active:
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.style.colors['text_primary'])
            self.is_placeholder_active = False

    def _on_entry_focus_in(self, event) -> None:
        """Handle search entry focus in event."""
        self._clear_placeholder()

    def _on_entry_focus_out(self, event) -> None:
        """Handle search entry focus out event."""
        if not self.search_entry.get().strip():
            self._set_placeholder()
        self._hide_suggestions()

    def _on_key_release(self, event) -> None:
        """Handle key release in search entry."""
        if self.is_placeholder_active:
            return
        
        query = self.search_entry.get().strip()
        self.current_search = query
        
        if len(query) >= 2:
            self._show_suggestions(query)
        else:
            self._hide_suggestions()

    def _on_search_enter(self, event) -> None:
        """Handle Enter key in search entry."""
        self._perform_search()

    def _on_suggestion_select(self, event) -> None:
        """Handle suggestion selection."""
        selection = self.suggestions_listbox.curselection()
        if selection:
            city = self.suggestions_listbox.get(selection[0])
            self.search_entry.delete(0, tk.END)
            self.search_entry.insert(0, city)
            self.is_placeholder_active = False
            self.search_entry.config(fg=self.style.colors['text_primary'])
            self._hide_suggestions()
            self._perform_search()

    def _show_suggestions(self, query: str) -> None:
        """Show search suggestions.
        
        Args:
            query: Search query
        """
        # Filter suggestions based on query
        filtered_suggestions = [
            city for city in self.search_suggestions
            if query.lower() in city.lower()
        ][:5]  # Limit to 5 suggestions
        
        if filtered_suggestions:
            self.suggestions_listbox.delete(0, tk.END)
            for suggestion in filtered_suggestions:
                self.suggestions_listbox.insert(tk.END, suggestion)
            
            # Show listbox
            self.suggestions_listbox.config(height=min(len(filtered_suggestions), 5))
        else:
            self._hide_suggestions()

    def _hide_suggestions(self) -> None:
        """Hide search suggestions."""
        self.suggestions_listbox.config(height=0)

    def _perform_search(self) -> None:
        """Perform weather search."""
        if self.is_placeholder_active:
            return
        
        query = self.search_entry.get().strip()
        if not query:
            return
        
        # Add to recent searches
        self._add_to_recent(query)
        
        # Hide suggestions
        self._hide_suggestions()
        
        # Apply search animation
        self.animation.pulse(self.search_button)
        
        # Call search callback
        if self.on_search:
            self.on_search(query)

    def _add_to_favorites(self) -> None:
        """Add current search to favorites."""
        if self.is_placeholder_active:
            return
        
        query = self.search_entry.get().strip()
        if not query or query in self.favorites:
            return
        
        self.favorites.insert(0, query)
        if len(self.favorites) > 10:  # Limit favorites
            self.favorites = self.favorites[:10]
        
        self._save_data()
        self._populate_favorites()
        
        # Apply favorite animation
        self.animation.glow_effect(self.favorite_button, self.style.colors['accent'])
        
        # Call favorite callback
        if self.on_favorite_add:
            self.on_favorite_add(query)

    def _add_to_recent(self, city: str) -> None:
        """Add city to recent searches.
        
        Args:
            city: City name to add
        """
        if city in self.recent_searches:
            self.recent_searches.remove(city)
        
        self.recent_searches.insert(0, city)
        if len(self.recent_searches) > 5:  # Limit recent searches
            self.recent_searches = self.recent_searches[:5]
        
        self._save_data()
        self._populate_recent_searches()

    def _populate_recent_searches(self) -> None:
        """Populate recent searches section."""
        if not self.recent_frame:
            return
        
        # Clear existing widgets
        for widget in self.recent_frame.winfo_children():
            widget.destroy()
        
        # Add recent search buttons
        for i, city in enumerate(self.recent_searches[:5]):
            btn = ModernButton(
                self.recent_frame,
                text=city,
                command=lambda c=city: self._select_recent(c),
                style_variant="secondary"
            )
            btn.grid(row=i//2, column=i%2, sticky="ew", padx=2, pady=2)
        
        # Configure grid weights
        self.recent_frame.grid_columnconfigure((0, 1), weight=1)

    def _populate_favorites(self) -> None:
        """Populate favorites section."""
        if not self.favorites_frame:
            return
        
        # Clear existing widgets
        for widget in self.favorites_frame.winfo_children():
            widget.destroy()
        
        if not self.favorites:
            # Show empty state
            empty_label = tk.Label(
                self.favorites_frame,
                text="No favorites yet. Add cities using the ⭐ button!",
                font=self.style.fonts['caption'],
                bg=self.style.colors['surface'],
                fg=self.style.colors['text_disabled'],
                wraplength=200
            )
            empty_label.pack(pady=10)
            return
        
        # Add favorite buttons
        for i, city in enumerate(self.favorites[:8]):
            btn_frame = tk.Frame(self.favorites_frame, bg=self.style.colors['surface'])
            btn_frame.grid(row=i//2, column=i%2, sticky="ew", padx=2, pady=2)
            btn_frame.grid_columnconfigure(0, weight=1)
            
            # City button
            city_btn = ModernButton(
                btn_frame,
                text=city,
                command=lambda c=city: self._select_favorite(c),
                style_variant="accent"
            )
            city_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
            
            # Remove button
            remove_btn = IconButton(
                btn_frame,
                icon="❌",
                command=lambda c=city: self._remove_favorite(c),
                style_variant="secondary"
            )
            remove_btn.grid(row=0, column=1)
        
        # Configure grid weights
        self.favorites_frame.grid_columnconfigure((0, 1), weight=1)

    def _select_recent(self, city: str) -> None:
        """Select a recent search.
        
        Args:
            city: City name to select
        """
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, city)
        self.is_placeholder_active = False
        self.search_entry.config(fg=self.style.colors['text_primary'])
        self._perform_search()

    def _select_favorite(self, city: str) -> None:
        """Select a favorite city.
        
        Args:
            city: City name to select
        """
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, city)
        self.is_placeholder_active = False
        self.search_entry.config(fg=self.style.colors['text_primary'])
        self._perform_search()

    def _remove_favorite(self, city: str) -> None:
        """Remove a city from favorites.
        
        Args:
            city: City name to remove
        """
        if city in self.favorites:
            self.favorites.remove(city)
            self._save_data()
            self._populate_favorites()

    def _load_popular_cities(self) -> None:
        """Load popular cities for suggestions."""
        # Popular world cities for suggestions
        self.search_suggestions = [
            "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX",
            "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX", "San Diego, CA",
            "Dallas, TX", "San Jose, CA", "Austin, TX", "Jacksonville, FL",
            "London, UK", "Paris, France", "Tokyo, Japan", "Sydney, Australia",
            "Toronto, Canada", "Berlin, Germany", "Rome, Italy", "Madrid, Spain",
            "Amsterdam, Netherlands", "Vienna, Austria", "Prague, Czech Republic",
            "Stockholm, Sweden", "Copenhagen, Denmark", "Oslo, Norway",
            "Helsinki, Finland", "Dublin, Ireland", "Brussels, Belgium",
            "Zurich, Switzerland", "Barcelona, Spain", "Milan, Italy",
            "Munich, Germany", "Hamburg, Germany", "Frankfurt, Germany"
        ]

    def _load_saved_data(self) -> None:
        """Load saved search data from file."""
        try:
            data_file = os.path.join(os.path.expanduser("~"), ".weather_dashboard_search.json")
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.recent_searches = data.get('recent_searches', [])
                    self.favorites = data.get('favorites', [])
        except Exception:
            # If loading fails, start with empty lists
            self.recent_searches = []
            self.favorites = []

    def _save_data(self) -> None:
        """Save search data to file."""
        try:
            data_file = os.path.join(os.path.expanduser("~"), ".weather_dashboard_search.json")
            data = {
                'recent_searches': self.recent_searches,
                'favorites': self.favorites,
                'last_updated': datetime.now().isoformat()
            }
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception:
            # If saving fails, continue silently
            pass

    def clear_search(self) -> None:
        """Clear current search input."""
        self._set_placeholder()
        self._hide_suggestions()

    def set_search_text(self, text: str) -> None:
        """Set search input text.
        
        Args:
            text: Text to set in search input
        """
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, text)
        self.is_placeholder_active = False
        self.search_entry.config(fg=self.style.colors['text_primary'])

    def get_search_text(self) -> str:
        """Get current search input text.
        
        Returns:
            Current search text or empty string if placeholder is active
        """
        if self.is_placeholder_active:
            return ""
        return self.search_entry.get().strip()

    def export_search_data(self) -> Dict[str, Any]:
        """Export search data for backup.
        
        Returns:
            Dictionary containing search data
        """
        return {
            'recent_searches': self.recent_searches.copy(),
            'favorites': self.favorites.copy(),
            'export_timestamp': datetime.now().isoformat()
        }

    def import_search_data(self, data: Dict[str, Any]) -> None:
        """Import search data from backup.
        
        Args:
            data: Dictionary containing search data
        """
        if 'recent_searches' in data:
            self.recent_searches = data['recent_searches'][:5]  # Limit to 5
        
        if 'favorites' in data:
            self.favorites = data['favorites'][:10]  # Limit to 10
        
        self._save_data()
        self._populate_recent_searches()
        self._populate_favorites()