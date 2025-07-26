"""Enhanced Database Models for Weather Dashboard.

This module provides enhanced SQLAlchemy ORM models with design patterns,
AI integration, and advanced functionality for persistent data storage.

Enhancements:
- Repository pattern for data access
- Factory pattern for model creation
- AI-enhanced data analysis
- Advanced querying and analytics
- Data validation and integrity
- Audit trail and metadata tracking
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
    event,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.sql import func

# Database configuration
DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "weather_dashboard.db"
DATABASE_URL = "sqlite:///" + str(DATABASE_PATH)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Enhanced protocols and base classes
class DatabaseRepository(Protocol):
    """Protocol for database repository pattern."""

    def create(self, **kwargs) -> Any:
        """Create a new record."""
        ...

    def get_by_id(self, id: Union[int, str]) -> Optional[Any]:
        """Get record by ID."""
        ...

    def update(self, id: Union[int, str], **kwargs) -> Optional[Any]:
        """Update record by ID."""
        ...

    def delete(self, id: Union[int, str]) -> bool:
        """Delete record by ID."""
        ...

    def list_all(self, **filters) -> List[Any]:
        """List all records with optional filters."""
        ...


class AuditMixin:
    """Mixin for audit trail functionality."""

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_by = Column(String, default="system")
    updated_by = Column(String, default="system")
    version = Column(Integer, default=1)

    def update_audit_fields(self, user: str = "system"):
        """Update audit fields."""
        self.updated_at = datetime.now(timezone.utc)
        self.updated_by = user
        self.version += 1


class AIEnhancedMixin:
    """Mixin for AI-enhanced database models (not abstract to avoid metaclass conflicts)."""

    def generate_ai_insights(self, gemini_api_key: str) -> Dict[str, Any]:
        """Generate AI insights for this model. Override in subclasses."""
        return {"error": "AI insights not implemented for this model"}

    def _call_gemini_api(self, prompt: str, api_key: str) -> Optional[str]:
        """Call Gemini API for insights."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            return response.text.strip() if response.text else None
        except Exception as e:
            logging.warning(f"Gemini API call failed: {e}")
            return None


class UserPreferences(Base, AuditMixin, AIEnhancedMixin):  # type: ignore[misc,valid-type]
    """Enhanced user preferences with AI-driven recommendations."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, nullable=False, default=lambda: str(uuid4()))
    activity_types = Column(JSON)  # Store as JSON array
    preferred_units = Column(String, default="imperial")
    cache_enabled = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)
    ai_insights_enabled = Column(Boolean, default=True)
    preferred_forecast_days = Column(Integer, default=5)
    location_sharing = Column(Boolean, default=False)
    privacy_level = Column(String, default="standard")  # minimal, standard, full
    theme_preference = Column(String, default="auto")  # light, dark, auto
    language = Column(String, default="en")
    timezone = Column(String)
    ai_personalization_data = Column(JSON)  # AI learning data

    # Relationships
    favorite_cities = relationship(
        "FavoriteCities", back_populates="user", cascade="all, delete-orphan"
    )
    journal_entries = relationship(
        "JournalEntries", back_populates="user", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (Index("idx_user_preferences_user_id", "user_id"),)

    @hybrid_property
    def is_metric_user(self) -> bool:
        """Check if user prefers metric units."""
        return self.preferred_units == "metric"

    @hybrid_property
    def activity_count(self) -> int:
        """Get number of preferred activity types."""
        return len(self.activity_types) if self.activity_types else 0

    def add_activity_type(self, activity_type: str) -> None:
        """Add activity type to preferences."""
        if not self.activity_types:
            self.activity_types = []
        if activity_type not in self.activity_types:
            self.activity_types.append(activity_type)

    def remove_activity_type(self, activity_type: str) -> None:
        """Remove activity type from preferences."""
        if self.activity_types and activity_type in self.activity_types:
            self.activity_types.remove(activity_type)

    def update_ai_learning_data(self, interaction_data: Dict[str, Any]) -> None:
        """Update AI personalization data based on user interactions."""
        if not self.ai_personalization_data:
            self.ai_personalization_data = {
                "interactions": [],
                "preferences": {},
                "patterns": {},
            }

        self.ai_personalization_data["interactions"].append(
            {"timestamp": datetime.now(timezone.utc).isoformat(), **interaction_data}
        )

        # Keep only last 100 interactions
        self.ai_personalization_data["interactions"] = self.ai_personalization_data[
            "interactions"
        ][-100:]

    def generate_ai_insights(self, gemini_api_key: str) -> Dict[str, Any]:
        """Generate AI insights about user preferences and patterns."""
        prompt = f"""Analyze user preferences and behavior patterns:
        
Activity Types: {self.activity_types}
Preferred Units: {self.preferred_units}
Notifications: {self.notifications_enabled}
Forecast Days: {self.preferred_forecast_days}
Interaction Data: {json.dumps(self.ai_personalization_data or {}, indent=2)[:1000]}...
        
Provide insights about:
1. User behavior patterns
2. Recommended features or settings
3. Optimal notification timing
4. Personalized activity suggestions
        
Format as JSON with keys: behavior_patterns, feature_recommendations, notification_optimization, activity_suggestions."""

        ai_response = self._call_gemini_api(prompt, gemini_api_key)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return {"raw_insights": ai_response}

        return {"error": "Failed to generate insights"}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_types": self.activity_types,
            "preferred_units": self.preferred_units,
            "cache_enabled": self.cache_enabled,
            "notifications_enabled": self.notifications_enabled,
            "ai_insights_enabled": self.ai_insights_enabled,
            "preferred_forecast_days": self.preferred_forecast_days,
            "location_sharing": self.location_sharing,
            "privacy_level": self.privacy_level,
            "theme_preference": self.theme_preference,
            "language": self.language,
            "timezone": self.timezone,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
        }


class FavoriteCities(Base, AuditMixin, AIEnhancedMixin):  # type: ignore[misc,valid-type]
    """Enhanced favorite cities with analytics and AI insights."""

    __tablename__ = "favorite_cities"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(String, unique=True, nullable=False, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("user_preferences.user_id"), nullable=False)
    city_name = Column(String, nullable=False)
    country_name = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    region = Column(String, nullable=True)  # state/province
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timezone = Column(String, nullable=True)
    nickname = Column(String, nullable=True)
    visit_count = Column(Integer, default=0)
    last_viewed = Column(DateTime)
    is_home_location = Column(Boolean, default=False)
    notification_enabled = Column(Boolean, default=True)
    alert_preferences = Column(JSON)  # Weather alert preferences
    custom_settings = Column(JSON)  # Custom display settings
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    user = relationship("UserPreferences", back_populates="favorite_cities")
    weather_entries = relationship(
        "WeatherHistory", back_populates="city", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("idx_favorite_cities_user_id", "user_id"),
        Index("idx_favorite_cities_city_name", "city_name"),
        Index("idx_favorite_cities_coordinates", "latitude", "longitude"),
    )

    @hybrid_property
    def display_name(self) -> str:
        """Get display name for the city."""
        if self.nickname:
            return self.nickname
        elif self.region:
            return f"{self.city_name}, {self.region}, {self.country_name or self.country_code}"
        else:
            return f"{self.city_name}, {self.country_name or self.country_code}"

    @hybrid_property
    def coordinates(self) -> Optional[str]:
        """Get coordinates as string."""
        if self.latitude is not None and self.longitude is not None:
            return f"{self.latitude},{self.longitude}"
        return None

    def mark_visited(self) -> None:
        """Mark city as visited and update counters."""
        self.visit_count += 1
        self.last_viewed = datetime.now(timezone.utc)

    def update_alert_preferences(
        self, alert_types: List[str], severity_threshold: str = "moderate"
    ) -> None:
        """Update weather alert preferences."""
        self.alert_preferences = {
            "enabled_alerts": alert_types,
            "severity_threshold": severity_threshold,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_weather_summary(self, session: Session) -> Dict[str, Any]:
        """Get weather history summary for this city."""
        from sqlalchemy import func

        # Get basic statistics
        stats = (
            session.query(
                func.avg(WeatherHistory.temperature).label("avg_temp"),
                func.min(WeatherHistory.temperature).label("min_temp"),
                func.max(WeatherHistory.temperature).label("max_temp"),
                func.avg(WeatherHistory.humidity).label("avg_humidity"),
                func.count(WeatherHistory.id).label("total_records"),
            )
            .filter(WeatherHistory.city_id == self.id)
            .first()
        )

        # Get most common conditions
        common_conditions = (
            session.query(
                WeatherHistory.condition,
                func.count(WeatherHistory.condition).label("count"),
            )
            .filter(WeatherHistory.city_id == self.id)
            .group_by(WeatherHistory.condition)
            .order_by(func.count(WeatherHistory.condition).desc())
            .limit(5)
            .all()
        )

        return {
            "city_name": self.display_name,
            "total_records": stats.total_records or 0,
            "average_temperature": float(stats.avg_temp) if stats.avg_temp else None,
            "min_temperature": float(stats.min_temp) if stats.min_temp else None,
            "max_temperature": float(stats.max_temp) if stats.max_temp else None,
            "average_humidity": (
                float(stats.avg_humidity) if stats.avg_humidity else None
            ),
            "common_conditions": [(cond, count) for cond, count in common_conditions],
            "visit_count": self.visit_count,
            "last_viewed": self.last_viewed.isoformat() if self.last_viewed else None,
        }

    def generate_ai_insights(self, gemini_api_key: str) -> Dict[str, Any]:
        """Generate AI insights about this favorite city."""
        prompt = f"""Analyze this favorite city and provide insights:
        
City: {self.display_name}
Coordinates: {self.coordinates}
Visit Count: {self.visit_count}
Last Viewed: {self.last_viewed}
Alert Preferences: {self.alert_preferences}
Custom Settings: {self.custom_settings}
        
Provide insights about:
1. Best times to visit based on typical weather patterns
2. Seasonal characteristics and what to expect
3. Activity recommendations for this location
4. Weather monitoring suggestions
        
Format as JSON with keys: best_visit_times, seasonal_info, activity_recommendations, monitoring_tips."""

        ai_response = self._call_gemini_api(prompt, gemini_api_key)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return {"raw_insights": ai_response}

        return {"error": "Failed to generate insights"}


class WeatherHistory(Base):  # type: ignore[misc,valid-type]
    """Weather history table."""

    __tablename__ = "weather_history"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("favorite_cities.id"), nullable=True)
    city_name = Column(String, nullable=False)  # Keep for non-favorite cities
    country = Column(String, nullable=True)
    temperature = Column(Float, nullable=False)
    condition = Column(String, nullable=False)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    wind_direction = Column(Float, nullable=True)
    pressure = Column(Float, nullable=True)
    visibility = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship to favorite cities
    city = relationship("FavoriteCities", back_populates="weather_entries")


class JournalEntries(Base, AuditMixin, AIEnhancedMixin):  # type: ignore[misc,valid-type]
    """Enhanced journal entries with AI analysis and insights."""

    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    entry_id = Column(String, unique=True, nullable=False, default=lambda: str(uuid4()))
    user_id = Column(String, ForeignKey("user_preferences.user_id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    weather_conditions = Column(JSON, nullable=True)  # Full weather data
    location = Column(String, nullable=True)
    coordinates = Column(String, nullable=True)  # lat,lon
    mood = Column(String, nullable=True)
    mood_score = Column(Float, nullable=True)  # -1.0 to 1.0
    activities = Column(JSON, nullable=True)  # Store as JSON array
    tags = Column(JSON, nullable=True)  # User-defined tags
    is_private = Column(Boolean, default=True)
    sentiment_analysis = Column(JSON, nullable=True)  # AI sentiment analysis
    weather_correlation = Column(JSON, nullable=True)  # Weather-mood correlation
    ai_summary = Column(Text, nullable=True)  # AI-generated summary
    word_count = Column(Integer, default=0)
    reading_time_minutes = Column(Integer, default=1)

    # Relationships
    user = relationship("UserPreferences", back_populates="journal_entries")

    # Indexes for performance
    __table_args__ = (
        Index("idx_journal_entries_user_id", "user_id"),
        Index("idx_journal_entries_created_at", "created_at"),
        Index("idx_journal_entries_mood", "mood"),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.content:
            self._update_content_metrics()

    def _update_content_metrics(self) -> None:
        """Update word count and reading time."""
        words = len(self.content.split())
        self.word_count = words
        self.reading_time_minutes = max(1, words // 200)  # Average reading speed

    @hybrid_property
    def has_weather_data(self) -> bool:
        """Check if entry has associated weather data."""
        return self.weather_conditions is not None

    @hybrid_property
    def activity_count(self) -> int:
        """Get number of activities mentioned."""
        return len(self.activities) if self.activities else 0

    def add_tag(self, tag: str) -> None:
        """Add a tag to the entry."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the entry."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)

    def update_content(self, new_content: str) -> None:
        """Update content and recalculate metrics."""
        self.content = new_content
        self._update_content_metrics()
        self.update_audit_fields()

    def analyze_sentiment(self, gemini_api_key: str) -> Dict[str, Any]:
        """Analyze sentiment of journal entry content."""
        prompt = f"""Analyze the sentiment and emotional content of this journal entry:
        
Title: {self.title}
Content: {self.content[:1000]}...
Weather: {self.weather_conditions}
Activities: {self.activities}
        
Provide analysis for:
1. Overall sentiment (positive, negative, neutral)
2. Emotional tone and intensity
3. Weather-mood correlation insights
4. Key themes and topics
        
Format as JSON with keys: sentiment, emotional_tone, intensity_score, weather_mood_correlation, key_themes."""

        ai_response = self._call_gemini_api(prompt, gemini_api_key)
        if ai_response:
            try:
                analysis = json.loads(ai_response)
                self.sentiment_analysis = analysis

                # Extract mood score
                if "intensity_score" in analysis:
                    self.mood_score = analysis["intensity_score"]

                return analysis
            except json.JSONDecodeError:
                return {"raw_analysis": ai_response}

        return {"error": "Failed to analyze sentiment"}

    def generate_ai_insights(self, gemini_api_key: str) -> Dict[str, Any]:
        """Generate AI insights about this journal entry."""
        prompt = f"""Provide insights and recommendations based on this journal entry:
        
Title: {self.title}
Content: {self.content[:500]}...
Mood: {self.mood}
Weather: {self.weather_conditions}
Activities: {self.activities}
Sentiment Analysis: {self.sentiment_analysis}
        
Provide insights about:
1. Personal growth opportunities
2. Pattern recognition in mood and activities
3. Weather impact on wellbeing
4. Recommendations for future activities
        
Format as JSON with keys: growth_opportunities, patterns, weather_impact, activity_recommendations."""

        ai_response = self._call_gemini_api(prompt, gemini_api_key)
        if ai_response:
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                return {"raw_insights": ai_response}

        return {"error": "Failed to generate insights"}


class ActivityRecommendations(Base):  # type: ignore[misc,valid-type]
    """Activity recommendations table."""

    __tablename__ = "activity_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    activity_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # outdoor, indoor, sports, relaxation
    min_temperature = Column(Float, nullable=True)
    max_temperature = Column(Float, nullable=True)
    suitable_conditions = Column(
        JSON, nullable=True
    )  # Weather conditions suitable for activity
    unsuitable_conditions = Column(
        JSON, nullable=True
    )  # Weather conditions not suitable
    created_at = Column(DateTime, default=datetime.utcnow)


def init_database():
    """Legacy database initialization - use init_enhanced_database() for new features."""
    logging.warning(
        "Using legacy database initialization. Consider upgrading to init_enhanced_database()"
    )
    init_enhanced_database()


def get_db_session() -> Session:
    """Get a database session."""
    return SessionLocal()


def close_db_session(session: Session):
    """Close a database session."""
    session.close()


# Repository Pattern Implementation
class BaseRepository:
    """Base repository with common CRUD operations."""

    def __init__(self, model_class, session: Optional[Session] = None):
        self.model_class = model_class
        self.session = session or SessionLocal()
        self._should_close_session = session is None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._should_close_session:
            self.session.close()

    def create(self, **kwargs) -> Any:
        """Create a new record."""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def get_by_id(self, id: Union[int, str]) -> Optional[Any]:
        """Get record by ID."""
        return (
            self.session.query(self.model_class)
            .filter(self.model_class.id == id)
            .first()
        )

    def update(self, id: Union[int, str], **kwargs) -> Optional[Any]:
        """Update record by ID."""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            if hasattr(instance, "update_audit_fields"):
                instance.update_audit_fields()
            self.session.commit()
            self.session.refresh(instance)
        return instance

    def delete(self, id: Union[int, str]) -> bool:
        """Delete record by ID."""
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False

    def list_all(self, **filters) -> List[Any]:
        """List all records with optional filters."""
        query = self.session.query(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.all()

    def count(self, **filters) -> int:
        """Count records with optional filters."""
        query = self.session.query(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                query = query.filter(getattr(self.model_class, key) == value)
        return query.count()


class UserPreferencesRepository(BaseRepository):
    """Repository for user preferences with specialized methods."""

    def __init__(self, session: Optional[Session] = None):
        super().__init__(UserPreferences, session)

    def get_by_user_id(self, user_id: str) -> Optional[UserPreferences]:
        """Get user preferences by user ID."""
        return (
            self.session.query(UserPreferences)
            .filter(UserPreferences.user_id == user_id)
            .first()
        )

    def create_default_preferences(self, user_id: str) -> UserPreferences:
        """Create default preferences for a new user."""
        return self.create(
            user_id=user_id,
            activity_types=["outdoor", "indoor", "sports", "relaxation"],
            preferred_units="imperial",
            cache_enabled=True,
            notifications_enabled=True,
            ai_insights_enabled=True,
            preferred_forecast_days=5,
        )

    def update_activity_preferences(
        self, user_id: str, activity_types: List[str]
    ) -> Optional[UserPreferences]:
        """Update user's activity preferences."""
        user_prefs = self.get_by_user_id(user_id)
        if user_prefs:
            user_prefs.activity_types = activity_types
            user_prefs.update_audit_fields()
            self.session.commit()
        return user_prefs


class FavoriteCitiesRepository(BaseRepository):
    """Repository for favorite cities with specialized methods."""

    def __init__(self, session: Optional[Session] = None):
        super().__init__(FavoriteCities, session)

    def get_user_cities(self, user_id: str) -> List[FavoriteCities]:
        """Get all favorite cities for a user."""
        return (
            self.session.query(FavoriteCities)
            .filter(FavoriteCities.user_id == user_id)
            .order_by(FavoriteCities.visit_count.desc())
            .all()
        )

    def get_by_coordinates(
        self, latitude: float, longitude: float, tolerance: float = 0.01
    ) -> Optional[FavoriteCities]:
        """Find city by coordinates with tolerance."""
        return (
            self.session.query(FavoriteCities)
            .filter(
                func.abs(FavoriteCities.latitude - latitude) < tolerance,
                func.abs(FavoriteCities.longitude - longitude) < tolerance,
            )
            .first()
        )

    def get_most_visited(self, user_id: str, limit: int = 5) -> List[FavoriteCities]:
        """Get most visited cities for a user."""
        return (
            self.session.query(FavoriteCities)
            .filter(FavoriteCities.user_id == user_id)
            .order_by(FavoriteCities.visit_count.desc())
            .limit(limit)
            .all()
        )

    def mark_city_visited(self, city_id: Union[int, str]) -> Optional[FavoriteCities]:
        """Mark a city as visited."""
        city = self.get_by_id(city_id)
        if city:
            city.mark_visited()
            self.session.commit()
        return city


class JournalEntriesRepository(BaseRepository):
    """Repository for journal entries with specialized methods."""

    def __init__(self, session: Optional[Session] = None):
        super().__init__(JournalEntries, session)

    def get_user_entries(
        self, user_id: str, limit: Optional[int] = None
    ) -> List[JournalEntries]:
        """Get journal entries for a user."""
        query = (
            self.session.query(JournalEntries)
            .filter(JournalEntries.user_id == user_id)
            .order_by(JournalEntries.created_at.desc())
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_entries_by_mood(self, user_id: str, mood: str) -> List[JournalEntries]:
        """Get entries filtered by mood."""
        return (
            self.session.query(JournalEntries)
            .filter(JournalEntries.user_id == user_id, JournalEntries.mood == mood)
            .order_by(JournalEntries.created_at.desc())
            .all()
        )

    def get_entries_with_weather(self, user_id: str) -> List[JournalEntries]:
        """Get entries that have weather data."""
        return (
            self.session.query(JournalEntries)
            .filter(
                JournalEntries.user_id == user_id,
                JournalEntries.weather_conditions.isnot(None),
            )
            .order_by(JournalEntries.created_at.desc())
            .all()
        )

    def get_mood_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get mood statistics for a user."""
        mood_counts = (
            self.session.query(
                JournalEntries.mood, func.count(JournalEntries.mood).label("count")
            )
            .filter(JournalEntries.user_id == user_id, JournalEntries.mood.isnot(None))
            .group_by(JournalEntries.mood)
            .all()
        )

        avg_mood_score = (
            self.session.query(func.avg(JournalEntries.mood_score))
            .filter(
                JournalEntries.user_id == user_id, JournalEntries.mood_score.isnot(None)
            )
            .scalar()
        )

        return {
            "mood_distribution": [(mood, count) for mood, count in mood_counts],
            "average_mood_score": float(avg_mood_score) if avg_mood_score else None,
            "total_entries": sum(count for _, count in mood_counts),
        }


# Factory Pattern for Model Creation
class DatabaseModelFactory:
    """Factory for creating database models with proper initialization."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        self.logger = logging.getLogger(__name__)

    def create_user_preferences(
        self, user_id: str, activity_types: Optional[List[str]] = None, **kwargs
    ) -> UserPreferences:
        """Create user preferences with defaults."""
        if activity_types is None:
            activity_types = ["outdoor", "indoor", "sports", "relaxation"]

        prefs = UserPreferences(
            user_id=user_id, activity_types=activity_types, **kwargs
        )

        # Generate AI insights if enabled
        if self.gemini_api_key and prefs.ai_insights_enabled:
            try:
                prefs.generate_ai_insights(self.gemini_api_key)
                self.logger.info(
                    f"Generated AI insights for user preferences: {user_id}"
                )
            except Exception as e:
                self.logger.warning(f"Failed to generate AI insights: {e}")

        return prefs

    def create_favorite_city(
        self,
        user_id: str,
        city_name: str,
        country_name: str,
        latitude: float,
        longitude: float,
        **kwargs,
    ) -> FavoriteCities:
        """Create favorite city with location data."""
        city = FavoriteCities(
            user_id=user_id,
            city_name=city_name,
            country_name=country_name,
            latitude=latitude,
            longitude=longitude,
            **kwargs,
        )

        # Generate AI insights if enabled
        if self.gemini_api_key:
            try:
                city.generate_ai_insights(self.gemini_api_key)
                self.logger.info(f"Generated AI insights for city: {city_name}")
            except Exception as e:
                self.logger.warning(f"Failed to generate AI insights: {e}")

        return city

    def create_journal_entry(
        self, user_id: str, title: str, content: str, **kwargs
    ) -> JournalEntries:
        """Create journal entry with content analysis."""
        entry = JournalEntries(user_id=user_id, title=title, content=content, **kwargs)

        # Perform AI analysis if enabled
        if self.gemini_api_key:
            try:
                # Analyze sentiment
                entry.analyze_sentiment(self.gemini_api_key)
                # Generate insights
                entry.generate_ai_insights(self.gemini_api_key)
                self.logger.info(f"Generated AI analysis for journal entry: {title}")
            except Exception as e:
                self.logger.warning(f"Failed to generate AI analysis: {e}")

        return entry


# Enhanced database initialization
def init_enhanced_database():
    """Initialize the enhanced database with all improvements."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logging.info(f"Enhanced database initialized at: {DATABASE_PATH}")

        # Insert enhanced default data
        with SessionLocal() as session:
            factory = DatabaseModelFactory()

            # Check if user preferences exist
            if not session.query(UserPreferences).first():
                default_prefs = factory.create_user_preferences(
                    user_id="default_user",
                    activity_types=["outdoor", "indoor", "sports", "relaxation"],
                    preferred_units="imperial",
                    cache_enabled=True,
                    notifications_enabled=True,
                    ai_insights_enabled=True,
                )
                session.add(default_prefs)

            # Enhanced activity recommendations with AI categories
            if not session.query(ActivityRecommendations).first():
                enhanced_activities = [
                    ActivityRecommendations(
                        activity_name="AI-Enhanced Beach Day",
                        description="Perfect for sunny, warm weather with AI-powered timing",
                        category="outdoor",
                        min_temperature=75.0,
                        suitable_conditions=["clear", "sunny"],
                        unsuitable_conditions=["rain", "storm", "snow"],
                    ),
                    ActivityRecommendations(
                        activity_name="Smart Museum Visit",
                        description="AI-curated indoor activity for any weather",
                        category="indoor",
                        suitable_conditions=["rain", "snow", "cold", "hot"],
                        unsuitable_conditions=[],
                    ),
                    ActivityRecommendations(
                        activity_name="Optimized Hiking",
                        description="AI-planned outdoor adventure in optimal conditions",
                        category="outdoor",
                        min_temperature=50.0,
                        max_temperature=85.0,
                        suitable_conditions=["clear", "partly cloudy"],
                        unsuitable_conditions=["rain", "storm", "snow"],
                    ),
                    ActivityRecommendations(
                        activity_name="Mindful Reading",
                        description="AI-enhanced relaxation activity with weather-based recommendations",
                        category="relaxation",
                        suitable_conditions=["rain", "snow", "cold"],
                        unsuitable_conditions=[],
                    ),
                ]
                session.add_all(enhanced_activities)

            session.commit()
            logging.info("Enhanced default data inserted into database")

    except Exception as e:
        logging.error(f"Error initializing enhanced database: {e}")
        raise


if __name__ == "__main__":
    # Initialize enhanced database when run directly
    logging.basicConfig(level=logging.INFO)
    init_enhanced_database()
    print(f"Enhanced database initialized at: {DATABASE_PATH}")

    # Demonstrate repository usage
    with UserPreferencesRepository() as user_repo:
        print(f"Total users: {user_repo.count()}")

    with FavoriteCitiesRepository() as city_repo:
        print(f"Total favorite cities: {city_repo.count()}")

    with JournalEntriesRepository() as journal_repo:
        print(f"Total journal entries: {journal_repo.count()}")
