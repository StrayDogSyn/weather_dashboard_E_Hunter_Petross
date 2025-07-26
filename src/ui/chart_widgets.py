"""
Chart Widgets for Weather Dashboard UI.

This module contains UI components for displaying weather charts and visualizations,
properly separated from the business logic visualization service.
"""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .styling import GlassmorphicStyle
from .components import GlassmorphicFrame
from src.models.weather_models import CurrentWeather, WeatherForecast


class WeatherChartWidget(GlassmorphicFrame):
    """Widget for displaying weather charts."""

    def __init__(self, parent, chart_type: str = "temperature", **kwargs):
        super().__init__(parent, bg_color="#1a1a2e", elevated=True, **kwargs)
        self.chart_type = chart_type
        self.logger = logging.getLogger(__name__)

        if MATPLOTLIB_AVAILABLE:
            plt.style.use("dark_background")
            self.setup_chart()
        else:
            self.setup_no_chart_message()

    def setup_chart(self):
        """Setup the matplotlib chart."""
        # Chart title
        title_label = tk.Label(
            self,
            text=f"{self.chart_type.title()} Chart",
            font=("Segoe UI", 14, "bold"),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color,
        )
        title_label.pack(pady=(10, 5))

        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 4), facecolor="#1a1a2e")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1a1a2e")

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg="#1a1a2e")
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def setup_no_chart_message(self):
        """Setup message when matplotlib is not available."""
        message_label = tk.Label(
            self,
            text="Charts require matplotlib.\nRun: pip install matplotlib numpy",
            font=("Segoe UI", 12),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color,
            justify=tk.CENTER,
        )
        message_label.pack(expand=True, pady=20)

    def update_chart_data(self, data: List[Tuple[datetime, float]],
                          title: str = None, ylabel: str = None):
        """Update the chart with new data."""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'ax'):
            return

        self.ax.clear()

        if not data:
            self.ax.text(0.5, 0.5, 'No data available',
                         transform=self.ax.transAxes, ha='center', va='center',
                         color=GlassmorphicStyle.TEXT_SECONDARY)
            self.canvas.draw()
            return

        # Extract timestamps and values
        timestamps, values = zip(*data)

        # Plot the data
        self.ax.plot(timestamps, values,
                     color=GlassmorphicStyle.ACCENT, linewidth=2, marker='o')

        # Customize appearance
        self.ax.set_title(title or f"{self.chart_type.title()} Over Time",
                          color=GlassmorphicStyle.TEXT_PRIMARY)
        self.ax.set_ylabel(ylabel or self.chart_type.title(),
                           color=GlassmorphicStyle.TEXT_SECONDARY)
        self.ax.tick_params(colors=GlassmorphicStyle.TEXT_SECONDARY)

        # Format x-axis for time
        self.fig.autofmt_xdate()

        # Tight layout
        self.fig.tight_layout()

        # Refresh canvas
        self.canvas.draw()


class ForecastChartWidget(GlassmorphicFrame):
    """Widget for displaying forecast charts."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg_color="#1a1a2e", elevated=True, **kwargs)
        self.logger = logging.getLogger(__name__)

        if MATPLOTLIB_AVAILABLE:
            plt.style.use("dark_background")
            self.setup_chart()
        else:
            self.setup_no_chart_message()

    def setup_chart(self):
        """Setup the forecast chart."""
        # Chart title
        title_label = tk.Label(
            self,
            text="5-Day Forecast",
            font=("Segoe UI", 14, "bold"),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color,
        )
        title_label.pack(pady=(10, 5))

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 6), facecolor="#1a1a2e")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1a1a2e")

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg="#1a1a2e")
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def setup_no_chart_message(self):
        """Setup message when matplotlib is not available."""
        message_label = tk.Label(
            self,
            text="Charts require matplotlib.\nRun: pip install matplotlib numpy",
            font=("Segoe UI", 12),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color,
            justify=tk.CENTER,
        )
        message_label.pack(expand=True, pady=20)

    def update_forecast_chart(self, forecast: WeatherForecast):
        """Update chart with forecast data."""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'ax'):
            return

        self.ax.clear()

        if not forecast or not forecast.daily_forecasts:
            self.ax.text(0.5, 0.5, 'No forecast data available',
                         transform=self.ax.transAxes, ha='center', va='center',
                         color=GlassmorphicStyle.TEXT_SECONDARY)
            self.canvas.draw()
            return

        # Extract data
        days = []
        highs = []
        lows = []

        for day_forecast in forecast.daily_forecasts[:5]:  # 5 days
            days.append(day_forecast.date.strftime('%m/%d'))
            highs.append(day_forecast.high_temp.to_celsius())
            lows.append(day_forecast.low_temp.to_celsius())

        # Create bar chart
        x = range(len(days))
        width = 0.4

        self.ax.bar([i - width/2 for i in x], highs, width,
                    label='High', color=GlassmorphicStyle.ACCENT_SECONDARY, alpha=0.8)
        self.ax.bar([i + width/2 for i in x], lows, width,
                    label='Low', color=GlassmorphicStyle.ACCENT, alpha=0.8)

        # Customize appearance
        self.ax.set_title('5-Day Temperature Forecast',
                          color=GlassmorphicStyle.TEXT_PRIMARY)
        self.ax.set_ylabel('Temperature (°C)',
                          color=GlassmorphicStyle.TEXT_SECONDARY)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(days)
        self.ax.tick_params(colors=GlassmorphicStyle.TEXT_SECONDARY)
        self.ax.legend()

        # Tight layout
        self.fig.tight_layout()

        # Refresh canvas
        self.canvas.draw()


class ComparisonChartWidget(GlassmorphicFrame):
    """Widget for displaying city comparison charts."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg_color="#1a1a2e", elevated=True, **kwargs)
        self.logger = logging.getLogger(__name__)

        if MATPLOTLIB_AVAILABLE:
            plt.style.use("dark_background")
            self.setup_chart()
        else:
            self.setup_no_chart_message()

    def setup_chart(self):
        """Setup the comparison chart."""
        # Chart title
        title_label = tk.Label(
            self,
            text="City Comparison",
            font=("Segoe UI", 14, "bold"),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color,
        )
        title_label.pack(pady=(10, 5))

        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), facecolor="#1a1a2e")
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor("#1a1a2e")

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.configure(bg="#1a1a2e")
        canvas_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def setup_no_chart_message(self):
        """Setup message when matplotlib is not available."""
        message_label = tk.Label(
            self,
            text="Charts require matplotlib.\nRun: pip install matplotlib numpy",
            font=("Segoe UI", 12),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=self.bg_color,
            justify=tk.CENTER,
        )
        message_label.pack(expand=True, pady=20)

    def update_comparison_chart(self, city1_data: dict, city2_data: dict):
        """Update chart with comparison data."""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'ax'):
            return

        self.ax.clear()

        if not city1_data or not city2_data:
            self.ax.text(0.5, 0.5, 'No comparison data available',
                        transform=self.ax.transAxes, ha='center', va='center',
                        color=GlassmorphicStyle.TEXT_SECONDARY)
            self.canvas.draw()
            return

        # Extract comparison metrics
        metrics = ['Temperature', 'Humidity', 'Wind Speed']
        city1_values = [
            city1_data.get('temperature', 0),
            city1_data.get('humidity', 0),
            city1_data.get('wind_speed', 0)
        ]
        city2_values = [
            city2_data.get('temperature', 0),
            city2_data.get('humidity', 0),
            city2_data.get('wind_speed', 0)
        ]

        # Create grouped bar chart
        x = range(len(metrics))
        width = 0.35

        self.ax.bar([i - width/2 for i in x], city1_values, width,
                   label=city1_data.get('name', 'City 1'),
                   color=GlassmorphicStyle.ACCENT, alpha=0.8)
        self.ax.bar([i + width/2 for i in x], city2_values, width,
                   label=city2_data.get('name', 'City 2'),
                   color=GlassmorphicStyle.ACCENT_SECONDARY, alpha=0.8)

        # Customize appearance
        self.ax.set_title('Weather Comparison',
                         color=GlassmorphicStyle.TEXT_PRIMARY)
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(metrics)
        self.ax.tick_params(colors=GlassmorphicStyle.TEXT_SECONDARY)
        self.ax.legend()

        # Tight layout
        self.fig.tight_layout()

        # Refresh canvas
        self.canvas.draw()
