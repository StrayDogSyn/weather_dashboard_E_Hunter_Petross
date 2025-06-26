"""
Weather API Module
Handles all weather-related API calls and data processing
"""

import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json

from config import WeatherAPIConfig, ErrorConfig

class WeatherAPI:
    """Weather API handler for OpenWeatherMap"""
    
    def __init__(self):
        self.api_key = WeatherAPIConfig.OPENWEATHER_API_KEY
        self.base_url = WeatherAPIConfig.OPENWEATHER_BASE_URL
        self.session = requests.Session()
        
        # Setup session headers
        self.session.headers.update({
            'User-Agent': 'WeatherDashboard/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make an API request with error handling
        
        Args:
            endpoint (str): API endpoint
            params (dict): Request parameters
            
        Returns:
            dict: API response data or None if error
        """
        # Add API key to parameters
        params['appid'] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(
                url, 
                params=params, 
                timeout=ErrorConfig.TIMEOUT
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logging.error("Request timeout")
            return None
        except requests.exceptions.ConnectionError:
            logging.error("Connection error")
            return None
        except requests.exceptions.HTTPError as e:
            if hasattr(e, 'response') and e.response is not None:
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
    
    def get_current_weather(self, city: str, units: str = "metric") -> Optional[Dict[str, Any]]:
        """
        Get current weather for a city
        
        Args:
            city (str): City name
            units (str): Temperature units (metric, imperial, standard)
            
        Returns:
            dict: Weather data or None if error
        """
        params = {
            'q': city,
            'units': units
        }
        
        data = self._make_request('weather', params)
        if not data:
            return None
        
        # Process and format the data
        processed_data = {
            'city': data['name'],
            'country': data['sys']['country'],
            'temperature': data['main']['temp'],
            'feels_like': data['main']['feels_like'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'description': data['weather'][0]['description'].title(),
            'icon': data['weather'][0]['icon'],
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'wind_direction': data.get('wind', {}).get('deg', 0),
            'visibility': data.get('visibility', 0) / 1000 if data.get('visibility') else 0,  # Convert to km
            'timestamp': datetime.now().isoformat(),
            'units': units
        }
        
        return processed_data
    
    def get_forecast(self, city: str, units: str = "metric") -> Optional[Dict[str, Any]]:
        """
        Get 5-day weather forecast for a city
        
        Args:
            city (str): City name
            units (str): Temperature units (metric, imperial, standard)
            
        Returns:
            dict: Forecast data or None if error
        """
        params = {
            'q': city,
            'units': units
        }
        
        data = self._make_request('forecast', params)
        if not data:
            return None
        
        # Process forecast data
        forecast_list = []
        for item in data['list']:
            forecast_item = {
                'datetime': item['dt_txt'],
                'temperature': item['main']['temp'],
                'feels_like': item['main']['feels_like'],
                'humidity': item['main']['humidity'],
                'pressure': item['main']['pressure'],
                'description': item['weather'][0]['description'].title(),
                'icon': item['weather'][0]['icon'],
                'wind_speed': item.get('wind', {}).get('speed', 0),
                'precipitation': item.get('rain', {}).get('3h', 0) + item.get('snow', {}).get('3h', 0)
            }
            forecast_list.append(forecast_item)
        
        processed_data = {
            'city': data['city']['name'],
            'country': data['city']['country'],
            'forecast': forecast_list,
            'units': units,
            'timestamp': datetime.now().isoformat()
        }
        
        return processed_data
    
    def get_weather_by_coordinates(self, lat: float, lon: float, units: str = "metric") -> Optional[Dict[str, Any]]:
        """
        Get current weather by coordinates
        
        Args:
            lat (float): Latitude
            lon (float): Longitude
            units (str): Temperature units
            
        Returns:
            dict: Weather data or None if error
        """
        params = {
            'lat': lat,
            'lon': lon,
            'units': units
        }
        
        return self._make_request('weather', params)

# Example usage functions for testing
def test_weather_api():
    """Test the weather API functionality"""
    api = WeatherAPI()
    
    # Test current weather
    print("Testing current weather...")
    weather = api.get_current_weather("London")
    if weather:
        print(f"Weather in {weather['city']}: {weather['temperature']}°C, {weather['description']}")
    else:
        print("Failed to get weather data")
    
    # Test forecast
    print("\nTesting forecast...")
    forecast = api.get_forecast("London")
    if forecast:
        print(f"Forecast for {forecast['city']}:")
        for item in forecast['forecast'][:3]:  # Show first 3 items
            print(f"  {item['datetime']}: {item['temperature']}°C, {item['description']}")
    else:
        print("Failed to get forecast data")

if __name__ == "__main__":
    test_weather_api()
