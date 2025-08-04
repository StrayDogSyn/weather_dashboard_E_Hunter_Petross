import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import requests
from io import BytesIO
import threading
import logging
import webbrowser
from typing import Optional, Dict, Tuple, List
from datetime import datetime
import math
import os

class EnhancedStaticMapsComponent(ctk.CTkFrame):
    """Enhanced maps component with full functionality including browser launch and weather layers"""
    
    def __init__(self, parent, weather_service=None, config=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.weather_service = weather_service
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Map state
        self.center_lat = 40.7128  # Default NYC
        self.center_lng = -74.0060
        self.zoom_level = 11
        self.map_type = "roadmap"
        self.current_image = None
        self.weather_data = {}
        self.weather_layers = {
            'temperature': False,
            'precipitation': False,
            'wind': False,
            'pressure': False,
            'clouds': False
        }
        
        # API configuration
        self.api_key = self._get_api_key()
        
        # Create complete UI
        self._create_main_layout()
        
        # Load initial map after UI is ready
        self.after(100, self._update_map)
        
    def _get_api_key(self):
        """Get Google Maps API key from config"""
        try:
            if self.config and hasattr(self.config, 'get'):
                api_key = self.config.get('google_maps_api_key', '')
                if api_key and len(api_key) > 10:  # Basic validation
                    return api_key
            # Try environment variable as fallback
            return os.getenv('GOOGLE_MAPS_API_KEY', '')
        except Exception as e:
            self.logger.warning(f"Failed to get API key: {e}")
            return ''
    
    def _create_main_layout(self):
        """Create the complete UI layout with toolbar, sidebar, and map area"""
        
        # Top toolbar frame with search and browser button
        self.toolbar_frame = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.toolbar_frame.pack(fill="x", padx=0, pady=0)
        self.toolbar_frame.pack_propagate(False)
        
        # Search section in toolbar
        self.search_frame = ctk.CTkFrame(self.toolbar_frame, fg_color="transparent")
        self.search_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        # Location icon
        self.location_icon = ctk.CTkLabel(self.search_frame, text="📍", font=("Arial", 16))
        self.location_icon.pack(side="left", padx=(0, 5))
        
        # Search entry field
        self.search_entry = ctk.CTkEntry(
            self.search_frame,
            placeholder_text="Search for a location...",
            width=300
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind("<Return>", self._on_search)
        
        # Search button
        self.search_btn = ctk.CTkButton(
            self.search_frame,
            text="Search",
            width=80,
            command=self._search_location
        )
        self.search_btn.pack(side="left", padx=5)
        
        # Browser button - IMPORTANT FEATURE
        self.browser_btn = ctk.CTkButton(
            self.toolbar_frame,
            text="🌐 Open in Browser",
            width=140,
            command=self._open_in_browser,
            fg_color="#2B7A78"
        )
        self.browser_btn.pack(side="right", padx=10)
        
        # Main content area with sidebar and map
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.pack(fill="both", expand=True)
        
        # Create left sidebar with all controls
        self._create_sidebar()
        
        # Map display area on the right
        self.map_container = ctk.CTkFrame(self.content_frame, corner_radius=10)
        self.map_container.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # Map label for displaying the image
        self.map_label = ctk.CTkLabel(
            self.map_container,
            text="Loading map...",
            fg_color="transparent"
        )
        self.map_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Status bar at bottom
        self.status_frame = ctk.CTkFrame(self, height=30, corner_radius=0)
        self.status_frame.pack(fill="x", side="bottom")
        self.status_frame.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="Ready",
            font=("Arial", 10)
        )
        self.status_label.pack(side="left", padx=10)
    
    def _create_sidebar(self):
        """Create left sidebar with map controls and weather layers"""
        self.sidebar = ctk.CTkFrame(self.content_frame, width=250, corner_radius=10)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        self.sidebar.pack_propagate(False)
        
        # Map Controls Section
        self.controls_label = ctk.CTkLabel(
            self.sidebar,
            text="Map Controls",
            font=("Arial", 16, "bold")
        )
        self.controls_label.pack(pady=(10, 5))
        
        # Zoom controls
        self.zoom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.zoom_frame.pack(fill="x", padx=10, pady=5)
        
        self.zoom_out_btn = ctk.CTkButton(
            self.zoom_frame,
            text="-",
            width=40,
            command=self._zoom_out
        )
        self.zoom_out_btn.pack(side="left")
        
        self.zoom_label = ctk.CTkLabel(
            self.zoom_frame,
            text=f"Zoom: {self.zoom_level}"
        )
        self.zoom_label.pack(side="left", expand=True)
        
        self.zoom_in_btn = ctk.CTkButton(
            self.zoom_frame,
            text="+",
            width=40,
            command=self._zoom_in
        )
        self.zoom_in_btn.pack(side="right")
        
        # Map type selection
        self.map_type_label = ctk.CTkLabel(self.sidebar, text="Map Type:")
        self.map_type_label.pack(pady=(10, 5))
        
        self.map_type_var = ctk.StringVar(value=self.map_type)
        self.map_type_menu = ctk.CTkOptionMenu(
            self.sidebar,
            values=["roadmap", "satellite", "hybrid", "terrain"],
            variable=self.map_type_var,
            command=self._on_map_type_change
        )
        self.map_type_menu.pack(fill="x", padx=10, pady=5)
        
        # Weather Layers Section
        self.weather_label = ctk.CTkLabel(
            self.sidebar,
            text="Weather Layers",
            font=("Arial", 16, "bold")
        )
        self.weather_label.pack(pady=(20, 10))
        
        # Weather layer checkboxes
        self.weather_checkboxes = {}
        weather_options = [
            ("temperature", "🌡️ Temperature"),
            ("precipitation", "🌧️ Precipitation"),
            ("wind", "💨 Wind"),
            ("pressure", "📊 Pressure"),
            ("clouds", "☁️ Clouds")
        ]
        
        for key, label in weather_options:
            checkbox = ctk.CTkCheckBox(
                self.sidebar,
                text=label,
                command=lambda k=key: self._toggle_weather_layer(k)
            )
            checkbox.pack(anchor="w", padx=20, pady=2)
            self.weather_checkboxes[key] = checkbox
        
        # Current location button
        self.current_location_btn = ctk.CTkButton(
            self.sidebar,
            text="📍 Current Location",
            command=self._get_current_location
        )
        self.current_location_btn.pack(fill="x", padx=10, pady=(20, 10))
        
        # Refresh button
        self.refresh_btn = ctk.CTkButton(
            self.sidebar,
            text="🔄 Refresh Map",
            command=self._update_map
        )
        self.refresh_btn.pack(fill="x", padx=10, pady=5)
    
    def _open_in_browser(self):
        """Open current map view in web browser"""
        try:
            # Build Google Maps URL with current position
            url = f"https://www.google.com/maps/@{self.center_lat},{self.center_lng},{self.zoom_level}z"
            
            # Add weather layer parameter if any layers active
            if any(self.weather_layers.values()):
                url += "/data=!5m1!1e1"
            
            webbrowser.open(url)
            self._update_status("Opened in browser", duration=2000)
            self.logger.info(f"Opened map in browser: {url}")
            
        except Exception as e:
            self.logger.error(f"Failed to open browser: {e}")
            self._update_status("Failed to open browser", error=True)
    
    def _update_status(self, message, error=False, duration=None):
        """Update status bar message"""
        self.status_label.configure(
            text=message,
            text_color="red" if error else "white"
        )
        
        if duration:
            self.after(duration, lambda: self.status_label.configure(text="Ready", text_color="white"))
    
    def _on_search(self, event):
        """Handle search entry return key"""
        self._search_location()
    
    def _search_location(self):
        """Search for a location and update map"""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        self._update_status("Searching...")
        
        # Run geocoding in background thread
        threading.Thread(
            target=self._geocode_location,
            args=(query,),
            daemon=True
        ).start()
    
    def _geocode_location(self, query):
        """Geocode location using Google Geocoding API"""
        try:
            if not self.api_key:
                self.after(0, lambda: self._update_status("API key required for search", error=True))
                return
            
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': query,
                'key': self.api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data['status'] == 'OK' and data['results']:
                location = data['results'][0]['geometry']['location']
                lat, lng = location['lat'], location['lng']
                
                # Update map on main thread
                self.after(0, lambda: self._update_location(lat, lng, query))
            else:
                self.after(0, lambda: self._update_status("Location not found", error=True))
                
        except Exception as e:
            self.logger.error(f"Geocoding error: {e}")
            self.after(0, lambda: self._update_status("Search failed", error=True))
    
    def _update_location(self, lat, lng, location_name=None):
        """Update map center to new location"""
        self.center_lat = lat
        self.center_lng = lng
        
        if location_name:
            self._update_status(f"Found: {location_name}")
        
        self._update_map()
    
    def _zoom_in(self):
        """Zoom in on the map"""
        if self.zoom_level < 20:
            self.zoom_level += 1
            self.zoom_label.configure(text=f"Zoom: {self.zoom_level}")
            self._update_map()
    
    def _zoom_out(self):
        """Zoom out on the map"""
        if self.zoom_level > 1:
            self.zoom_level -= 1
            self.zoom_label.configure(text=f"Zoom: {self.zoom_level}")
            self._update_map()
    
    def _on_map_type_change(self, value):
        """Handle map type change"""
        self.map_type = value
        self._update_map()
    
    def _toggle_weather_layer(self, layer_key):
        """Toggle weather layer on/off"""
        checkbox = self.weather_checkboxes[layer_key]
        self.weather_layers[layer_key] = checkbox.get()
        self._update_map()
    
    def _get_current_location(self):
        """Get user's current location (placeholder - would need geolocation API)"""
        # For demo, use a default location
        self._update_location(40.7128, -74.0060, "New York City")
        self._update_status("Using default location")
    
    def _update_map(self):
        """Update the map display"""
        if not self.api_key:
            self._display_fallback_map()
            return
        
        self._update_status("Loading map...")
        
        # Run map loading in background thread
        threading.Thread(
            target=self._load_map_image,
            daemon=True
        ).start()
    
    def _load_map_image(self):
        """Load map image from Google Static Maps API"""
        try:
            # Build Static Maps API URL
            base_url = "https://maps.googleapis.com/maps/api/staticmap"
            params = {
                'center': f"{self.center_lat},{self.center_lng}",
                'zoom': self.zoom_level,
                'size': '640x480',
                'maptype': self.map_type,
                'key': self.api_key
            }
            
            # Add weather layers if enabled
            if any(self.weather_layers.values()):
                # Add weather overlay markers
                self._add_weather_markers(params)
            
            response = requests.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            
            # Load and display image
            image = Image.open(BytesIO(response.content))
            self.after(0, lambda: self._display_map_image(image))
            
        except Exception as e:
            self.logger.error(f"Failed to load map: {e}")
            self.after(0, lambda: self._display_fallback_map())
    
    def _add_weather_markers(self, params):
        """Add weather data markers to map parameters"""
        markers = []
        
        # Add center marker with weather info
        if self.weather_service:
            try:
                # Get weather data for current location
                weather_data = self.weather_service.get_current_weather(
                    self.center_lat, self.center_lng
                )
                
                if weather_data:
                    # Create weather marker
                    temp = weather_data.get('temperature', 'N/A')
                    marker = f"color:red|label:T|{self.center_lat},{self.center_lng}"
                    markers.append(marker)
                    
            except Exception as e:
                self.logger.warning(f"Failed to get weather data: {e}")
        
        if markers:
            params['markers'] = '|'.join(markers)
    
    def _display_map_image(self, image):
        """Display the loaded map image"""
        try:
            # Convert PIL image to PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Update map label
            self.map_label.configure(image=photo, text="")
            self.map_label.image = photo  # Keep reference
            
            self.current_image = image
            self._update_status("Map loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to display map: {e}")
            self._display_fallback_map()
    
    def _display_fallback_map(self):
        """Display attractive fallback when map can't be loaded"""
        try:
            # Create gradient image
            width = 640
            height = 480
            img = Image.new('RGB', (width, height))
            draw = ImageDraw.Draw(img)
            
            # Draw gradient
            for i in range(height):
                color = int(50 + (i / height) * 50)
                draw.line([(0, i), (width, i)], fill=(color, color, color + 20))
            
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            
            text = "Weather Map"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            
            # Add status message
            status = "Configure API key for interactive maps"
            try:
                small_font = ImageFont.truetype("arial.ttf", 12)
            except:
                small_font = ImageFont.load_default()
            
            status_bbox = draw.textbbox((0, 0), status, font=small_font)
            status_width = status_bbox[2] - status_bbox[0]
            status_x = (width - status_width) // 2
            
            draw.text((status_x, height - 50), status, fill=(200, 200, 200), font=small_font)
            
            self._display_map_image(img)
            
        except Exception as e:
            # Ultimate fallback - just text
            self.map_label.configure(
                text="Weather Map\n\nConfigure API key for interactive maps",
                image=""
            )
            self.logger.error(f"Fallback display failed: {e}")
    
    def set_location(self, lat, lng):
        """Set map location programmatically"""
        self._update_location(lat, lng)
    
    def get_current_location(self):
        """Get current map center location"""
        return self.center_lat, self.center_lng
    
    def update_weather_data(self, weather_data):
        """Update weather data for map display (compatibility method)"""
        try:
            if weather_data:
                self.weather_data = weather_data
                
                # Extract location if available
                if 'lat' in weather_data and 'lng' in weather_data:
                    self.center_lat = weather_data['lat']
                    self.center_lng = weather_data['lng']
                elif 'coord' in weather_data:
                    coord = weather_data['coord']
                    if 'lat' in coord and 'lon' in coord:
                        self.center_lat = coord['lat']
                        self.center_lng = coord['lon']
                
                # Update map if weather layers are active
                if any(self.weather_layers.values()):
                    self._update_map()
                    
                self.logger.info("Weather data updated for enhanced maps")
                
        except Exception as e:
            self.logger.error(f"Failed to update weather data: {e}")
    
    def refresh_weather_data(self):
        """Refresh weather data and update map"""
        if any(self.weather_layers.values()):
            self._update_map()
    
    def cleanup(self):
        """Clean up resources"""
        try:
            if hasattr(self, 'current_image'):
                self.current_image = None
            self.logger.info("Enhanced static maps component cleaned up")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")