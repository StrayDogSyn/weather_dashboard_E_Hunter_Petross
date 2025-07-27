"""Interfaces for weather comparison services."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta


class ComparisonMetric(Enum):
    """Weather metrics that can be compared."""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"
    WIND_SPEED = "wind_speed"
    PRECIPITATION = "precipitation"
    UV_INDEX = "uv_index"
    VISIBILITY = "visibility"
    FEELS_LIKE = "feels_like"


class ChartType(Enum):
    """Types of charts for data visualization."""
    LINE = "line"
    BAR = "bar"
    AREA = "area"
    SCATTER = "scatter"
    RADAR = "radar"
    HEATMAP = "heatmap"


class TimeRange(Enum):
    """Time ranges for comparison."""
    CURRENT = "current"
    HOURLY_24H = "hourly_24h"
    DAILY_7D = "daily_7d"
    DAILY_14D = "daily_14d"
    MONTHLY = "monthly"
    YEARLY = "yearly"


@dataclass
class ComparisonLocation:
    """Location for weather comparison."""
    name: str
    latitude: float
    longitude: float
    country: Optional[str] = None
    state: Optional[str] = None
    timezone: Optional[str] = None
    color: Optional[str] = None  # For chart visualization


@dataclass
class WeatherDataPoint:
    """Single weather data point for comparison."""
    timestamp: datetime
    location: ComparisonLocation
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[float] = None
    uv_index: Optional[float] = None
    visibility: Optional[float] = None
    feels_like: Optional[float] = None
    condition: Optional[str] = None
    icon: Optional[str] = None


@dataclass
class ComparisonRequest:
    """Request for weather comparison."""
    locations: List[ComparisonLocation]
    metrics: List[ComparisonMetric]
    time_range: TimeRange
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    chart_type: ChartType = ChartType.LINE
    include_forecast: bool = False


@dataclass
class ChartDataSeries:
    """Data series for chart visualization."""
    name: str
    data: List[Tuple[datetime, float]]
    color: Optional[str] = None
    unit: Optional[str] = None
    location: Optional[ComparisonLocation] = None


@dataclass
class ChartConfiguration:
    """Configuration for chart generation."""
    chart_type: ChartType
    title: str
    x_axis_label: str
    y_axis_label: str
    series: List[ChartDataSeries]
    width: int = 800
    height: int = 400
    show_legend: bool = True
    show_grid: bool = True
    time_format: str = "%Y-%m-%d %H:%M"
    theme: str = "light"


@dataclass
class ComparisonStatistics:
    """Statistical analysis of comparison data."""
    metric: ComparisonMetric
    locations: List[str]
    min_values: Dict[str, float]
    max_values: Dict[str, float]
    avg_values: Dict[str, float]
    std_deviation: Dict[str, float]
    correlation_matrix: Optional[Dict[str, Dict[str, float]]] = None
    trend_analysis: Optional[Dict[str, str]] = None


@dataclass
class ComparisonResult:
    """Result of weather comparison analysis."""
    request: ComparisonRequest
    data_points: List[WeatherDataPoint]
    chart_config: ChartConfiguration
    statistics: List[ComparisonStatistics]
    insights: List[str]
    generated_at: datetime
    data_quality_score: float
    missing_data_points: int


class IWeatherDataCollector(ABC):
    """Interface for collecting weather data for comparison."""

    @abstractmethod
    async def collect_current_data(self, locations: List[ComparisonLocation]) -> List[WeatherDataPoint]:
        """Collect current weather data for multiple locations.
        
        Args:
            locations: List of locations to collect data for
            
        Returns:
            List of current weather data points
        """
        pass

    @abstractmethod
    async def collect_historical_data(
        self,
        locations: List[ComparisonLocation],
        start_date: datetime,
        end_date: datetime
    ) -> List[WeatherDataPoint]:
        """Collect historical weather data for multiple locations.
        
        Args:
            locations: List of locations to collect data for
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            List of historical weather data points
        """
        pass

    @abstractmethod
    async def collect_forecast_data(
        self,
        locations: List[ComparisonLocation],
        days: int = 7
    ) -> List[WeatherDataPoint]:
        """Collect forecast data for multiple locations.
        
        Args:
            locations: List of locations to collect data for
            days: Number of days to forecast
            
        Returns:
            List of forecast weather data points
        """
        pass


class IChartGenerator(ABC):
    """Interface for generating weather comparison charts."""

    @abstractmethod
    async def generate_chart(self, config: ChartConfiguration) -> bytes:
        """Generate chart image from configuration.
        
        Args:
            config: Chart configuration
            
        Returns:
            Chart image as bytes
        """
        pass

    @abstractmethod
    async def generate_interactive_chart(self, config: ChartConfiguration) -> str:
        """Generate interactive chart HTML.
        
        Args:
            config: Chart configuration
            
        Returns:
            Interactive chart as HTML string
        """
        pass

    @abstractmethod
    async def get_supported_chart_types(self) -> List[ChartType]:
        """Get list of supported chart types.
        
        Returns:
            List of supported chart types
        """
        pass


class IStatisticsCalculator(ABC):
    """Interface for calculating comparison statistics."""

    @abstractmethod
    async def calculate_basic_stats(
        self,
        data_points: List[WeatherDataPoint],
        metric: ComparisonMetric
    ) -> ComparisonStatistics:
        """Calculate basic statistics for a metric.
        
        Args:
            data_points: Weather data points
            metric: Metric to analyze
            
        Returns:
            Basic statistics for the metric
        """
        pass

    @abstractmethod
    async def calculate_correlation(
        self,
        data_points: List[WeatherDataPoint],
        metrics: List[ComparisonMetric]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate correlation between metrics across locations.
        
        Args:
            data_points: Weather data points
            metrics: Metrics to correlate
            
        Returns:
            Correlation matrix
        """
        pass

    @abstractmethod
    async def analyze_trends(
        self,
        data_points: List[WeatherDataPoint],
        metric: ComparisonMetric
    ) -> Dict[str, str]:
        """Analyze trends in weather data.
        
        Args:
            data_points: Weather data points
            metric: Metric to analyze
            
        Returns:
            Trend analysis results
        """
        pass


class IInsightGenerator(ABC):
    """Interface for generating weather comparison insights."""

    @abstractmethod
    async def generate_insights(
        self,
        comparison_result: ComparisonResult
    ) -> List[str]:
        """Generate insights from comparison results.
        
        Args:
            comparison_result: Comparison analysis results
            
        Returns:
            List of insight strings
        """
        pass

    @abstractmethod
    async def generate_recommendations(
        self,
        comparison_result: ComparisonResult
    ) -> List[str]:
        """Generate recommendations based on comparison.
        
        Args:
            comparison_result: Comparison analysis results
            
        Returns:
            List of recommendation strings
        """
        pass


class IComparisonService(ABC):
    """High-level interface for weather comparison service."""

    @abstractmethod
    async def compare_weather(
        self,
        request: ComparisonRequest
    ) -> ComparisonResult:
        """Perform comprehensive weather comparison.
        
        Args:
            request: Comparison request parameters
            
        Returns:
            Complete comparison results with charts and analysis
        """
        pass

    @abstractmethod
    async def compare_current_weather(
        self,
        locations: List[ComparisonLocation],
        metrics: List[ComparisonMetric]
    ) -> ComparisonResult:
        """Compare current weather across locations.
        
        Args:
            locations: Locations to compare
            metrics: Metrics to compare
            
        Returns:
            Current weather comparison results
        """
        pass

    @abstractmethod
    async def compare_forecasts(
        self,
        locations: List[ComparisonLocation],
        days: int = 7
    ) -> ComparisonResult:
        """Compare weather forecasts across locations.
        
        Args:
            locations: Locations to compare
            days: Number of forecast days
            
        Returns:
            Forecast comparison results
        """
        pass

    @abstractmethod
    async def get_location_suggestions(self, query: str) -> List[ComparisonLocation]:
        """Get location suggestions for comparison.
        
        Args:
            query: Search query for locations
            
        Returns:
            List of suggested locations
        """
        pass

    @abstractmethod
    async def save_comparison(
        self,
        result: ComparisonResult,
        name: str
    ) -> str:
        """Save comparison results for later retrieval.
        
        Args:
            result: Comparison results to save
            name: Name for the saved comparison
            
        Returns:
            Unique identifier for the saved comparison
        """
        pass

    @abstractmethod
    async def load_comparison(self, comparison_id: str) -> Optional[ComparisonResult]:
        """Load previously saved comparison results.
        
        Args:
            comparison_id: Unique identifier of the comparison
            
        Returns:
            Loaded comparison results or None if not found
        """
        pass

    @abstractmethod
    async def list_saved_comparisons(self) -> List[Dict[str, Any]]:
        """List all saved comparisons.
        
        Returns:
            List of saved comparison metadata
        """
        pass