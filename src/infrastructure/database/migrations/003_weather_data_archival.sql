-- Migration: 003_weather_data_archival
-- Description: Add weather data archival and cleanup functionality
-- Version: 3
-- Created: 2024-01-03

-- Create weather_archive table for long-term storage
CREATE TABLE IF NOT EXISTS weather_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_cache_id INTEGER,
    location_key TEXT NOT NULL,
    data_type TEXT NOT NULL,
    weather_data TEXT NOT NULL, -- Compressed JSON weather data
    archived_at TEXT NOT NULL,
    original_created_at TEXT NOT NULL,
    access_count INTEGER DEFAULT 0,
    data_size_bytes INTEGER,
    compression_ratio REAL,
    
    -- Constraints
    CHECK (data_type IN ('current', 'forecast', 'historical', 'alerts')),
    CHECK (access_count >= 0),
    CHECK (data_size_bytes > 0),
    CHECK (compression_ratio > 0)
);

-- Create indexes for weather_archive
CREATE INDEX IF NOT EXISTS idx_weather_archive_location ON weather_archive(location_key);
CREATE INDEX IF NOT EXISTS idx_weather_archive_type ON weather_archive(data_type);
CREATE INDEX IF NOT EXISTS idx_weather_archive_archived_at ON weather_archive(archived_at DESC);
CREATE INDEX IF NOT EXISTS idx_weather_archive_original_created ON weather_archive(original_created_at DESC);
CREATE INDEX IF NOT EXISTS idx_weather_archive_location_type ON weather_archive(location_key, data_type);
CREATE INDEX IF NOT EXISTS idx_weather_archive_access_count ON weather_archive(access_count DESC);

-- Create weather_cleanup_log table to track cleanup operations
CREATE TABLE IF NOT EXISTS weather_cleanup_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cleanup_type TEXT NOT NULL, -- 'expired', 'archive', 'manual'
    records_processed INTEGER NOT NULL,
    records_archived INTEGER DEFAULT 0,
    records_deleted INTEGER DEFAULT 0,
    data_size_freed_bytes INTEGER DEFAULT 0,
    cleanup_duration_ms INTEGER,
    cleanup_started_at TEXT NOT NULL,
    cleanup_completed_at TEXT,
    error_message TEXT,
    cleanup_criteria TEXT, -- JSON criteria used for cleanup
    
    -- Constraints
    CHECK (cleanup_type IN ('expired', 'archive', 'manual', 'scheduled')),
    CHECK (records_processed >= 0),
    CHECK (records_archived >= 0),
    CHECK (records_deleted >= 0),
    CHECK (data_size_freed_bytes >= 0),
    CHECK (cleanup_duration_ms >= 0)
);

-- Create indexes for weather_cleanup_log
CREATE INDEX IF NOT EXISTS idx_weather_cleanup_log_type ON weather_cleanup_log(cleanup_type);
CREATE INDEX IF NOT EXISTS idx_weather_cleanup_log_started ON weather_cleanup_log(cleanup_started_at DESC);
CREATE INDEX IF NOT EXISTS idx_weather_cleanup_log_completed ON weather_cleanup_log(cleanup_completed_at DESC);

-- Add new columns to weather_cache for better management
ALTER TABLE weather_cache ADD COLUMN data_size_bytes INTEGER DEFAULT 0;
ALTER TABLE weather_cache ADD COLUMN is_archived BOOLEAN DEFAULT FALSE;
ALTER TABLE weather_cache ADD COLUMN archive_eligible_at TEXT;

-- Create indexes for new weather_cache columns
CREATE INDEX IF NOT EXISTS idx_weather_cache_archived ON weather_cache(is_archived);
CREATE INDEX IF NOT EXISTS idx_weather_cache_archive_eligible ON weather_cache(archive_eligible_at);
CREATE INDEX IF NOT EXISTS idx_weather_cache_data_size ON weather_cache(data_size_bytes DESC);

-- Create trigger to calculate data size on insert/update
CREATE TRIGGER IF NOT EXISTS calculate_weather_cache_size
    AFTER INSERT ON weather_cache
    FOR EACH ROW
BEGIN
    UPDATE weather_cache 
    SET data_size_bytes = length(weather_data),
        archive_eligible_at = datetime(created_at, '+7 days')
    WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_weather_cache_size
    AFTER UPDATE OF weather_data ON weather_cache
    FOR EACH ROW
BEGIN
    UPDATE weather_cache 
    SET data_size_bytes = length(NEW.weather_data)
    WHERE id = NEW.id;
END;

-- Create view for cache statistics
CREATE VIEW IF NOT EXISTS v_weather_cache_detailed_stats AS
SELECT 
    data_type,
    COUNT(*) as total_entries,
    COUNT(CASE WHEN expires_at > datetime('now') THEN 1 END) as active_entries,
    COUNT(CASE WHEN expires_at <= datetime('now') THEN 1 END) as expired_entries,
    COUNT(CASE WHEN is_archived = 1 THEN 1 END) as archived_entries,
    COUNT(CASE WHEN archive_eligible_at <= datetime('now') AND is_archived = 0 THEN 1 END) as archive_eligible,
    SUM(data_size_bytes) as total_size_bytes,
    AVG(data_size_bytes) as avg_size_bytes,
    MAX(data_size_bytes) as max_size_bytes,
    AVG(access_count) as avg_access_count,
    MAX(last_accessed) as last_access_time,
    MIN(created_at) as oldest_entry,
    MAX(created_at) as newest_entry
FROM weather_cache
GROUP BY data_type;

-- Create view for archive statistics
CREATE VIEW IF NOT EXISTS v_weather_archive_stats AS
SELECT 
    data_type,
    COUNT(*) as archived_entries,
    SUM(data_size_bytes) as total_archived_size_bytes,
    AVG(data_size_bytes) as avg_archived_size_bytes,
    AVG(compression_ratio) as avg_compression_ratio,
    SUM(access_count) as total_access_count,
    MIN(original_created_at) as oldest_archived,
    MAX(archived_at) as latest_archived,
    COUNT(DISTINCT location_key) as unique_locations
FROM weather_archive
GROUP BY data_type;

-- Create view for cleanup history
CREATE VIEW IF NOT EXISTS v_weather_cleanup_history AS
SELECT 
    cleanup_type,
    COUNT(*) as cleanup_operations,
    SUM(records_processed) as total_records_processed,
    SUM(records_archived) as total_records_archived,
    SUM(records_deleted) as total_records_deleted,
    SUM(data_size_freed_bytes) as total_data_freed_bytes,
    AVG(cleanup_duration_ms) as avg_cleanup_duration_ms,
    MAX(cleanup_completed_at) as last_cleanup,
    COUNT(CASE WHEN error_message IS NOT NULL THEN 1 END) as failed_cleanups
FROM weather_cleanup_log
WHERE cleanup_completed_at IS NOT NULL
GROUP BY cleanup_type;

-- Create view for locations with most cached data
CREATE VIEW IF NOT EXISTS v_weather_cache_by_location AS
SELECT 
    location_key,
    COUNT(*) as cache_entries,
    COUNT(DISTINCT data_type) as data_types,
    SUM(data_size_bytes) as total_size_bytes,
    AVG(access_count) as avg_access_count,
    MAX(last_accessed) as last_accessed,
    MIN(created_at) as first_cached,
    MAX(created_at) as last_cached,
    COUNT(CASE WHEN expires_at > datetime('now') THEN 1 END) as active_entries,
    COUNT(CASE WHEN is_archived = 1 THEN 1 END) as archived_entries
FROM weather_cache
GROUP BY location_key
ORDER BY total_size_bytes DESC;

-- Create view for cache efficiency analysis
CREATE VIEW IF NOT EXISTS v_weather_cache_efficiency AS
SELECT 
    cache_key,
    location_key,
    data_type,
    access_count,
    data_size_bytes,
    CASE 
        WHEN access_count = 0 THEN 0
        ELSE CAST(access_count AS REAL) / data_size_bytes * 1000
    END as efficiency_score, -- accesses per KB
    julianday('now') - julianday(created_at) as age_days,
    julianday('now') - julianday(last_accessed) as days_since_access,
    expires_at,
    is_archived,
    archive_eligible_at
FROM weather_cache
ORDER BY efficiency_score DESC;

-- Create indexes for better performance on views
CREATE INDEX IF NOT EXISTS idx_weather_cache_efficiency ON weather_cache(access_count, data_size_bytes);
CREATE INDEX IF NOT EXISTS idx_weather_cache_age ON weather_cache(created_at, last_accessed);

-- Update existing data to calculate sizes
UPDATE weather_cache 
SET data_size_bytes = length(weather_data),
    archive_eligible_at = datetime(created_at, '+7 days')
WHERE data_size_bytes = 0 OR data_size_bytes IS NULL;

-- Create function-like view for getting archival candidates
CREATE VIEW IF NOT EXISTS v_weather_archival_candidates AS
SELECT 
    id,
    cache_key,
    location_key,
    data_type,
    data_size_bytes,
    access_count,
    created_at,
    last_accessed,
    archive_eligible_at,
    julianday('now') - julianday(COALESCE(last_accessed, created_at)) as days_since_access,
    CASE 
        WHEN access_count = 0 THEN 'never_accessed'
        WHEN julianday('now') - julianday(last_accessed) > 30 THEN 'stale'
        WHEN archive_eligible_at <= datetime('now') THEN 'eligible'
        ELSE 'active'
    END as archival_reason
FROM weather_cache
WHERE is_archived = 0
    AND (
        archive_eligible_at <= datetime('now')
        OR access_count = 0
        OR julianday('now') - julianday(COALESCE(last_accessed, created_at)) > 30
    )
ORDER BY 
    CASE archival_reason
        WHEN 'never_accessed' THEN 1
        WHEN 'stale' THEN 2
        WHEN 'eligible' THEN 3
        ELSE 4
    END,
    days_since_access DESC;

-- Insert migration record
INSERT INTO migration_history (version, name, checksum, applied_at, execution_time_ms)
VALUES (3, 'weather_data_archival', 'weather_archival_checksum_v3', datetime('now'), 0);