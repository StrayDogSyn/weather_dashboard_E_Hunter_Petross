import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from datetime import datetime

from src.services.sql_data_storage import SQLDataStorage

storage = SQLDataStorage()

# Test weather history data
weather_data = {
    "entries": [
        {
            "city": "New York",
            "country": "US",
            "temperature": 22.5,
            "condition": "Partly Cloudy",
            "humidity": 65,
            "wind_speed": 12.5,
            "timestamp": datetime.now().isoformat(),
        }
    ]
}

print("💾 Saving weather history...")
save_result = storage.save_data(weather_data, "weather_history.json")
print(f"Save result: {save_result}")

print("📖 Loading weather history...")
loaded_data = storage.load_data("weather_history.json")
entries = loaded_data.get("entries", []) if loaded_data else []
print(f"Number of entries: {len(entries)}")
if entries:
    entry = entries[0]
    print(f'Latest entry: {entry.get("city")} - {entry.get("temperature")}°C')

# Check database size
size = storage.get_file_size("weather_history.json")
print(f"Total records in database: {size}")
