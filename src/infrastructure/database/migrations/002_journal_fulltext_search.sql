-- Migration: 002_journal_fulltext_search
-- Description: Add full-text search capabilities to journal entries
-- Version: 2
-- Created: 2024-01-02

-- Enable FTS5 extension (if available)
-- Note: FTS5 provides better performance and features than FTS4

-- Create FTS5 virtual table for journal entries
CREATE VIRTUAL TABLE IF NOT EXISTS journal_entries_fts USING fts5(
    title,
    content,
    tags,
    location_name,
    content=journal_entries,
    content_rowid=id
);

-- Create triggers to keep FTS table in sync with journal_entries
CREATE TRIGGER IF NOT EXISTS journal_entries_fts_insert 
    AFTER INSERT ON journal_entries
BEGIN
    INSERT INTO journal_entries_fts(rowid, title, content, tags, location_name)
    VALUES (NEW.id, NEW.title, NEW.content, NEW.tags, NEW.location_name);
END;

CREATE TRIGGER IF NOT EXISTS journal_entries_fts_delete 
    AFTER DELETE ON journal_entries
BEGIN
    INSERT INTO journal_entries_fts(journal_entries_fts, rowid, title, content, tags, location_name)
    VALUES ('delete', OLD.id, OLD.title, OLD.content, OLD.tags, OLD.location_name);
END;

CREATE TRIGGER IF NOT EXISTS journal_entries_fts_update 
    AFTER UPDATE ON journal_entries
BEGIN
    INSERT INTO journal_entries_fts(journal_entries_fts, rowid, title, content, tags, location_name)
    VALUES ('delete', OLD.id, OLD.title, OLD.content, OLD.tags, OLD.location_name);
    INSERT INTO journal_entries_fts(rowid, title, content, tags, location_name)
    VALUES (NEW.id, NEW.title, NEW.content, NEW.tags, NEW.location_name);
END;

-- Populate FTS table with existing data
INSERT INTO journal_entries_fts(rowid, title, content, tags, location_name)
SELECT id, title, content, tags, location_name FROM journal_entries;

-- Create additional indexes for better search performance
CREATE INDEX IF NOT EXISTS idx_journal_entries_content_length ON journal_entries(length(content));
CREATE INDEX IF NOT EXISTS idx_journal_entries_title_length ON journal_entries(length(title));

-- Create view for search results with ranking
CREATE VIEW IF NOT EXISTS v_journal_search_results AS
SELECT 
    je.id,
    je.title,
    je.content,
    je.entry_type,
    je.weather_mood,
    je.location_name,
    je.latitude,
    je.longitude,
    je.tags,
    je.is_favorite,
    je.is_private,
    je.created_at,
    je.updated_at,
    je.weather_date,
    fts.rank
FROM journal_entries je
JOIN journal_entries_fts fts ON je.id = fts.rowid;

-- Create stored procedure equivalent (using view) for common search patterns
CREATE VIEW IF NOT EXISTS v_journal_recent_by_mood AS
SELECT 
    weather_mood,
    COUNT(*) as entry_count,
    MAX(created_at) as latest_entry,
    AVG(length(content)) as avg_content_length
FROM journal_entries
WHERE weather_mood IS NOT NULL
    AND created_at >= date('now', '-30 days')
GROUP BY weather_mood
ORDER BY entry_count DESC;

-- Create view for location-based journal statistics
CREATE VIEW IF NOT EXISTS v_journal_location_stats AS
SELECT 
    location_name,
    COUNT(*) as entry_count,
    COUNT(DISTINCT weather_mood) as mood_variety,
    MIN(created_at) as first_entry,
    MAX(created_at) as latest_entry,
    AVG(length(content)) as avg_content_length
FROM journal_entries
WHERE location_name IS NOT NULL
GROUP BY location_name
HAVING entry_count > 1
ORDER BY entry_count DESC;

-- Create view for tag analysis
CREATE VIEW IF NOT EXISTS v_journal_tag_analysis AS
SELECT 
    json_each.value as tag,
    COUNT(*) as usage_count,
    COUNT(DISTINCT entry_type) as entry_type_variety,
    MAX(created_at) as last_used
FROM journal_entries, json_each(journal_entries.tags)
WHERE json_valid(journal_entries.tags)
GROUP BY json_each.value
HAVING usage_count > 1
ORDER BY usage_count DESC;

-- Add search optimization settings
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = memory;

-- Insert migration record
INSERT INTO migration_history (version, name, checksum, applied_at, execution_time_ms)
VALUES (2, 'journal_fulltext_search', 'journal_fts_checksum_v2', datetime('now'), 0);