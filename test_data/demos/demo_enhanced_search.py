#!/usr/bin/env python3
"""
Enhanced Search Bar Demo

This demo showcases the intelligent command center functionality
of the enhanced search bar component.

Run this script to see the search bar in action with:
- Smart autocomplete
- Command shortcuts
- Natural language processing
- Quick actions
- Search history
- Multi-city selection
"""

import customtkinter as ctk
import sys
import os
from pathlib import Path

# Add src directory to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    # Import the enhanced search bar components
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src', 'ui', 'components'))
    import enhanced_search_bar
    import search_bar_integration
    
    EnhancedSearchBar = enhanced_search_bar.EnhancedSearchBar
    SearchBarDemo = search_bar_integration.SearchBarDemo
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure the enhanced_search_bar.py file exists in src/ui/components/")
    sys.exit(1)

class DemoApplication(ctk.CTk):
    """Main demo application window"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Enhanced Search Bar - Intelligent Command Center Demo")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the demo UI"""
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Demo content
        self.create_demo_content()
        
        # Footer
        self.create_footer()
    
    def create_header(self):
        """Create the header section"""
        header_frame = ctk.CTkFrame(self.main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="🔍 Enhanced Search Bar Demo",
            font=("Helvetica", 28, "bold")
        )
        title.pack(pady=20)
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Intelligent Command Center for Weather Dashboard",
            font=("Helvetica", 16),
            text_color="gray70"
        )
        subtitle.pack(pady=(0, 20))
    
    def create_demo_content(self):
        """Create the main demo content"""
        # Create notebook for different demo sections
        self.notebook = ctk.CTkTabview(self.main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Interactive Demo Tab
        self.create_interactive_demo()
        
        # Features Overview Tab
        self.create_features_overview()
        
        # Command Reference Tab
        self.create_command_reference()
        
        # Examples Tab
        self.create_examples_tab()
    
    def create_interactive_demo(self):
        """Create interactive demo tab"""
        tab = self.notebook.add("Interactive Demo")
        
        # Instructions
        instructions = ctk.CTkLabel(
            tab,
            text="Try the enhanced search bar below! Type commands, city names, or natural language queries.",
            font=("Helvetica", 14),
            wraplength=800
        )
        instructions.pack(pady=20)
        
        # Create the enhanced search bar demo
        self.search_demo = SearchBarDemo(tab)
        self.search_demo.pack(fill="both", expand=True, padx=20, pady=10)
    
    def create_features_overview(self):
        """Create features overview tab"""
        tab = self.notebook.add("Features")
        
        # Scrollable frame for features
        scrollable_frame = ctk.CTkScrollableFrame(tab)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        features = [
            {
                "title": "🎯 Smart Autocomplete",
                "description": "Intelligent suggestions based on recent searches, favorites, and available commands. The system learns from your usage patterns.",
                "examples": ["Type 'Lon' → suggests 'London'", "Recent: 'New York', 'Paris'", "Commands: 'compare:', 'analyze:'"]
            },
            {
                "title": "⚡ Command Shortcuts",
                "description": "Powerful command system for quick actions across the entire weather dashboard.",
                "examples": ["compare: London, Paris, Tokyo", "analyze: New York", "map: San Francisco", "weather: Miami"]
            },
            {
                "title": "🧠 Natural Language Processing",
                "description": "Understand and process natural language queries for intuitive weather searches.",
                "examples": ["show me rainy cities", "find sunny places", "cold cities", "places above 80 degrees"]
            },
            {
                "title": "🚀 Quick Actions",
                "description": "Fast access to common operations with visual indicators and keyboard shortcuts.",
                "examples": ["★ Favorites menu", "🕐 Search history", "Multi-city selection", "Keyboard shortcuts"]
            },
            {
                "title": "📚 Search History",
                "description": "Persistent search history with smart suggestions and easy access to previous queries.",
                "examples": ["Auto-saves all searches", "Smart suggestions", "Quick re-search", "History management"]
            },
            {
                "title": "🔄 Multi-City Selection",
                "description": "Select and compare multiple cities simultaneously for comprehensive weather analysis.",
                "examples": ["Enable multi-select mode", "Add multiple cities", "Batch comparisons", "Visual indicators"]
            }
        ]
        
        for feature in features:
            self.create_feature_card(scrollable_frame, feature)
    
    def create_feature_card(self, parent, feature):
        """Create a feature card"""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", pady=10)
        
        # Title
        title = ctk.CTkLabel(
            card,
            text=feature["title"],
            font=("Helvetica", 18, "bold"),
            anchor="w"
        )
        title.pack(fill="x", padx=20, pady=(15, 5))
        
        # Description
        desc = ctk.CTkLabel(
            card,
            text=feature["description"],
            font=("Helvetica", 12),
            anchor="w",
            justify="left",
            wraplength=700
        )
        desc.pack(fill="x", padx=20, pady=5)
        
        # Examples
        examples_frame = ctk.CTkFrame(card, fg_color="gray20")
        examples_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        examples_label = ctk.CTkLabel(
            examples_frame,
            text="Examples:",
            font=("Helvetica", 11, "bold"),
            anchor="w"
        )
        examples_label.pack(fill="x", padx=10, pady=(10, 5))
        
        for example in feature["examples"]:
            example_label = ctk.CTkLabel(
                examples_frame,
                text=f"• {example}",
                font=("Helvetica", 10),
                anchor="w",
                text_color="gray80"
            )
            example_label.pack(fill="x", padx=20, pady=2)
        
        # Add some bottom padding
        ctk.CTkLabel(examples_frame, text="", height=5).pack()
    
    def create_command_reference(self):
        """Create command reference tab"""
        tab = self.notebook.add("Commands")
        
        # Scrollable frame for commands
        scrollable_frame = ctk.CTkScrollableFrame(tab)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Command categories
        command_categories = [
            {
                "category": "Basic Commands",
                "commands": [
                    {"cmd": "compare: London, Paris, Tokyo", "desc": "Compare weather across multiple cities"},
                    {"cmd": "analyze: New York", "desc": "AI-powered weather analysis for a city"},
                    {"cmd": "map: San Francisco", "desc": "Open map view for specified location"},
                    {"cmd": "weather: Miami", "desc": "Get detailed weather information"}
                ]
            },
            {
                "category": "Natural Language Queries",
                "commands": [
                    {"cmd": "show me rainy cities", "desc": "Find cities with current precipitation"},
                    {"cmd": "find sunny places", "desc": "Locate cities with clear weather"},
                    {"cmd": "cold cities", "desc": "Cities with low temperatures"},
                    {"cmd": "places above 80 degrees", "desc": "High temperature locations"}
                ]
            },
            {
                "category": "Advanced Commands",
                "commands": [
                    {"cmd": "activity: Boston", "desc": "Get activity recommendations based on weather"},
                    {"cmd": "journal: Seattle", "desc": "Access weather journal entries"},
                    {"cmd": "find windy cities", "desc": "Locate cities with high wind speeds"},
                    {"cmd": "cities below 32 degrees", "desc": "Find freezing temperature locations"}
                ]
            }
        ]
        
        for category in command_categories:
            self.create_command_category(scrollable_frame, category)
    
    def create_command_category(self, parent, category):
        """Create a command category section"""
        # Category header
        header = ctk.CTkLabel(
            parent,
            text=category["category"],
            font=("Helvetica", 20, "bold"),
            anchor="w"
        )
        header.pack(fill="x", pady=(20, 10))
        
        # Commands frame
        commands_frame = ctk.CTkFrame(parent)
        commands_frame.pack(fill="x", pady=(0, 20))
        
        for cmd_info in category["commands"]:
            cmd_frame = ctk.CTkFrame(commands_frame, fg_color="gray25")
            cmd_frame.pack(fill="x", padx=15, pady=5)
            
            # Command
            cmd_label = ctk.CTkLabel(
                cmd_frame,
                text=cmd_info["cmd"],
                font=("Courier", 12, "bold"),
                anchor="w",
                text_color="lightblue"
            )
            cmd_label.pack(fill="x", padx=15, pady=(10, 5))
            
            # Description
            desc_label = ctk.CTkLabel(
                cmd_frame,
                text=cmd_info["desc"],
                font=("Helvetica", 11),
                anchor="w",
                text_color="gray80"
            )
            desc_label.pack(fill="x", padx=15, pady=(0, 10))
    
    def create_examples_tab(self):
        """Create examples tab"""
        tab = self.notebook.add("Examples")
        
        # Scrollable frame for examples
        scrollable_frame = ctk.CTkScrollableFrame(tab)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Example scenarios
        examples = [
            {
                "title": "🌍 Planning a Trip",
                "scenario": "You're planning a trip and want to compare weather in multiple destinations.",
                "steps": [
                    "Type: compare: London, Paris, Rome, Barcelona",
                    "The system switches to analytics view",
                    "Weather comparison appears with detailed metrics",
                    "You can see temperature, precipitation, and conditions"
                ]
            },
            {
                "title": "🌧️ Finding Good Weather",
                "scenario": "You want to find cities with sunny weather for your vacation.",
                "steps": [
                    "Type: show me sunny cities",
                    "Natural language processor identifies 'sunny' condition",
                    "System searches for cities with clear weather",
                    "Results show sunny destinations with current conditions"
                ]
            },
            {
                "title": "🗺️ Exploring a Location",
                "scenario": "You want to see a city on the map and get detailed weather info.",
                "steps": [
                    "Type: map: Tokyo",
                    "System switches to map view",
                    "Map centers on Tokyo with weather overlay",
                    "Weather details appear in sidebar"
                ]
            },
            {
                "title": "🤖 AI Weather Analysis",
                "scenario": "You want AI-powered insights about weather patterns.",
                "steps": [
                    "Type: analyze: San Francisco",
                    "AI analysis begins processing",
                    "System provides weather trends and insights",
                    "Recommendations for activities appear"
                ]
            },
            {
                "title": "📱 Quick Multi-City Check",
                "scenario": "You need to quickly check weather in several cities.",
                "steps": [
                    "Enable 'Multi' checkbox",
                    "Type first city: New York",
                    "Add to selection, type: Los Angeles",
                    "Add to selection, type: Chicago",
                    "All cities appear in comparison view"
                ]
            }
        ]
        
        for example in examples:
            self.create_example_card(scrollable_frame, example)
    
    def create_example_card(self, parent, example):
        """Create an example scenario card"""
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", pady=15)
        
        # Title
        title = ctk.CTkLabel(
            card,
            text=example["title"],
            font=("Helvetica", 18, "bold"),
            anchor="w"
        )
        title.pack(fill="x", padx=20, pady=(15, 5))
        
        # Scenario
        scenario = ctk.CTkLabel(
            card,
            text=example["scenario"],
            font=("Helvetica", 12),
            anchor="w",
            justify="left",
            wraplength=700,
            text_color="gray80"
        )
        scenario.pack(fill="x", padx=20, pady=5)
        
        # Steps
        steps_frame = ctk.CTkFrame(card, fg_color="gray20")
        steps_frame.pack(fill="x", padx=20, pady=(10, 15))
        
        steps_label = ctk.CTkLabel(
            steps_frame,
            text="Steps:",
            font=("Helvetica", 12, "bold"),
            anchor="w"
        )
        steps_label.pack(fill="x", padx=15, pady=(10, 5))
        
        for i, step in enumerate(example["steps"], 1):
            step_label = ctk.CTkLabel(
                steps_frame,
                text=f"{i}. {step}",
                font=("Helvetica", 11),
                anchor="w",
                justify="left",
                wraplength=650,
                text_color="gray90"
            )
            step_label.pack(fill="x", padx=25, pady=3)
        
        # Add some bottom padding
        ctk.CTkLabel(steps_frame, text="", height=5).pack()
    
    def create_footer(self):
        """Create the footer section"""
        footer_frame = ctk.CTkFrame(self.main_frame, height=60)
        footer_frame.pack(fill="x", pady=(20, 0))
        footer_frame.pack_propagate(False)
        
        # Footer content
        footer_content = ctk.CTkFrame(footer_frame, fg_color="transparent")
        footer_content.pack(expand=True)
        
        # Info text
        info_text = ctk.CTkLabel(
            footer_content,
            text="Enhanced Search Bar - Transforming weather dashboard interaction",
            font=("Helvetica", 12),
            text_color="gray70"
        )
        info_text.pack(pady=20)

def main():
    """Main function to run the demo"""
    print("Starting Enhanced Search Bar Demo...")
    print("Features: Smart autocomplete, Command shortcuts, Natural language processing")
    print("Press Ctrl+C to exit\n")
    
    try:
        app = DemoApplication()
        app.mainloop()
    except KeyboardInterrupt:
        print("\nDemo terminated by user")
    except Exception as e:
        print(f"Error running demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()