"""Google Maps Widget for Weather Dashboard.

Provides Google Maps JavaScript API integration with weather overlays.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

import customtkinter as ctk
import tkinterweb

from ...services.enhanced_weather_service import EnhancedWeatherService
from ..theme import DataTerminalTheme


class GoogleMapsWidget(ctk.CTkFrame):
    """Google Maps widget with weather integration."""

    def __init__(self, parent, weather_service: EnhancedWeatherService, config_service=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.weather_service = weather_service
        self.config_service = config_service
        self.logger = logging.getLogger(__name__)
        
        # Get Google Maps API key
        self.api_key = self._get_google_maps_api_key()
        
        # Current map state
        self.current_location = {"lat": 40.7128, "lng": -74.0060}  # Default to NYC
        self.current_zoom = 10
        self.active_layers = set()
        
        # Temporary file for map HTML
        self.temp_dir = Path(tempfile.gettempdir()) / "google_maps"
        self.temp_dir.mkdir(exist_ok=True)
        self.current_map_file = None
        
        # Setup UI
        self._setup_ui()
        
        # Load initial map
        self._load_initial_map()
    
    def _get_google_maps_api_key(self) -> str:
        """Get Google Maps API key from config service or environment."""
        try:
            if self.config_service:
                api_key = self.config_service.get_setting("api.google_maps_api_key")
                if api_key and api_key != "demo_key":
                    return api_key
            
            # Fallback to environment variable
            env_key = os.getenv("GOOGLE_MAPS_API_KEY")
            if env_key:
                return env_key
                
            self.logger.warning("No Google Maps API key found. Using demo mode.")
            return "demo_key"
            
        except Exception as e:
            self.logger.error(f"Error getting Google Maps API key: {e}")
            return "demo_key"
    
    def _setup_ui(self):
        """Setup the user interface."""
        self.configure(
            fg_color=DataTerminalTheme.BACKGROUND,
            corner_radius=12,
            border_width=1,
            border_color=DataTerminalTheme.BORDER,
        )
        
        # Create main layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create control panel
        self._create_control_panel()
        
        # Create map display
        self._create_map_display()
    
    def _create_control_panel(self):
        """Create control panel with map options."""
        self.control_panel = ctk.CTkFrame(
            self, 
            fg_color=DataTerminalTheme.CARD_BG, 
            corner_radius=8,
            width=250
        )
        self.control_panel.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        self.control_panel.grid_propagate(False)
        
        # Title
        title_label = ctk.CTkLabel(
            self.control_panel,
            text="🗺️ Weather Maps",
            font=(DataTerminalTheme.FONT_FAMILY, 18, "bold"),
            text_color=DataTerminalTheme.ACCENT
        )
        title_label.pack(pady=(15, 10))
        
        # Location section
        self._create_location_section()
        
        # Weather layers section
        self._create_weather_layers_section()
        
        # Map tools section
        self._create_map_tools_section()
    
    def _create_location_section(self):
        """Create location input section."""
        location_frame = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        location_frame.pack(fill="x", pady=(0, 15), padx=15)
        
        ctk.CTkLabel(
            location_frame,
            text="📍 Location",
            font=(DataTerminalTheme.FONT_FAMILY, 14, "bold"),
            text_color=DataTerminalTheme.TEXT
        ).pack(anchor="w", pady=(0, 5))
        
        # Location entry
        self.location_entry = ctk.CTkEntry(
            location_frame,
            placeholder_text="Enter city or coordinates...",
            font=(DataTerminalTheme.FONT_FAMILY, 12)
        )
        self.location_entry.pack(fill="x", pady=(0, 10))
        self.location_entry.bind("<Return>", lambda e: self._search_location())
        
        # Search button
        search_btn = ctk.CTkButton(
            location_frame,
            text="🔍 Search",
            command=self._search_location,
            height=32,
            font=(DataTerminalTheme.FONT_FAMILY, 12)
        )
        search_btn.pack(fill="x")
    
    def _create_weather_layers_section(self):
        """Create weather layers section."""
        layers_frame = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        layers_frame.pack(fill="x", pady=(0, 15), padx=15)
        
        ctk.CTkLabel(
            layers_frame,
            text="🌤️ Weather Layers",
            font=(DataTerminalTheme.FONT_FAMILY, 14, "bold"),
            text_color=DataTerminalTheme.TEXT
        ).pack(anchor="w", pady=(0, 10))
        
        # Weather layer checkboxes
        self.layer_vars = {}
        layers = [
            ("temperature", "🌡️ Temperature"),
            ("precipitation", "🌧️ Precipitation"),
            ("wind", "💨 Wind Speed"),
            ("pressure", "📊 Pressure"),
            ("clouds", "☁️ Clouds")
        ]
        
        for layer_id, layer_name in layers:
            var = ctk.BooleanVar()
            self.layer_vars[layer_id] = var
            
            checkbox = ctk.CTkCheckBox(
                layers_frame,
                text=layer_name,
                variable=var,
                command=lambda lid=layer_id: self._toggle_layer(lid),
                font=(DataTerminalTheme.FONT_FAMILY, 11)
            )
            checkbox.pack(anchor="w", pady=2)
    
    def _create_map_tools_section(self):
        """Create map tools section."""
        tools_frame = ctk.CTkFrame(self.control_panel, fg_color="transparent")
        tools_frame.pack(fill="x", pady=(0, 15), padx=15)
        
        ctk.CTkLabel(
            tools_frame,
            text="🛠️ Map Tools",
            font=(DataTerminalTheme.FONT_FAMILY, 14, "bold"),
            text_color=DataTerminalTheme.TEXT
        ).pack(anchor="w", pady=(0, 10))
        
        # Tool buttons
        tools = [
            ("🎯 Current Location", self._go_to_current_location),
            ("🔄 Refresh Map", self._refresh_map),
            ("📏 Measure Distance", self._enable_measurement),
            ("🎨 Map Style", self._change_map_style)
        ]
        
        for tool_name, tool_command in tools:
            btn = ctk.CTkButton(
                tools_frame,
                text=tool_name,
                command=tool_command,
                height=32,
                font=(DataTerminalTheme.FONT_FAMILY, 11)
            )
            btn.pack(fill="x", pady=2)
    
    def _create_map_display(self):
        """Create map display area."""
        map_frame = ctk.CTkFrame(
            self, 
            fg_color=DataTerminalTheme.CARD_BG, 
            corner_radius=8
        )
        map_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        map_frame.grid_columnconfigure(0, weight=1)
        map_frame.grid_rowconfigure(1, weight=1)
        
        # Map title
        map_title = ctk.CTkLabel(
            map_frame,
            text="Google Maps - Weather View",
            font=(DataTerminalTheme.FONT_FAMILY, 18, "bold"),
            text_color=DataTerminalTheme.ACCENT
        )
        map_title.grid(row=0, column=0, pady=(10, 5), sticky="ew")
        
        # Map container
        map_container = ctk.CTkFrame(map_frame, fg_color="white", corner_radius=8)
        map_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        map_container.grid_columnconfigure(0, weight=1)
        map_container.grid_rowconfigure(0, weight=1)
        
        # Web view for Google Maps
        try:
            self.map_webview = tkinterweb.HtmlFrame(map_container)
            self.map_webview.grid(row=0, column=0, sticky="nsew")
        except Exception as e:
            self.logger.error(f"Failed to create web view: {e}")
            # Fallback label
            fallback_label = ctk.CTkLabel(
                map_container,
                text="Google Maps not available\nPlease check your internet connection",
                font=(DataTerminalTheme.FONT_FAMILY, 14),
                text_color=DataTerminalTheme.TEXT_SECONDARY
            )
            fallback_label.grid(row=0, column=0)
    
    def _load_initial_map(self):
        """Load initial Google Maps."""
        try:
            self._create_google_maps_html()
            self._display_map()
        except Exception as e:
            self.logger.error(f"Failed to load initial map: {e}")
            self._show_fallback_map(str(e))
    
    def _create_google_maps_html(self):
        """Create Google Maps HTML with weather overlays."""
        # Get active weather layers
        active_layers = [layer for layer, var in self.layer_vars.items() if var.get()]
        
        # Create weather layer overlays
        weather_overlays = self._generate_weather_overlays(active_layers)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Google Maps Weather</title>
            <style>
                html, body {{
                    height: 100%;
                    margin: 0;
                    padding: 0;
                    font-family: Arial, sans-serif;
                }}
                #map {{
                    height: 100%;
                    width: 100%;
                }}
                .weather-info {{
                    background: white;
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    font-size: 14px;
                }}
                .loading {{
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div id="loading" class="loading">
                <div>🗺️ Loading Google Maps...</div>
                <div style="margin-top: 10px; font-size: 12px; color: #666;">
                    Weather data will appear shortly
                </div>
            </div>
            <div id="map"></div>
            
            <script>
                let map;
                let weatherLayers = [];
                
                function initMap() {{
                    // Hide loading indicator
                    document.getElementById('loading').style.display = 'none';
                    
                    // Initialize map
                    map = new google.maps.Map(document.getElementById('map'), {{
                        center: {self.current_location},
                        zoom: {self.current_zoom},
                        mapTypeId: 'roadmap',
                        styles: [
                            {{
                                featureType: 'all',
                                elementType: 'geometry.fill',
                                stylers: [{{
                                    weight: '2.00'
                                }}]
                            }},
                            {{
                                featureType: 'all',
                                elementType: 'geometry.stroke',
                                stylers: [{{
                                    color: '#9c9c9c'
                                }}]
                            }}
                        ]
                    }});
                    
                    // Add weather overlays
                    {weather_overlays}
                    
                    // Add click listener for weather data
                    map.addListener('click', function(event) {{
                        getWeatherAtLocation(event.latLng);
                    }});
                    
                    // Add current location marker
                    addCurrentLocationMarker();
                }}
                
                function addCurrentLocationMarker() {{
                    const marker = new google.maps.Marker({{
                        position: {self.current_location},
                        map: map,
                        title: 'Current Location',
                        icon: {{
                            url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <circle cx="12" cy="12" r="8" fill="#4285f4" stroke="white" stroke-width="2"/>
                                    <circle cx="12" cy="12" r="3" fill="white"/>
                                </svg>
                            `),
                            scaledSize: new google.maps.Size(24, 24)
                        }}
                    }});
                    
                    const infoWindow = new google.maps.InfoWindow({{
                        content: '<div class="weather-info">📍 Current Location<br/>Click anywhere on the map for weather data</div>'
                    }});
                    
                    marker.addListener('click', function() {{
                        infoWindow.open(map, marker);
                    }});
                }}
                
                function getWeatherAtLocation(latLng) {{
                    const lat = latLng.lat();
                    const lng = latLng.lng();
                    
                    // Create info window with weather data placeholder
                    const infoWindow = new google.maps.InfoWindow({{
                        position: latLng,
                        content: `
                            <div class="weather-info">
                                <div style="font-weight: bold;">🌤️ Weather Info</div>
                                <div style="margin-top: 5px;">📍 Lat: ${{lat.toFixed(4)}}, Lng: ${{lng.toFixed(4)}}</div>
                                <div style="margin-top: 5px; font-size: 12px; color: #666;">
                                    Weather data integration available with API
                                </div>
                            </div>
                        `
                    }});
                    
                    infoWindow.open(map);
                }}
                
                function addWeatherLayer(layerType) {{
                    // Weather layer implementation would go here
                    console.log('Adding weather layer:', layerType);
                }}
                
                function removeWeatherLayer(layerType) {{
                    // Weather layer removal would go here
                    console.log('Removing weather layer:', layerType);
                }}
                
                // Handle API key errors
                function handleApiError() {{
                    document.getElementById('loading').innerHTML = `
                        <div style="color: #d32f2f;">
                            <div>⚠️ Google Maps API Error</div>
                            <div style="margin-top: 10px; font-size: 12px;">
                                Please check your API key configuration
                            </div>
                        </div>
                    `;
                }}
                
                window.gm_authFailure = handleApiError;
            </script>
            
            <script async defer 
                src="https://maps.googleapis.com/maps/api/js?key={self.api_key}&callback=initMap&libraries=geometry">
            </script>
        </body>
        </html>
        """
        
        # Save HTML to temporary file
        self.current_map_file = self.temp_dir / f"google_map_{hash(html_content) % 10000}.html"
        with open(self.current_map_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Google Maps HTML created: {self.current_map_file}")
    
    def _generate_weather_overlays(self, active_layers: list) -> str:
        """Generate JavaScript code for weather overlays."""
        if not active_layers:
            return "// No weather layers active"
        
        overlays_js = "// Weather layer overlays\n"
        
        for layer in active_layers:
            if layer == "temperature":
                overlays_js += """
                // Temperature overlay
                const temperatureLayer = new google.maps.ImageMapType({
                    getTileUrl: function(coord, zoom) {
                        return `https://tile.openweathermap.org/map/temp_new/${zoom}/${coord.x}/${coord.y}.png?appid=demo_key`;
                    },
                    tileSize: new google.maps.Size(256, 256),
                    maxZoom: 18,
                    minZoom: 0,
                    name: 'Temperature'
                });
                map.overlayMapTypes.push(temperatureLayer);
                """
            elif layer == "precipitation":
                overlays_js += """
                // Precipitation overlay
                const precipitationLayer = new google.maps.ImageMapType({
                    getTileUrl: function(coord, zoom) {
                        return `https://tile.openweathermap.org/map/precipitation_new/${zoom}/${coord.x}/${coord.y}.png?appid=demo_key`;
                    },
                    tileSize: new google.maps.Size(256, 256),
                    maxZoom: 18,
                    minZoom: 0,
                    name: 'Precipitation'
                });
                map.overlayMapTypes.push(precipitationLayer);
                """
            elif layer == "wind":
                overlays_js += """
                // Wind overlay
                const windLayer = new google.maps.ImageMapType({
                    getTileUrl: function(coord, zoom) {
                        return `https://tile.openweathermap.org/map/wind_new/${zoom}/${coord.x}/${coord.y}.png?appid=demo_key`;
                    },
                    tileSize: new google.maps.Size(256, 256),
                    maxZoom: 18,
                    minZoom: 0,
                    name: 'Wind'
                });
                map.overlayMapTypes.push(windLayer);
                """
            elif layer == "clouds":
                overlays_js += """
                // Clouds overlay
                const cloudsLayer = new google.maps.ImageMapType({
                    getTileUrl: function(coord, zoom) {
                        return `https://tile.openweathermap.org/map/clouds_new/${zoom}/${coord.x}/${coord.y}.png?appid=demo_key`;
                    },
                    tileSize: new google.maps.Size(256, 256),
                    maxZoom: 18,
                    minZoom: 0,
                    name: 'Clouds'
                });
                map.overlayMapTypes.push(cloudsLayer);
                """
        
        return overlays_js
    
    def _display_map(self):
        """Display map in web view."""
        try:
            if hasattr(self, 'map_webview') and self.current_map_file and os.path.exists(self.current_map_file):
                self.map_webview.load_file(str(self.current_map_file))
                self.logger.info("Google Maps loaded successfully")
            else:
                self._show_fallback_map("Web view not available")
        except Exception as e:
            self.logger.error(f"Failed to display map: {e}")
            self._show_fallback_map(str(e))
    
    def _show_fallback_map(self, error_msg: str):
        """Show fallback content when Google Maps cannot be displayed."""
        try:
            if hasattr(self, 'map_webview'):
                fallback_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Google Maps - Fallback</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            margin: 0;
                            padding: 20px;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            min-height: 100vh;
                        }}
                        .container {{
                            text-align: center;
                            background: rgba(255,255,255,0.1);
                            padding: 40px;
                            border-radius: 15px;
                            backdrop-filter: blur(10px);
                        }}
                        .error {{ color: #ffcdd2; margin: 15px 0; }}
                        .info {{ color: #e1f5fe; margin: 10px 0; }}
                        .location {{ color: #fff9c4; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>🗺️ Google Maps</h1>
                        <div class="error">⚠️ {error_msg}</div>
                        <div class="info">📍 Current Location:</div>
                        <div class="location">{self.current_location['lat']:.4f}, {self.current_location['lng']:.4f}</div>
                        <div class="info">🔄 Please check your Google Maps API key</div>
                        <div class="info">🌐 Internet connection required</div>
                    </div>
                </body>
                </html>
                """
                self.map_webview.load_html(fallback_html)
        except Exception as e:
            self.logger.error(f"Failed to show fallback map: {e}")
    
    def _search_location(self):
        """Search for a location and update map."""
        location = self.location_entry.get().strip()
        if not location:
            return
        
        try:
            # Use weather service's advanced location search
            locations = self.weather_service.search_locations_advanced(location)
            if locations:
                # Use the first result
                first_location = locations[0]
                self.current_location = {"lat": first_location.latitude, "lng": first_location.longitude}
                self._refresh_map()
                self.logger.info(f"Location updated to: {first_location.display_name} ({first_location.latitude}, {first_location.longitude})")
            else:
                self.logger.warning(f"Location not found: {location}")
        except Exception as e:
            self.logger.error(f"Failed to search location: {e}")
    
    def _toggle_layer(self, layer_id: str):
        """Toggle weather layer on/off."""
        try:
            self._refresh_map()
            self.logger.info(f"Toggled layer: {layer_id}")
        except Exception as e:
            self.logger.error(f"Failed to toggle layer {layer_id}: {e}")
    
    def _go_to_current_location(self):
        """Go to current location."""
        try:
            # Reset to default location (could be enhanced with actual geolocation)
            self.current_location = {"lat": 40.7128, "lng": -74.0060}
            self._refresh_map()
            self.logger.info("Moved to current location")
        except Exception as e:
            self.logger.error(f"Failed to go to current location: {e}")
    
    def _refresh_map(self):
        """Refresh the map with current settings."""
        try:
            self._create_google_maps_html()
            self._display_map()
            self.logger.info("Map refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh map: {e}")
    
    def _enable_measurement(self):
        """Enable distance measurement tool."""
        self.logger.info("Measurement tool activated (feature available in full version)")
    
    def _change_map_style(self):
        """Change map style."""
        self.logger.info("Map style change (feature available in full version)")
    
    def cleanup(self):
        """Clean up resources."""
        try:
            # Clean up temporary files
            if self.current_map_file and os.path.exists(self.current_map_file):
                os.remove(self.current_map_file)
            
            # Clean up temp directory if empty
            if self.temp_dir.exists() and not any(self.temp_dir.iterdir()):
                self.temp_dir.rmdir()
                
            self.logger.info("Google Maps widget cleaned up")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def destroy(self):
        """Destroy widget and clean up."""
        self.cleanup()
        super().destroy()