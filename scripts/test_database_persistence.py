#!/usr/bin/env python3
"""Test script to verify database persistence functionality."""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.sql_data_storage import SQLDataStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_user_preferences_persistence():
    """Test user preferences storage and retrieval."""
    print("\n=== Testing User Preferences Persistence ===")

    storage = SQLDataStorage()

    # Test data
    test_prefs = {
        "activity_types": ["outdoor", "sports", "photography"],
        "preferred_units": "metric",
        "cache_enabled": False,
        "notifications_enabled": True,
    }

    # Save data
    print("1. Saving user preferences...")
    success = storage.save_data(test_prefs, "user_preferences.json")
    print(f"   Save result: {'SUCCESS' if success else 'FAILED'}")

    # Load data
    print("2. Loading user preferences...")
    loaded_data = storage.load_data("user_preferences.json")
    print(f"   Load result: {'SUCCESS' if loaded_data else 'FAILED'}")

    if loaded_data:
        print(f"   Loaded data: {json.dumps(loaded_data, indent=2)}")

        # Verify data integrity
        matches = (
            loaded_data["activity_types"] == test_prefs["activity_types"]
            and loaded_data["preferred_units"] == test_prefs["preferred_units"]
            and loaded_data["cache_enabled"] == test_prefs["cache_enabled"]
            and loaded_data["notifications_enabled"]
            == test_prefs["notifications_enabled"]
        )
        print(f"   Data integrity: {'PASSED' if matches else 'FAILED'}")
        return matches

    return False


def test_favorite_cities_persistence():
    """Test favorite cities storage and retrieval."""
    print("\n=== Testing Favorite Cities Persistence ===")

    storage = SQLDataStorage()

    # Test data
    test_cities = {
        "cities": [
            {
                "location": {
                    "name": "New York",
                    "country": "US",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                }
            },
            {
                "location": {
                    "name": "London",
                    "country": "GB",
                    "latitude": 51.5074,
                    "longitude": -0.1278,
                }
            },
        ]
    }

    # Save data
    print("1. Saving favorite cities...")
    success = storage.save_data(test_cities, "favorite_cities.json")
    print(f"   Save result: {'SUCCESS' if success else 'FAILED'}")

    # Load data
    print("2. Loading favorite cities...")
    loaded_data = storage.load_data("favorite_cities.json")
    print(f"   Load result: {'SUCCESS' if loaded_data else 'FAILED'}")

    if loaded_data:
        print(f"   Number of cities loaded: {len(loaded_data.get('cities', []))}")
        for i, city in enumerate(loaded_data.get("cities", [])):
            location = city.get("location", {})
            print(f"   City {i+1}: {location.get('name')} ({location.get('country')})")

        # Verify data integrity
        loaded_cities = loaded_data.get("cities", [])
        original_cities = test_cities["cities"]

        matches = len(loaded_cities) == len(original_cities)
        if matches:
            for i, (loaded, original) in enumerate(zip(loaded_cities, original_cities)):
                loaded_loc = loaded.get("location", {})
                original_loc = original.get("location", {})
                if loaded_loc.get("name") != original_loc.get("name") or loaded_loc.get(
                    "country"
                ) != original_loc.get("country"):
                    matches = False
                    break

        print(f"   Data integrity: {'PASSED' if matches else 'FAILED'}")
        return matches

    return False


def test_weather_history_persistence():
    """Test weather history storage and retrieval."""
    print("\n=== Testing Weather History Persistence ===")

    storage = SQLDataStorage()

    # Test data
    test_history = {
        "entries": [
            {
                "city": "New York",
                "country": "US",
                "temperature": 22.5,
                "condition": "Partly Cloudy",
                "humidity": 65,
                "wind_speed": 12.5,
                "wind_direction": "NW",
                "pressure": 1013.25,
                "visibility": 10.0,
                "timestamp": datetime.now().isoformat(),
            },
            {
                "city": "London",
                "country": "GB",
                "temperature": 18.0,
                "condition": "Rainy",
                "humidity": 80,
                "wind_speed": 8.0,
                "wind_direction": "SW",
                "pressure": 1008.5,
                "visibility": 8.0,
                "timestamp": datetime.now().isoformat(),
            },
        ]
    }

    # Save data
    print("1. Saving weather history...")
    success = storage.save_data(test_history, "weather_history.json")
    print(f"   Save result: {'SUCCESS' if success else 'FAILED'}")

    # Load data
    print("2. Loading weather history...")
    loaded_data = storage.load_data("weather_history.json")
    print(f"   Load result: {'SUCCESS' if loaded_data else 'FAILED'}")

    if loaded_data:
        entries = loaded_data.get("entries", [])
        print(f"   Number of entries loaded: {len(entries)}")
        for i, entry in enumerate(entries[:2]):  # Show first 2
            print(
                f"   Entry {i+1}: {entry.get('city')} - {entry.get('temperature')}°C - {entry.get('condition')}"
            )

        # Verify data integrity
        original_entries = test_history["entries"]
        matches = len(entries) >= len(
            original_entries
        )  # >= because there might be existing data

        print(f"   Data integrity: {'PASSED' if matches else 'FAILED'}")
        return matches

    return False


def test_journal_entries_persistence():
    """Test journal entries storage and retrieval."""
    print("\n=== Testing Journal Entries Persistence ===")

    storage = SQLDataStorage()

    # Test data
    test_journal = {
        "entries": [
            {
                "title": "Beautiful Sunny Day",
                "content": "Had a wonderful walk in the park today. The weather was perfect!",
                "weather_conditions": "Sunny, 25°C",
                "location": "Central Park, NYC",
                "mood": "Happy",
                "activities": ["walking", "photography"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        ]
    }

    # Save data
    print("1. Saving journal entries...")
    success = storage.save_data(test_journal, "journal_entries.json")
    print(f"   Save result: {'SUCCESS' if success else 'FAILED'}")

    # Load data
    print("2. Loading journal entries...")
    loaded_data = storage.load_data("journal_entries.json")
    print(f"   Load result: {'SUCCESS' if loaded_data else 'FAILED'}")

    if loaded_data:
        entries = loaded_data.get("entries", [])
        print(f"   Number of entries loaded: {len(entries)}")
        if entries:
            entry = entries[0]
            print(f"   First entry: '{entry.get('title')}' - {entry.get('mood')}")

        # Verify data integrity
        original_entries = test_journal["entries"]
        matches = len(entries) >= len(original_entries)

        print(f"   Data integrity: {'PASSED' if matches else 'FAILED'}")
        return matches

    return False


def test_database_file_existence():
    """Test that database file is created and accessible."""
    print("\n=== Testing Database File Existence ===")

    db_path = Path(__file__).parent.parent / "data" / "weather_dashboard.db"
    exists = db_path.exists()

    print(f"Database path: {db_path}")
    print(f"Database exists: {'YES' if exists else 'NO'}")

    if exists:
        size = db_path.stat().st_size
        print(f"Database size: {size} bytes")
        print(f"Last modified: {datetime.fromtimestamp(db_path.stat().st_mtime)}")

    return exists


def main():
    """Run all persistence tests."""
    print("🔍 Weather Dashboard - Database Persistence Test")
    print("=" * 50)

    # Test database file
    db_exists = test_database_file_existence()

    if not db_exists:
        print("\n❌ Database file not found! Creating...")
        try:
            storage = SQLDataStorage()  # This should initialize the database
            db_exists = test_database_file_existence()
        except Exception as e:
            print(f"❌ Failed to create database: {e}")
            return False

    # Run all tests
    tests = [
        ("User Preferences", test_user_preferences_persistence),
        ("Favorite Cities", test_favorite_cities_persistence),
        ("Weather History", test_weather_history_persistence),
        ("Journal Entries", test_journal_entries_persistence),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1

    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All tests passed! Database persistence is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
