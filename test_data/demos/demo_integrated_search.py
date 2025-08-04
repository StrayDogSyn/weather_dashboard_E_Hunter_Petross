#!/usr/bin/env python3
"""
Integrated Search Demo - Enhanced Search Bar with SearchStateService

This demo shows how to integrate the enhanced search bar with the SearchStateService
for intelligent, persistent search functionality.

Features:
- Database-backed search history and favorites
- Smart suggestions based on user patterns
- Real-time state synchronization
- Observer pattern for UI updates
- Comprehensive analytics
"""

import tkinter as tk
import customtkinter as ctk
from pathlib import Path
import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'ui', 'components'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    import enhanced_search_bar
    from services.search_state_service import SearchStateService
    
    EnhancedSearchBar = enhanced_search_bar.EnhancedSearchBar
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the enhanced_search_bar.py file exists in src/ui/components/")
    sys.exit(1)

class IntegratedSearchDemo:
    def __init__(self):
        # Initialize services
        self.search_service = SearchStateService()
        
        # Setup UI
        self.setup_ui()
        
        # Connect search bar with service
        self.integrate_services()
        
        # Setup observers
        self.setup_observers()
        
        print("🚀 Integrated Search Demo Started")
        print("Features:")
        print("  • Smart autocomplete with database-backed suggestions")
        print("  • Persistent search history and favorites")
        print("  • Real-time analytics and pattern recognition")
        print("  • Observer-based state synchronization")
        print("\n💡 Try typing city names to see intelligent suggestions!")
    
    def setup_ui(self):
        """Setup the main UI"""
        self.root = ctk.CTk()
        self.root.title("Integrated Search Demo - Enhanced Search + State Service")
        self.root.geometry("800x600")
        
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🔍 Intelligent Search System",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Search bar container
        search_container = ctk.CTkFrame(main_frame)
        search_container.pack(fill="x", padx=20, pady=(0, 20))
        
        # Enhanced search bar
        self.search_bar = EnhancedSearchBar(
            search_container,
            width=700
        )
        self.search_bar.pack(pady=20)
        
        # Set custom placeholder text
        self.search_bar.search_entry.configure(
            placeholder_text="Search cities, compare weather, or use commands..."
        )
        
        # Info panel
        self.info_frame = ctk.CTkFrame(main_frame)
        self.info_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Current state display
        self.state_label = ctk.CTkLabel(
            self.info_frame,
            text="Current State: Ready",
            font=("Arial", 14)
        )
        self.state_label.pack(pady=(20, 10))
        
        # Statistics display
        self.stats_text = ctk.CTkTextbox(self.info_frame, height=200)
        self.stats_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Control buttons
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        ctk.CTkButton(
            button_frame,
            text="📊 Show Statistics",
            command=self.show_statistics
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="⭐ Show Favorites",
            command=self.show_favorites
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="🔄 Clear History",
            command=self.clear_history
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            button_frame,
            text="💾 Export Data",
            command=self.export_data
        ).pack(side="left")
    
    def integrate_services(self):
        """Integrate search bar with state service"""
        # Override search bar's suggestion method
        original_get_suggestions = self.search_bar.get_suggestions
        
        def enhanced_get_suggestions(query):
            """Get suggestions from both built-in and service"""
            # Get built-in suggestions
            builtin_suggestions = original_get_suggestions(query)
            
            # Get smart suggestions from service
            smart_suggestions = self.search_service.get_smart_suggestions(query)
            
            # Combine and format suggestions
            combined = []
            
            # Add smart suggestions first (higher priority)
            for suggestion in smart_suggestions:
                combined.append({
                    'text': f"{suggestion['icon']} {suggestion['text']}",
                    'value': suggestion['text'],
                    'type': suggestion['type']
                })
            
            # Add built-in suggestions
            for suggestion in builtin_suggestions:
                if suggestion not in [s['value'] for s in combined]:
                    combined.append({
                        'text': f"🌍 {suggestion}",
                        'value': suggestion,
                        'type': 'builtin'
                    })
            
            return combined[:10]  # Limit to 10 suggestions
        
        # Replace the method
        self.search_bar.get_suggestions = enhanced_get_suggestions
        
        # Register search callback
        def on_search(query, cities):
            """Handle search events"""
            mode = "single" if len(cities) <= 1 else "multi"
            if query.startswith("compare:"):
                mode = "command"
            
            # Update service state
            self.search_service.update_search(query, cities, mode)
            
            # Update UI
            self.update_state_display(query, cities, mode)
        
        self.search_bar.register_callback('search', on_search)
    
    def setup_observers(self):
        """Setup state change observers"""
        def on_state_change(state):
            """Handle state changes from service"""
            print(f"🔔 State Change: {state['query']} | Cities: {state['cities']} | Mode: {state['mode']}")
        
        self.search_service.add_observer(on_state_change)
    
    def update_state_display(self, query, cities, mode):
        """Update the current state display"""
        state_text = f"Query: '{query}' | Cities: {len(cities)} | Mode: {mode}"
        self.state_label.configure(text=f"Current State: {state_text}")
    
    def show_statistics(self):
        """Display usage statistics"""
        stats = self.search_service.get_usage_statistics()
        
        stats_text = "📊 Usage Statistics\n" + "="*50 + "\n"
        stats_text += f"📈 Total searches: {stats['total_searches']}\n"
        stats_text += f"🌍 Unique cities: {stats['unique_cities']}\n"
        stats_text += f"🔥 Most popular type: {stats['most_popular_type']}\n"
        stats_text += f"📅 Avg searches/day: {stats['avg_searches_per_day']:.1f}\n\n"
        
        stats_text += "🏆 Top Cities:\n"
        for i, (city, count) in enumerate(stats['top_cities'][:5], 1):
            stats_text += f"  {i}. {city} ({count} searches)\n"
        
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", stats_text)
    
    def show_favorites(self):
        """Display favorites"""
        favorites = self.search_service.get_favorites()
        
        fav_text = "⭐ Favorites\n" + "="*50 + "\n"
        if favorites:
            for fav in favorites:
                fav_text += f"★ {fav['city_name']} (used {fav['use_count']} times)\n"
        else:
            fav_text += "No favorites yet. Add some by using the ★ button in search suggestions!\n"
        
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", fav_text)
    
    def clear_history(self):
        """Clear search history"""
        self.search_service.clear_history()
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", "🗑️ Search history cleared!\n")
        print("🗑️ Search history cleared")
    
    def export_data(self):
        """Export search data"""
        data = self.search_service.export_data()
        
        # Save to file
        export_path = Path("data/integrated_search_backup.json")
        export_path.parent.mkdir(exist_ok=True)
        
        import json
        with open(export_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        export_text = f"💾 Data Export\n" + "="*50 + "\n"
        export_text += f"📤 Exported {len(data['search_history'])} search entries\n"
        export_text += f"⭐ Exported {len(data['favorites'])} favorites\n"
        export_text += f"📊 Exported {len(data['analytics'])} analytics patterns\n"
        export_text += f"💾 Data saved to {export_path}\n"
        
        self.stats_text.delete("1.0", "end")
        self.stats_text.insert("1.0", export_text)
        print(f"💾 Data exported to {export_path}")
    
    def run(self):
        """Start the demo"""
        self.root.mainloop()

def main():
    """Main function"""
    # Set appearance
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run demo
    demo = IntegratedSearchDemo()
    demo.run()

if __name__ == "__main__":
    main()