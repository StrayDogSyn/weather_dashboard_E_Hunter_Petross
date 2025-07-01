"""SQL database utilities for Weather Dashboard."""

import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class SQLiteHelper:
    """Helper class for SQLite database operations without SQLAlchemy dependency."""
    
    def __init__(self, db_path: str = "data/weather_dashboard.db"):
        """Initialize SQLite helper."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        
    def init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_types TEXT,  -- JSON string
                    preferred_units TEXT DEFAULT 'imperial',
                    cache_enabled BOOLEAN DEFAULT 1,
                    notifications_enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Favorite cities table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorite_cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT NOT NULL,
                    country_code TEXT,
                    latitude REAL,
                    longitude REAL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Weather history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_id INTEGER,
                    city_name TEXT NOT NULL,
                    country TEXT,
                    temperature REAL NOT NULL,
                    condition TEXT NOT NULL,
                    humidity REAL,
                    wind_speed REAL,
                    wind_direction REAL,
                    pressure REAL,
                    visibility REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (city_id) REFERENCES favorite_cities (id)
                )
            """)
            
            # Journal entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    weather_conditions TEXT,
                    location TEXT,
                    mood TEXT,
                    activities TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Activity recommendations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_name TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    min_temperature REAL,
                    max_temperature REAL,
                    suitable_conditions TEXT,  -- JSON string
                    unsuitable_conditions TEXT,  -- JSON string
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logging.info(f"Database initialized at: {self.db_path}")
    
    def insert_default_data(self):
        """Insert default data if tables are empty."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if user preferences exist
            cursor.execute("SELECT COUNT(*) FROM user_preferences")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO user_preferences (activity_types, preferred_units, cache_enabled, notifications_enabled)
                    VALUES (?, ?, ?, ?)
                """, ('["outdoor", "indoor", "sports", "relaxation"]', 'imperial', 1, 1))
            
            # Check if activity recommendations exist
            cursor.execute("SELECT COUNT(*) FROM activity_recommendations")
            if cursor.fetchone()[0] == 0:
                activities = [
                    ("Beach Day", "Perfect for sunny, warm weather", "outdoor", 75.0, None, '["clear", "sunny"]', '["rain", "storm", "snow"]'),
                    ("Museum Visit", "Great indoor activity for any weather", "indoor", None, None, '["rain", "snow", "cold", "hot"]', '[]'),
                    ("Hiking", "Outdoor adventure in good weather", "outdoor", 50.0, 85.0, '["clear", "partly cloudy"]', '["rain", "storm", "snow"]'),
                    ("Reading at Home", "Perfect relaxation activity", "relaxation", None, None, '["rain", "snow", "cold"]', '[]')
                ]
                
                cursor.executemany("""
                    INSERT INTO activity_recommendations 
                    (activity_name, description, category, min_temperature, max_temperature, suitable_conditions, unsuitable_conditions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, activities)
            
            conn.commit()
            logging.info("Default data inserted")
    
    def migrate_json_data(self, json_data: Dict[str, Any], table_name: str) -> bool:
        """Migrate JSON data to appropriate table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if table_name == "user_preferences":
                    return self._migrate_user_preferences(cursor, json_data)
                elif table_name == "favorite_cities":
                    return self._migrate_favorite_cities(cursor, json_data)
                elif table_name == "weather_history":
                    return self._migrate_weather_history(cursor, json_data)
                elif table_name == "journal_entries":
                    return self._migrate_journal_entries(cursor, json_data)
                
                conn.commit()
                return True
                
        except Exception as e:
            logging.error(f"Error migrating {table_name}: {e}")
            return False
    
    def _migrate_user_preferences(self, cursor, data: Dict[str, Any]) -> bool:
        """Migrate user preferences data."""
        import json
        
        cursor.execute("DELETE FROM user_preferences")
        cursor.execute("""
            INSERT INTO user_preferences (activity_types, preferred_units, cache_enabled, notifications_enabled)
            VALUES (?, ?, ?, ?)
        """, (
            json.dumps(data.get("activity_types", [])),
            data.get("preferred_units", "imperial"),
            data.get("cache_enabled", True),
            data.get("notifications_enabled", True)
        ))
        return True
    
    def _migrate_favorite_cities(self, cursor, data: Dict[str, Any]) -> bool:
        """Migrate favorite cities data."""
        cursor.execute("DELETE FROM favorite_cities")
        favorites = data.get("favorites", [])
        
        for fav in favorites:
            cursor.execute("""
                INSERT INTO favorite_cities (city_name, country_code, latitude, longitude)
                VALUES (?, ?, ?, ?)
            """, (
                fav.get("city", ""),
                fav.get("country", ""),
                fav.get("latitude"),
                fav.get("longitude")
            ))
        return True
    
    def _migrate_weather_history(self, cursor, data: Dict[str, Any]) -> bool:
        """Migrate weather history data."""
        entries = data.get("entries", [])
        
        for entry in entries:
            # Check if entry already exists
            cursor.execute("""
                SELECT COUNT(*) FROM weather_history 
                WHERE city_name = ? AND timestamp = ?
            """, (entry.get("city", ""), entry.get("timestamp", "")))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO weather_history 
                    (city_name, country, temperature, condition, humidity, wind_speed, wind_direction, pressure, visibility, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.get("city", ""),
                    entry.get("country", ""),
                    entry.get("temperature", 0.0),
                    entry.get("condition", ""),
                    entry.get("humidity"),
                    entry.get("wind_speed"),
                    entry.get("wind_direction"),
                    entry.get("pressure"),
                    entry.get("visibility"),
                    entry.get("timestamp", "")
                ))
        return True
    
    def _migrate_journal_entries(self, cursor, data: Dict[str, Any]) -> bool:
        """Migrate journal entries data."""
        import json
        
        entries = data.get("entries", [])
        
        for entry in entries:
            # Check if entry already exists
            cursor.execute("""
                SELECT COUNT(*) FROM journal_entries 
                WHERE title = ? AND created_at = ?
            """, (entry.get("title", ""), entry.get("created_at", "")))
            
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO journal_entries 
                    (title, content, weather_conditions, location, mood, activities, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.get("title", ""),
                    entry.get("content", ""),
                    entry.get("weather_conditions"),
                    entry.get("location"),
                    entry.get("mood"),
                    json.dumps(entry.get("activities", [])),
                    entry.get("created_at", ""),
                    entry.get("updated_at", "")
                ))
        return True
    
    def get_table_info(self) -> Dict[str, int]:
        """Get information about tables and record counts."""
        info = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                tables = ["user_preferences", "favorite_cities", "weather_history", "journal_entries", "activity_recommendations"]
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    info[table] = cursor.fetchone()[0]
                    
        except Exception as e:
            logging.error(f"Error getting table info: {e}")
            
        return info
