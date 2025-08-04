import customtkinter as ctk
from tkinter import ttk
import tkintermapview
from typing import Optional, Dict, Any
import logging

class MapsTabManager:
    def __init__(self, parent, weather_service, config_service):
        self.parent = parent
        self.weather_service = weather_service
        self.config_service = config_service
        self.logger = logging.getLogger(__name__)
        
        # Initialize map widget with fallback
        self.map_widget = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the maps interface with error handling"""
        # Create main container
        self.main_frame = ctk.CTkFrame(self.parent)
        self.main_frame.pack(fill="both", expand=True)
        
        # Try to create map widget with multiple fallbacks
        self.create_map_widget()
        
    def create_map_widget(self):
        """Create map widget with fallback options"""
        try:
            # Option 1: Try tkintermapview
            self.try_tkintermapview()
            
        except Exception as e:
            self.logger.error(f"tkintermapview failed: {e}")
            
            # Option 2: Try embedded HTML map
            try:
                self.try_html_map()
            except Exception as e2:
                self.logger.error(f"HTML map failed: {e2}")
                
                # Option 3: Static map fallback
                self.create_static_map_fallback()
 
    def try_tkintermapview(self):
        """Try to create tkintermapview widget"""
        import tkintermapview
        
        self.map_widget = tkintermapview.TkinterMapView(
            self.main_frame,
            width=800,
            height=600,
            corner_radius=10
        )
        self.map_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Set default position (London)
        self.map_widget.set_position(51.5074, -0.1278)
        self.map_widget.set_zoom(10)
        
        # Use OpenStreetMap tile server (no API key needed)
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        
        self.logger.info("tkintermapview loaded successfully")
 
    def try_html_map(self):
        """Create HTML-based map using tkinterweb"""
        try:
            from tkinterweb import HtmlFrame
            
            self.map_frame = HtmlFrame(self.main_frame)
            self.map_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create simple Leaflet map HTML
            map_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css"/>
                <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
                <style>
                    body { margin: 0; padding: 0; }
                    #map { height: 100vh; width: 100%; }
                </style>
            </head>
            <body>
                <div id="map"></div>
                <script>
                    var map = L.map('map').setView([51.505, -0.09], 10);
                    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: 'OpenStreetMap contributors'
                    }).addTo(map);
                    
                    // Add weather layer placeholder
                    var weatherInfo = L.control({position: 'topright'});
                    weatherInfo.onAdd = function(map) {
                        var div = L.DomUtil.create('div', 'weather-info');
                        div.innerHTML = '<div style="background:white;padding:10px;border-radius:5px;">Weather Layers Available</div>';
                        return div;
                    };
                    weatherInfo.addTo(map);
                </script>
            </body>
            </html>
            """
            
            self.map_frame.load_html(map_html)
            self.logger.info("HTML map loaded successfully")
            
        except ImportError:
            raise Exception("tkinterweb not available")
 
    def create_static_map_fallback(self):
        """Create a static map display as final fallback"""
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
        
        self.logger.info("Static map fallback created")
 
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
        location_label.pack(pady=10)
        
        # Weather info grid
        info_frame = ctk.CTkFrame(self.weather_display)
        info_frame.pack(pady=10, padx=20, fill="x")
        
        # Temperature
        temp_frame = ctk.CTkFrame(info_frame)
        temp_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(temp_frame, text="🌡️ Temperature", font=("Helvetica", 14, "bold")).pack()
        ctk.CTkLabel(temp_frame, text=data.get('temperature', 'N/A'), font=("Helvetica", 16)).pack()
        
        # Condition
        condition_frame = ctk.CTkFrame(info_frame)
        condition_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(condition_frame, text="☁️ Condition", font=("Helvetica", 14, "bold")).pack()
        ctk.CTkLabel(condition_frame, text=data.get('condition', 'N/A'), font=("Helvetica", 16)).pack()
        
        # Humidity
        humidity_frame = ctk.CTkFrame(info_frame)
        humidity_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(humidity_frame, text="💧 Humidity", font=("Helvetica", 14, "bold")).pack()
        ctk.CTkLabel(humidity_frame, text=data.get('humidity', 'N/A'), font=("Helvetica", 16)).pack()
        
        # Wind
        wind_frame = ctk.CTkFrame(info_frame)
        wind_frame.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        ctk.CTkLabel(wind_frame, text="💨 Wind", font=("Helvetica", 14, "bold")).pack()
        ctk.CTkLabel(wind_frame, text=data.get('wind', 'N/A'), font=("Helvetica", 16)).pack()
        
        # Configure grid weights
        info_frame.grid_columnconfigure(0, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
    
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