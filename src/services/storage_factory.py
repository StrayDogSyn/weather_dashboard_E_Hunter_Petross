"""Data storage factory for creating appropriate storage implementations."""

import logging
import os
from typing import Optional

from ..interfaces.weather_interfaces import IDataStorage


class DataStorageFactory:
    """Factory for creating data storage implementations."""

    @staticmethod
    def create_storage(config_manager=None) -> IDataStorage:
        """
        Create appropriate data storage implementation based on configuration.

        Args:
            config_manager: Configuration manager instance (optional)

        Returns:
            IDataStorage implementation
        """
        # Check environment variable for storage type
        storage_type = os.getenv("WEATHER_STORAGE_TYPE", "file").lower()

        try:
            if storage_type == "sql":
                return DataStorageFactory._create_sql_storage(config_manager)
            else:
                return DataStorageFactory._create_file_storage(config_manager)

        except Exception as e:
            logging.error(f"Error creating {storage_type} storage: {e}")
            logging.info("Falling back to file storage")
            return DataStorageFactory._create_file_storage(config_manager)

    @staticmethod
    def _create_sql_storage(config_manager) -> IDataStorage:
        """Create SQL-based storage implementation."""
        try:
            # Use SQLAlchemy-based implementation
            from .sql_data_storage import SQLDataStorage

            logging.info("Using SQLAlchemy-based SQL storage")
            return SQLDataStorage()

        except ImportError as e:
            logging.error(f"SQLAlchemy storage not available: {e}")
            raise Exception(
                "SQL storage implementation not available. Please install SQLAlchemy: pip install sqlalchemy"
            )

    @staticmethod
    def _create_file_storage(config_manager) -> IDataStorage:
        """Create file-based storage implementation."""
        from .data_storage import FileDataStorage

        data_dir = os.getenv("WEATHER_DATA_DIR", "data")
        logging.info(f"Using file-based storage in directory: {data_dir}")
        return FileDataStorage(data_dir=data_dir)

    @staticmethod
    def can_use_sql_storage() -> bool:
        """Check if SQL storage can be used (dependencies available)."""
        try:
            # SQLite is built into Python, so check for our implementation
            import sqlite3

            return True
        except ImportError:
            return False
