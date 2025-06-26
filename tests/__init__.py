"""Test package for the Weather Dashboard application."""

# Test configuration
import sys
import os

# Add project root to path for testing
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
