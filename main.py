"""
Weather Dashboard - Main Application Entry Point
A comprehensive weather dashboard application

Author: E Hunter Petross
Project: Weather Dashboard Capstone

This is the main entry point that launches the refactored application
using clean architecture and separation of concerns.
"""

import os
import sys

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import and run the main application
from src import main

if __name__ == "__main__":
    main()