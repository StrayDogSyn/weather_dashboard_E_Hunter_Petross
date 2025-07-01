"""Database migration script to move data from JSON files to SQL database."""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add the src directory to the path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from data.database import init_database
    from services.sql_data_storage import SQLDataStorage
    from services.data_storage import FileDataStorage
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure SQLAlchemy is installed: pip install sqlalchemy")
    sys.exit(1)


def migrate_json_to_sql():
    """Migrate existing JSON data to SQL database."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize SQL storage
        sql_storage = SQLDataStorage()
        file_storage = FileDataStorage(data_dir="data")
        
        logging.info("Starting migration from JSON to SQL database...")
        
        # Files to migrate
        files_to_migrate = [
            "user_preferences.json",
            "favorite_cities.json", 
            "weather_history.json",
            "journal_entries.json"
        ]
        
        migration_results = {}
        
        for filename in files_to_migrate:
            logging.info(f"Migrating {filename}...")
            
            # Load data from JSON file
            json_data = file_storage.load_data(filename)
            
            if json_data is None:
                logging.warning(f"No data found in {filename}, skipping...")
                migration_results[filename] = "skipped - no data"
                continue
            
            # Save data to SQL database
            success = sql_storage.save_data(json_data, filename)
            
            if success:
                logging.info(f"Successfully migrated {filename}")
                migration_results[filename] = "success"
            else:
                logging.error(f"Failed to migrate {filename}")
                migration_results[filename] = "failed"
        
        # Create backup of original JSON files
        backup_dir = Path("data") / "json_backup"
        backup_dir.mkdir(exist_ok=True)
        
        for filename in files_to_migrate:
            json_file = Path("data") / filename
            if json_file.exists():
                backup_file = backup_dir / f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                json_file.rename(backup_file)
                logging.info(f"Backed up {filename} to {backup_file}")
        
        # Print migration summary
        print("\n" + "="*50)
        print("MIGRATION SUMMARY")
        print("="*50)
        
        for filename, result in migration_results.items():
            print(f"{filename}: {result}")
        
        print(f"\nOriginal JSON files backed up to: {backup_dir}")
        print("Migration completed!")
        
        # Verify migration by loading data back
        print("\nVerifying migration...")
        for filename in files_to_migrate:
            if migration_results.get(filename) == "success":
                data = sql_storage.load_data(filename)
                if data:
                    print(f"✓ {filename}: Data successfully loaded from SQL database")
                else:
                    print(f"✗ {filename}: Failed to load data from SQL database")
                    
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        print(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    migrate_json_to_sql()
