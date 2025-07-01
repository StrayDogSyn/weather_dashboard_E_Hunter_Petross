"""Simple SQL data storage implementation using SQLite without SQLAlchemy."""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import interfaces and sqlite helper using absolute imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from interfaces.weather_interfaces import IDataStorage
from services.sqlite_helper import SQLiteHelper


class SimpleSQLDataStorage(IDataStorage):
    """Simple SQL data storage implementation using SQLite directly."""

    def __init__(self, db_path: str = "data/weather_dashboard.db"):
        """Initialize simple SQL data storage."""
        self.db_helper = SQLiteHelper(db_path)
        try:
            self.db_helper.init_database()
            self.db_helper.insert_default_data()
            logging.info("Simple SQL data storage initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing simple SQL storage: {e}")
            raise

    def save_data(self, data: Dict[str, Any], filename: str) -> bool:
        """
        Save data to SQL database.
        
        Args:
            data: Data to save
            filename: Determines which table to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            table_name = self._filename_to_table(filename)
            if table_name:
                return self.db_helper.migrate_json_data(data, table_name)
            else:
                logging.warning(f"Unknown filename for SQL storage: {filename}")
                return False
                
        except Exception as e:
            logging.error(f"Error saving {filename}: {e}")
            return False

    def load_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load data from SQL database.
        
        Args:
            filename: Determines which table to load from
            
        Returns:
            Loaded data or None if error
        """
        try:
            if filename == "user_preferences.json":
                return self._load_user_preferences()
            elif filename == "favorite_cities.json":
                return self._load_favorite_cities()
            elif filename == "weather_history.json":
                return self._load_weather_history()
            elif filename == "journal_entries.json":
                return self._load_journal_entries()
            else:
                logging.warning(f"Unknown filename for SQL storage: {filename}")
                return None
                
        except Exception as e:
            logging.error(f"Error loading {filename}: {e}")
            return None

    def delete_data(self, filename: str) -> bool:
        """
        Delete data from SQL database.
        
        Args:
            filename: Determines which table to clear
            
        Returns:
            True if successful, False otherwise
        """
        try:
            table_name = self._filename_to_table(filename)
            if table_name:
                with sqlite3.connect(self.db_helper.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"DELETE FROM {table_name}")
                    conn.commit()
                    logging.info(f"Data cleared for {filename}")
                    return True
            else:
                logging.warning(f"Unknown filename for SQL deletion: {filename}")
                return False
                
        except Exception as e:
            logging.error(f"Error deleting {filename}: {e}")
            return False

    def _filename_to_table(self, filename: str) -> Optional[str]:
        """Convert filename to table name."""
        mapping = {
            "user_preferences.json": "user_preferences",
            "favorite_cities.json": "favorite_cities",
            "weather_history.json": "weather_history",
            "journal_entries.json": "journal_entries"
        }
        return mapping.get(filename)

    def _load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences from database."""
        with sqlite3.connect(self.db_helper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM user_preferences ORDER BY id DESC LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                return {
                    "activity_types": json.loads(row[1]) if row[1] else [],
                    "preferred_units": row[2] or "imperial",
                    "cache_enabled": bool(row[3]),
                    "notifications_enabled": bool(row[4])
                }
            else:
                # Return defaults if no preferences found
                return {
                    "activity_types": ["outdoor", "indoor", "sports", "relaxation"],
                    "preferred_units": "imperial",
                    "cache_enabled": True,
                    "notifications_enabled": True
                }

    def _load_favorite_cities(self) -> Dict[str, Any]:
        """Load favorite cities from database."""
        with sqlite3.connect(self.db_helper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM favorite_cities ORDER BY added_at")
            rows = cursor.fetchall()
            
            favorites = []
            for row in rows:
                fav = {
                    "city": row[1],  # city_name
                    "country": row[2] or "",  # country_code
                    "added_at": row[5]  # added_at
                }
                if row[3]:  # latitude
                    fav["latitude"] = row[3]
                if row[4]:  # longitude
                    fav["longitude"] = row[4]
                favorites.append(fav)
                
            return {
                "favorites": favorites,
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }

    def _load_weather_history(self) -> Dict[str, Any]:
        """Load weather history from database."""
        with sqlite3.connect(self.db_helper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM weather_history ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            
            entries = []
            for row in rows:
                weather_data = {
                    "city": row[2],  # city_name
                    "country": row[3] or "",  # country
                    "temperature": row[4],  # temperature
                    "condition": row[5],  # condition
                    "timestamp": row[11]  # timestamp
                }
                
                # Add optional fields if they exist
                if row[6] is not None:  # humidity
                    weather_data["humidity"] = row[6]
                if row[7] is not None:  # wind_speed
                    weather_data["wind_speed"] = row[7]
                if row[8] is not None:  # wind_direction
                    weather_data["wind_direction"] = row[8]
                if row[9] is not None:  # pressure
                    weather_data["pressure"] = row[9]
                if row[10] is not None:  # visibility
                    weather_data["visibility"] = row[10]
                    
                entries.append(weather_data)
                
            return {
                "entries": entries,
                "last_updated": datetime.utcnow().isoformat()
            }

    def _load_journal_entries(self) -> Dict[str, Any]:
        """Load journal entries from database."""
        with sqlite3.connect(self.db_helper.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM journal_entries ORDER BY created_at DESC")
            rows = cursor.fetchall()
            
            entries = []
            for row in rows:
                journal_data = {
                    "title": row[1],  # title
                    "content": row[2],  # content
                    "created_at": row[7],  # created_at
                    "updated_at": row[8]   # updated_at
                }
                
                # Add optional fields if they exist
                if row[3]:  # weather_conditions
                    journal_data["weather_conditions"] = row[3]
                if row[4]:  # location
                    journal_data["location"] = row[4]
                if row[5]:  # mood
                    journal_data["mood"] = row[5]
                if row[6]:  # activities
                    journal_data["activities"] = json.loads(row[6])
                    
                entries.append(journal_data)
                
            return {
                "entries": entries,
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }

    # Additional methods for compatibility with existing interface
    def list_files(self) -> List[str]:
        """List available data types."""
        return [
            "user_preferences.json",
            "favorite_cities.json", 
            "weather_history.json",
            "journal_entries.json"
        ]

    def file_exists(self, filename: str) -> bool:
        """Check if data exists for the given filename."""
        try:
            table_name = self._filename_to_table(filename)
            if table_name:
                with sqlite3.connect(self.db_helper.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    return cursor.fetchone()[0] > 0
            return False
        except Exception as e:
            logging.error(f"Error checking file existence: {e}")
            return False

    def get_file_size(self, filename: str) -> Optional[int]:
        """Get number of records for the given filename."""
        try:
            table_name = self._filename_to_table(filename)
            if table_name:
                with sqlite3.connect(self.db_helper.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    return cursor.fetchone()[0]
            return None
        except Exception as e:
            logging.error(f"Error getting file size: {e}")
            return None

    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        return {
            "database_path": str(self.db_helper.db_path),
            "tables": self.db_helper.get_table_info(),
            "storage_type": "sqlite"
        }
