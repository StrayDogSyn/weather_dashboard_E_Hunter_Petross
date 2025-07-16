import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.storage_factory import DataStorageFactory

print("🔧 Current Environment Variables:")
print(f'WEATHER_STORAGE_TYPE: {os.getenv("WEATHER_STORAGE_TYPE", "<not set>")}')

print("\n🏭 Testing Storage Factory:")
storage = DataStorageFactory.create_storage()
print(f"Storage type: {type(storage).__name__}")
print(f"Storage class: {storage.__class__.__module__}.{storage.__class__.__name__}")

# Test that it's working
print("\n✅ Testing storage functionality:")
test_data = {"test": "data", "timestamp": "2025-07-15"}
save_result = storage.save_data(test_data, "user_preferences.json")
print(f'Save test: {"✅ SUCCESS" if save_result else "❌ FAILED"}')

load_result = storage.load_data("user_preferences.json")
print(f'Load test: {"✅ SUCCESS" if load_result else "❌ FAILED"}')

# Show what was loaded
if load_result:
    print(f"Loaded data keys: {list(load_result.keys())}")

print("\n📊 Storage verification complete!")
