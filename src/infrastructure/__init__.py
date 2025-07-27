"""Infrastructure layer for Weather Dashboard.

This module contains infrastructure services and implementations
for external dependencies like APIs, databases,
configuration management, and storage.
"""

from .config_manager import ConfigManager
from .storage_service import StorageService

__all__ = ["ConfigManager", "StorageService"]
