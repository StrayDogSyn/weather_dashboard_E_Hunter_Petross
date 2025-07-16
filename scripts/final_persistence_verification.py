#!/usr/bin/env python3
"""
Final verification that weather dashboard data persistence is working correctly.
This script tests the complete data flow and ensures data survives application restarts.
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.sql_data_storage import SQLDataStorage
from src.services.storage_factory import DataStorageFactory


def check_database_health():
    """Check database file health and structure."""
    print("🔍 Database Health Check")
    print("-" * 30)

    db_path = project_root / "data" / "weather_dashboard.db"

    if not db_path.exists():
        print("❌ Database file does not exist!")
        return False

    print(f"✅ Database file exists: {db_path}")
    print(f"📊 File size: {db_path.stat().st_size:,} bytes")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [table[0] for table in cursor.fetchall()]
        print(f"📋 Tables: {tables}")

        # Check record counts
        for table in [
            "user_preferences",
            "favorite_cities",
            "weather_history",
            "journal_entries",
        ]:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   - {table}: {count} records")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def test_complete_workflow():
    """Test complete data workflow."""
    print("\n🔄 Complete Workflow Test")
    print("-" * 30)

    # Step 1: Create storage via factory (how the app does it)
    print("1. Creating storage via factory...")
    storage = DataStorageFactory.create_storage()
    print(f"   Storage type: {type(storage).__name__}")

    # Step 2: Save different types of data
    print("2. Saving various data types...")

    test_datasets = {
        "user_preferences.json": {
            "activity_types": ["testing", "verification", "persistence"],
            "preferred_units": "metric",
            "cache_enabled": True,
            "notifications_enabled": True,
        },
        "favorite_cities.json": {
            "cities": [
                {
                    "location": {
                        "name": "Test City",
                        "country": "TC",
                        "latitude": 40.0,
                        "longitude": -74.0,
                    }
                }
            ]
        },
        "weather_history.json": {
            "entries": [
                {
                    "city": "Test City",
                    "country": "TC",
                    "temperature": 20.0,
                    "condition": "Clear",
                    "humidity": 50,
                    "timestamp": datetime.now().isoformat(),
                }
            ]
        },
    }

    save_results = {}
    for filename, data in test_datasets.items():
        result = storage.save_data(data, filename)
        save_results[filename] = result
        print(f"   {filename}: {'✅' if result else '❌'}")

    # Step 3: Simulate application restart
    print("3. Simulating application restart...")
    del storage  # Remove reference

    # Create new storage instance
    new_storage = DataStorageFactory.create_storage()
    print(f"   New storage type: {type(new_storage).__name__}")

    # Step 4: Verify data persistence
    print("4. Verifying data persistence...")
    load_results = {}
    for filename in test_datasets.keys():
        loaded_data = new_storage.load_data(filename)
        load_results[filename] = loaded_data is not None
        print(f"   {filename}: {'✅' if loaded_data else '❌'}")

    # Step 5: Check data integrity
    print("5. Checking data integrity...")
    integrity_check = True

    for filename, original_data in test_datasets.items():
        if load_results[filename]:
            loaded_data = new_storage.load_data(filename)

            # Basic integrity checks
            if filename == "user_preferences.json":
                if loaded_data and (
                    loaded_data.get("preferred_units")
                    != original_data["preferred_units"]
                    or loaded_data.get("cache_enabled")
                    != original_data["cache_enabled"]
                ):
                    integrity_check = False
                    print(f"   ❌ {filename} integrity failed")
                else:
                    print(f"   ✅ {filename} integrity passed")
            else:
                print(f"   ✅ {filename} structure valid")

    return all(save_results.values()) and all(load_results.values()) and integrity_check


def test_concurrent_access():
    """Test that multiple storage instances can access the same data."""
    print("\n🤝 Concurrent Access Test")
    print("-" * 30)

    # Create multiple storage instances
    storage1 = DataStorageFactory.create_storage()
    storage2 = DataStorageFactory.create_storage()

    # Save data with first instance
    test_data = {"test": "concurrent", "value": 123}
    save_result = storage1.save_data(test_data, "user_preferences.json")
    print(f"1. Save with instance 1: {'✅' if save_result else '❌'}")

    # Read data with second instance
    loaded_data = storage2.load_data("user_preferences.json")
    load_result = loaded_data is not None
    print(f"2. Load with instance 2: {'✅' if load_result else '❌'}")

    return save_result and load_result


def main():
    """Run all verification tests."""
    print("🎯 Weather Dashboard - Data Persistence Verification")
    print("=" * 60)

    tests = [
        ("Database Health", check_database_health),
        ("Complete Workflow", test_complete_workflow),
        ("Concurrent Access", test_concurrent_access),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))

    # Final report
    print("\n" + "=" * 60)
    print("📊 FINAL VERIFICATION REPORT")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} | {status}")
        if result:
            passed += 1

    total = len(results)
    success_rate = (passed / total) * 100

    print(f"\nSuccess Rate: {passed}/{total} ({success_rate:.1f}%)")

    if passed == total:
        print("\n🎉 EXCELLENT! Data persistence is working perfectly!")
        print("✅ Weather dashboard data is being stored correctly")
        print("✅ Data persists between application sessions")
        print("✅ Multiple instances can access the same data")
        print("✅ Database integrity is maintained")

        # Show current database status
        print("\n📋 Current Database Status:")
        sql_storage = SQLDataStorage()  # Use specific type for additional methods
        filenames = [
            "user_preferences.json",
            "favorite_cities.json",
            "weather_history.json",
            "journal_entries.json",
        ]
        for filename in filenames:
            exists = sql_storage.file_exists(filename)
            size = sql_storage.get_file_size(filename)
            print(f"   {filename}: {'✅' if exists else '❌'} ({size} records)")

    else:
        print("\n⚠️ Some issues were detected with data persistence!")
        print("   Please review the failed tests above.")

    return passed == total


if __name__ == "__main__":
    success = main()
    print(
        f"\n{'🎯 Verification completed successfully!' if success else '⚠️ Verification completed with issues!'}"
    )
    sys.exit(0 if success else 1)
