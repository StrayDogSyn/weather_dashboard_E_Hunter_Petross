"""Storage Service Implementation for Weather Dashboard.

This module provides data persistence functionality with support
for SQLite database operations, backup management, and data validation.
"""

import json
import logging
import shutil
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ..business.interfaces import IStorageService
from ..shared.constants import DEFAULT_DATABASE_PATH
from ..shared.exceptions import StorageError


class StorageService(IStorageService):
    """SQLite-based storage service with backup and validation.

    Provides persistent storage for weather data, journal entries,
    user preferences, and application state with automatic backup
    and data integrity features.
    """

    def __init__(
        self,
        database_path: str = DEFAULT_DATABASE_PATH,
        backup_enabled: bool = True,
        backup_interval: int = 3600,
        max_backups: int = 5,
        connection_timeout: int = 30,
    ):
        """Initialize the storage service.

        Args:
            database_path: Path to SQLite database file
            backup_enabled: Whether to enable automatic backups
            backup_interval: Backup interval in seconds
            max_backups: Maximum number of backup files to keep
            connection_timeout: Database connection timeout in seconds
        """
        self._logger = logging.getLogger(self.__class__.__name__)

        # Configuration
        self._database_path = database_path
        self._backup_enabled = backup_enabled
        self._backup_interval = backup_interval
        self._max_backups = max_backups
        self._connection_timeout = connection_timeout

        # Threading
        self._lock = threading.RLock()
        self._backup_timer: Optional[threading.Timer] = None
        self._running = False

        # Initialize database
        self._initialize_database()

        # Start backup timer if enabled
        if self._backup_enabled:
            self._start_backup_timer()

    def _initialize_database(self) -> None:
        """Initialize the database with required tables.

        Raises:
            StorageError: If database initialization fails
        """
        try:
            # Ensure directory exists
            Path(self._database_path).parent.mkdir(parents=True, exist_ok=True)

            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Create tables
                self._create_tables(cursor)

                # Create indexes
                self._create_indexes(cursor)

                conn.commit()

            self._logger.info(f"Database initialized: {self._database_path}")

        except Exception as e:
            raise StorageError(
                f"Failed to initialize database: {e}",
                "StorageService",
                "initialize_database",
            ) from e

    def _create_tables(self, cursor: sqlite3.Cursor) -> None:
        """Create database tables.

        Args:
            cursor: Database cursor
        """
        # Weather data table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                country TEXT,
                data TEXT NOT NULL,
                timestamp REAL NOT NULL,
                created_at REAL NOT NULL DEFAULT (julianday('now'))
            )
        """
        )

        # Weather forecast table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_forecast (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                country TEXT,
                forecast_data TEXT NOT NULL,
                days INTEGER NOT NULL,
                timestamp REAL NOT NULL,
                created_at REAL NOT NULL DEFAULT (julianday('now'))
            )
        """
        )

        # Journal entries table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                content TEXT NOT NULL,
                weather_data TEXT,
                tags TEXT,
                created_at REAL NOT NULL DEFAULT (julianday('now')),
                updated_at REAL NOT NULL DEFAULT (julianday('now'))
            )
        """
        )

        # User preferences table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL DEFAULT (julianday('now'))
            )
        """
        )

        # Application state table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS application_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL DEFAULT (julianday('now'))
            )
        """
        )

        # Favorites table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                country TEXT,
                display_name TEXT,
                created_at REAL NOT NULL DEFAULT (julianday('now')),
                UNIQUE(city, country)
            )
        """
        )

        # Activity suggestions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                weather_condition TEXT NOT NULL,
                temperature_range TEXT NOT NULL,
                activity_data TEXT NOT NULL,
                created_at REAL NOT NULL DEFAULT (julianday('now'))
            )
        """
        )

    def _create_indexes(self, cursor: sqlite3.Cursor) -> None:
        """Create database indexes for performance.

        Args:
            cursor: Database cursor
        """
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_weather_data_city ON weather_data(city)",
            "CREATE INDEX IF NOT EXISTS idx_weather_data_timestamp ON weather_data(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_weather_forecast_city ON weather_forecast(city)",
            "CREATE INDEX IF NOT EXISTS idx_weather_forecast_timestamp ON weather_forecast(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_journal_entries_city ON journal_entries(city)",
            "CREATE INDEX IF NOT EXISTS idx_journal_entries_created_at ON journal_entries(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_favorites_city ON favorites(city)",
            "CREATE INDEX IF NOT EXISTS idx_activity_suggestions_condition ON activity_suggestions(weather_condition)",
        ]

        for index_sql in indexes:
            cursor.execute(index_sql)

    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper error handling.

        Yields:
            SQLite connection

        Raises:
            StorageError: If connection fails
        """
        conn = None
        try:
            conn = sqlite3.connect(
                self._database_path,
                timeout=self._connection_timeout,
                check_same_thread=False,
            )
            conn.row_factory = sqlite3.Row
            yield conn

        except Exception as e:
            if conn:
                conn.rollback()
            raise StorageError(
                f"Database connection failed: {e}", "StorageService", "get_connection"
            ) from e
        finally:
            if conn:
                conn.close()

    async def store(
        self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a value with optional metadata.

        Args:
            key: Storage key
            value: Value to store
            metadata: Optional metadata

        Returns:
            Storage ID or key

        Raises:
            StorageError: If storage operation fails
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    # Serialize value
                    serialized_value = json.dumps(value, default=str)
                    serialized_metadata = json.dumps(metadata or {}, default=str)

                    # Store in application_state table
                    cursor.execute(
                        "INSERT OR REPLACE INTO application_state (key, value) VALUES (?, ?)",
                        (
                            key,
                            json.dumps(
                                {
                                    "value": serialized_value,
                                    "metadata": serialized_metadata,
                                }
                            ),
                        ),
                    )

                    conn.commit()

                    self._logger.debug(f"Stored value for key: {key}")
                    return key

        except Exception as e:
            raise StorageError(
                f"Failed to store value: {e}", "StorageService", "store"
            ) from e

    async def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value by key.

        Args:
            key: Storage key

        Returns:
            Retrieved value or None if not found

        Raises:
            StorageError: If retrieval operation fails
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        "SELECT value FROM application_state WHERE key = ?", (key,)
                    )

                    row = cursor.fetchone()
                    if row is None:
                        return None

                    # Deserialize value
                    stored_data = json.loads(row["value"])
                    return json.loads(stored_data["value"])

        except Exception as e:
            raise StorageError(
                f"Failed to retrieve value: {e}", "StorageService", "retrieve"
            ) from e

    async def delete(self, key: str) -> bool:
        """Delete a value by key.

        Args:
            key: Storage key

        Returns:
            True if deleted, False if not found

        Raises:
            StorageError: If deletion operation fails
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        "DELETE FROM application_state WHERE key = ?", (key,)
                    )

                    conn.commit()

                    deleted = cursor.rowcount > 0
                    if deleted:
                        self._logger.debug(f"Deleted value for key: {key}")

                    return deleted

        except Exception as e:
            raise StorageError(
                f"Failed to delete value: {e}", "StorageService", "delete"
            ) from e

    async def query(
        self, filters: Dict[str, Any], limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query stored data with filters.

        Args:
            filters: Query filters
            limit: Optional result limit

        Returns:
            List of matching records

        Raises:
            StorageError: If query operation fails
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    # Build query based on filters
                    table = filters.get("table", "application_state")
                    conditions = []
                    params = []

                    for key, value in filters.items():
                        if key != "table":
                            conditions.append(f"{key} = ?")
                            params.append(value)

                    query = f"SELECT * FROM {table}"
                    if conditions:
                        query += " WHERE " + " AND ".join(conditions)

                    if limit:
                        query += f" LIMIT {limit}"

                    cursor.execute(query, params)
                    rows = cursor.fetchall()

                    # Convert to list of dictionaries
                    return [dict(row) for row in rows]

        except Exception as e:
            raise StorageError(
                f"Failed to query data: {e}", "StorageService", "query"
            ) from e

    async def store_weather_data(
        self, city: str, data: Dict[str, Any], country: Optional[str] = None
    ) -> str:
        """Store weather data for a city.

        Args:
            city: City name
            data: Weather data
            country: Optional country code

        Returns:
            Storage ID
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute(
                        "INSERT INTO weather_data (city, country, data, timestamp) VALUES (?, ?, ?, ?)",
                        (city, country, json.dumps(data, default=str), time.time()),
                    )

                    conn.commit()
                    return str(cursor.lastrowid)

        except Exception as e:
            raise StorageError(
                f"Failed to store weather data: {e}",
                "StorageService",
                "store_weather_data",
            ) from e

    async def store_journal_entry(
        self, city: str, content: str, weather_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a journal entry.

        Args:
            city: City name
            content: Journal content
            weather_data: Optional weather data

        Returns:
            Entry ID
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    weather_json = (
                        json.dumps(weather_data, default=str) if weather_data else None
                    )

                    cursor.execute(
                        "INSERT INTO journal_entries (city, content, weather_data) VALUES (?, ?, ?)",
                        (city, content, weather_json),
                    )

                    conn.commit()
                    return str(cursor.lastrowid)

        except Exception as e:
            raise StorageError(
                f"Failed to store journal entry: {e}",
                "StorageService",
                "store_journal_entry",
            ) from e

    async def get_journal_entries(
        self, city: Optional[str] = None, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get journal entries.

        Args:
            city: Optional city filter
            limit: Maximum number of entries

        Returns:
            List of journal entries
        """
        try:
            with self._lock:
                with self._get_connection() as conn:
                    cursor = conn.cursor()

                    if city:
                        cursor.execute(
                            "SELECT * FROM journal_entries WHERE city = ? ORDER BY created_at DESC LIMIT ?",
                            (city, limit),
                        )
                    else:
                        cursor.execute(
                            "SELECT * FROM journal_entries ORDER BY created_at DESC LIMIT ?",
                            (limit,),
                        )

                    rows = cursor.fetchall()

                    # Convert to list of dictionaries and parse JSON fields
                    entries = []
                    for row in rows:
                        entry = dict(row)
                        if entry["weather_data"]:
                            entry["weather_data"] = json.loads(entry["weather_data"])
                        entries.append(entry)

                    return entries

        except Exception as e:
            raise StorageError(
                f"Failed to get journal entries: {e}",
                "StorageService",
                "get_journal_entries",
            ) from e

    def _start_backup_timer(self) -> None:
        """Start the backup timer."""
        if self._running:
            return

        self._running = True
        self._schedule_backup()

    def _schedule_backup(self) -> None:
        """Schedule the next backup."""
        if not self._running:
            return

        self._backup_timer = threading.Timer(self._backup_interval, self._run_backup)
        self._backup_timer.daemon = True
        self._backup_timer.start()

    def _run_backup(self) -> None:
        """Run backup and schedule next one."""
        try:
            self._create_backup()
            self._cleanup_old_backups()
        except Exception as e:
            self._logger.error(f"Backup failed: {e}")
        finally:
            self._schedule_backup()

    def _create_backup(self) -> None:
        """Create a database backup."""
        try:
            if not Path(self._database_path).exists():
                return

            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self._database_path}.backup_{timestamp}"

            # Copy database file
            shutil.copy2(self._database_path, backup_path)

            self._logger.info(f"Database backup created: {backup_path}")

        except Exception as e:
            self._logger.error(f"Failed to create backup: {e}")

    def _cleanup_old_backups(self) -> None:
        """Remove old backup files."""
        try:
            backup_dir = Path(self._database_path).parent
            backup_pattern = f"{Path(self._database_path).name}.backup_*"

            # Find all backup files
            backup_files = list(backup_dir.glob(backup_pattern))

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

            # Remove excess backups
            for backup_file in backup_files[self._max_backups :]:
                backup_file.unlink()
                self._logger.debug(f"Removed old backup: {backup_file}")

        except Exception as e:
            self._logger.error(f"Failed to cleanup old backups: {e}")

    def shutdown(self) -> None:
        """Shutdown the storage service."""
        self._running = False

        if self._backup_timer:
            self._backup_timer.cancel()

        if self._backup_enabled:
            self._create_backup()

        self._logger.info("Storage service shutdown")

    def __del__(self):
        """Cleanup on destruction."""
        try:
            self.shutdown()
        except Exception:
            pass  # Ignore errors during cleanup
