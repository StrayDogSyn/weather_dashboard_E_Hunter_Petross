# Weather Dashboard

A comprehensive weather dashboard application built as a capstone project.

## 🌟 Features

- **Current Weather**: Real-time weather information for any city
- **Weather Forecast**: 5-day weather forecast with detailed information
- **Favorite Cities**: Save and manage your favorite locations
- **Weather Maps**: Visual representation of weather patterns (coming soon)
- **Weather Alerts**: Notifications for severe weather conditions (coming soon)
- **Historical Data**: Access to past weather data (premium feature)

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Weather API key (free from [OpenWeatherMap](https://openweathermap.org/api))

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/weather-dashboard-E_Hunter_Petross.git
   cd weather-dashboard-E_Hunter_Petross
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**:

   **Option A**: Using .env file (recommended for security)

   ```bash
   # Copy the environment template
   copy .env.example .env
   
   # Edit .env file and set your API key
   OPENWEATHER_API_KEY=your_actual_api_key_here
   ```

   **Option B**: Environment variable (temporary)

   ```bash
   # Windows PowerShell
   $env:OPENWEATHER_API_KEY="your_api_key_here"
   
   # Windows Command Prompt
   set OPENWEATHER_API_KEY=your_api_key_here
   
   # Linux/Mac
   export OPENWEATHER_API_KEY="your_api_key_here"
   ```

### Running the Application

```bash
python main.py
```

## 📁 Project Structure

```txt
weather-dashboard-E_Hunter_Petross/
├── main.py              # Main application logic
├── config.py            # Secure configuration system
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules (protects .env)
├── SECURITY.md         # Security guidelines
├── setup.py            # Automated setup script
├── features/           # Feature modules
│   └── weather_api.py  # Weather API integration
├── data/              # Data storage and cache
├── docs/              # Documentation
│   ├── README.md      # This file
│   └── user_guide.md  # Detailed user guide
└── screenshots/       # Application screenshots
```

## 🔧 Configuration

The application uses a modern, secure configuration system:

- **Environment Variables**: Secure API key storage in `.env` file
- **Feature Flags**: Enable/disable specific features via environment variables
- **Logging Configuration**: Configurable log levels and output options
- **UI Settings**: Customizable themes, window sizes, and display options
- **Security Settings**: API key masking, privacy mode, and audit logging

### Configuration Files

- `.env` - Your personal environment variables (never commit this!)
- `.env.example` - Template with all available options
- `settings.json` - Non-sensitive application settings
- `SECURITY.md` - Security guidelines and best practices

## 🎯 Development Roadmap

### Week 16: Foundation

- [x] Project structure setup
- [x] Secure configuration system with .env support
- [x] Modern, type-safe configuration management
- [x] Security implementation (API key masking, .gitignore)
- [x] Core application framework
- [x] Basic CLI interface with configuration display
- [ ] Full API integration with real weather data

### Week 17: Core Features

- [ ] Current weather display
- [ ] Weather forecast implementation
- [ ] Data caching system
- [ ] Error handling

### Week 18: User Interface

- [ ] GUI framework selection and setup
- [ ] Main dashboard layout
- [ ] Weather data visualization
- [ ] City search functionality

### Week 19: Advanced Features

- [ ] Favorite cities management
- [ ] Weather maps integration
- [ ] Weather alerts system
- [ ] Data export functionality

### Week 20: Polish & Documentation

- [ ] UI/UX improvements
- [ ] Comprehensive testing
- [ ] Documentation completion
- [ ] Performance optimization

## 🧪 Testing

Run tests using pytest:

```bash
pytest tests/
```

## 📖 API Documentation

This application uses the OpenWeatherMap API:

- **Current Weather**: `https://api.openweathermap.org/data/2.5/weather`
- **5-Day Forecast**: `https://api.openweathermap.org/data/2.5/forecast`
- **Weather Maps**: `https://api.openweathermap.org/data/2.5/map` (coming soon)

## 🔒 Security

This project implements enterprise-level security practices:

- **API Key Protection**: Never stored in code, only in environment variables
- **Environment Variables**: Secure `.env` file management with templates
- **Git Security**: Comprehensive `.gitignore` prevents sensitive data commits
- **Configuration Validation**: Automatic API key format and security validation
- **Audit Logging**: Masked API keys in logs, optional API response logging
- **Security Documentation**: Complete guidelines in `SECURITY.md`

### Security Checklist

- [ ] Get your API key from [OpenWeatherMap](https://openweathermap.org/api)
- [ ] Copy `.env.example` to `.env`
- [ ] Add your API key to `.env` file
- [ ] Never commit your `.env` file to version control
- [ ] Review `SECURITY.md` for best practices

## 🤝 Contributing

This is a capstone project, but suggestions and feedback are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📜 License

This project is created for educational purposes as part of a capstone project.

## 📧 Contact

**Author**: E Hunter Petross  
**Project**: Weather Dashboard Capstone  
**Date**: June 2025

---

*This project is part of a software development capstone program.*