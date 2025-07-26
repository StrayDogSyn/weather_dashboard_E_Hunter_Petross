"""Weather API service implementation."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import requests

from ..config import config_manager
from ..interfaces.weather_interfaces import IWeatherAPI
from ..models import (
    AtmosphericPressure,
    CurrentWeather,
    Location,
    Precipitation,
    Temperature,
    TemperatureUnit,
    WeatherCondition,
    WeatherForecast,
    WeatherForecastDay,
    Wind,
)

# Type aliases
WeatherData = CurrentWeather
ForecastData = WeatherForecast
LocationData = Location


class OpenWeatherMapAPI(IWeatherAPI):
    """OpenWeatherMap API implementation."""

    def __init__(self, language: str = "en"):
        """Initialize the weather API service.

        Args:
            language: Language code for weather descriptions (default: "en")
        """
        self.config = config_manager.config.api
        self.api_key = self.config.api_key
        self.base_url = self.config.base_url
        self.language = language
        self.session = requests.Session()

        # Setup session headers
        self.session.headers.update({"User-Agent": "WeatherDashboard/1.0"})

        # Condition mapping
        self._condition_map = {
            "clear": WeatherCondition.CLEAR,
            "clouds": WeatherCondition.CLOUDS,
            "rain": WeatherCondition.RAIN,
            "snow": WeatherCondition.SNOW,
            "thunderstorm": WeatherCondition.THUNDERSTORM,
            "drizzle": WeatherCondition.DRIZZLE,
            "mist": WeatherCondition.MIST,
            "fog": WeatherCondition.FOG,
            "haze": WeatherCondition.HAZE,
        }

    def _make_request(
        self, endpoint: str, params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Make an API request with error handling and retry logic.

        Args:
            endpoint: API endpoint
            params: Request parameters

        Returns:
            API response data or None if error
        """
        # Add API key to parameters
        params["appid"] = self.api_key

        url = f"{self.base_url}/{endpoint}"
        max_retries = 2  # Quick retries for network issues

        for attempt in range(max_retries + 1):
            try:
                response = self.session.get(
                    url, params=params, timeout=self.config.timeout
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    logging.warning(
                        f"Request timeout (attempt {attempt + 1}/{max_retries + 1}), retrying..."
                    )
                    continue
                logging.error("Request timeout after retries")
                return None
            except requests.exceptions.ConnectionError:
                if attempt < max_retries:
                    logging.warning(
                        f"Connection error (attempt {attempt + 1}/{max_retries + 1}), retrying..."
                    )
                    continue
                logging.error("Connection error after retries")
                return None
            except requests.exceptions.HTTPError as e:
                if hasattr(e, "response") and e.response is not None:
                    if e.response.status_code == 404:
                        logging.error("City not found")
                    elif e.response.status_code == 401:
                        logging.error("Invalid API key")
                    elif e.response.status_code == 429:
                        logging.error("API rate limit exceeded")
                    else:
                        logging.error(f"HTTP error: {e}")
                else:
                    logging.error(f"HTTP error: {e}")
                return None
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                return None

    def _parse_weather_condition(
        self, weather_data: Dict[str, Any]
    ) -> WeatherCondition:
        """Parse weather condition from API response."""
        if "weather" in weather_data and weather_data["weather"]:
            main = weather_data["weather"][0]["main"].lower()
            return self._condition_map.get(main, WeatherCondition.CLEAR)
        return WeatherCondition.CLEAR

    def _parse_location(self, data: Dict[str, Any]) -> Location:
        """Parse location from API response."""
        return Location(
            name=data["name"],
            country=data["sys"]["country"],
            latitude=data["coord"]["lat"],
            longitude=data["coord"]["lon"],
        )

    def _parse_temperature(self, temp_data: Dict[str, Any], units: str) -> Temperature:
        """Parse temperature from API response."""
        unit_map = {
            "metric": TemperatureUnit.CELSIUS,
            "imperial": TemperatureUnit.FAHRENHEIT,
            "standard": TemperatureUnit.KELVIN,
        }

        return Temperature(
            value=temp_data["temp"],
            unit=unit_map.get(units, TemperatureUnit.CELSIUS),
            feels_like=temp_data.get("feels_like"),
        )

    def _parse_wind(self, wind_data: Dict[str, Any]) -> Wind:
        """Parse wind from API response."""
        return Wind(
            speed=wind_data.get("speed", 0),
            direction=wind_data.get("deg"),
            gust=wind_data.get("gust"),
        )

    def _parse_precipitation(self, data: Dict[str, Any]) -> Optional[Precipitation]:
        """Parse precipitation from API response."""
        rain = data.get("rain", {})
        snow = data.get("snow", {})

        if rain or snow:
            return Precipitation(
                rain_1h=rain.get("1h"),
                rain_3h=rain.get("3h"),
                snow_1h=snow.get("1h"),
                snow_3h=snow.get("3h"),
            )
        return None

    def get_current_weather(
        self, city: str, units: str = "metric"
    ) -> Optional[WeatherData]:
        """
        Get current weather for a city.

        Args:
            city: City name
            units: Temperature units (metric, imperial, standard)

        Returns:
            WeatherData or None if error
        """
        params = {
            "q": city,
            "units": units,
            "lang": self.language,  # Configurable language for weather descriptions
            "mode": "json",  # Response format
        }

        data = self._make_request("weather", params)
        if not data:
            return None

        try:
            location = self._parse_location(data)
            temperature = self._parse_temperature(data["main"], units)
            condition = self._parse_weather_condition(data)
            description = data["weather"][0]["description"]

            pressure = AtmosphericPressure(
                value=data["main"]["pressure"],
                sea_level=data["main"].get("sea_level"),
                ground_level=data["main"].get("grnd_level"),
            )

            wind = self._parse_wind(data.get("wind", {}))
            precipitation = self._parse_precipitation(data)

            return CurrentWeather(
                location=location,
                temperature=temperature,
                condition=condition,
                description=description,
                humidity=data["main"]["humidity"],
                pressure=pressure,
                wind=wind,
                precipitation=precipitation,
                visibility=(
                    data.get("visibility", 0) / 1000 if data.get("visibility") else None
                ),  # Convert to km
                timestamp=datetime.fromtimestamp(data["dt"]),
            )

        except (KeyError, ValueError) as e:
            logging.error(f"Error parsing weather data: {e}")
            return None

    def get_forecast(
        self, city: str, days: int = 5, units: str = "metric"
    ) -> Optional[ForecastData]:
        """
        Get weather forecast for a city.

        Args:
            city: City name
            days: Number of days for forecast
            units: Temperature units

        Returns:
            ForecastData or None if error
        """
        params = {
            "q": city,
            "units": units,
            "cnt": days * 8,  # 8 forecasts per day (3-hour intervals)
            "lang": self.language,  # Configurable language for weather descriptions
            "mode": "json",  # Response format
        }

        data = self._make_request("forecast", params)
        if not data:
            return None

        try:
            location = Location(
                name=data["city"]["name"],
                country=data["city"]["country"],
                latitude=data["city"]["coord"]["lat"],
                longitude=data["city"]["coord"]["lon"],
            )

            # Group forecasts by day
            forecast_days = []
            current_date = None
            daily_forecasts: List[Dict[str, Any]] = []

            for forecast in data["list"]:
                forecast_time = datetime.fromtimestamp(forecast["dt"])
                forecast_date = forecast_time.date()

                if current_date != forecast_date:
                    if daily_forecasts:
                        # Process previous day
                        forecast_day = self._create_forecast_day(daily_forecasts, units)
                        if forecast_day:
                            forecast_days.append(forecast_day)

                    current_date = forecast_date
                    daily_forecasts = []

                daily_forecasts.append(forecast)

            # Process last day
            if daily_forecasts:
                forecast_day = self._create_forecast_day(daily_forecasts, units)
                if forecast_day:
                    forecast_days.append(forecast_day)

            return WeatherForecast(
                location=location,
                forecast_days=forecast_days[:days],  # Limit to requested days
            )

        except (KeyError, ValueError) as e:
            logging.error(f"Error parsing forecast data: {e}")
            return None

    def _create_forecast_day(
        self, forecasts: List[Dict], units: str
    ) -> Optional[WeatherForecastDay]:
        """Create a forecast day from multiple forecasts."""
        if not forecasts:
            return None

        try:
            # Use the first forecast for date and general info
            first_forecast = forecasts[0]

            # Find min/max temperatures
            temps = [f["main"]["temp"] for f in forecasts]
            temp_high = max(temps)
            temp_low = min(temps)

            unit_map = {
                "metric": TemperatureUnit.CELSIUS,
                "imperial": TemperatureUnit.FAHRENHEIT,
                "standard": TemperatureUnit.KELVIN,
            }
            temp_unit = unit_map.get(units, TemperatureUnit.CELSIUS)

            # Average humidity
            humidity = sum(f["main"]["humidity"] for f in forecasts) // len(forecasts)

            # Average wind
            wind_speeds = [f.get("wind", {}).get("speed", 0) for f in forecasts]
            avg_wind_speed = sum(wind_speeds) / len(wind_speeds)

            # Most common weather condition
            conditions = [f["weather"][0]["main"].lower() for f in forecasts]
            most_common_condition = max(set(conditions), key=conditions.count)

            return WeatherForecastDay(
                date=datetime.fromtimestamp(first_forecast["dt"]),
                temperature_high=Temperature(temp_high, temp_unit),
                temperature_low=Temperature(temp_low, temp_unit),
                condition=self._condition_map.get(
                    most_common_condition, WeatherCondition.CLEAR
                ),
                description=first_forecast["weather"][0]["description"],
                humidity=humidity,
                wind=Wind(speed=avg_wind_speed),
                precipitation_chance=int(
                    forecasts[0].get("pop", 0) * 100
                ),  # Probability of precipitation
                precipitation=self._parse_precipitation(first_forecast),
            )

        except (KeyError, ValueError) as e:
            logging.error(f"Error creating forecast day: {e}")
            return None

    def search_locations(self, query: str, limit: int = 5) -> List[LocationData]:
        """
        Search for locations by name.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of LocationData
        """
        # Use geocoding API
        url = self.config.geocoding_url + "/direct"
        params: Dict[str, Union[str, int]] = {
            "q": query,
            "limit": limit,
            "appid": self.api_key,
            "lang": self.language,  # Configurable language for location names
        }

        try:
            response = self.session.get(url, params=params, timeout=self.config.timeout)
            response.raise_for_status()
            data = response.json()

            locations = []
            for item in data:
                location = Location(
                    name=item["name"],
                    country=item["country"],
                    latitude=item["lat"],
                    longitude=item["lon"],
                )
                locations.append(location)

            return locations

        except Exception as e:
            logging.error(f"Error searching locations: {e}")
            return []

    def get_current_weather_by_coordinates(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> Optional[WeatherData]:
        """
        Get current weather for specific coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Temperature units (metric, imperial, standard)

        Returns:
            WeatherData or None if error
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "units": units,
            "lang": self.language,  # Configurable language for weather descriptions
            "mode": "json",  # Response format
        }

        data = self._make_request("weather", params)
        if not data:
            return None

        try:
            location = self._parse_location(data)
            temperature = self._parse_temperature(data["main"], units)
            condition = self._parse_weather_condition(data)
            description = data["weather"][0]["description"]

            pressure = AtmosphericPressure(
                value=data["main"]["pressure"],
                sea_level=data["main"].get("sea_level"),
                ground_level=data["main"].get("grnd_level"),
            )

            wind = self._parse_wind(data.get("wind", {}))
            precipitation = self._parse_precipitation(data)

            return CurrentWeather(
                location=location,
                temperature=temperature,
                condition=condition,
                description=description,
                humidity=data["main"]["humidity"],
                pressure=pressure,
                wind=wind,
                precipitation=precipitation,
                timestamp=datetime.fromtimestamp(data["dt"]),
                visibility=data.get("visibility", 0) / 1000,  # Convert to km
            )

        except (KeyError, ValueError) as e:
            logging.error(f"Error parsing weather data: {e}")
            return None

    def get_forecast_by_coordinates(
        self, latitude: float, longitude: float, days: int = 5, units: str = "metric"
    ) -> Optional[ForecastData]:
        """
        Get weather forecast for specific coordinates.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days for forecast
            units: Temperature units

        Returns:
            ForecastData or None if error
        """
        params = {
            "lat": latitude,
            "lon": longitude,
            "units": units,
            "cnt": days * 8,  # 8 forecasts per day (3-hour intervals)
            "lang": self.language,  # Configurable language for weather descriptions
            "mode": "json",  # Response format
        }

        data = self._make_request("forecast", params)
        if not data:
            return None

        try:
            location = Location(
                name=data["city"]["name"],
                country=data["city"]["country"],
                latitude=data["city"]["coord"]["lat"],
                longitude=data["city"]["coord"]["lon"],
            )

            # Group forecasts by day
            forecast_days = []
            current_date = None
            daily_forecasts: List[Dict[str, Any]] = []

            for forecast in data["list"]:
                forecast_time = datetime.fromtimestamp(forecast["dt"])
                forecast_date = forecast_time.date()

                if current_date != forecast_date:
                    if daily_forecasts:
                        # Process previous day
                        forecast_day = self._create_forecast_day(daily_forecasts, units)
                        if forecast_day:
                            forecast_days.append(forecast_day)

                    current_date = forecast_date
                    daily_forecasts = []

                daily_forecasts.append(forecast)

            # Process last day
            if daily_forecasts:
                forecast_day = self._create_forecast_day(daily_forecasts, units)
                if forecast_day:
                    forecast_days.append(forecast_day)

            return WeatherForecast(
                location=location,
                forecast_days=forecast_days[:days],  # Limit to requested days
            )

        except (KeyError, ValueError) as e:
            logging.error(f"Error parsing forecast data: {e}")
            return None
