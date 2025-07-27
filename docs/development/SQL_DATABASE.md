# SQL Database Integration

The Weather Dashboard uses SQLite for robust data management, offering improved performance, data integrity,
and advanced querying capabilities.

## Overview

The application implements a hybrid storage system that supports:

- **SQL Database** (SQLite) - Primary storage for better performance and data integrity
- **JSON Files** - Backup storage and data export functionality
- **Automatic Backups** - Daily JSON backups of critical data

## Database Features

### 🗃️ Database Structure

The SQLite database (`data/weather_dashboard.db`) includes the following tables:

1. **user_preferences**
   - User interface settings
   - Unit preferences (°C/°F)
   - Auto-refresh intervals
   - Visual theme settings

2. **favorite_cities**
   - City name and coordinates
   - Display order
   - Last update timestamp
   - Custom city labels

3. **weather_history**
   - Historical weather data
   - Timestamp and location
   - Temperature, humidity, pressure
   - Weather conditions and descriptions

4. **journal_entries**
   - Daily weather journal entries
   - Mood and activity tracking
   - Weather impact notes
   - Timestamps and locations

5. **activity_suggestions**
   - Weather-based activity recommendations
   - Condition mappings
   - User feedback and ratings
   - Seasonal adjustments

### 📊 Automatic Data Migration

When you first run the SQL setup, the system will:

- Create the SQLite database structure
- Migrate existing JSON data to SQL tables
- Backup original JSON files to `data/json_backup/`
- Update configuration to use SQL storage

## Setup Instructions

### Step 1: Install Dependencies

SQLAlchemy is optional but recommended for advanced features:

```bash
pip install sqlalchemy
```

### Step 2: Run Database Setup

Execute the setup script to initialize the database:

```bash
python setup_sql_database.py
```

This script will:

- Create the SQLite database at `data/weather_dashboard.db`
- Set up all required tables
- Migrate existing JSON data (if any)
- Update your `.env` configuration

### Step 3: Verify Setup

Run the verification script to ensure everything is working:

```bash
python verify_sql_setup.py
```

## Configuration

The application uses environment variables to control storage behavior:

```env
# Use SQL database storage
WEATHER_STORAGE_TYPE=sql

# Database file location
WEATHER_DATABASE_PATH=data/weather_dashboard.db

# Alternative: Use legacy JSON files
# WEATHER_STORAGE_TYPE=file
```

## Technical Architecture

### Storage Factory Pattern

The application uses a factory pattern to create the appropriate storage implementation:

```python
from services.storage_factory import DataStorageFactory

# Automatically chooses SQL or file storage based on configuration
storage = DataStorageFactory.create_storage()
```

### Storage Implementations

1. **SQLDataStorage** - SQLAlchemy-based implementation (requires SQLAlchemy)
2. **FileDataStorage** - JSON file storage for backward compatibility

### Backward Compatibility

The application maintains full backward compatibility:

- Existing installations continue to work with JSON files
- Data migration is optional and reversible
- Same API interfaces regardless of storage backend

## Database Management

### Viewing Database Contents

You can inspect the database using any SQLite browser or command line:

```bash
sqlite3 data/weather_dashboard.db

.tables                    # List all tables
SELECT * FROM weather_history LIMIT 5;  # View weather data
```

### Backup and Recovery

The database file can be easily backed up:

```bash
# Backup
cp data/weather_dashboard.db data/weather_dashboard_backup.db

# Restore
cp data/weather_dashboard_backup.db data/weather_dashboard.db
```

### Performance Benefits

SQL storage provides several advantages:

1. **Faster Queries** - Indexed searches and efficient filtering
2. **Data Integrity** - ACID transactions and constraints
3. **Concurrent Access** - Better handling of multiple operations
4. **Scalability** - Handles larger datasets efficiently
5. **Query Flexibility** - SQL queries for complex data analysis

## Data Migration

### Automatic Migration

The setup script automatically migrates data from JSON to SQL format:

```text
data/user_preferences.json    → user_preferences table
data/favorite_cities.json     → favorite_cities table
data/weather_history.json     → weather_history table
data/journal_entries.json     → journal_entries table
```

### Manual Migration

You can also migrate data programmatically:

```python
from services.storage_factory import DataStorageFactory

# Create storage instances
file_storage = DataStorageFactory._create_file_storage()
sql_storage = DataStorageFactory._create_sql_storage()

# Migrate specific data
data = file_storage.load_data("weather_history.json")
sql_storage.save_data(data, "weather_history.json")
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the project root directory
   - Check that the virtual environment is activated

2. **Database Locked**
   - Close any other applications accessing the database
   - Restart the application

3. **Migration Failures**
   - Check file permissions in the `data/` directory
   - Verify JSON files are valid format

### Switching Back to JSON Storage

To revert to JSON file storage:

1. Update `.env` file:

   ```env
   WEATHER_STORAGE_TYPE=file
   ```

2. Restore JSON files from backup:

   ```bash
   cp data/json_backup/*.json data/
   ```

## File Structure

After SQL setup, your project structure will include:

```text
data/
├── weather_dashboard.db        # SQLite database
├── database.py                 # Database models (SQLAlchemy)
└── json_backup/               # Backup of original JSON files
    ├── user_preferences.json.backup_YYYYMMDD_HHMMSS
    ├── favorite_cities.json.backup_YYYYMMDD_HHMMSS
    ├── weather_history.json.backup_YYYYMMDD_HHMMSS
    └── journal_entries.json.backup_YYYYMMDD_HHMMSS

src/services/
├── storage_factory.py          # Storage implementation factory
├── sql_data_storage.py         # SQLAlchemy implementation
└── data_storage.py             # File-based storage implementation
```

## Future Enhancements

The SQL database foundation enables future features:

- Advanced weather data analytics
- User account management
- Data export/import capabilities
- Real-time data synchronization
- Multi-user support
- Cloud database integration

## Support

If you encounter any issues with the SQL database integration:

1. Run `python verify_sql_setup.py` to diagnose problems
2. Check the application logs for error messages
3. Ensure all dependencies are installed correctly
4. Review the troubleshooting section above

The SQL database integration provides a robust foundation for the Weather Dashboard while maintaining
simplicity and ease of use.
