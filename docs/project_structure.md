# Project Structure - Weather Dashboard TKinter GUI

## 📁 Clean Project Layout

```text
weather_dashboard_E_Hunter_Petross/
├── 📄 main.py                    # Main application entry point
├── 📄 run_gui.py                 # Simplified GUI launcher (always works)
├── 📄 requirements.txt           # Python dependencies (minimal)
├── 📄 .env.example              # Environment configuration template
├── 📄 README.md                 # Professional project documentation
├── 📄 LICENSE                   # MIT License
├── 📄 settings.json             # Application settings
├── 📁 src/                      # Source code directory
│   ├── 📄 __init__.py
│   ├── 📄 app_gui.py            # Main GUI application controller
│   ├── 📁 ui/                   # User interface layer
│   │   ├── 📄 __init__.py
│   │   └── 📄 gui_interface.py  # Modern TKinter GUI with glassmorphic design
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
│   │   └── 📄 location_service.py     # Geolocation services
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
│   ├── 📄 README.md
│   ├── 📄 user_guide.md
│   ├── � architecture.md         # Architecture documentation
│   ├── 📄 security.md             # Security guidelines
│   ├── � project_structure.md    # This file - project organization
│   ├── 📄 refactor_complete.md    # Refactoring summary
│   └── 📄 Week11_Reflection.md    # Capstone reflection
├── 📁 cache/                    # Application cache (runtime)
├── 📁 data/                     # Application data (runtime)
├── � logs/                     # Application logs (runtime)
└── � exports/                  # Data exports (runtime)
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

- Clean, focused TKinter GUI application
- No CLI dependencies or legacy code
- Professional file organization
- Proper Python naming conventions
- Comprehensive documentation
- Minimal dependencies

### 🚀 Launch Commands

```bash
# Recommended: Simplified launcher (always works)
python run_gui.py

# Alternative: Main application entry point
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

## 📦 Dependencies (Minimal)

- `requests` - HTTP client for weather API
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation and modeling
- `tkinter` - GUI framework (built into Python)

The project is now clean, focused, and ready for professional use or demonstration! 🎉

## Resources & Attribution

For a complete list of development tools, libraries, and learning resources used in this project, please refer to the [Works Cited section](README.md#works-cited) in the documentation index.
