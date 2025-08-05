import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
import json
from pathlib import Path
from datetime import datetime
import re
import threading
import time

class EnhancedSearchBar(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.search_callbacks = {}  # Feature-specific callbacks
        self.search_history = self.load_search_history()
        self.favorites = self.load_favorites()
        self.command_patterns = self.init_command_patterns()
        self.selected_cities = []  # For multi-city selection
        self.autocomplete_visible = False
        
        self.setup_ui()
        self.bind_shortcuts()
    
    def setup_ui(self):
        """Create the compact search interface"""
        # Ultra-minimal search container
        self.search_container = ctk.CTkFrame(self, fg_color="transparent")
        self.search_container.pack(fill="x", padx=0, pady=0)
        
        # Ultra-minimal search entry
        self.search_entry = ctk.CTkEntry(
            self.search_container,
            placeholder_text="Search",
            width=100,
            height=20,
            font=("Helvetica", 8),
            fg_color=("gray98", "gray18"),
            border_width=0,
            corner_radius=2
        )
        self.search_entry.pack(side="left", padx=1)
        
        # Bind events
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        self.search_entry.bind("<Return>", self.on_search_submit)
        self.search_entry.bind("<Control-space>", self.show_command_menu)
        self.search_entry.bind("<FocusOut>", self.on_focus_out)
        
        # Ultra-minimal action buttons
        self.action_frame = ctk.CTkFrame(self.search_container, fg_color="transparent")
        self.action_frame.pack(side="left", padx=0)
        
        # Tiny favorites button
        self.fav_button = ctk.CTkButton(
            self.action_frame,
            text="★",
            width=16,
            height=16,
            font=("Helvetica", 7),
            fg_color="transparent",
            hover_color=("gray90", "gray20"),
            command=self.toggle_favorites_menu
        )
        self.fav_button.pack(side="left", padx=0)
        
        # Tiny history button
        self.history_button = ctk.CTkButton(
            self.action_frame,
            text="⏰",
            width=16,
            height=16,
            font=("Helvetica", 7),
            fg_color="transparent",
            hover_color=("gray90", "gray20"),
            command=self.show_history_menu
        )
        self.history_button.pack(side="left", padx=0)
        
        # Hidden status label (only shows when needed)
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=("Helvetica", 8),
            text_color="gray",
            height=0
        )
        # Don't pack by default - only show when needed
        
        # Selected cities display
        self.selected_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.selected_frame.pack(fill="x", padx=4, pady=(0, 2))
        
        # Autocomplete dropdown (initially hidden)
        self.create_autocomplete_dropdown()
        
    def init_command_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize command recognition patterns"""
        return {
            'compare': re.compile(r'^compare:\s*(.+)$', re.IGNORECASE),
            'analyze': re.compile(r'^analyze:\s*(.+)$', re.IGNORECASE),
            'map': re.compile(r'^map:\s*(.+)$', re.IGNORECASE),
            'weather': re.compile(r'^weather:\s*(.+)$', re.IGNORECASE),
            'activity': re.compile(r'^activity:\s*(.+)$', re.IGNORECASE),
            'journal': re.compile(r'^journal:\s*(.+)$', re.IGNORECASE),
            'find': re.compile(r'^find\s+(.+?)\s+cities?$', re.IGNORECASE),
            'rainy': re.compile(r'rainy|rain|precipitation', re.IGNORECASE),
            'sunny': re.compile(r'sunny|sun|clear', re.IGNORECASE),
            'cold': re.compile(r'cold|freezing|below\s*\d+', re.IGNORECASE),
            'hot': re.compile(r'hot|warm|above\s*\d+', re.IGNORECASE)
        }
    
    def create_autocomplete_dropdown(self):
        """Create the ultra-compact autocomplete dropdown menu"""
        self.autocomplete_frame = ctk.CTkFrame(
            self,
            fg_color=("gray95", "gray15"),
            border_width=1,
            corner_radius=2
        )
        
        # Ultra-compact scrollable frame for suggestions
        self.suggestions_frame = ctk.CTkScrollableFrame(
            self.autocomplete_frame,
            height=60,  # Much smaller - only 60px
            fg_color="transparent"
        )
        self.suggestions_frame.pack(fill="both", expand=True, padx=1, pady=1)  # Minimal padding
        
    def on_search_change(self, event=None):
        """Handle search input changes with smart detection"""
        query = self.search_entry.get().strip()
        
        if not query:
            self.hide_autocomplete()
            self.update_status("")
            return
        
        # Check for command patterns
        for cmd_name, pattern in self.command_patterns.items():
            if pattern.match(query):
                self.handle_command_preview(cmd_name, query)
                return
        
        # Check for natural language patterns
        if self.detect_natural_language(query):
            return
        
        # Show autocomplete suggestions
        suggestions = self.get_suggestions(query)
        if suggestions:
            self.show_autocomplete(suggestions)
        else:
            self.hide_autocomplete()
    
    def detect_natural_language(self, query: str) -> bool:
        """Detect and handle natural language queries"""
        query_lower = query.lower()
        
        if any(pattern.search(query) for pattern in [self.command_patterns['rainy'], 
                                                     self.command_patterns['sunny'],
                                                     self.command_patterns['cold'],
                                                     self.command_patterns['hot']]):
            self.update_status(f"Natural language query detected: '{query}'")
            return True
        
        if "show me" in query_lower or "find" in query_lower:
            self.update_status(f"Processing natural language: '{query}'")
            return True
        
        return False
    
    def handle_command_preview(self, command: str, query: str):
        """Show preview of command execution"""
        if command == 'compare':
            match = self.command_patterns['compare'].match(query)
            if match:
                cities = [c.strip() for c in match.group(1).split(',')]
                self.update_status(f"Ready to compare: {', '.join(cities)}")
        
        elif command == 'analyze':
            match = self.command_patterns['analyze'].match(query)
            if match:
                target = match.group(1).strip()
                self.update_status(f"Ready to analyze: {target}")
        
        elif command == 'map':
            match = self.command_patterns['map'].match(query)
            if match:
                location = match.group(1).strip()
                self.update_status(f"Ready to show map: {location}")
        
        self.hide_autocomplete()
    
    def on_search_submit(self, event=None):
        """Handle search submission"""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        # Add to search history
        self.add_to_history(query)
        
        # Check for commands first
        for cmd_name, pattern in self.command_patterns.items():
            if pattern.match(query):
                self.execute_command(cmd_name, query)
                return
        
        # Check for natural language
        if self.detect_and_execute_natural_language(query):
            return
        
        # Regular city search
        if self.multi_select_var.get():
            self.add_to_selection(query)
        else:
            self.execute_city_search(query)
    
    def execute_command(self, command: str, query: str):
        """Execute recognized commands"""
        if command == 'compare':
            match = self.command_patterns['compare'].match(query)
            if match:
                cities = [c.strip() for c in match.group(1).split(',')]
                self.execute_compare(cities)
        
        elif command == 'analyze':
            match = self.command_patterns['analyze'].match(query)
            if match:
                cities = [c.strip() for c in match.group(1).split(',')]
                self.execute_analysis(cities)
        
        elif command == 'map':
            match = self.command_patterns['map'].match(query)
            if match:
                location = match.group(1).strip()
                self.execute_map_view(location)
        
        elif command == 'weather':
            match = self.command_patterns['weather'].match(query)
            if match:
                location = match.group(1).strip()
                self.execute_weather_search(location)
        
        self.search_entry.delete(0, 'end')
    
    def detect_and_execute_natural_language(self, query: str) -> bool:
        """Detect and execute natural language queries"""
        query_lower = query.lower()
        
        if self.command_patterns['rainy'].search(query):
            self.execute_weather_condition_search("rainy")
            return True
        elif self.command_patterns['sunny'].search(query):
            self.execute_weather_condition_search("sunny")
            return True
        elif self.command_patterns['cold'].search(query):
            self.execute_weather_condition_search("cold")
            return True
        elif self.command_patterns['hot'].search(query):
            self.execute_weather_condition_search("hot")
            return True
        
        return False
    
    def get_suggestions(self, query: str) -> List[str]:
        """Get autocomplete suggestions"""
        suggestions = []
        query_lower = query.lower()
        
        # Add command suggestions
        commands = ['compare:', 'analyze:', 'map:', 'weather:', 'activity:', 'journal:']
        for cmd in commands:
            if cmd.startswith(query_lower):
                suggestions.append(cmd)
        
        # Add recent searches
        if isinstance(self.search_history, list):
            for search in self.search_history[-10:]:
                if isinstance(search, str) and query_lower in search.lower() and search not in suggestions:
                    suggestions.append(search)
        
        # Add favorites
        if isinstance(self.favorites, list):
            for fav in self.favorites:
                if isinstance(fav, str) and query_lower in fav.lower() and fav not in suggestions:
                    suggestions.append(fav)
        
        # Add common cities
        common_cities = [
            "New York", "London", "Paris", "Tokyo", "Sydney", "Berlin",
            "Los Angeles", "Chicago", "Toronto", "Vancouver", "Madrid",
            "Rome", "Amsterdam", "Barcelona", "Vienna", "Prague"
        ]
        
        for city in common_cities:
            if query_lower in city.lower() and city not in suggestions:
                suggestions.append(city)
        
        return suggestions[:5]  # Limit to 5 suggestions for compact display
    
    def show_autocomplete(self, suggestions: List[str]):
        """Display ultra-compact autocomplete suggestions"""
        # Clear previous suggestions
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        # Limit to only 3 suggestions for ultra-compact design
        limited_suggestions = suggestions[:3]
        
        # Add new suggestions with minimal styling
        for suggestion in limited_suggestions:
            btn = ctk.CTkButton(
                self.suggestions_frame,
                text=suggestion,
                height=16,  # Very small height
                anchor="w",
                font=("Helvetica", 8),  # Very small font
                fg_color="transparent",
                hover_color=("gray85", "gray25"),
                command=lambda s=suggestion: self.select_suggestion(s)
            )
            btn.pack(fill="x", pady=0)  # No padding
        
        # Ultra-compact dynamic height
        dynamic_height = min(len(limited_suggestions) * 18 + 4, 60)  # Max 60px
        self.suggestions_frame.configure(height=dynamic_height)
        
        # Position and show autocomplete - smaller width
        self.autocomplete_frame.configure(width=min(self.search_entry.winfo_width(), 120))
        self.autocomplete_frame.place(
            in_=self.search_entry,
            x=0,
            y=self.search_entry.winfo_height() + 1
        )
        self.autocomplete_visible = True
    
    def hide_autocomplete(self):
        """Hide autocomplete dropdown"""
        if hasattr(self, 'autocomplete_frame'):
            self.autocomplete_frame.place_forget()
        self.autocomplete_visible = False
    
    def select_suggestion(self, suggestion: str):
        """Handle suggestion selection"""
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, suggestion)
        self.hide_autocomplete()
        self.search_entry.focus()
    
    def on_focus_out(self, event=None):
        """Handle focus out event"""
        # Delay hiding to allow button clicks
        self.after(100, self.hide_autocomplete)
    
    def show_command_menu(self, event=None):
        """Show command shortcuts menu"""
        commands = [
            "compare: city1, city2, city3",
            "analyze: location",
            "map: location",
            "weather: location",
            "find rainy cities",
            "show me sunny places"
        ]
        self.show_autocomplete(commands)
    
    def toggle_favorites_menu(self):
        """Toggle favorites menu"""
        if self.favorites:
            self.show_autocomplete(self.favorites)
        else:
            self.update_status("No favorites saved yet")
    
    def show_history_menu(self):
        """Show search history menu"""
        if isinstance(self.search_history, list) and self.search_history:
            recent = self.search_history[-10:]  # Last 10 searches
            self.show_autocomplete(recent)
        else:
            self.update_status("No search history available")
    
    def toggle_multi_select(self):
        """Toggle multi-city selection mode"""
        if self.multi_select_var.get():
            self.update_status("Multi-city mode enabled. Add cities to compare.")
            self.update_selected_display()
        else:
            self.selected_cities.clear()
            self.update_status("Multi-city mode disabled.")
            self.update_selected_display()
    
    def add_to_selection(self, city: str):
        """Add city to multi-selection"""
        if city not in self.selected_cities:
            self.selected_cities.append(city)
            self.update_status(f"Added {city} to selection ({len(self.selected_cities)} cities)")
            self.update_selected_display()
            self.search_entry.delete(0, 'end')
    
    def update_selected_display(self):
        """Update the display of selected cities"""
        # Clear previous display
        for widget in self.selected_frame.winfo_children():
            widget.destroy()
        
        if not self.selected_cities:
            return
        
        # Create city tags
        for i, city in enumerate(self.selected_cities):
            city_frame = ctk.CTkFrame(self.selected_frame)
            city_frame.pack(side="left", padx=2, pady=2)
            
            city_label = ctk.CTkLabel(city_frame, text=city, font=("Helvetica", 12))
            city_label.pack(side="left", padx=5)
            
            remove_btn = ctk.CTkButton(
                city_frame,
                text="×",
                width=20,
                height=20,
                command=lambda idx=i: self.remove_from_selection(idx)
            )
            remove_btn.pack(side="left", padx=(0, 5))
        
        # Add compare button if multiple cities
        if len(self.selected_cities) > 1:
            compare_btn = ctk.CTkButton(
                self.selected_frame,
                text=f"Compare {len(self.selected_cities)} Cities",
                command=self.compare_selected_cities
            )
            compare_btn.pack(side="left", padx=10)
    
    def remove_from_selection(self, index: int):
        """Remove city from selection"""
        if 0 <= index < len(self.selected_cities):
            removed = self.selected_cities.pop(index)
            self.update_status(f"Removed {removed} from selection")
            self.update_selected_display()
    
    def compare_selected_cities(self):
        """Compare all selected cities"""
        if len(self.selected_cities) > 1:
            self.execute_compare(self.selected_cities.copy())
            self.selected_cities.clear()
            self.update_selected_display()
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts"""
        # Note: bind_all is not supported in customtkinter
        # Keyboard shortcuts will be handled through the search entry focus
        self.search_entry.bind("<Control-h>", lambda e: self.show_history_menu())
        self.search_entry.bind("<Control-m>", lambda e: self.multi_select_var.set(not self.multi_select_var.get()))
        self.search_entry.bind("<Escape>", lambda e: self.clear_search())
    
    def update_status(self, message: str, duration: int = 3000):
        """Update status message with auto-clear"""
        self.status_label.configure(text=message)
        if message and duration > 0:
            self.after(duration, lambda: self.status_label.configure(text=""))
    
    # Execution methods for different features
    def execute_compare(self, cities: List[str]):
        """Execute city comparison"""
        self.update_status(f"Comparing {len(cities)} cities: {', '.join(cities)}")
        if 'compare' in self.search_callbacks:
            self.search_callbacks['compare'](cities)
    
    def execute_analysis(self, cities: List[str]):
        """Execute AI analysis"""
        self.update_status(f"Analyzing: {', '.join(cities)}")
        if 'analyze' in self.search_callbacks:
            self.search_callbacks['analyze'](cities)
    
    def execute_map_view(self, location: str):
        """Execute map view"""
        self.update_status(f"Opening map for: {location}")
        if 'map' in self.search_callbacks:
            self.search_callbacks['map'](location)
    
    def execute_weather_search(self, location: str):
        """Execute weather search"""
        self.update_status(f"Getting weather for: {location}")
        if 'weather' in self.search_callbacks:
            self.search_callbacks['weather'](location)
    
    def execute_city_search(self, city: str):
        """Execute regular city search"""
        self.update_status(f"Searching for: {city}")
        if 'search' in self.search_callbacks:
            self.search_callbacks['search'](city)
    
    def execute_weather_condition_search(self, condition: str):
        """Execute weather condition search"""
        self.update_status(f"Finding {condition} cities...")
        if 'condition' in self.search_callbacks:
            self.search_callbacks['condition'](condition)
    
    # Data management methods
    def load_search_history(self) -> List[str]:
        """Load search history from file"""
        try:
            history_file = Path("data/search_history.json")
            if history_file.exists():
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def load_favorites(self) -> List[str]:
        """Load favorites from file"""
        try:
            favorites_file = Path("data/favorite_locations.json")
            if favorites_file.exists():
                with open(favorites_file, 'r') as f:
                    data = json.load(f)
                    return [item.get('name', '') for item in data if 'name' in item]
        except Exception:
            pass
        return []
    
    def add_to_history(self, query: str):
        """Add query to search history"""
        if not isinstance(self.search_history, list):
            self.search_history = []
        if query not in self.search_history:
            self.search_history.append(query)
            # Keep only last 50 searches
            if len(self.search_history) > 50:
                self.search_history = self.search_history[-50:]
            self.save_search_history()
    
    def save_search_history(self):
        """Save search history to file"""
        try:
            history_file = Path("data/search_history.json")
            history_file.parent.mkdir(exist_ok=True)
            with open(history_file, 'w') as f:
                json.dump(self.search_history, f, indent=2)
        except Exception:
            pass
    
    def add_to_favorites(self, city: str):
        """Add city to favorites"""
        if city not in self.favorites:
            self.favorites.append(city)
            self.update_status(f"Added {city} to favorites")
    
    def register_callback(self, feature: str, callback: Callable):
        """Register callback for specific feature"""
        self.search_callbacks[feature] = callback
    
    def get_selected_cities(self) -> List[str]:
        """Get currently selected cities"""
        return self.selected_cities.copy()
    
    def clear_selection(self):
        """Clear all selected cities"""
        self.selected_cities.clear()
        self.update_selected_display()
    
    def set_placeholder(self, text: str):
        """Update placeholder text"""
        self.search_entry.configure(placeholder_text=text)