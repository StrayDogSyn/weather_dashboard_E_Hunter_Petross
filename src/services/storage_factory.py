"""Data storage factory for creating appropriate storage implementations."""

import logging
import os
from typing import Optional

from ..interfaces.weather_interfaces import IDataStorage
from ..config.config import ConfigurationManager


class DataStorageFactory:
    """Factory for creating data storage implementations."""
    
    @staticmethod
    def create_storage(config_manager: Optional[ConfigurationManager] = None) -> IDataStorage:
        """
        Create appropriate data storage implementation based on configuration.
        
        Args:
            config_manager: Configuration manager instance
            
        Returns:
            IDataStorage implementation
        """
        # Use provided config or create new one
        if config_manager is None:
            config_manager = ConfigurationManager()
        
        storage_type = config_manager.config.database.storage_type.lower()
        
        try:
            if storage_type == "sql":
                return DataStorageFactory._create_sql_storage(config_manager)
            elif storage_type == "file":
                return DataStorageFactory._create_file_storage(config_manager)
            else:
                logging.warning(f"Unknown storage type '{storage_type}', defaulting to file storage")
                return DataStorageFactory._create_file_storage(config_manager)
                
        except ImportError as e:
            logging.error(f"Failed to import SQL storage dependencies: {e}")
            logging.info("Falling back to file storage")
            return DataStorageFactory._create_file_storage(config_manager)
        except Exception as e:
            logging.error(f"Error creating {storage_type} storage: {e}")
            logging.info("Falling back to file storage")
            return DataStorageFactory._create_file_storage(config_manager)
    
    @staticmethod
    def _create_sql_storage(config_manager: ConfigurationManager) -> IDataStorage:
        """Create SQL-based storage implementation."""
        try:
            # Try SQLAlchemy first, fallback to simple SQLite
            try:
                from .sql_data_storage import SQLDataStorage
                logging.info("Using SQLAlchemy-based SQL storage")
                return SQLDataStorage()
            except ImportError:
                # Fallback to simple SQLite implementation
                from .simple_sql_storage import SimpleSQLDataStorage
                db_path = config_manager.config.database.database_path
                logging.info(f"Using simple SQLite storage at: {db_path}")
                return SimpleSQLDataStorage(db_path=db_path)
                
        except ImportError as e:
            logging.error(f"SQL storage not available: {e}")
            raise
    
    @staticmethod
    def _create_file_storage(config_manager: ConfigurationManager) -> IDataStorage:
        """Create file-based storage implementation."""
        from .data_storage import FileDataStorage
        data_dir = config_manager.config.database.data_directory
        logging.info(f"Using file-based storage in directory: {data_dir}")
        return FileDataStorage(data_dir=data_dir)
    
    @staticmethod
    def can_use_sql_storage() -> bool:
        """Check if SQL storage can be used (dependencies available)."""
        try:
            # Try to import simple SQL storage (always available with Python's sqlite3)
            from .simple_sql_storage import SimpleSQLDataStorage
            return True
        except ImportError:
            try:
                # Fallback to checking SQLAlchemy
                import sqlalchemy
                return True
            except ImportError:
                return False
    
    @staticmethod
    def migrate_file_to_sql(config_manager: Optional[ConfigurationManager] = None) -> bool:
        """
        Migrate data from file storage to SQL storage.
        
        Args:
            config_manager: Configuration manager instance
            
        Returns:
            True if migration successful, False otherwise
        """
        if config_manager is None:
            config_manager = ConfigurationManager()
        
        try:
            # Create both storage implementations
            file_storage = DataStorageFactory._create_file_storage(config_manager)
            sql_storage = DataStorageFactory._create_sql_storage(config_manager)
            
            # Files to migrate
            files_to_migrate = [
                "user_preferences.json",
                "favorite_cities.json",
                "weather_history.json", 
                "journal_entries.json"
            ]
            
            migration_success = True
            
            for filename in files_to_migrate:
                logging.info(f"Migrating {filename}...")
                
                # Load data from file storage
                data = file_storage.load_data(filename)
                if data is None:
                    logging.warning(f"No data found in {filename}, skipping...")
                    continue
                
                # Save data to SQL storage
                success = sql_storage.save_data(data, filename)
                if not success:
                    logging.error(f"Failed to migrate {filename}")
                    migration_success = False
                else:
                    logging.info(f"Successfully migrated {filename}")
            
            return migration_success
            
        except Exception as e:
            logging.error(f"Migration failed: {e}")
            return False
