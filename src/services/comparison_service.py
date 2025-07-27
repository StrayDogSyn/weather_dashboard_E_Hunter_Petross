"""Weather comparison service implementation with chart generation and analytics."""

import asyncio
import logging
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import statistics
import math

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    import pandas as pd
    import numpy as np
except ImportError:
    plt = sns = pd = np = None

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
except ImportError:
    go = px = make_subplots = None

from ..interfaces.comparison_interfaces import (
    IComparisonService, IWeatherDataCollector, IChartGenerator,
    IStatisticsCalculator, IInsightGenerator,
    ComparisonRequest, ComparisonResult, ComparisonLocation,
    WeatherDataPoint, ChartConfiguration, ChartDataSeries,
    ComparisonStatistics, ComparisonMetric, ChartType, TimeRange
)
from ..interfaces.weather_interfaces import IAsyncWeatherAPI


logger = logging.getLogger(__name__)


class WeatherDataCollector(IWeatherDataCollector):
    """Collects weather data from multiple sources for comparison."""

    def __init__(self, weather_api: IAsyncWeatherAPI):
        self.weather_api = weather_api

    async def collect_current_data(self, locations: List[ComparisonLocation]) -> List[WeatherDataPoint]:
        """Collect current weather data for multiple locations."""
        data_points = []
        
        # Collect data concurrently for better performance
        tasks = []
        for location in locations:
            task = self._fetch_current_weather(location)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for location, result in zip(locations, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching weather for {location.name}: {result}")
                continue
            
            if result:
                data_points.append(result)
        
        return data_points

    async def collect_historical_data(
        self,
        locations: List[ComparisonLocation],
        start_date: datetime,
        end_date: datetime
    ) -> List[WeatherDataPoint]:
        """Collect historical weather data for multiple locations."""
        data_points = []
        
        # Note: This would require a historical weather API
        # For now, we'll simulate with current data
        logger.warning("Historical data collection not fully implemented - using current data")
        
        current_data = await self.collect_current_data(locations)
        return current_data

    async def collect_forecast_data(
        self,
        locations: List[ComparisonLocation],
        days: int = 7
    ) -> List[WeatherDataPoint]:
        """Collect forecast data for multiple locations."""
        data_points = []
        
        tasks = []
        for location in locations:
            task = self._fetch_forecast_weather(location, days)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for location, result in zip(locations, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching forecast for {location.name}: {result}")
                continue
            
            if result:
                data_points.extend(result)
        
        return data_points

    async def _fetch_current_weather(self, location: ComparisonLocation) -> Optional[WeatherDataPoint]:
        """Fetch current weather for a single location."""
        try:
            weather_data = await self.weather_api.get_current_weather(
                lat=location.latitude,
                lon=location.longitude
            )
            
            return WeatherDataPoint(
                timestamp=datetime.now(),
                location=location,
                temperature=weather_data.get('main', {}).get('temp'),
                humidity=weather_data.get('main', {}).get('humidity'),
                pressure=weather_data.get('main', {}).get('pressure'),
                wind_speed=weather_data.get('wind', {}).get('speed'),
                feels_like=weather_data.get('main', {}).get('feels_like'),
                visibility=weather_data.get('visibility'),
                condition=weather_data.get('weather', [{}])[0].get('description'),
                icon=weather_data.get('weather', [{}])[0].get('icon')
            )
        except Exception as e:
            logger.error(f"Error fetching current weather for {location.name}: {e}")
            return None

    async def _fetch_forecast_weather(self, location: ComparisonLocation, days: int) -> List[WeatherDataPoint]:
        """Fetch forecast weather for a single location."""
        try:
            forecast_data = await self.weather_api.get_forecast(
                lat=location.latitude,
                lon=location.longitude,
                days=days
            )
            
            data_points = []
            for item in forecast_data.get('list', []):
                timestamp = datetime.fromtimestamp(item.get('dt', 0))
                
                data_point = WeatherDataPoint(
                    timestamp=timestamp,
                    location=location,
                    temperature=item.get('main', {}).get('temp'),
                    humidity=item.get('main', {}).get('humidity'),
                    pressure=item.get('main', {}).get('pressure'),
                    wind_speed=item.get('wind', {}).get('speed'),
                    feels_like=item.get('main', {}).get('feels_like'),
                    visibility=item.get('visibility'),
                    condition=item.get('weather', [{}])[0].get('description'),
                    icon=item.get('weather', [{}])[0].get('icon')
                )
                data_points.append(data_point)
            
            return data_points
        except Exception as e:
            logger.error(f"Error fetching forecast for {location.name}: {e}")
            return []


class PlotlyChartGenerator(IChartGenerator):
    """Chart generator using Plotly for interactive visualizations."""

    def __init__(self):
        if not go:
            raise ImportError("Plotly not installed. Install with: pip install plotly")

    async def generate_chart(self, config: ChartConfiguration) -> bytes:
        """Generate static chart image from configuration."""
        try:
            fig = await self._create_plotly_figure(config)
            
            # Convert to image bytes
            img_bytes = fig.to_image(format="png", width=config.width, height=config.height)
            return img_bytes
        except Exception as e:
            logger.error(f"Error generating chart: {e}")
            return b""

    async def generate_interactive_chart(self, config: ChartConfiguration) -> str:
        """Generate interactive chart HTML."""
        try:
            fig = await self._create_plotly_figure(config)
            
            # Convert to HTML
            html = fig.to_html(
                include_plotlyjs='cdn',
                div_id=f"chart_{uuid.uuid4().hex[:8]}"
            )
            return html
        except Exception as e:
            logger.error(f"Error generating interactive chart: {e}")
            return ""

    async def get_supported_chart_types(self) -> List[ChartType]:
        """Get list of supported chart types."""
        return [
            ChartType.LINE,
            ChartType.BAR,
            ChartType.AREA,
            ChartType.SCATTER,
            ChartType.RADAR
        ]

    async def _create_plotly_figure(self, config: ChartConfiguration):
        """Create Plotly figure from configuration."""
        fig = go.Figure()
        
        for series in config.series:
            x_values = [point[0] for point in series.data]
            y_values = [point[1] for point in series.data]
            
            if config.chart_type == ChartType.LINE:
                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode='lines+markers',
                    name=series.name,
                    line=dict(color=series.color) if series.color else None
                ))
            elif config.chart_type == ChartType.BAR:
                fig.add_trace(go.Bar(
                    x=x_values,
                    y=y_values,
                    name=series.name,
                    marker_color=series.color
                ))
            elif config.chart_type == ChartType.AREA:
                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    fill='tonexty' if len(fig.data) > 0 else 'tozeroy',
                    mode='lines',
                    name=series.name,
                    line=dict(color=series.color) if series.color else None
                ))
            elif config.chart_type == ChartType.SCATTER:
                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode='markers',
                    name=series.name,
                    marker=dict(color=series.color) if series.color else None
                ))
        
        # Update layout
        fig.update_layout(
            title=config.title,
            xaxis_title=config.x_axis_label,
            yaxis_title=config.y_axis_label,
            showlegend=config.show_legend,
            width=config.width,
            height=config.height,
            template='plotly_white' if config.theme == 'light' else 'plotly_dark'
        )
        
        if config.show_grid:
            fig.update_xaxes(showgrid=True)
            fig.update_yaxes(showgrid=True)
        
        return fig


class StatisticsCalculator(IStatisticsCalculator):
    """Calculator for weather comparison statistics."""

    async def calculate_basic_stats(
        self,
        data_points: List[WeatherDataPoint],
        metric: ComparisonMetric
    ) -> ComparisonStatistics:
        """Calculate basic statistics for a metric."""
        try:
            # Group data by location
            location_data = {}
            for point in data_points:
                location_name = point.location.name
                if location_name not in location_data:
                    location_data[location_name] = []
                
                value = self._get_metric_value(point, metric)
                if value is not None:
                    location_data[location_name].append(value)
            
            # Calculate statistics for each location
            min_values = {}
            max_values = {}
            avg_values = {}
            std_deviation = {}
            
            for location, values in location_data.items():
                if values:
                    min_values[location] = min(values)
                    max_values[location] = max(values)
                    avg_values[location] = statistics.mean(values)
                    std_deviation[location] = statistics.stdev(values) if len(values) > 1 else 0.0
            
            return ComparisonStatistics(
                metric=metric,
                locations=list(location_data.keys()),
                min_values=min_values,
                max_values=max_values,
                avg_values=avg_values,
                std_deviation=std_deviation
            )
        except Exception as e:
            logger.error(f"Error calculating basic stats: {e}")
            return ComparisonStatistics(
                metric=metric,
                locations=[],
                min_values={},
                max_values={},
                avg_values={},
                std_deviation={}
            )

    async def calculate_correlation(
        self,
        data_points: List[WeatherDataPoint],
        metrics: List[ComparisonMetric]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate correlation between metrics across locations."""
        try:
            # Group data by location and extract metric values
            location_metrics = {}
            
            for point in data_points:
                location_name = point.location.name
                if location_name not in location_metrics:
                    location_metrics[location_name] = {metric: [] for metric in metrics}
                
                for metric in metrics:
                    value = self._get_metric_value(point, metric)
                    if value is not None:
                        location_metrics[location_name][metric].append(value)
            
            # Calculate correlation matrix
            correlation_matrix = {}
            
            for location, metric_data in location_metrics.items():
                correlation_matrix[location] = {}
                
                for i, metric1 in enumerate(metrics):
                    for j, metric2 in enumerate(metrics):
                        if i <= j:  # Only calculate upper triangle
                            values1 = metric_data[metric1]
                            values2 = metric_data[metric2]
                            
                            if len(values1) > 1 and len(values2) > 1 and len(values1) == len(values2):
                                corr = self._calculate_pearson_correlation(values1, values2)
                                correlation_matrix[location][f"{metric1.value}_{metric2.value}"] = corr
            
            return correlation_matrix
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return {}

    async def analyze_trends(
        self,
        data_points: List[WeatherDataPoint],
        metric: ComparisonMetric
    ) -> Dict[str, str]:
        """Analyze trends in weather data."""
        try:
            # Group data by location and sort by timestamp
            location_data = {}
            for point in data_points:
                location_name = point.location.name
                if location_name not in location_data:
                    location_data[location_name] = []
                
                value = self._get_metric_value(point, metric)
                if value is not None:
                    location_data[location_name].append((point.timestamp, value))
            
            # Analyze trends for each location
            trends = {}
            for location, data in location_data.items():
                if len(data) < 2:
                    trends[location] = "insufficient_data"
                    continue
                
                # Sort by timestamp
                data.sort(key=lambda x: x[0])
                values = [item[1] for item in data]
                
                # Simple trend analysis using linear regression slope
                n = len(values)
                x = list(range(n))
                
                slope = self._calculate_slope(x, values)
                
                if abs(slope) < 0.01:  # Threshold for "stable"
                    trends[location] = "stable"
                elif slope > 0:
                    trends[location] = "increasing"
                else:
                    trends[location] = "decreasing"
            
            return trends
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
            return {}

    def _get_metric_value(self, point: WeatherDataPoint, metric: ComparisonMetric) -> Optional[float]:
        """Extract metric value from weather data point."""
        metric_map = {
            ComparisonMetric.TEMPERATURE: point.temperature,
            ComparisonMetric.HUMIDITY: point.humidity,
            ComparisonMetric.PRESSURE: point.pressure,
            ComparisonMetric.WIND_SPEED: point.wind_speed,
            ComparisonMetric.PRECIPITATION: point.precipitation,
            ComparisonMetric.UV_INDEX: point.uv_index,
            ComparisonMetric.VISIBILITY: point.visibility,
            ComparisonMetric.FEELS_LIKE: point.feels_like
        }
        return metric_map.get(metric)

    def _calculate_pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        sum_y2 = sum(yi * yi for yi in y)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator

    def _calculate_slope(self, x: List[float], y: List[float]) -> float:
        """Calculate slope of linear regression line."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi * xi for xi in x)
        
        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0
        
        return (n * sum_xy - sum_x * sum_y) / denominator


class InsightGenerator(IInsightGenerator):
    """Generates insights and recommendations from comparison data."""

    async def generate_insights(self, comparison_result: ComparisonResult) -> List[str]:
        """Generate insights from comparison results."""
        insights = []
        
        try:
            # Temperature insights
            temp_stats = next(
                (s for s in comparison_result.statistics if s.metric == ComparisonMetric.TEMPERATURE),
                None
            )
            
            if temp_stats:
                insights.extend(self._generate_temperature_insights(temp_stats))
            
            # Humidity insights
            humidity_stats = next(
                (s for s in comparison_result.statistics if s.metric == ComparisonMetric.HUMIDITY),
                None
            )
            
            if humidity_stats:
                insights.extend(self._generate_humidity_insights(humidity_stats))
            
            # General insights
            insights.extend(self._generate_general_insights(comparison_result))
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights.append("Unable to generate detailed insights due to data processing error.")
        
        return insights

    async def generate_recommendations(self, comparison_result: ComparisonResult) -> List[str]:
        """Generate recommendations based on comparison."""
        recommendations = []
        
        try:
            # Weather-based recommendations
            temp_stats = next(
                (s for s in comparison_result.statistics if s.metric == ComparisonMetric.TEMPERATURE),
                None
            )
            
            if temp_stats:
                recommendations.extend(self._generate_temperature_recommendations(temp_stats))
            
            # Activity recommendations based on conditions
            recommendations.extend(self._generate_activity_recommendations(comparison_result))
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("Unable to generate recommendations due to data processing error.")
        
        return recommendations

    def _generate_temperature_insights(self, stats: ComparisonStatistics) -> List[str]:
        """Generate temperature-specific insights."""
        insights = []
        
        if stats.avg_values:
            warmest = max(stats.avg_values, key=stats.avg_values.get)
            coolest = min(stats.avg_values, key=stats.avg_values.get)
            
            temp_diff = stats.avg_values[warmest] - stats.avg_values[coolest]
            
            insights.append(f"{warmest} is the warmest location with an average of {stats.avg_values[warmest]:.1f}°C")
            insights.append(f"{coolest} is the coolest location with an average of {stats.avg_values[coolest]:.1f}°C")
            insights.append(f"Temperature difference between locations: {temp_diff:.1f}°C")
        
        return insights

    def _generate_humidity_insights(self, stats: ComparisonStatistics) -> List[str]:
        """Generate humidity-specific insights."""
        insights = []
        
        if stats.avg_values:
            most_humid = max(stats.avg_values, key=stats.avg_values.get)
            least_humid = min(stats.avg_values, key=stats.avg_values.get)
            
            insights.append(f"{most_humid} has the highest humidity at {stats.avg_values[most_humid]:.1f}%")
            insights.append(f"{least_humid} has the lowest humidity at {stats.avg_values[least_humid]:.1f}%")
        
        return insights

    def _generate_general_insights(self, result: ComparisonResult) -> List[str]:
        """Generate general insights about the comparison."""
        insights = []
        
        insights.append(f"Comparison includes {len(result.request.locations)} locations")
        insights.append(f"Data quality score: {result.data_quality_score:.1%}")
        
        if result.missing_data_points > 0:
            insights.append(f"Note: {result.missing_data_points} data points were missing")
        
        return insights

    def _generate_temperature_recommendations(self, stats: ComparisonStatistics) -> List[str]:
        """Generate temperature-based recommendations."""
        recommendations = []
        
        if stats.avg_values:
            warmest = max(stats.avg_values, key=stats.avg_values.get)
            coolest = min(stats.avg_values, key=stats.avg_values.get)
            
            if stats.avg_values[warmest] > 25:
                recommendations.append(f"Consider {warmest} for warm weather activities")
            
            if stats.avg_values[coolest] < 10:
                recommendations.append(f"Pack warm clothing if visiting {coolest}")
        
        return recommendations

    def _generate_activity_recommendations(self, result: ComparisonResult) -> List[str]:
        """Generate activity recommendations based on weather conditions."""
        recommendations = []
        
        # Simple activity recommendations based on temperature
        temp_stats = next(
            (s for s in result.statistics if s.metric == ComparisonMetric.TEMPERATURE),
            None
        )
        
        if temp_stats and temp_stats.avg_values:
            for location, temp in temp_stats.avg_values.items():
                if temp > 25:
                    recommendations.append(f"{location}: Great for outdoor swimming and beach activities")
                elif temp > 15:
                    recommendations.append(f"{location}: Perfect for hiking and outdoor sports")
                elif temp > 5:
                    recommendations.append(f"{location}: Good for sightseeing and indoor activities")
                else:
                    recommendations.append(f"{location}: Ideal for winter sports and cozy indoor activities")
        
        return recommendations


class ComparisonService(IComparisonService):
    """High-level weather comparison service."""

    def __init__(
        self,
        data_collector: IWeatherDataCollector,
        chart_generator: IChartGenerator,
        statistics_calculator: IStatisticsCalculator,
        insight_generator: IInsightGenerator
    ):
        self.data_collector = data_collector
        self.chart_generator = chart_generator
        self.statistics_calculator = statistics_calculator
        self.insight_generator = insight_generator
        self._saved_comparisons: Dict[str, ComparisonResult] = {}

    async def compare_weather(self, request: ComparisonRequest) -> ComparisonResult:
        """Perform comprehensive weather comparison."""
        try:
            # Collect data based on time range
            if request.time_range == TimeRange.CURRENT:
                data_points = await self.data_collector.collect_current_data(request.locations)
            elif request.time_range in [TimeRange.HOURLY_24H, TimeRange.DAILY_7D, TimeRange.DAILY_14D]:
                if request.include_forecast:
                    days = 1 if request.time_range == TimeRange.HOURLY_24H else (
                        7 if request.time_range == TimeRange.DAILY_7D else 14
                    )
                    data_points = await self.data_collector.collect_forecast_data(request.locations, days)
                else:
                    data_points = await self.data_collector.collect_current_data(request.locations)
            else:
                # Historical data
                start_date = request.start_date or datetime.now() - timedelta(days=30)
                end_date = request.end_date or datetime.now()
                data_points = await self.data_collector.collect_historical_data(
                    request.locations, start_date, end_date
                )
            
            # Calculate statistics for each metric
            statistics_list = []
            for metric in request.metrics:
                stats = await self.statistics_calculator.calculate_basic_stats(data_points, metric)
                statistics_list.append(stats)
            
            # Generate chart configuration
            chart_config = await self._create_chart_config(request, data_points)
            
            # Generate insights
            result = ComparisonResult(
                request=request,
                data_points=data_points,
                chart_config=chart_config,
                statistics=statistics_list,
                insights=[],  # Will be filled below
                generated_at=datetime.now(),
                data_quality_score=self._calculate_data_quality_score(data_points, request.locations),
                missing_data_points=self._count_missing_data_points(data_points, request.locations)
            )
            
            insights = await self.insight_generator.generate_insights(result)
            recommendations = await self.insight_generator.generate_recommendations(result)
            result.insights = insights + recommendations
            
            return result
            
        except Exception as e:
            logger.error(f"Error in weather comparison: {e}")
            raise

    async def compare_current_weather(
        self,
        locations: List[ComparisonLocation],
        metrics: List[ComparisonMetric]
    ) -> ComparisonResult:
        """Compare current weather across locations."""
        request = ComparisonRequest(
            locations=locations,
            metrics=metrics,
            time_range=TimeRange.CURRENT,
            chart_type=ChartType.BAR
        )
        return await self.compare_weather(request)

    async def compare_forecasts(
        self,
        locations: List[ComparisonLocation],
        days: int = 7
    ) -> ComparisonResult:
        """Compare weather forecasts across locations."""
        request = ComparisonRequest(
            locations=locations,
            metrics=[ComparisonMetric.TEMPERATURE, ComparisonMetric.HUMIDITY],
            time_range=TimeRange.DAILY_7D if days <= 7 else TimeRange.DAILY_14D,
            chart_type=ChartType.LINE,
            include_forecast=True
        )
        return await self.compare_weather(request)

    async def get_location_suggestions(self, query: str) -> List[ComparisonLocation]:
        """Get location suggestions for comparison."""
        # This would typically integrate with a geocoding service
        # For now, return some sample locations
        sample_locations = [
            ComparisonLocation("New York", 40.7128, -74.0060, "US", "NY"),
            ComparisonLocation("London", 51.5074, -0.1278, "GB"),
            ComparisonLocation("Tokyo", 35.6762, 139.6503, "JP"),
            ComparisonLocation("Sydney", -33.8688, 151.2093, "AU"),
            ComparisonLocation("Paris", 48.8566, 2.3522, "FR")
        ]
        
        # Simple filtering based on query
        query_lower = query.lower()
        suggestions = [loc for loc in sample_locations if query_lower in loc.name.lower()]
        
        return suggestions[:5]  # Return top 5 suggestions

    async def save_comparison(self, result: ComparisonResult, name: str) -> str:
        """Save comparison results for later retrieval."""
        comparison_id = str(uuid.uuid4())
        self._saved_comparisons[comparison_id] = result
        return comparison_id

    async def load_comparison(self, comparison_id: str) -> Optional[ComparisonResult]:
        """Load previously saved comparison results."""
        return self._saved_comparisons.get(comparison_id)

    async def list_saved_comparisons(self) -> List[Dict[str, Any]]:
        """List all saved comparisons."""
        comparisons = []
        for comp_id, result in self._saved_comparisons.items():
            comparisons.append({
                "id": comp_id,
                "generated_at": result.generated_at.isoformat(),
                "locations": [loc.name for loc in result.request.locations],
                "metrics": [metric.value for metric in result.request.metrics],
                "time_range": result.request.time_range.value
            })
        return comparisons

    async def _create_chart_config(self, request: ComparisonRequest, data_points: List[WeatherDataPoint]) -> ChartConfiguration:
        """Create chart configuration from request and data."""
        series_list = []
        
        # Group data by location and metric
        for location in request.locations:
            for metric in request.metrics:
                location_data = [
                    point for point in data_points 
                    if point.location.name == location.name
                ]
                
                if location_data:
                    series_data = []
                    for point in location_data:
                        value = self.statistics_calculator._get_metric_value(point, metric)
                        if value is not None:
                            series_data.append((point.timestamp, value))
                    
                    if series_data:
                        series = ChartDataSeries(
                            name=f"{location.name} - {metric.value}",
                            data=series_data,
                            color=location.color,
                            unit=self._get_metric_unit(metric),
                            location=location
                        )
                        series_list.append(series)
        
        return ChartConfiguration(
            chart_type=request.chart_type,
            title=f"Weather Comparison - {', '.join([loc.name for loc in request.locations])}",
            x_axis_label="Time",
            y_axis_label=self._get_y_axis_label(request.metrics),
            series=series_list
        )

    def _get_metric_unit(self, metric: ComparisonMetric) -> str:
        """Get unit for a metric."""
        unit_map = {
            ComparisonMetric.TEMPERATURE: "°C",
            ComparisonMetric.HUMIDITY: "%",
            ComparisonMetric.PRESSURE: "hPa",
            ComparisonMetric.WIND_SPEED: "m/s",
            ComparisonMetric.PRECIPITATION: "mm",
            ComparisonMetric.UV_INDEX: "index",
            ComparisonMetric.VISIBILITY: "km",
            ComparisonMetric.FEELS_LIKE: "°C"
        }
        return unit_map.get(metric, "")

    def _get_y_axis_label(self, metrics: List[ComparisonMetric]) -> str:
        """Get Y-axis label for metrics."""
        if len(metrics) == 1:
            return f"{metrics[0].value.replace('_', ' ').title()} ({self._get_metric_unit(metrics[0])})"
        return "Value"

    def _calculate_data_quality_score(self, data_points: List[WeatherDataPoint], locations: List[ComparisonLocation]) -> float:
        """Calculate data quality score based on completeness."""
        if not locations:
            return 0.0
        
        expected_points = len(locations)
        actual_points = len(data_points)
        
        return min(actual_points / expected_points, 1.0)

    def _count_missing_data_points(self, data_points: List[WeatherDataPoint], locations: List[ComparisonLocation]) -> int:
        """Count missing data points."""
        expected_points = len(locations)
        actual_points = len(data_points)
        
        return max(expected_points - actual_points, 0)


def create_comparison_service(weather_api: IAsyncWeatherAPI) -> ComparisonService:
    """Factory function to create a complete comparison service."""
    data_collector = WeatherDataCollector(weather_api)
    chart_generator = PlotlyChartGenerator()
    statistics_calculator = StatisticsCalculator()
    insight_generator = InsightGenerator()
    
    return ComparisonService(
        data_collector=data_collector,
        chart_generator=chart_generator,
        statistics_calculator=statistics_calculator,
        insight_generator=insight_generator
    )