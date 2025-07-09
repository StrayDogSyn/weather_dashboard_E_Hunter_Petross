"""Weather Data Visualization Service with Charts and Graphs."""

# mypy: disable-error-code="arg-type,assignment"

import logging
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk
from typing import Dict, List, Optional, Tuple

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure

    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print(
        "Matplotlib not available. Please install it with: pip install matplotlib numpy"
    )

from src.models.weather_models import CurrentWeather, WeatherForecast
from src.ui.gui_interface import GlassmorphicFrame, GlassmorphicStyle


class WeatherVisualizationService:
    """Service for creating weather data visualizations and charts."""

    def __init__(self):
        """Initialize the visualization service."""
        self.logger = logging.getLogger(__name__)

        # Configure matplotlib for dark theme if available
        if MATPLOTLIB_AVAILABLE:
            plt.style.use("dark_background")  # type: ignore[possibly-unbound]

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

    def create_temperature_trend_chart(self, parent: tk.Widget) -> tk.Widget:
        """Create a temperature trend line chart."""
        frame = GlassmorphicFrame(parent, bg_color="#1a1a2e", elevated=True)

        if not MATPLOTLIB_AVAILABLE:
            label = tk.Label(
                frame,
                text="📈 Temperature Trend\n\nMatplotlib not available.\nPlease install matplotlib:\npip install matplotlib numpy",
                font=("Segoe UI", 12),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg="#1a1a2e",
                justify=tk.CENTER,
            )
            label.pack(expand=True)
            return frame

        if not self.temperature_data:
            # Show placeholder if no data
            label = tk.Label(
                frame,
                text="📈 Temperature Trend\n\nNo data available yet.\nWeather data will appear here\nafter collecting measurements.",
                font=("Segoe UI", 12),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg="#1a1a2e",
                justify=tk.CENTER,
            )
            label.pack(expand=True)
            return frame

        # Create matplotlib figure
        fig = Figure(figsize=(8, 4), dpi=100, facecolor="#1a1a2e")  # type: ignore[possibly-unbound]
        ax = fig.add_subplot(111, facecolor="#1a1a2e")

        # Extract data
        times = [t for t, _ in self.temperature_data]
        temps = [temp for _, temp in self.temperature_data]

        # Plot temperature line - matplotlib handles datetime objects automatically
        ax.plot(times, temps, color="#4a9eff", linewidth=2, marker="o", markersize=4)  # type: ignore[arg-type]
        ax.set_title("Temperature Trend (24h)", color="white", fontsize=14, pad=20)
        ax.set_xlabel("Time", color="white")
        ax.set_ylabel("Temperature (°C)", color="white")
        ax.grid(True, alpha=0.3, color="#333333")

        # Style the axes
        ax.tick_params(colors="white", labelsize=9)
        ax.spines["bottom"].set_color("white")
        ax.spines["top"].set_color("white")
        ax.spines["right"].set_color("white")
        ax.spines["left"].set_color("white")

        # Format x-axis for time
        fig.autofmt_xdate()
        if MATPLOTLIB_AVAILABLE:
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)  # type: ignore[possibly-unbound]

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, frame)  # type: ignore[possibly-unbound]
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        return frame

    def create_weather_metrics_chart(self, parent: tk.Widget) -> tk.Widget:
        """Create a multi-metric bar chart."""
        frame = GlassmorphicFrame(parent, bg_color="#1a1a2e", elevated=True)

        if not self.temperature_data:
            # Show placeholder if no data
            label = tk.Label(
                frame,
                text="📊 Weather Metrics\n\nNo data available yet.\nWeather metrics will appear here\nafter collecting measurements.",
                font=("Segoe UI", 12),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg="#1a1a2e",
                justify=tk.CENTER,
            )
            label.pack(expand=True)
            return frame

        # Create matplotlib figure
        fig = Figure(figsize=(8, 4), dpi=100, facecolor="#1a1a2e")  # type: ignore[possibly-unbound]
        ax = fig.add_subplot(111, facecolor="#1a1a2e")

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

        # Create bar chart
        bars = ax.bar(
            metrics, values, color=colors, alpha=0.8, edgecolor="white", linewidth=1
        )

        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                height + max(values) * 0.01,
                f"{value:.1f}",
                ha="center",
                va="bottom",
                color="white",
                fontweight="bold",
            )

        ax.set_title("Current Weather Metrics", color="white", fontsize=14, pad=20)
        ax.set_ylabel("Value", color="white")
        ax.grid(True, alpha=0.3, color="#333333", axis="y")

        # Style the axes
        ax.tick_params(colors="white", labelsize=9)
        ax.spines["bottom"].set_color("white")
        ax.spines["top"].set_color("white")
        ax.spines["right"].set_color("white")
        ax.spines["left"].set_color("white")

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, frame)  # type: ignore[possibly-unbound]
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        return frame

    def create_forecast_comparison_chart(
        self, parent: tk.Widget, forecast: Optional[WeatherForecast] = None
    ) -> tk.Widget:
        """Create a forecast comparison chart."""
        frame = GlassmorphicFrame(parent, bg_color="#1a1a2e", elevated=True)

        if not MATPLOTLIB_AVAILABLE:
            label = tk.Label(
                frame,
                text="🌤️ 5-Day Forecast\n\nMatplotlib not available.\nPlease install matplotlib:\npip install matplotlib numpy",
                font=("Segoe UI", 12),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg="#1a1a2e",
                justify=tk.CENTER,
            )
            label.pack(expand=True)
            return frame

        if not forecast or not forecast.forecast_days:
            # Show placeholder if no data
            label = tk.Label(
                frame,
                text="🌤️ 5-Day Forecast\n\nNo forecast data available.\nForecast comparison will appear here\nafter loading weather data.",
                font=("Segoe UI", 12),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg="#1a1a2e",
                justify=tk.CENTER,
            )
            label.pack(expand=True)
            return frame

        # Create matplotlib figure
        fig = Figure(figsize=(8, 4), dpi=100, facecolor="#1a1a2e")  # type: ignore[possibly-unbound]
        ax = fig.add_subplot(111, facecolor="#1a1a2e")

        # Extract forecast data (first 5 days)
        days = []
        high_temps = []
        low_temps = []

        for i, day_forecast in enumerate(forecast.forecast_days[:5]):
            days.append(f"Day {i+1}")
            high_temps.append(day_forecast.temperature_high.to_celsius())
            low_temps.append(day_forecast.temperature_low.to_celsius())

        # Create grouped bar chart using range if numpy not available
        try:
            x = np.arange(len(days))  # type: ignore[misc]
        except NameError:
            x = list(range(len(days)))  # type: ignore[assignment]
        width = 0.35

        bars1 = ax.bar(
            [xi - width / 2 for xi in x],
            high_temps,
            width,
            label="High",
            color="#ff6b4a",
            alpha=0.8,
        )
        bars2 = ax.bar(
            [xi + width / 2 for xi in x],
            low_temps,
            width,
            label="Low",
            color="#4a9eff",
            alpha=0.8,
        )

        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.5,
                    f"{height:.0f}°",
                    ha="center",
                    va="bottom",
                    color="white",
                    fontsize=9,
                )

        ax.set_title("5-Day Temperature Forecast", color="white", fontsize=14, pad=20)
        ax.set_xlabel("Days", color="white")
        ax.set_ylabel("Temperature (°C)", color="white")
        ax.set_xticks(x)
        ax.set_xticklabels(days)
        ax.legend(facecolor="#2a2a2a", edgecolor="white", labelcolor="white")
        ax.grid(True, alpha=0.3, color="#333333", axis="y")

        # Style the axes
        ax.tick_params(colors="white", labelsize=9)
        ax.spines["bottom"].set_color("white")
        ax.spines["top"].set_color("white")
        ax.spines["right"].set_color("white")
        ax.spines["left"].set_color("white")

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, frame)  # type: ignore[possibly-unbound]
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        return frame

    def create_humidity_pressure_chart(self, parent: tk.Widget) -> tk.Widget:
        """Create a combined humidity and pressure chart."""
        frame = GlassmorphicFrame(parent, bg_color="#1a1a2e", elevated=True)

        if not self.humidity_data and not self.pressure_data:
            # Show placeholder if no data
            label = tk.Label(
                frame,
                text="💧 Humidity & Pressure\n\nNo atmospheric data available.\nHumidity and pressure trends\nwill appear after data collection.",
                font=("Segoe UI", 12),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg="#1a1a2e",
                justify=tk.CENTER,
            )
            label.pack(expand=True)
            return frame

        # Create matplotlib figure with dual y-axes
        fig = Figure(figsize=(8, 4), dpi=100, facecolor="#1a1a2e")  # type: ignore[possibly-unbound]
        ax1 = fig.add_subplot(111, facecolor="#1a1a2e")
        ax2 = ax1.twinx()

        # Plot humidity
        if self.humidity_data:
            times_hum = [t for t, _ in self.humidity_data]
            humidity_vals = [h for _, h in self.humidity_data]
            line1 = ax1.plot(
                times_hum,  # type: ignore[arg-type]
                humidity_vals,
                color="#4a9eff",
                linewidth=2,
                marker="o",
                markersize=3,
                label="Humidity (%)",
            )
            ax1.set_ylabel("Humidity (%)", color="#4a9eff")
            ax1.tick_params(axis="y", labelcolor="#4a9eff")

        # Plot pressure
        if self.pressure_data:
            times_press = [t for t, _ in self.pressure_data]
            pressure_vals = [p for _, p in self.pressure_data]
            line2 = ax2.plot(
                times_press,  # type: ignore[arg-type]
                pressure_vals,
                color="#22c55e",
                linewidth=2,
                marker="s",
                markersize=3,
                label="Pressure (hPa)",
            )
            ax2.set_ylabel("Pressure (hPa)", color="#22c55e")
            ax2.tick_params(axis="y", labelcolor="#22c55e")

        ax1.set_title(
            "Humidity & Pressure Trends (24h)", color="white", fontsize=14, pad=20
        )
        ax1.set_xlabel("Time", color="white")
        ax1.grid(True, alpha=0.3, color="#333333")

        # Style the axes
        ax1.tick_params(colors="white", labelsize=9)
        ax1.spines["bottom"].set_color("white")
        ax1.spines["top"].set_color("white")
        ax1.spines["left"].set_color("#4a9eff")
        ax2.spines["right"].set_color("#22c55e")

        # Format x-axis for time
        fig.autofmt_xdate()

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, frame)  # type: ignore[possibly-unbound]
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        return frame
