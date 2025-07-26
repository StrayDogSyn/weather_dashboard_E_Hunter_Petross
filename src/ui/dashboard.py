"""Weather Data Visualization Dashboard with Hotkey Support."""

import logging
import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from src.models.weather_models import CurrentWeather, WeatherForecast
from src.services.visualization_service import WeatherVisualizationService
from src.ui.components.responsive_layout import (
    ResponsiveLayoutManager,
    ResponsiveSpacing,
)
from src.ui.styles.glassmorphic import GlassmorphicFrame, GlassmorphicStyle
from src.ui.widgets.enhanced_button import ButtonFactory, EnhancedButton


class WeatherDashboard:
    """Interactive weather dashboard with visualization charts and hotkey support."""

    def __init__(self, parent: tk.Tk):
        """Initialize the weather dashboard."""
        self.parent = parent
        self.logger = logging.getLogger(__name__)

        # Initialize visualization service
        self.viz_service = WeatherVisualizationService()

        # Initialize responsive layout and button factory
        self.responsive_layout = ResponsiveLayoutManager()
        self.button_factory = ButtonFactory()

        # Dashboard window
        self.dashboard_window: Optional[tk.Toplevel] = None

        # Chart containers
        self.chart_frames: Dict[str, tk.Widget] = {}

        # Current weather and forecast data
        self.current_weather: Optional[CurrentWeather] = None
        self.current_forecast: Optional[WeatherForecast] = None

        # Setup hotkeys
        self.setup_hotkeys()

    def setup_hotkeys(self):
        """Setup global hotkeys for dashboard operations."""
        # Bind hotkeys to the main window
        self.parent.bind("<Control-d>", self.toggle_dashboard)
        self.parent.bind(
            "<Control-1>", lambda e: self.show_chart_with_feedback("temperature")
        )
        self.parent.bind(
            "<Control-2>", lambda e: self.show_chart_with_feedback("metrics")
        )
        self.parent.bind(
            "<Control-3>", lambda e: self.show_chart_with_feedback("forecast")
        )
        self.parent.bind(
            "<Control-4>", lambda e: self.show_chart_with_feedback("humidity_pressure")
        )
        self.parent.bind(
            "<Control-r>", lambda e: self.refresh_all_charts_with_feedback()
        )
        self.parent.bind("<Control-h>", self.show_help)

        # Make sure the main window can receive focus for hotkeys
        self.parent.focus_set()

    def _create_chart_command(self, chart_id: str):
        """Create a command function for chart button."""

        def command():
            self.show_chart_with_feedback(chart_id)

        return command

    def toggle_dashboard(self, event=None):
        """Toggle the dashboard visibility."""
        if self.dashboard_window is None or not self.dashboard_window.winfo_exists():
            self.show_dashboard()
        else:
            self.hide_dashboard()

    def show_dashboard(self):
        """Show the weather visualization dashboard."""
        if self.dashboard_window is not None and self.dashboard_window.winfo_exists():
            self.dashboard_window.lift()
            return

        # Create dashboard window
        self.dashboard_window = tk.Toplevel(self.parent)
        self.dashboard_window.title("Weather Data Visualization Dashboard")
        self.dashboard_window.geometry("1200x800")
        self.dashboard_window.configure(bg=GlassmorphicStyle.BACKGROUND)

        # Make window resizable
        self.dashboard_window.resizable(True, True)

        # Setup window icon and styling
        try:
            self.dashboard_window.iconname("Weather Dashboard")
        except Exception:
            pass  # Ignore if icon setting fails

        # Create main layout
        self.create_dashboard_layout()

        # Load initial charts
        self.refresh_all_charts()

        # Set initial active chart (temperature by default)
        self.show_chart_with_feedback("temperature")

        # Bind hotkeys to dashboard window as well
        self.setup_dashboard_hotkeys()

        # Setup window close event
        self.dashboard_window.protocol("WM_DELETE_WINDOW", self.hide_dashboard)

    def hide_dashboard(self):
        """Hide the dashboard window."""
        if self.dashboard_window and self.dashboard_window.winfo_exists():
            self.dashboard_window.destroy()
            self.dashboard_window = None

    def create_dashboard_layout(self):
        """Create the dashboard layout with chart areas."""
        # Main container
        main_frame = GlassmorphicFrame(
            self.dashboard_window,
            bg_color=GlassmorphicStyle.BACKGROUND,
        )
        # Get responsive spacing
        spacing = ResponsiveSpacing()
        main_frame.pack(
            fill=tk.BOTH, expand=True, padx=spacing.MEDIUM, pady=spacing.MEDIUM
        )

        # Title bar
        title_frame = GlassmorphicFrame(main_frame, elevated=True)
        title_frame.pack(fill=tk.X, pady=(0, spacing.MEDIUM))

        title_label = tk.Label(
            title_frame,
            text="🌤️ Weather Data Visualization Dashboard",
            font=("Segoe UI", 18, "bold"),
            fg=GlassmorphicStyle.ACCENT,
            bg=title_frame.bg_color,
        )
        title_label.pack(pady=spacing.LARGE)

        # Hotkey info
        hotkey_info = tk.Label(
            title_frame,
            text="Hotkeys: Ctrl+1-4 (Charts) | Ctrl+R (Refresh) | Ctrl+H (Help) | Ctrl+D (Toggle)",
            font=("Segoe UI", 10),
            fg=GlassmorphicStyle.TEXT_SECONDARY,
            bg=title_frame.bg_color,
        )
        hotkey_info.pack(pady=(0, spacing.MEDIUM))

        # Chart controls with responsive layout
        controls_frame = GlassmorphicFrame(main_frame, elevated=True)
        controls_frame.pack(fill=tk.X, pady=(0, spacing.MEDIUM))

        # Control buttons with enhanced button system
        button_frame = tk.Frame(controls_frame, bg=controls_frame.bg_color)
        button_frame.pack(pady=spacing.element_padding)

        # Chart selection buttons using enhanced button factory
        charts_info = [
            ("📈 Temperature Trend", "temperature", "Ctrl+1"),
            ("📊 Weather Metrics", "metrics", "Ctrl+2"),
            ("🌤️ 5-Day Forecast", "forecast", "Ctrl+3"),
            ("💧 Humidity & Pressure", "humidity_pressure", "Ctrl+4"),
        ]

        # Store button references for visual feedback
        self.chart_buttons = {}

        for text, chart_id, hotkey in charts_info:
            btn = self.button_factory.create_chart_button(
                button_frame,
                text=f"{text}\n({hotkey})",
                command=self._create_chart_command(chart_id),
                tooltip=f"Show {text} chart ({hotkey})",
            )
            btn.pack(side=tk.LEFT, padx=spacing.element_spacing)
            self.chart_buttons[chart_id] = btn

        # Refresh button using enhanced button factory
        self.refresh_btn = self.button_factory.create_action_button(
            button_frame,
            text="🔄 Refresh All\n(Ctrl+R)",
            command=self.refresh_all_charts_with_feedback,
            style="accent",
            tooltip="Refresh all charts (Ctrl+R)",
        )
        self.refresh_btn.pack(side=tk.RIGHT, padx=spacing.element_spacing)

        # Charts container with grid layout
        charts_container = GlassmorphicFrame(main_frame)
        charts_container.pack(fill=tk.BOTH, expand=True)

        # Configure grid layout (2x2)
        charts_container.grid_rowconfigure(0, weight=1)
        charts_container.grid_rowconfigure(1, weight=1)
        charts_container.grid_columnconfigure(0, weight=1)
        charts_container.grid_columnconfigure(1, weight=1)

        # Create chart placeholder frames with responsive spacing
        chart_positions = [
            ("temperature", 0, 0),
            ("metrics", 0, 1),
            ("forecast", 1, 0),
            ("humidity_pressure", 1, 1),
        ]

        for chart_id, row, col in chart_positions:
            chart_frame = GlassmorphicFrame(
                charts_container,
                bg_color=GlassmorphicStyle.GLASS_BG,
                elevated=True,
            )
            chart_frame.grid(
                row=row,
                column=col,
                padx=spacing.element_spacing,
                pady=spacing.element_spacing,
                sticky="nsew",
            )
            self.chart_frames[chart_id] = chart_frame

    def show_chart(self, chart_type: str):
        """Show a specific chart type."""
        if chart_type not in self.chart_frames:
            self.logger.warning(f"Unknown chart type: {chart_type}")
            return

        # Clear existing chart
        frame = self.chart_frames[chart_type]
        for widget in frame.winfo_children():
            widget.destroy()

        # Create new chart based on type
        if chart_type == "temperature":
            chart = self.viz_service.create_temperature_trend_chart(frame)
        elif chart_type == "metrics":
            chart = self.viz_service.create_weather_metrics_chart(frame)
        elif chart_type == "forecast":
            chart = self.viz_service.create_forecast_comparison_chart(
                frame, self.current_forecast
            )
        elif chart_type == "humidity_pressure":
            chart = self.viz_service.create_humidity_pressure_chart(frame)
        else:
            # Fallback placeholder
            label = tk.Label(
                frame,
                text=f"📊 {chart_type.title()} Chart\n\nChart type not implemented yet.",
                font=("Segoe UI", 12),
                fg=GlassmorphicStyle.TEXT_SECONDARY,
                bg=GlassmorphicStyle.GLASS_BG,
                justify=tk.CENTER,
            )
            label.pack(expand=True)
            return

        # Pack the chart
        if chart != frame:  # Only pack if it's a different widget
            chart.pack(fill=tk.BOTH, expand=True)

    def refresh_all_charts(self, event=None):
        """Refresh all charts with current data."""
        if self.dashboard_window is None or not self.dashboard_window.winfo_exists():
            return

        # Refresh each chart
        for chart_type in self.chart_frames.keys():
            self.show_chart(chart_type)

        # Log refresh completion
        self.logger.info("Dashboard charts refreshed")

    def update_weather_data(self, weather: CurrentWeather):
        """Update dashboard with new weather data."""
        self.current_weather = weather
        self.viz_service.add_weather_data_point(weather)

        # Refresh charts if dashboard is visible
        if self.dashboard_window and self.dashboard_window.winfo_exists():
            self.refresh_all_charts()

    def update_forecast_data(self, forecast: WeatherForecast):
        """Update dashboard with new forecast data."""
        self.current_forecast = forecast

        # Refresh forecast chart if dashboard is visible
        if self.dashboard_window and self.dashboard_window.winfo_exists():
            self.show_chart("forecast")

    def show_help(self, event=None):
        """Show hotkey help dialog."""
        help_window = tk.Toplevel(self.parent)
        help_window.title("Dashboard Hotkeys")
        help_window.geometry("400x300")
        help_window.configure(bg=GlassmorphicStyle.BACKGROUND)
        help_window.transient(self.parent)
        help_window.grab_set()

        # Center the window
        help_window.geometry(
            "+%d+%d"
            % (self.parent.winfo_rootx() + 100, self.parent.winfo_rooty() + 100)
        )

        help_frame = GlassmorphicFrame(help_window, elevated=True)
        help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title = tk.Label(
            help_frame,
            text="🔗 Dashboard Hotkeys",
            font=("Segoe UI", 16, "bold"),
            fg=GlassmorphicStyle.ACCENT,
            bg=help_frame.bg_color,
        )
        title.pack(pady=(10, 20))

        hotkeys_text = """
Ctrl + D    Toggle Dashboard
Ctrl + 1    Show Temperature Trend
Ctrl + 2    Show Weather Metrics
Ctrl + 3    Show 5-Day Forecast
Ctrl + 4    Show Humidity & Pressure
Ctrl + R    Refresh All Charts
Ctrl + H    Show This Help

Note: Make sure the main window has focus
for hotkeys to work properly.
        """

        help_label = tk.Label(
            help_frame,
            text=hotkeys_text.strip(),
            font=("Segoe UI", 11),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=help_frame.bg_color,
            justify=tk.LEFT,
        )
        help_label.pack(pady=10)

        close_btn = tk.Button(
            help_frame,
            text="Close",
            font=("Segoe UI", 10),
            fg=GlassmorphicStyle.TEXT_PRIMARY,
            bg=GlassmorphicStyle.ACCENT,
            activebackground=GlassmorphicStyle.ACCENT_LIGHT,
            relief="flat",
            padx=20,
            pady=5,
            cursor="hand2",
            command=help_window.destroy,
        )
        close_btn.pack(pady=20)

    def setup_dashboard_hotkeys(self):
        """Setup hotkeys specifically for the dashboard window."""
        if not self.dashboard_window:
            return

        # Bind hotkeys to dashboard window for when it has focus
        self.dashboard_window.bind(
            "<Control-1>", lambda e: self.show_chart_with_feedback("temperature")
        )
        self.dashboard_window.bind(
            "<Control-2>", lambda e: self.show_chart_with_feedback("metrics")
        )
        self.dashboard_window.bind(
            "<Control-3>", lambda e: self.show_chart_with_feedback("forecast")
        )
        self.dashboard_window.bind(
            "<Control-4>", lambda e: self.show_chart_with_feedback("humidity_pressure")
        )
        self.dashboard_window.bind(
            "<Control-r>", lambda e: self.refresh_all_charts_with_feedback()
        )
        self.dashboard_window.bind("<Control-h>", self.show_help)
        self.dashboard_window.bind("<Control-d>", self.toggle_dashboard)

        # Make dashboard window focusable for hotkeys
        self.dashboard_window.focus_set()

    def show_chart_with_feedback(self, chart_type: str):
        """Show chart with visual button feedback."""
        # Reset all button colors
        for btn_id, btn in self.chart_buttons.items():
            btn.configure(bg=GlassmorphicStyle.ACCENT)

        # Highlight the active button
        if chart_type in self.chart_buttons:
            self.chart_buttons[chart_type].configure(bg=GlassmorphicStyle.ACCENT_DARK)

        # Show the chart
        self.show_chart(chart_type)

    def refresh_all_charts_with_feedback(self):
        """Refresh all charts with visual feedback."""
        # Change button color to indicate refresh is happening
        original_bg = self.refresh_btn.cget("bg")
        self.refresh_btn.configure(
            bg=GlassmorphicStyle.WARNING, text="🔄 Refreshing...\n(Ctrl+R)"
        )

        # Update the window to show the change
        if self.dashboard_window:
            self.dashboard_window.update()

        # Perform the actual refresh
        self.refresh_all_charts()

        # Restore button appearance
        self.refresh_btn.configure(bg=original_bg, text="🔄 Refresh All\n(Ctrl+R)")
