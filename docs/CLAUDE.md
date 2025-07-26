# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Running the Application
```bash
# Main application entry point
python main.py
```

### Testing
```bash
# Run all tests with the test runner
python tests/run_tests.py

# Run tests with pytest (if pytest is installed)
python -m pytest tests/ -v --cov=src

# Run specific test files
python -m pytest tests/test_weather_models.py -v
python -m pytest tests/test_weather_service.py -v
```

### Code Quality & Linting
```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Run linting with flake8
flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503,F401,F541,E501,E402,F841

# Type checking with mypy
mypy src/ --ignore-missing-imports

# Run all quality checks (from README.md)
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
        sys.exit(1)
    else:
        print(f'✅ Passed: {\" \".join(cmd)}')

print('🎉 All quality checks passed!')
"
```

### Setup & Dependencies
```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Install testing dependencies
pip install -r tests/requirements-test.txt

# Automated setup for new developers
python scripts/setup.py
```

## Architecture Overview

This is a modern Python TKinter weather dashboard application following Clean Architecture principles with clear separation of concerns.

### Core Architecture Layers

- **`main.py`** - Application entry point with fallback GUI
- **`src/app_gui.py`** - Main GUI application controller
- **`src/controllers/`** - GUI controllers implementing MVC pattern
- **`src/ui/`** - User interface components and widgets
- **`src/core/`** - Business logic and use cases
- **`src/services/`** - External service integrations (APIs, storage)
- **`src/models/`** - Data models with Pydantic validation
- **`src/interfaces/`** - Abstract interfaces for dependency inversion
- **`src/config/`** - Configuration management with environment variables
- **`src/utils/`** - Utility functions and helpers

### Key Design Patterns

1. **Model-View-Controller (MVC)** - GUI follows MVC with controllers in `src/controllers/gui_controller.py`
2. **Service Layer Pattern** - External integrations isolated in `src/services/`
3. **Repository Pattern** - Data access abstracted through storage services
4. **Factory Pattern** - Storage factory (`src/services/storage_factory.py`) for different persistence options

### Data Flow Architecture

1. **GUI Layer** (`src/ui/gui_interface.py`) - Handles user interactions and display
2. **Controller Layer** (`src/controllers/gui_controller.py`) - Processes user actions, connects GUI to business logic
3. **Business Logic** (`src/core/`) - Core application logic (weather_service.py, journal_service.py, etc.)
4. **Service Layer** (`src/services/`) - External API calls and data persistence
5. **Data Models** (`src/models/`) - Data validation and structure with Pydantic

### Storage & Persistence

- **SQLite Database** - Primary storage (`data/weather_dashboard.db`) via SQLAlchemy ORM
- **JSON Backup System** - Automatic backups in `data/json_backup/`
- **Multiple Storage Backends** - Factory pattern supports different storage options
- **Caching Layer** - Built-in caching (`src/services/cache_service.py`) for API responses

### GUI Architecture

- **TKinter + ttkbootstrap** - Modern Bootstrap-inspired styling with "superhero" dark theme
- **Glassmorphic Design** - Dark theme with transparency effects and blur controls
- **Tabbed Interface** - Weather, Forecast, Comparison, Journal, Activities, Poetry, Favorites
- **Dashboard Integration** - Interactive charts (`src/ui/dashboard.py`) with keyboard shortcuts (Ctrl+1-4)
- **Chart Widgets** - Specialized chart components in `src/ui/chart_widgets.py`

### API Integration

- **OpenWeatherMap API** - Primary weather data source via `src/services/weather_api.py`
- **Environment Variables** - API keys stored in `.env` file, managed by `src/config/config.py`
- **Composite Service Pattern** - `src/services/composite_weather_service.py` aggregates multiple weather sources
- **Error Handling** - Comprehensive error handling with user feedback

### Key Capstone Features

1. **Weather Display** - Current conditions and forecasts
2. **City Comparison** - Side-by-side weather comparison (`src/core/enhanced_comparison_service.py`)
3. **Weather Journal** - Mood and activity tracking (`src/core/journal_service.py`)
4. **Activity Suggestions** - Weather-based recommendations (`src/core/activity_service.py`)
5. **Weather Poetry** - AI-generated weather poems (`src/services/poetry_service.py`)
6. **Data Visualization** - Interactive charts with matplotlib integration
7. **Machine Learning** - Predictive models (`src/models/predictive_models.py`, `src/services/model_training_service.py`)

### Configuration System

- **Type-Safe Configuration** - `src/config/config.py` with dataclasses and validation
- **Environment Variables** - `.env` file for sensitive data (API keys)
- **Application Settings** - `settings.json` for user preferences
- **Project Configuration** - `pyproject.toml` with tool configurations for Black, isort, flake8

### Testing Strategy

- **Custom Test Runner** - `tests/run_tests.py` for comprehensive testing
- **Unit Tests** - Individual component testing
- **Integration Tests** - Service layer testing
- **Model Validation Tests** - Data model integrity
- **Session Persistence Tests** - User state management
- **Test Configuration** - Separate `tests/settings.json` and `tests/requirements-test.txt`

### Development Workflow

**Branch Strategy (from README.md):**
- Never commit directly to `main` branch
- Use feature branches: `git checkout -b feature/your-feature-name`
- Create Pull Requests for code review
- All code must pass Black, flake8, and mypy quality gates

### Cross-Platform CI/CD

- **Multi-OS Support** - Tested on Ubuntu, Windows, and macOS
- **Python Versions** - Compatible with Python 3.9, 3.10, 3.11, and 3.12
- **Automated Quality Checks** - GitHub Actions with security scanning (Bandit, Safety)
- **Code Quality Gates** - All code must pass formatting, linting, and type checks

### Project Dependencies

**Core Stack:**
- `requests` - HTTP client for weather API
- `python-dotenv` - Environment variable management  
- `pydantic>=2.0.0` - Data validation and modeling
- `sqlalchemy>=2.0.0` - Database ORM
- `ttkbootstrap>=1.10.1` - Modern TKinter styling

**Data & Visualization:**
- `matplotlib>=3.7.0` - Charts and graphs
- `numpy>=1.24.0` - Numerical operations
- `pandas>=2.0.0` - Data manipulation
- `seaborn>=0.12.0` - Statistical visualization

**Machine Learning:**
- `scikit-learn>=1.3.0` - ML algorithms
- `joblib>=1.3.0` - Model persistence

**Development Tools:**
- `black>=23.0.0` - Code formatting
- `isort>=5.12.0` - Import sorting
- `flake8>=6.0.0` - Linting
- `mypy` - Type checking
- `pytest>=7.4.0` - Testing framework