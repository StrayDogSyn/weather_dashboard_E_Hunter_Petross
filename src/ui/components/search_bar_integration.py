import customtkinter as ctk
from typing import List, Dict, Any
import threading
import time

# Import EnhancedSearchBar - will be handled by the demo script
try:
    from enhanced_search_bar import EnhancedSearchBar
except ImportError:
    # Fallback for when running as module
    from .enhanced_search_bar import EnhancedSearchBar

class SearchBarIntegration:
    """Integration class to connect EnhancedSearchBar with weather dashboard features"""
    
    def __init__(self, dashboard_instance):
        self.dashboard = dashboard_instance
        self.search_bar = None
        
    def create_search_bar(self, parent) -> EnhancedSearchBar:
        """Create and configure the enhanced search bar"""
        self.search_bar = EnhancedSearchBar(parent)
        
        # Register all feature callbacks
        self.register_callbacks()
        
        return self.search_bar
    
    def register_callbacks(self):
        """Register callbacks for all search features"""
        if not self.search_bar:
            return
        
        # Basic search callback
        self.search_bar.register_callback('search', self.handle_city_search)
        
        # Comparison callback
        self.search_bar.register_callback('compare', self.handle_city_comparison)
        
        # Analysis callback
        self.search_bar.register_callback('analyze', self.handle_ai_analysis)
        
        # Map view callback
        self.search_bar.register_callback('map', self.handle_map_view)
        
        # Weather search callback
        self.search_bar.register_callback('weather', self.handle_weather_search)
        
        # Weather condition search callback
        self.search_bar.register_callback('condition', self.handle_condition_search)
    
    def handle_city_search(self, city: str):
        """Handle basic city search"""
        try:
            # Update main weather display
            if hasattr(self.dashboard, 'weather_service'):
                threading.Thread(
                    target=self._async_weather_update,
                    args=(city,),
                    daemon=True
                ).start()
            
            # Update status
            self.search_bar.update_status(f"Loading weather for {city}...")
            
        except Exception as e:
            self.search_bar.update_status(f"Error searching for {city}: {str(e)}")
    
    def handle_city_comparison(self, cities: List[str]):
        """Handle multi-city comparison"""
        try:
            if len(cities) < 2:
                self.search_bar.update_status("Need at least 2 cities to compare")
                return
            
            # Switch to analytics tab if available
            if hasattr(self.dashboard, 'notebook'):
                # Find analytics tab
                for i in range(self.dashboard.notebook.index('end')):
                    tab_text = self.dashboard.notebook.tab(i, 'text')
                    if 'Analytics' in tab_text or 'Compare' in tab_text:
                        self.dashboard.notebook.select(i)
                        break
            
            # Trigger comparison in analytics component
            if hasattr(self.dashboard, 'analytics_component'):
                threading.Thread(
                    target=self._async_comparison,
                    args=(cities,),
                    daemon=True
                ).start()
            
            self.search_bar.update_status(f"Comparing {len(cities)} cities...")
            
        except Exception as e:
            self.search_bar.update_status(f"Error comparing cities: {str(e)}")
    
    def handle_ai_analysis(self, cities: List[str]):
        """Handle AI analysis request"""
        try:
            # Switch to activities tab if available
            if hasattr(self.dashboard, 'notebook'):
                for i in range(self.dashboard.notebook.index('end')):
                    tab_text = self.dashboard.notebook.tab(i, 'text')
                    if 'Activities' in tab_text or 'AI' in tab_text:
                        self.dashboard.notebook.select(i)
                        break
            
            # Trigger AI analysis
            if hasattr(self.dashboard, 'activity_service'):
                threading.Thread(
                    target=self._async_ai_analysis,
                    args=(cities,),
                    daemon=True
                ).start()
            
            self.search_bar.update_status(f"Starting AI analysis for {', '.join(cities)}...")
            
        except Exception as e:
            self.search_bar.update_status(f"Error starting AI analysis: {str(e)}")
    
    def handle_map_view(self, location: str):
        """Handle map view request"""
        try:
            # Switch to maps tab
            if hasattr(self.dashboard, 'notebook'):
                for i in range(self.dashboard.notebook.index('end')):
                    tab_text = self.dashboard.notebook.tab(i, 'text')
                    if 'Maps' in tab_text or 'Map' in tab_text:
                        self.dashboard.notebook.select(i)
                        break
            
            # Update map location
            if hasattr(self.dashboard, 'maps_component'):
                threading.Thread(
                    target=self._async_map_update,
                    args=(location,),
                    daemon=True
                ).start()
            
            self.search_bar.update_status(f"Opening map for {location}...")
            
        except Exception as e:
            self.search_bar.update_status(f"Error opening map: {str(e)}")
    
    def handle_weather_search(self, location: str):
        """Handle weather-specific search"""
        try:
            # Same as city search but with weather focus
            self.handle_city_search(location)
            
            # Also update any weather-specific components
            if hasattr(self.dashboard, 'weather_details_component'):
                threading.Thread(
                    target=self._async_detailed_weather,
                    args=(location,),
                    daemon=True
                ).start()
            
        except Exception as e:
            self.search_bar.update_status(f"Error getting weather: {str(e)}")
    
    def handle_condition_search(self, condition: str):
        """Handle weather condition search (e.g., 'rainy cities')"""
        try:
            # This would require a more advanced weather service
            # For now, show a demo response
            demo_cities = self._get_demo_cities_by_condition(condition)
            
            if demo_cities:
                self.search_bar.update_status(
                    f"Found {condition} cities: {', '.join(demo_cities[:3])}..."
                )
                
                # Optionally trigger comparison of found cities
                if len(demo_cities) > 1:
                    self.handle_city_comparison(demo_cities[:3])
            else:
                self.search_bar.update_status(f"No {condition} cities found")
            
        except Exception as e:
            self.search_bar.update_status(f"Error searching {condition} cities: {str(e)}")
    
    def _get_demo_cities_by_condition(self, condition: str) -> List[str]:
        """Get demo cities based on weather condition"""
        condition_map = {
            'rainy': ['Seattle', 'London', 'Vancouver', 'Portland'],
            'sunny': ['Los Angeles', 'Miami', 'Phoenix', 'San Diego'],
            'cold': ['Anchorage', 'Moscow', 'Montreal', 'Minneapolis'],
            'hot': ['Phoenix', 'Las Vegas', 'Dubai', 'Death Valley']
        }
        
        return condition_map.get(condition.lower(), [])
    
    # Async methods for non-blocking operations
    def _async_weather_update(self, city: str):
        """Async weather update"""
        try:
            if hasattr(self.dashboard, 'weather_service'):
                # Simulate API call delay
                time.sleep(0.5)
                
                # Update weather data
                weather_data = self.dashboard.weather_service.get_weather(city)
                
                # Update UI on main thread
                self.dashboard.after(0, lambda: self._update_weather_ui(city, weather_data))
            
        except Exception as e:
            self.dashboard.after(0, lambda: self.search_bar.update_status(f"Failed to load weather for {city}"))
    
    def _async_comparison(self, cities: List[str]):
        """Async city comparison"""
        try:
            # Simulate comparison processing
            time.sleep(1.0)
            
            # Update UI on main thread
            self.dashboard.after(0, lambda: self._update_comparison_ui(cities))
            
        except Exception as e:
            self.dashboard.after(0, lambda: self.search_bar.update_status("Comparison failed"))
    
    def _async_ai_analysis(self, cities: List[str]):
        """Async AI analysis"""
        try:
            # Simulate AI processing
            time.sleep(2.0)
            
            # Update UI on main thread
            self.dashboard.after(0, lambda: self._update_ai_analysis_ui(cities))
            
        except Exception as e:
            self.dashboard.after(0, lambda: self.search_bar.update_status("AI analysis failed"))
    
    def _async_map_update(self, location: str):
        """Async map update"""
        try:
            # Simulate geocoding delay
            time.sleep(0.3)
            
            # Update UI on main thread
            self.dashboard.after(0, lambda: self._update_map_ui(location))
            
        except Exception as e:
            self.dashboard.after(0, lambda: self.search_bar.update_status(f"Failed to load map for {location}"))
    
    def _async_detailed_weather(self, location: str):
        """Async detailed weather update"""
        try:
            # Simulate detailed weather fetch
            time.sleep(0.7)
            
            # Update UI on main thread
            self.dashboard.after(0, lambda: self._update_detailed_weather_ui(location))
            
        except Exception as e:
            self.dashboard.after(0, lambda: self.search_bar.update_status("Failed to load detailed weather"))
    
    # UI update methods (to be called on main thread)
    def _update_weather_ui(self, city: str, weather_data):
        """Update weather UI with new data"""
        try:
            # Update main weather display
            if hasattr(self.dashboard, 'main_weather_component'):
                self.dashboard.main_weather_component.update_weather(weather_data)
            
            self.search_bar.update_status(f"Weather updated for {city}")
            
        except Exception as e:
            self.search_bar.update_status(f"Error updating weather UI: {str(e)}")
    
    def _update_comparison_ui(self, cities: List[str]):
        """Update comparison UI"""
        try:
            if hasattr(self.dashboard, 'analytics_component'):
                self.dashboard.analytics_component.compare_cities(cities)
            
            self.search_bar.update_status(f"Comparison complete for {len(cities)} cities")
            
        except Exception as e:
            self.search_bar.update_status(f"Error updating comparison UI: {str(e)}")
    
    def _update_ai_analysis_ui(self, cities: List[str]):
        """Update AI analysis UI"""
        try:
            if hasattr(self.dashboard, 'activities_component'):
                self.dashboard.activities_component.show_analysis_results(cities)
            
            self.search_bar.update_status(f"AI analysis complete for {', '.join(cities)}")
            
        except Exception as e:
            self.search_bar.update_status(f"Error updating AI analysis UI: {str(e)}")
    
    def _update_map_ui(self, location: str):
        """Update map UI"""
        try:
            if hasattr(self.dashboard, 'maps_component'):
                # Update map location
                if hasattr(self.dashboard.maps_component, 'search_location'):
                    self.dashboard.maps_component.search_location(location)
                elif hasattr(self.dashboard.maps_component, 'set_location'):
                    self.dashboard.maps_component.set_location(location)
            
            self.search_bar.update_status(f"Map updated for {location}")
            
        except Exception as e:
            self.search_bar.update_status(f"Error updating map UI: {str(e)}")
    
    def _update_detailed_weather_ui(self, location: str):
        """Update detailed weather UI"""
        try:
            # Update any detailed weather components
            self.search_bar.update_status(f"Detailed weather loaded for {location}")
            
        except Exception as e:
            self.search_bar.update_status(f"Error updating detailed weather UI: {str(e)}")


class SearchBarDemo(ctk.CTkFrame):
    """Demo application showing the enhanced search bar"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setup_demo_ui()
    
    def setup_demo_ui(self):
        """Setup demo UI"""
        # Title
        title = ctk.CTkLabel(
            self,
            text="Enhanced Search Bar Demo",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
        # Create search bar
        self.search_integration = SearchBarIntegration(self)
        self.search_bar = self.search_integration.create_search_bar(self)
        self.search_bar.pack(fill="x", padx=20, pady=10)
        
        # Demo content area
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Demo instructions
        instructions = ctk.CTkTextbox(
            self.content_frame,
            height=200,
            font=("Helvetica", 12)
        )
        instructions.pack(fill="both", expand=True, padx=10, pady=10)
        
        demo_text = """
Enhanced Search Bar Features:

1. Smart Autocomplete:
   - Type any city name for suggestions
   - Recent searches and favorites appear
   - Command suggestions when typing commands

2. Command Shortcuts:
   - compare: London, Paris, Tokyo
   - analyze: New York
   - map: San Francisco
   - weather: Miami

3. Natural Language:
   - "show me rainy cities"
   - "find sunny places"
   - "cold cities"
   - "hot weather locations"

4. Multi-City Selection:
   - Enable "Multi" checkbox
   - Add multiple cities
   - Compare them all at once

5. Quick Actions:
   - ★ Favorites menu
   - 🕐 Search history
   - Keyboard shortcuts (Ctrl+F, Ctrl+H, Ctrl+M)

6. Smart Features:
   - Auto-complete with recent searches
   - Command pattern recognition
   - Status feedback for all operations
   - Persistent search history
"""
        
        instructions.insert("1.0", demo_text)
        instructions.configure(state="disabled")


if __name__ == "__main__":
    # Demo application
    app = ctk.CTk()
    app.title("Enhanced Search Bar Demo")
    app.geometry("800x600")
    
    demo = SearchBarDemo(app)
    demo.pack(fill="both", expand=True)
    
    app.mainloop()