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
   
   **Option A**: Environment variable (recommended)

   ```bash
   # Windows PowerShell
   $env:OPENWEATHER_API_KEY="your_api_key_here"
   
   # Windows Command Prompt
   set OPENWEATHER_API_KEY=your_api_key_here
   
   # Linux/Mac
   export OPENWEATHER_API_KEY="your_api_key_here"
   ```
   
   **Option B**: Edit `config.py`
   - Open `config.py`
   - Replace `'your_api_key_here'` with your actual API key

### Running the Application

```bash
python main.py
```

## 📁 Project Structure

```txt
weather-dashboard-E_Hunter_Petross/
├── main.py              # Main application logic
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── features/            # Feature modules (to be added)
├── data/               # Data storage and cache
├── docs/               # Documentation
│   ├── README.md       # This file
│   └── user_guide.md   # Detailed user guide
└── screenshots/        # Application screenshots
```

## 🔧 Configuration

The application can be configured through `config.py`:

- **API Settings**: Configure weather API endpoints and keys
- **Display Options**: Customize themes, colors, and window settings
- **Feature Toggles**: Enable/disable specific features
- **Data Storage**: Configure cache duration and data directory

## 🎯 Development Roadmap

### Week 16: Foundation

- [x] Project structure setup
- [x] Basic configuration system
- [x] Core application framework
- [ ] API integration
- [ ] Basic CLI interface

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