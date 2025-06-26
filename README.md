# Weather Dashboard

A professional weather dashboard application built with clean architecture principles using Python.

## 🌟 Features

- **Current Weather**: Real-time weather information for any city
- **Weather Forecast**: Detailed weather forecasts
- **Favorite Cities**: Save and manage your favorite locations
- **Data Caching**: Efficient caching to minimize API calls
- **Secure Configuration**: Environment-based configuration management
- **Professional UI**: Modern command-line interface

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenWeatherMap API key (free from [openweathermap.org](https://openweathermap.org/api))

### Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd weather_dashboard_E_Hunter_Petross
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key**

   ```bash
   # Copy the template
   cp .env.example .env
   
   # Edit .env and add your API key
   OPENWEATHER_API_KEY=your_api_key_here
   ```

4. **Run the application**

   ```bash
   python main.py
   ```

## 🏗️ Architecture

This project implements Clean Architecture with clear separation of concerns:

- **`src/models/`** - Domain entities and value objects
- **`src/core/`** - Business logic and use cases
- **`src/services/`** - External service integrations
- **`src/interfaces/`** - Abstract interfaces for dependency inversion
- **`src/config/`** - Configuration management
- **`src/ui/`** - User interface layer
- **`tests/`** - Comprehensive test suite

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

## 📚 Documentation

- [Architecture Documentation](ARCHITECTURE.md) - Detailed architecture overview
- [Security Guidelines](SECURITY.md) - Security best practices
- [User Guide](docs/user_guide.md) - Detailed usage instructions

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
