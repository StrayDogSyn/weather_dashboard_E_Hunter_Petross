"""Standalone database setup script for Weather Dashboard."""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path


class DatabaseSetup:
    """Standalone database setup class."""

    def __init__(self, db_path: str = "data/weather_dashboard.db"):
        """Initialize database setup."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)

    def init_database(self):
        """Initialize database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # User preferences table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity_types TEXT,  -- JSON string
                    preferred_units TEXT DEFAULT 'imperial',
                    cache_enabled BOOLEAN DEFAULT 1,
                    notifications_enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Favorite cities table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS favorite_cities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT NOT NULL,
                    country_code TEXT,
                    latitude REAL,
                    longitude REAL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Weather history table
            cursor.execute(
                """
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
            """
            )

            # Journal entries table
            cursor.execute(
                """
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
            """
            )

            # Activity recommendations table
            cursor.execute(
                """
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
            """
            )

            conn.commit()
            print(f"✅ Database tables created at: {self.db_path}")

    def insert_default_data(self):
        """Insert default data if tables are empty."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Check if user preferences exist
            cursor.execute("SELECT COUNT(*) FROM user_preferences")
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    """
                    INSERT INTO user_preferences (activity_types, preferred_units, cache_enabled, notifications_enabled)
                    VALUES (?, ?, ?, ?)
                """,
                    ('["outdoor", "indoor", "sports", "relaxation"]', "imperial", 1, 1),
                )
                print("✅ Default user preferences inserted")

            # Check if activity recommendations exist
            cursor.execute("SELECT COUNT(*) FROM activity_recommendations")
            if cursor.fetchone()[0] == 0:
                activities = [
                    (
                        "Beach Day",
                        "Perfect for sunny, warm weather",
                        "outdoor",
                        75.0,
                        None,
                        '["clear", "sunny"]',
                        '["rain", "storm", "snow"]',
                    ),
                    (
                        "Museum Visit",
                        "Great indoor activity for any weather",
                        "indoor",
                        None,
                        None,
                        '["rain", "snow", "cold", "hot"]',
                        "[]",
                    ),
                    (
                        "Hiking",
                        "Outdoor adventure in good weather",
                        "outdoor",
                        50.0,
                        85.0,
                        '["clear", "partly cloudy"]',
                        '["rain", "storm", "snow"]',
                    ),
                    (
                        "Reading at Home",
                        "Perfect relaxation activity",
                        "relaxation",
                        None,
                        None,
                        '["rain", "snow", "cold"]',
                        "[]",
                    ),
                ]

                cursor.executemany(
                    """
                    INSERT INTO activity_recommendations 
                    (activity_name, description, category, min_temperature, max_temperature, suitable_conditions, unsuitable_conditions)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    activities,
                )
                print("✅ Default activity recommendations inserted")

            conn.commit()

    def migrate_json_file(self, json_path: Path, table_name: str) -> bool:
        """Migrate a specific JSON file to the database."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if table_name == "user_preferences":
                    cursor.execute("DELETE FROM user_preferences")
                    cursor.execute(
                        """
                        INSERT INTO user_preferences (activity_types, preferred_units, cache_enabled, notifications_enabled)
                        VALUES (?, ?, ?, ?)
                    """,
                        (
                            json.dumps(data.get("activity_types", [])),
                            data.get("preferred_units", "imperial"),
                            data.get("cache_enabled", True),
                            data.get("notifications_enabled", True),
                        ),
                    )

                elif table_name == "favorite_cities":
                    cursor.execute("DELETE FROM favorite_cities")
                    favorites = data.get("favorites", [])
                    for fav in favorites:
                        cursor.execute(
                            """
                            INSERT INTO favorite_cities (city_name, country_code, latitude, longitude)
                            VALUES (?, ?, ?, ?)
                        """,
                            (
                                fav.get("city", ""),
                                fav.get("country", ""),
                                fav.get("latitude"),
                                fav.get("longitude"),
                            ),
                        )

                elif table_name == "weather_history":
                    entries = data.get("entries", [])
                    for entry in entries:
                        # Check if entry already exists
                        cursor.execute(
                            """
                            SELECT COUNT(*) FROM weather_history 
                            WHERE city_name = ? AND timestamp = ?
                        """,
                            (entry.get("city", ""), entry.get("timestamp", "")),
                        )

                        if cursor.fetchone()[0] == 0:
                            cursor.execute(
                                """
                                INSERT INTO weather_history 
                                (city_name, country, temperature, condition, humidity, wind_speed, wind_direction, pressure, visibility, timestamp)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    entry.get("city", ""),
                                    entry.get("country", ""),
                                    entry.get("temperature", 0.0),
                                    entry.get("condition", ""),
                                    entry.get("humidity"),
                                    entry.get("wind_speed"),
                                    entry.get("wind_direction"),
                                    entry.get("pressure"),
                                    entry.get("visibility"),
                                    entry.get("timestamp", ""),
                                ),
                            )

                elif table_name == "journal_entries":
                    entries = data.get("entries", [])
                    for entry in entries:
                        # Check if entry already exists
                        cursor.execute(
                            """
                            SELECT COUNT(*) FROM journal_entries 
                            WHERE title = ? AND created_at = ?
                        """,
                            (entry.get("title", ""), entry.get("created_at", "")),
                        )

                        if cursor.fetchone()[0] == 0:
                            cursor.execute(
                                """
                                INSERT INTO journal_entries 
                                (title, content, weather_conditions, location, mood, activities, created_at, updated_at)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                                (
                                    entry.get("title", ""),
                                    entry.get("content", ""),
                                    entry.get("weather_conditions"),
                                    entry.get("location"),
                                    entry.get("mood"),
                                    json.dumps(entry.get("activities", [])),
                                    entry.get("created_at", ""),
                                    entry.get("updated_at", ""),
                                ),
                            )

                conn.commit()
                return True

        except Exception as e:
            print(f"❌ Error migrating {json_path}: {e}")
            return False

    def get_table_info(self) -> dict:
        """Get information about tables and record counts."""
        info = {}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                tables = [
                    "user_preferences",
                    "favorite_cities",
                    "weather_history",
                    "journal_entries",
                    "activity_recommendations",
                ]

                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    info[table] = cursor.fetchone()[0]

        except Exception as e:
            print(f"❌ Error getting table info: {e}")

        return info


def main():
    """Main setup function."""
    print("🗃️ Weather Dashboard Database Setup")
    print("=" * 50)

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    try:
        # Initialize database
        db_setup = DatabaseSetup()

        print("🔧 Initializing SQLite database...")
        db_setup.init_database()
        db_setup.insert_default_data()

        # Check for existing JSON data to migrate
        data_dir = Path("data")
        json_files = {
            "user_preferences.json": "user_preferences",
            "favorite_cities.json": "favorite_cities",
            "weather_history.json": "weather_history",
            "journal_entries.json": "journal_entries",
        }

        migration_candidates = []
        for json_file, table_name in json_files.items():
            json_path = data_dir / json_file
            if json_path.exists() and json_path.stat().st_size > 0:
                migration_candidates.append((json_path, table_name))

        if migration_candidates:
            print(f"📁 Found {len(migration_candidates)} JSON data files to migrate")
            response = input(
                "Would you like to migrate this data to SQL database? (y/n): "
            )

            if response.lower() in ["y", "yes"]:
                print("🔄 Migrating data from JSON to SQL...")

                successful_migrations = 0
                for json_path, table_name in migration_candidates:
                    print(f"  Migrating {json_path.name}...")

                    if db_setup.migrate_json_file(json_path, table_name):
                        print(f"  ✅ {json_path.name} migrated successfully")
                        successful_migrations += 1
                    else:
                        print(f"  ❌ Failed to migrate {json_path.name}")

                if successful_migrations == len(migration_candidates):
                    print("✅ All data migrated successfully")

                    # Create backup directory and move JSON files
                    backup_dir = data_dir / "json_backup"
                    backup_dir.mkdir(exist_ok=True)

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                    for json_path, _ in migration_candidates:
                        backup_file = (
                            backup_dir / f"{json_path.name}.backup_{timestamp}"
                        )
                        json_path.rename(backup_file)
                        print(f"📦 Backed up {json_path.name} to {backup_file.name}")
                else:
                    print(
                        f"⚠️ Only {successful_migrations}/{len(migration_candidates)} files migrated successfully"
                    )
            else:
                print("⏭️ Skipping data migration")
        else:
            print("ℹ️ No existing JSON data found to migrate")

        # Update configuration
        print("⚙️ Updating configuration...")

        env_file = Path(".env")
        env_content = []

        if env_file.exists():
            with open(env_file, "r") as f:
                env_content = f.readlines()

        # Update storage type setting
        storage_type_found = False
        for i, line in enumerate(env_content):
            if line.startswith("WEATHER_STORAGE_TYPE="):
                env_content[i] = "WEATHER_STORAGE_TYPE=sql\n"
                storage_type_found = True
                break

        if not storage_type_found:
            env_content.append("\n# Weather Dashboard Configuration\n")
            env_content.append("WEATHER_STORAGE_TYPE=sql\n")
            env_content.append(f"WEATHER_DATABASE_PATH={db_setup.db_path}\n")

        # Add API key placeholder if not present
        api_key_found = any(
            line.startswith("OPENWEATHER_API_KEY=") for line in env_content
        )
        if not api_key_found:
            env_content.append("\n# Add your OpenWeatherMap API key here:\n")
            env_content.append("# OPENWEATHER_API_KEY=your_api_key_here\n")

        with open(env_file, "w") as f:
            f.writelines(env_content)

        print("✅ Configuration updated in .env file")

        # Show database info
        table_info = db_setup.get_table_info()
        print("\n📊 Database Statistics:")
        for table, count in table_info.items():
            print(f"  {table}: {count} records")

        print("\n🎉 Database setup completed successfully!")
        print(f"📍 Database location: {db_setup.db_path.absolute()}")
        print("🚀 Your Weather Dashboard is now using SQL database storage")

        return True

    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False


if __name__ == "__main__":
    main()
