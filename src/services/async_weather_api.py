"""Async OpenWeatherMap API implementation with proper async/await patterns."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import aiohttp
from pydantic import BaseModel, ValidationError

from src.interfaces.weather_interfaces import IAsyncWeatherAPI
from src.models.weather_models import (
    CurrentWeather,
    Location,
    WeatherCondition,
    WeatherForecast,
    ForecastDay,
    Temperature,
    Wind,
    Precipitation,
)
from src.utils.formatters import clean_city_name, validate_city_name
from src.utils.validators import sanitize_input


class AsyncOpenWeatherMapAPI(IAsyncWeatherAPI):
    """Async OpenWeatherMap API implementation with proper error handling."""

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize async OpenWeatherMap API client.

        Args:
            api_key: OpenWeatherMap API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "https://api.openweathermap.org/geo/1.0"
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        
        # Session will be created when needed
        self._session: Optional[aiohttp.ClientSession] = None
        
        logging.info("Async OpenWeatherMap API initialized")

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self):
        """Ensure aiohttp session is created."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,  # Total connection pool size
                limit_per_host=30,  # Per-host connection limit
                ttl_dns_cache=300,  # DNS cache TTL
                use_dns_cache=True,
            )
            
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=self.timeout,
                headers={
                    "User-Agent": "WeatherDashboard/1.0 (Async)",
                    "Accept": "application/json",
                },
            )

    async def close(self):
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def get_current_weather(
        self, city: str, units: str = "metric"
    ) -> Optional[CurrentWeather]:
        """
        Get current weather for a city asynchronously.

        Args:
            city: City name
            units: Temperature units (metric, imperial, standard)

        Returns:
            CurrentWeather or None if error
        """
        if not validate_city_name(city):
            logging.error(f"Invalid city name: {city}")
            return None

        city = clean_city_name(city)
        
        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
        }

        url = f"{self.base_url}/weather"
        
        try:
            data = await self._make_request(url, params)
            if data:
                return self._parse_current_weather(data, units)
            return None
            
        except Exception as e:
            logging.error(f"Error getting current weather for {city}: {e}")
            return None

    async def get_forecast(
        self, city: str, days: int = 5, units: str = "metric"
    ) -> Optional[WeatherForecast]:
        """
        Get weather forecast for a city asynchronously.

        Args:
            city: City name
            days: Number of forecast days (1-16)
            units: Temperature units

        Returns:
            WeatherForecast or None if error
        """
        if not validate_city_name(city):
            logging.error(f"Invalid city name: {city}")
            return None

        if not (1 <= days <= 16):
            logging.error(f"Invalid forecast days: {days}")
            return None

        city = clean_city_name(city)
        
        # Use 5-day forecast endpoint (free tier) or 16-day if available
        if days <= 5:
            endpoint = "forecast"
            cnt = days * 8  # 8 forecasts per day (3-hour intervals)
        else:
            endpoint = "forecast/daily"
            cnt = days

        params = {
            "q": city,
            "appid": self.api_key,
            "units": units,
            "cnt": cnt,
        }

        url = f"{self.base_url}/{endpoint}"
        
        try:
            data = await self._make_request(url, params)
            if data:
                return self._parse_forecast(data, units, days)
            return None
            
        except Exception as e:
            logging.error(f"Error getting forecast for {city}: {e}")
            return None

    async def search_locations(self, query: str, limit: int = 5) -> List[Location]:
        """
        Search for locations by name asynchronously.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of Location objects
        """
        if not query or len(query.strip()) < 2:
            logging.warning("Search query too short")
            return []

        query = sanitize_input(query.strip())
        
        params = {
            "q": query,
            "limit": min(limit, 10),  # API limit
            "appid": self.api_key,
        }

        url = f"{self.geo_url}/direct"
        
        try:
            data = await self._make_request(url, params)
            if data and isinstance(data, list):
                return self._parse_locations(data)
            return []
            
        except Exception as e:
            logging.error(f"Error searching locations for {query}: {e}")
            return []

    async def get_current_weather_by_coordinates(
        self, latitude: float, longitude: float, units: str = "metric"
    ) -> Optional[CurrentWeather]:
        """
        Get current weather by coordinates asynchronously.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            units: Temperature units

        Returns:
            CurrentWeather or None if error
        """
        if not (-90 <= latitude <= 90):
            logging.error(f"Invalid latitude: {latitude}")
            return None
            
        if not (-180 <= longitude <= 180):
            logging.error(f"Invalid longitude: {longitude}")
            return None
        
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": units,
        }

        url = f"{self.base_url}/weather"
        
        try:
            data = await self._make_request(url, params)
            if data:
                return self._parse_current_weather(data, units)
            return None
            
        except Exception as e:
            logging.error(f"Error getting weather for coordinates ({latitude}, {longitude}): {e}")
            return None

    async def get_forecast_by_coordinates(
        self, latitude: float, longitude: float, days: int = 5, units: str = "metric"
    ) -> Optional[WeatherForecast]:
        """
        Get weather forecast by coordinates asynchronously.

        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            days: Number of forecast days
            units: Temperature units

        Returns:
            WeatherForecast or None if error
        """
        if not (-90 <= latitude <= 90):
            logging.error(f"Invalid latitude: {latitude}")
            return None
            
        if not (-180 <= longitude <= 180):
            logging.error(f"Invalid longitude: {longitude}")
            return None
            
        if not (1 <= days <= 16):
            logging.error(f"Invalid forecast days: {days}")
            return None
        
        # Use 5-day forecast endpoint (free tier) or 16-day if available
        if days <= 5:
            endpoint = "forecast"
            cnt = days * 8  # 8 forecasts per day (3-hour intervals)
        else:
            endpoint = "forecast/daily"
            cnt = days

        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": self.api_key,
            "units": units,
            "cnt": cnt,
        }

        url = f"{self.base_url}/{endpoint}"
        
        try:
            data = await self._make_request(url, params)
            if data:
                return self._parse_forecast(data, units, days)
            return None
            
        except Exception as e:
            logging.error(f"Error getting forecast for coordinates ({latitude}, {longitude}): {e}")
            return None

    async def _make_request(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make async HTTP request with proper error handling.

        Args:
            url: Request URL
            params: Request parameters

        Returns:
            JSON response data or None if error
        """
        await self._ensure_session()
        
        try:
            query_string = urlencode(params)
            full_url = f"{url}?{query_string}"
            
            logging.debug(f"Making request to: {url}")
            
            async with self._session.get(url, params=params) as response:
                # Check for HTTP errors
                if response.status == 401:
                    logging.error("Invalid API key")
                    return None
                elif response.status == 404:
                    logging.error("Location not found")
                    return None
                elif response.status == 429:
                    logging.error("API rate limit exceeded")
                    return None
                elif response.status >= 400:
                    logging.error(f"HTTP error {response.status}: {response.reason}")
                    return None
                
                # Parse JSON response
                try:
                    data = await response.json()
                    logging.debug(f"Received response with {len(str(data))} characters")
                    return data
                    
                except aiohttp.ContentTypeError as e:
                    logging.error(f"Invalid JSON response: {e}")
                    return None
                    
        except aiohttp.ClientTimeout:
            logging.error(f"Request timeout for {url}")
            return None
            
        except aiohttp.ClientError as e:
            logging.error(f"Client error for {url}: {e}")
            return None
            
        except Exception as e:
            logging.error(f"Unexpected error for {url}: {e}")
            return None

    def _parse_current_weather(self, data: Dict[str, Any], units: str) -> Optional[CurrentWeather]:
        """
        Parse current weather data from API response.

        Args:
            data: API response data
            units: Temperature units

        Returns:
            CurrentWeather object or None if parsing fails
        """
        try:
            # Parse location
            location = self._parse_location(data)
            if not location:
                return None

            # Parse weather condition
            condition = self._parse_condition(data.get("weather", []))
            if not condition:
                return None

            # Parse temperature
            temperature = self._parse_temperature(data.get("main", {}), units)
            if not temperature:
                return None

            # Parse optional fields
            wind = self._parse_wind(data.get("wind", {}))
            precipitation = self._parse_precipitation(data.get("rain", {}), data.get("snow", {}))
            
            # Parse other fields
            humidity = data.get("main", {}).get("humidity")
            pressure = data.get("main", {}).get("pressure")
            visibility = data.get("visibility")
            uv_index = data.get("uvi")  # Not available in current weather endpoint
            
            # Parse timestamp
            timestamp = None
            if "dt" in data:
                timestamp = datetime.fromtimestamp(data["dt"])

            return CurrentWeather(
                location=location,
                condition=condition,
                temperature=temperature,
                wind=wind,
                precipitation=precipitation,
                humidity=humidity,
                pressure=pressure,
                visibility=visibility,
                uv_index=uv_index,
                timestamp=timestamp,
            )

        except Exception as e:
            logging.error(f"Error parsing current weather data: {e}")
            return None

    def _parse_forecast(self, data: Dict[str, Any], units: str, days: int) -> Optional[WeatherForecast]:
        """
        Parse forecast data from API response.

        Args:
            data: API response data
            units: Temperature units
            days: Number of forecast days

        Returns:
            WeatherForecast object or None if parsing fails
        """
        try:
            # Parse location from city data
            city_data = data.get("city", {})
            location = Location(
                name=city_data.get("name", "Unknown"),
                country=city_data.get("country", "Unknown"),
                latitude=city_data.get("coord", {}).get("lat", 0.0),
                longitude=city_data.get("coord", {}).get("lon", 0.0),
            )

            # Parse forecast list
            forecast_list = data.get("list", [])
            if not forecast_list:
                logging.error("No forecast data in response")
                return None

            forecast_days = self._parse_forecast_days(forecast_list, units, days)
            if not forecast_days:
                logging.error("Failed to parse forecast days")
                return None

            return WeatherForecast(
                location=location,
                forecast_days=forecast_days,
                generated_at=datetime.now(),
            )

        except Exception as e:
            logging.error(f"Error parsing forecast data: {e}")
            return None

    def _parse_forecast_days(self, forecast_list: List[Dict[str, Any]], units: str, days: int) -> List[ForecastDay]:
        """
        Parse forecast days from API forecast list.

        Args:
            forecast_list: List of forecast entries
            units: Temperature units
            days: Number of days to parse

        Returns:
            List of ForecastDay objects
        """
        forecast_days = []
        current_date = None
        daily_temps = []
        daily_conditions = []
        daily_precipitation = []
        daily_wind = []

        try:
            for entry in forecast_list:
                # Parse timestamp
                timestamp = datetime.fromtimestamp(entry.get("dt", 0))
                entry_date = timestamp.date()

                # If new day, process previous day's data
                if current_date and entry_date != current_date:
                    if len(forecast_days) < days:
                        forecast_day = self._create_forecast_day(
                            current_date, daily_temps, daily_conditions, 
                            daily_precipitation, daily_wind, units
                        )
                        if forecast_day:
                            forecast_days.append(forecast_day)
                    
                    # Reset for new day
                    daily_temps = []
                    daily_conditions = []
                    daily_precipitation = []
                    daily_wind = []

                current_date = entry_date

                # Collect data for current day
                main_data = entry.get("main", {})
                if "temp" in main_data:
                    daily_temps.append(main_data["temp"])
                if "temp_max" in main_data:
                    daily_temps.append(main_data["temp_max"])
                if "temp_min" in main_data:
                    daily_temps.append(main_data["temp_min"])

                # Collect weather conditions
                weather_list = entry.get("weather", [])
                if weather_list:
                    daily_conditions.append(weather_list[0])

                # Collect precipitation
                rain_data = entry.get("rain", {})
                snow_data = entry.get("snow", {})
                if rain_data or snow_data:
                    daily_precipitation.append((rain_data, snow_data))

                # Collect wind data
                wind_data = entry.get("wind", {})
                if wind_data:
                    daily_wind.append(wind_data)

            # Process last day
            if current_date and len(forecast_days) < days and daily_temps:
                forecast_day = self._create_forecast_day(
                    current_date, daily_temps, daily_conditions, 
                    daily_precipitation, daily_wind, units
                )
                if forecast_day:
                    forecast_days.append(forecast_day)

            return forecast_days[:days]  # Ensure we don't exceed requested days

        except Exception as e:
            logging.error(f"Error parsing forecast days: {e}")
            return []

    def _create_forecast_day(
        self, 
        date, 
        temps, 
        conditions, 
        precipitation_data, 
        wind_data, 
        units
    ) -> Optional[ForecastDay]:
        """
        Create a ForecastDay from collected daily data.

        Args:
            date: Date for the forecast
            temps: List of temperatures for the day
            conditions: List of weather conditions
            precipitation_data: List of precipitation data
            wind_data: List of wind data
            units: Temperature units

        Returns:
            ForecastDay object or None if creation fails
        """
        try:
            if not temps:
                return None

            # Calculate temperature range
            temp_high = Temperature(value=max(temps), unit=self._get_temp_unit(units))
            temp_low = Temperature(value=min(temps), unit=self._get_temp_unit(units))

            # Get most common condition
            condition = None
            if conditions:
                # Use first condition as representative
                condition_data = conditions[0]
                condition = WeatherCondition(
                    value=condition_data.get("main", "Unknown"),
                    description=condition_data.get("description", ""),
                    icon=condition_data.get("icon", ""),
                )

            # Calculate average wind
            wind = None
            if wind_data:
                avg_speed = sum(w.get("speed", 0) for w in wind_data) / len(wind_data)
                avg_direction = sum(w.get("deg", 0) for w in wind_data) / len(wind_data)
                wind = Wind(
                    speed=avg_speed,
                    direction=avg_direction,
                    unit="m/s" if units == "metric" else "mph",
                )

            # Calculate total precipitation
            precipitation = None
            if precipitation_data:
                total_rain = sum(
                    rain.get("3h", 0) for rain, _ in precipitation_data if rain
                )
                total_snow = sum(
                    snow.get("3h", 0) for _, snow in precipitation_data if snow
                )
                
                if total_rain > 0 or total_snow > 0:
                    precipitation = Precipitation(
                        rain_mm=total_rain,
                        snow_mm=total_snow,
                        probability=None,  # Not available in this endpoint
                    )

            return ForecastDay(
                date=date,
                temperature_high=temp_high,
                temperature_low=temp_low,
                condition=condition,
                wind=wind,
                precipitation=precipitation,
                humidity=None,  # Could calculate average if needed
                uv_index=None,  # Not available in this endpoint
            )

        except Exception as e:
            logging.error(f"Error creating forecast day: {e}")
            return None

    def _parse_location(self, data: Dict[str, Any]) -> Optional[Location]:
        """
        Parse location data from API response.

        Args:
            data: API response data

        Returns:
            Location object or None if parsing fails
        """
        try:
            name = data.get("name")
            if not name:
                logging.error("No city name in response")
                return None

            sys_data = data.get("sys", {})
            country = sys_data.get("country", "Unknown")

            coord_data = data.get("coord", {})
            latitude = coord_data.get("lat", 0.0)
            longitude = coord_data.get("lon", 0.0)

            return Location(
                name=name,
                country=country,
                latitude=latitude,
                longitude=longitude,
            )

        except Exception as e:
            logging.error(f"Error parsing location: {e}")
            return None

    def _parse_locations(self, data: List[Dict[str, Any]]) -> List[Location]:
        """
        Parse multiple locations from geocoding API response.

        Args:
            data: List of location data from API

        Returns:
            List of Location objects
        """
        locations = []
        
        try:
            for item in data:
                name = item.get("name")
                if not name:
                    continue

                # Build display name with state/country
                display_parts = [name]
                if "state" in item:
                    display_parts.append(item["state"])
                if "country" in item:
                    display_parts.append(item["country"])
                
                display_name = ", ".join(display_parts)

                location = Location(
                    name=display_name,
                    country=item.get("country", "Unknown"),
                    latitude=item.get("lat", 0.0),
                    longitude=item.get("lon", 0.0),
                )
                
                locations.append(location)

        except Exception as e:
            logging.error(f"Error parsing locations: {e}")

        return locations

    def _parse_condition(self, weather_list: List[Dict[str, Any]]) -> Optional[WeatherCondition]:
        """
        Parse weather condition from API response.

        Args:
            weather_list: List of weather data

        Returns:
            WeatherCondition object or None if parsing fails
        """
        try:
            if not weather_list:
                logging.error("No weather data in response")
                return None

            weather_data = weather_list[0]  # Use first weather entry
            
            return WeatherCondition(
                value=weather_data.get("main", "Unknown"),
                description=weather_data.get("description", ""),
                icon=weather_data.get("icon", ""),
            )

        except Exception as e:
            logging.error(f"Error parsing weather condition: {e}")
            return None

    def _parse_temperature(self, main_data: Dict[str, Any], units: str) -> Optional[Temperature]:
        """
        Parse temperature data from API response.

        Args:
            main_data: Main weather data section
            units: Temperature units

        Returns:
            Temperature object or None if parsing fails
        """
        try:
            temp_value = main_data.get("temp")
            if temp_value is None:
                logging.error("No temperature data in response")
                return None

            temp_unit = self._get_temp_unit(units)
            
            return Temperature(
                value=float(temp_value),
                unit=temp_unit,
                feels_like=main_data.get("feels_like"),
            )

        except (ValueError, TypeError) as e:
            logging.error(f"Error parsing temperature: {e}")
            return None

    def _parse_wind(self, wind_data: Dict[str, Any]) -> Optional[Wind]:
        """
        Parse wind data from API response.

        Args:
            wind_data: Wind data section

        Returns:
            Wind object or None if no wind data
        """
        try:
            if not wind_data:
                return None

            speed = wind_data.get("speed")
            if speed is None:
                return None

            return Wind(
                speed=float(speed),
                direction=wind_data.get("deg"),
                unit="m/s",  # OpenWeatherMap uses m/s for metric
            )

        except (ValueError, TypeError) as e:
            logging.error(f"Error parsing wind data: {e}")
            return None

    def _parse_precipitation(self, rain_data: Dict[str, Any], snow_data: Dict[str, Any]) -> Optional[Precipitation]:
        """
        Parse precipitation data from API response.

        Args:
            rain_data: Rain data section
            snow_data: Snow data section

        Returns:
            Precipitation object or None if no precipitation
        """
        try:
            rain_mm = 0.0
            snow_mm = 0.0

            # Parse rain data (1h or 3h)
            if rain_data:
                rain_mm = rain_data.get("1h", rain_data.get("3h", 0.0))

            # Parse snow data (1h or 3h)
            if snow_data:
                snow_mm = snow_data.get("1h", snow_data.get("3h", 0.0))

            # Return precipitation object if any precipitation exists
            if rain_mm > 0 or snow_mm > 0:
                return Precipitation(
                    rain_mm=rain_mm,
                    snow_mm=snow_mm,
                    probability=None,  # Not available in current weather
                )

            return None

        except (ValueError, TypeError) as e:
            logging.error(f"Error parsing precipitation data: {e}")
            return None

    def _get_temp_unit(self, units: str) -> str:
        """
        Get temperature unit string based on API units parameter.

        Args:
            units: API units parameter

        Returns:
            Temperature unit string
        """
        unit_map = {
            "metric": "°C",
            "imperial": "°F",
            "standard": "K",
        }
        return unit_map.get(units, "°C")

    def __del__(self):
        """Cleanup when object is destroyed."""
        if self._session and not self._session.closed:
            # Create a new event loop if none exists for cleanup
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Schedule cleanup for later
                    loop.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except RuntimeError:
                # No event loop available, create one for cleanup
                asyncio.run(self.close())