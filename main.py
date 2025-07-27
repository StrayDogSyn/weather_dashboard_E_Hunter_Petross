#!/usr/bin/env python3
"""
Weather Dashboard Application Entry Point

This is the main entry point for the Weather Dashboard application.
It uses the application factory pattern and dependency injection
for clean architecture and proper separation of concerns.

Author: E Hunter Petross
Project: Weather Dashboard Capstone

Features:
- Clean Architecture with Dependency Injection
- Modern TKinter GUI with glassmorphic design
- Current weather and forecasts
- City comparison
- Weather journal
- Activity suggestions
- Weather poetry
- Voice assistant integration
"""

import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def check_tkinter() -> bool:
    """Check if TKinter is available.

    Returns:
        True if TKinter is available, False otherwise
    """
    try:
        import tkinter

        return True
    except ImportError:
        print("❌ Error: TKinter is not available.")
        print("Please install TKinter to run the Weather Dashboard GUI.")
        print("On Ubuntu/Debian: sudo apt-get install python3-tk")
        print("On CentOS/RHEL: sudo yum install tkinter")
        print("On macOS: TKinter should be included with Python")
        print("On Windows: TKinter should be included with Python")
        return False


def setup_environment() -> None:
    """Setup the application environment."""
    # Ensure required directories exist
    base_dir = Path(__file__).parent
    required_dirs = ["config", "data", "logs", "cache", "temp"]

    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        dir_path.mkdir(exist_ok=True)


def main() -> None:
    """Main entry point for the application."""
    print("Weather Dashboard - Clean Architecture")
    print("=" * 50)

    try:
        # Check TKinter availability
        if not check_tkinter():
            sys.exit(1)

        print("✅ TKinter: Available")

        # Setup environment
        setup_environment()
        print("✅ Environment: Setup complete")

        # Import application factory
        from src.application.app_factory import create_application

        # Create and initialize application
        print("🔧 Initializing Weather Dashboard...")
        app_factory = create_application()
        print("✅ Application Factory: Initialized")

        # Create GUI application
        gui_app = app_factory.create_gui_application()
        print("✅ GUI Application: Created")

        # Initialize and run GUI
        gui_app.initialize()
        print("✅ GUI Application: Initialized")
        print("🚀 Starting Weather Dashboard GUI...")
        gui_app.run()

    except KeyboardInterrupt:
        print("\n⚠️ Application interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Application startup failed: {e}")
        print(f"❌ Error starting application: {e}")
        print("Please check the logs for more details.")
        sys.exit(1)
    finally:
        # Cleanup
        try:
            if "app_factory" in locals():
                print("🧹 Cleaning up...")
                app_factory.shutdown()
                print("✅ Cleanup: Complete")
        except Exception as e:
            logging.error(f"Error during application shutdown: {e}")


if __name__ == "__main__":
    main()
