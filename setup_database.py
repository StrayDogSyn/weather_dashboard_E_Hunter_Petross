"""Setup script for Weather Dashboard SQL database integration."""

import sys
import subprocess
import logging
from pathlib import Path


def install_sqlalchemy():
    """Install SQLAlchemy if not already installed."""
    try:
        import sqlalchemy
        print("✅ SQLAlchemy is already installed")
        return True
    except ImportError:
        print("Installing SQLAlchemy...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlalchemy>=2.0.0"])
            print("✅ SQLAlchemy installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install SQLAlchemy: {e}")
            return False


def setup_database():
    """Set up the SQL database and migrate existing data."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    print("🗃️ Weather Dashboard Database Setup")
    print("=" * 50)
    
    # Install SQLAlchemy
    if not install_sqlalchemy():
        print("❌ Cannot proceed without SQLAlchemy")
        return False
    
    try:
        # Now we can import the database modules
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        from data.database import init_database, DATABASE_PATH
        from services.storage_factory import DataStorageFactory
        
        print(f"📍 Database location: {DATABASE_PATH}")
        
        # Initialize the database
        print("🔧 Initializing database...")
        init_database()
        print("✅ Database initialized successfully")
        
        # Check if we can use SQL storage
        if DataStorageFactory.can_use_sql_storage():
            print("✅ SQL storage is available")
            
            # Check if there's existing JSON data to migrate
            json_files = [
                Path("data/user_preferences.json"),
                Path("data/favorite_cities.json"),
                Path("data/weather_history.json"),
                Path("data/journal_entries.json")
            ]
            
            has_json_data = any(f.exists() and f.stat().st_size > 0 for f in json_files)
            
            if has_json_data:
                print("📁 Found existing JSON data files")
                response = input("Would you like to migrate this data to SQL database? (y/n): ")
                
                if response.lower() in ['y', 'yes']:
                    print("🔄 Migrating data from JSON to SQL...")
                    success = DataStorageFactory.migrate_file_to_sql()
                    
                    if success:
                        print("✅ Data migration completed successfully")
                        
                        # Create backup directory and move JSON files
                        backup_dir = Path("data/json_backup")
                        backup_dir.mkdir(exist_ok=True)
                        
                        for json_file in json_files:
                            if json_file.exists():
                                backup_file = backup_dir / f"{json_file.name}.backup"
                                json_file.rename(backup_file)
                                print(f"📦 Backed up {json_file} to {backup_file}")
                        
                        print("✅ JSON files backed up successfully")
                    else:
                        print("❌ Data migration failed")
                        return False
                else:
                    print("⏭️ Skipping data migration")
            else:
                print("ℹ️ No existing JSON data found to migrate")
        else:
            print("❌ SQL storage dependencies not available")
            return False
        
        # Update configuration to use SQL storage
        print("⚙️ Updating configuration...")
        import os
        os.environ["WEATHER_STORAGE_TYPE"] = "sql"
        
        # Create .env file if it doesn't exist
        env_file = Path(".env")
        if not env_file.exists():
            with open(env_file, "w") as f:
                f.write("# Weather Dashboard Configuration\n")
                f.write("WEATHER_STORAGE_TYPE=sql\n")
                f.write(f"WEATHER_DATABASE_PATH={DATABASE_PATH}\n")
                f.write("\n# Add your OpenWeatherMap API key here:\n")
                f.write("# OPENWEATHER_API_KEY=your_api_key_here\n")
            print(f"✅ Created .env configuration file")
        else:
            print("ℹ️ .env file already exists")
        
        print("\n🎉 Database setup completed successfully!")
        print(f"📍 Database location: {DATABASE_PATH}")
        print("🚀 Your Weather Dashboard is now using SQL database storage")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        logging.error(f"Database setup failed: {e}")
        return False


if __name__ == "__main__":
    setup_database()
