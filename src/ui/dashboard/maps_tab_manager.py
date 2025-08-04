import customtkinter as ctk
from tkinter import ttk
from typing import Optional, Dict, Any, List, Callable
import logging
import threading
import time
import json
from datetime import datetime, timedelta
from .maps_config_manager import MapsConfigManager

# Import map dependencies with fallbacks
try:
    import tkintermapview
    TKINTER_MAPVIEW_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"tkintermapview not available: {e}")
    TKINTER_MAPVIEW_AVAILABLE = False

# Import our thread-safe components
try:
    from src.ui.maps.thread_safe_google_maps_widget import ThreadSafeGoogleMapsWidget
    from src.ui.maps.weather_controls_panel import WeatherControlsPanel
    from src.ui.maps.weather_map_overlay import WeatherPoint
    THREAD_SAFE_MAPS_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"Thread-safe maps not available: {e}")
    THREAD_SAFE_MAPS_AVAILABLE = False

# Overall maps availability
MAPS_AVAILABLE = TKINTER_MAPVIEW_AVAILABLE and THREAD_SAFE_MAPS_AVAILABLE

class ThreadSafeMapsTabManager:
    """Enhanced thread-safe maps tab manager with weather integration."""
    
    def __init__(self, parent, weather_service, config_service):
        self.parent = parent
        self.weather_service = weather_service
        self.config_service = config_service
        self.maps_config_manager = MapsConfigManager(config_service)
        self.logger = logging.getLogger(__name__)
        
        # Thread-safe components
        self.maps_widget = None
        self.weather_controls = None
        self._weather_update_thread = None
        self._shutdown_event = threading.Event()
        self._last_weather_update = None
        self._weather_update_interval = 30  # seconds
        
        # Public access to shutdown event for external cleanup
        self.shutdown_event = self._shutdown_event
        
        # Configuration management is handled by maps_config_manager
        
        # Performance optimization
        self._viewport_cache = {}
        self._tile_cache = {}
        self._update_throttle = {}
        
        # Initialize UI state
        self._is_loading = False
        self._fade_animation = None
        self._keyboard_shortcuts = {}
        self.is_active = False
        
        # Initialize caches
        self.weather_cache = {}
        self.last_weather_update = 0
        self.weather_update_throttle = 5  # seconds
        
        # Initialize UI
        self._setup_ui()
        self._setup_weather_sync()
        self._setup_keyboard_shortcuts()
        self._start_background_services()
        
    def _setup_ui(self):
        """Setup the weather visualization interface (replacing broken maps)."""
        # Create main container
        self.main_frame = ctk.CTkFrame(
            self.parent,
            fg_color=("#F8F9FA", "#1A1A1A"),
            corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # Create beautiful weather visualization instead of broken maps
        self._create_main_content()
        
    def _create_main_content(self):
        """Create the main content area - replace broken map with weather viz"""
        # Remove all the broken WebView code
        # Create a beautiful weather visualization instead
        
        from src.ui.components.weather_visualization_panel import WeatherVisualizationPanel
        
        self.main_content = WeatherVisualizationPanel(
            self.main_frame,
            weather_service=self.weather_service,
            config=self.config_service
        )
        self.main_content.pack(fill="both", expand=True)
        
    def _create_thread_safe_maps(self):
        """Create the thread-safe maps interface."""
        try:
            # Create horizontal layout
            self.maps_container = ctk.CTkFrame(self.main_frame, fg_color=("#F0F0F0", "#2B2B2B"))
            self.maps_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Configure grid
            self.maps_container.grid_columnconfigure(1, weight=1)
            self.maps_container.grid_rowconfigure(0, weight=1)
            
            # Create weather controls panel (left side)
            self.weather_controls = WeatherControlsPanel(
                self.maps_container,
                None,  # Will be set after maps widget creation
                width=350
            )
            self.weather_controls.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            
            # Create maps widget (right side)
            self.maps_widget = ThreadSafeGoogleMapsWidget(
                self.maps_container,
                self.weather_service,
                self.config_service
            )
            self.maps_widget.grid(row=0, column=1, sticky="nsew")
            
            # Connect weather controls to maps widget
            self.weather_controls.maps_widget = self.maps_widget
            
            # Setup event handlers
            self._setup_maps_event_handlers()
            
            self.logger.info("Thread-safe maps interface created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create thread-safe maps: {e}")
            self._create_fallback_maps()
 
    def _create_fallback_maps(self):
        """Create fallback maps interface using tkintermapview."""
        try:
            # Create container for fallback maps
            self.maps_container = ctk.CTkFrame(self.main_frame, fg_color=("#F0F0F0", "#2B2B2B"))
            self.maps_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create enhanced info panel with installation guidance
            info_frame = ctk.CTkFrame(self.maps_container, width=350)
            info_frame.pack(side="left", fill="y", padx=(0, 10))
            
            # Header
            header_label = ctk.CTkLabel(
                info_frame,
                text="🗺️ Maps (Basic Mode)",
                font=("Helvetica", 16, "bold")
            )
            header_label.pack(pady=(20, 10), padx=20)
            
            # Status info
            status_text = "Status: Thread-safe maps unavailable\nUsing basic tkintermapview"
            status_label = ctk.CTkLabel(
                info_frame,
                text=status_text,
                justify="left",
                font=("Helvetica", 12)
            )
            status_label.pack(pady=10, padx=20)
            
            # Missing dependencies info
            missing_deps = []
            if not TKINTER_MAPVIEW_AVAILABLE:
                missing_deps.append("tkintermapview")
            if not THREAD_SAFE_MAPS_AVAILABLE:
                missing_deps.extend(["tkinterweb", "pywebview"])
            
            if missing_deps:
                deps_text = f"Missing: {', '.join(missing_deps)}"
                deps_label = ctk.CTkLabel(
                    info_frame,
                    text=deps_text,
                    justify="left",
                    font=("Helvetica", 11),
                    text_color=("#FF6B6B", "#FF8E8E")
                )
                deps_label.pack(pady=5, padx=20)
            
            # Installation button
            install_button = ctk.CTkButton(
                info_frame,
                text="📦 Install Dependencies",
                command=self._show_installation_guide,
                width=200
            )
            install_button.pack(pady=15, padx=20)
            
            # Instructions
            instructions = (
                "To enable full maps functionality:\n\n"
                "1. Run: python install_maps_dependencies.py\n"
                "2. Or manually install:\n"
                "   pip install tkintermapview\n"
                "   pip install tkinterweb\n"
                "   pip install pywebview\n\n"
                "3. Restart the application"
            )
            instructions_label = ctk.CTkLabel(
                info_frame,
                text=instructions,
                justify="left",
                font=("Helvetica", 10),
                wraplength=300
            )
            instructions_label.pack(pady=10, padx=20, fill="x")
            
            # Create tkintermapview widget
            self.map_widget = tkintermapview.TkinterMapView(
                self.maps_container,
                width=800,
                height=600,
                corner_radius=10
            )
            self.map_widget.pack(side="right", fill="both", expand=True)
            
            # Set default position from config
            lat = self.maps_config_manager.get('last_latitude', 51.5074)
            lng = self.maps_config_manager.get('last_longitude', -0.1278)
            zoom = self.maps_config_manager.get('last_zoom', 10)
            
            self.map_widget.set_position(lat, lng)
            self.map_widget.set_zoom(zoom)
            
            # Use OpenStreetMap tile server
            self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
            
            self.logger.info("Fallback tkintermapview loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Fallback maps failed: {e}")
            self._create_static_fallback()
 
    def _setup_weather_sync(self):
        """Setup weather data synchronization with the dashboard's weather service."""
        if self.weather_service:
            # Add observer for weather updates
            self.weather_service.add_observer(self._on_weather_update)
            
            # Start periodic weather updates
            self._start_weather_updates()
            
            self.logger.info("Weather synchronization setup complete")
    
    def _on_weather_update(self, weather_data):
        """Handle weather data updates from the dashboard service."""
        if not self.is_active or not hasattr(self, 'maps_widget'):
            return
            
        try:
            # Throttle updates to prevent overwhelming the UI
            current_time = time.time()
            if current_time - self.last_weather_update < self.weather_update_throttle:
                return
                
            self.last_weather_update = current_time
            
            # Update weather overlays if thread-safe maps available
            if THREAD_SAFE_MAPS_AVAILABLE and hasattr(self, 'weather_controls'):
                self._update_weather_overlays(weather_data)
                
        except Exception as e:
            self.logger.error(f"Error updating weather data: {e}")
    
    def _update_weather_overlays(self, weather_data):
        """Update weather overlays with new data."""
        if not self.weather_controls or not self.maps_widget:
            return
            
        # Get current map bounds for viewport-based loading
        bounds = self.maps_widget.get_bounds()
        if not bounds:
            return
            
        # Filter weather data to viewport
        viewport_weather = self._filter_weather_to_viewport(weather_data, bounds)
        
        # Update weather layers
        self.weather_controls.update_weather_data(viewport_weather)
 
    def _create_static_fallback(self):
        """Create static fallback interface when all map options fail."""
        # Create canvas-based map display
        self.fallback_frame = ctk.CTkFrame(self.main_frame)
        self.fallback_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header = ctk.CTkLabel(
            self.fallback_frame,
            text="📍 Weather Map Viewer",
            font=("Helvetica", 24, "bold")
        )
        header.pack(pady=20)
        
        # Create tabbed interface for different views
        self.map_tabs = ctk.CTkTabview(self.fallback_frame)
        self.map_tabs.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Weather Overview Tab
        overview_tab = self.map_tabs.add("Weather Overview")
        self.create_weather_overview(overview_tab)
        
        # City Weather Tab
        city_tab = self.map_tabs.add("City Weather")
        self.create_city_weather_grid(city_tab)
        
        # Weather Stations Tab
        stations_tab = self.map_tabs.add("Weather Stations")
        self.create_stations_view(stations_tab)
        
        self.logger.info("Static fallback interface created")
    
    def _get_maps_api_key(self):
        """Get Google Maps API key from configuration."""
        if self.config_service:
            return self.config_service.get('google_maps_api_key', '')
        return ''
    
    def _setup_maps_event_handlers(self):
        """Setup event handlers for the maps widget."""
        if not hasattr(self, 'maps_widget'):
            return
            
        # Bind map events
        self.maps_widget.bind_event('bounds_changed', self._on_map_bounds_changed)
        self.maps_widget.bind_event('zoom_changed', self._on_map_zoom_changed)
        self.maps_widget.bind_event('center_changed', self._on_map_center_changed)
    
    def _load_maps_config(self):
        """Load maps configuration from config manager."""
        return self.maps_config_manager.config
    
    def _save_maps_config(self):
        """Save current maps configuration."""
        try:
            # Get current map state and save directly to config manager
            if hasattr(self, 'maps_widget') and self.maps_widget:
                center = self.maps_widget.get_center()
                if center:
                    self.maps_config_manager.set('last_latitude', center['lat'])
                    self.maps_config_manager.set('last_longitude', center['lng'])
                    
                zoom = self.maps_widget.get_zoom()
                if zoom:
                    self.maps_config_manager.set('last_zoom', zoom)
            
            # Save configuration
            self.maps_config_manager.save()
            
        except Exception as e:
            self.logger.error(f"Error saving maps config: {e}")
    
    def _apply_saved_config(self):
        """Apply saved configuration to maps interface."""
        if not hasattr(self, 'maps_widget') or not self.maps_widget:
            return
            
        try:
            # Apply map position and zoom
            lat = self.maps_config_manager.get('last_latitude', 51.5074)
            lng = self.maps_config_manager.get('last_longitude', -0.1278)
            zoom = self.maps_config_manager.get('last_zoom', 10)
            
            self.maps_widget.set_center(lat, lng)
            self.maps_widget.set_zoom(zoom)
            
            # Apply map style
            style = self.maps_config_manager.get('map_style', 'roadmap')
            self.maps_widget.set_map_style(style)
            
            # Apply active layers and opacity
            if hasattr(self, 'weather_controls'):
                active_layers = self.maps_config_manager.get('active_layers', [])
                layer_opacity = self.maps_config_manager.get('layer_opacity', {})
                
                for layer in active_layers:
                    self.weather_controls.enable_layer(layer)
                    if layer in layer_opacity:
                        self.weather_controls.set_layer_opacity(layer, layer_opacity[layer])
                        
        except Exception as e:
            self.logger.error(f"Error applying saved config: {e}")
    
    def _on_map_bounds_changed(self, bounds):
        """Handle map bounds change events."""
        if not self.is_active:
            return
            
        # Trigger viewport-based weather data loading
        self._load_viewport_weather_data(bounds)
        
        # Save bounds to cache for performance
        self.viewport_cache['bounds'] = bounds
        self.viewport_cache['timestamp'] = time.time()
    
    def _on_map_zoom_changed(self, zoom):
        """Handle map zoom change events."""
        if not self.is_active:
            return
            
        # Update config
        self.maps_config_manager.set('last_zoom', zoom)
        
        # Adjust weather data density based on zoom level
        self._adjust_weather_density(zoom)
    
    def _on_map_center_changed(self, center):
        """Handle map center change events."""
        if not self.is_active:
            return
            
        # Update config
        self.maps_config_manager.set('last_latitude', center['lat'])
        self.maps_config_manager.set('last_longitude', center['lng'])
    
    def _load_viewport_weather_data(self, bounds):
        """Load weather data for current viewport."""
        if not bounds or not self.weather_service:
            return
            
        # Check cache first
        cache_key = f"{bounds['north']},{bounds['south']},{bounds['east']},{bounds['west']}"
        if cache_key in self.weather_cache:
            cache_entry = self.weather_cache[cache_key]
            if time.time() - cache_entry['timestamp'] < 300:  # 5 minute cache
                return cache_entry['data']
        
        # Load new data in background thread
        def load_data():
            try:
                weather_data = self.weather_service.get_weather_for_bounds(bounds)
                self.weather_cache[cache_key] = {
                    'data': weather_data,
                    'timestamp': time.time()
                }
                
                # Update UI on main thread
                self.parent.after(0, lambda: self._update_weather_overlays(weather_data))
                
            except Exception as e:
                self.logger.error(f"Error loading viewport weather data: {e}")
        
        if not self.shutdown_event.is_set():
            threading.Thread(target=load_data, daemon=True).start()
    
    def _filter_weather_to_viewport(self, weather_data, bounds):
        """Filter weather data to current viewport."""
        if not weather_data or not bounds:
            return weather_data
            
        filtered_data = []
        for point in weather_data:
            if (bounds['south'] <= point.get('lat', 0) <= bounds['north'] and
                bounds['west'] <= point.get('lng', 0) <= bounds['east']):
                filtered_data.append(point)
                
        return filtered_data
    
    def _adjust_weather_density(self, zoom):
        """Adjust weather data density based on zoom level."""
        if not hasattr(self, 'weather_controls'):
            return
            
        # Higher zoom = more detailed data
        if zoom >= 12:
            density = 'high'
        elif zoom >= 8:
            density = 'medium'
        else:
            density = 'low'
            
        self.weather_controls.set_data_density(density)
        
        # Save density preference
        self.maps_config_manager.set('weather_data_density', density)
    
    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for maps interface."""
        if not hasattr(self, 'main_frame'):
            return
            
        # Bind keyboard events
        self.main_frame.bind('<Control-l>', self._on_location_shortcut)
        self.main_frame.bind('<Control-r>', self._on_refresh_shortcut)
        self.main_frame.bind('<Control-e>', self._on_export_shortcut)
        self.main_frame.bind('<F1>', self._on_help_shortcut)
        
        # Make frame focusable
        self.main_frame.focus_set()
    
    def _on_location_shortcut(self, event):
        """Handle Ctrl+L shortcut for location search."""
        if hasattr(self, 'weather_controls'):
            self.weather_controls.focus_location_search()
    
    def _on_refresh_shortcut(self, event):
        """Handle Ctrl+R shortcut for refresh."""
        self.refresh_weather_data()
    
    def _on_export_shortcut(self, event):
        """Handle Ctrl+E shortcut for export."""
        self.export_map_image()
    
    def _on_help_shortcut(self, event):
        """Handle F1 shortcut for help."""
        self._show_help_tooltips()
    
    def _show_loading_shimmer(self):
        """Show loading shimmer effect."""
        if hasattr(self, 'main_frame'):
            self.loading_frame = ctk.CTkFrame(
                self.main_frame,
                fg_color=("#E8E8E8", "#2B2B2B")
            )
            self.loading_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
            
            # Create shimmer animation
            self.loading_label = ctk.CTkLabel(
                self.loading_frame,
                text="Loading Maps Interface...",
                font=("Arial", 16)
            )
            self.loading_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _hide_loading_shimmer(self):
        """Hide loading shimmer effect."""
        if hasattr(self, 'loading_frame'):
            self.loading_frame.destroy()
            delattr(self, 'loading_frame')
    
    def _show_help_tooltips(self):
        """Show help tooltips for first-time users."""
        if not self.maps_config_manager.get('show_help', True):
            return
            
        # Create help overlay
        help_window = ctk.CTkToplevel(self.parent)
        help_window.title("Maps Interface Help")
        help_window.geometry("400x300")
        help_window.transient(self.parent)
        
        help_text = """
Maps Interface Shortcuts:

• Ctrl+L: Focus location search
• Ctrl+R: Refresh weather data
• Ctrl+E: Export map image
• F1: Show this help

Weather Layers:
• Toggle layers using the control panel
• Adjust opacity with sliders
• Use map tools for analysis

Tips:
• Zoom in for more detailed weather data
• Weather data updates every 30 seconds
• Click markers for detailed information
        """
        
        help_label = ctk.CTkLabel(
            help_window,
            text=help_text,
            justify="left",
            font=("Arial", 12)
        )
        help_label.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Don't show again checkbox
        def toggle_help():
            self.maps_config_manager.set('show_help', not dont_show_var.get())
            self.maps_config_manager.save()
        
        dont_show_var = ctk.BooleanVar()
        dont_show_cb = ctk.CTkCheckBox(
            help_window,
            text="Don't show again",
            variable=dont_show_var,
            command=toggle_help
        )
        dont_show_cb.pack(pady=10)
        
        close_btn = ctk.CTkButton(
            help_window,
            text="Close",
            command=help_window.destroy
        )
        close_btn.pack(pady=10)
    
    def _start_background_services(self):
        """Start background services for weather updates and caching."""
        if self.shutdown_event.is_set():
            return
            
        # Start weather update thread
        self.weather_thread = threading.Thread(
            target=self._weather_update_loop,
            daemon=True
        )
        self.weather_thread.start()
        
        # Start cache cleanup thread
        self.cache_thread = threading.Thread(
            target=self._cache_cleanup_loop,
            daemon=True
        )
        self.cache_thread.start()
        
        self.logger.info("Background services started")
    
    def _weather_update_loop(self):
        """Background loop for weather updates."""
        while not self.shutdown_event.is_set():
            try:
                if self.is_active and self.maps_config_manager.get('auto_refresh', True):
                    # Trigger weather update
                    if hasattr(self, 'maps_widget') and self.maps_widget:
                        bounds = self.maps_widget.get_bounds()
                        if bounds:
                            self._load_viewport_weather_data(bounds)
                
                # Wait for next update
                interval = self.maps_config_manager.get('refresh_interval', 30)
                self.shutdown_event.wait(interval)
                
            except Exception as e:
                self.logger.error(f"Error in weather update loop: {e}")
                self.shutdown_event.wait(5)  # Wait before retry
    
    def _cache_cleanup_loop(self):
        """Background loop for cache cleanup."""
        while not self.shutdown_event.is_set():
            try:
                current_time = time.time()
                
                # Clean weather cache (remove entries older than 10 minutes)
                expired_keys = []
                for key, entry in self.weather_cache.items():
                    if current_time - entry['timestamp'] > 600:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.weather_cache[key]
                
                # Clean tile cache if it gets too large
                if len(self._tile_cache) > 1000:
                    # Remove oldest 20% of entries
                    sorted_cache = sorted(
                        self._tile_cache.items(),
                        key=lambda x: x[1]['timestamp']
                    )
                    remove_count = len(sorted_cache) // 5
                    for i in range(remove_count):
                        del self._tile_cache[sorted_cache[i][0]]
                
                # Wait 5 minutes before next cleanup
                self.shutdown_event.wait(300)
                
            except Exception as e:
                self.logger.error(f"Error in cache cleanup loop: {e}")
                self.shutdown_event.wait(60)  # Wait before retry
    
    def _start_weather_updates(self):
        """Start periodic weather updates."""
        if hasattr(self, 'weather_update_timer'):
            return
            
        def update_weather():
            if not self.shutdown_event.is_set() and self.is_active:
                if hasattr(self, 'maps_widget') and self.maps_widget:
                    bounds = self.maps_widget.get_bounds()
                    if bounds:
                        self._load_viewport_weather_data(bounds)
                
                # Schedule next update
                interval = self.maps_config_manager.get('refresh_interval', 30) * 1000
                self.weather_update_timer = self.parent.after(interval, update_weather)
        
        # Start first update
        update_weather()
    
    def refresh_weather_data(self):
        """Manually refresh weather data."""
        if hasattr(self, 'maps_widget') and self.maps_widget:
            bounds = self.maps_widget.get_bounds()
            if bounds:
                # Clear cache for immediate refresh
                cache_key = f"{bounds['north']},{bounds['south']},{bounds['east']},{bounds['west']}"
                if cache_key in self.weather_cache:
                    del self.weather_cache[cache_key]
                
                self._load_viewport_weather_data(bounds)
    
    def export_map_image(self):
        """Export current map view as image."""
        if not hasattr(self, 'maps_widget') or not self.maps_widget:
            return
            
        try:
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")],
                title="Export Map Image"
            )
            
            if filename:
                self.maps_widget.export_image(filename)
                self.logger.info(f"Map exported to {filename}")
                
        except Exception as e:
            self.logger.error(f"Error exporting map: {e}")
    
    def activate(self):
        """Activate the maps tab."""
        self.is_active = True
        
        # Apply fade-in effect
        if hasattr(self, 'main_frame'):
            self.main_frame.configure(fg_color=("#F8F9FA", "#1A1A1A"))
        
        # Resume weather updates
        if not hasattr(self, 'weather_update_timer'):
            self._start_weather_updates()
        
        self.logger.info("Maps tab activated")
    
    def deactivate(self):
        """Deactivate the maps tab and cleanup resources."""
        self.is_active = False
        
        # Stop weather updates
        if hasattr(self, 'weather_update_timer'):
            self.parent.after_cancel(self.weather_update_timer)
            delattr(self, 'weather_update_timer')
        
        # Cleanup WebView resources
        if hasattr(self, 'maps_widget') and self.maps_widget:
            self.maps_widget.cleanup()
        
        # Save current configuration
        self._save_maps_config()
        
        self.logger.info("Maps tab deactivated")
    
    def cleanup(self):
        """Cleanup resources when closing the application."""
        self.shutdown_event.set()
        
        # Stop background threads
        if hasattr(self, 'weather_thread') and self.weather_thread.is_alive():
            self.weather_thread.join(timeout=2)
        
        if hasattr(self, 'cache_thread') and self.cache_thread.is_alive():
            self.cache_thread.join(timeout=2)
        
        # Cleanup maps widget
        if hasattr(self, 'maps_widget') and self.maps_widget:
            self.maps_widget.cleanup()
        
        # Save final configuration
        if hasattr(self, 'maps_config_manager'):
            self.maps_config_manager.save()
        
        self.logger.info("Maps tab cleanup completed")
     
    def create_weather_overview(self, parent):
        """Create weather overview display"""
        # Search frame
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.location_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter city name...",
            width=300
        )
        self.location_entry.pack(side="left", padx=10, pady=10)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search Weather",
            command=self.search_weather
        )
        search_btn.pack(side="left", padx=10, pady=10)
        
        # Weather display frame
        self.weather_display = ctk.CTkFrame(parent)
        self.weather_display.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Default weather info
        self.show_default_weather()
    
    def create_city_weather_grid(self, parent):
        """Create city weather grid display"""
        # Scrollable frame for cities
        self.cities_frame = ctk.CTkScrollableFrame(parent)
        self.cities_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sample cities
        cities = [
            ("London", "15°C", "Cloudy"),
            ("New York", "22°C", "Sunny"),
            ("Tokyo", "18°C", "Rainy"),
            ("Paris", "12°C", "Overcast"),
            ("Sydney", "25°C", "Clear"),
            ("Moscow", "8°C", "Snow")
        ]
        
        for i, (city, temp, condition) in enumerate(cities):
            city_frame = ctk.CTkFrame(self.cities_frame)
            city_frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
            
            city_label = ctk.CTkLabel(city_frame, text=city, font=("Helvetica", 16, "bold"))
            city_label.pack(pady=5)
            
            temp_label = ctk.CTkLabel(city_frame, text=temp, font=("Helvetica", 14))
            temp_label.pack()
            
            condition_label = ctk.CTkLabel(city_frame, text=condition, font=("Helvetica", 12))
            condition_label.pack(pady=5)
    
    def create_stations_view(self, parent):
        """Create weather stations view"""
        # Stations list
        stations_frame = ctk.CTkFrame(parent)
        stations_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        title = ctk.CTkLabel(stations_frame, text="Weather Stations", font=("Helvetica", 18, "bold"))
        title.pack(pady=10)
        
        # Sample stations
        stations = [
            "Heathrow Airport - London",
            "Central Park - New York",
            "Narita Airport - Tokyo",
            "Charles de Gaulle - Paris",
            "Sydney Observatory",
            "Red Square - Moscow"
        ]
        
        for station in stations:
            station_label = ctk.CTkLabel(stations_frame, text=f"📡 {station}")
            station_label.pack(pady=5, anchor="w", padx=20)
    
    def show_default_weather(self):
        """Show default weather information"""
        default_label = ctk.CTkLabel(
            self.weather_display,
            text="🌤️ Welcome to Weather Maps\n\nEnter a city name above to view weather information",
            font=("Helvetica", 16)
        )
        default_label.pack(expand=True)
    
    def search_weather(self):
        """Search for weather information"""
        location = self.location_entry.get().strip()
        if not location:
            return
        
        # Clear previous results
        for widget in self.weather_display.winfo_children():
            widget.destroy()
        
        try:
            # Try to get weather data
            weather_data = self.get_weather_data(location)
            self.display_weather_data(weather_data)
        except Exception as e:
            self.logger.error(f"Weather search failed: {e}")
            error_label = ctk.CTkLabel(
                self.weather_display,
                text=f"❌ Could not fetch weather for {location}\n\nPlease try again or check the city name.",
                font=("Helvetica", 14)
            )
            error_label.pack(expand=True)
    
    def get_weather_data(self, location: str) -> Dict[str, Any]:
        """Get weather data for location"""
        if self.weather_service:
            try:
                return self.weather_service.get_weather(location)
            except Exception as e:
                self.logger.error(f"Weather service error: {e}")
        
        # Fallback mock data
        return {
            "location": location,
            "temperature": "20°C",
            "condition": "Partly Cloudy",
            "humidity": "65%",
            "wind": "10 km/h"
        }
    
    def display_weather_data(self, data: Dict[str, Any]):
        """Display weather data"""
        # Location header
        location_label = ctk.CTkLabel(
            self.weather_display,
            text=f"📍 {data.get('location', 'Unknown')}",
            font=("Helvetica", 20, "bold")
        )
    
    def _show_installation_guide(self):
        """Show installation guide dialog."""
        import tkinter.messagebox as messagebox
        
        message = (
            "Maps Dependencies Installation\n\n"
            "To enable full maps functionality, install these packages:\n\n"
            "• tkintermapview (interactive maps)\n"
            "• tkinterweb (web integration)\n"
            "• pywebview (enhanced web views)\n\n"
            "Installation Options:\n\n"
            "1. Automatic (Recommended):\n"
            "   Run: python install_maps_dependencies.py\n\n"
            "2. Manual:\n"
            "   pip install tkintermapview>=1.29\n"
            "   pip install tkinterweb>=3.24\n"
            "   pip install pywebview>=4.0\n\n"
            "After installation, restart the application to use the enhanced maps."
        )
        
        messagebox.showinfo("Maps Installation Guide", message)
        self.logger.info("Installation guide displayed")
    
    def add_weather_marker(self, lat: float, lon: float, weather_data: Dict[str, Any]):
        """Add weather marker to map (if map widget is available)"""
        if self.map_widget:
            try:
                marker_text = f"{weather_data.get('location', 'Unknown')}\n{weather_data.get('temperature', 'N/A')}"
                self.map_widget.set_marker(lat, lon, text=marker_text)
                self.map_widget.set_position(lat, lon)
            except Exception as e:
                self.logger.error(f"Failed to add marker: {e}")
    
    def refresh_map(self):
        """Refresh map display"""
        try:
            if self.map_widget:
                # Refresh tkintermapview
                self.map_widget.delete_all_marker()
            else:
                # Recreate fallback display
                self.create_map_widget()
        except Exception as e:
            self.logger.error(f"Map refresh failed: {e}")
            self.create_static_map_fallback()