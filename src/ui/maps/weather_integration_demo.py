#!/usr/bin/env python3
"""
Weather Integration Demo

Demonstrates the complete integration of the thread-safe Google Maps widget
with weather data overlays and UI controls.
"""

import logging
import threading
import time
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta

import customtkinter as ctk
from .thread_safe_google_maps_widget import ThreadSafeGoogleMapsWidget
from .weather_controls_panel import WeatherControlsPanel
from .weather_map_overlay import WeatherPoint


class MockWeatherService:
    """Mock weather service for demonstration purposes."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._data_cache: Dict[str, List[WeatherPoint]] = {}
        self._last_update: Dict[str, datetime] = {}
    
    def get_weather_data(self, layer_type: str, bounds: Dict[str, float]) -> List[WeatherPoint]:
        """Generate mock weather data for the specified layer and bounds.
        
        Args:
            layer_type: Type of weather data (temperature, precipitation, etc.)
            bounds: Map bounds with 'north', 'south', 'east', 'west' keys
            
        Returns:
            List of WeatherPoint objects
        """
        # Check cache freshness (5 minutes)
        cache_key = f"{layer_type}_{bounds['north']}_{bounds['south']}_{bounds['east']}_{bounds['west']}"
        now = datetime.now()
        
        if (cache_key in self._data_cache and 
            cache_key in self._last_update and 
            (now - self._last_update[cache_key]).seconds < 300):
            return self._data_cache[cache_key]
        
        # Generate new data
        points = []
        
        # Create a grid of points within bounds
        lat_step = (bounds['north'] - bounds['south']) / 10
        lng_step = (bounds['east'] - bounds['west']) / 10
        
        for i in range(10):
            for j in range(10):
                lat = bounds['south'] + (i * lat_step) + random.uniform(-lat_step/4, lat_step/4)
                lng = bounds['west'] + (j * lng_step) + random.uniform(-lng_step/4, lng_step/4)
                
                # Generate realistic values based on layer type
                value = self._generate_value_for_layer(layer_type)
                
                point = WeatherPoint(
                    latitude=lat,
                    longitude=lng,
                    temperature=value if layer_type == 'temperature' else random.uniform(15, 25),
                    precipitation=value if layer_type == 'precipitation' else random.uniform(0, 10),
                    wind_speed=value if layer_type == 'wind' else random.uniform(0, 20),
                    pressure=value if layer_type == 'pressure' else random.uniform(1000, 1020),
                    cloud_cover=value if layer_type == 'clouds' else random.uniform(0, 100),
                    timestamp=now
                )
                points.append(point)
        
        # Cache the data
        self._data_cache[cache_key] = points
        self._last_update[cache_key] = now
        
        self.logger.info(f"Generated {len(points)} weather points for {layer_type}")
        return points
    
    def _generate_value_for_layer(self, layer_type: str) -> float:
        """Generate a realistic value for the specified layer type."""
        if layer_type == 'temperature':
            return random.uniform(-10, 35)  # Celsius
        elif layer_type == 'precipitation':
            return random.uniform(0, 50)  # mm/hour
        elif layer_type == 'wind':
            return random.uniform(0, 30)  # km/h
        elif layer_type == 'pressure':
            return random.uniform(980, 1040)  # hPa
        elif layer_type == 'clouds':
            return random.uniform(0, 100)  # percentage
        else:
            return random.uniform(0, 100)


class WeatherIntegrationDemo(ctk.CTk):
    """Main demo application showing weather integration."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Weather Maps Integration Demo")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Initialize services
        self.weather_service = MockWeatherService()
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.maps_widget: Optional[ThreadSafeGoogleMapsWidget] = None
        self.controls_panel: Optional[WeatherControlsPanel] = None
        
        # Weather update thread
        self._weather_thread: Optional[threading.Thread] = None
        self._weather_running = False
        
        self._setup_ui()
        self._start_weather_updates()
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.logger.info("Weather integration demo initialized")
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Create controls panel (left side)
        self.controls_panel = WeatherControlsPanel(
            self,
            None,  # Will be set after maps widget is created
            width=350
        )
        self.controls_panel.grid(row=0, column=0, sticky='nsew', padx=(10, 5), pady=10)
        
        # Create maps widget (right side)
        maps_frame = ctk.CTkFrame(self, corner_radius=15)
        maps_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 10), pady=10)
        maps_frame.grid_columnconfigure(0, weight=1)
        maps_frame.grid_rowconfigure(1, weight=1)
        
        # Maps header
        maps_header = ctk.CTkLabel(
            maps_frame,
            text="Interactive Weather Map",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        maps_header.grid(row=0, column=0, pady=(15, 10))
        
        # Initialize maps widget
        self.maps_widget = ThreadSafeGoogleMapsWidget(
            maps_frame,
            width=800,
            height=600
        )
        self.maps_widget.grid(row=1, column=0, sticky='nsew', padx=15, pady=(0, 15))
        
        # Connect controls panel to maps widget
        self.controls_panel.maps_widget = self.maps_widget
        
        # Add weather data update callback
        self._setup_weather_callbacks()
    
    def _setup_weather_callbacks(self):
        """Set up callbacks for weather data updates."""
        if not self.maps_widget:
            return
        
        # Add click handler for weather queries
        def on_map_click(lat: float, lng: float):
            """Handle map clicks to show weather at location."""
            self.logger.info(f"Map clicked at {lat:.4f}, {lng:.4f}")
            
            # Get weather data for the clicked location
            bounds = {
                'north': lat + 0.1,
                'south': lat - 0.1,
                'east': lng + 0.1,
                'west': lng - 0.1
            }
            
            # Update status in controls panel
            if self.controls_panel:
                self.controls_panel._update_main_status(
                    f"Weather query at {lat:.3f}, {lng:.3f}"
                )
        
        self.maps_widget.add_click_handler('weather_query', on_map_click)
    
    def _start_weather_updates(self):
        """Start the weather data update thread."""
        self._weather_running = True
        self._weather_thread = threading.Thread(
            target=self._weather_update_loop,
            daemon=True
        )
        self._weather_thread.start()
        self.logger.info("Weather update thread started")
    
    def _weather_update_loop(self):
        """Main weather data update loop."""
        while self._weather_running:
            try:
                if self.maps_widget and self.controls_panel:
                    # Get current map bounds
                    current_location = self.maps_widget.get_current_location()
                    if current_location:
                        lat, lng = current_location
                        
                        # Define bounds around current view
                        bounds = {
                            'north': lat + 0.5,
                            'south': lat - 0.5,
                            'east': lng + 0.5,
                            'west': lng - 0.5
                        }
                        
                        # Update active layers
                        layer_states = self.controls_panel.get_layer_states()
                        for layer_type, enabled in layer_states.items():
                            if enabled:
                                self._update_weather_layer(layer_type, bounds)
                
                # Wait before next update
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Weather update error: {e}")
                time.sleep(10)  # Wait before retrying
    
    def _update_weather_layer(self, layer_type: str, bounds: Dict[str, float]):
        """Update a specific weather layer.
        
        Args:
            layer_type: Type of weather layer
            bounds: Map bounds for data retrieval
        """
        try:
            # Get weather data
            weather_points = self.weather_service.get_weather_data(layer_type, bounds)
            
            if weather_points and self.maps_widget:
                # Update the maps widget with new data
                self.maps_widget.update_weather_data(layer_type, weather_points)
                
                # Update controls panel status
                if self.controls_panel:
                    self.controls_panel.update_weather_data_status(
                        layer_type, len(weather_points)
                    )
                
                self.logger.debug(f"Updated {layer_type} layer with {len(weather_points)} points")
        
        except Exception as e:
            self.logger.error(f"Failed to update {layer_type} layer: {e}")
    
    def _on_closing(self):
        """Handle application closing."""
        self.logger.info("Shutting down weather integration demo")
        
        # Stop weather updates
        self._weather_running = False
        if self._weather_thread and self._weather_thread.is_alive():
            self._weather_thread.join(timeout=2)
        
        # Cleanup components
        if self.controls_panel:
            self.controls_panel.cleanup()
        
        if self.maps_widget:
            self.maps_widget.cleanup()
        
        self.destroy()


def main():
    """Main entry point for the demo."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('weather_integration_demo.log')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting weather integration demo")
    
    try:
        # Create and run the demo application
        app = WeatherIntegrationDemo()
        app.mainloop()
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        logger.info("Demo finished")


if __name__ == "__main__":
    main()