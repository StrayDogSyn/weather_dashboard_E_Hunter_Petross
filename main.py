"""
Weather Dashboard - TKinter GUI Application Entry Point
A comprehensive weather dashboard with glassmorphic design

Author: E Hunter Petross
Project: Weather Dashboard Capstone

Features:
- Modern TKinter GUI with glassmorphic design
- Current weather and forecasts
- City comparison
- Weather journal
- Activity suggestions
- Weather poetry
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)


def main():
    """Main entry point for the Weather Dashboard GUI."""
    print("🌤️ Weather Dashboard - TKinter GUI")
    print("=" * 50)

    try:
        # Test TKinter availability
        try:
            test_root = tk.Tk()
            test_root.withdraw()  # Hide test window immediately
            test_root.destroy()  # Properly destroy test window
            del test_root  # Remove reference
            print("✅ TKinter: Available")
        except Exception as e:
            print(f"❌ TKinter: Not available - {e}")
            return

        # Try to import and launch the full GUI app
        try:
            from src.app_gui import WeatherDashboardGUIApp

            print("✅ Loading full GUI application...")

            app = WeatherDashboardGUIApp()
            if app.gui and app.controller.is_initialized():
                print("✅ Main application initialized successfully")
                app.run()
                return  # Exit successfully
            else:
                print("❌ Full app initialization failed - exiting")
                return

        except ImportError as e:
            print(f"❌ Full app import failed: {e}")
            print("❌ Cannot start application without required modules")
            return
        except Exception as e:
            print(f"❌ Full app failed to run: {e}")
            print("❌ Application startup failed")
            return

    except Exception as e:
        print(f"❌ Critical error: {e}")
        try:
            messagebox.showerror("Error", f"Failed to start Weather Dashboard: \n{e}")
        except:
            pass


# Removed SimpleWeatherGUI fallback - main application handles all functionality


if __name__ == "__main__":
    main()
