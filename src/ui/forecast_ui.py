"""
Advanced Forecast UI Components for Weather Dashboard

This module provides enhanced UI components for displaying ML-powered weather
forecasts with confidence intervals, prediction explanations, and interactive
visualization features.
"""

import asyncio
import logging
import threading
import tkinter as tk
from datetime import datetime
from datetime import timedelta
from tkinter import messagebox
from tkinter import ttk
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from ..models.predictive_models import PredictionResult
from ..services.model_integration_service import IntegratedForecast
from ..services.model_integration_service import ModelIntegrationService
from .components.responsive_layout import ResponsiveSpacing


class ForecastVisualizationFrame(ttk.Frame):
    """Frame for advanced forecast visualization with ML predictions."""

    def __init__(self, parent, integration_service: ModelIntegrationService):
        """Initialize the forecast visualization frame.

        Args:
            parent: Parent widget
            integration_service: Model integration service
        """
        super().__init__(parent)
        self.integration_service = integration_service
        self.logger = logging.getLogger(__name__)
        # Use ResponsiveSpacing class attributes directly

        # Current forecast data
        self.current_forecast = None
        self.current_city = ""

        # Create UI components
        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        """Create all UI widgets for forecast visualization."""
        # Title and controls
        self.title_frame = ttk.Frame(self)
        self.title_label = ttk.Label(
            self.title_frame,
            text="Advanced Weather Forecast",
            font=("Arial", 16, "bold"),
        )

        # Forecast options
        self.options_frame = ttk.LabelFrame(self, text="Forecast Options")

        # City selection
        self.city_label = ttk.Label(self.options_frame, text="City:")
        self.city_var = tk.StringVar(value="London")
        self.city_entry = ttk.Entry(
            self.options_frame, textvariable=self.city_var, width=20
        )

        # Days selection
        self.days_label = ttk.Label(self.options_frame, text="Days:")
        self.days_var = tk.IntVar(value=5)
        self.days_spin = ttk.Spinbox(
            self.options_frame, from_=1, to=7, textvariable=self.days_var, width=5
        )

        # ML predictions toggle
        self.ml_var = tk.BooleanVar(value=True)
        self.ml_check = ttk.Checkbutton(
            self.options_frame, text="Include ML Predictions", variable=self.ml_var
        )

        # Generate forecast button
        self.generate_btn = ttk.Button(
            self.options_frame,
            text="Generate Forecast",
            command=self._generate_forecast,
        )

        # Refresh button
        self.refresh_btn = ttk.Button(
            self.options_frame, text="Refresh", command=self._refresh_forecast
        )

        # Forecast display area
        self.forecast_notebook = ttk.Notebook(self)

        # Temperature chart tab
        self.temp_frame = ttk.Frame(self.forecast_notebook)
        self.forecast_notebook.add(self.temp_frame, text="Temperature Forecast")

        # Confidence chart tab
        self.confidence_frame = ttk.Frame(self.forecast_notebook)
        self.forecast_notebook.add(self.confidence_frame, text="Confidence Analysis")

        # Model comparison tab
        self.comparison_frame = ttk.Frame(self.forecast_notebook)
        self.forecast_notebook.add(self.comparison_frame, text="Model Comparison")

        # Details tab
        self.details_frame = ttk.Frame(self.forecast_notebook)
        self.forecast_notebook.add(self.details_frame, text="Forecast Details")

        # Status bar
        self.status_frame = ttk.Frame(self)
        self.status_var = tk.StringVar(value="Ready to generate forecast")
        self.status_label = ttk.Label(self.status_frame, textvariable=self.status_var)

        # Progress bar
        self.progress = ttk.Progressbar(self.status_frame, mode="indeterminate")

        # Create chart canvases
        self._create_chart_canvases()

        # Create details widgets
        self._create_details_widgets()

    def _create_chart_canvases(self):
        """Create matplotlib canvases for charts."""
        # Temperature forecast chart
        self.temp_fig = Figure(figsize=(12, 6), dpi=100)
        self.temp_canvas = FigureCanvasTkAgg(self.temp_fig, self.temp_frame)
        self.temp_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Confidence analysis chart
        self.conf_fig = Figure(figsize=(12, 6), dpi=100)
        self.conf_canvas = FigureCanvasTkAgg(self.conf_fig, self.confidence_frame)
        self.conf_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Model comparison chart
        self.comp_fig = Figure(figsize=(12, 6), dpi=100)
        self.comp_canvas = FigureCanvasTkAgg(self.comp_fig, self.comparison_frame)
        self.comp_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _create_details_widgets(self):
        """Create widgets for forecast details display."""
        # Scrollable text area for detailed information
        self.details_scroll_frame = ttk.Frame(self.details_frame)
        self.details_scroll_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=ResponsiveSpacing.SMALL,
            pady=ResponsiveSpacing.SMALL,
        )

        # Text widget with scrollbar
        self.details_text = tk.Text(
            self.details_scroll_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Courier", 10),
        )

        self.details_scrollbar = ttk.Scrollbar(
            self.details_scroll_frame,
            orient=tk.VERTICAL,
            command=self.details_text.yview,
        )
        self.details_text.configure(yscrollcommand=self.details_scrollbar.set)

        self.details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Export buttons
        self.export_frame = ttk.Frame(self.details_frame)
        self.export_frame.pack(
            fill=tk.X, padx=ResponsiveSpacing.SMALL, pady=ResponsiveSpacing.SMALL
        )

        self.export_json_btn = ttk.Button(
            self.export_frame, text="Export JSON", command=self._export_json
        )
        self.export_json_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.export_chart_btn = ttk.Button(
            self.export_frame, text="Export Chart", command=self._export_chart
        )
        self.export_chart_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.model_explanation_btn = ttk.Button(
            self.export_frame,
            text="Model Explanation",
            command=self._show_model_explanation,
        )
        self.model_explanation_btn.pack(side=tk.LEFT)

    def _setup_layout(self):
        """Setup the layout of all widgets."""
        # Title
        self.title_frame.pack(
            fill=tk.X, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.SMALL
        )
        self.title_label.pack()

        # Options
        self.options_frame.pack(
            fill=tk.X, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.SMALL
        )

        # City input
        self.city_label.grid(
            row=0,
            column=0,
            padx=ResponsiveSpacing.SMALL,
            pady=ResponsiveSpacing.SMALL,
            sticky=tk.W,
        )
        self.city_entry.grid(
            row=0,
            column=1,
            padx=ResponsiveSpacing.SMALL,
            pady=ResponsiveSpacing.SMALL,
            sticky=tk.W,
        )

        # Days input
        self.days_label.grid(
            row=0,
            column=2,
            padx=ResponsiveSpacing.SMALL,
            pady=ResponsiveSpacing.SMALL,
            sticky=tk.W,
        )
        self.days_spin.grid(
            row=0,
            column=3,
            padx=ResponsiveSpacing.SMALL,
            pady=ResponsiveSpacing.SMALL,
            sticky=tk.W,
        )

        # ML checkbox
        self.ml_check.grid(
            row=0,
            column=4,
            padx=ResponsiveSpacing.MEDIUM,
            pady=ResponsiveSpacing.SMALL,
            sticky=tk.W,
        )

        # Buttons
        self.generate_btn.grid(
            row=0, column=5, padx=ResponsiveSpacing.SMALL, pady=ResponsiveSpacing.SMALL
        )
        self.refresh_btn.grid(
            row=0, column=6, padx=ResponsiveSpacing.SMALL, pady=ResponsiveSpacing.SMALL
        )

        # Forecast display
        self.forecast_notebook.pack(
            fill=tk.BOTH,
            expand=True,
            padx=ResponsiveSpacing.MEDIUM,
            pady=ResponsiveSpacing.SMALL,
        )

        # Status bar
        self.status_frame.pack(
            fill=tk.X, padx=ResponsiveSpacing.MEDIUM, pady=ResponsiveSpacing.SMALL
        )
        self.status_label.pack(side=tk.LEFT)
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))

    def _generate_forecast(self):
        """Generate enhanced forecast with ML predictions."""
        city = self.city_var.get().strip()
        days = self.days_var.get()
        include_ml = self.ml_var.get()

        if not city:
            messagebox.showerror("Error", "Please enter a city name")
            return

        # Run async function in thread
        def run_async():
            try:
                self._set_loading(True)
                self.status_var.set(f"Generating forecast for {city}...")

                # Create new event loop for thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Generate integrated forecast
                forecast = loop.run_until_complete(
                    self.integration_service.get_enhanced_forecast(
                        city=city, days=days, include_ml_predictions=include_ml
                    )
                )

                self.current_forecast = forecast
                self.current_city = city

                # Update UI in main thread
                self.after(0, self._update_all_displays)
                self.after(
                    0,
                    lambda: self.status_var.set(
                        f"Forecast generated for {city} - Confidence: {forecast.confidence_score: .1%}"
                    ),
                )

            except Exception as e:
                self.logger.error(f"Error generating forecast: {e}")
                self.after(
                    0,
                    lambda e=e: messagebox.showerror(
                        "Error", f"Failed to generate forecast: {str(e)}"
                    ),
                )
                self.after(0, lambda: self.status_var.set("Error generating forecast"))
            finally:
                self.after(0, lambda: self._set_loading(False))

        # Start in background thread
        thread = threading.Thread(target=run_async)
        thread.daemon = True
        thread.start()

    def _update_all_displays(self):
        """Update all display components."""
        self._update_temperature_chart()
        self._update_confidence_chart()
        self._update_comparison_chart()
        self._update_details_display()

    def _refresh_forecast(self):
        """Refresh the current forecast."""
        if self.current_city:
            # Clear cache and regenerate
            self.integration_service.clear_prediction_cache()
            self._generate_forecast()
        else:
            messagebox.showinfo(
                "Info", "No forecast to refresh. Generate a forecast first."
            )

    def _set_loading(self, loading: bool):
        """Set loading state for UI elements."""
        if loading:
            self.progress.start()
            self.generate_btn.configure(state="disabled")
            self.refresh_btn.configure(state="disabled")
        else:
            self.progress.stop()
            self.generate_btn.configure(state="normal")
            self.refresh_btn.configure(state="normal")

    def _update_temperature_chart(self):
        """Update the temperature forecast chart."""
        if not self.current_forecast:
            return

        self.temp_fig.clear()
        ax = self.temp_fig.add_subplot(111)

        # Prepare data
        days = list(range(len(self.current_forecast.ml_predictions or [])))
        dates = [(datetime.now() + timedelta(days=i)).strftime("%m/%d") for i in days]

        # API temperatures (if available)
        api_temps = []
        api_forecast = self.current_forecast.api_forecast or {}
        forecast_days = api_forecast.get("forecast_days", [])
        if not isinstance(forecast_days, list):
            forecast_days = []
        for day_data in forecast_days:
            temp_data = day_data.get("temperature", {})
            if isinstance(temp_data, dict):
                api_temps.append(temp_data.get("max", 0))
            else:
                api_temps.append(float(temp_data) if temp_data else 0)

        # ML predictions
        ml_predictions = getattr(self.current_forecast, "ml_predictions", []) or []
        ml_temps = [pred.predicted_temperature for pred in ml_predictions]
        confidence_intervals = [pred.confidence_interval for pred in ml_predictions]

        # Plot API forecast
        if api_temps and len(api_temps) == len(days):
            ax.plot(
                days, api_temps, "o-", label="API Forecast", color="blue", linewidth=2
            )

        # Plot ML predictions
        if ml_temps:
            ax.plot(
                days, ml_temps, "s-", label="ML Prediction", color="red", linewidth=2
            )

            # Add confidence intervals
            if confidence_intervals:
                lower_bounds = [ci[0] for ci in confidence_intervals]
                upper_bounds = [ci[1] for ci in confidence_intervals]
                ax.fill_between(
                    days,
                    lower_bounds,
                    upper_bounds,
                    alpha=0.3,
                    color="red",
                    label="Confidence Interval",
                )

        # Hybrid forecast (if available)
        hybrid_temps = []
        hybrid_forecast = self.current_forecast.hybrid_forecast or {}
        hybrid_days = hybrid_forecast.get("forecast_days", [])
        if not isinstance(hybrid_days, list):
            hybrid_days = []
        for day_data in hybrid_days:
            hybrid_temp = day_data.get("temperature", {}).get("ml_enhanced")
            if hybrid_temp:
                hybrid_temps.append(hybrid_temp)

        if hybrid_temps and len(hybrid_temps) == len(days):
            ax.plot(
                days,
                hybrid_temps,
                "^-",
                label="Hybrid Forecast",
                color="green",
                linewidth=2,
            )

        # Formatting
        ax.set_xlabel("Days from Today")
        ax.set_ylabel("Temperature (°C)")
        ax.set_title(f"Temperature Forecast for {self.current_city}")
        ax.set_xticks(days)
        ax.set_xticklabels(dates)
        ax.legend()
        ax.grid(True, alpha=0.3)

        self.temp_fig.tight_layout()
        self.temp_canvas.draw()

    def _update_confidence_chart(self):
        """Update the confidence analysis chart."""
        ml_predictions = (
            self.current_forecast.ml_predictions if self.current_forecast else []
        )
        if not self.current_forecast or not ml_predictions:
            return

        self.conf_fig.clear()

        # Create subplots for different confidence metrics
        ax1 = self.conf_fig.add_subplot(211)
        ax2 = self.conf_fig.add_subplot(212)

        days = list(range(len(ml_predictions)))
        dates = [(datetime.now() + timedelta(days=i)).strftime("%m/%d") for i in days]

        # Prediction accuracy over time
        accuracies = [pred.prediction_accuracy for pred in ml_predictions]
        ax1.bar(days, accuracies, alpha=0.7, color="skyblue")
        ax1.set_ylabel("Prediction Accuracy")
        ax1.set_title("ML Model Confidence by Day")
        ax1.set_xticks(days)
        ax1.set_xticklabels(dates)
        ax1.set_ylim(0, 1)

        # Confidence interval width (uncertainty)
        interval_widths = [
            pred.confidence_interval[1] - pred.confidence_interval[0]
            for pred in ml_predictions
        ]
        ax2.bar(days, interval_widths, alpha=0.7, color="orange")
        ax2.set_ylabel("Uncertainty (°C)")
        ax2.set_xlabel("Days from Today")
        ax2.set_title("Prediction Uncertainty by Day")
        ax2.set_xticks(days)
        ax2.set_xticklabels(dates)

        self.conf_fig.tight_layout()
        self.conf_canvas.draw()

    def _update_comparison_chart(self):
        """Update the model comparison chart."""
        if not self.current_forecast:
            return

        self.comp_fig.clear()
        ax = self.comp_fig.add_subplot(111)

        # Get model status from integration service
        service_status = self.integration_service.get_service_status()

        if service_status.prediction_accuracy:
            models = list(service_status.prediction_accuracy.keys())
            accuracies = list(service_status.prediction_accuracy.values())

            # Create bar chart of model accuracies
            bars = ax.bar(models, accuracies, alpha=0.7)

            # Color bars based on performance
            for bar, acc in zip(bars, accuracies):
                if acc >= 0.8:
                    bar.set_color("green")
                elif acc >= 0.6:
                    bar.set_color("orange")
                else:
                    bar.set_color("red")

            ax.set_ylabel("R² Score")
            ax.set_title("Model Performance Comparison")
            ax.set_ylim(0, 1)

            # Add value labels on bars
            for bar, acc in zip(bars, accuracies):
                height = bar.get_height()
                ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    height + 0.01,
                    f"{acc: .3f}",
                    ha="center",
                    va="bottom",
                )
        else:
            ax.text(
                0.5,
                0.5,
                "No model performance data available",
                transform=ax.transAxes,
                ha="center",
                va="center",
            )

        self.comp_fig.tight_layout()
        self.comp_canvas.draw()

    def _update_details_display(self):
        """Update the detailed forecast information display."""
        if not self.current_forecast:
            return

        self.details_text.delete("1.0", tk.END)

        # Format detailed forecast information
        details = []
        details.append(f"Enhanced Weather Forecast for {self.current_city}")
        details.append("=" * 50)
        details.append(
            f"Generated: {self.current_forecast.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        )
        details.append(
            f"Overall Confidence: {self.current_forecast.confidence_score: .1%}"
        )
        details.append("")

        # API forecast summary
        details.append("API Forecast Data:")
        details.append("-" * 20)
        if "forecast_days" in self.current_forecast.api_forecast:
            for i, day_data in enumerate(
                self.current_forecast.api_forecast["forecast_days"]
            ):
                date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
                temp = day_data.get("temperature", {})
                desc = day_data.get("description", "N/A")
                details.append(f"Day {i+1} ({date}): {temp}°C - {desc}")
        details.append("")

        # ML predictions
        if self.current_forecast.ml_predictions:
            details.append("ML Predictions:")
            details.append("-" * 15)
            for i, pred in enumerate(self.current_forecast.ml_predictions):
                date = pred.timestamp.strftime("%Y-%m-%d")
                details.append(f"Day {i+1} ({date}): ")
                details.append(f"  Temperature: {pred.predicted_temperature: .1f}°C")
                details.append(
                    f"  Confidence Interval: {pred.confidence_interval[0]: .1f}°C - {pred.confidence_interval[1]: .1f}°C"
                )
                details.append(f"  Weather Pattern: {pred.weather_pattern}")
                details.append(
                    f"  Prediction Accuracy: {pred.prediction_accuracy: .1%}"
                )
                details.append(
                    f"  Features Used: {', '.join(pred.features_used[:5])}{'...' if len(pred.features_used) > 5 else ''}"
                )
                details.append("")

        # Model information
        service_status = self.integration_service.get_service_status()
        details.append("Active Models:")
        details.append("-" * 14)
        for model in service_status.active_models:
            accuracy = service_status.prediction_accuracy.get(model, 0)
            details.append(f"  {model}: R² = {accuracy: .3f}")
        details.append("")

        # Service status
        details.append("Service Status:")
        details.append("-" * 15)
        details.append(f"Models Loaded: {service_status.models_loaded}")
        details.append(f"Service Uptime: {service_status.service_uptime}")
        if service_status.last_training:
            details.append(
                f"Last Training: {service_status.last_training.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        # Insert all details
        self.details_text.insert(tk.END, "\\n".join(details))

    def _export_json(self):
        """Export forecast data as JSON."""
        if not self.current_forecast:
            messagebox.showwarning("Warning", "No forecast data to export")
            return

        try:
            import json
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Forecast Data",
            )

            if filename:
                # Convert forecast to serializable format
                export_data = {
                    "city": self.current_city,
                    "timestamp": self.current_forecast.timestamp.isoformat(),
                    "confidence_score": self.current_forecast.confidence_score,
                    "api_forecast": self.current_forecast.api_forecast,
                    "hybrid_forecast": self.current_forecast.hybrid_forecast,
                    "ml_predictions": [],
                }

                ml_predictions = (
                    getattr(self.current_forecast, "ml_predictions", []) or []
                )
                for pred in ml_predictions:
                    pred_data = {
                        "timestamp": pred.timestamp.isoformat(),
                        "predicted_temperature": pred.predicted_temperature,
                        "confidence_interval": pred.confidence_interval,
                        "weather_pattern": pred.weather_pattern,
                        "prediction_accuracy": pred.prediction_accuracy,
                        "features_used": pred.features_used,
                    }
                    export_data["ml_predictions"].append(pred_data)

                with open(filename, "w") as f:
                    json.dump(export_data, f, indent=2)

                messagebox.showinfo("Success", f"Forecast data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def _export_chart(self):
        """Export the current chart as an image."""
        try:
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*"),
                ],
                title="Export Chart",
            )

            if filename:
                # Get current tab
                current_tab = self.forecast_notebook.index(
                    self.forecast_notebook.select()
                )

                if current_tab == 0:  # Temperature chart
                    self.temp_fig.savefig(filename, dpi=300, bbox_inches="tight")
                elif current_tab == 1:  # Confidence chart
                    self.conf_fig.savefig(filename, dpi=300, bbox_inches="tight")
                elif current_tab == 2:  # Comparison chart
                    self.comp_fig.savefig(filename, dpi=300, bbox_inches="tight")

                messagebox.showinfo("Success", f"Chart exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export chart: {str(e)}")

    def _show_model_explanation(self):
        """Show detailed explanation of ML model predictions."""
        if not self.current_city:
            messagebox.showwarning("Warning", "Generate a forecast first")
            return

        def run_async():
            try:
                # Create new event loop for thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                explanation = loop.run_until_complete(
                    self.integration_service.get_prediction_explanation(
                        self.current_city
                    )
                )

                # Update UI in main thread
                self.after(0, lambda: self._display_explanation(explanation))

            except Exception as e:
                self.after(
                    0,
                    lambda e=e: messagebox.showerror(
                        "Error", f"Failed to get model explanation: {str(e)}"
                    ),
                )

        # Start in background thread
        thread = threading.Thread(target=run_async)
        thread.daemon = True
        thread.start()

    def _display_explanation(self, explanation):
        """Display the model explanation in a popup window."""
        # Create explanation window
        explanation_window = tk.Toplevel(self)
        explanation_window.title("ML Model Explanation")
        explanation_window.geometry("600x500")

        # Create text widget with scrollbar
        text_frame = ttk.Frame(explanation_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        explanation_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10))
        scrollbar = ttk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=explanation_text.yview
        )
        explanation_text.configure(yscrollcommand=scrollbar.set)

        explanation_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Format explanation
        explanation_lines = []
        explanation_lines.append("Machine Learning Model Explanation")
        explanation_lines.append("=" * 40)
        explanation_lines.append(f"City: {explanation['city']}")
        explanation_lines.append(f"Analysis Time: {explanation['timestamp']}")
        explanation_lines.append("")

        explanation_lines.append("Models Used:")
        for model in explanation["models_used"]:
            explanation_lines.append(
                f"  • {model['type']} (weight: {model['weight']: .3f})"
            )
            explanation_lines.append(
                f"    Features: {', '.join(model['features_used'][:5])}"
            )
        explanation_lines.append("")

        explanation_lines.append("Feature Sources:")
        for source in explanation["feature_sources"]:
            explanation_lines.append(f"  • {source}")
        explanation_lines.append("")

        explanation_lines.append("Model Performance:")
        for model_type, metrics in explanation["accuracy_metrics"].items():
            explanation_lines.append(f"  • {model_type}: ")
            explanation_lines.append(f"    R² Score: {metrics['r2_score']}")
            explanation_lines.append(
                f"    Mean Absolute Error: {metrics['mean_absolute_error']}°C"
            )
        explanation_lines.append("")

        explanation_lines.append("Limitations:")
        for limitation in explanation["limitations"]:
            explanation_lines.append(f"  • {limitation}")

        explanation_text.insert(tk.END, "\\n".join(explanation_lines))
        explanation_text.configure(state="disabled")
