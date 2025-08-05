"""Integration Example: Replacing Original Google Maps Widget with Thread-Safe Version

This file demonstrates how to integrate the new ThreadSafeGoogleMapsWidget
into the existing weather dashboard while maintaining compatibility.
"""

import logging
from typing import Optional

import customtkinter as ctk

from .thread_safe_google_maps_widget import ThreadSafeGoogleMapsWidget
from ..safe_widgets import SafeWidget
from ...services.enhanced_weather_service import EnhancedWeatherService
from ...services.config_service import ConfigService


class MapsIntegrationManager(SafeWidget):
    """Manager for integrating thread-safe maps into the dashboard."""
    
    def __init__(self, parent, weather_service: EnhancedWeatherService, 
                 config_service: ConfigService):
        super().__init__()
        
        self.parent = parent
        self.weather_service = weather_service
        self.config_service = config_service
        self.logger = logging.getLogger(__name__)
        
        # Maps widget instance
        self.maps_widget: Optional[ThreadSafeGoogleMapsWidget] = None
        
        # Initialize the maps integration
        self.safe_after_idle(self._initialize_maps)
    
    def _initialize_maps(self):
        """Initialize the thread-safe maps widget."""
        try:
            self.logger.info("Initializing thread-safe Google Maps widget...")
            
            # Create the thread-safe maps widget
            self.maps_widget = ThreadSafeGoogleMapsWidget(
                parent=self.parent,
                weather_service=self.weather_service,
                config_service=self.config_service,
                corner_radius=10,
                fg_color=("gray90", "gray13")
            )
            
            # Configure layout
            self.maps_widget.pack(fill="both", expand=True, padx=10, pady=10)
            
            self.logger.info("Thread-safe Google Maps widget initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize maps widget: {e}")
            self._show_initialization_error(str(e))
    
    def _show_initialization_error(self, error_msg: str):
        """Show error message if maps initialization fails."""
        error_frame = ctk.CTkFrame(self.parent)
        error_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        error_label = ctk.CTkLabel(
            error_frame,
            text=f"🗺️ Maps Initialization Error\n\n{error_msg}\n\nPlease check your configuration and try again.",
            font=ctk.CTkFont(size=14),
            justify="center"
        )
        error_label.pack(expand=True)
    
    def update_weather_location(self, lat: float, lng: float, zoom: int = 10):
        """Update the map location for weather display."""
        if self.maps_widget:
            self.maps_widget.update_location(lat, lng, zoom)
            self.logger.info(f"Updated map location to {lat}, {lng}")
    
    def toggle_weather_layers(self, layers: dict):
        """Toggle weather layers on the map."""
        if self.maps_widget:
            for layer_name, enabled in layers.items():
                self.maps_widget.toggle_weather_layer(layer_name, enabled)
            self.logger.info(f"Updated weather layers: {layers}")
    
    def cleanup(self):
        """Clean up the maps integration."""
        try:
            if self.maps_widget:
                self.maps_widget.cleanup()
                self.maps_widget = None
            
            self.cleanup_after_callbacks()
            self.logger.info("Maps integration cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during maps cleanup: {e}")


# Example: Updating the main dashboard to use thread-safe maps
class UpdatedProfessionalWeatherDashboard:
    """Example of how to update the main dashboard class."""
    
    def __init__(self):
        # ... existing initialization code ...
        
        # Replace the original maps widget creation with:
        self._setup_thread_safe_maps()
    
    def _setup_thread_safe_maps(self):
        """Set up the thread-safe maps widget."""
        try:
            # Create maps tab frame (if using tabs)
            self.maps_frame = ctk.CTkFrame(self.main_notebook)
            self.main_notebook.add(self.maps_frame, text="🗺️ Maps")
            
            # Initialize the maps integration manager
            self.maps_manager = MapsIntegrationManager(
                parent=self.maps_frame,
                weather_service=self.weather_service,
                config_service=self.config_service
            )
            
            # Store reference for cleanup
            self._cleanup_managers.append(self.maps_manager)
            
            self.logger.info("Thread-safe maps integration set up")
            
        except Exception as e:
            self.logger.error(f"Failed to set up maps integration: {e}")
    
    def _on_location_changed(self, lat: float, lng: float):
        """Handle location changes from other parts of the dashboard."""
        # Update maps location when user selects a new location
        if hasattr(self, 'maps_manager') and self.maps_manager:
            self.maps_manager.update_weather_location(lat, lng)
    
    def _on_weather_layers_changed(self, layers: dict):
        """Handle weather layer toggle changes."""
        # Update maps layers when user toggles weather overlays
        if hasattr(self, 'maps_manager') and self.maps_manager:
            self.maps_manager.toggle_weather_layers(layers)
    
    def cleanup(self):
        """Clean up all dashboard components."""
        try:
            # Clean up maps manager
            if hasattr(self, 'maps_manager') and self.maps_manager:
                self.maps_manager.cleanup()
            
            # ... existing cleanup code ...
            
        except Exception as e:
            self.logger.error(f"Error during dashboard cleanup: {e}")


# Example: Direct replacement in maps_tab_manager.py
class ThreadSafeMapsTabManager:
    """Thread-safe replacement for the original MapsTabManager."""
    
    def __init__(self, parent, weather_service: EnhancedWeatherService, 
                 config_service: ConfigService):
        self.parent = parent
        self.weather_service = weather_service
        self.config_service = config_service
        self.logger = logging.getLogger(__name__)
        
        # Create the main container
        self.main_frame = ctk.CTkFrame(parent)
        self.main_frame.pack(fill="both", expand=True)
        
        # Initialize thread-safe maps
        self.maps_widget = ThreadSafeGoogleMapsWidget(
            parent=self.main_frame,
            weather_service=weather_service,
            config_service=config_service
        )
        self.maps_widget.pack(fill="both", expand=True)
        
        self.logger.info("Thread-safe maps tab manager initialized")
    
    def get_frame(self):
        """Get the main frame for the maps tab."""
        return self.main_frame
    
    def update_location(self, lat: float, lng: float, zoom: int = 10):
        """Update map location."""
        self.maps_widget.update_location(lat, lng, zoom)
    
    def toggle_layer(self, layer_name: str, enabled: bool):
        """Toggle a weather layer."""
        self.maps_widget.toggle_weather_layer(layer_name, enabled)
    
    def refresh_map(self):
        """Refresh the map display."""
        self.maps_widget._safe_refresh_map()
    
    def cleanup(self):
        """Clean up the maps tab."""
        if self.maps_widget:
            self.maps_widget.cleanup()
        self.logger.info("Maps tab manager cleaned up")


# Migration helper function
def migrate_to_thread_safe_maps(dashboard_instance):
    """Helper function to migrate existing dashboard to thread-safe maps."""
    logger = logging.getLogger(__name__)
    
    try:
        # Check if dashboard has existing maps components
        if hasattr(dashboard_instance, 'maps_tab_manager'):
            # Clean up old maps manager
            if hasattr(dashboard_instance.maps_tab_manager, 'cleanup'):
                dashboard_instance.maps_tab_manager.cleanup()
            
            # Replace with thread-safe version
            dashboard_instance.maps_tab_manager = ThreadSafeMapsTabManager(
                parent=dashboard_instance.maps_frame,
                weather_service=dashboard_instance.weather_service,
                config_service=dashboard_instance.config_service
            )
            
            logger.info("Successfully migrated to thread-safe maps")
            return True
            
    except Exception as e:
        logger.error(f"Failed to migrate to thread-safe maps: {e}")
        return False
    
    return False


# Configuration validation
def validate_maps_configuration(config_service: ConfigService) -> bool:
    """Validate that maps configuration is properly set up."""
    logger = logging.getLogger(__name__)
    
    try:
        # Check for Google Maps API key
        api_key = config_service.get_setting("api.google_maps_api_key")
        if not api_key or api_key.strip() == "":
            logger.warning("Google Maps API key not configured")
            return False
        
        # Check for required dependencies
        try:
            import tkinterweb
            logger.info("tkinterweb available for maps integration")
        except ImportError:
            logger.warning("tkinterweb not available - maps will use fallback")
        
        try:
            import webview
            logger.info("webview available for enhanced maps")
        except ImportError:
            logger.info("webview not available - using tkinterweb only")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating maps configuration: {e}")
        return False


if __name__ == "__main__":
    # Example usage
    import sys
    import os
    
    # Add project root to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Thread-safe maps integration example ready")
    
    # This would be used in the actual dashboard initialization
    print("Thread-safe Google Maps widget integration example")
    print("Use the classes above to replace existing maps components")