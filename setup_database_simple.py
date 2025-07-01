"""Simple database setup script for Weather Dashboard."""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_database():
    """Set up the SQL database and migrate existing data."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🗃️ Weather Dashboard Database Setup")
    print("=" * 50)
    
    try:
        # Add the src directory to the path to import modules
        project_root = Path(__file__).parent
        src_path = project_root / "src"
        sys.path.insert(0, str(src_path))
        
        # Import with absolute imports
        import services.sqlite_helper
        import services.simple_sql_storage
        
        SQLiteHelper = services.sqlite_helper.SQLiteHelper
        SimpleSQLDataStorage = services.simple_sql_storage.SimpleSQLDataStorage
        
        # Initialize database
        print("🔧 Initializing SQLite database...")
        db_path = "data/weather_dashboard.db"
        db_helper = SQLiteHelper(db_path)
        db_helper.init_database()
        db_helper.insert_default_data()
        
        print(f"✅ Database initialized at: {db_path}")
        
        # Check for existing JSON data to migrate
        data_dir = Path("data")
        json_files = {
            "user_preferences.json": "user_preferences",
            "favorite_cities.json": "favorite_cities", 
            "weather_history.json": "weather_history",
            "journal_entries.json": "journal_entries"
        }
        
        has_data_to_migrate = False
        migration_files = []
        
        for json_file, table_name in json_files.items():
            json_path = data_dir / json_file
            if json_path.exists() and json_path.stat().st_size > 0:
                has_data_to_migrate = True
                migration_files.append((json_path, table_name))
        
        if has_data_to_migrate:
            print(f"📁 Found {len(migration_files)} JSON data files to migrate")
            response = input("Would you like to migrate this data to SQL database? (y/n): ")
            
            if response.lower() in ['y', 'yes']:
                print("🔄 Migrating data from JSON to SQL...")
                
                successful_migrations = 0
                
                for json_path, table_name in migration_files:
                    print(f"  Migrating {json_path.name}...")
                    
                    try:
                        # Load JSON data
                        with open(json_path, 'r', encoding='utf-8') as f:
                            json_data = json.load(f)
                        
                        # Migrate to SQL
                        success = db_helper.migrate_json_data(json_data, table_name)
                        
                        if success:
                            print(f"  ✅ {json_path.name} migrated successfully")
                            successful_migrations += 1
                        else:
                            print(f"  ❌ Failed to migrate {json_path.name}")
                            
                    except Exception as e:
                        print(f"  ❌ Error migrating {json_path.name}: {e}")
                
                if successful_migrations == len(migration_files):
                    print("✅ All data migrated successfully")
                    
                    # Create backup directory and move JSON files
                    backup_dir = data_dir / "json_backup"
                    backup_dir.mkdir(exist_ok=True)
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    
                    for json_path, _ in migration_files:
                        backup_file = backup_dir / f"{json_path.name}.backup_{timestamp}"
                        json_path.rename(backup_file)
                        print(f"📦 Backed up {json_path.name} to {backup_file.name}")
                    
                else:
                    print(f"⚠️ Only {successful_migrations}/{len(migration_files)} files migrated successfully")
            else:
                print("⏭️ Skipping data migration")
        else:
            print("ℹ️ No existing JSON data found to migrate")
        
        # Update configuration
        print("⚙️ Updating configuration...")
        
        # Create/update .env file
        env_file = Path(".env")
        env_content = []
        
        if env_file.exists():
            with open(env_file, 'r') as f:
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
            env_content.append(f"WEATHER_DATABASE_PATH={db_path}\n")
        
        # Add API key placeholder if not present
        api_key_found = any(line.startswith("OPENWEATHER_API_KEY=") for line in env_content)
        if not api_key_found:
            env_content.append("\n# Add your OpenWeatherMap API key here:\n")
            env_content.append("# OPENWEATHER_API_KEY=your_api_key_here\n")
        
        with open(env_file, 'w') as f:
            f.writelines(env_content)
        
        print(f"✅ Configuration updated in .env file")
        
        # Show database info
        table_info = db_helper.get_table_info()
        print("\n📊 Database Statistics:")
        for table, count in table_info.items():
            print(f"  {table}: {count} records")
        
        print("\n🎉 Database setup completed successfully!")
        print(f"📍 Database location: {Path(db_path).absolute()}")
        print("🚀 Your Weather Dashboard is now using SQL database storage")
        
        # Test the storage
        print("\n🧪 Testing SQL storage...")
        try:
            storage = SimpleSQLDataStorage(db_path)
            test_data = storage.load_data("user_preferences.json")
            if test_data:
                print("✅ SQL storage is working correctly")
            else:
                print("⚠️ SQL storage test returned no data (this may be normal)")
        except Exception as e:
            print(f"❌ SQL storage test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        logging.error(f"Database setup failed: {e}")
        return False


if __name__ == "__main__":
    setup_database()
