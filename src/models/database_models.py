"""Database models for Weather Dashboard using SQLAlchemy ORM."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

# Database configuration
DATABASE_PATH = Path(__file__).parent.parent.parent / "data" / "weather_dashboard.db"
DATABASE_URL = "sqlite:///" + str(DATABASE_PATH)

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class UserPreferences(Base):  # type: ignore[misc,valid-type]
    """User preferences table."""

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    activity_types = Column(JSON)  # Store as JSON array
    preferred_units = Column(String, default="imperial")
    cache_enabled = Column(Boolean, default=True)
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FavoriteCities(Base):  # type: ignore[misc,valid-type]
    """Favorite cities table."""

    __tablename__ = "favorite_cities"

    id = Column(Integer, primary_key=True, index=True)
    city_name = Column(String, nullable=False)
    country_code = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to weather history
    weather_entries = relationship("WeatherHistory", back_populates="city")


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


class JournalEntries(Base):  # type: ignore[misc,valid-type]
    """Journal entries table."""

    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    weather_conditions = Column(String, nullable=True)
    location = Column(String, nullable=True)
    mood = Column(String, nullable=True)
    activities = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


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
    """Initialize the database and create all tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logging.info(f"Database initialized at: {DATABASE_PATH}")

        # Insert default data if tables are empty
        with SessionLocal() as session:
            # Check if user preferences exist
            if not session.query(UserPreferences).first():
                default_prefs = UserPreferences(
                    activity_types=["outdoor", "indoor", "sports", "relaxation"],
                    preferred_units="imperial",
                    cache_enabled=True,
                    notifications_enabled=True,
                )
                session.add(default_prefs)

            # Add default activity recommendations
            if not session.query(ActivityRecommendations).first():
                default_activities = [
                    ActivityRecommendations(
                        activity_name="Beach Day",
                        description="Perfect for sunny, warm weather",
                        category="outdoor",
                        min_temperature=75.0,
                        suitable_conditions=["clear", "sunny"],
                        unsuitable_conditions=["rain", "storm", "snow"],
                    ),
                    ActivityRecommendations(
                        activity_name="Museum Visit",
                        description="Great indoor activity for any weather",
                        category="indoor",
                        suitable_conditions=["rain", "snow", "cold", "hot"],
                        unsuitable_conditions=[],
                    ),
                    ActivityRecommendations(
                        activity_name="Hiking",
                        description="Outdoor adventure in good weather",
                        category="outdoor",
                        min_temperature=50.0,
                        max_temperature=85.0,
                        suitable_conditions=["clear", "partly cloudy"],
                        unsuitable_conditions=["rain", "storm", "snow"],
                    ),
                    ActivityRecommendations(
                        activity_name="Reading at Home",
                        description="Perfect relaxation activity",
                        category="relaxation",
                        suitable_conditions=["rain", "snow", "cold"],
                        unsuitable_conditions=[],
                    ),
                ]
                session.add_all(default_activities)

            session.commit()
            logging.info("Default data inserted into database")

    except Exception as e:
        logging.error(f"Error initializing database: {e}")
        raise


def get_db_session() -> Session:
    """Get a database session."""
    return SessionLocal()


def close_db_session(session: Session):
    """Close a database session."""
    session.close()


if __name__ == "__main__":
    # Initialize database when run directly
    logging.basicConfig(level=logging.INFO)
    init_database()
    print(f"Database initialized at: {DATABASE_PATH}")
