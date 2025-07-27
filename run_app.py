#!/usr/bin/env python3
"""
Weather Dashboard Application Runner

This script properly sets up the Python path and runs the weather dashboard application.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import and run the application
if __name__ == "__main__":
    try:
        from src.app_gui import main_gui
        main_gui()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)