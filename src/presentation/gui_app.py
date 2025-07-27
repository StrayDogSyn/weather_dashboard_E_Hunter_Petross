"""GUI Application for Weather Dashboard.

This module contains the main GUI application class that orchestrates
the user interface using dependency injection and clean architecture.
"""

import logging
import threading
import tkinter as tk
from typing import Optional

from ..application.dependency_container import DependencyContainer
from ..business.interfaces import IActivitySuggestionService
from ..business.interfaces import ICityComparisonService
from ..business.interfaces import ICortanaVoiceService
from ..business.interfaces import IWeatherJournalService
from ..business.interfaces import IWeatherPoetryService
from ..business.interfaces import IWeatherService
from ..shared.constants import DEFAULT_WINDOW_HEIGHT
from ..shared.constants import DEFAULT_WINDOW_WIDTH
from ..shared.constants import MIN_WINDOW_HEIGHT
from ..shared.constants import MIN_WINDOW_WIDTH
from ..shared.constants import REFRESH_INTERVAL
from ..shared.exceptions import UIError
from ..shared.exceptions import WeatherDashboardError


class WeatherDashboardGUIApp:
    """Main GUI application for Weather Dashboard.

    This class serves as the main entry point for the GUI application,
    coordinating between the UI components and business services through
    dependency injection.
    """

    def __init__(self, container: DependencyContainer):
        """Initialize the GUI application.

        Args:
            container: Dependency injection container with all services
        """
        self._container = container
        self._logger = logging.getLogger(self.__class__.__name__)

        # UI components
        self._root: Optional[tk.Tk] = None
        self._main_window = None

        # Services (injected)
        self._weather_service: Optional[IWeatherService] = None
        self._comparison_service: Optional[ICityComparisonService] = None
        self._journal_service: Optional[IWeatherJournalService] = None
        self._activity_service: Optional[IActivitySuggestionService] = None
        self._poetry_service: Optional[IWeatherPoetryService] = None
        self._voice_service: Optional[ICortanaVoiceService] = None

        # Application state
        self._is_running = False
        self._refresh_timer: Optional[str] = None

        # Initialize services
        self._inject_dependencies()

    def _inject_dependencies(self) -> None:
        """Inject required dependencies from the container.

        Raises:
            UIError: If required services cannot be injected
        """
        try:
            self._weather_service = self._container.get_service(IWeatherService)
            self._comparison_service = self._container.get_service(
                ICityComparisonService
            )
            self._journal_service = self._container.get_service(IWeatherJournalService)
            self._activity_service = self._container.get_service(
                IActivitySuggestionService
            )
            self._poetry_service = self._container.get_service(IWeatherPoetryService)
            self._voice_service = self._container.get_service(ICortanaVoiceService)

            self._logger.info("Dependencies injected successfully")

        except Exception as e:
            raise UIError(
                f"Failed to inject dependencies: {e}",
                "WeatherDashboardGUIApp",
                "dependency_injection",
            ) from e

    def initialize(self) -> None:
        """Initialize the GUI application.

        Raises:
            UIError: If GUI initialization fails
        """
        try:
            self._logger.info("Initializing GUI application")

            # Create root window
            self._create_root_window()

            # Create main window
            self._create_main_window()

            # Setup event handlers
            self._setup_event_handlers()

            # Load initial data
            self._load_initial_data()

            self._logger.info("GUI application initialized successfully")

        except Exception as e:
            self._logger.error(f"Failed to initialize GUI: {e}")
            raise UIError(
                f"Failed to initialize GUI application: {e}",
                "WeatherDashboardGUIApp",
                "initialization",
            ) from e

    def run(self) -> None:
        """Start the GUI application main loop.

        Raises:
            UIError: If application startup fails
        """
        try:
            if not self._root:
                raise UIError(
                    "GUI application not initialized",
                    "WeatherDashboardGUIApp",
                    "startup",
                )

            self._logger.info("Starting GUI application")
            self._is_running = True

            # Start refresh timer
            self._start_refresh_timer()

            # Start main loop
            self._root.mainloop()

        except Exception as e:
            self._logger.error(f"GUI application error: {e}")
            raise UIError(
                f"GUI application runtime error: {e}",
                "WeatherDashboardGUIApp",
                "runtime",
            ) from e
        finally:
            self._cleanup()

    def shutdown(self) -> None:
        """Shutdown the GUI application gracefully."""
        self._logger.info("Shutting down GUI application")

        self._is_running = False

        # Cancel refresh timer
        if self._refresh_timer and self._root:
            self._root.after_cancel(self._refresh_timer)

        # Close main window
        if self._root:
            self._root.quit()
            self._root.destroy()

        self._cleanup()
        self._logger.info("GUI application shutdown completed")

    def _create_root_window(self) -> None:
        """Create and configure the root Tkinter window."""
        self._root = tk.Tk()
        self._root.title("Weather Dashboard - Your Personal Weather Companion")

        # Set window to fullscreen
        self._root.state("zoomed")  # Windows fullscreen
        self._root.minsize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        # Configure window properties for fullscreen
        self._root.configure(bg="#1a1a1a")  # Dark background

        # Configure grid weights for responsive layout
        self._root.grid_rowconfigure(0, weight=1)
        self._root.grid_columnconfigure(0, weight=1)

        # Configure window properties
        self._root.protocol("WM_DELETE_WINDOW", self._on_window_close)
        self._root.bind("<Configure>", self._on_window_configure)
        self._root.bind("<F11>", self._toggle_fullscreen)
        self._root.bind("<Escape>", self._exit_fullscreen)

        # Mark as configured by parent to prevent conflicts
        self._root._configured_by_parent = True
        self._root._events_bound = True

        self._logger.debug("Root window created with fullscreen support")

    def _create_main_window(self) -> None:
        """Create the main application window."""
        try:
            # Import here to avoid circular imports
            from ..ui.gui_interface import WeatherDashboardGUI

            # Pass the root window to the GUI constructor
            self._main_window = WeatherDashboardGUI(root=self._root)

            # Initialize services in the GUI
            self._main_window.initialize_services(self._container)

            self._logger.debug("Main window created with shared root")

        except Exception as e:
            raise UIError(
                f"Failed to create main window: {e}", "MainWindow", "creation"
            ) from e

    def _setup_event_handlers(self) -> None:
        """Setup application-level event handlers."""
        # Bind keyboard shortcuts
        self._root.bind("<Control-q>", lambda e: self.shutdown())
        self._root.bind("<F5>", lambda e: self._refresh_data())
        self._root.bind("<Control-r>", lambda e: self._refresh_data())

        # Bind window events
        self._root.bind("<Configure>", self._on_window_configure)

        self._logger.debug("Event handlers setup completed")

    def _load_initial_data(self) -> None:
        """Load initial application data asynchronously."""

        def load_data():
            try:
                self._logger.info("Loading initial data")

                # Load default city weather
                if self._main_window and hasattr(
                    self._main_window, "load_default_weather"
                ):
                    self._main_window.load_default_weather()

                self._logger.info("Initial data loaded successfully")

            except Exception as e:
                self._logger.error(f"Failed to load initial data: {e}")
                # Show error in UI if possible
                if self._main_window and hasattr(self._main_window, "show_error"):
                    self._main_window.show_error(f"Failed to load initial data: {e}")

        # Load data in background thread
        threading.Thread(target=load_data, daemon=True).start()

    def _start_refresh_timer(self) -> None:
        """Start the automatic data refresh timer."""
        if self._root and self._is_running:
            self._refresh_timer = self._root.after(REFRESH_INTERVAL, self._auto_refresh)

    def _auto_refresh(self) -> None:
        """Automatically refresh data at regular intervals."""
        if self._is_running:
            try:
                self._refresh_data()
            except Exception as e:
                self._logger.warning(f"Auto-refresh failed: {e}")
            finally:
                # Schedule next refresh
                self._start_refresh_timer()

    def _refresh_data(self) -> None:
        """Refresh application data."""

        def refresh():
            try:
                self._logger.debug("Refreshing application data")

                if self._main_window and hasattr(self._main_window, "refresh_data"):
                    self._main_window.refresh_data()

            except Exception as e:
                self._logger.error(f"Data refresh failed: {e}")

        # Refresh in background thread
        threading.Thread(target=refresh, daemon=True).start()

    def _center_window(self) -> None:
        """Center the window on the screen."""
        if not self._root:
            return

        self._root.update_idletasks()

        # Get screen dimensions
        screen_width = self._root.winfo_screenwidth()
        screen_height = self._root.winfo_screenheight()

        # Calculate position
        x = (screen_width - DEFAULT_WINDOW_WIDTH) // 2
        y = (screen_height - DEFAULT_WINDOW_HEIGHT) // 2

        self._root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}+{x}+{y}")

    def _on_window_close(self) -> None:
        """Handle window close event."""
        self.shutdown()

    def _on_window_configure(self, event) -> None:
        """Handle window configuration changes."""
        # Only handle root window events
        if event.widget == self._root:
            # Update window state if needed
            pass

    def _toggle_fullscreen(self, event=None) -> None:
        """Toggle fullscreen mode."""
        try:
            current_state = self._root.state()
            if current_state == "zoomed":
                self._root.state("normal")
                self._root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
                self._center_window()
                self._logger.debug("Exited fullscreen mode")
            else:
                self._root.state("zoomed")
                self._logger.debug("Entered fullscreen mode")
        except Exception as e:
            self._logger.error(f"Error toggling fullscreen: {e}")

    def _exit_fullscreen(self, event=None) -> None:
        """Exit fullscreen mode."""
        try:
            if self._root.state() == "zoomed":
                self._root.state("normal")
                self._root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
                self._center_window()
                self._logger.debug("Exited fullscreen mode via Escape key")
        except Exception as e:
            self._logger.error(f"Error exiting fullscreen: {e}")

    def _cleanup(self) -> None:
        """Cleanup application resources."""
        try:
            # Cleanup main window
            if self._main_window and hasattr(self._main_window, "cleanup"):
                self._main_window.cleanup()

            # Reset references
            self._main_window = None
            self._root = None

            self._logger.debug("Application cleanup completed")

        except Exception as e:
            self._logger.error(f"Error during cleanup: {e}")

    @property
    def is_running(self) -> bool:
        """Check if the application is currently running."""
        return self._is_running

    @property
    def container(self) -> DependencyContainer:
        """Get the dependency injection container."""
        return self._container
