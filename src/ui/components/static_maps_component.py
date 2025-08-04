import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import requests
from io import BytesIO
import threading
import logging
from typing import Optional, Dict, Tuple, List
from datetime import datetime
import math

class StaticMapsComponent(ctk.CTkFrame):
    """Maps component using Google Static Maps API - reliable and no WebView needed"""
    
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
        
        # API configuration
        self.api_key = self._get_api_key()
        self.map_size = "640x480"
        
        # Create UI
        self._create_ui()
        
        # Load initial map
        self.after(100, self._load_initial_map)
        
    def _get_api_key(self):
        """Get Google Maps API key from config"""
        try:
            if self.config and hasattr(self.config, 'get'):
                return self.config.get('google_maps_api_key', '')
            return ''
        except:
            return ''
    
    def _create_ui(self):
        """Create the UI components"""
        # Map display frame
        self.map_frame = ctk.CTkFrame(self, corner_radius=10)
        self.map_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Map label for image display
        self.map_label = ctk.CTkLabel(
            self.map_frame,
            text="Loading map...",
            fg_color="transparent"
        )
        self.map_label.pack(fill="both", expand=True)
        
        # Controls frame
        self.controls_frame = ctk.CTkFrame(self, height=60, corner_radius=10)
        self.controls_frame.pack(fill="x", padx=10, pady=(0, 10))
        self.controls_frame.pack_propagate(False)
        
        # Zoom controls
        self.zoom_in_btn = ctk.CTkButton(
            self.controls_frame,
            text="+",
            width=40,
            command=self._zoom_in
        )
        self.zoom_in_btn.pack(side="left", padx=5, pady=10)
        
        self.zoom_out_btn = ctk.CTkButton(
            self.controls_frame,
            text="-",
            width=40,
            command=self._zoom_out
        )
        self.zoom_out_btn.pack(side="left", padx=5, pady=10)
        
        # Map type selector
        self.map_type_var = ctk.StringVar(value="roadmap")
        self.map_type_menu = ctk.CTkOptionMenu(
            self.controls_frame,
            values=["roadmap", "satellite", "hybrid", "terrain"],
            variable=self.map_type_var,
            command=self._on_map_type_change
        )
        self.map_type_menu.pack(side="left", padx=10, pady=10)
        
        # Location entry
        self.location_entry = ctk.CTkEntry(
            self.controls_frame,
            placeholder_text="Enter location..."
        )
        self.location_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        self.location_entry.bind("<Return>", self._on_location_search)
        
        # Search button
        self.search_btn = ctk.CTkButton(
            self.controls_frame,
            text="Search",
            width=80,
            command=self._search_location
        )
        self.search_btn.pack(side="left", padx=(0, 10), pady=10)
        
    def _load_initial_map(self):
        """Load the initial map"""
        self._update_map()
    
    def _build_map_url(self):
        """Build Google Static Maps API URL"""
        base_url = "https://maps.googleapis.com/maps/api/staticmap"
        
        params = {
            'center': f"{self.center_lat},{self.center_lng}",
            'zoom': self.zoom_level,
            'size': self.map_size,
            'maptype': self.map_type,
            'format': 'png',
            'scale': 2  # Higher quality
        }
        
        # Add API key if available
        if self.api_key:
            params['key'] = self.api_key
        
        # Build URL
        url = base_url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        # Add weather markers if available
        if self.weather_data:
            markers = self._build_weather_markers()
            if markers:
                url += "&" + markers
        
        return url
    
    def _build_weather_markers(self):
        """Build marker parameters for weather data"""
        markers = []
        
        for location, data in self.weather_data.items():
            if 'lat' in data and 'lon' in data:
                temp = data.get('temperature', 0)
                color = self._temp_to_color(temp)
                marker = f"markers=color:{color}|size:mid|label:{int(temp)}|{data['lat']},{data['lon']}"
                markers.append(marker)
        
        return "&".join(markers)
    
    def _temp_to_color(self, temp):
        """Convert temperature to marker color"""
        if temp < 0:
            return "blue"
        elif temp < 15:
            return "green"
        elif temp < 25:
            return "yellow"
        else:
            return "red"
    
    def _update_map(self):
        """Update the map display"""
        def _fetch_and_display():
            try:
                url = self._build_map_url()
                
                # Use fallback image if no API key
                if not self.api_key:
                    self._show_fallback_map()
                    return
                
                # Fetch map image
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                # Load and display image
                image = Image.open(BytesIO(response.content))
                self.current_image = image
                
                # Convert to PhotoImage for display
                photo = ImageTk.PhotoImage(image)
                
                # Update UI on main thread
                self.after(0, lambda: self._display_image(photo))
                
            except Exception as e:
                self.logger.error(f"Failed to load map: {e}")
                self.after(0, self._show_error_map)
        
        # Run in background thread
        threading.Thread(target=_fetch_and_display, daemon=True).start()
    
    def _display_image(self, photo):
        """Display the map image in the UI"""
        self.map_label.configure(image=photo, text="")
        self.map_label.image = photo  # Keep a reference
    
    def _show_fallback_map(self):
        """Show fallback map when API key is not available"""
        # Create a simple fallback image
        img = Image.new('RGB', (640, 480), color='lightgray')
        draw = ImageDraw.Draw(img)
        
        # Draw simple map representation
        draw.rectangle([50, 50, 590, 430], outline='darkgray', width=2)
        
        # Add text
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        text = f"Map View\nLat: {self.center_lat:.4f}\nLng: {self.center_lng:.4f}\nZoom: {self.zoom_level}"
        draw.text((320, 200), text, fill='black', font=font, anchor='mm')
        
        # Add note about API key
        api_text = "Google Maps API key required\nfor full functionality"
        draw.text((320, 350), api_text, fill='red', font=font, anchor='mm')
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        self.after(0, lambda: self._display_image(photo))
    
    def _show_error_map(self):
        """Show error message when map loading fails"""
        self.map_label.configure(image="", text="Failed to load map\nPlease check your internet connection")
        self.map_label.image = None
    
    def _zoom_in(self):
        """Zoom in on the map"""
        if self.zoom_level < 20:
            self.zoom_level += 1
            self._update_map()
    
    def _zoom_out(self):
        """Zoom out on the map"""
        if self.zoom_level > 1:
            self.zoom_level -= 1
            self._update_map()
    
    def _on_map_type_change(self, value):
        """Handle map type change"""
        self.map_type = value
        self._update_map()
    
    def _on_location_search(self, event):
        """Handle location search from entry widget"""
        self._search_location()
    
    def _search_location(self):
        """Search for a location and update map"""
        location = self.location_entry.get().strip()
        if not location:
            return
        
        def _geocode_and_update():
            try:
                # Simple geocoding using Google's geocoding API
                geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
                params = {'address': location}
                
                if self.api_key:
                    params['key'] = self.api_key
                
                response = requests.get(geocode_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                if data['status'] == 'OK' and data['results']:
                    result = data['results'][0]
                    geometry = result['geometry']['location']
                    
                    # Update map center
                    self.center_lat = geometry['lat']
                    self.center_lng = geometry['lng']
                    
                    # Update map
                    self.after(0, self._update_map)
                    
                    self.logger.info(f"Location found: {location} -> {self.center_lat}, {self.center_lng}")
                else:
                    self.logger.warning(f"Location not found: {location}")
                    
            except Exception as e:
                self.logger.error(f"Geocoding failed: {e}")
        
        # Run geocoding in background
        threading.Thread(target=_geocode_and_update, daemon=True).start()
    
    def set_location(self, lat, lng, zoom=None):
        """Set map location programmatically"""
        self.center_lat = lat
        self.center_lng = lng
        if zoom is not None:
            self.zoom_level = zoom
        self._update_map()
    
    def get_current_location(self):
        """Get current map center location"""
        return {
            'lat': self.center_lat,
            'lng': self.center_lng,
            'zoom': self.zoom_level
        }
    
    def add_weather_data(self, weather_data):
        """Add weather data to display on map"""
        self.weather_data = weather_data
        self._update_map()
    
    def clear_weather_data(self):
        """Clear weather data from map"""
        self.weather_data = {}
        self._update_map()
    
    def export_image(self, filename):
        """Export current map as image"""
        if self.current_image:
            try:
                self.current_image.save(filename)
                self.logger.info(f"Map exported to {filename}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to export map: {e}")
                return False
        return False
    
    def cleanup(self):
        """Clean up resources"""
        self.current_image = None
        self.weather_data = {}
        if hasattr(self.map_label, 'image'):
            self.map_label.image = None
        self.logger.info("StaticMapsComponent cleaned up")