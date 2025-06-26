#!/usr/bin/env python3
"""
Simple launcher script for the Weather Dashboard GUI.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.app_gui import WeatherDashboardGUIApp
    
    def main():
        """Main entry point for the GUI application."""
        print("🌤️ Starting Weather Dashboard GUI...")
        
        app = WeatherDashboardGUIApp()
        app.run()
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have installed all required dependencies:")
    print("pip install -r requirements.txt")
except Exception as e:
    print(f"❌ Error starting application: {e}")
    print("Check the weather_dashboard.log file for more details.")
