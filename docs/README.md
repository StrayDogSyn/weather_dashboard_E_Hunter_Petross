# Weather Dashboard - Documentation Index

This directory contains comprehensive documentation for the Weather Dashboard project, organized into logical categories for easier navigation and maintainability.

## 📁 Documentation Structure

### 🏗️ Architecture
- **[Architecture](architecture/architecture.md)** - Clean Architecture implementation and design patterns
- **[Project Structure](architecture/project_structure.md)** - Detailed file organization and component breakdown

### 🚀 Deployment
- **[Deployment Guide](deployment/DEPLOYMENT_GUIDE.md)** - Production deployment with Bot Framework and Azure services

### ⚙️ Configuration
- **[Security](configuration/security.md)** - API key management and security best practices
- **[Cortana Configuration](configuration/CORTANA_CONFIGURATION.md)** - Voice assistant setup and configuration
- **[Cortana Integration](configuration/CORTANA_INTEGRATION.md)** - Enhanced voice service implementation

### 💻 Development
- **[Implementation Guide](development/IMPLEMENTATION_GUIDE.md)** - Development setup and guidelines
- **[SQL Database](development/SQL_DATABASE.md)** - Database schema and data management
- **[GitHub Team Integration](development/GITHUB_TEAM_DATA_INTEGRATION.md)** - Team collaboration features
- **[GUI Layout Analysis](development/GUI_LAYOUT_ANALYSIS_AND_IMPROVEMENTS.md)** - UI/UX improvements and analysis
- **[Development Requirements](development/requirements-dev.txt)** - Development dependencies

### 📝 Reflections
- **[Week 11 Reflection](reflections/Week11_Reflection.md)** - Clean architecture and core service implementation
- **[Week 12 Reflection](reflections/Week12_Reflection.md)** - Advanced features and data visualization implementation
- **[Week 13 Reflection](reflections/Week13_Reflection.md)** - Machine learning integration and advanced analytics
- **[Week 14 Reflection](reflections/Week14_Reflection.md)** - Development progress and milestones
- **[Week 15 Reflection](reflections/Week15_Reflection.md)** - Continued development insights

## 🔗 Works Cited

This section provides comprehensive attribution for all major tools, libraries, frameworks, AI services, and learning resources used in developing the Weather Dashboard project.

### 🐍 Core Python Libraries & Frameworks

#### GUI & Interface

- **TKinter** - Python's standard GUI toolkit (built-in with Python)
  - Documentation: [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)
  - Tutorial: [https://tkdocs.com/](https://tkdocs.com/)

- **ttkbootstrap** (v1.10.1+) - Bootstrap-inspired styling for TKinter
  - GitHub: [https://github.com/israel-dryer/ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap)
  - Documentation: [https://ttkbootstrap.readthedocs.io/](https://ttkbootstrap.readthedocs.io/)

#### Data Science & Visualization

- **matplotlib** (v3.7.0+) - Comprehensive plotting library
  - Website: [https://matplotlib.org/](https://matplotlib.org/)
  - Documentation: [https://matplotlib.org/stable/contents.html](https://matplotlib.org/stable/contents.html)

- **numpy** (v1.24.0+) - Fundamental package for scientific computing
  - Website: [https://numpy.org/](https://numpy.org/)
  - Documentation: [https://numpy.org/doc/stable/](https://numpy.org/doc/stable/)

- **pandas** (v2.0.0+) - Data manipulation and analysis library
  - Website: [https://pandas.pydata.org/](https://pandas.pydata.org/)
  - Documentation: [https://pandas.pydata.org/docs/](https://pandas.pydata.org/docs/)

- **seaborn** (v0.12.0+) - Statistical data visualization
  - Website: [https://seaborn.pydata.org/](https://seaborn.pydata.org/)
  - Documentation: [https://seaborn.pydata.org/tutorial.html](https://seaborn.pydata.org/tutorial.html)

#### Machine Learning

- **scikit-learn** (v1.3.0+) - Machine learning library
  - Website: [https://scikit-learn.org/](https://scikit-learn.org/)
  - Documentation: [https://scikit-learn.org/stable/user_guide.html](https://scikit-learn.org/stable/user_guide.html)

- **joblib** (v1.3.0+) - Lightweight pipelining and model persistence
  - Documentation: [https://joblib.readthedocs.io/](https://joblib.readthedocs.io/)

#### Database & Storage

- **SQLAlchemy** (v2.0.0+) - Python SQL toolkit and ORM
  - Website: [https://www.sqlalchemy.org/](https://www.sqlalchemy.org/)
  - Documentation: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)

- **SQLite** - Embedded SQL database (built-in with Python)
  - Website: [https://www.sqlite.org/](https://www.sqlite.org/)
  - Python Documentation: [https://docs.python.org/3/library/sqlite3.html](https://docs.python.org/3/library/sqlite3.html)

#### HTTP & API Integration

- **requests** (v2.31.0+) - HTTP library for Python
  - Website: [https://requests.readthedocs.io/](https://requests.readthedocs.io/)
  - Documentation: [https://requests.readthedocs.io/en/latest/](https://requests.readthedocs.io/en/latest/)

#### Configuration & Environment

- **python-dotenv** (v1.0.0+) - Environment variable management
  - GitHub: [https://github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv)
  - Documentation: [https://saurabh-kumar.com/python-dotenv/](https://saurabh-kumar.com/python-dotenv/)

- **pydantic** (v2.0.0+) - Data validation using Python type hints
  - Website: [https://pydantic.dev/](https://pydantic.dev/)
  - Documentation: [https://docs.pydantic.dev/](https://docs.pydantic.dev/)

- **PyYAML** (v6.0.0+) - YAML parser and emitter
  - Website: [https://pyyaml.org/](https://pyyaml.org/)
  - Documentation: [https://pyyaml.org/wiki/PyYAMLDocumentation](https://pyyaml.org/wiki/PyYAMLDocumentation)

### 🤖 AI & Machine Learning Services

#### OpenAI Integration

- **OpenAI API** - AI-powered weather poetry generation
  - Website: [https://openai.com/](https://openai.com/)
  - API Documentation: [https://platform.openai.com/docs](https://platform.openai.com/docs)
  - Model Used: GPT-3.5-turbo for creative weather poetry
  - Implementation: Custom poetry service with fallback templates

- **Google Generative AI (Gemini Pro)** - Alternative AI content generation
  - Website: [https://ai.google.dev/](https://ai.google.dev/)
  - API Documentation: [https://ai.google.dev/docs](https://ai.google.dev/docs)
  - Model Used: Gemini Pro for enhanced AI capabilities
  - Implementation: Multi-provider AI service architecture

### 🌤️ Weather APIs & Data Sources

#### Primary Weather Service

- **OpenWeatherMap API** - Primary weather data provider
  - Website: [https://openweathermap.org/](https://openweathermap.org/)
  - API Documentation: [https://openweathermap.org/api](https://openweathermap.org/api)
  - Services Used: Current Weather, 5-Day Forecast, Geocoding
  - Free Tier: 60 calls/minute, 1,000 calls/day

#### Backup Weather Service

- **WeatherAPI.com** - Fallback weather data provider
  - Website: [https://www.weatherapi.com/](https://www.weatherapi.com/)
  - API Documentation: [https://www.weatherapi.com/docs/](https://www.weatherapi.com/docs/)
  - Implementation: Composite service pattern for reliability

### 🛠️ Development Tools & Code Quality

#### Code Formatting & Style

- **Black** (v23.0.0+) - Python code formatter
  - GitHub: [https://github.com/psf/black](https://github.com/psf/black)
  - Documentation: [https://black.readthedocs.io/](https://black.readthedocs.io/)

- **isort** (v5.12.0+) - Import sorting utility
  - GitHub: [https://github.com/PyCQA/isort](https://github.com/PyCQA/isort)
  - Documentation: [https://pycqa.github.io/isort/](https://pycqa.github.io/isort/)

- **autopep8** (v2.0.0+) - Automatic PEP 8 formatting
  - GitHub: [https://github.com/hhatto/autopep8](https://github.com/hhatto/autopep8)

#### Linting & Type Checking

- **flake8** (v6.0.0+) - Python linting tool
  - Website: [https://flake8.pycqa.org/](https://flake8.pycqa.org/)
  - Documentation: [https://flake8.pycqa.org/en/latest/](https://flake8.pycqa.org/en/latest/)

- **mypy** (v1.5.0+) - Static type checker
  - Website: [http://mypy-lang.org/](http://mypy-lang.org/)
  - Documentation: [https://mypy.readthedocs.io/](https://mypy.readthedocs.io/)

#### Security & Testing

- **bandit** (v1.7.0+) - Security linter for Python
  - GitHub: [https://github.com/PyCQA/bandit](https://github.com/PyCQA/bandit)
  - Documentation: [https://bandit.readthedocs.io/](https://bandit.readthedocs.io/)

- **pytest** (v7.4.0+) - Testing framework
  - Website: [https://pytest.org/](https://pytest.org/)
  - Documentation: [https://docs.pytest.org/](https://docs.pytest.org/)

- **pytest-cov** (v4.1.0+) - Coverage plugin for pytest
  - GitHub: [https://github.com/pytest-dev/pytest-cov](https://github.com/pytest-dev/pytest-cov)

- **pytest-mock** (v3.11.0+) - Mocking plugin for pytest
  - GitHub: [https://github.com/pytest-dev/pytest-mock](https://github.com/pytest-dev/pytest-mock)

#### Development Environment

- **pre-commit** (v3.3.0+) - Git hooks framework
  - Website: [https://pre-commit.com/](https://pre-commit.com/)
  - Documentation: [https://pre-commit.com/hooks.html](https://pre-commit.com/hooks.html)

- **IPython** (v8.0.0+) - Enhanced interactive Python shell
  - Website: [https://ipython.org/](https://ipython.org/)
  - Documentation: [https://ipython.readthedocs.io/](https://ipython.readthedocs.io/)

- **Jupyter** (v1.0.0+) - Interactive computing environment
  - Website: [https://jupyter.org/](https://jupyter.org/)
  - Documentation: [https://jupyter-notebook.readthedocs.io/](https://jupyter-notebook.readthedocs.io/)

### 📚 Documentation & Learning Resources

#### Official Python Documentation

- **Python Official Documentation** - Core language reference
  - Website: [https://docs.python.org/3/](https://docs.python.org/3/)
  - Tutorial: [https://docs.python.org/3/tutorial/](https://docs.python.org/3/tutorial/)

#### MDN Web Documentation

- **MDN Web Docs** - Web development reference (for understanding web APIs)
  - Website: [https://developer.mozilla.org/](https://developer.mozilla.org/)
  - API Reference: [https://developer.mozilla.org/en-US/docs/Web/API](https://developer.mozilla.org/en-US/docs/Web/API)
  - Used for: Understanding REST API patterns and HTTP methods

#### Architecture & Design Patterns

- **Clean Architecture** by Robert C. Martin
  - Concepts applied: Dependency inversion, separation of concerns
  - Reference: [https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

- **SOLID Principles** - Object-oriented design principles
  - Applied throughout the codebase for maintainable architecture
  - Reference: [https://en.wikipedia.org/wiki/SOLID](https://en.wikipedia.org/wiki/SOLID)

#### Documentation Tools

- **MkDocs** (v1.5.0+) - Static site generator for documentation
  - Website: [https://www.mkdocs.org/](https://www.mkdocs.org/)
  - Documentation: [https://www.mkdocs.org/user-guide/](https://www.mkdocs.org/user-guide/)

- **MkDocs Material** (v9.0.0+) - Material theme for MkDocs
  - Website: [https://squidfunk.github.io/mkdocs-material/](https://squidfunk.github.io/mkdocs-material/)
  - Documentation: [https://squidfunk.github.io/mkdocs-material/getting-started/](https://squidfunk.github.io/mkdocs-material/getting-started/)

### 🔧 CI/CD & DevOps Tools

#### GitHub Actions

- **GitHub Actions** - CI/CD platform
  - Documentation: [https://docs.github.com/en/actions](https://docs.github.com/en/actions)
  - Workflows: Automated testing, linting, security scanning
  - Multi-OS testing: Ubuntu, Windows, macOS
  - Python versions: 3.9, 3.10, 3.11, 3.12

#### Package Management

- **pip** - Python package installer
  - Documentation: [https://pip.pypa.io/en/stable/](https://pip.pypa.io/en/stable/)

- **setuptools** - Python package development
  - Documentation: [https://setuptools.pypa.io/en/latest/](https://setuptools.pypa.io/en/latest/)

### 🎨 Design & UI Resources

#### Design Inspiration

- **Glassmorphism Design Trend** - Modern UI design pattern
  - Implemented in custom TKinter styling
  - Reference: [https://uxdesign.cc/glassmorphism-in-user-interfaces-1f39bb1308c9](https://uxdesign.cc/glassmorphism-in-user-interfaces-1f39bb1308c9)

- **Material Design** - Google's design system
  - Principles applied to button design and layout
  - Reference: [https://material.io/design](https://material.io/design)

#### Typography

- **Segoe UI** - Primary font family (Windows system font)
- **Georgia & Palatino Linotype** - Poetry display fonts
- **Font selection principles** from typography best practices

### 🌐 Web Standards & Protocols

#### HTTP & REST APIs

- **HTTP/1.1 Specification** - Protocol for API communication
  - RFC 7231: [https://tools.ietf.org/html/rfc7231](https://tools.ietf.org/html/rfc7231)
  - Used for weather API integration

- **JSON Specification** - Data interchange format
  - RFC 7159: [https://tools.ietf.org/html/rfc7159](https://tools.ietf.org/html/rfc7159)
  - Used for API responses and configuration

#### Security Standards

- **OAuth 2.0** - Authorization framework
  - RFC 6749: [https://tools.ietf.org/html/rfc6749](https://tools.ietf.org/html/rfc6749)
  - Applied in API key management patterns

### 📖 Educational Resources

#### Python Learning

- **Real Python** - Python tutorials and best practices
  - Website: [https://realpython.com/](https://realpython.com/)
  - Used for: Advanced Python patterns and GUI development

- **Python Enhancement Proposals (PEPs)**
  - PEP 8 (Style Guide): [https://pep8.org/](https://pep8.org/)
  - PEP 484 (Type Hints): [https://www.python.org/dev/peps/pep-0484/](https://www.python.org/dev/peps/pep-0484/)

#### Software Architecture

- **Martin Fowler's Architecture Patterns**
  - Website: [https://martinfowler.com/architecture/](https://martinfowler.com/architecture/)
  - Applied: Repository pattern, Service layer pattern

### 🏆 Project Attribution

**Author**: E Hunter Petross  
**Institution**: [Educational Institution]  
**Course**: Software Development Capstone  
**Year**: 2024-2025  
**License**: MIT License

### 📝 Citation Format

When citing this project or its components, please use:

```text
Petross, E. H. (2025). Weather Dashboard: A Modern Python GUI Application with Clean Architecture. 
[Software]. GitHub. https://github.com/StrayDogSyn/weather_dashboard_E_Hunter_Petross
```

### 🔄 Version Information

- **Project Version**: 1.0.0
- **Python Compatibility**: 3.8+
- **Last Updated**: January 2025
- **Documentation Version**: 1.0

---

*This Works Cited section is maintained to provide proper attribution to all tools, libraries, and resources that contributed to the development of the Weather Dashboard project. All external resources are used in accordance with their respective licenses and terms of service.*