"""Static Maps Component - Google Maps Static API Integration

Provides location selection, place search, and static map visualization
for the weather dashboard application using Google Maps Static API.
"""

import tkinter as tk
import customtkinter as ctk
from typing import Optional, List, Callable, Tuple
import threading
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import logging

from ..theme import DataTerminalTheme
from ...services.google_maps_service import GoogleMapsService, PlaceResult, GeocodeResult, DirectionsResult
from ...services.config_service import ConfigService


class StaticMapsComponent(ctk.CTkFrame):
    """Static maps component with Google Maps integration."""
    
    def __init__(self, parent, config_service: ConfigService, on_location_selected: Optional[Callable] = None, **kwargs):
        """Initialize maps component."""
        super().__init__(parent, **kwargs)
        
        self.config_service = config_service
        self.on_location_selected = on_location_selected
        self.logger = logging.getLogger(__name__)
        
        # Initialize Google Maps service
        self.maps_service = GoogleMapsService(config_service)
        
        # Component state
        self.selected_place: Optional[PlaceResult] = None
        self.current_location: Optional[Tuple[float, float]] = None
        self.current_address: str = ""
        self.search_results: List[PlaceResult] = []
        
        # Theme colors
        self.BACKGROUND = DataTerminalTheme.BACKGROUND
        self.SURFACE = DataTerminalTheme.SURFACE
        self.PRIMARY = DataTerminalTheme.PRIMARY
        self.TEXT_PRIMARY = DataTerminalTheme.TEXT_PRIMARY
        self.TEXT_SECONDARY = DataTerminalTheme.TEXT_SECONDARY
        self.BORDER = DataTerminalTheme.BORDER
        
        # Setup UI
        self._setup_ui()
        
        # Load default location
        self._load_default_location()
    
    def _setup_ui(self) -> None:
        """Setup the user interface."""
        self.configure(
            fg_color=self.BACKGROUND,
            corner_radius=12,
            border_width=1,
            border_color=self.BORDER
        )
        
        # Create widgets
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create all UI widgets."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header section
        self._create_header()
        
        # Main content area
        self._create_main_content()
    
    def _create_header(self) -> None:
        """Create header with search functionality."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="🗺️ Location Search",
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_LARGE, "bold"),
            text_color=self.PRIMARY
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Search entry
        self.search_entry = ctk.CTkEntry(
            header_frame,
            placeholder_text="Search for places, addresses, or landmarks...",
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL),
            height=40,
            fg_color=self.SURFACE,
            border_color=self.BORDER
        )
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self._on_search())
        
        # Search button
        self.search_button = ctk.CTkButton(
            header_frame,
            text="🔍 Search",
            command=self._on_search,
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL),
            height=40,
            width=100,
            fg_color=self.PRIMARY,
            hover_color=DataTerminalTheme.PRIMARY_HOVER
        )
        self.search_button.grid(row=1, column=1, padx=(0, 10))
        
        # Current location button
        self.current_location_button = ctk.CTkButton(
            header_frame,
            text="📍 Current",
            command=self._get_current_location,
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL),
            height=40,
            width=100,
            fg_color=self.SURFACE,
            hover_color=DataTerminalTheme.SURFACE_HOVER,
            text_color=self.TEXT_PRIMARY,
            border_width=1,
            border_color=self.BORDER
        )
        self.current_location_button.grid(row=1, column=2)
    
    def _create_main_content(self) -> None:
        """Create main content area with search results and map."""
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_frame.grid_columnconfigure(1, weight=2)  # Map gets more space
        main_frame.grid_rowconfigure(0, weight=1)
        
        # Left panel - Search results
        self._create_search_results_panel(main_frame)
        
        # Right panel - Map display
        self._create_map_panel(main_frame)
    
    def _create_search_results_panel(self, parent) -> None:
        """Create search results panel."""
        results_container = ctk.CTkFrame(
            parent,
            fg_color=self.SURFACE,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER
        )
        results_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        results_container.grid_columnconfigure(0, weight=1)
        results_container.grid_rowconfigure(1, weight=1)
        
        # Results title
        results_title = ctk.CTkLabel(
            results_container,
            text="Search Results",
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL, "bold"),
            text_color=self.TEXT_PRIMARY
        )
        results_title.grid(row=0, column=0, pady=(15, 10))
        
        # Scrollable results frame
        self.results_frame = ctk.CTkScrollableFrame(
            results_container,
            fg_color="transparent",
            width=300,
            height=400
        )
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        # Initial message
        self._show_initial_message()
    
    def _create_map_panel(self, parent) -> None:
        """Create map display panel."""
        map_container = ctk.CTkFrame(
            parent,
            fg_color=self.SURFACE,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER
        )
        map_container.grid(row=0, column=1, sticky="nsew")
        map_container.grid_columnconfigure(0, weight=1)
        map_container.grid_rowconfigure(1, weight=1)
        
        # Map title
        map_title = ctk.CTkLabel(
            map_container,
            text="Map View",
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL, "bold"),
            text_color=self.TEXT_PRIMARY
        )
        map_title.grid(row=0, column=0, pady=(15, 10))
        
        # Map display frame
        self.map_frame = ctk.CTkFrame(
            map_container,
            fg_color=self.BACKGROUND,
            corner_radius=8
        )
        self.map_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.map_frame.grid_columnconfigure(0, weight=1)
        self.map_frame.grid_rowconfigure(0, weight=1)
        
        # Map controls
        self._create_map_controls(map_container)
        
        # Initial map placeholder
        self._show_map_placeholder("Select a location to view map")
    
    def _create_map_controls(self, parent) -> None:
        """Create map control buttons."""
        controls_frame = ctk.CTkFrame(parent, fg_color="transparent")
        controls_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 15))
        controls_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Open in browser button
        self.open_browser_button = ctk.CTkButton(
            controls_frame,
            text="🌐 Open in Browser",
            command=self._open_in_browser,
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_SMALL),
            height=32,
            fg_color=self.PRIMARY,
            hover_color=DataTerminalTheme.PRIMARY_HOVER,
            state="disabled"
        )
        self.open_browser_button.grid(row=0, column=0, padx=(0, 5))
        
        # Get directions button
        self.directions_button = ctk.CTkButton(
            controls_frame,
            text="🧭 Directions",
            command=self._get_directions,
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_SMALL),
            height=32,
            fg_color=self.SURFACE,
            hover_color=DataTerminalTheme.SURFACE_HOVER,
            text_color=self.TEXT_PRIMARY,
            border_width=1,
            border_color=self.BORDER,
            state="disabled"
        )
        self.directions_button.grid(row=0, column=1, padx=5)
        
        # Clear selection button
        self.clear_button = ctk.CTkButton(
            controls_frame,
            text="🗑️ Clear",
            command=self._clear_selection,
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_SMALL),
            height=32,
            fg_color=self.SURFACE,
            hover_color=DataTerminalTheme.SURFACE_HOVER,
            text_color=self.TEXT_PRIMARY,
            border_width=1,
            border_color=self.BORDER
        )
        self.clear_button.grid(row=0, column=2, padx=(5, 0))
    
    def _show_initial_message(self) -> None:
        """Show initial message in results area."""
        message = ctk.CTkLabel(
            self.results_frame,
            text="🔍\n\nEnter a location in the search box\nto find places and view results",
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL),
            text_color=self.TEXT_SECONDARY,
            justify="center"
        )
        message.pack(pady=50)
    
    def _on_search(self) -> None:
        """Handle search button click."""
        query = self.search_entry.get().strip()
        if not query:
            return
        
        self.logger.info(f"🔍 Searching for: {query}")
        
        # Clear previous results
        self._clear_results()
        
        # Show loading message
        loading_label = ctk.CTkLabel(
            self.results_frame,
            text="🔍 Searching...",
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL),
            text_color=self.TEXT_SECONDARY
        )
        loading_label.pack(pady=20)
        
        # Disable search button
        self.search_button.configure(state="disabled", text="Searching...")
        
        # Perform search in background thread
        threading.Thread(target=self._perform_search, args=(query,), daemon=True).start()
    
    def _perform_search(self, query: str) -> None:
        """Perform place search in background thread."""
        try:
            # Search for places
            results = self.maps_service.search_places(query)
            
            # Update UI in main thread
            self.after(0, self._update_search_results, results)
            
        except Exception as e:
            self.logger.error(f"❌ Search failed: {e}")
            self.after(0, self._show_search_error, str(e))
    
    def _update_search_results(self, results: List[PlaceResult]) -> None:
        """Update search results in UI."""
        # Re-enable search button
        self.search_button.configure(state="normal", text="🔍 Search")
        
        # Clear loading message
        self._clear_results()
        
        if not results:
            no_results = ctk.CTkLabel(
                self.results_frame,
                text="❌\n\nNo results found\nTry a different search term",
                font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL),
                text_color=self.TEXT_SECONDARY,
                justify="center"
            )
            no_results.pack(pady=50)
            return
        
        self.search_results = results
        
        # Display results
        for i, place in enumerate(results[:10]):  # Limit to 10 results
            self._create_result_card(place, i)
    
    def _create_result_card(self, place: PlaceResult, index: int) -> None:
        """Create a result card for a place."""
        card = ctk.CTkFrame(
            self.results_frame,
            fg_color=self.BACKGROUND,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER
        )
        card.pack(fill="x", pady=5, padx=5)
        
        # Place name
        name_label = ctk.CTkLabel(
            card,
            text=place.name,
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL, "bold"),
            text_color=self.TEXT_PRIMARY,
            anchor="w"
        )
        name_label.pack(fill="x", padx=10, pady=(10, 5))
        
        # Address
        address_label = ctk.CTkLabel(
            card,
            text=place.formatted_address,
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_SMALL),
            text_color=self.TEXT_SECONDARY,
            anchor="w",
            wraplength=250
        )
        address_label.pack(fill="x", padx=10, pady=(0, 5))
        
        # Rating (if available)
        if place.rating:
            rating_text = f"⭐ {place.rating}/5"
            rating_label = ctk.CTkLabel(
                card,
                text=rating_text,
                font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_SMALL),
                text_color=self.PRIMARY,
                anchor="w"
            )
            rating_label.pack(fill="x", padx=10, pady=(0, 5))
        
        # Select button
        select_button = ctk.CTkButton(
            card,
            text="📍 Select",
            command=lambda: self._select_place(place),
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_SMALL),
            height=28,
            fg_color=self.PRIMARY,
            hover_color=DataTerminalTheme.PRIMARY_HOVER
        )
        select_button.pack(pady=(0, 10))
    
    def _select_place(self, place: PlaceResult) -> None:
        """Select a place and update map."""
        self.selected_place = place
        self.current_location = (place.latitude, place.longitude)
        self.current_address = place.formatted_address
        
        self.logger.info(f"📍 Selected place: {place.name}")
        
        # Update map
        self._update_map()
        
        # Enable map controls
        self.open_browser_button.configure(state="normal")
        self.directions_button.configure(state="normal")
        
        # Notify parent component
        if self.on_location_selected:
            self.on_location_selected(place.latitude, place.longitude, place.name)
    
    def _update_map(self) -> None:
        """Update map display with current location."""
        if not self.current_location:
            return
        
        try:
            # Get static map URL
            map_url = self.maps_service.get_static_map_url(
                center=self.current_location,
                zoom=15,
                size=(500, 400),
                markers=[self.current_location]
            )
            
            if map_url:
                # Load map image in background
                threading.Thread(target=self._load_map_image, args=(map_url,), daemon=True).start()
            else:
                self._show_map_placeholder("Map unavailable")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update map: {e}")
            self._show_map_placeholder("Map error")
    
    def _load_map_image(self, url: str) -> None:
        """Load map image from URL."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Load image
            image = Image.open(BytesIO(response.content))
            photo = ImageTk.PhotoImage(image)
            
            # Update UI in main thread
            self.after(0, self._display_map_image, photo)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load map image: {e}")
            self.after(0, self._show_map_placeholder, "Failed to load map")
    
    def _display_map_image(self, photo: ImageTk.PhotoImage) -> None:
        """Display map image in UI."""
        # Clear existing content
        for widget in self.map_frame.winfo_children():
            widget.destroy()
        
        # Display map image
        map_image_label = tk.Label(
            self.map_frame,
            image=photo,
            bg=DataTerminalTheme.BACKGROUND
        )
        map_image_label.image = photo  # Keep a reference
        map_image_label.grid(row=0, column=0, padx=10, pady=10)
        
        # Add location info
        info_frame = ctk.CTkFrame(self.map_frame, fg_color="transparent")
        info_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        if self.selected_place:
            location_info = ctk.CTkLabel(
                info_frame,
                text=f"📍 {self.selected_place.name}\n{self.current_address}",
                font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_SMALL),
                text_color=self.TEXT_PRIMARY,
                justify="center"
            )
            location_info.pack(pady=5)
    
    def _show_map_placeholder(self, message: str) -> None:
        """Show placeholder message in map area."""
        # Clear existing content
        for widget in self.map_frame.winfo_children():
            widget.destroy()
        
        placeholder = ctk.CTkLabel(
            self.map_frame,
            text=f"🗺️\n\n{message}",
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_LARGE),
            text_color=self.TEXT_SECONDARY,
            justify="center"
        )
        placeholder.grid(row=0, column=0, pady=50)
    
    def _show_search_error(self, error: str) -> None:
        """Show search error message."""
        # Re-enable search button
        self.search_button.configure(state="normal", text="🔍 Search")
        
        # Clear results and show error
        self._clear_results()
        
        error_label = ctk.CTkLabel(
            self.results_frame,
            text=f"❌\n\nSearch failed\n{error}",
            font=(DataTerminalTheme.FONT_FAMILY, DataTerminalTheme.FONT_SIZE_NORMAL),
            text_color=self.TEXT_SECONDARY,
            justify="center"
        )
        error_label.pack(pady=50)
    
    def _clear_results(self) -> None:
        """Clear search results."""
        for widget in self.results_frame.winfo_children():
            widget.destroy()
    
    def _get_current_location(self) -> None:
        """Get current location (placeholder implementation)."""
        # For demo purposes, use a default location
        default_location = (40.7128, -74.0060)  # New York City
        
        self.current_location = default_location
        self.current_address = "New York, NY, USA"
        
        # Create a mock place result
        self.selected_place = PlaceResult(
            place_id="demo_nyc",
            name="New York City",
            formatted_address="New York, NY, USA",
            latitude=default_location[0],
            longitude=default_location[1],
            types=["locality", "political"]
        )
        
        self._update_map()
        
        # Enable map controls
        self.open_browser_button.configure(state="normal")
        self.directions_button.configure(state="normal")
        
        # Notify parent
        if self.on_location_selected:
            self.on_location_selected(default_location[0], default_location[1], "New York City")
    
    def _load_default_location(self) -> None:
        """Load default location on startup."""
        self._get_current_location()
    
    def _open_in_browser(self) -> None:
        """Open location in web browser."""
        if not self.current_location:
            return
        
        lat, lng = self.current_location
        url = f"https://www.google.com/maps/@{lat},{lng},15z"
        webbrowser.open(url)
    
    def _get_directions(self) -> None:
        """Get directions to selected location."""
        if not self.current_location:
            return
        
        lat, lng = self.current_location
        url = f"https://www.google.com/maps/dir//{lat},{lng}"
        webbrowser.open(url)
    
    def _clear_selection(self) -> None:
        """Clear current selection."""
        self.selected_place = None
        self.current_location = None
        self.current_address = ""
        
        # Clear results
        self._clear_results()
        self._show_initial_message()
        
        # Show map placeholder
        self._show_map_placeholder("Select a location to view map")
        
        # Disable map controls
        self.open_browser_button.configure(state="disabled")
        self.directions_button.configure(state="disabled")
        
        # Clear search entry
        self.search_entry.delete(0, "end")
    
    def set_location(self, latitude: float, longitude: float, name: str = "") -> None:
        """Programmatically set location."""
        self.current_location = (latitude, longitude)
        
        if name:
            # Create a mock place result
            self.selected_place = PlaceResult(
                place_id=f"manual_{latitude}_{longitude}",
                name=name,
                formatted_address=f"{latitude:.4f}, {longitude:.4f}",
                latitude=latitude,
                longitude=longitude,
                types=["point_of_interest"]
            )
            self.current_address = name
        else:
            # Try reverse geocoding
            threading.Thread(target=self._reverse_geocode, args=(latitude, longitude), daemon=True).start()
        
        self._update_map()
        
        # Enable map controls
        self.open_browser_button.configure(state="normal")
        self.directions_button.configure(state="normal")
    
    def _reverse_geocode(self, latitude: float, longitude: float) -> None:
        """Reverse geocode coordinates to get address."""
        try:
            result = self.maps_service.reverse_geocode(latitude, longitude)
            if result:
                self.after(0, self._update_reverse_geocode_result, result)
        except Exception as e:
            self.logger.error(f"❌ Reverse geocoding failed: {e}")
    
    def _update_reverse_geocode_result(self, result: GeocodeResult) -> None:
        """Update UI with reverse geocoding result."""
        self.current_address = result.formatted_address
        
        # Create place result
        self.selected_place = PlaceResult(
            place_id=result.place_id,
            name=result.formatted_address.split(',')[0],
            formatted_address=result.formatted_address,
            latitude=result.latitude,
            longitude=result.longitude,
            types=result.types
        )
        
        # Update map display
        self._update_map()