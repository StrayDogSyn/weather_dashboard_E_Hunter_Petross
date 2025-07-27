-- Migration: 001_initial_schema
-- Description: Create initial database schema for weather dashboard
-- Version: 1
-- Created: 2024-01-01

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create favorite_locations table
CREATE TABLE IF NOT EXISTS favorite_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    country TEXT NOT NULL,
    state TEXT,
    timezone TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    display_order INTEGER DEFAULT 0,
    tags TEXT DEFAULT '[]', -- JSON array of strings
    notes TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    last_accessed TEXT,
    access_count INTEGER DEFAULT 0,
    
    -- Constraints
    CHECK (latitude >= -90 AND latitude <= 90),
    CHECK (longitude >= -180 AND longitude <= 180),
    CHECK (display_order >= 0),
    CHECK (access_count >= 0)
);

-- Create indexes for favorite_locations
CREATE INDEX IF NOT EXISTS idx_favorite_locations_coordinates ON favorite_locations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_favorite_locations_default ON favorite_locations(is_default);
CREATE INDEX IF NOT EXISTS idx_favorite_locations_display_order ON favorite_locations(display_order);
CREATE INDEX IF NOT EXISTS idx_favorite_locations_country ON favorite_locations(country);
CREATE INDEX IF NOT EXISTS idx_favorite_locations_access_count ON favorite_locations(access_count DESC);
CREATE INDEX IF NOT EXISTS idx_favorite_locations_last_accessed ON favorite_locations(last_accessed DESC);

-- Create journal_entries table
CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    entry_type TEXT NOT NULL DEFAULT 'PERSONAL', -- PERSONAL, WEATHER_LOG, ACTIVITY, REFLECTION
    weather_mood TEXT, -- SUNNY, CLOUDY, RAINY, STORMY, PEACEFUL, ENERGETIC
    location_name TEXT,
    latitude REAL,
    longitude REAL,
    weather_data TEXT, -- JSON weather snapshot
    tags TEXT DEFAULT '[]', -- JSON array of strings
    is_favorite BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    template_id TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    weather_date TEXT, -- Date the weather data refers to
    
    -- Constraints
    CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90)),
    CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180)),
    CHECK (entry_type IN ('PERSONAL', 'WEATHER_LOG', 'ACTIVITY', 'REFLECTION')),
    CHECK (weather_mood IS NULL OR weather_mood IN ('SUNNY', 'CLOUDY', 'RAINY', 'STORMY', 'PEACEFUL', 'ENERGETIC'))
);

-- Create indexes for journal_entries
CREATE INDEX IF NOT EXISTS idx_journal_entries_type ON journal_entries(entry_type);
CREATE INDEX IF NOT EXISTS idx_journal_entries_mood ON journal_entries(weather_mood);
CREATE INDEX IF NOT EXISTS idx_journal_entries_location ON journal_entries(location_name);
CREATE INDEX IF NOT EXISTS idx_journal_entries_coordinates ON journal_entries(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_journal_entries_favorite ON journal_entries(is_favorite);
CREATE INDEX IF NOT EXISTS idx_journal_entries_private ON journal_entries(is_private);
CREATE INDEX IF NOT EXISTS idx_journal_entries_created_at ON journal_entries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_journal_entries_weather_date ON journal_entries(weather_date DESC);
CREATE INDEX IF NOT EXISTS idx_journal_entries_template ON journal_entries(template_id);

-- Create settings table
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL, -- JSON value
    value_type TEXT NOT NULL DEFAULT 'string', -- string, number, boolean, object, array
    description TEXT,
    is_user_configurable BOOLEAN DEFAULT TRUE,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    -- Constraints
    UNIQUE(category, key),
    CHECK (value_type IN ('string', 'number', 'boolean', 'object', 'array'))
);

-- Create indexes for settings
CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category);
CREATE INDEX IF NOT EXISTS idx_settings_key ON settings(key);
CREATE INDEX IF NOT EXISTS idx_settings_category_key ON settings(category, key);
CREATE INDEX IF NOT EXISTS idx_settings_user_configurable ON settings(is_user_configurable);

-- Create weather_cache table
CREATE TABLE IF NOT EXISTS weather_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT NOT NULL UNIQUE,
    location_key TEXT NOT NULL, -- "lat,lon" format
    data_type TEXT NOT NULL, -- current, forecast, historical, alerts
    weather_data TEXT NOT NULL, -- JSON weather data
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    access_count INTEGER DEFAULT 0,
    last_accessed TEXT,
    
    -- Constraints
    CHECK (data_type IN ('current', 'forecast', 'historical', 'alerts')),
    CHECK (access_count >= 0)
);

-- Create indexes for weather_cache
CREATE INDEX IF NOT EXISTS idx_weather_cache_key ON weather_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_weather_cache_location ON weather_cache(location_key);
CREATE INDEX IF NOT EXISTS idx_weather_cache_type ON weather_cache(data_type);
CREATE INDEX IF NOT EXISTS idx_weather_cache_expires ON weather_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_weather_cache_location_type ON weather_cache(location_key, data_type);
CREATE INDEX IF NOT EXISTS idx_weather_cache_access_count ON weather_cache(access_count DESC);
CREATE INDEX IF NOT EXISTS idx_weather_cache_last_accessed ON weather_cache(last_accessed DESC);

-- Create user_preferences table
CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    preference_category TEXT NOT NULL,
    preference_data TEXT NOT NULL, -- JSON preferences data
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    
    -- Constraints
    UNIQUE(user_id, preference_category)
);

-- Create indexes for user_preferences
CREATE INDEX IF NOT EXISTS idx_user_preferences_user ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_category ON user_preferences(preference_category);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_category ON user_preferences(user_id, preference_category);

-- Create activity_log table
CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL DEFAULT 'default',
    activity_type TEXT NOT NULL, -- weather_check, location_add, journal_entry, etc.
    activity_data TEXT NOT NULL, -- JSON activity details
    location_name TEXT,
    latitude REAL,
    longitude REAL,
    created_at TEXT NOT NULL,
    session_id TEXT,
    
    -- Constraints
    CHECK (latitude IS NULL OR (latitude >= -90 AND latitude <= 90)),
    CHECK (longitude IS NULL OR (longitude >= -180 AND longitude <= 180))
);

-- Create indexes for activity_log
CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log(user_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_type ON activity_log(activity_type);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_activity_log_location ON activity_log(location_name);
CREATE INDEX IF NOT EXISTS idx_activity_log_coordinates ON activity_log(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_activity_log_session ON activity_log(session_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_user_type ON activity_log(user_id, activity_type);

-- Create migration_history table to track applied migrations
CREATE TABLE IF NOT EXISTS migration_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    checksum TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    execution_time_ms INTEGER,
    
    -- Constraints
    CHECK (version > 0),
    CHECK (execution_time_ms >= 0)
);

-- Create index for migration_history
CREATE INDEX IF NOT EXISTS idx_migration_history_version ON migration_history(version);
CREATE INDEX IF NOT EXISTS idx_migration_history_applied_at ON migration_history(applied_at DESC);

-- Insert default settings
INSERT OR IGNORE INTO settings (category, key, value, value_type, description, is_user_configurable, created_at, updated_at) VALUES
('weather', 'default_units', '"metric"', 'string', 'Default temperature units (metric/imperial)', true, datetime('now'), datetime('now')),
('weather', 'cache_duration_minutes', '15', 'number', 'Weather data cache duration in minutes', true, datetime('now'), datetime('now')),
('weather', 'forecast_days', '7', 'number', 'Number of forecast days to fetch', true, datetime('now'), datetime('now')),
('ui', 'theme', '"light"', 'string', 'UI theme (light/dark/auto)', true, datetime('now'), datetime('now')),
('ui', 'language', '"en"', 'string', 'Interface language', true, datetime('now'), datetime('now')),
('ui', 'show_detailed_weather', 'true', 'boolean', 'Show detailed weather information', true, datetime('now'), datetime('now')),
('notifications', 'weather_alerts', 'true', 'boolean', 'Enable weather alert notifications', true, datetime('now'), datetime('now')),
('notifications', 'daily_summary', 'false', 'boolean', 'Enable daily weather summary notifications', true, datetime('now'), datetime('now')),
('privacy', 'location_tracking', 'true', 'boolean', 'Allow location tracking for weather', true, datetime('now'), datetime('now')),
('privacy', 'data_retention_days', '365', 'number', 'Data retention period in days', false, datetime('now'), datetime('now')),
('api', 'rate_limit_per_minute', '60', 'number', 'API rate limit per minute', false, datetime('now'), datetime('now')),
('api', 'timeout_seconds', '30', 'number', 'API request timeout in seconds', false, datetime('now'), datetime('now')),
('cache', 'redis_ttl_seconds', '900', 'number', 'Default Redis cache TTL in seconds', false, datetime('now'), datetime('now')),
('cache', 'max_cache_size_mb', '100', 'number', 'Maximum cache size in MB', false, datetime('now'), datetime('now')),
('journal', 'auto_weather_capture', 'true', 'boolean', 'Automatically capture weather data in journal entries', true, datetime('now'), datetime('now')),
('journal', 'default_entry_type', '"PERSONAL"', 'string', 'Default journal entry type', true, datetime('now'), datetime('now'));

-- Insert default user preferences
INSERT OR IGNORE INTO user_preferences (user_id, preference_category, preference_data, created_at, updated_at) VALUES
('default', 'weather_display', '{"show_feels_like": true, "show_humidity": true, "show_wind": true, "show_pressure": false, "show_uv_index": true, "show_visibility": false}', datetime('now'), datetime('now')),
('default', 'location_preferences', '{"auto_detect_location": true, "save_search_history": true, "max_recent_locations": 10}', datetime('now'), datetime('now')),
('default', 'notification_preferences', '{"severe_weather_alerts": true, "daily_forecast": false, "rain_alerts": true, "temperature_thresholds": {"high": 35, "low": 0}}', datetime('now'), datetime('now')),
('default', 'activity_preferences', '{"preferred_categories": ["OUTDOOR", "SPORTS"], "difficulty_level": "MODERATE", "duration_preference": "MEDIUM"}', datetime('now'), datetime('now')),
('default', 'journal_preferences', '{"auto_location": true, "auto_weather": true, "default_privacy": false, "reminder_enabled": false, "reminder_time": "20:00"}', datetime('now'), datetime('now'));

-- Create triggers for automatic timestamp updates
CREATE TRIGGER IF NOT EXISTS update_favorite_locations_timestamp 
    AFTER UPDATE ON favorite_locations
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE favorite_locations SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_journal_entries_timestamp 
    AFTER UPDATE ON journal_entries
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE journal_entries SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_settings_timestamp 
    AFTER UPDATE ON settings
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE settings SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_weather_cache_timestamp 
    AFTER UPDATE ON weather_cache
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE weather_cache SET updated_at = datetime('now') WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_user_preferences_timestamp 
    AFTER UPDATE ON user_preferences
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE user_preferences SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- Create trigger to ensure only one default location
CREATE TRIGGER IF NOT EXISTS ensure_single_default_location
    AFTER UPDATE OF is_default ON favorite_locations
    FOR EACH ROW
    WHEN NEW.is_default = 1
BEGIN
    UPDATE favorite_locations 
    SET is_default = 0 
    WHERE id != NEW.id AND is_default = 1;
END;

-- Create trigger for weather cache cleanup
CREATE TRIGGER IF NOT EXISTS cleanup_expired_weather_cache
    AFTER INSERT ON weather_cache
BEGIN
    DELETE FROM weather_cache 
    WHERE expires_at < datetime('now')
    AND id != NEW.id;
END;

-- Create views for common queries
CREATE VIEW IF NOT EXISTS v_active_favorite_locations AS
SELECT 
    id, name, latitude, longitude, country, state, timezone,
    is_default, display_order, tags, notes,
    created_at, updated_at, last_accessed, access_count
FROM favorite_locations
ORDER BY display_order ASC, name ASC;

CREATE VIEW IF NOT EXISTS v_recent_journal_entries AS
SELECT 
    id, title, content, entry_type, weather_mood,
    location_name, latitude, longitude,
    tags, is_favorite, is_private,
    created_at, updated_at, weather_date
FROM journal_entries
ORDER BY created_at DESC
LIMIT 50;

CREATE VIEW IF NOT EXISTS v_weather_cache_stats AS
SELECT 
    data_type,
    COUNT(*) as total_entries,
    COUNT(CASE WHEN expires_at > datetime('now') THEN 1 END) as active_entries,
    COUNT(CASE WHEN expires_at <= datetime('now') THEN 1 END) as expired_entries,
    AVG(access_count) as avg_access_count,
    MAX(last_accessed) as last_access_time
FROM weather_cache
GROUP BY data_type;

-- Insert initial migration record
INSERT OR IGNORE INTO migration_history (version, name, checksum, applied_at, execution_time_ms)
VALUES (1, 'initial_schema', 'initial_schema_checksum_v1', datetime('now'), 0);