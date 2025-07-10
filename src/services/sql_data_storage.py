"""SQL database-based data storage implementation."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from ..interfaces.weather_interfaces import IDataStorage

# Import database models from src.models
try:
    from ..models.database_models import (
        ActivityRecommendations,
        FavoriteCities,
        JournalEntries,
        UserPreferences,
        WeatherHistory,
        close_db_session,
        get_db_session,
        init_database,
    )
except ImportError as e:
    logging.error(f"Failed to import database module: {e}")
    raise ImportError(
        "Database module not found. Ensure database.py exists in the data directory."
    )


class SQLDataStorage(IDataStorage):
    """SQL database-based data storage implementation."""

    def __init__(self):
        """Initialize SQL data storage."""
        try:
            init_database()
            logging.info("SQL data storage initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing SQL storage: {e}")
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
        session = get_db_session()
        try:
            if filename == "user_preferences.json":
                return self._save_user_preferences(session, data)
            elif filename == "favorite_cities.json":
                return self._save_favorite_cities(session, data)
            elif filename == "weather_history.json":
                return self._save_weather_history(session, data)
            elif filename == "journal_entries.json":
                return self._save_journal_entries(session, data)
            else:
                logging.warning(f"Unknown filename for SQL storage: {filename}")
                return False

        except SQLAlchemyError as e:
            logging.error(f"Database error saving {filename}: {e}")
            session.rollback()
            return False
        except Exception as e:
            logging.error(f"Error saving {filename}: {e}")
            session.rollback()
            return False
        finally:
            close_db_session(session)

    def load_data(self, filename: str) -> Optional[Dict[str, Any]]:
        """
        Load data from SQL database.

        Args:
            filename: Determines which table to load from

        Returns:
            Loaded data or None if error
        """
        session = get_db_session()
        try:
            if filename == "user_preferences.json":
                return self._load_user_preferences(session)
            elif filename == "favorite_cities.json":
                return self._load_favorite_cities(session)
            elif filename == "weather_history.json":
                return self._load_weather_history(session)
            elif filename == "journal_entries.json":
                return self._load_journal_entries(session)
            else:
                logging.warning(f"Unknown filename for SQL storage: {filename}")
                return None

        except SQLAlchemyError as e:
            logging.error(f"Database error loading {filename}: {e}")
            return None
        except Exception as e:
            logging.error(f"Error loading {filename}: {e}")
            return None
        finally:
            close_db_session(session)

    def delete_data(self, filename: str) -> bool:
        """
        Delete data from SQL database.

        Args:
            filename: Determines which table to clear

        Returns:
            True if successful, False otherwise
        """
        session = get_db_session()
        try:
            if filename == "user_preferences.json":
                session.query(UserPreferences).delete()
            elif filename == "favorite_cities.json":
                session.query(FavoriteCities).delete()
            elif filename == "weather_history.json":
                session.query(WeatherHistory).delete()
            elif filename == "journal_entries.json":
                session.query(JournalEntries).delete()
            else:
                logging.warning(f"Unknown filename for SQL deletion: {filename}")
                return False

            session.commit()
            logging.info(f"Data cleared for {filename}")
            return True

        except SQLAlchemyError as e:
            logging.error(f"Database error deleting {filename}: {e}")
            session.rollback()
            return False
        except Exception as e:
            logging.error(f"Error deleting {filename}: {e}")
            session.rollback()
            return False
        finally:
            close_db_session(session)

    def _save_user_preferences(self, session: Session, data: Dict[str, Any]) -> bool:
        """Save user preferences to database."""
        # Delete existing preferences and insert new ones
        session.query(UserPreferences).delete()

        prefs = UserPreferences(
            activity_types=data.get("activity_types", []),
            preferred_units=data.get("preferred_units", "imperial"),
            cache_enabled=data.get("cache_enabled", True),
            notifications_enabled=data.get("notifications_enabled", True),
        )
        session.add(prefs)
        session.commit()
        return True

    def _load_user_preferences(self, session: Session) -> Dict[str, Any]:
        """Load user preferences from database."""
        prefs = session.query(UserPreferences).first()
        if prefs:
            return {
                "activity_types": prefs.activity_types,
                "preferred_units": prefs.preferred_units,
                "cache_enabled": prefs.cache_enabled,
                "notifications_enabled": prefs.notifications_enabled,
            }
        else:
            # Return defaults if no preferences found
            return {
                "activity_types": ["outdoor", "indoor", "sports", "relaxation"],
                "preferred_units": "imperial",
                "cache_enabled": True,
                "notifications_enabled": True,
            }

    def _save_favorite_cities(self, session: Session, data: Dict[str, Any]) -> bool:
        """Save favorite cities to database."""
        cities = data.get("cities", [])  # WeatherService uses "cities" key

        # Clear existing favorites
        session.query(FavoriteCities).delete()

        # Add new favorites
        for city_data in cities:
            # Handle nested location structure from WeatherService
            location = city_data.get("location", {})
            city = FavoriteCities(
                city_name=location.get("name", ""),
                country_code=location.get("country", ""),
                latitude=location.get("latitude"),
                longitude=location.get("longitude"),
            )
            session.add(city)

        session.commit()
        return True

    def _load_favorite_cities(self, session: Session) -> Dict[str, Any]:
        """Load favorite cities from database."""
        cities = session.query(FavoriteCities).all()
        cities_data = []

        for city in cities:
            city_data = {
                "location": {
                    "name": city.city_name,
                    "country": city.country_code,
                    "latitude": city.latitude,
                    "longitude": city.longitude,
                },
                "nickname": city.city_name,  # Use city name as nickname
                "added_date": (
                    city.added_at.isoformat() if city.added_at is not None else None
                ),
                "last_viewed": None,  # Not stored in current schema
            }
            cities_data.append(city_data)

        return {
            "cities": cities_data,
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }

    def _save_weather_history(self, session: Session, data: Dict[str, Any]) -> bool:
        """Save weather history to database."""
        entries = data.get("entries", [])

        for entry in entries:
            # Check if entry already exists (avoid duplicates)
            existing = (
                session.query(WeatherHistory)
                .filter_by(
                    city_name=entry.get("city", ""),
                    timestamp=datetime.fromisoformat(
                        entry.get("timestamp", "").replace("Z", "")
                    ),
                )
                .first()
            )

            if not existing:
                weather_entry = WeatherHistory(
                    city_name=entry.get("city", ""),
                    country=entry.get("country", ""),
                    temperature=entry.get("temperature", 0.0),
                    condition=entry.get("condition", ""),
                    humidity=entry.get("humidity"),
                    wind_speed=entry.get("wind_speed"),
                    wind_direction=entry.get("wind_direction"),
                    pressure=entry.get("pressure"),
                    visibility=entry.get("visibility"),
                    timestamp=datetime.fromisoformat(
                        entry.get("timestamp", "").replace("Z", "")
                    ),
                )
                session.add(weather_entry)

        session.commit()
        return True

    def _load_weather_history(self, session: Session) -> Dict[str, Any]:
        """Load weather history from database."""
        entries = (
            session.query(WeatherHistory)
            .order_by(WeatherHistory.timestamp.desc())
            .all()
        )

        weather_entries = []
        for entry in entries:
            weather_data = {
                "city": entry.city_name,
                "country": entry.country,
                "temperature": entry.temperature,
                "condition": entry.condition,
                "timestamp": entry.timestamp.isoformat(),
            }

            # Add optional fields if they exist
            if entry.humidity is not None:
                weather_data["humidity"] = entry.humidity
            if entry.wind_speed is not None:
                weather_data["wind_speed"] = entry.wind_speed
            if entry.wind_direction is not None:
                weather_data["wind_direction"] = entry.wind_direction
            if entry.pressure is not None:
                weather_data["pressure"] = entry.pressure
            if entry.visibility is not None:
                weather_data["visibility"] = entry.visibility

            weather_entries.append(weather_data)

        return {
            "entries": weather_entries,
            "last_updated": datetime.utcnow().isoformat(),
        }

    def _save_journal_entries(self, session: Session, data: Dict[str, Any]) -> bool:
        """Save journal entries to database."""
        entries = data.get("entries", [])

        for entry in entries:
            # Check if entry already exists
            existing = (
                session.query(JournalEntries)
                .filter_by(
                    title=entry.get("title", ""),
                    created_at=datetime.fromisoformat(
                        entry.get("created_at", "").replace("Z", "")
                    ),
                )
                .first()
            )

            if not existing:
                journal_entry = JournalEntries(
                    title=entry.get("title", ""),
                    content=entry.get("content", ""),
                    weather_conditions=entry.get("weather_conditions"),
                    location=entry.get("location"),
                    mood=entry.get("mood"),
                    activities=entry.get("activities", []),
                    created_at=datetime.fromisoformat(
                        entry.get("created_at", "").replace("Z", "")
                    ),
                    updated_at=datetime.fromisoformat(
                        entry.get("updated_at", "").replace("Z", "")
                    ),
                )
                session.add(journal_entry)

        session.commit()
        return True

    def _load_journal_entries(self, session: Session) -> Dict[str, Any]:
        """Load journal entries from database."""
        entries = (
            session.query(JournalEntries)
            .order_by(JournalEntries.created_at.desc())
            .all()
        )

        journal_entries = []
        for entry in entries:
            journal_data = {
                "title": entry.title,
                "content": entry.content,
                "created_at": entry.created_at.isoformat() + "Z",
                "updated_at": entry.updated_at.isoformat() + "Z",
            }

            # Add optional fields if they exist
            if entry.weather_conditions is not None:
                journal_data["weather_conditions"] = entry.weather_conditions
            if entry.location is not None:
                journal_data["location"] = entry.location
            if entry.mood is not None:
                journal_data["mood"] = entry.mood
            if entry.activities is not None:
                journal_data["activities"] = entry.activities

            journal_entries.append(journal_data)

        return {
            "entries": journal_entries,
            "last_updated": datetime.utcnow().isoformat() + "Z",
        }

    # Additional methods for compatibility with existing interface
    def list_files(self) -> List[str]:
        """List available data types."""
        return [
            "user_preferences.json",
            "favorite_cities.json",
            "weather_history.json",
            "journal_entries.json",
        ]

    def file_exists(self, filename: str) -> bool:
        """Check if data exists for the given filename."""
        session = get_db_session()
        try:
            if filename == "user_preferences.json":
                return session.query(UserPreferences).first() is not None
            elif filename == "favorite_cities.json":
                return session.query(FavoriteCities).first() is not None
            elif filename == "weather_history.json":
                return session.query(WeatherHistory).first() is not None
            elif filename == "journal_entries.json":
                return session.query(JournalEntries).first() is not None
            return False
        except Exception as e:
            logging.error(f"Error checking file existence: {e}")
            return False
        finally:
            close_db_session(session)

    def get_file_size(self, filename: str) -> Optional[int]:
        """Get number of records for the given filename."""
        session = get_db_session()
        try:
            if filename == "user_preferences.json":
                return session.query(UserPreferences).count()
            elif filename == "favorite_cities.json":
                return session.query(FavoriteCities).count()
            elif filename == "weather_history.json":
                return session.query(WeatherHistory).count()
            elif filename == "journal_entries.json":
                return session.query(JournalEntries).count()
            return None
        except Exception as e:
            logging.error(f"Error getting file size: {e}")
            return None
        finally:
            close_db_session(session)
