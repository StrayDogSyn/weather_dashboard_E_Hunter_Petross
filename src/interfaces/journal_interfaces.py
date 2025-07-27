"""Interfaces for weather journal and diary services."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from enum import Enum


class JournalEntryType(Enum):
    """Types of journal entries."""
    DAILY_WEATHER = "daily_weather"
    ACTIVITY_LOG = "activity_log"
    MOOD_WEATHER = "mood_weather"
    TRAVEL_LOG = "travel_log"
    OBSERVATION = "observation"
    REFLECTION = "reflection"
    PHOTO_DIARY = "photo_diary"


class WeatherMood(Enum):
    """Weather-related mood states."""
    ENERGETIC = "energetic"
    CALM = "calm"
    MELANCHOLY = "melancholy"
    COZY = "cozy"
    RESTLESS = "restless"
    INSPIRED = "inspired"
    DROWSY = "drowsy"
    REFRESHED = "refreshed"
    ANXIOUS = "anxious"
    CONTENT = "content"


class SearchSortBy(Enum):
    """Sort options for journal searches."""
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    TITLE = "title"
    MOOD = "mood"
    WEATHER_CONDITION = "weather_condition"
    TEMPERATURE = "temperature"
    RELEVANCE = "relevance"


@dataclass
class WeatherSnapshot:
    """Weather conditions at time of journal entry."""
    temperature: float
    condition: str
    humidity: float
    wind_speed: float
    precipitation: float
    pressure: Optional[float] = None
    visibility: Optional[float] = None
    uv_index: Optional[float] = None
    sunrise: Optional[datetime] = None
    sunset: Optional[datetime] = None
    location: Optional[str] = None


@dataclass
class JournalEntry:
    """A weather journal entry."""
    id: str
    title: str
    content: str
    entry_type: JournalEntryType
    date: date
    created_at: datetime
    weather_snapshot: WeatherSnapshot
    mood: Optional[WeatherMood] = None
    tags: Optional[List[str]] = None
    location: Optional[str] = None
    photos: Optional[List[str]] = None  # Photo URLs or paths
    activities: Optional[List[str]] = None
    rating: Optional[float] = None  # 1-5 rating for the day
    is_favorite: bool = False
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class JournalSearchFilter:
    """Filter criteria for journal searches."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    entry_types: Optional[List[JournalEntryType]] = None
    moods: Optional[List[WeatherMood]] = None
    weather_conditions: Optional[List[str]] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    tags: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    has_photos: Optional[bool] = None
    min_rating: Optional[float] = None
    max_rating: Optional[float] = None
    is_favorite: Optional[bool] = None
    text_query: Optional[str] = None


@dataclass
class JournalSearchRequest:
    """Request for searching journal entries."""
    filters: JournalSearchFilter
    sort_by: SearchSortBy = SearchSortBy.DATE_DESC
    limit: int = 50
    offset: int = 0
    include_weather_stats: bool = False


@dataclass
class WeatherStatistics:
    """Weather statistics for a period."""
    avg_temperature: float
    min_temperature: float
    max_temperature: float
    avg_humidity: float
    total_precipitation: float
    most_common_condition: str
    avg_wind_speed: float
    sunny_days: int
    rainy_days: int
    total_days: int
    temperature_trend: str  # "increasing", "decreasing", "stable"


@dataclass
class MoodAnalysis:
    """Analysis of mood patterns related to weather."""
    most_common_mood: WeatherMood
    mood_distribution: Dict[WeatherMood, int]
    weather_mood_correlations: Dict[str, WeatherMood]  # weather condition -> most common mood
    best_weather_days: List[date]  # Days with highest ratings
    challenging_weather_days: List[date]  # Days with lowest ratings


@dataclass
class JournalSearchResult:
    """Result of journal search."""
    entries: List[JournalEntry]
    total_count: int
    weather_stats: Optional[WeatherStatistics] = None
    mood_analysis: Optional[MoodAnalysis] = None
    search_metadata: Optional[Dict[str, Any]] = None


@dataclass
class JournalTemplate:
    """Template for creating journal entries."""
    id: str
    name: str
    entry_type: JournalEntryType
    title_template: str
    content_template: str
    suggested_tags: List[str]
    prompts: List[str]  # Writing prompts
    is_default: bool = False


@dataclass
class JournalExportRequest:
    """Request for exporting journal data."""
    filters: JournalSearchFilter
    format: str  # "json", "csv", "pdf", "markdown"
    include_photos: bool = False
    include_weather_data: bool = True
    include_statistics: bool = False


@dataclass
class JournalInsight:
    """Insight generated from journal analysis."""
    type: str  # "pattern", "correlation", "trend", "recommendation"
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    supporting_data: Dict[str, Any]
    generated_at: datetime


class IJournalStorage(ABC):
    """Interface for journal data storage."""

    @abstractmethod
    async def save_entry(self, entry: JournalEntry) -> bool:
        """Save a journal entry."""
        pass

    @abstractmethod
    async def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Get a journal entry by ID."""
        pass

    @abstractmethod
    async def update_entry(self, entry: JournalEntry) -> bool:
        """Update an existing journal entry."""
        pass

    @abstractmethod
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a journal entry."""
        pass

    @abstractmethod
    async def search_entries(self, request: JournalSearchRequest) -> JournalSearchResult:
        """Search journal entries with filters."""
        pass

    @abstractmethod
    async def get_entries_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[JournalEntry]:
        """Get entries within a date range."""
        pass

    @abstractmethod
    async def get_all_tags(self) -> List[str]:
        """Get all unique tags used in journal."""
        pass

    @abstractmethod
    async def get_all_locations(self) -> List[str]:
        """Get all unique locations mentioned in journal."""
        pass


class IWeatherAnalyzer(ABC):
    """Interface for analyzing weather patterns in journal."""

    @abstractmethod
    async def calculate_weather_statistics(
        self, 
        entries: List[JournalEntry]
    ) -> WeatherStatistics:
        """Calculate weather statistics from journal entries."""
        pass

    @abstractmethod
    async def analyze_mood_patterns(
        self, 
        entries: List[JournalEntry]
    ) -> MoodAnalysis:
        """Analyze mood patterns related to weather."""
        pass

    @abstractmethod
    async def find_weather_correlations(
        self, 
        entries: List[JournalEntry]
    ) -> Dict[str, Any]:
        """Find correlations between weather and mood/activities."""
        pass

    @abstractmethod
    async def generate_insights(
        self, 
        entries: List[JournalEntry]
    ) -> List[JournalInsight]:
        """Generate insights from journal data."""
        pass


class ITemplateManager(ABC):
    """Interface for managing journal templates."""

    @abstractmethod
    async def get_templates(self) -> List[JournalTemplate]:
        """Get all available templates."""
        pass

    @abstractmethod
    async def get_template(self, template_id: str) -> Optional[JournalTemplate]:
        """Get a specific template."""
        pass

    @abstractmethod
    async def create_template(self, template: JournalTemplate) -> bool:
        """Create a new template."""
        pass

    @abstractmethod
    async def update_template(self, template: JournalTemplate) -> bool:
        """Update an existing template."""
        pass

    @abstractmethod
    async def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        pass

    @abstractmethod
    async def get_templates_by_type(
        self, 
        entry_type: JournalEntryType
    ) -> List[JournalTemplate]:
        """Get templates for a specific entry type."""
        pass


class IExportManager(ABC):
    """Interface for exporting journal data."""

    @abstractmethod
    async def export_journal(
        self, 
        request: JournalExportRequest
    ) -> bytes:
        """Export journal data in specified format."""
        pass

    @abstractmethod
    async def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        pass

    @abstractmethod
    async def estimate_export_size(
        self, 
        request: JournalExportRequest
    ) -> int:
        """Estimate size of export in bytes."""
        pass


class IJournalService(ABC):
    """High-level interface for weather journal service."""

    @abstractmethod
    async def create_entry(
        self,
        title: str,
        content: str,
        entry_type: JournalEntryType,
        weather_snapshot: WeatherSnapshot,
        mood: Optional[WeatherMood] = None,
        tags: Optional[List[str]] = None,
        **kwargs
    ) -> JournalEntry:
        """Create a new journal entry."""
        pass

    @abstractmethod
    async def update_entry(
        self,
        entry_id: str,
        **updates
    ) -> Optional[JournalEntry]:
        """Update an existing journal entry."""
        pass

    @abstractmethod
    async def delete_entry(self, entry_id: str) -> bool:
        """Delete a journal entry."""
        pass

    @abstractmethod
    async def get_entry(self, entry_id: str) -> Optional[JournalEntry]:
        """Get a journal entry by ID."""
        pass

    @abstractmethod
    async def search_entries(
        self, 
        request: JournalSearchRequest
    ) -> JournalSearchResult:
        """Search journal entries."""
        pass

    @abstractmethod
    async def get_recent_entries(self, limit: int = 10) -> List[JournalEntry]:
        """Get recent journal entries."""
        pass

    @abstractmethod
    async def get_entries_for_date(self, target_date: date) -> List[JournalEntry]:
        """Get all entries for a specific date."""
        pass

    @abstractmethod
    async def get_weather_summary(
        self, 
        start_date: date, 
        end_date: date
    ) -> WeatherStatistics:
        """Get weather summary for a date range."""
        pass

    @abstractmethod
    async def analyze_mood_trends(
        self, 
        start_date: date, 
        end_date: date
    ) -> MoodAnalysis:
        """Analyze mood trends for a date range."""
        pass

    @abstractmethod
    async def get_insights(
        self, 
        days_back: int = 30
    ) -> List[JournalInsight]:
        """Get insights from recent journal entries."""
        pass

    @abstractmethod
    async def export_journal(
        self, 
        request: JournalExportRequest
    ) -> bytes:
        """Export journal data."""
        pass

    @abstractmethod
    async def get_templates(self) -> List[JournalTemplate]:
        """Get available journal templates."""
        pass

    @abstractmethod
    async def create_from_template(
        self,
        template_id: str,
        weather_snapshot: WeatherSnapshot,
        **template_vars
    ) -> JournalEntry:
        """Create entry from template."""
        pass

    @abstractmethod
    async def get_popular_tags(self, limit: int = 20) -> List[str]:
        """Get most popular tags."""
        pass

    @abstractmethod
    async def suggest_tags(
        self, 
        content: str, 
        weather: WeatherSnapshot
    ) -> List[str]:
        """Suggest tags based on content and weather."""
        pass

    @abstractmethod
    async def get_memory_for_date(
        self, 
        target_date: date, 
        years_back: int = 5
    ) -> List[JournalEntry]:
        """Get entries from the same date in previous years."""
        pass