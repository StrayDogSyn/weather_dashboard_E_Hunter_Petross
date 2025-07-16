#!/usr/bin/env python3
"""Test session persistence - verify data survives application restarts."""

import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.sql_data_storage import SQLDataStorage


def test_session_persistence():
    """Test that data persists between sessions."""
    print("🔄 Testing Session Persistence")
    print("=" * 40)

    # Create NEW instance (simulates new session)
    storage1 = SQLDataStorage()

    # Save some test data
    session_data = {
        "activity_types": ["hiking", "photography", "cycling"],
        "preferred_units": "metric",
        "cache_enabled": True,
        "notifications_enabled": False,
    }

    print("1️⃣ Session 1: Saving data...")
    save_result = storage1.save_data(session_data, "user_preferences.json")
    print(f"   Save result: {'✅ SUCCESS' if save_result else '❌ FAILED'}")

    # Load data to verify it was saved
    loaded_data1 = storage1.load_data("user_preferences.json")
    print(f"   Verification: {'✅ DATA SAVED' if loaded_data1 else '❌ NO DATA'}")

    # Simulate application restart by creating a completely new instance
    print("\n2️⃣ Session 2: Simulating application restart...")
    storage2 = SQLDataStorage()  # NEW instance

    # Try to load the data that was saved in the previous "session"
    loaded_data2 = storage2.load_data("user_preferences.json")
    print(f"   Load result: {'✅ SUCCESS' if loaded_data2 else '❌ FAILED'}")

    if loaded_data2:
        print(f"   Data integrity check:")
        matches = (
            loaded_data2["activity_types"] == session_data["activity_types"]
            and loaded_data2["preferred_units"] == session_data["preferred_units"]
            and loaded_data2["cache_enabled"] == session_data["cache_enabled"]
            and loaded_data2["notifications_enabled"]
            == session_data["notifications_enabled"]
        )
        print(f"   {'✅ PASSED' if matches else '❌ FAILED'} - Data matches original")

        # Show the data
        print(f"   Activity types: {loaded_data2['activity_types']}")
        print(f"   Units: {loaded_data2['preferred_units']}")
        print(f"   Cache enabled: {loaded_data2['cache_enabled']}")
        print(f"   Notifications: {loaded_data2['notifications_enabled']}")

        return matches

    return False


def test_multiple_data_types():
    """Test persistence of multiple data types."""
    print("\n🗂️ Testing Multiple Data Types Persistence")
    print("=" * 40)

    storage = SQLDataStorage()

    # Test different data types
    test_cases = [
        (
            "user_preferences.json",
            {
                "activity_types": ["test1", "test2"],
                "preferred_units": "imperial",
                "cache_enabled": False,
                "notifications_enabled": True,
            },
        ),
        (
            "favorite_cities.json",
            {
                "cities": [
                    {
                        "location": {
                            "name": "Paris",
                            "country": "FR",
                            "latitude": 48.8566,
                            "longitude": 2.3522,
                        }
                    }
                ]
            },
        ),
        (
            "journal_entries.json",
            {
                "entries": [
                    {
                        "title": "Persistence Test Entry",
                        "content": "Testing database persistence functionality",
                        "mood": "confident",
                        "activities": ["testing", "coding"],
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat(),
                    }
                ]
            },
        ),
    ]

    results = []

    for filename, test_data in test_cases:
        print(f"\n📝 Testing {filename}:")

        # Save data
        save_result = storage.save_data(test_data, filename)
        print(f"   Save: {'✅' if save_result else '❌'}")

        # Create new storage instance (simulate restart)
        new_storage = SQLDataStorage()

        # Load data
        loaded_data = new_storage.load_data(filename)
        load_success = loaded_data is not None
        print(f"   Load: {'✅' if load_success else '❌'}")

        # Check file exists
        exists = new_storage.file_exists(filename)
        size = new_storage.get_file_size(filename)
        print(f"   Exists: {'✅' if exists else '❌'}, Records: {size}")

        results.append(save_result and load_success and exists)

    all_passed = all(results)
    print(f"\n📊 Overall result: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")

    return all_passed


def main():
    """Run all persistence tests."""
    print("🔍 Weather Dashboard - Session Persistence Test")
    print("=" * 50)

    # Test 1: Basic session persistence
    test1_result = test_session_persistence()

    # Test 2: Multiple data types
    test2_result = test_multiple_data_types()

    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL RESULTS")
    print("=" * 50)

    print(f"Session Persistence: {'✅ PASSED' if test1_result else '❌ FAILED'}")
    print(f"Multiple Data Types: {'✅ PASSED' if test2_result else '❌ FAILED'}")

    overall_success = test1_result and test2_result
    print(
        f"\nOverall: {'🎉 ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}"
    )

    if overall_success:
        print("\n✅ Data is being stored correctly and persists between sessions!")
        print("✅ The weather_dashboard.db is working as expected!")
    else:
        print("\n❌ There are issues with data persistence that need to be addressed.")

    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
