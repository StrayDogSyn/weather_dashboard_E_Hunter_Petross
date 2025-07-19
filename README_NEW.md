# 🌤️ Weather Dashboard

A modern, feature-rich weather dashboard built with Python and TKinter, following clean architecture principles and best practices.

## ✨ Features

### Core Weather Functionality
- **Real-time Weather Data** - Current conditions and forecasts via OpenWeatherMap API
- **City Comparison** - Side-by-side weather comparison between multiple cities
- **Smart Data Sources** - Intelligent fallback between team data and live API
- **Interactive Charts** - Visual weather data with matplotlib integration

### Enhanced Features
- **Weather Journal** - Daily weather tracking with mood logging
- **Activity Suggestions** - Weather-based activity recommendations  
- **Weather Poetry** - AI-generated poems inspired by current conditions
- **Sound Effects** - Audio feedback for interactions and weather events
- **Predictive Models** - Machine learning weather predictions (optional)

### Technical Excellence
- **Clean Architecture** - Well-organized, maintainable codebase
- **Multiple Storage** - JSON files, SQLite database with automatic migration
- **Comprehensive Testing** - Unit tests for all core functionality
- **Modern UI** - Glassmorphic design with dark theme
- **Performance Optimized** - Intelligent caching and async operations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- OpenWeatherMap API key (free at [openweathermap.org](https://openweathermap.org/api))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/StrayDogSyn/weather_dashboard_E_Hunter_Petross.git
   cd weather_dashboard_E_Hunter_Petross
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   # Edit .env and add your OpenWeatherMap API key
   ```

5. **Launch the application**
   ```bash
   python main.py
   ```

## 🏗️ Architecture

The project follows **Clean Architecture** principles with clear separation of concerns:

```
src/
├── 📁 models/           # Domain entities and value objects
├── 📁 core/             # Business logic and use cases  
├── 📁 services/         # External service integrations
├── 📁 ui/               # User interface components
├── 📁 config/           # Configuration management
├── 📁 utils/            # Utility functions and helpers
└── 📁 interfaces/       # Abstract interfaces for dependency inversion
```

### Key Design Patterns
- **Repository Pattern** - Abstract data access
- **Service Layer** - Business logic encapsulation
- **Dependency Injection** - Loose coupling between components
- **Factory Pattern** - Object creation abstraction

## 🛠️ Development

### Code Quality Tools
```bash
# Format code
black src/

# Sort imports  
isort src/

# Lint code
flake8 src/

# Run tests
pytest tests/
```

### Project Configuration
- **pyproject.toml** - Modern Python project configuration
- **Black** - Code formatting (88 character line length)
- **isort** - Import sorting
- **flake8** - Linting with sensible ignore rules
- **pytest** - Testing framework with coverage

## 📊 Data Management

### Storage Options
- **SQLite Database** - Primary storage for better performance
- **JSON Files** - Backup storage and data portability
- **Automatic Backups** - Daily JSON backups of critical data
- **Smart Migration** - Seamless transition between storage methods

### Data Sources
- **OpenWeatherMap API** - Live weather data
- **Team Data Integration** - Collaborative weather data sharing
- **Local Caching** - Reduced API calls and offline functionality

## 🧪 Testing

Comprehensive test suite covering:
- **Unit Tests** - Individual component testing
- **Integration Tests** - Service interaction testing  
- **Model Validation** - Data structure integrity
- **Error Handling** - Graceful failure scenarios

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
WEATHER_API_KEY=your_openweathermap_api_key

# Optional
WEATHER_DEFAULT_CITY=New York
WEATHER_DEBUG=false
WEATHER_CACHE_TTL=300
```

### Application Settings
Configure via `settings.json`:
```json
{
  "ui": {
    "theme": "dark",
    "sound_enabled": true,
    "auto_refresh": true
  },
  "data": {
    "use_database": true,
    "backup_enabled": true,
    "cache_size": 100
  }
}
```

## 📈 Performance

### Optimizations
- **Intelligent Caching** - TTL-based with automatic cleanup
- **Async Operations** - Non-blocking API calls
- **Data Compression** - Efficient storage formats  
- **Resource Management** - Automatic cleanup of unused resources

### Monitoring
- **Comprehensive Logging** - Debug, info, warning, and error levels
- **Performance Metrics** - API response times and cache hit rates
- **Error Tracking** - Detailed error reporting and recovery

## 🎨 User Interface

### Modern Design
- **Glassmorphic Theme** - Modern, translucent design elements
- **Dark Mode** - Easy on the eyes for extended use
- **Responsive Layout** - Adapts to different screen sizes
- **Intuitive Navigation** - Tabbed interface with keyboard shortcuts

### Accessibility
- **Keyboard Navigation** - Full keyboard support (Ctrl+1-4 for tabs)
- **Clear Typography** - Readable fonts and appropriate sizing
- **Color Contrast** - High contrast for better visibility
- **Audio Feedback** - Optional sound effects for interactions

## 🔮 Machine Learning

### Predictive Models (Optional)
- **Temperature Forecasting** - ML-based temperature predictions
- **Weather Pattern Recognition** - Seasonal trend analysis
- **Model Training** - Automatic retraining with new data
- **Confidence Scoring** - Prediction reliability metrics

### Supported Algorithms
- **Linear Regression** - Simple, interpretable baseline
- **Random Forest** - Ensemble method for robust predictions
- **Gradient Boosting** - Advanced ensemble for high accuracy

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the coding standards
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines
- Follow **PEP 8** style guidelines (enforced by Black)
- Write **comprehensive tests** for new features
- Update **documentation** for any API changes
- Use **meaningful commit messages** following conventional commits

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenWeatherMap** - Weather data API
- **Python Community** - Amazing ecosystem and libraries
- **TKinter** - Built-in GUI framework for Python
- **scikit-learn** - Machine learning library
- **SQLAlchemy** - Python SQL toolkit and ORM

## 🔗 Links

- **Repository**: [GitHub](https://github.com/StrayDogSyn/weather_dashboard_E_Hunter_Petross)
- **Issues**: [Bug Reports](https://github.com/StrayDogSyn/weather_dashboard_E_Hunter_Petross/issues)
- **API Documentation**: [OpenWeatherMap](https://openweathermap.org/api)

---

**Built with ❤️ using Python and modern software engineering practices.**
