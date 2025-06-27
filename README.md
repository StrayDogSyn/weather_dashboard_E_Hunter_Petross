# 🌤️ Weather Dashboard - TKinter GUI

A modern weather dashboard application with glassmorphic design, built using Python TKinter. Features comprehensive weather data, capstone functionality, and an intuitive graphical interface.

## 🌟 Capstone Features

### Core Weather Features

- **🌡️ Current Weather**: Real-time weather conditions for any city
- **📅 Weather Forecast**: Detailed multi-day weather forecasts  
- **⭐ Favorite Cities**: Save and manage your preferred locations

### Advanced Capstone Features

- **🌍 City Comparison**: Side-by-side weather comparison between cities
- **📔 Weather Journal**: Track daily weather with mood and activity logging
- **🎯 Activity Suggestions**: Weather-based activity recommendations
- **🎨 Weather Poetry**: AI-generated poems inspired by current weather
- **💾 Data Management**: Intelligent caching and data storage

### Modern GUI Design

- **🎨 Glassmorphic Interface**: Modern dark theme with glass-like effects
- **📱 Responsive Layout**: Tabbed interface with intuitive navigation
- **🎯 Interactive Elements**: Custom styled buttons and smooth interactions
- **📊 Data Visualization**: Beautiful weather cards and information displays

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (TKinter included by default)
- OpenWeatherMap API key ([Get free key](https://openweathermap.org/api))

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd weather_dashboard_E_Hunter_Petross
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key**

   ```bash
   # Copy the example configuration
   copy .env.example .env
   
   # Edit .env and add your API key
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

4. **Launch the GUI**

   ```bash
   python main.py
   ```

## 🎨 GUI Features

### Main Interface

- **Weather Tab**: Current conditions with detailed metrics
- **Forecast Tab**: Multi-day weather predictions
- **Comparison Tab**: Compare weather between two cities
- **Journal Tab**: Create and view weather journal entries
- **Activities Tab**: Get weather-appropriate activity suggestions
- **Poetry Tab**: Generate weather-inspired poems
- **Favorites Tab**: Manage and view favorite cities

### Design Elements

- **Dark glassmorphic theme** with transparency effects
- **Custom styled buttons** with hover animations  
- **Modern typography** using Segoe UI font
- **Responsive layout** that adapts to window size
- **Color-coded information** for easy reading

## 📱 Using the Application

### Getting Weather Data

1. Enter a city name in the search box
2. Click "Get Weather" or press Enter
3. View current conditions and forecast
4. Add cities to favorites for quick access

### Capstone Features

- **City Comparison**: Enter two cities to compare their weather
- **Journal Entries**: Record daily weather observations and mood
- **Activity Suggestions**: Get personalized recommendations based on weather
- **Weather Poetry**: Generate creative poems inspired by current conditions

## 🛠️ Technical Details

### Architecture

- **Clean separation of concerns** with modular design
- **Model-View-Controller** pattern for GUI architecture
- **Service layer** for weather API integration
- **Data persistence** for favorites and journal entries

### Dependencies

- **TKinter**: Built-in Python GUI framework
- **requests**: HTTP client for weather API
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and modeling

### File Structure

```text
weather_dashboard_E_Hunter_Petross/
├── main.py                 # Main application entry point
├── run_gui.py              # Simplified GUI launcher
├── src/
│   ├── ui/
│   │   └── gui_interface.py # TKinter GUI implementation
│   ├── core/               # Core business logic
│   ├── services/           # External service integrations
│   ├── models/            # Data models and schemas
│   └── config/            # Configuration management
├── requirements.txt       # Python dependencies
└── .env.example          # Environment configuration template
```

## 🌟 Capstone Highlights

This project demonstrates:

- **Modern GUI Development** with TKinter and custom styling
- **API Integration** with proper error handling and caching
- **Data Management** with models, validation, and persistence
- **User Experience Design** with intuitive interface and features
- **Code Organization** following clean architecture principles

## 🚀 Future Enhancements

Potential additions:

- **Weather maps** integration
- **Notification system** for weather alerts
- **Export functionality** for journal and data
- **Customizable themes** and color schemes
- **Weather widgets** for desktop integration

---

**Author**: E Hunter Petross  
**Project**: Weather Dashboard Capstone  
**Technology**: Python, TKinter, OpenWeatherMap API

## 🏗️ Architecture

This project implements Clean Architecture with clear separation of concerns:

- **`src/models/`** - Domain entities and value objects
- **`src/core/`** - Business logic and use cases
- **`src/services/`** - External service integrations
- **`src/interfaces/`** - Abstract interfaces for dependency inversion
- **`src/config/`** - Configuration management
- **`src/ui/`** - User interface layer
- **`src/utils/`** - Utility functions and helpers

## 🧪 Testing

Testing framework setup is ready for future implementation:

```bash
# Install testing dependencies (when needed)
pip install pytest pytest-cov

# Run tests (when test suite is implemented)
python -m pytest tests/ -v
```

## 📚 Documentation

- [Architecture Documentation](docs/architecture.md) - Detailed architecture overview
- [Security Guidelines](docs/security.md) - Security best practices
- [User Guide](docs/user_guide.md) - Detailed usage instructions
- [Project Structure](docs/project_structure.md) - Complete project organization
- [Refactor Summary](docs/refactor_complete.md) - Recent improvements and changes

## 🔐 Security

- API keys are stored securely in environment variables
- No sensitive data is logged or exposed
- Input validation and sanitization
- Secure configuration management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenWeatherMap for providing the weather API
- Python community for excellent libraries
- Clean Architecture principles by Robert C. Martin
