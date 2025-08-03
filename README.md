# 🌤️ Professional Weather Dashboard

![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A modern, professional weather dashboard application built with Python and CustomTkinter. Features real-time weather data, interactive maps, AI-powered analytics, and a dynamic theme system.

> **📋 Status**: ✅ Production Ready | 🎨 Multi-Theme | 🔬 ML Analytics | 🛠️ Clean Architecture

**Author**: E Hunter Petross | **Project**: Weather Dashboard Capstone | **Technology**: Python, CustomTkinter, OpenWeatherMap API

## **Screenshots**

![Weather Dashboard Screenshot](assets/images/Main.png)

## ✨ Core Features

### 🌤️ Weather Data & Display

- **Real-time weather conditions** for any city worldwide
- **5-day detailed forecasts** with hourly breakdowns
- **Enhanced weather metrics** including humidity, wind speed, pressure, and UV index
- **Temperature unit conversion** (Celsius/Fahrenheit) with persistent preferences
- **Location search** with autocomplete and recent searches
- **Weather alerts** and severe weather notifications
- **Air quality data** with health recommendations
- **Astronomical information** including sunrise, sunset, and moon phases

### 🗺️ Interactive Maps

- **Weather layer visualization** with temperature, precipitation, and wind data
- **Regional weather panels** for comprehensive area coverage
- **Radar simulation** for precipitation tracking
- **Map location search** with coordinate support
- **Weather station data** integration

### 🧠 AI-Powered Analytics

- **ML Weather Analysis**: Machine learning algorithms for weather pattern recognition
- **City Comparison**: AI-driven similarity analysis with heatmap visualizations
- **Weather Clustering**: Intelligent grouping of cities by weather patterns
- **Radar Charts**: Multi-dimensional weather profile comparisons
- **Smart Insights**: AI-generated recommendations and pattern explanations

### 🎯 Activity Recommendations

- **AI-Powered Suggestions**: Intelligent activity recommendations using OpenAI and Google Gemini APIs
- **Weather-Specific Activities**: Tailored suggestions for different weather conditions
- **Advanced Filtering**: Cost, accessibility, duration, and equipment filtering
- **Fallback System**: Robust offline suggestions when AI services are unavailable
- **Smart Caching**: Intelligent caching with proper invalidation

### 🎨 Dynamic Theme System

- **6 Professional Themes**: Matrix, Cyberpunk, Arctic, Solar, Terminal, Midnight
- **Live Theme Switching**: Instant theme changes without restart
- **Chart Theme Integration**: All visualizations automatically adapt to selected theme
- **Consistent Styling**: Unified color schemes across all components

### 🔧 Technical Features

- **Clean Architecture** with dependency injection and repository patterns
- **Type Safety** with comprehensive type hints and validation
- **Async Support** for non-blocking operations
- **SQLite database** with repository pattern for data persistence
- **Intelligent caching** with configurable TTL
- **Custom exceptions** for structured error handling
- **Comprehensive logging** with rotating file handlers
- **Cross-platform** compatibility

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ with tkinter
- [OpenWeatherMap API key](https://openweathermap.org/api) (free)

### Installation

```bash
# 1. Clone and navigate
git clone <repository-url>
cd weather_dashboard_E_Hunter_Petross

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API keys (create .env file in root directory)
OPENWEATHER_API_KEY=your_openweather_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional for AI activity suggestions
GEMINI_API_KEY=your_gemini_key_here  # Optional for enhanced AI features

# 5. Run application
python main.py
```

> 📚 **API Key**: Get your free API key from [OpenWeatherMap](https://openweathermap.org/api) and add it to your .env file

## 🎨 Interface Overview

### Navigation Tabs

- **Weather** - Current conditions and enhanced meteorological data
- **🏙️ Team Compare** - Traditional multi-city weather comparison
- **🧠 AI Analysis** - AI-powered weather analytics with clustering and similarity analysis
- **Activities** - Weather-based suggestions with AI recommendations
- **Maps** - Interactive weather maps with multiple layers
- **Settings** - Application configuration and preferences

### Design Highlights

- **🎨 6 Professional Themes**: Matrix (green terminal), Cyberpunk (neon purple), Arctic (ice blue), Solar (warm orange), Terminal (classic green), Midnight (deep purple)
- **Live Theme Switching** with instant visual updates across all components
- **Professional typography** using JetBrains Mono font family
- **Responsive layout** that adapts to window size and theme changes
- **Dynamic hover effects** that match selected theme colors
- **Theme-synchronized data visualization** with consistent color schemes

## 📱 Usage

### Basic Operations

1. Enter city name → Click "Get Weather"
2. Navigate tabs for different features
3. Toggle temperature units (°C/°F)
4. Save cities to favorites for quick access

### Keyboard Shortcuts

- **Ctrl+1** - Temperature trends chart
- **Ctrl+2** - Weather metrics comparison
- **Ctrl+3** - Forecast visualization
- **Ctrl+4** - Humidity/pressure data

### Advanced Features

- **🤖 ML Weather Analysis** - AI-powered pattern recognition and clustering
- **📊 Similarity Heatmaps** - Visual correlation analysis between cities
- **🎯 Weather Clustering** - Intelligent grouping with K-means algorithms
- **📈 Radar Charts** - Multi-dimensional weather profile comparisons
- **🌍 Enhanced City Comparison** - Traditional and AI-powered analysis modes
- **🎯 Enhanced Activity Suggestions** - AI-powered recommendations with filtering
- **🎨 Live Theme System** - 6 professional themes with instant switching

## 🛠️ Technical Stack

### Core Dependencies

```txt
# UI Framework
customtkinter==5.2.2          # Modern UI framework
ttkbootstrap==1.10.1          # Bootstrap-themed widgets

# Data & Visualization
matplotlib==3.8.2             # Charts and visualizations
seaborn==0.13.0               # Statistical plotting
plotly==5.17.0                # Interactive charts
numpy==1.24.4                 # Numerical computing
pandas==2.1.4                 # Data analysis
scipy==1.11.4                 # Scientific computing

# Machine Learning
scikit-learn==1.3.2           # ML algorithms (clustering, PCA)
joblib==1.3.2                 # Model persistence

# API & Networking
requests==2.31.0              # HTTP client
aiohttp==3.9.1                # Async HTTP client
httpx==0.25.2                 # Modern HTTP client

# Configuration & Environment
python-dotenv==1.0.0          # Environment management
pydantic==2.5.2               # Data validation
pyyaml==6.0.1                 # YAML parsing

# Geolocation
geopy==2.4.1                  # Geocoding services
geocoder==1.38.1              # Alternative geocoding
timezonefinder==6.2.0         # Timezone lookup

# AI Integration
openai==1.6.1                 # OpenAI API client
google-generativeai==0.3.2    # Google Gemini AI

# Utilities
Pillow==10.1.0                # Image processing
loguru==0.7.2                 # Enhanced logging
rich==13.7.0                  # Rich text formatting
cachetools==5.3.2             # Caching utilities
ratelimit==2.2.1              # API rate limiting
```

### Project Structure

```text
weather_dashboard_E_Hunter_Petross/
├── src/                    # Source code
│   ├── config/            # Configuration management
│   ├── models/            # Data models
│   ├── services/          # Business logic & APIs
│   │   ├── activity_service.py        # Activity suggestions
│   │   ├── config_service.py          # Configuration management
│   │   ├── enhanced_weather_service.py # Weather API integration
│   │   ├── geocoding_service.py       # Location services
│   │   ├── github_team_service.py     # Team data integration
│   │   ├── ml_weather_service.py      # AI/ML analytics engine
│   │   └── maps_service.py            # Interactive maps
│   ├── ui/               # GUI components
│   │   ├── components/   # Reusable UI components
│   │   ├── dashboard/    # Dashboard tab managers
│   │   ├── maps/         # Interactive map components
│   │   ├── styles/       # UI styling and themes
│   │   └── professional_weather_dashboard.py # Main dashboard
│   └── utils/            # Utility functions
├── assets/               # Static resources
├── cache/                # Runtime cache
├── config/               # Configuration files
├── data/                 # Application data
├── docs/                 # Documentation
├── scripts/              # Development tools
├── main.py              # Application entry point
├── requirements.txt     # Production dependencies
└── README.md           # This documentation
```

## 🏗️ Architecture

The Weather Dashboard follows clean architecture principles with modular design and separation of concerns:

### Core Components

- **`src/config/`** - Application configuration management with environment variable support
- **`src/models/`** - Data models and domain entities (WeatherData, location models, etc.)
- **`src/services/`** - Business logic layer (weather, configuration, geocoding, activity services)
- **`src/ui/`** - User interface components and main dashboard
- **`src/utils/`** - Utility functions and loading management

### Key Patterns

- **Service Layer Architecture**: Clean separation between UI, business logic, and data
- **Configuration Management**: Centralized settings with environment variable support
- **Component-Based UI**: Modular CustomTkinter components for reusability
- **Caching Strategy**: Intelligent data caching for performance optimization
- **Theme Observer Pattern**: Real-time theme switching across all components

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Detailed architecture documentation
- **[API_GUIDE.md](docs/API_GUIDE.md)** - API integration and internal interfaces
- **[WORKS_CITED.md](docs/WORKS_CITED.md)** - Comprehensive citations for all external resources
- **[FINAL_REFLECTION.md](docs/FINAL_REFLECTION.md)** - Project reflection and lessons learned

## 🔒 Security

- **API key protection** with environment variables
- **Input validation** and sanitization
- **Secure error handling** without information disclosure
- **Comprehensive logging** for security monitoring

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes with tests
4. Run quality checks: `python scripts/pre_commit_check.py`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push and open Pull Request

**Standards**: PEP 8, 80%+ test coverage, type hints, conventional commits

## 📄 License

MIT License - This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **[OpenWeatherMap](https://openweathermap.org/)** - Weather data API
- **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - Modern GUI framework
- **Python Community** - Excellent libraries and documentation

---

**Author**: E Hunter Petross | **Technology**: Python, CustomTkinter, OpenWeatherMap API | **License**: MIT
