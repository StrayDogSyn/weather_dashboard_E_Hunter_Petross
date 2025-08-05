import customtkinter as ctk
from typing import List, Dict, Any, Optional, Callable
import tkinter as tk
from PIL import Image, ImageDraw
import math
import json
from pathlib import Path
import re

class ProfessionalSearchBar(ctk.CTkFrame):
    def __init__(self, parent, dashboard_ref=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.dashboard = dashboard_ref
        self.dropdown_visible = False
        self.suggestions = []
        self.selected_index = -1
        self.callbacks = {}
        self.tooltips = {}
        
        # Command patterns for smart search
        self.command_patterns = {
            'compare': re.compile(r'^compare:\s*(.+)', re.IGNORECASE),
            'analyze': re.compile(r'^analyze:\s*(.+)', re.IGNORECASE),
            'map': re.compile(r'^map:\s*(.+)', re.IGNORECASE),
            'weather': re.compile(r'^weather:\s*(.+)', re.IGNORECASE)
        }
        
        self.setup_search_interface()
        
    def setup_search_interface(self):
        """Create the professional search interface"""
        # Main search container with proper sizing
        self.search_container = ctk.CTkFrame(
            self,
            fg_color=("white", "gray20"),
            corner_radius=15,
            border_width=2,
            border_color=("gray70", "gray30"),
            height=60  # Fixed height for consistency
        )
        self.search_container.pack(fill="x", padx=20, pady=(15, 5))
        self.search_container.pack_propagate(False)  # Maintain fixed height
        
        # Search icon with better sizing
        self.search_icon = ctk.CTkLabel(
            self.search_container,
            text="🔍",
            font=("Helvetica", 20),  # Larger icon
            width=40
        )
        self.search_icon.pack(side="left", padx=(15, 5))
        
        # Professional search entry
        self.search_entry = ctk.CTkEntry(
            self.search_container,
            placeholder_text="Search city, use commands (compare:, analyze:), or press Ctrl+K for help",
            font=("Helvetica", 16),  # Much larger, readable font
            height=40,
            border_width=0,
            fg_color="transparent"
        )
        self.search_entry.pack(side="left", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # Quick action buttons frame
        self.actions_frame = ctk.CTkFrame(self.search_container, fg_color="transparent")
        self.actions_frame.pack(side="right", padx=(5, 15))
        
        # Favorites button with tooltip
        self.fav_button = ctk.CTkButton(
            self.actions_frame,
            text="⭐",
            width=35,
            height=35,
            font=("Helvetica", 18),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            command=self.toggle_favorites
        )
        self.fav_button.pack(side="left", padx=2)
        self.add_tooltip(self.fav_button, "Favorite Cities (Ctrl+F)")
        
        # Recent searches button
        self.recent_button = ctk.CTkButton(
            self.actions_frame,
            text="🕐",
            width=35,
            height=35,
            font=("Helvetica", 18),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            command=self.show_recent
        )
        self.recent_button.pack(side="left", padx=2)
        self.add_tooltip(self.recent_button, "Recent Searches (Ctrl+H)")
        
        # Command menu button
        self.cmd_button = ctk.CTkButton(
            self.actions_frame,
            text="⚡",
            width=35,
            height=35,
            font=("Helvetica", 18),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            command=self.show_commands
        )
        self.cmd_button.pack(side="left", padx=2)
        self.add_tooltip(self.cmd_button, "Quick Commands (Ctrl+/)")
        
        # Current location button
        self.location_button = ctk.CTkButton(
            self.actions_frame,
            text="📍",
            width=35,
            height=35,
            font=("Helvetica", 18),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            command=self.get_current_location
        )
        self.location_button.pack(side="left", padx=2)
        self.add_tooltip(self.location_button, "Use Current Location (Ctrl+L)")
        
        # Create collapsible dropdown (initially hidden)
        self.create_smart_dropdown()
        
        # Bind events
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        self.search_entry.bind("<Return>", self.on_search_submit)
        self.search_entry.bind("<Down>", self.navigate_down)
        self.search_entry.bind("<Up>", self.navigate_up)
        self.search_entry.bind("<Escape>", lambda e: self.hide_dropdown())
        self.search_entry.bind("<FocusOut>", self.on_focus_out)
        
        # Global shortcuts - use dashboard reference for global bindings
        if self.dashboard:
            self.dashboard.bind("<Control-k>", lambda e: self.search_entry.focus())
            self.dashboard.bind("<Control-slash>", lambda e: self.show_commands())
            self.dashboard.bind("<Control-l>", lambda e: self.get_current_location())
        
    def create_smart_dropdown(self):
        """Create the collapsible smart dropdown"""
        # Dropdown container (initially hidden)
        self.dropdown_frame = ctk.CTkFrame(
            self,
            fg_color=("white", "gray20"),
            corner_radius=15,
            border_width=2,
            border_color=("gray70", "gray30")
        )
        # Don't pack yet - will be shown when needed
        
        # Dropdown header with categories
        self.dropdown_header = ctk.CTkFrame(
            self.dropdown_frame,
            fg_color="transparent",
            height=40
        )
        
        # Category tabs
        self.categories = ["All", "Cities", "Commands", "Recent", "Favorites"]
        self.category_buttons = []
        self.active_category = "All"
        
        for cat in self.categories:
            btn = ctk.CTkButton(
                self.dropdown_header,
                text=cat,
                width=80,
                height=30,
                font=("Helvetica", 12),
                fg_color="transparent",
                hover_color=("gray80", "gray30"),
                command=lambda c=cat: self.switch_category(c)
            )
            btn.pack(side="left", padx=2)
            self.category_buttons.append(btn)
        
        # Scrollable frame for suggestions
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.dropdown_frame,
            fg_color="transparent",
            height=250,  # Max height before scrolling
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray50", "gray40")
        )
        
        # Status bar at bottom
        self.status_frame = ctk.CTkFrame(
            self.dropdown_frame,
            fg_color=("gray95", "gray25"),
            height=30
        )
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Type to search or use commands like 'compare: London, Paris'",
            font=("Helvetica", 11),
            text_color=("gray60", "gray40")
        )
        self.status_label.pack(pady=5)
        
    def show_dropdown(self):
        """Show the smart dropdown with animation"""
        if not self.dropdown_visible:
            self.dropdown_frame.pack(fill="x", padx=20, pady=(0, 15))
            self.dropdown_header.pack(fill="x", padx=10, pady=(10, 5))
            self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
            self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
            self.dropdown_visible = True
            self.update_category_buttons()
            
    def hide_dropdown(self):
        """Hide the dropdown"""
        if self.dropdown_visible:
            self.dropdown_frame.pack_forget()
            self.dropdown_visible = False
            
    def on_search_change(self, event=None):
        """Handle search input changes"""
        query = self.search_entry.get().strip()
        
        if len(query) >= 2:
            self.show_dropdown()
            self.update_suggestions(query)
        elif len(query) == 0:
            self.hide_dropdown()
            
    def update_suggestions(self, query: str):
        """Update dropdown suggestions based on query"""
        # Clear existing suggestions
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        suggestions = self.get_smart_suggestions(query)
        
        for i, suggestion in enumerate(suggestions[:10]):  # Limit to 10 items
            self.create_suggestion_item(suggestion, i)
            
    def get_smart_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get intelligent suggestions based on query"""
        suggestions = []
        
        # Check for command patterns
        for cmd, pattern in self.command_patterns.items():
            if pattern.match(query):
                suggestions.extend(self.get_command_suggestions(cmd, query))
                return suggestions
        
        # Regular city search
        if self.active_category in ["All", "Cities"]:
            suggestions.extend(self.get_city_suggestions(query))
            
        # Command suggestions
        if self.active_category in ["All", "Commands"]:
            suggestions.extend(self.get_available_commands(query))
            
        # Recent searches
        if self.active_category in ["All", "Recent"]:
            suggestions.extend(self.get_recent_suggestions(query))
            
        # Favorites
        if self.active_category in ["All", "Favorites"]:
            suggestions.extend(self.get_favorite_suggestions(query))
            
        return suggestions
        
    def get_city_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get city suggestions"""
        cities = [
            "London, UK", "Paris, France", "New York, USA", "Tokyo, Japan",
            "Sydney, Australia", "Berlin, Germany", "Rome, Italy", "Madrid, Spain",
            "Amsterdam, Netherlands", "Vienna, Austria", "Prague, Czech Republic",
            "Stockholm, Sweden", "Copenhagen, Denmark", "Oslo, Norway"
        ]
        
        matching_cities = [city for city in cities if query.lower() in city.lower()]
        return [{
            'type': 'city',
            'text': city,
            'icon': '🌍',
            'description': f'Get weather for {city}'
        } for city in matching_cities]
        
    def get_command_suggestions(self, cmd: str, query: str) -> List[Dict[str, Any]]:
        """Get suggestions for specific commands"""
        if cmd == 'compare':
            return [{
                'type': 'command',
                'text': 'compare: London, Paris, Berlin',
                'icon': '⚖️',
                'description': 'Compare weather between multiple cities'
            }]
        elif cmd == 'analyze':
            return [{
                'type': 'command',
                'text': 'analyze: New York, Tokyo',
                'icon': '📊',
                'description': 'Analyze weather patterns and trends'
            }]
        elif cmd == 'map':
            return [{
                'type': 'command',
                'text': 'map: Europe',
                'icon': '🗺️',
                'description': 'Show weather map for region'
            }]
        return []
        
    def get_available_commands(self, query: str) -> List[Dict[str, Any]]:
        """Get available command suggestions"""
        commands = [
            {'cmd': 'compare:', 'desc': 'Compare multiple cities', 'icon': '⚖️'},
            {'cmd': 'analyze:', 'desc': 'Analyze weather patterns', 'icon': '📊'},
            {'cmd': 'map:', 'desc': 'Show weather map', 'icon': '🗺️'},
            {'cmd': 'weather:', 'desc': 'Get detailed weather', 'icon': '🌤️'}
        ]
        
        matching = [cmd for cmd in commands if query.lower() in cmd['cmd'].lower()]
        return [{
            'type': 'command',
            'text': cmd['cmd'],
            'icon': cmd['icon'],
            'description': cmd['desc']
        } for cmd in matching]
        
    def get_recent_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get recent search suggestions"""
        # Mock recent searches - in real app, load from storage
        recent = ["London", "Paris", "New York", "Tokyo"]
        matching = [city for city in recent if query.lower() in city.lower()]
        return [{
            'type': 'recent',
            'text': city,
            'icon': '🕐',
            'description': f'Recent search: {city}'
        } for city in matching]
        
    def get_favorite_suggestions(self, query: str) -> List[Dict[str, Any]]:
        """Get favorite city suggestions"""
        # Mock favorites - in real app, load from storage
        favorites = ["London", "Berlin", "Amsterdam"]
        matching = [city for city in favorites if query.lower() in city.lower()]
        return [{
            'type': 'favorite',
            'text': city,
            'icon': '⭐',
            'description': f'Favorite: {city}'
        } for city in matching]
        
    def create_suggestion_item(self, suggestion: Dict[str, Any], index: int):
        """Create a suggestion item in the dropdown"""
        item_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="transparent",
            height=50
        )
        item_frame.pack(fill="x", pady=1)
        item_frame.pack_propagate(False)
        
        # Make the frame clickable
        item_frame.bind("<Button-1>", lambda e: self.select_suggestion(suggestion))
        
        # Icon
        icon_label = ctk.CTkLabel(
            item_frame,
            text=suggestion['icon'],
            font=("Helvetica", 16),
            width=30
        )
        icon_label.pack(side="left", padx=(10, 5))
        icon_label.bind("<Button-1>", lambda e: self.select_suggestion(suggestion))
        
        # Text content frame
        text_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, padx=5)
        text_frame.bind("<Button-1>", lambda e: self.select_suggestion(suggestion))
        
        # Main text
        main_label = ctk.CTkLabel(
            text_frame,
            text=suggestion['text'],
            font=("Helvetica", 14, "bold"),
            anchor="w"
        )
        main_label.pack(anchor="w")
        main_label.bind("<Button-1>", lambda e: self.select_suggestion(suggestion))
        
        # Description
        desc_label = ctk.CTkLabel(
            text_frame,
            text=suggestion['description'],
            font=("Helvetica", 11),
            text_color=("gray60", "gray40"),
            anchor="w"
        )
        desc_label.pack(anchor="w")
        desc_label.bind("<Button-1>", lambda e: self.select_suggestion(suggestion))
        
        # Hover effects
        def on_enter(e):
            item_frame.configure(fg_color=("gray90", "gray30"))
            
        def on_leave(e):
            item_frame.configure(fg_color="transparent")
            
        for widget in [item_frame, icon_label, text_frame, main_label, desc_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            
    def select_suggestion(self, suggestion: Dict[str, Any]):
        """Handle suggestion selection"""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, suggestion['text'])
        self.hide_dropdown()
        self.on_search_submit()
        
    def switch_category(self, category: str):
        """Switch active category"""
        self.active_category = category
        self.update_category_buttons()
        query = self.search_entry.get().strip()
        if query:
            self.update_suggestions(query)
            
    def update_category_buttons(self):
        """Update category button appearance"""
        for i, btn in enumerate(self.category_buttons):
            if self.categories[i] == self.active_category:
                btn.configure(fg_color=("blue", "blue"), text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=("black", "white"))
                
    def on_search_submit(self, event=None):
        """Handle search submission"""
        query = self.search_entry.get().strip()
        if not query:
            return
            
        # Check for command patterns
        for cmd, pattern in self.command_patterns.items():
            match = pattern.match(query)
            if match:
                self.execute_command(cmd, match.group(1))
                return
                
        # Regular weather search
        self.execute_weather_search(query)
        
    def execute_command(self, command: str, params: str):
        """Execute a specific command"""
        if command in self.callbacks:
            self.callbacks[command](params)
        elif self.dashboard:
            # Fallback to dashboard methods
            if hasattr(self.dashboard, f'handle_{command}_search'):
                getattr(self.dashboard, f'handle_{command}_search')(params)
                
    def execute_weather_search(self, query: str):
        """Execute regular weather search"""
        if 'weather' in self.callbacks:
            self.callbacks['weather'](query)
        elif self.dashboard and hasattr(self.dashboard, 'handle_weather_search'):
            self.dashboard.handle_weather_search(query)
            
    def navigate_down(self, event):
        """Navigate down in suggestions"""
        if self.dropdown_visible:
            # Implementation for keyboard navigation
            pass
            
    def navigate_up(self, event):
        """Navigate up in suggestions"""
        if self.dropdown_visible:
            # Implementation for keyboard navigation
            pass
            
    def on_focus_out(self, event):
        """Handle focus out event"""
        # Delay hiding to allow for clicks
        self.after(100, self.check_focus)
        
    def check_focus(self):
        """Check if focus is still within search components"""
        focused = self.focus_get()
        if focused not in [self.search_entry] and not self.is_child_of_dropdown(focused):
            self.hide_dropdown()
            
    def is_child_of_dropdown(self, widget) -> bool:
        """Check if widget is child of dropdown"""
        if not widget:
            return False
        parent = widget.master
        while parent:
            if parent == self.dropdown_frame:
                return True
            parent = parent.master
        return False
        
    def toggle_favorites(self):
        """Toggle favorites display"""
        self.active_category = "Favorites"
        self.show_dropdown()
        self.update_suggestions("")
        
    def show_recent(self):
        """Show recent searches"""
        self.active_category = "Recent"
        self.show_dropdown()
        self.update_suggestions("")
        
    def show_commands(self):
        """Show available commands"""
        self.active_category = "Commands"
        self.show_dropdown()
        self.update_suggestions("")
        
    def get_current_location(self):
        """Get user's current location and search for weather"""
        try:
            if self.dashboard:
                # Try to get current location from browser geolocation
                self.search_entry.delete(0, 'end')
                self.search_entry.insert(0, "Getting current location...")
                self.search_entry.configure(state="disabled")
                
                # Use browser geolocation API through the dashboard
                if hasattr(self.dashboard, '_get_user_location'):
                    self.dashboard._get_user_location(self._on_location_received)
                else:
                    # Fallback: use a default location or show error
                    self._on_location_error("Geolocation not available")
            else:
                self._on_location_error("Dashboard reference not available")
        except Exception as e:
            self._on_location_error(f"Error getting location: {str(e)}")
    
    def _on_location_received(self, lat, lng):
        """Handle received location coordinates"""
        try:
            # Re-enable search entry
            self.search_entry.configure(state="normal")
            self.search_entry.delete(0, 'end')
            
            # Use reverse geocoding to get city name
            location_name = f"{lat:.4f}, {lng:.4f}"  # Fallback to coordinates
            
            # Try to get city name from coordinates if dashboard has the capability
            if hasattr(self.dashboard, '_reverse_geocode'):
                self.dashboard._reverse_geocode(lat, lng, self._on_city_name_received)
            else:
                # Use coordinates directly
                self.search_entry.insert(0, location_name)
                self._trigger_search()
        except Exception as e:
            self._on_location_error(f"Error processing location: {str(e)}")
    
    def _on_city_name_received(self, city_name):
        """Handle received city name from reverse geocoding"""
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, city_name)
        self._trigger_search()
    
    def _on_location_error(self, error_msg):
        """Handle location error"""
        self.search_entry.configure(state="normal")
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, f"Location error: {error_msg}")
        # Clear error message after 3 seconds
        self.after(3000, lambda: self.search_entry.delete(0, 'end') if self.search_entry.get().startswith("Location error:") else None)
    
    def _trigger_search(self):
        """Trigger search with current entry value"""
        if self.dashboard and hasattr(self.dashboard, '_enhanced_search_weather'):
            self.dashboard._enhanced_search_weather()
        elif self.dashboard and hasattr(self.dashboard, '_search_weather'):
            self.dashboard._search_weather()
        
    def add_tooltip(self, widget, text: str):
        """Add tooltip to widget"""
        def on_enter(event):
            # Simple tooltip implementation
            self.status_label.configure(text=text)
            
        def on_leave(event):
            self.status_label.configure(text="Type to search or use commands like 'compare: London, Paris'")
            
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
        
    def register_callback(self, command: str, callback: Callable):
        """Register callback for command"""
        self.callbacks[command] = callback
        
    def set_placeholder(self, text: str):
        """Set placeholder text"""
        self.search_entry.configure(placeholder_text=text)
        
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_entry.get().strip()
        
    def clear_search(self):
        """Clear search entry"""
        self.search_entry.delete(0, tk.END)
        self.hide_dropdown()