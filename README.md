# 🌤️ Weather Dashboard - TKinter GUI

> **📋 WEEK 15 SUBMISSION STATUS: ✅ READY**  
> All core requirements met, including:  
> ✅ GitHub Repository Updated  
> ✅ UI Design Implemented  
> ✅ API Integration Complete  
> ✅ Core Features Functional

![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)
[![Code Quality](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type Checking](https://img.shields.io/badge/mypy-checked-blue)](http://mypy-lang.org/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)

A modern weather dashboard application with glassmorphic design, built using Python TKinter. Features comprehensive
weather data, capstone functionality, and an intuitive graphical interface.

## 🌟 Capstone Features

### Core Weather Features

- **🌡️ Current Weather**: Real-time weather conditions for any city
- **📅 Weather Forecast**: Detailed multi-day weather forecasts
- **⭐ Favorite Cities**: Save and manage your preferred locations
- **📍 Location Detection**: Automatic geolocation to show your local weather
- **🌡️ Temperature Unit Toggle**: Quick switching between Celsius and Fahrenheit
- **📊 Interactive Dashboard**: Advanced data visualization with multiple chart types and hotkey support

### Advanced Capstone Features

- **🌍 City Comparison**: Side-by-side weather comparison between cities
- **📔 Weather Journal**: Track daily weather with mood and activity logging
- **🎯 Activity Suggestions**: Weather-based activity recommendations
- **🎨 Weather Poetry**: AI-generated poems inspired by current weather with beautiful display
- **🗃️ SQL Database Integration**: Robust data persistence with SQLAlchemy ORM
- **💾 Data Management**: Intelligent caching and flexible storage options
- **🔊 Cortana Voice Assistant**: Voice-based weather queries and information with customizable settings

### Modern GUI Design

- **🎨 Enhanced Glassmorphic Interface**: Modern dark theme with advanced glass-like effects and blur controls
- **📱 Responsive Layout**: Tabbed interface with intuitive navigation and scrollable panels
- **🎯 Interactive Elements**: Custom styled buttons with modern hover animations and visual feedback
- **📊 Data Visualization**: Beautiful weather cards and elegantly styled information displays
- **📈 Visualization Dashboard**: Interactive charts with hotkeys (Ctrl+1-4) for temperature trends, metrics,
  forecasts, and humidity/pressure data
- **✨ Poetry Display**: Artistically rendered weather poems with decorative elements and elegant typography
- **🔄 Auto-Refresh**: Convenient auto-refresh functionality with status indicators

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

> **💡 Developer Note**: This project includes comprehensive CI/CD with automated testing, code formatting (Black),
> linting (flake8), and type checking (mypy). All code changes are automatically validated for quality and
> cross-platform compatibility.

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

### Data Visualization Dashboard

- **Open Dashboard**: Click the "Charts" button in the header or press `Ctrl+D`
- **Chart Navigation**: Use hotkeys to quickly switch between chart types:
  - `Ctrl+1`: Temperature trends over time
  - `Ctrl+2`: Weather metrics overview
  - `Ctrl+3`: 5-day forecast visualization
  - `Ctrl+4`: Humidity and pressure charts
- **Dashboard Controls**:
  - `Ctrl+R`: Refresh all charts with latest data
  - `Ctrl+H`: Show help information
  - `Ctrl+D`: Toggle dashboard visibility

### Capstone Features

- **City Comparison**: Enter two cities to compare their weather
- **Journal Entries**: Record daily weather observations and mood
- **Activity Suggestions**: Get personalized recommendations based on weather
- **Weather Poetry**: Generate creative poems inspired by current conditions
- **Cortana Voice Assistant**: Use voice commands to get weather information and control the application

## 🛠️ Technical Details

### Architecture

- **Clean separation of concerns** with modular design
- **Model-View-Controller** pattern for GUI architecture
- **Service layer** for weather API integration
- **Data persistence** for favorites and journal entries

### Dependencies

- **TKinter & ttkbootstrap**: Modern GUI framework with Bootstrap-inspired styling
- **SQLAlchemy**: SQL database ORM for robust data management
- **requests**: HTTP client for weather API integration
- **matplotlib**: Data visualization and charting
- **python-dotenv**: Environment variable management
- **pydantic**: Data validation and modeling
- **openai**: AI-powered weather poetry generation
- **PyYAML**: YAML parsing and generation for configuration files
- **black & flake8**: Code formatting and linting
- **mypy**: Static type checking

### File Structure

```text
weather_dashboard_E_Hunter_Petross/
├── 📄 main.py                    # Main application entry point
├── 📄 requirements.txt           # Python dependencies
├── 📁 docs/                      # Documentation folder (organized)
├── 📄 pyproject.toml            # Project configuration
├── 📄 setup.cfg                 # Setup configuration
├── 📄 settings.json             # Application settings
├── 📁 src/                      # Source code directory
│   ├── 📁 application/          # Application layer
│   │   ├── 📄 app_factory.py    # Application factory
│   │   └── 📄 dependency_container.py # Dependency injection
│   ├── 📁 business/             # Business interfaces
│   │   └── 📄 interfaces.py     # Business layer interfaces
│   ├── 📁 config/               # Configuration management
│   │   └── 📄 config.py         # Application configuration
│   ├── 📁 controllers/          # Controller layer
│   │   └── 📄 gui_controller.py # GUI controller
│   ├── 📁 core/                 # Business logic layer
│   │   ├── 📄 activity_service.py      # Activity suggestions
│   │   ├── 📄 enhanced_comparison_service.py # City comparison
│   │   ├── 📄 journal_service.py       # Weather journal
│   │   ├── 📄 preferences.py           # User preferences
│   │   └── 📄 weather_service.py       # Core weather service
│   ├── 📁 infrastructure/       # Infrastructure layer
│   │   ├── 📄 cache_service.py  # Caching infrastructure
│   │   ├── 📄 config_manager.py # Configuration management
│   │   └── 📄 storage_service.py # Storage infrastructure
│   ├── 📁 interfaces/           # Abstract interfaces
│   │   └── 📄 weather_interfaces.py # Service interfaces
│   ├── 📁 models/               # Domain models
│   │   ├── 📄 capstone_models.py    # Capstone feature models
│   │   ├── 📄 database_models.py    # Database models
│   │   ├── 📄 predictive_models.py  # ML models
│   │   └── 📄 weather_models.py     # Weather domain models
│   ├── 📁 presentation/         # Presentation layer
│   │   ├── 📄 cli_app.py        # CLI application
│   │   └── 📄 gui_app.py        # GUI application
│   ├── 📁 services/             # External service integrations
│   │   ├── 📄 cache_service.py         # Data caching
│   │   ├── 📄 composite_weather_service.py # Multi-provider service
│   │   ├── 📄 cortana_voice_service.py # Voice assistant
│   │   ├── 📄 data_storage.py          # JSON storage
│   │   ├── 📄 location_service.py      # Geolocation
│   │   ├── 📄 model_integration_service.py # ML integration
│   │   ├── 📄 model_training_service.py # ML training
│   │   ├── 📄 poetry_service.py        # Weather poetry
│   │   ├── 📄 sound_service.py         # Audio feedback
│   │   ├── 📄 sql_data_storage.py      # SQL storage
│   │   ├── 📄 storage_factory.py       # Storage factory
│   │   ├── 📄 team_data_service.py     # Team collaboration
│   │   ├── 📄 visualization_service.py # Data visualization
│   │   ├── 📄 weather_api.py           # OpenWeatherMap API
│   │   └── 📄 weatherapi_service.py    # WeatherAPI.com
│   ├── 📁 shared/               # Shared utilities
│   │   ├── 📄 constants.py      # Application constants
│   │   └── 📄 exceptions.py     # Custom exceptions
│   ├── 📁 ui/                   # User interface layer
│   │   ├── 📁 animations/       # Animation effects
│   │   │   └── 📄 effects.py    # Animation utilities
│   │   ├── 📁 components/       # UI components
│   │   │   ├── 📄 header.py           # Application header
│   │   │   ├── 📄 main_dashboard.py   # Main dashboard
│   │   │   ├── 📄 responsive_layout.py # Responsive layout
│   │   │   ├── 📄 search_panel.py     # Search interface
│   │   │   ├── 📄 temperature_controls.py # Temperature controls
│   │   │   ├── 📄 weather_card.py     # Weather display
│   │   │   └── 📄 weather_icons.py    # Weather icons
│   │   ├── 📁 dialogs/          # Dialog windows
│   │   ├── 📁 styles/           # UI styling
│   │   │   └── 📄 glassmorphic.py # Design system
│   │   ├── 📁 widgets/          # Reusable widgets
│   │   │   ├── 📄 enhanced_button.py # Enhanced buttons
│   │   │   └── 📄 modern_button.py    # Modern buttons
│   │   ├── 📄 chart_widgets.py  # Chart components
│   │   ├── 📄 components.py     # Legacy components
│   │   ├── 📄 dashboard.py      # Dashboard interface
│   │   ├── 📄 forecast_ui.py    # Forecast interface
│   │   ├── 📄 gui_interface.py  # Main GUI orchestrator
│   │   ├── 📄 layout.py         # Layout management
│   │   ├── 📄 settings_dialog.py # Settings interface
│   │   ├── 📄 styling.py        # Legacy styling
│   │   └── 📄 weather_components.py # Weather components
│   └── 📁 utils/                # Utility functions
│       ├── 📄 formatters.py     # Data formatting
│       ├── 📄 sample_data.py    # Sample data
│       └── 📄 validators.py     # Input validation
├── 📁 cache/                    # Cache directory
├── 📁 config/                   # Configuration files
├── 📁 configs/                  # Additional configurations
│   └── 📁 cortana/              # Cortana voice assistant
│       ├── 📄 cli.py            # CLI interface
│       ├── 📄 config_manager.py # Configuration manager
│       ├── 📄 cortana_builder.py # Builder utility
│       ├── 📄 cortana_config.yaml # Configuration file
│       ├── 📄 manifest.yaml     # Manifest file
│       ├── 📄 manifest_template.yaml # Template
│       ├── 📄 schema.json       # JSON schema
│       ├── 📄 test_config.py    # Configuration tests
│       ├── 📄 test_cortana_builder.py # Builder tests
│       ├── 📄 README.md         # Documentation
│       └── 📄 validation_report.md # Validation report
├── 📁 data/                     # Application data
│   ├── 📄 favorite_cities.json # Favorite cities
│   ├── 📄 journal_entries.json # Journal entries
│   ├── 📄 weather_dashboard.db # SQLite database
│   ├── 📄 weather_history.json # Weather history
│   ├── 📁 json_backup/         # Data backups
│   ├── 📁 screenshots/         # UI screenshots
│   └── 📁 sounds/              # Audio files
├── 📁 docs/                     # Documentation
│   ├── 📄 README.md            # Documentation index
│   ├── 📁 architecture/        # Architecture documentation
│   │   ├── 📄 architecture.md      # Architecture overview
│   │   └── 📄 project_structure.md # Project structure
│   ├── 📁 configuration/       # Configuration documentation
│   │   ├── 📄 CORTANA_CONFIGURATION.md # Cortana setup
│   │   ├── 📄 CORTANA_INTEGRATION.md # Cortana integration
│   │   └── 📄 security.md          # Security guidelines
│   ├── 📁 deployment/          # Deployment documentation
│   │   └── 📄 DEPLOYMENT_GUIDE.md  # Deployment guide
│   ├── 📁 development/         # Development documentation
│   │   ├── 📄 IMPLEMENTATION_GUIDE.md # Implementation guide
│   │   ├── 📄 GITHUB_TEAM_DATA_INTEGRATION.md # Team integration
│   │   ├── 📄 GUI_LAYOUT_ANALYSIS_AND_IMPROVEMENTS.md # GUI analysis
│   │   ├── 📄 SQL_DATABASE.md      # Database documentation
│   │   ├── 📄 requirements-dev.txt # Development dependencies
│   └── 📁 reflections/         # Weekly reflections
│       ├── 📄 Week11_Reflection.md # Week 11 reflection
│       ├── 📄 Week12_Reflection.md # Week 12 reflection
│       ├── 📄 Week13_Reflection.md # Week 13 reflection
│       ├── 📄 Week14_Reflection.md # Week 14 reflection
│       └── 📄 Week15_Reflection.md # Week 15 reflection
├── 📁 exports/                  # Export files
├── 📁 logs/                     # Application logs
├── 📁 scripts/                  # Utility scripts
│   ├── 📄 inspect_database.py  # Database inspection
│   ├── 📄 pre_commit_check.py  # Pre-commit checks
│   └── 📄 setup.py            # Setup script
├── 📁 temp/                     # Temporary files
└── 📁 tests/                    # Test suite
    ├── 📄 README.md            # Test documentation
    ├── 📄 requirements-test.txt # Test dependencies
    ├── 📄 run_tests.py         # Test runner
    ├── 📄 settings.json        # Test settings
    ├── 📄 test_cortana_integration.py # Voice assistant tests
├── 📄 test_week14_features.py # Advanced features tests
    ├── 📄 test_validators.py    # Validator tests
    ├── 📄 test_weather_models.py # Model tests
    ├── 📄 test_weather_service.py # Service tests
    └── 📄 test_week14_features.py # Feature tests
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
- **Enhanced Cortana voice assistant** with natural language processing
- **Multi-language support** for voice commands and responses

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
- **`configs/cortana/`** - Cortana voice assistant configuration and management

## 🧪 Testing

The project includes a comprehensive test suite:

```bash
# Install testing dependencies
pip install -r tests/requirements-test.txt

# Run the test suite
python -m pytest tests/ -v --cov=src

# Run specific test files
python -m pytest tests/test_weather_models.py -v
python -m pytest tests/test_weather_service.py -v
```

### Test Coverage

- **Models**: Data model validation and integrity
- **Services**: Core business logic and API integration
- **Cache**: Data caching behavior and persistence
- **Validators**: Input validation and error handling
- **Session**: User session persistence and state management

## 📚 Documentation

### Architecture & Design

- [Architecture Documentation](docs/architecture/architecture.md) - Detailed architecture overview and design principles
- [Project Structure](docs/architecture/project_structure.md) - Complete project organization and file structure

### Configuration & Setup

- [Security Guidelines](docs/configuration/security.md) - Security best practices and API key management
- [Cortana Configuration](docs/configuration/CORTANA_CONFIGURATION.md) - Cortana voice assistant setup and configuration
- [Cortana Integration](docs/configuration/CORTANA_INTEGRATION.md) - Cortana integration details

### Development & Implementation

- [Implementation Guide](docs/development/IMPLEMENTATION_GUIDE.md) - Detailed implementation documentation
- [GUI Layout Analysis](docs/development/GUI_LAYOUT_ANALYSIS_AND_IMPROVEMENTS.md) - UI design analysis and improvements
- [GitHub Team Integration](docs/development/GITHUB_TEAM_DATA_INTEGRATION.md) - Team collaboration features
- [SQL Database Documentation](docs/development/SQL_DATABASE.md) - Database design and implementation

### Deployment

- [Deployment Guide](docs/deployment/DEPLOYMENT_GUIDE.md) - Production deployment instructions

### Weekly Reflections

- [Week 11 Reflection](docs/reflections/Week11_Reflection.md) - Clean architecture and core service implementation
- [Week 12 Reflection](docs/reflections/Week12_Reflection.md) - Advanced features and data visualization
- [Week 13 Reflection](docs/reflections/Week13_Reflection.md) - Machine learning integration and analytics
- [Week 14 Reflection](docs/reflections/Week14_Reflection.md) - Development milestones and reflection
- [Week 15 Reflection](docs/reflections/Week15_Reflection.md) - Final project reflection

### Complete Documentation Index

- [Documentation Index](docs/README.md) - Complete documentation overview with works cited

## 🔐 Security

- API keys are stored securely in environment variables
- No sensitive data is logged or exposed
- Input validation and sanitization
- Secure configuration management

## 🤝 Contributing

### Branching Strategy

**⚠️ Important: Never commit directly to `main` branch**

1. **Create a feature branch** for all development work:

   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Work on your feature branch**:

   ```bash
   # Make your changes
   git add .
   git commit -m "feat: your descriptive commit message"
   git push -u origin feature/your-feature-name
   ```

3. **Create a Pull Request** when ready:
   - Open a PR from your feature branch to `main`
   - Add descriptive title and description
   - Request code review before merging

4. **Clean up after merge**:

   ```bash
   git checkout main
   git pull origin main
   git branch -d feature/your-feature-name
   ```

### Development Guidelines

1. Fork the repository (if external contributor)
2. Create a feature branch from `main`
3. Make your changes following the coding standards
4. Add tests for new functionality
5. Run the test suite to ensure everything passes
6. Update documentation as needed
7. Submit a pull request with clear description

### Code Quality Standards

- **Type Checking**: All code must pass MyPy static analysis
- **Code Formatting**: Use Black formatter for consistent style
- **Linting**: Code must pass Flake8 linting checks
- **Testing**: New features require corresponding tests
- **Documentation**: Update relevant documentation for changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenWeatherMap for providing the weather API
- Python community for excellent libraries
- Clean Architecture principles by Robert C. Martin

## 🔧 CI/CD & Code Quality

### Automated Testing & Linting

This project includes a comprehensive CI/CD pipeline with automated code quality checks:

#### Code Formatting & Style

- **Black**: Automatic code formatting for consistent style
- **isort**: Import sorting and organization
- **flake8**: Linting for code quality and PEP 8 compliance
- **mypy**: Static type checking for better code reliability

#### Cross-Platform Testing

- **Multi-OS Support**: Tested on Ubuntu, Windows, and macOS
- **Python Versions**: Compatible with Python 3.9, 3.10, 3.11, and 3.12
- **Automated Testing**: Comprehensive test suite with coverage reporting

#### GitHub Actions Workflows

- **Continuous Integration**: Automatic testing on every push and pull request
- **Code Quality Gates**: All code must pass linting and formatting checks
- **Security Scanning**: Automated vulnerability detection with Bandit and Safety
- **Documentation Generation**: Automatic API documentation updates
- **Build Artifacts**: Cross-platform application builds for distribution

### Running Quality Checks Locally

```bash
# Install development dependencies
pip install black isort flake8 mypy types-requests

# Format code
black src/ tests/
isort src/ tests/

# Check code quality
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,F401,F541,E501,E402,F841
mypy src/ --ignore-missing-imports

# Run all checks together
python -c "
import subprocess
import sys

commands = [
    ['black', '--check', 'src/', 'tests/'],
    ['isort', '--check-only', 'src/', 'tests/'],
    ['flake8', 'src/', 'tests/', '--max-line-length=88', '--extend-ignore=E203,W503,F401,F541,E501,E402,F841'],
    ['mypy', 'src/', '--ignore-missing-imports']
]

for cmd in commands:
    print(f'Running: {\" \".join(cmd)}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'❌ Failed: {\" \".join(cmd)}')
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)
    else:
        print(f'✅ Passed: {\" \".join(cmd)}')

print('🎉 All quality checks passed!')
"
```

### Configuration Files

The project includes several configuration files for development tools:

- **`.flake8`**: Flake8 linting configuration
- **`pyproject.toml`**: Black, isort, and other tool configurations  
- **`.github/workflows/`**: GitHub Actions CI/CD pipeline definitions

### Recent Improvements (June 2025)

#### 🔧 CI/CD & Infrastructure

- ✅ **Fixed deprecated GitHub Actions**: Updated all actions to latest versions (v4/v5)
- ✅ **Cross-platform compatibility**: Resolved Windows/Linux/macOS compatibility issues in CI/CD
- ✅ **Multi-OS testing**: Added comprehensive testing across Ubuntu, Windows, and macOS
- ✅ **Python version matrix**: Testing on Python 3.9, 3.10, 3.11, and 3.12

#### 📝 Code Quality & Standards

- ✅ **Code formatting**: Applied comprehensive Black and isort formatting (30 files reformatted)
- ✅ **Type safety**: Added proper type annotations and mypy compliance
- ✅ **Linting compliance**: Fixed all flake8 violations and code quality issues
- ✅ **Import organization**: Automated import sorting with isort

#### 🚀 Developer Experience

- ✅ **Automated workflows**: Fully automated testing and deployment pipeline
- ✅ **Quality gates**: All code must pass formatting, linting, and type checks
- ✅ **Security scanning**: Integrated Bandit and Safety vulnerability detection
- ✅ **Configuration files**: Added `.flake8`, `pyproject.toml` for tool configuration

## 🎨 Enhanced Poetry Display

The Weather Dashboard includes a beautifully designed poetry feature that generates and displays weather-inspired poems:

### Poetry Features

- **Elegant Typography**: Uses Georgia and Palatino Linotype fonts for elegant display
- **Beautiful Layout**: Decorative elements and proper spacing enhance readability
- **Multiple Poem Types**: Supports haikus, limericks, and free-form poems
- **Visual Effects**: Glassmorphic containers with custom blur effects
- **Collection View**: Beautifully formatted poetry collections with consistent styling
- **Center-Aligned Text**: Properly formatted poetry with appropriate line breaks
- **Dynamic Sizing**: Adjusts text area size based on poem type and length
- **Decorative Elements**: Subtle borders, accent lines, and thematic icons

The poetry display uses modern UI techniques to present weather-inspired poems in an engaging, visually pleasing format.

## 🛠️ Development & Maintenance

### Quick Setup

For new developers or setting up on a new machine:

```bash
# Clone the repository
git clone <repository-url>
cd weather_dashboard_E_Hunter_Petross

# Run automated setup
python scripts/setup.py
```

### Project Cleanup

To clean up temporary files and cache:

```bash
python scripts/cleanup.py
```

### Project Structure

```text
weather_dashboard_E_Hunter_Petross/
├── 📁 src/                 # Main application source code (Clean Architecture)
│   ├── 📁 application/     # Application layer (orchestration)
│   │   ├── 📄 app_factory.py        # Application factory pattern
│   │   └── 📄 dependency_container.py # Dependency injection container
│   ├── 📁 business/        # Business layer interfaces
│   │   └── 📄 interfaces.py         # Business logic contracts
│   ├── 📁 controllers/     # Controller layer
│   │   └── 📄 gui_controller.py     # GUI controller orchestration
│   ├── 📁 core/            # Core business logic (use cases)
│   │   ├── 📄 weather_service.py    # Core weather functionality
│   │   ├── 📄 journal_service.py    # Weather journal features
│   │   ├── 📄 activity_service.py   # Activity suggestions
│   │   └── 📄 preferences.py        # User preferences management
│   ├── 📁 infrastructure/  # Infrastructure layer
│   │   ├── 📄 cache_service.py      # Caching infrastructure
│   │   ├── 📄 config_manager.py     # Configuration management
│   │   └── 📄 storage_service.py    # Data persistence infrastructure
│   ├── 📁 interfaces/      # Abstract interfaces (ports)
│   │   └── 📄 weather_interfaces.py # Service abstractions
│   ├── 📁 models/          # Domain models (entities)
│   │   ├── 📄 weather_models.py     # Weather domain entities
│   │   ├── 📄 capstone_models.py    # Capstone feature models
│   │   └── 📄 database_models.py    # Database models
│   ├── 📁 presentation/    # Presentation layer
│   │   ├── 📄 gui_app.py            # GUI application entry
│   │   └── 📄 cli_app.py            # CLI application entry
│   ├── 📁 services/        # External service integrations (adapters)
│   │   ├── 📄 weather_api.py        # OpenWeatherMap integration
│   │   ├── 📄 poetry_service.py     # AI poetry generation
│   │   ├── 📄 cortana_voice_service.py # Voice assistant
│   │   └── 📄 data_storage.py       # Data persistence
│   ├── 📁 shared/          # Shared utilities
│   │   ├── 📄 constants.py          # Application constants
│   │   └── 📄 exceptions.py         # Custom exceptions
│   ├── 📁 ui/              # User interface components (refactored)
│   │   ├── 📄 gui_interface.py      # Main GUI orchestrator (649 lines)
│   │   ├── 📁 styles/               # UI styling system
│   │   │   └── 📄 glassmorphic.py   # Glassmorphic design system
│   │   ├── 📁 widgets/              # Reusable UI widgets
│   │   │   ├── 📄 modern_button.py  # Modern button components
│   │   │   └── 📄 enhanced_button.py # Enhanced button variants
│   │   ├── 📁 animations/           # Animation effects
│   │   │   └── 📄 effects.py        # Animation utilities
│   │   ├── 📁 components/           # Specialized UI components
│   │   │   ├── 📄 weather_icons.py    # Weather icon management
│   │   │   ├── 📄 weather_card.py     # Weather display cards
│   │   │   ├── 📄 search_panel.py     # Search interface
│   │   │   ├── 📄 main_dashboard.py   # Dashboard layout
│   │   │   ├── 📄 header.py           # Application header
│   │   │   └── 📄 temperature_controls.py # Temperature controls
│   │   └── 📁 dialogs/              # Dialog windows
│   └── 📁 utils/           # Utility functions
│       ├── 📄 formatters.py         # Data formatting utilities
│       ├── 📄 validators.py         # Input validation
│       └── 📄 sample_data.py        # Sample data generation
├── 📁 configs/             # Configuration files
│   └── 📁 cortana/         # Cortana voice assistant configuration
├── 📁 data/                # Application data and database
│   ├── 📄 weather_dashboard.db     # SQLite database
│   ├── 📁 json_backup/             # Data backups
│   └── 📁 screenshots/             # UI screenshots
├── 📁 docs/                # Comprehensive documentation
│   ├── 📄 architecture.md          # Architecture documentation
│   ├── 📄 security.md              # Security guidelines
│   └── 📄 README.md                # Documentation index
├── 📁 tests/               # Test suite
│   ├── 📄 test_weather_models.py   # Model tests
│   ├── 📄 test_weather_service.py  # Service tests
│   └── 📄 run_tests.py             # Test runner
├── 📁 scripts/             # Development and utility scripts
│   ├── 📄 setup.py                 # Project setup
│   └── 📄 pre_commit_check.py      # Code quality checks
├── 🔧 requirements.txt     # Python dependencies
├── ⚙️ pyproject.toml       # Project configuration
├── 📄 main.py              # Application entry point
└── 📄 README.md           # This file
```

### 🏆 **UI Architecture Highlights**

**Major Refactoring Achievement (2025):**

- **82% reduction** in main GUI file size (3,592 → 649 lines)
- **15+ specialized components** extracted into modular architecture
- **Enterprise-level design** with clear separation of concerns
- **Enhanced maintainability** and testability

### Code Quality

This project maintains high code quality standards:

- **Type Checking**: MyPy static type analysis
- **Code Formatting**: Black code formatter
- **Linting**: Flake8 with comprehensive rules
- **Testing**: Pytest with comprehensive test coverage
- **Security**: Bandit security scanning

### UI Styling

The application now uses **ttkbootstrap** for modern Bootstrap-inspired styling:

- Professional dark theme ("superhero")
- Responsive design principles
- Consistent visual hierarchy
- Enhanced accessibility features
