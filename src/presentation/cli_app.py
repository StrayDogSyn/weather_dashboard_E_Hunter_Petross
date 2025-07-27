"""CLI Application for Weather Dashboard.

This module contains the command-line interface application class
for the Weather Dashboard, providing a text-based interface for
all weather dashboard functionality.
"""

import argparse
import asyncio
import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from ..application.dependency_container import DependencyContainer
from ..business.interfaces import IActivitySuggestionService
from ..business.interfaces import ICityComparisonService
from ..business.interfaces import ICortanaVoiceService
from ..business.interfaces import IWeatherJournalService
from ..business.interfaces import IWeatherPoetryService
from ..business.interfaces import IWeatherService
from ..shared.exceptions import UIError
from ..shared.exceptions import WeatherDashboardError


class WeatherDashboardCLIApp:
    """Command-line interface application for Weather Dashboard.

    This class provides a text-based interface for all weather dashboard
    functionality, suitable for headless environments or automation.
    """

    def __init__(self, container: DependencyContainer):
        """Initialize the CLI application.

        Args:
            container: Dependency injection container with all services
        """
        self._container = container
        self._logger = logging.getLogger(self.__class__.__name__)

        # Services (injected)
        self._weather_service: Optional[IWeatherService] = None
        self._comparison_service: Optional[ICityComparisonService] = None
        self._journal_service: Optional[IWeatherJournalService] = None
        self._activity_service: Optional[IActivitySuggestionService] = None
        self._poetry_service: Optional[IWeatherPoetryService] = None
        self._voice_service: Optional[ICortanaVoiceService] = None

        # Application state
        self._is_running = False

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
                "WeatherDashboardCLIApp",
                "dependency_injection",
            ) from e

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI application.

        Args:
            args: Optional command line arguments

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            self._logger.info("Starting CLI application")
            self._is_running = True

            # Parse command line arguments
            parser = self._create_argument_parser()
            parsed_args = parser.parse_args(args)

            # Execute the requested command
            return asyncio.run(self._execute_command(parsed_args))

        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return 130  # Standard exit code for Ctrl+C
        except Exception as e:
            self._logger.error(f"CLI application error: {e}")
            print(f"Error: {e}")
            return 1
        finally:
            self._is_running = False

    def _create_argument_parser(self) -> argparse.ArgumentParser:
        """Create the command line argument parser.

        Returns:
            Configured ArgumentParser instance
        """
        parser = argparse.ArgumentParser(
            description="Weather Dashboard CLI", prog="weather-dashboard"
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Weather command
        weather_parser = subparsers.add_parser("weather", help="Get current weather")
        weather_parser.add_argument("city", help="City name")
        weather_parser.add_argument("--country", help="Country code")
        weather_parser.add_argument(
            "--forecast", "-f", action="store_true", help="Include forecast"
        )
        weather_parser.add_argument(
            "--days", type=int, default=7, help="Forecast days (default: 7)"
        )

        # Compare command
        compare_parser = subparsers.add_parser("compare", help="Compare cities")
        compare_parser.add_argument("cities", nargs="+", help="Cities to compare")
        compare_parser.add_argument(
            "--metrics", nargs="*", help="Specific metrics to compare"
        )

        # Journal command
        journal_parser = subparsers.add_parser(
            "journal", help="Weather journal operations"
        )
        journal_subparsers = journal_parser.add_subparsers(dest="journal_action")

        # Journal create
        create_parser = journal_subparsers.add_parser(
            "create", help="Create journal entry"
        )
        create_parser.add_argument("city", help="City name")
        create_parser.add_argument("content", help="Journal entry content")

        # Journal list
        list_parser = journal_subparsers.add_parser("list", help="List journal entries")
        list_parser.add_argument("--city", help="Filter by city")
        list_parser.add_argument(
            "--limit", type=int, default=10, help="Number of entries"
        )

        # Activity command
        activity_parser = subparsers.add_parser(
            "activities", help="Get activity suggestions"
        )
        activity_parser.add_argument("city", help="City name")
        activity_parser.add_argument("--category", help="Activity category")

        # Poetry command
        poetry_parser = subparsers.add_parser("poetry", help="Generate weather poetry")
        poetry_parser.add_argument("city", help="City name")
        poetry_parser.add_argument(
            "--style", default="haiku", help="Poetry style (default: haiku)"
        )

        return parser

    async def _execute_command(self, args: argparse.Namespace) -> int:
        """Execute the parsed command.

        Args:
            args: Parsed command line arguments

        Returns:
            Exit code
        """
        try:
            if args.command == "weather":
                return await self._handle_weather_command(args)
            elif args.command == "compare":
                return await self._handle_compare_command(args)
            elif args.command == "journal":
                return await self._handle_journal_command(args)
            elif args.command == "activities":
                return await self._handle_activities_command(args)
            elif args.command == "poetry":
                return await self._handle_poetry_command(args)
            else:
                print("No command specified. Use --help for usage information.")
                return 1

        except Exception as e:
            self._logger.error(f"Command execution failed: {e}")
            print(f"Error executing command: {e}")
            return 1

    async def _handle_weather_command(self, args: argparse.Namespace) -> int:
        """Handle weather command.

        Args:
            args: Parsed arguments

        Returns:
            Exit code
        """
        try:
            # Get current weather
            weather_data = await self._weather_service.get_current_weather(
                args.city, args.country
            )

            self._print_weather_data(weather_data)

            # Get forecast if requested
            if args.forecast:
                forecast_data = await self._weather_service.get_weather_forecast(
                    args.city, args.days, args.country
                )
                self._print_forecast_data(forecast_data)

            return 0

        except Exception as e:
            print(f"Failed to get weather data: {e}")
            return 1

    async def _handle_compare_command(self, args: argparse.Namespace) -> int:
        """Handle compare command.

        Args:
            args: Parsed arguments

        Returns:
            Exit code
        """
        try:
            comparison_data = await self._comparison_service.compare_cities(
                args.cities, args.metrics
            )

            self._print_comparison_data(comparison_data)
            return 0

        except Exception as e:
            print(f"Failed to compare cities: {e}")
            return 1

    async def _handle_journal_command(self, args: argparse.Namespace) -> int:
        """Handle journal command.

        Args:
            args: Parsed arguments

        Returns:
            Exit code
        """
        try:
            if args.journal_action == "create":
                entry_id = await self._journal_service.create_entry(
                    args.city, args.content
                )
                print(f"Journal entry created with ID: {entry_id}")

            elif args.journal_action == "list":
                if args.city:
                    entries = await self._journal_service.get_entries_by_city(
                        args.city, args.limit
                    )
                else:
                    # Get recent entries (this would need to be implemented)
                    entries = []  # Placeholder

                self._print_journal_entries(entries)

            return 0

        except Exception as e:
            print(f"Journal operation failed: {e}")
            return 1

    async def _handle_activities_command(self, args: argparse.Namespace) -> int:
        """Handle activities command.

        Args:
            args: Parsed arguments

        Returns:
            Exit code
        """
        try:
            # Get weather data first
            weather_data = await self._weather_service.get_current_weather(args.city)

            # Get activity suggestions
            if args.category:
                suggestions = await self._activity_service.get_suggestions_by_category(
                    args.category, weather_data
                )
            else:
                suggestions = await self._activity_service.get_suggestions(weather_data)

            self._print_activity_suggestions(suggestions)
            return 0

        except Exception as e:
            print(f"Failed to get activity suggestions: {e}")
            return 1

    async def _handle_poetry_command(self, args: argparse.Namespace) -> int:
        """Handle poetry command.

        Args:
            args: Parsed arguments

        Returns:
            Exit code
        """
        try:
            # Get weather data first
            weather_data = await self._weather_service.get_current_weather(args.city)

            # Generate poetry
            poem = await self._poetry_service.generate_poem(weather_data, args.style)

            print(f"\n{args.style.title()} for {args.city}: ")
            print("-" * 40)
            print(poem)
            print("-" * 40)

            return 0

        except Exception as e:
            print(f"Failed to generate poetry: {e}")
            return 1

    def _print_weather_data(self, weather_data: Dict[str, Any]) -> None:
        """Print weather data in a formatted way."""
        print(f"\nWeather for {weather_data.get('city', 'Unknown')}: ")
        print(f"Temperature: {weather_data.get('temperature', 'N/A')}°C")
        print(f"Condition: {weather_data.get('condition', 'N/A')}")
        print(f"Humidity: {weather_data.get('humidity', 'N/A')}%")
        print(f"Wind: {weather_data.get('wind_speed', 'N/A')} km/h")

    def _print_forecast_data(self, forecast_data: List[Dict[str, Any]]) -> None:
        """Print forecast data in a formatted way."""
        print("\nForecast:")
        for day in forecast_data:
            print(
                f"{day.get('date', 'N/A')}: {day.get('temperature', 'N/A')}°C, {day.get('condition', 'N/A')}"
            )

    def _print_comparison_data(self, comparison_data: Dict[str, Any]) -> None:
        """Print comparison data in a formatted way."""
        print("\nCity Comparison:")
        # Implementation would depend on the comparison data structure
        print(comparison_data)

    def _print_journal_entries(self, entries: List[Dict[str, Any]]) -> None:
        """Print journal entries in a formatted way."""
        print("\nJournal Entries:")
        for entry in entries:
            print(
                f"[{entry.get('date', 'N/A')}] {entry.get('city', 'N/A')}: {entry.get('content', 'N/A')}"
            )

    def _print_activity_suggestions(self, suggestions: List[Dict[str, Any]]) -> None:
        """Print activity suggestions in a formatted way."""
        print("\nActivity Suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            print(
                f"{i}. {suggestion.get('name', 'N/A')} - {suggestion.get('description', 'N/A')}"
            )

    @property
    def is_running(self) -> bool:
        """Check if the application is currently running."""
        return self._is_running

    @property
    def container(self) -> DependencyContainer:
        """Get the dependency injection container."""
        return self._container
