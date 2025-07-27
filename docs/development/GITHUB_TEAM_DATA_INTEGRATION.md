# GitHub Team Data Integration

## Overview

The Weather Dashboard has been updated to import team weather data directly from the GitHub
repository: **StrayDogSyn/New_Team_Dashboard**. This enables the Compare Cities feature to use
real collaborative data from team members instead of relying solely on API calls.

## Key Features

### 🌐 Remote Data Access

- **Automatic Download**: Data is automatically downloaded from GitHub repository
- **Fallback Support**: Falls back to API calls if GitHub data is unavailable
- **Local Caching**: Downloaded data is cached locally for performance

### 📊 Team Data Integration

- **Real Team Data**: Uses actual weather data collected by team members
- **Multiple Cities**: Access to 7+ cities with comprehensive weather information
- **Rich Dataset**: 200+ weather records from multiple team members

## Available Cities

Based on the GitHub repository data:

- **Austin, TX** - Hot climate data from Eric
- **Providence, RI** - Northeast weather patterns from Shomari  
- **Rawlins, WY** - Mountain/continental climate
- **Ontario, OR** - Pacific Northwest patterns
- **New York, NY** - Urban Northeast data
- **Miami, FL** - Tropical/subtropical data
- **New Jersey** - Mid-Atlantic patterns (extensive dataset)

## Usage Instructions

### 1. Compare Cities with Team Data

1. **Launch Application**: Run `python main.py`
2. **Navigate to Compare Cities**: Click the "Compare Cities" tab
3. **Enter City Names**: Use cities from the available list above
4. **View Results**: Get enhanced comparisons with team insights

### 2. Refresh Team Data

- **Manual Refresh**: Click the "🔄 Refresh Team Data" button in the Compare Cities tab
- **Automatic Download**: Data is automatically downloaded on first use
- **Status Display**: View data source and availability information

### 3. Team Data Status

The application displays:

- **Data Source**: GitHub repository information
- **Available Cities**: Count and list of cities with data
- **Data Freshness**: Last refresh timestamp
- **Team Summary**: Overall statistics from team data

## Technical Implementation

### Data Sources

**Primary**: GitHub Repository

- Repository: `StrayDogSyn/New_Team_Dashboard`
- CSV Data: `team_weather_data_20250717_204218.csv`
- Analysis Data: `team_compare_cities_data_20250717_204218.json`

**Fallback**: OpenWeatherMap API

- Used when team data is unavailable
- Seamless transition between data sources

### Data Structure

**CSV Format**:

```csv
timestamp,member_name,city,country,temperature,humidity,wind_speed,weather_main,weather_description,...
```

**Key Fields**:

- `city`: City name for comparison
- `temperature`: Temperature in Celsius
- `humidity`: Humidity percentage
- `wind_speed`: Wind speed in m/s
- `weather_main`: Main weather condition
- `member_name`: Team member who contributed data

## Enhanced Compare Cities Features

### Team Insights

- **Data Attribution**: Shows which team members contributed data
- **Collaborative Analysis**: Combines data from multiple sources
- **Rich Comparisons**: More comprehensive than single API calls

### Example Comparison

```text
🏙️ Berlin vs London Team Comparison

Berlin (Team Data):
- Temperature: 24.5°C
- Humidity: 58%
- Condition: Clear sky
- Data Source: Team Member Data

London (Team Data):
- Temperature: 18.0°C  
- Humidity: 78%
- Condition: Partly cloudy
- Data Source: Team Member Data

🔬 Team Insights:
- Temperature difference: 6.5°C (Berlin warmer)
- Data from collaborative team repository
- Enhanced with team member observations
```

## Configuration

### GitHub Repository Settings

```python
# In TeamDataService
github_repo_base = "https://raw.githubusercontent.com/StrayDogSyn/New_Team_Dashboard/main/exports"
csv_filename = "team_weather_data_20250717_204218.csv"
json_filename = "team_compare_cities_data_20250717_204218.json"
```

### Local Storage

- **Exports Directory**: `exports/` (auto-created)
- **Downloaded Files**: Cached for offline use
- **Sample Data**: Created if GitHub unavailable

## Troubleshooting

### Common Issues

**GitHub Download Fails**:

- Check internet connection
- Repository files may have moved
- Application falls back to sample data automatically

**City Not Found**:

- Verify city name spelling matches available cities
- Use exact city names from the available list
- Check team data status for current city list

**Timestamp Parsing Errors**:

- Application handles multiple timestamp formats automatically
- Falls back to current timestamp if parsing fails

### Error Resolution

1. **Refresh Team Data**: Click refresh button to re-download
2. **Check Logs**: Application logs show detailed error information
3. **Fallback Mode**: API mode still available if team data fails

## Development Notes

### Team Data Service Updates

- **Flexible Parsing**: Handles multiple timestamp formats
- **Error Resilience**: Graceful fallback to local/sample data
- **Caching Strategy**: Local storage for performance

### GUI Enhancements

- **Refresh Button**: Manual data refresh capability
- **Status Display**: Real-time team data information
- **Source Attribution**: Clear indication of data source

## Future Enhancements

### Planned Features

- **Automatic Updates**: Periodic refresh from GitHub
- **Multiple Repositories**: Support for additional team data sources
- **Data Validation**: Enhanced verification of team data quality
- **Contribution Tools**: Interface for adding new team data

---

**🌟 The Compare Cities feature now leverages real team collaboration data from GitHub!** 🏙️
