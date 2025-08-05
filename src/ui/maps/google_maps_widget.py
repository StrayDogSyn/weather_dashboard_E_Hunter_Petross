"""Google Maps Widget for Weather Dashboard.

Provides Google Maps JavaScript API integration with weather overlays.
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any

import customtkinter as ctk
# import tkinterweb  # COMMENTED OUT FOR DEBUGGING - Step 2
# import webview      # COMMENTED OUT FOR DEBUGGING - Step 2
import threading
import time

from ...services.enhanced_weather_service import EnhancedWeatherService
from ..theme import DataTerminalTheme


class GoogleMapsWidget(ctk.CTkFrame):
    """Google Maps widget with weather integration."""

    def __init__(self, parent, weather_service: EnhancedWeatherService, config_service=None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.weather_service = weather_service
        self.config_service = config_service
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("=== INITIALIZING GOOGLE MAPS WIDGET ===")
        
        # Get Google Maps API key
        self.api_key = self._get_google_maps_api_key()
        self.logger.info(f"API key retrieved: {self.api_key[:10] if self.api_key else 'None'}...")
        
        # Current map state
        self.current_location = {"lat": 40.7128, "lng": -74.0060}  # Default to NYC
        self.current_zoom = 10
        self.active_layers = set()
        
        # Temporary file for map HTML
        self.temp_dir = Path(tempfile.gettempdir()) / "google_maps"
        self.logger.info(f"Creating temp directory: {self.temp_dir}")
        self.temp_dir.mkdir(exist_ok=True)
        self.logger.info(f"Temp directory created successfully: {self.temp_dir.exists()}")
        self.current_map_file = None
        
        # Track scheduled after() calls for cleanup
        self.scheduled_calls = set()
        
        # Setup UI
        self.logger.info("Setting up UI components...")
        self._setup_ui()
        
        # Load initial map
        self.logger.info("Loading initial map...")
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
        
        # Create container for webview
        self.webview_container = ctk.CTkFrame(map_container, fg_color="white")
        self.webview_container.grid(row=0, column=0, sticky="nsew")
        
        # DEBUGGING STEP 2: Replace tkinterweb with standard CTkFrame
        try:
            # self.map_webview = tkinterweb.HtmlFrame(self.webview_container)  # COMMENTED OUT
            self.map_webview = ctk.CTkFrame(self.webview_container, fg_color="#2b2b2b")
            self.map_webview.pack(fill="both", expand=True)
            
            # Add placeholder content
            placeholder_label = ctk.CTkLabel(
                self.map_webview,
                text="🗺️ Google Maps Widget\n(tkinterweb replaced with CTkFrame for debugging)",
                font=(DataTerminalTheme.FONT_FAMILY, 16),
                text_color=DataTerminalTheme.TEXT
            )
            placeholder_label.pack(expand=True)
            
            self.logger.info("DEBUG: TkinterWeb replaced with CTkFrame successfully")
        except Exception as e:
            self.logger.error(f"Failed to create replacement frame: {e}")
            self.map_webview = None
        
        self.webview_window = None
        self.logger.info("Map container created successfully")
    
    def _load_initial_map(self):
        """Load the initial Google Maps view using pywebview"""
        try:
            self.logger.info("Starting initial Google Maps load...")
            self.logger.info(f"Temp directory: {self.temp_dir}")
            self.logger.info(f"Temp directory exists: {self.temp_dir.exists()}")
            
            self._create_google_maps_html()
            
            # Start pywebview in a separate thread
            if self.current_map_file and self.current_map_file.exists():
                self.logger.info(f"HTML file created successfully: {self.current_map_file}")
                self.logger.info(f"HTML file size: {self.current_map_file.stat().st_size} bytes")
                self._start_webview(str(self.current_map_file))
                self.logger.info(f"Google Maps HTML file loaded: {self.current_map_file}")
                
                # Check map loading after a delay
                self.safe_after(3000, self._check_map_loading)
            else:
                self.logger.error(f"HTML file not found: {self.current_map_file}")
                self._show_fallback_map("HTML file not found")
                
        except Exception as e:
            self.logger.error(f"Failed to load initial map: {e}")
            self._show_fallback_map(str(e))
    
    def _create_google_maps_html(self):
        """Create Google Maps HTML with weather overlays."""
        self.logger.info(f"Creating Google Maps HTML with API key: {self.api_key[:10]}...")
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
    

    
    def _start_webview(self, html_file_path):
        """DEBUGGING STEP 2: Skip HTML loading since tkinterweb is replaced"""
        try:
            if self.map_webview:
                self.logger.info(f"DEBUG: Skipping HTML file loading (tkinterweb replaced): {html_file_path}")
                # Update placeholder content to show it's working
                for child in self.map_webview.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text="🗺️ Google Maps Widget\n(tkinterweb replaced - map loading skipped)\n✅ Widget created successfully")
                self.logger.info("DEBUG: Placeholder content updated successfully")
            else:
                self.logger.warning("DEBUG: Replacement widget not available")
                self._show_webview_fallback()
        except Exception as e:
            self.logger.error(f"DEBUG: Failed to update replacement widget: {e}")
            self._show_webview_fallback()
    
    def _create_webview_window(self, html_file_path):
        """Legacy method - now handled by _start_webview"""
        self.logger.info("_create_webview_window called - delegating to _start_webview")
        self._start_webview(html_file_path)
    
    def _check_map_loading(self):
        """Check the status of map loading and provide diagnostic information"""
        try:
            self.logger.info("=== MAP LOADING STATUS CHECK ===")
            
            # Check if HTML file still exists
            if self.current_map_file and self.current_map_file.exists():
                self.logger.info(f"✓ HTML file exists: {self.current_map_file}")
                
                # Read HTML content to verify it was created properly
                with open(self.current_map_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.logger.info(f"✓ HTML file size: {len(content)} characters")
                    
                    # Check for key elements
                    if 'google.maps.Map' in content:
                        self.logger.info("✓ Google Maps API initialization code found")
                    else:
                        self.logger.warning("⚠️ Google Maps API initialization code NOT found")
                        
                    if self.api_key in content:
                        self.logger.info("✓ API key properly embedded in HTML")
                    else:
                        self.logger.warning("⚠️ API key NOT found in HTML")
                        
            else:
                self.logger.error("✗ HTML file does not exist or was deleted")
            
            # Check webview container status
            children = self.webview_container.winfo_children()
            self.logger.info(f"Webview container has {len(children)} child widgets")
            
            # Check if pywebview window exists
            if hasattr(self, 'webview_window') and self.webview_window:
                self.logger.info("✓ Pywebview window object exists")
            else:
                self.logger.warning("⚠️ Pywebview window object is None or missing")
                
            # Schedule another check if needed
            call_id = self.safe_after(5000, self._check_map_loading_followup)
            if call_id:
                self.scheduled_calls.add(call_id)
            
        except Exception as e:
            self.logger.error(f"Error during map loading check: {e}")
    
    def _check_map_loading_followup(self):
        """Follow-up check for map loading status"""
        try:
            self.logger.info("=== FOLLOW-UP MAP STATUS CHECK ===")
            
            # Check if we should show fallback
            children = self.webview_container.winfo_children()
            if len(children) == 0:
                self.logger.warning("⚠️ No widgets in webview container - showing fallback")
                self._show_webview_fallback()
            else:
                self.logger.info(f"✓ Webview container has {len(children)} widgets")
                
        except Exception as e:
            self.logger.error(f"Error during follow-up check: {e}")
    
    def _show_webview_fallback(self):
        """Show fallback message when webview fails"""
        try:
            self.logger.info("Showing webview fallback message")
            # Clear the container and show a message
            for widget in self.webview_container.winfo_children():
                widget.destroy()
            
            fallback_label = ctk.CTkLabel(
                self.webview_container,
                text="🗺️ Google Maps\n\nA separate window should open with the interactive map.\nIf no window appears, please check your system settings.",
                font=("Arial", 14),
                justify="center"
            )
            fallback_label.pack(expand=True, fill="both", padx=20, pady=20)
            
        except Exception as e:
            self.logger.error(f"Failed to show webview fallback: {e}")
    
    def _check_map_loading(self):
        """Check if the map has loaded properly and log debugging information"""
        try:
            self.logger.info("Checking map loading status...")
            
            if not self.webview_window:
                self.logger.warning("Webview window is None")
                return
                
            # Check if webview supports JavaScript execution
            try:
                # Test JavaScript execution
                result = self.webview_window.evaluate_js('typeof initMap')
                self.logger.info(f"JavaScript execution test result: {result}")
                
                if result == 'function':
                    self.logger.info("Google Maps initMap function is available")
                else:
                    self.logger.warning("initMap function not found in JavaScript context")
                    
            except Exception as js_error:
                self.logger.error(f"JavaScript execution failed: {js_error}")
            
            # Check if HTML file contains the necessary components
            if self.current_map_file and self.current_map_file.exists():
                with open(self.current_map_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    if 'initMap' in html_content and self.api_key in html_content:
                        self.logger.info("HTML file contains initMap function and valid API key")
                    else:
                        self.logger.warning("HTML file missing initMap function or API key")
            
        except Exception as e:
            self.logger.error(f"Error checking map loading: {e}")
    
    def _show_fallback_map(self, error_msg: str):
        """Show fallback content when Google Maps cannot be displayed."""
        try:
            if self.map_webview:
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
            if self.current_map_file and self.current_map_file.exists():
                self._start_webview(str(self.current_map_file))
            self.logger.info("Map refreshed")
        except Exception as e:
            self.logger.error(f"Failed to refresh map: {e}")
    
    def _enable_measurement(self):
        """Enable distance measurement tool."""
        self.logger.info("Measurement tool activated (feature available in full version)")
    
    def _change_map_style(self):
        """Change map style."""
        self.logger.info("Map style change (feature available in full version)")
    
    def safe_after(self, delay, callback):
        """Safe after() call that tracks scheduled calls for cleanup."""
        try:
            call_id = self.after(delay, callback)
            self.scheduled_calls.add(call_id)
            return call_id
        except Exception as e:
            self.logger.error(f"Error scheduling after() call: {e}")
            return None
    
    def cleanup(self):
        """Clean up resources."""
        try:
            # Cancel all scheduled after() calls
            for call_id in self.scheduled_calls.copy():
                try:
                    self.after_cancel(call_id)
                except Exception:
                    pass  # Call may have already executed
            self.scheduled_calls.clear()
            
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