"""
WeatherAPI.com implementation as a backup weather service.

This service provides a fallback when the primary OpenWeatherMap API fails.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from ..config import config_manager
from ..interfaces.weather_interfaces import IWeatherAPI
from ..models.weather_models import (
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


class WeatherAPIService(IWeatherAPI):
    """WeatherAPI.com service implementation as backup."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize WeatherAPI service.

        Args:
            api_key: WeatherAPI.com API key (optional, will try to get from env)
        """
        self.api_key = api_key or self._get_api_key()
        self.base_url = "https://api.weatherapi.com/v1"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Weather-Dashboard/1.0"})

        # Condition mapping from WeatherAPI to our enum
        self._condition_map = {
            1000: WeatherCondition.CLEAR,  # Sunny/Clear
            1003: WeatherCondition.CLOUDS,  # Partly cloudy
            1006: WeatherCondition.CLOUDS,  # Cloudy
            1009: WeatherCondition.CLOUDS,  # Overcast
            1030: WeatherCondition.MIST,  # Mist
            1063: WeatherCondition.RAIN,  # Patchy rain possible
            1066: WeatherCondition.SNOW,  # Patchy snow possible
            1069: WeatherCondition.RAIN,  # Patchy sleet possible
            1072: WeatherCondition.DRIZZLE,  # Patchy freezing drizzle
            1087: WeatherCondition.THUNDERSTORM,  # Thundery outbreaks possible
            1114: WeatherCondition.SNOW,  # Blowing snow
            1117: WeatherCondition.SNOW,  # Blizzard
            1135: WeatherCondition.FOG,  # Fog
            1147: WeatherCondition.FOG,  # Freezing fog
            1150: WeatherCondition.DRIZZLE,  # Patchy light drizzle
            1153: WeatherCondition.DRIZZLE,  # Light drizzle
            1168: WeatherCondition.DRIZZLE,  # Freezing drizzle
            1171: WeatherCondition.DRIZZLE,  # Heavy freezing drizzle
            1180: WeatherCondition.RAIN,  # Patchy light rain
            1183: WeatherCondition.RAIN,  # Light rain
            1186: WeatherCondition.RAIN,  # Moderate rain at times
            1189: WeatherCondition.RAIN,  # Moderate rain
            1192: WeatherCondition.RAIN,  # Heavy rain at times
            1195: WeatherCondition.RAIN,  # Heavy rain
            1198: WeatherCondition.RAIN,  # Light freezing rain
            1201: WeatherCondition.RAIN,  # Moderate or heavy freezing rain
            1204: WeatherCondition.RAIN,  # Light sleet
            1207: WeatherCondition.RAIN,  # Moderate or heavy sleet
            1210: WeatherCondition.SNOW,  # Patchy light snow
            1213: WeatherCondition.SNOW,  # Light snow
            1216: WeatherCondition.SNOW,  # Patchy moderate snow
            1219: WeatherCondition.SNOW,  # Moderate snow
            1222: WeatherCondition.SNOW,  # Patchy heavy snow
            1225: WeatherCondition.SNOW,  # Heavy snow
            1237: WeatherCondition.SNOW,  # Ice pellets
            1240: WeatherCondition.RAIN,  # Light rain shower
            1243: WeatherCondition.RAIN,  # Moderate or heavy rain shower
            1246: WeatherCondition.RAIN,  # Torrential rain shower
            1249: WeatherCondition.RAIN,  # Light sleet showers
            1252: WeatherCondition.RAIN,  # Moderate or heavy sleet showers
            1255: WeatherCondition.SNOW,  # Light snow showers
            1258: WeatherCondition.SNOW,  # Moderate or heavy snow showers
            1261: WeatherCondition.SNOW,  # Light showers of ice pellets
            1264: WeatherCondition.SNOW,  # Moderate or heavy showers of ice pellets
            1273: WeatherCondition.THUNDERSTORM,  # Patchy light rain with thunder
            1276: WeatherCondition.THUNDERSTORM,  # Moderate or heavy rain with thunder
            1279: WeatherCondition.THUNDERSTORM,  # Patchy light snow with thunder
            1282: WeatherCondition.THUNDERSTORM,  # Moderate or heavy snow with thunder
        }

    def _get_api_key(self) -> str:
        """Get API key from environment or config."""
        import os

        return os.getenv("WEATHERAPI_API_KEY", "")

    def _make_request(
        self, endpoint: str, params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Make an API request with error handling.

        Args:
            endpoint: API endpoint
            params: Request parameters

        Returns:
            API response data or None if error
        """
        if not self.api_key:
            logging.error("WeatherAPI.com API key not configured")
            return None

        # Add API key to parameters
        params["key"] = self.api_key

        url = f"{self.base_url}/{endpoint}"

        try:
            response = self.session.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logging.error("WeatherAPI request timeout")
            return None
        except requests.exceptions.ConnectionError:
            logging.error("WeatherAPI connection error")
            return None
        except requests.exceptions.HTTPError as e:
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 400:
                    logging.error("WeatherAPI: Invalid request")
                elif e.response.status_code == 401:
                    logging.error("WeatherAPI: Invalid API key")
                elif e.response.status_code == 403:
                    logging.error("WeatherAPI: API key quota exceeded")
                else:
                    logging.error(f"WeatherAPI HTTP error: {e}")
            return None
        except Exception as e:
            logging.error(f"WeatherAPI unexpected error: {e}")
            return None

    def _parse_condition(self, condition_code: int) -> WeatherCondition:
        """Parse weather condition from WeatherAPI code."""
        return self._condition_map.get(condition_code, WeatherCondition.CLEAR)

    def _parse_location(self, data: Dict[str, Any]) -> Location:
        """Parse location from WeatherAPI response."""
        location_data = data.get("location", {})
        return Location(
            name=location_data.get("name", ""),
            country=location_data.get("country", ""),
            latitude=location_data.get("lat", 0.0),
            longitude=location_data.get("lon", 0.0),
        )

    def _parse_current_weather(self, data: Dict[str, Any]) -> Optional[CurrentWeather]:
        """Parse current weather from WeatherAPI response."""
        try:
            current = data.get("current", {})
            condition = current.get("condition", {})

            location = self._parse_location(data)

            # Temperature data
            temp_c = current.get("temp_c", 0.0)
            feels_like_c = current.get("feelslike_c", temp_c)

            temperature = Temperature(
                value=temp_c, unit=TemperatureUnit.CELSIUS, feels_like=feels_like_c
            )

            # Weather condition
            condition_code = condition.get("code", 1000)
            weather_condition = self._parse_condition(condition_code)

            # Wind data
            wind = Wind(
                speed=current.get("wind_kph", 0.0) / 3.6,  # Convert kph to m/s
                direction=current.get("wind_degree", 0),
                gust=(
                    current.get("gust_kph", 0.0) / 3.6
                    if current.get("gust_kph")
                    else None
                ),
            )

            # Atmospheric pressure
            pressure = AtmosphericPressure(
                value=current.get("pressure_mb", 1013.25),
                sea_level=current.get("pressure_mb", 1013.25),
                ground_level=current.get("pressure_mb", 1013.25),
            )

            # Precipitation (if available)
            precipitation = None
            precip_mm = current.get("precip_mm", 0.0)
            if precip_mm > 0:
                precipitation = Precipitation(rain_1h=precip_mm, rain_3h=precip_mm)

            return CurrentWeather(
                location=location,
                temperature=temperature,
                condition=weather_condition,
                description=condition.get("text", ""),
                humidity=int(current.get("humidity", 0)),
                pressure=pressure,
                wind=wind,
                precipitation=precipitation,
                visibility=current.get("vis_km", 10.0),
                uv_index=current.get("uv", 0.0),
                timestamp=datetime.now(),
            )

        except Exception as e:
            logging.error(f"Error parsing WeatherAPI current weather: {e}")
            return None

    def get_current_weather(
        self, city: str, units: str = "metric"
    ) -> Optional[CurrentWeather]:
        """
        Get current weather for a city from WeatherAPI.com.

        Args:
            city: City name
            units: Temperature units (metric, imperial, standard)

        Returns:
            CurrentWeather or None if error
        """
        params = {"q": city, "aqi": "no"}  # We don't need air quality data

        data = self._make_request("current.json", params)
        if not data:
            return None

        return self._parse_current_weather(data)

    def get_forecast(
        self, city: str, days: int = 5, units: str = "metric"
    ) -> Optional[WeatherForecast]:
        """
        Get weather forecast for a city from WeatherAPI.com.

        Args:
            city: City name
            days: Number of days for forecast (max 10 for free tier)
            units: Temperature units

        Returns:
            WeatherForecast or None if error
        """
        # WeatherAPI free tier allows up to 3 days, paid allows up to 10
        days = min(days, 3)  # Limit to 3 days for free tier compatibility

        params = {"q": city, "days": days, "aqi": "no", "alerts": "no"}

        data = self._make_request("forecast.json", params)
        if not data:
            return None

        try:
            location = self._parse_location(data)
            forecast_data = data.get("forecast", {}).get("forecastday", [])

            daily_forecasts = []
            for day_data in forecast_data:
                day = day_data.get("day", {})

                # Parse date
                date_str = day_data.get("date", "")
                try:
                    forecast_date = datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue

                # Temperature data
                min_temp = day.get("mintemp_c", 0.0)
                max_temp = day.get("maxtemp_c", 0.0)
                avg_temp = day.get("avgtemp_c", (min_temp + max_temp) / 2)

                high_temp = Temperature(
                    value=max_temp, unit=TemperatureUnit.CELSIUS, feels_like=max_temp
                )

                low_temp = Temperature(
                    value=min_temp, unit=TemperatureUnit.CELSIUS, feels_like=min_temp
                )

                # Weather condition
                condition = day.get("condition", {})
                condition_code = condition.get("code", 1000)
                weather_condition = self._parse_condition(condition_code)

                # Wind data
                wind = Wind(
                    speed=day.get("maxwind_kph", 0.0) / 3.6,  # Convert kph to m/s
                    direction=0,  # WeatherAPI doesn't provide forecast wind direction
                    gust=None,
                )

                # Precipitation
                precipitation = None
                precip_mm = day.get("totalprecip_mm", 0.0)
                if precip_mm > 0:
                    precipitation = Precipitation(rain_1h=precip_mm, rain_3h=precip_mm)

                # Create forecast day
                forecast_day = WeatherForecastDay(
                    date=forecast_date,
                    temperature_high=high_temp,
                    temperature_low=low_temp,
                    condition=weather_condition,
                    description=condition.get("text", ""),
                    humidity=int(day.get("avghumidity", 0)),
                    wind=wind,
                    precipitation_chance=int(day.get("daily_chance_of_rain", 0)),
                    precipitation=precipitation,
                )

                daily_forecasts.append(forecast_day)

            # Create WeatherForecast object
            return WeatherForecast(
                location=location,
                forecast_days=daily_forecasts,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logging.error(f"Error parsing WeatherAPI forecast: {e}")
            return None

    def search_locations(self, query: str, limit: int = 5) -> List[Location]:
        """
        Search for locations by name using WeatherAPI.com.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of Location objects
        """
        params = {"q": query}

        data = self._make_request("search.json", params)
        if not data or not isinstance(data, list):
            return []

        locations = []
        for i, item in enumerate(data):
            if i >= limit:
                break
            try:
                if isinstance(item, dict):
                    location = Location(
                        name=item.get("name", ""),
                        country=item.get("country", ""),
                        latitude=item.get("lat", 0.0),
                        longitude=item.get("lon", 0.0),
                    )
                    locations.append(location)
            except Exception as e:
                logging.error(f"Error parsing location from WeatherAPI: {e}")
                continue

        return locations

    def get_current_weather_by_coordinates(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> Optional[CurrentWeather]:
        """
        Get current weather for specific coordinates from WeatherAPI.com.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Temperature units

        Returns:
            CurrentWeather or None if error
        """
        # WeatherAPI.com accepts coordinates as "lat,lon" format
        coords = f"{latitude},{longitude}"
        return self.get_current_weather(coords, units)

    def get_forecast_by_coordinates(
        self, latitude: float, longitude: float, days: int = 5, units: str = "metric"
    ) -> Optional[WeatherForecast]:
        """
        Get weather forecast for specific coordinates from WeatherAPI.com.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of days for forecast
            units: Temperature units

        Returns:
            WeatherForecast or None if error
        """
        # WeatherAPI.com accepts coordinates as "lat,lon" format
        coords = f"{latitude},{longitude}"
        return self.get_forecast(coords, days, units)
