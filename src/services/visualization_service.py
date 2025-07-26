"""Weather Data Visualization Service for Processing Chart Data."""

# mypy: disable-error-code="arg-type,assignment"

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any

from src.models.weather_models import CurrentWeather, WeatherForecast


class WeatherVisualizationService:
    """Service for processing weather data for visualization."""

    def __init__(self):
        """Initialize the visualization service."""
        self.logger = logging.getLogger(__name__)

        # Store chart data for updates
        self.temperature_data: List[Tuple[datetime, float]] = []
        self.humidity_data: List[Tuple[datetime, float]] = []
        self.pressure_data: List[Tuple[datetime, float]] = []
        self.wind_data: List[Tuple[datetime, float]] = []

    def add_weather_data_point(self, weather: CurrentWeather) -> None:
        """Add a weather data point for tracking over time."""
        timestamp = datetime.now()

        # Add data points (keep last 24 hours)
        cutoff_time = timestamp - timedelta(hours=24)

        # Temperature data - convert Temperature object to float
        temp_value = weather.temperature.to_celsius()
        self.temperature_data.append((timestamp, temp_value))
        self.temperature_data = [
            (t, temp) for t, temp in self.temperature_data if t > cutoff_time
        ]

        # Humidity data
        if weather.humidity is not None:
            self.humidity_data.append((timestamp, float(weather.humidity)))
            self.humidity_data = [
                (t, hum) for t, hum in self.humidity_data if t > cutoff_time
            ]

        # Pressure data - convert AtmosphericPressure object to float
        if weather.pressure is not None:
            pressure_value = weather.pressure.value
            self.pressure_data.append((timestamp, pressure_value))
            self.pressure_data = [
                (t, press) for t, press in self.pressure_data if t > cutoff_time
            ]

        # Wind speed data - get from Wind object
        if weather.wind is not None and weather.wind.speed is not None:
            self.wind_data.append((timestamp, weather.wind.speed))
            self.wind_data = [
                (t, wind) for t, wind in self.wind_data if t > cutoff_time
            ]

    def get_temperature_trend_data(self) -> Dict[str, Any]:
        """Get temperature trend data for visualization."""
        if not self.temperature_data:
            return {
                "has_data": False,
                "title": "Temperature Trend (24h)",
                "placeholder_message": "No data available yet.\nWeather data will appear here\nafter collecting measurements."
            }

        # Extract data
        times = [t for t, _ in self.temperature_data]
        temps = [temp for _, temp in self.temperature_data]

        return {
            "has_data": True,
            "title": "Temperature Trend (24h)",
            "times": times,
            "temperatures": temps,
            "line_color": "#4a9eff",
            "xlabel": "Time",
            "ylabel": "Temperature (°C)",
            "chart_type": "line"
        }

    def get_weather_metrics_data(self) -> Dict[str, Any]:
        """Get current weather metrics data for visualization."""
        if not self.temperature_data:
            return {
                "has_data": False,
                "title": "Current Weather Metrics",
                "placeholder_message": "No data available yet.\nWeather metrics will appear here\nafter collecting measurements."
            }

        # Get latest values
        latest_temp = self.temperature_data[-1][1] if self.temperature_data else 0
        latest_humidity = self.humidity_data[-1][1] if self.humidity_data else 0
        latest_pressure = (
            (self.pressure_data[-1][1] / 10) if self.pressure_data else 0
        )  # Scale pressure
        latest_wind = self.wind_data[-1][1] if self.wind_data else 0

        # Data for bar chart
        metrics = [
            "Temperature\n(°C)",
            "Humidity\n(%)",
            "Pressure\n(x10 hPa)",
            "Wind Speed\n(m/s)",
        ]
        values = [latest_temp, latest_humidity, latest_pressure, latest_wind]
        colors = ["#ff6b4a", "#4a9eff", "#22c55e", "#f59e0b"]

        return {
            "has_data": True,
            "title": "Current Weather Metrics",
            "metrics": metrics,
            "values": values,
            "colors": colors,
            "ylabel": "Value",
            "chart_type": "bar"
        }

    def get_forecast_comparison_data(
        self, forecast: Optional[WeatherForecast] = None
    ) -> Dict[str, Any]:
        """Get forecast comparison data for visualization."""
        if not forecast or not forecast.forecast_days:
            return {
                "has_data": False,
                "title": "5-Day Temperature Forecast",
                "placeholder_message": "No forecast data available.\nForecast comparison will appear here\nafter loading weather data."
            }

        # Extract forecast data (first 5 days)
        days = []
        high_temps = []
        low_temps = []

        for i, day_forecast in enumerate(forecast.forecast_days[:5]):
            days.append(f"Day {i+1}")
            high_temps.append(day_forecast.temperature_high.to_celsius())
            low_temps.append(day_forecast.temperature_low.to_celsius())

        return {
            "has_data": True,
            "title": "5-Day Temperature Forecast",
            "days": days,
            "high_temps": high_temps,
            "low_temps": low_temps,
            "high_color": "#ff6b4a",
            "low_color": "#4a9eff",
            "xlabel": "Days",
            "ylabel": "Temperature (°C)",
            "chart_type": "grouped_bar",
            "bar_width": 0.35
        }

    def get_humidity_pressure_data(self) -> Dict[str, Any]:
        """Get humidity and pressure data for dual-axis visualization."""
        if not self.humidity_data and not self.pressure_data:
            return {
                "has_data": False,
                "title": "Humidity & Pressure Trends (24h)",
                "placeholder_message": "No atmospheric data available.\nHumidity and pressure trends\nwill appear after data collection."
            }

        humidity_series = None
        pressure_series = None

        # Process humidity data
        if self.humidity_data:
            times_hum = [t for t, _ in self.humidity_data]
            humidity_vals = [h for _, h in self.humidity_data]
            humidity_series = {
                "times": times_hum,
                "values": humidity_vals,
                "color": "#4a9eff",
                "label": "Humidity (%)",
                "ylabel": "Humidity (%)",
                "marker": "o"
            }

        # Process pressure data
        if self.pressure_data:
            times_press = [t for t, _ in self.pressure_data]
            pressure_vals = [p for _, p in self.pressure_data]
            pressure_series = {
                "times": times_press,
                "values": pressure_vals,
                "color": "#22c55e",
                "label": "Pressure (hPa)",
                "ylabel": "Pressure (hPa)",
                "marker": "s"
            }

        return {
            "has_data": True,
            "title": "Humidity & Pressure Trends (24h)",
            "xlabel": "Time",
            "humidity_series": humidity_series,
            "pressure_series": pressure_series,
            "chart_type": "dual_axis"
        }

    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of all collected data."""
        return {
            "temperature_points": len(self.temperature_data),
            "humidity_points": len(self.humidity_data),
            "pressure_points": len(self.pressure_data),
            "wind_points": len(self.wind_data),
            "data_time_range": self._get_time_range(),
            "latest_values": self._get_latest_values()
        }

    def _get_time_range(self) -> Optional[Dict[str, datetime]]:
        """Get the time range of collected data."""
        all_times = []

        if self.temperature_data:
            all_times.extend([t for t, _ in self.temperature_data])
        if self.humidity_data:
            all_times.extend([t for t, _ in self.humidity_data])
        if self.pressure_data:
            all_times.extend([t for t, _ in self.pressure_data])
        if self.wind_data:
            all_times.extend([t for t, _ in self.wind_data])

        if not all_times:
            return None

        return {
            "earliest": min(all_times),
            "latest": max(all_times)
        }

    def _get_latest_values(self) -> Dict[str, Optional[float]]:
        """Get the latest values for all metrics."""
        return {
            "temperature": self.temperature_data[-1][1] if self.temperature_data else None,
            "humidity": self.humidity_data[-1][1] if self.humidity_data else None,
            "pressure": self.pressure_data[-1][1] if self.pressure_data else None,
            "wind_speed": self.wind_data[-1][1] if self.wind_data else None
        }

    def clear_old_data(self, hours: int = 24) -> None:
        """Clear data older than specified hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)

        self.temperature_data = [
            (t, temp) for t, temp in self.temperature_data if t > cutoff_time
        ]
        self.humidity_data = [
            (t, hum) for t, hum in self.humidity_data if t > cutoff_time
        ]
        self.pressure_data = [
            (t, press) for t, press in self.pressure_data if t > cutoff_time
        ]
        self.wind_data = [
            (t, wind) for t, wind in self.wind_data if t > cutoff_time
        ]

    def has_sufficient_data(self, min_points: int = 2) -> bool:
        """Check if there's sufficient data for meaningful visualization."""
        return (
            len(self.temperature_data) >= min_points or
            len(self.humidity_data) >= min_points or
            len(self.pressure_data) >= min_points or
            len(self.wind_data) >= min_points
        )
