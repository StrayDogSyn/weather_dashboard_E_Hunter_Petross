# Weather Dashboard User Guide

This guide will help you set up and use the Weather Dashboard application.

## 🚀 Quick Start

### Step 1: Get Your API Key

1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for a free account
3. Go to the API keys section
4. Copy your API key

### Step 2: Configure the Application

Choose one of these methods to set your API key:

#### Method A: Environment Variable (Recommended)

**Windows PowerShell:**
```powershell
$env:OPENWEATHER_API_KEY="your_actual_api_key_here"
```

**Windows Command Prompt:**
```cmd
set OPENWEATHER_API_KEY=your_actual_api_key_here
```

**For permanent setup, add to Windows environment variables:**
1. Open System Properties → Advanced → Environment Variables
2. Add new user variable:
   - Name: `OPENWEATHER_API_KEY`
   - Value: `your_actual_api_key_here`

#### Method B: Edit Configuration File

1. Open `config.py` in a text editor
2. Find this line:
   ```python
   OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'your_api_key_here')
   ```
3. Replace `'your_api_key_here'` with your actual API key:
   ```python
   OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', 'abc123xyz789')
   ```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python main.py
```

## 📱 Using the Application

### Current Weather
1. Select option 1 from the menu
2. Enter the name of any city
3. View current temperature, humidity, and weather conditions

### Weather Forecast
1. Select option 2 from the menu
2. Enter the name of any city
3. View the 5-day weather forecast

### Favorite Cities
1. Select option 4 to add cities to your favorites
2. Select option 3 to view your favorite cities
3. Quickly check weather for cities you visit frequently

## 🔧 Configuration Options

### Changing Default Settings

Edit `config.py` to customize:

- **Default City**: Change `DEFAULT_CITY = "New York"` to your preferred city
- **Temperature Units**: 
  - `"metric"` for Celsius (default)
  - `"imperial"` for Fahrenheit
  - `"standard"` for Kelvin
- **Refresh Interval**: How often data updates (in seconds)

### Available Features

The application can be configured to enable/disable features:

```python
FEATURES = {
    "current_weather": True,      # Current weather display
    "forecast": True,             # Weather forecast
    "weather_map": True,          # Weather maps (coming soon)
    "historical_data": False,     # Historical weather data
    "alerts": True,               # Weather alerts (coming soon)
    "favorites": True             # Favorite cities
}
```

## 🎨 Customization

### Theme Settings

```python
THEME = "light"  # Options: "light", "dark"
```

### Window Settings (for future GUI)

```python
WINDOW_SIZE = (1200, 800)        # Width, height in pixels
MIN_WINDOW_SIZE = (800, 600)     # Minimum window size
```

### Color Scheme

Customize colors in the `UIConfig` class:

```python
COLORS = {
    "primary": "#2196F3",     # Main accent color
    "secondary": "#FF9800",   # Secondary accent
    "success": "#4CAF50",     # Success messages
    "warning": "#FF5722",     # Warning messages
    "background": "#FFFFFF",  # Background color
    "text": "#333333"         # Text color
}
```

## 🔍 Troubleshooting

### Common Issues

#### "Invalid API key" Error
- Double-check your API key is correct
- Ensure there are no extra spaces
- Wait a few minutes if you just created the API key

#### "City not found" Error
- Check the spelling of the city name
- Try using the format "City, Country" (e.g., "London, UK")
- Some cities may require the state/province (e.g., "Portland, OR")

#### "Connection error"
- Check your internet connection
- Verify firewall settings allow the application
- Try again in a few moments

#### "Rate limit exceeded"
- Free API keys have usage limits
- Wait a few minutes before making more requests
- Consider upgrading your API plan for higher limits

### Debug Mode

Enable debug mode for detailed logging:

1. Set environment variable: `DEBUG=true`
2. Or edit config.py: `DEBUG = True`

This will show detailed information about API requests and responses.

### Log Files

The application creates a log file `weather_dashboard.log` that contains:
- Application startup information
- API request details
- Error messages and stack traces
- User actions and responses

## 🆘 Getting Help

### Check the Logs
Look at `weather_dashboard.log` for detailed error information.

### API Documentation
- [OpenWeatherMap API Documentation](https://openweathermap.org/api)
- [Current Weather API](https://openweathermap.org/current)
- [5-Day Forecast API](https://openweathermap.org/forecast5)

### Common API Error Codes
- **401**: Invalid API key
- **404**: City not found
- **429**: Too many requests (rate limit)
- **500**: Server error (try again later)

## 🔮 Future Features

The following features are planned for future releases:

- **Graphical User Interface**: Replace CLI with modern GUI
- **Weather Maps**: Visual weather overlays
- **Weather Alerts**: Notifications for severe weather
- **Historical Data**: Access to past weather information
- **Multiple Locations**: Track weather for multiple cities simultaneously
- **Weather Charts**: Temperature and precipitation graphs
- **Export Data**: Save weather data to CSV files

## 📊 Data Storage

### Cache Directory
Weather data is cached in the `data/` directory to:
- Reduce API calls
- Improve response times
- Work offline with recent data

### Data Retention
- Current weather: Cached for 10 minutes
- Forecast data: Cached for 1 hour
- Favorite cities: Saved permanently

### Clearing Cache
Delete files in the `data/` directory to clear cached weather information.

---

**Need more help?** Check the main README.md file or the application logs for additional information.
