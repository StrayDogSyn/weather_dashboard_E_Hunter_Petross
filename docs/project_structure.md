# Project Structure - Weather Dashboard TKinter GUI

## 📁 Clean Project Layout

```text
weather_dashboard_E_Hunter_Petross/
├── 📄 main.py                    # Main application entry point
├── 📄 requirements.txt           # Python dependencies
├── 📄 requirements-dev.txt       # Development dependencies
├── 📄 requirements-test.txt      # Testing dependencies
├── 📄 pyproject.toml            # Project configuration and metadata
├── 📄 README.md                 # Project documentation
├── 📄 LICENSE                   # MIT License
├── 📄 settings.json             # Application settings
├── 📁 data/                     # Application data directory
│   ├── 📄 weather_dashboard.db   # SQLite database
│   ├── 📁 json_backup/          # JSON data backups
│   └── 📁 screenshots/          # UI screenshots
├── 📁 docs/                     # Documentation directory
│   ├── 📄 architecture.md       # Architecture documentation
│   ├── 📄 project_structure.md  # Project structure guide
│   ├── 📄 security.md          # Security guidelines
│   ├── 📄 SQL_DATABASE.md      # Database documentation
│   └── 📄 Week13_Reflection.md  # Latest progress reflection
├── 📁 src/                      # Source code directory
│   ├── 📄 __init__.py
│   ├── 📄 app_gui.py            # Main GUI application controller
│   ├── 📁 ui/                   # User interface layer
│   │   ├── 📄 __init__.py
│   │   ├── 📄 gui_interface.py  # Modern TKinter GUI with glassmorphic design
│   │   └── 📄 dashboard.py      # Weather data visualization dashboard with hotkeys
│   ├── 📁 core/                 # Business logic and services
│   │   ├── 📄 __init__.py
│   │   ├── 📄 weather_service.py      # Core weather functionality
│   │   ├── 📄 comparison_service.py   # City comparison feature
│   │   ├── 📄 journal_service.py      # Weather journal feature
│   │   └── 📄 activity_service.py     # Activity suggestion feature
│   ├── 📁 services/             # External service integrations
│   │   ├── 📄 __init__.py
│   │   ├── 📄 weather_api.py          # OpenWeatherMap API client
│   │   ├── 📄 poetry_service.py       # Weather poetry generation
│   │   ├── 📄 cache_service.py        # Caching functionality
│   │   ├── 📄 data_storage.py         # JSON data persistence
│   │   ├── 📄 sql_data_storage.py     # SQL database integration
│   │   ├── 📄 storage_factory.py      # Storage implementation factory
│   │   ├── 📄 location_service.py     # Geolocation services
│   │   └── 📄 visualization_service.py # Weather data visualization with matplotlib
│   ├── 📁 models/               # Data models and schemas
│   │   ├── 📄 __init__.py
│   │   ├── 📄 weather_models.py       # Weather data models
│   │   ├── 📄 capstone_models.py      # Capstone feature models
│   │   └── 📄 database_models.py      # SQLAlchemy database models
│   ├── 📁 interfaces/           # Abstract interfaces
│   │   ├── 📄 __init__.py
│   │   └── 📄 weather_interfaces.py   # Interface definitions
│   ├── 📁 config/               # Configuration management
│   │   ├── 📄 __init__.py
│   │   └── 📄 config.py               # Configuration handling
│   └── 📁 utils/                # Utility functions
│       ├── 📄 __init__.py
│       ├── 📄 validators.py           # Input validation
│       └── 📄 formatters.py           # Data formatting
├── 📁 docs/                     # Documentation
│   ├── 📄 README.md              # Documentation index
│   ├── 📄 architecture.md        # Architecture documentation
│   ├── 📄 security.md           # Security guidelines
│   ├── 📄 project_structure.md  # This file - project organization
│   ├── 📄 SQL_DATABASE.md       # Database documentation
│   └── 📄 Week11_Reflection.md  # Capstone reflection
├── 📁 tests/                    # Test suite
│   ├── 📄 __init__.py
│   ├── 📄 README.md             # Test documentation
│   ├── 📄 requirements-test.txt # Test dependencies
│   ├── 📄 run_tests.py         # Test runner
│   ├── 📄 settings.json        # Test configuration
│   └── 📄 test_*.py           # Test files
├── 📁 cache/                    # Application cache (runtime)
├── 📁 data/                     # Application data
│   ├── 📄 weather_dashboard.db  # SQLite database
│   ├── 📁 json_backup/         # JSON data backups
│   └── 📁 screenshots/         # Application screenshots
├── 📁 logs/                     # Application logs
├── 📁 exports/                  # Data exports
└── 📁 scripts/                  # Utility scripts
    ├── 📄 cleanup.py           # Cleanup utilities
    └── 📄 setup.py            # Setup utilities
```

## 🧹 Cleanup & Organization Completed

### 📁 Moved to /docs/

- `architecture.md` - Architecture documentation
- `security.md` - Security guidelines
- `project_structure.md` - This project structure documentation
- `refactor_complete.md` - Refactoring summary

### ❌ Removed Files

- `src/app.py` - Old CLI application controller
- `src/ui/cli_interface.py` - CLI interface (GUI-only focus)
- `launch_gui.py` - Duplicate launcher
- `main_gui.py` - Duplicate launcher
- `simple_gui.py` - Duplicate launcher
- `README_old.md` - Backup file
- `weather_dashboard.log` - Old log file
- All `__pycache__/` directories - Python cache files
- `.pytest_cache/` - Test cache files

### ✅ Cleaned Up

- Removed all CLI references from code
- Updated `src/ui/__init__.py` to only export GUI interface
- Fixed file structure documentation in README.md
- Moved documentation files to /docs/ folder for better organization:
  - `architecture.md` → `docs/architecture.md`
  - `security.md` → `docs/security.md`
  - `project_structure.md` → `docs/project_structure.md`
  - `refactor_complete.md` → `docs/refactor_complete.md`

### 📏 Naming Conventions Applied

- **Python files**: `snake_case.py` ✅
- **Documentation files**: `lowercase.md` ✅
- **Directory names**: `lowercase/` ✅
- **Configuration files**: Standard naming ✅

## 🎯 Current Project Status

### ✅ Ready for Use

- Modern TKinter GUI application with glass effects
- SQLite database integration for persistent storage
- Comprehensive test suite
- Well-organized project structure
- Complete documentation
- CI/CD ready with test requirements

### 🚀 Launch Command

```bash
# Launch the Weather Dashboard
python main.py
```

## 🌟 Features Available

- **Modern Glassmorphic GUI** - Dark theme with glass effects
- **Weather Data** - Current conditions and forecasts
- **City Comparison** - Side-by-side weather comparison
- **Weather Journal** - Daily weather tracking with mood
- **Activity Suggestions** - Weather-based recommendations
- **Weather Poetry** - AI-generated poems
- **Data Management** - Caching and persistence

## 📦 Core Dependencies

- `tkinter` - GUI framework (built into Python)
- `requests` - HTTP client for weather API
- `SQLAlchemy` - SQL database ORM
- `matplotlib` - Data visualization
- `openai` - AI poetry generation
- `pydantic` - Data validation
- `python-dotenv` - Environment configuration

Development dependencies are specified in `requirements-dev.txt` and test dependencies in `tests/requirements-test.txt`.

The project is now clean, focused, and ready for professional use or demonstration! 🎉

## Resources & Attribution

For a complete list of development tools, libraries, and learning resources used in this project, please refer to the [Works Cited section](README.md#works-cited) in the documentation index.
