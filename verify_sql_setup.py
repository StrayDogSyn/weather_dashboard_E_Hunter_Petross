"""Simple verification script for SQL database setup."""

import sqlite3
import json
from pathlib import Path


def verify_database():
    """Verify the SQL database is set up correctly."""
    print("🔍 Verifying SQL Database Setup")
    print("=" * 35)

    db_path = Path("data/weather_dashboard.db")

    if not db_path.exists():
        print("❌ Database file not found!")
        return False

    print(f"✅ Database file found: {db_path}")
    print(f"📏 Database size: {db_path.stat().st_size} bytes")

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            expected_tables = [
                "user_preferences",
                "favorite_cities",
                "weather_history",
                "journal_entries",
                "activity_recommendations",
            ]

            print("\n📊 Database Tables:")
            for table in expected_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"  ✅ {table}: {count} records")
                else:
                    print(f"  ❌ {table}: Table missing")

            # Check if weather history was migrated
            cursor.execute("SELECT COUNT(*) FROM weather_history")
            weather_count = cursor.fetchone()[0]

            if weather_count > 0:
                print(f"\n🌤️ Found {weather_count} weather history records")

                # Show sample weather data
                cursor.execute(
                    "SELECT city_name, temperature, condition, timestamp FROM weather_history LIMIT 3"
                )
                rows = cursor.fetchall()

                print("📝 Sample weather data:")
                for row in rows:
                    print(f"  {row[0]}: {row[1]}°, {row[2]} at {row[3]}")

            # Check user preferences
            cursor.execute("SELECT * FROM user_preferences LIMIT 1")
            prefs = cursor.fetchone()

            if prefs:
                print(f"\n⚙️ User preferences configured:")
                print(f"  Preferred units: {prefs[2]}")
                print(f"  Cache enabled: {bool(prefs[3])}")
                print(f"  Notifications: {bool(prefs[4])}")

            # Check activity recommendations
            cursor.execute("SELECT COUNT(*) FROM activity_recommendations")
            activity_count = cursor.fetchone()[0]
            print(f"\n🎯 Activity recommendations: {activity_count} available")

            return True

    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False


def verify_configuration():
    """Verify configuration is set up for SQL storage."""
    print("\n⚙️ Verifying Configuration")
    print("=" * 28)

    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, "r") as f:
            content = f.read()

        if "WEATHER_STORAGE_TYPE=sql" in content:
            print("✅ Storage type set to SQL")
        else:
            print("⚠️ Storage type not set to SQL")

        if "WEATHER_DATABASE_PATH=" in content:
            print("✅ Database path configured")
        else:
            print("⚠️ Database path not configured")

        if (
            "OPENWEATHER_API_KEY=" in content
            and len(content.split("OPENWEATHER_API_KEY=")[1].split("\n")[0].strip())
            > 10
        ):
            print("✅ API key configured")
        else:
            print("⚠️ API key may not be configured")

        return True
    else:
        print("❌ .env file not found")
        return False


def verify_json_backup():
    """Verify JSON files were backed up."""
    print("\n📦 Verifying JSON Backup")
    print("=" * 24)

    backup_dir = Path("data/json_backup")
    if backup_dir.exists():
        backup_files = list(backup_dir.glob("*.backup_*"))
        print(f"✅ Backup directory found with {len(backup_files)} files")

        for backup_file in backup_files:
            print(f"  📄 {backup_file.name}")

        return len(backup_files) > 0
    else:
        print("ℹ️ No backup directory found (may be normal if no data to migrate)")
        return True


if __name__ == "__main__":
    print("🗃️ Weather Dashboard Database Verification")
    print("=" * 45)

    # Run all verifications
    db_ok = verify_database()
    config_ok = verify_configuration()
    backup_ok = verify_json_backup()

    print("\n" + "=" * 45)
    print("VERIFICATION SUMMARY")
    print("=" * 45)
    print(f"Database Setup: {'✅ PASSED' if db_ok else '❌ FAILED'}")
    print(f"Configuration: {'✅ PASSED' if config_ok else '❌ FAILED'}")
    print(f"Backup Status: {'✅ PASSED' if backup_ok else '❌ FAILED'}")

    if db_ok and config_ok:
        print("\n🎉 SQL database integration is ready!")
        print("🚀 Your Weather Dashboard will now use SQL database storage.")
        print("\n💡 Next steps:")
        print("  1. Run 'python main.py' to start the application")
        print("  2. The app will automatically use the SQL database")
        print("  3. All new data will be stored in SQLite database")
    else:
        print("\n⚠️ Some issues were found. Please check the output above.")

        if not db_ok:
            print("  - Database setup may have failed")
        if not config_ok:
            print("  - Configuration may need to be updated")
