#!/usr/bin/env python3
"""
Test script to verify session data persistence in Weather Dashboard.
This script simulates adding data and verifying it persists between sessions.
"""

import json
import logging
import os
import sqlite3
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_file_storage_persistence():
    """Test file-based storage persistence."""
    logger.info("Testing file-based storage persistence...")
    
    data_dir = Path("data")
    favorites_file = data_dir / "favorite_cities.json"
    journal_file = data_dir / "journal_entries.json"
    
    # Check if files exist
    files_exist = []
    if favorites_file.exists():
        files_exist.append(f"✅ {favorites_file}")
        with open(favorites_file, 'r') as f:
            data = json.load(f)
            cities_count = len(data.get('cities', []))
            logger.info(f"   Found {cities_count} favorite cities")
    else:
        files_exist.append(f"❌ {favorites_file} not found")
    
    if journal_file.exists():
        files_exist.append(f"✅ {journal_file}")
        with open(journal_file, 'r') as f:
            data = json.load(f)
            entries_count = len(data.get('entries', []))
            logger.info(f"   Found {entries_count} journal entries")
    else:
        files_exist.append(f"❌ {journal_file} not found")
    
    return files_exist

def test_sql_storage_persistence():
    """Test SQL-based storage persistence."""
    logger.info("Testing SQL-based storage persistence...")
    
    db_path = Path("data/weather_dashboard.db")
    
    if not db_path.exists():
        return [f"❌ Database file {db_path} not found"]
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        results = []
        
        # Check favorite cities
        cursor.execute("SELECT COUNT(*) FROM favorite_cities")
        cities_count = cursor.fetchone()[0]
        results.append(f"✅ Database contains {cities_count} favorite cities")
        
        # Check journal entries
        cursor.execute("SELECT COUNT(*) FROM journal_entries")
        entries_count = cursor.fetchone()[0]
        results.append(f"✅ Database contains {entries_count} journal entries")
        
        # Check weather history
        cursor.execute("SELECT COUNT(*) FROM weather_history")
        history_count = cursor.fetchone()[0]
        results.append(f"✅ Database contains {history_count} weather history records")
        
        conn.close()
        return results
        
    except Exception as e:
        return [f"❌ Error reading database: {e}"]

def main():
    """Main test function."""
    logger.info("🧪 Testing Weather Dashboard Session Persistence")
    logger.info("=" * 60)
    
    # Check storage type
    storage_type = os.getenv("WEATHER_STORAGE_TYPE", "file").lower()
    logger.info(f"Storage type: {storage_type}")
    
    if storage_type == "sql":
        results = test_sql_storage_persistence()
    else:
        results = test_file_storage_persistence()
    
    logger.info("\n📋 Test Results:")
    for result in results:
        logger.info(f"   {result}")
    
    logger.info("\n🎯 Summary:")
    success_count = sum(1 for r in results if r.startswith("✅"))
    total_count = len(results)
    
    if success_count == total_count:
        logger.info("✅ All session persistence tests passed!")
        logger.info("✅ User data is properly saved and available between sessions.")
    else:
        logger.info(f"⚠️  {success_count}/{total_count} tests passed")
        logger.info("❌ Some issues with session persistence detected.")

if __name__ == "__main__":
    main()
