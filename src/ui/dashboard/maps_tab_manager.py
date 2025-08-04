import customtkinter as ctk
from typing import Optional, Dict, Any, List, Callable
import logging
import threading
import time
from datetime import datetime, timedelta

# Import static maps component
try:
    from ..components.static_maps_component import StaticMapsComponent
    STATIC_MAPS_AVAILABLE = True
except ImportError as e:
    logging.getLogger(__name__).warning(f"Static maps not available: {e}")
    STATIC_MAPS_AVAILABLE = False

class ThreadSafeMapsTabManager:
    """Simple maps tab manager using static Google Maps."""
    
    def __init__(self, parent, weather_service, config_service):
        self.parent = parent
        self.weather_service = weather_service
        self.config_service = config_service
        self.logger = logging.getLogger(__name__)
        
        # Maps component
        self.maps_component = None
        self._shutdown_event = threading.Event()
        
        # Public access to shutdown event for external cleanup
        self.shutdown_event = self._shutdown_event
        
        # Initialize UI
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the maps interface using static Google Maps."""
        # Create main container
        self.main_frame = ctk.CTkFrame(
            self.parent,
            fg_color=("#F8F9FA", "#1A1A1A"),
            corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # Create maps component if available
        if STATIC_MAPS_AVAILABLE:
            try:
                self.maps_component = StaticMapsComponent(self.main_frame)
                self.maps_component.pack(fill="both", expand=True)
                self.logger.info("Static maps component loaded successfully")
            except Exception as e:
                self.logger.error(f"Failed to load static maps component: {e}")
                self._create_fallback_ui()
        else:
            self._create_fallback_ui()
    
    def _create_fallback_ui(self):
        """Create fallback UI when maps are not available."""
        fallback_label = ctk.CTkLabel(
            self.main_frame,
            text="Maps functionality is currently unavailable.\nPlease check your Google Maps API key configuration.",
            font=("Arial", 16),
            text_color=("#666666", "#CCCCCC")
        )
        fallback_label.pack(expand=True)
        
    def get_current_location(self):
        """Get the current location from the maps component."""
        if self.maps_component:
            return self.maps_component.get_current_location()
        return None
    
    def set_location(self, latitude, longitude, zoom=None):
        """Set the location on the maps component."""
        if self.maps_component:
            self.maps_component.set_location(latitude, longitude, zoom)
    
    def search_location(self, query):
        """Search for a location using the maps component."""
        if self.maps_component:
            self.maps_component.search_location(query)

    def cleanup(self):
        """Clean up resources when the tab is closed."""
        try:
            # Signal shutdown
            self._shutdown_event.set()
            
            # Clean up maps component
            if self.maps_component:
                if hasattr(self.maps_component, 'cleanup'):
                    self.maps_component.cleanup()
                self.maps_component = None
            
            self.logger.info("Maps tab manager cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")