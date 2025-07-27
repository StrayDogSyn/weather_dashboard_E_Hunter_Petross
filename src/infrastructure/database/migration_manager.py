"""Database migration manager for schema versioning and updates."""

import hashlib
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...shared.exceptions import DatabaseError
from .connection_manager import DatabaseConnectionManager

logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration."""

    def __init__(self, version: str, name: str, up_sql: str, down_sql: str = ""):
        self.version = version
        self.name = name
        self.up_sql = up_sql
        self.down_sql = down_sql
        self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum for migration integrity."""
        content = f"{self.version}{self.name}{self.up_sql}{self.down_sql}"
        return hashlib.sha256(content.encode()).hexdigest()

    def __str__(self) -> str:
        return f"Migration {self.version}: {self.name}"


class MigrationManager:
    """Manages database schema migrations."""

    def __init__(
        self,
        db_manager: DatabaseConnectionManager,
        migrations_dir: Optional[Path] = None,
    ):
        self.db_manager = db_manager
        self.migrations_dir = migrations_dir or Path(__file__).parent / "migrations"
        self.migrations: List[Migration] = []
        self._load_built_in_migrations()

    def _load_built_in_migrations(self) -> None:
        """Load built-in migrations."""
        # Migration 001: Initial schema
        migration_001 = Migration(
            version="001",
            name="initial_schema",
            up_sql="""
            -- Create migration tracking table
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                checksum TEXT NOT NULL,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                execution_time_ms INTEGER
            );

            -- Create favorite locations table
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
                tags TEXT DEFAULT '[]',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0
            );

            -- Create journal entries table
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                entry_type TEXT DEFAULT 'personal',
                weather_data TEXT,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                mood TEXT,
                activities TEXT DEFAULT '[]',
                tags TEXT DEFAULT '[]',
                is_favorite BOOLEAN DEFAULT FALSE,
                is_private BOOLEAN DEFAULT FALSE,
                template_id TEXT,
                attachments TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                entry_date TIMESTAMP
            );

            -- Create settings table
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                category TEXT DEFAULT 'general',
                data_type TEXT DEFAULT 'string',
                description TEXT,
                is_user_configurable BOOLEAN DEFAULT TRUE,
                is_encrypted BOOLEAN DEFAULT FALSE,
                default_value TEXT,
                validation_rules TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Create weather cache table
            CREATE TABLE IF NOT EXISTS weather_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                location_key TEXT NOT NULL,
                data_type TEXT DEFAULT 'current',
                weather_data TEXT NOT NULL DEFAULT '{}',
                provider TEXT DEFAULT 'openweather',
                quality_score REAL DEFAULT 1.0,
                request_params TEXT,
                response_metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                is_stale BOOLEAN DEFAULT FALSE
            );

            -- Create user preferences table
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL DEFAULT 'default',
                display_name TEXT,
                email TEXT,
                preferred_units TEXT DEFAULT 'metric',
                preferred_language TEXT DEFAULT 'en',
                timezone TEXT DEFAULT 'UTC',
                default_location_id INTEGER,
                theme TEXT DEFAULT 'auto',
                notifications_enabled BOOLEAN DEFAULT TRUE,
                weather_alerts_enabled BOOLEAN DEFAULT TRUE,
                privacy_level TEXT DEFAULT 'normal',
                data_retention_days INTEGER DEFAULT 365,
                preferences TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                FOREIGN KEY (default_location_id) REFERENCES favorite_locations(id)
            );

            -- Create activity log table
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'default',
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT,
                details TEXT,
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                duration_ms INTEGER,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Create indexes for better performance
            CREATE INDEX IF NOT EXISTS idx_favorite_locations_coords ON favorite_locations(latitude, longitude);
            CREATE INDEX IF NOT EXISTS idx_favorite_locations_default ON favorite_locations(is_default);
            CREATE INDEX IF NOT EXISTS idx_favorite_locations_order ON favorite_locations(display_order);

            CREATE INDEX IF NOT EXISTS idx_journal_entries_date ON journal_entries(entry_date);
            CREATE INDEX IF NOT EXISTS idx_journal_entries_type ON journal_entries(entry_type);
            CREATE INDEX IF NOT EXISTS idx_journal_entries_location ON journal_entries(latitude, longitude);
            CREATE INDEX IF NOT EXISTS idx_journal_entries_favorite ON journal_entries(is_favorite);
            CREATE INDEX IF NOT EXISTS idx_journal_entries_created ON journal_entries(created_at);

            CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category);
            CREATE INDEX IF NOT EXISTS idx_settings_configurable ON settings(is_user_configurable);

            CREATE INDEX IF NOT EXISTS idx_weather_cache_location ON weather_cache(location_key);
            CREATE INDEX IF NOT EXISTS idx_weather_cache_type ON weather_cache(data_type);
            CREATE INDEX IF NOT EXISTS idx_weather_cache_expires ON weather_cache(expires_at);
            CREATE INDEX IF NOT EXISTS idx_weather_cache_stale ON weather_cache(is_stale);

            CREATE INDEX IF NOT EXISTS idx_activity_log_user ON activity_log(user_id);
            CREATE INDEX IF NOT EXISTS idx_activity_log_action ON activity_log(action);
            CREATE INDEX IF NOT EXISTS idx_activity_log_resource ON activity_log(resource_type, resource_id);
            CREATE INDEX IF NOT EXISTS idx_activity_log_created ON activity_log(created_at);

            -- Create triggers for updated_at timestamps
            CREATE TRIGGER IF NOT EXISTS update_favorite_locations_timestamp
                AFTER UPDATE ON favorite_locations
                BEGIN
                    UPDATE favorite_locations SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;

            CREATE TRIGGER IF NOT EXISTS update_journal_entries_timestamp
                AFTER UPDATE ON journal_entries
                BEGIN
                    UPDATE journal_entries SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;

            CREATE TRIGGER IF NOT EXISTS update_settings_timestamp
                AFTER UPDATE ON settings
                BEGIN
                    UPDATE settings SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;

            CREATE TRIGGER IF NOT EXISTS update_user_preferences_timestamp
                AFTER UPDATE ON user_preferences
                BEGIN
                    UPDATE user_preferences SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
                END;
            """,
            down_sql="""
            -- Drop all tables and indexes
            DROP TRIGGER IF EXISTS update_user_preferences_timestamp;
            DROP TRIGGER IF EXISTS update_settings_timestamp;
            DROP TRIGGER IF EXISTS update_journal_entries_timestamp;
            DROP TRIGGER IF EXISTS update_favorite_locations_timestamp;

            DROP INDEX IF EXISTS idx_activity_log_created;
            DROP INDEX IF EXISTS idx_activity_log_resource;
            DROP INDEX IF EXISTS idx_activity_log_action;
            DROP INDEX IF EXISTS idx_activity_log_user;
            DROP INDEX IF EXISTS idx_weather_cache_stale;
            DROP INDEX IF EXISTS idx_weather_cache_expires;
            DROP INDEX IF EXISTS idx_weather_cache_type;
            DROP INDEX IF EXISTS idx_weather_cache_location;
            DROP INDEX IF EXISTS idx_settings_configurable;
            DROP INDEX IF EXISTS idx_settings_category;
            DROP INDEX IF EXISTS idx_journal_entries_created;
            DROP INDEX IF EXISTS idx_journal_entries_favorite;
            DROP INDEX IF EXISTS idx_journal_entries_location;
            DROP INDEX IF EXISTS idx_journal_entries_type;
            DROP INDEX IF EXISTS idx_journal_entries_date;
            DROP INDEX IF EXISTS idx_favorite_locations_order;
            DROP INDEX IF EXISTS idx_favorite_locations_default;
            DROP INDEX IF EXISTS idx_favorite_locations_coords;

            DROP TABLE IF EXISTS activity_log;
            DROP TABLE IF EXISTS user_preferences;
            DROP TABLE IF EXISTS weather_cache;
            DROP TABLE IF EXISTS settings;
            DROP TABLE IF EXISTS journal_entries;
            DROP TABLE IF EXISTS favorite_locations;
            DROP TABLE IF EXISTS schema_migrations;
            """,
        )

        # Migration 002: Add full-text search for journal entries
        migration_002 = Migration(
            version="002",
            name="add_journal_fts",
            up_sql="""
            -- Create FTS virtual table for journal entries
            CREATE VIRTUAL TABLE IF NOT EXISTS journal_entries_fts USING fts5(
                title, content, tags,
                content='journal_entries',
                content_rowid='id'
            );

            -- Populate FTS table with existing data
            INSERT INTO journal_entries_fts(rowid, title, content, tags)
            SELECT id, title, content, tags FROM journal_entries;

            -- Create triggers to keep FTS table in sync
            CREATE TRIGGER IF NOT EXISTS journal_entries_fts_insert
                AFTER INSERT ON journal_entries
                BEGIN
                    INSERT INTO journal_entries_fts(rowid, title, content, tags)
                    VALUES (NEW.id, NEW.title, NEW.content, NEW.tags);
                END;

            CREATE TRIGGER IF NOT EXISTS journal_entries_fts_update
                AFTER UPDATE ON journal_entries
                BEGIN
                    UPDATE journal_entries_fts
                    SET title = NEW.title, content = NEW.content, tags = NEW.tags
                    WHERE rowid = NEW.id;
                END;

            CREATE TRIGGER IF NOT EXISTS journal_entries_fts_delete
                AFTER DELETE ON journal_entries
                BEGIN
                    DELETE FROM journal_entries_fts WHERE rowid = OLD.id;
                END;
            """,
            down_sql="""
            DROP TRIGGER IF EXISTS journal_entries_fts_delete;
            DROP TRIGGER IF EXISTS journal_entries_fts_update;
            DROP TRIGGER IF EXISTS journal_entries_fts_insert;
            DROP TABLE IF EXISTS journal_entries_fts;
            """,
        )

        # Migration 003: Add weather data archival
        migration_003 = Migration(
            version="003",
            name="add_weather_archive",
            up_sql="""
            -- Create weather archive table for historical data
            CREATE TABLE IF NOT EXISTS weather_archive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location_key TEXT NOT NULL,
                weather_data TEXT NOT NULL,
                data_type TEXT DEFAULT 'historical',
                provider TEXT DEFAULT 'openweather',
                recorded_at TIMESTAMP NOT NULL,
                archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                quality_score REAL DEFAULT 1.0,
                source_cache_id INTEGER,
                FOREIGN KEY (source_cache_id) REFERENCES weather_cache(id)
            );

            CREATE INDEX IF NOT EXISTS idx_weather_archive_location ON weather_archive(location_key);
            CREATE INDEX IF NOT EXISTS idx_weather_archive_recorded ON weather_archive(recorded_at);
            CREATE INDEX IF NOT EXISTS idx_weather_archive_archived ON weather_archive(archived_at);

            -- Add archival flag to weather_cache
            ALTER TABLE weather_cache ADD COLUMN is_archived BOOLEAN DEFAULT FALSE;
            CREATE INDEX IF NOT EXISTS idx_weather_cache_archived ON weather_cache(is_archived);
            """,
            down_sql="""
            DROP INDEX IF EXISTS idx_weather_cache_archived;
            -- Note: SQLite doesn't support DROP COLUMN, so we leave the column
            DROP INDEX IF EXISTS idx_weather_archive_archived;
            DROP INDEX IF EXISTS idx_weather_archive_recorded;
            DROP INDEX IF EXISTS idx_weather_archive_location;
            DROP TABLE IF EXISTS weather_archive;
            """,
        )

        self.migrations = [migration_001, migration_002, migration_003]

    async def load_file_migrations(self) -> None:
        """Load migrations from files in the migrations directory."""
        if not self.migrations_dir.exists():
            logger.info(f"Migrations directory not found: {self.migrations_dir}")
            return

        migration_files = sorted(self.migrations_dir.glob("*.sql"))

        for file_path in migration_files:
            try:
                # Parse filename: 004_add_feature.sql
                filename = file_path.stem
                parts = filename.split("_", 1)

                if len(parts) != 2:
                    logger.warning(
                        f"Skipping migration file with invalid name: {filename}"
                    )
                    continue

                version, name = parts

                # Read migration content
                content = file_path.read_text(encoding="utf-8")

                # Split up and down migrations (if present)
                if "-- DOWN" in content:
                    up_sql, down_sql = content.split("-- DOWN", 1)
                    up_sql = up_sql.replace("-- UP", "").strip()
                    down_sql = down_sql.strip()
                else:
                    up_sql = content.replace("-- UP", "").strip()
                    down_sql = ""

                migration = Migration(version, name, up_sql, down_sql)

                # Check if migration already exists
                existing = next(
                    (m for m in self.migrations if m.version == version), None
                )
                if existing:
                    logger.warning(
                        f"Migration {version} already exists, skipping file: {filename}"
                    )
                    continue

                self.migrations.append(migration)
                logger.info(f"Loaded migration from file: {filename}")

            except Exception as e:
                logger.error(f"Failed to load migration file {file_path}: {e}")

        # Sort migrations by version
        self.migrations.sort(key=lambda m: m.version)

    async def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """Get list of applied migrations from database."""
        try:
            async with self.db_manager.get_connection() as conn:
                # Check if migrations table exists
                cursor = await conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
                )
                table_exists = await cursor.fetchone()

                if not table_exists:
                    return []

                cursor = await conn.execute(
                    "SELECT version, name, checksum, applied_at, execution_time_ms FROM schema_migrations ORDER BY version"
                )
                rows = await cursor.fetchall()

                return [
                    {
                        "version": row[0],
                        "name": row[1],
                        "checksum": row[2],
                        "applied_at": row[3],
                        "execution_time_ms": row[4],
                    }
                    for row in rows
                ]

        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            raise DatabaseError(f"Failed to get applied migrations: {e}")

    async def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        applied = await self.get_applied_migrations()
        applied_versions = {m["version"] for m in applied}

        pending = [m for m in self.migrations if m.version not in applied_versions]
        return sorted(pending, key=lambda m: m.version)

    async def apply_migration(self, migration: Migration) -> None:
        """Apply a single migration."""
        start_time = datetime.now()

        try:
            async with self.db_manager.get_transaction() as conn:
                # Execute migration SQL
                await conn.executescript(migration.up_sql)

                # Record migration in tracking table
                execution_time = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )

                await conn.execute(
                    """
                    INSERT INTO schema_migrations (version, name, checksum, applied_at, execution_time_ms)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        migration.version,
                        migration.name,
                        migration.checksum,
                        datetime.now().isoformat(),
                        execution_time,
                    ),
                )

                await conn.commit()

                logger.info(f"Applied migration {migration} in {execution_time}ms")

        except Exception as e:
            logger.error(f"Failed to apply migration {migration}: {e}")
            raise DatabaseError(f"Migration {migration.version} failed: {e}")

    async def rollback_migration(self, migration: Migration) -> None:
        """Rollback a single migration."""
        if not migration.down_sql:
            raise DatabaseError(f"Migration {migration.version} has no rollback SQL")

        try:
            async with self.db_manager.get_transaction() as conn:
                # Execute rollback SQL
                await conn.executescript(migration.down_sql)

                # Remove migration from tracking table
                await conn.execute(
                    "DELETE FROM schema_migrations WHERE version = ?",
                    (migration.version,),
                )

                await conn.commit()

                logger.info(f"Rolled back migration {migration}")

        except Exception as e:
            logger.error(f"Failed to rollback migration {migration}: {e}")
            raise DatabaseError(
                f"Rollback of migration {migration.version} failed: {e}"
            )

    async def migrate_up(self, target_version: Optional[str] = None) -> int:
        """Apply all pending migrations up to target version."""
        await self.load_file_migrations()

        pending = await self.get_pending_migrations()

        if target_version:
            pending = [m for m in pending if m.version <= target_version]

        if not pending:
            logger.info("No pending migrations to apply")
            return 0

        applied_count = 0
        for migration in pending:
            await self.apply_migration(migration)
            applied_count += 1

        logger.info(f"Applied {applied_count} migrations")
        return applied_count

    async def migrate_down(self, target_version: str) -> int:
        """Rollback migrations down to target version."""
        applied = await self.get_applied_migrations()

        # Find migrations to rollback (in reverse order)
        to_rollback = [m for m in applied if m["version"] > target_version]
        to_rollback.sort(key=lambda m: m["version"], reverse=True)

        if not to_rollback:
            logger.info(f"No migrations to rollback to version {target_version}")
            return 0

        rollback_count = 0
        for migration_info in to_rollback:
            # Find the migration object
            migration = next(
                (m for m in self.migrations if m.version == migration_info["version"]),
                None,
            )

            if not migration:
                logger.error(
                    f"Migration {migration_info['version']} not found for rollback"
                )
                continue

            await self.rollback_migration(migration)
            rollback_count += 1

        logger.info(f"Rolled back {rollback_count} migrations")
        return rollback_count

    async def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        await self.load_file_migrations()

        applied = await self.get_applied_migrations()
        pending = await self.get_pending_migrations()

        return {
            "total_migrations": len(self.migrations),
            "applied_count": len(applied),
            "pending_count": len(pending),
            "current_version": applied[-1]["version"] if applied else None,
            "latest_version": self.migrations[-1].version if self.migrations else None,
            "applied_migrations": applied,
            "pending_migrations": [
                {"version": m.version, "name": m.name} for m in pending
            ],
        }

    async def validate_migrations(self) -> List[str]:
        """Validate migration integrity."""
        issues = []
        applied = await self.get_applied_migrations()

        for applied_migration in applied:
            version = applied_migration["version"]
            stored_checksum = applied_migration["checksum"]

            # Find corresponding migration
            migration = next((m for m in self.migrations if m.version == version), None)

            if not migration:
                issues.append(
                    f"Applied migration {version} not found in available migrations"
                )
                continue

            if migration.checksum != stored_checksum:
                issues.append(
                    f"Migration {version} checksum mismatch - migration may have been modified"
                )

        return issues

    async def create_migration_file(
        self, name: str, up_sql: str, down_sql: str = ""
    ) -> Path:
        """Create a new migration file."""
        # Generate next version number
        existing_versions = [
            int(m.version) for m in self.migrations if m.version.isdigit()
        ]
        next_version = str(max(existing_versions, default=0) + 1).zfill(3)

        filename = f"{next_version}_{name}.sql"
        file_path = self.migrations_dir / filename

        # Ensure migrations directory exists
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        # Create migration file content
        content = f"-- UP\n{up_sql}\n"
        if down_sql:
            content += f"\n-- DOWN\n{down_sql}\n"

        file_path.write_text(content, encoding="utf-8")

        logger.info(f"Created migration file: {filename}")
        return file_path
