"""Database models for SQLite storage."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class FavoriteLocationModel:
    """Model for favorite weather locations."""

    id: Optional[int] = None
    name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    country: str = ""
    state: Optional[str] = None
    timezone: Optional[str] = None
    is_default: bool = False
    display_order: int = 0
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for database storage."""
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "country": self.country,
            "state": self.state,
            "timezone": self.timezone,
            "is_default": self.is_default,
            "display_order": self.display_order,
            "tags": json.dumps(self.tags) if self.tags else "[]",
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "access_count": self.access_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FavoriteLocationModel":
        """Create model from dictionary."""
        return cls(
            id=data.get("id"),
            name=data.get("name", ""),
            latitude=data.get("latitude", 0.0),
            longitude=data.get("longitude", 0.0),
            country=data.get("country", ""),
            state=data.get("state"),
            timezone=data.get("timezone"),
            is_default=bool(data.get("is_default", False)),
            display_order=data.get("display_order", 0),
            tags=json.loads(data.get("tags", "[]")) if data.get("tags") else [],
            notes=data.get("notes"),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else None
            ),
            last_accessed=(
                datetime.fromisoformat(data["last_accessed"])
                if data.get("last_accessed")
                else None
            ),
            access_count=data.get("access_count", 0),
        )


@dataclass
class JournalEntryModel:
    """Model for weather journal entries."""

    id: Optional[int] = None
    title: str = ""
    content: str = ""
    entry_type: str = "personal"  # personal, weather_observation, activity, mood
    weather_data: Optional[Dict[str, Any]] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    mood: Optional[str] = None
    activities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    is_favorite: bool = False
    is_private: bool = False
    template_id: Optional[str] = None
    attachments: List[str] = field(default_factory=list)  # File paths or URLs
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    entry_date: Optional[datetime] = None  # Date the entry refers to

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for database storage."""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "entry_type": self.entry_type,
            "weather_data": (
                json.dumps(self.weather_data) if self.weather_data else None
            ),
            "location_name": self.location_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "mood": self.mood,
            "activities": json.dumps(self.activities) if self.activities else "[]",
            "tags": json.dumps(self.tags) if self.tags else "[]",
            "is_favorite": self.is_favorite,
            "is_private": self.is_private,
            "template_id": self.template_id,
            "attachments": json.dumps(self.attachments) if self.attachments else "[]",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "entry_date": self.entry_date.isoformat() if self.entry_date else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JournalEntryModel":
        """Create model from dictionary."""
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            content=data.get("content", ""),
            entry_type=data.get("entry_type", "personal"),
            weather_data=(
                json.loads(data["weather_data"]) if data.get("weather_data") else None
            ),
            location_name=data.get("location_name"),
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            mood=data.get("mood"),
            activities=(
                json.loads(data.get("activities", "[]"))
                if data.get("activities")
                else []
            ),
            tags=json.loads(data.get("tags", "[]")) if data.get("tags") else [],
            is_favorite=bool(data.get("is_favorite", False)),
            is_private=bool(data.get("is_private", False)),
            template_id=data.get("template_id"),
            attachments=(
                json.loads(data.get("attachments", "[]"))
                if data.get("attachments")
                else []
            ),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else None
            ),
            entry_date=(
                datetime.fromisoformat(data["entry_date"])
                if data.get("entry_date")
                else None
            ),
        )


@dataclass
class SettingsModel:
    """Model for application settings."""

    id: Optional[int] = None
    key: str = ""
    value: Any = None
    category: str = "general"  # general, weather, ui, notifications, etc.
    data_type: str = "string"  # string, int, float, bool, json
    description: Optional[str] = None
    is_user_configurable: bool = True
    is_encrypted: bool = False
    default_value: Any = None
    validation_rules: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for database storage."""
        # Handle value serialization based on data type
        if self.data_type == "json" and self.value is not None:
            serialized_value = json.dumps(self.value)
        elif self.value is not None:
            serialized_value = str(self.value)
        else:
            serialized_value = None

        # Handle default value serialization
        if self.data_type == "json" and self.default_value is not None:
            serialized_default = json.dumps(self.default_value)
        elif self.default_value is not None:
            serialized_default = str(self.default_value)
        else:
            serialized_default = None

        return {
            "id": self.id,
            "key": self.key,
            "value": serialized_value,
            "category": self.category,
            "data_type": self.data_type,
            "description": self.description,
            "is_user_configurable": self.is_user_configurable,
            "is_encrypted": self.is_encrypted,
            "default_value": serialized_default,
            "validation_rules": (
                json.dumps(self.validation_rules) if self.validation_rules else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SettingsModel":
        """Create model from dictionary."""
        # Deserialize value based on data type
        raw_value = data.get("value")
        data_type = data.get("data_type", "string")

        if raw_value is None:
            value = None
        elif data_type == "int":
            value = int(raw_value)
        elif data_type == "float":
            value = float(raw_value)
        elif data_type == "bool":
            value = (
                raw_value.lower() in ("true", "1", "yes", "on")
                if isinstance(raw_value, str)
                else bool(raw_value)
            )
        elif data_type == "json":
            value = json.loads(raw_value)
        else:
            value = raw_value

        # Deserialize default value
        raw_default = data.get("default_value")
        if raw_default is None:
            default_value = None
        elif data_type == "int":
            default_value = int(raw_default)
        elif data_type == "float":
            default_value = float(raw_default)
        elif data_type == "bool":
            default_value = (
                raw_default.lower() in ("true", "1", "yes", "on")
                if isinstance(raw_default, str)
                else bool(raw_default)
            )
        elif data_type == "json":
            default_value = json.loads(raw_default)
        else:
            default_value = raw_default

        return cls(
            id=data.get("id"),
            key=data.get("key", ""),
            value=value,
            category=data.get("category", "general"),
            data_type=data_type,
            description=data.get("description"),
            is_user_configurable=bool(data.get("is_user_configurable", True)),
            is_encrypted=bool(data.get("is_encrypted", False)),
            default_value=default_value,
            validation_rules=(
                json.loads(data["validation_rules"])
                if data.get("validation_rules")
                else None
            ),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else None
            ),
        )


@dataclass
class WeatherCacheModel:
    """Model for cached weather data."""

    id: Optional[int] = None
    cache_key: str = ""
    location_key: str = ""  # lat,lon or location identifier
    data_type: str = "current"  # current, forecast, historical, alerts
    weather_data: Dict[str, Any] = field(default_factory=dict)
    provider: str = "openweather"  # openweather, weatherapi, etc.
    quality_score: float = 1.0  # Data quality/confidence score
    request_params: Optional[Dict[str, Any]] = None
    response_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None
    access_count: int = 0
    is_stale: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for database storage."""
        return {
            "id": self.id,
            "cache_key": self.cache_key,
            "location_key": self.location_key,
            "data_type": self.data_type,
            "weather_data": (
                json.dumps(self.weather_data) if self.weather_data else "{}"
            ),
            "provider": self.provider,
            "quality_score": self.quality_score,
            "request_params": (
                json.dumps(self.request_params) if self.request_params else None
            ),
            "response_metadata": (
                json.dumps(self.response_metadata) if self.response_metadata else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "last_accessed": (
                self.last_accessed.isoformat() if self.last_accessed else None
            ),
            "access_count": self.access_count,
            "is_stale": self.is_stale,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WeatherCacheModel":
        """Create model from dictionary."""
        return cls(
            id=data.get("id"),
            cache_key=data.get("cache_key", ""),
            location_key=data.get("location_key", ""),
            data_type=data.get("data_type", "current"),
            weather_data=(
                json.loads(data.get("weather_data", "{}"))
                if data.get("weather_data")
                else {}
            ),
            provider=data.get("provider", "openweather"),
            quality_score=data.get("quality_score", 1.0),
            request_params=(
                json.loads(data["request_params"])
                if data.get("request_params")
                else None
            ),
            response_metadata=(
                json.loads(data["response_metadata"])
                if data.get("response_metadata")
                else None
            ),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
            last_accessed=(
                datetime.fromisoformat(data["last_accessed"])
                if data.get("last_accessed")
                else None
            ),
            access_count=data.get("access_count", 0),
            is_stale=bool(data.get("is_stale", False)),
        )


@dataclass
class UserPreferencesModel:
    """Model for user preferences and profile data."""

    id: Optional[int] = None
    user_id: str = "default"  # Support for multiple users in future
    display_name: Optional[str] = None
    email: Optional[str] = None
    preferred_units: str = "metric"  # metric, imperial
    preferred_language: str = "en"
    timezone: str = "UTC"
    default_location_id: Optional[int] = None
    theme: str = "auto"  # light, dark, auto
    notifications_enabled: bool = True
    weather_alerts_enabled: bool = True
    privacy_level: str = "normal"  # minimal, normal, full
    data_retention_days: int = 365
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for database storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "display_name": self.display_name,
            "email": self.email,
            "preferred_units": self.preferred_units,
            "preferred_language": self.preferred_language,
            "timezone": self.timezone,
            "default_location_id": self.default_location_id,
            "theme": self.theme,
            "notifications_enabled": self.notifications_enabled,
            "weather_alerts_enabled": self.weather_alerts_enabled,
            "privacy_level": self.privacy_level,
            "data_retention_days": self.data_retention_days,
            "preferences": json.dumps(self.preferences) if self.preferences else "{}",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferencesModel":
        """Create model from dictionary."""
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id", "default"),
            display_name=data.get("display_name"),
            email=data.get("email"),
            preferred_units=data.get("preferred_units", "metric"),
            preferred_language=data.get("preferred_language", "en"),
            timezone=data.get("timezone", "UTC"),
            default_location_id=data.get("default_location_id"),
            theme=data.get("theme", "auto"),
            notifications_enabled=bool(data.get("notifications_enabled", True)),
            weather_alerts_enabled=bool(data.get("weather_alerts_enabled", True)),
            privacy_level=data.get("privacy_level", "normal"),
            data_retention_days=data.get("data_retention_days", 365),
            preferences=(
                json.loads(data.get("preferences", "{}"))
                if data.get("preferences")
                else {}
            ),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if data.get("updated_at")
                else None
            ),
            last_login=(
                datetime.fromisoformat(data["last_login"])
                if data.get("last_login")
                else None
            ),
        )


@dataclass
class ActivityLogModel:
    """Model for user activity logging."""

    id: Optional[int] = None
    user_id: str = "default"
    action: str = ""  # view_weather, add_favorite, create_journal, etc.
    resource_type: str = ""  # location, journal_entry, setting, etc.
    resource_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    duration_ms: Optional[int] = None
    success: bool = True
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for database storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": json.dumps(self.details) if self.details else None,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActivityLogModel":
        """Create model from dictionary."""
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id", "default"),
            action=data.get("action", ""),
            resource_type=data.get("resource_type", ""),
            resource_id=data.get("resource_id"),
            details=json.loads(data["details"]) if data.get("details") else None,
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            session_id=data.get("session_id"),
            duration_ms=data.get("duration_ms"),
            success=bool(data.get("success", True)),
            error_message=data.get("error_message"),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else None
            ),
        )
