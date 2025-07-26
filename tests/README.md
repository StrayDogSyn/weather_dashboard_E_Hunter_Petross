# Testing Documentation

This folder contains comprehensive unit tests for the Weather Dashboard application.

## Test Structure

### 📁 Test Files

1. **`test_weather_models.py`** - Tests for data models and domain objects
   - Location model validation
   - Temperature conversion and formatting
   - Wind direction calculations
   - Current weather data validation
   - Weather forecast structure
   - Data model integrity

2. **`test_weather_service.py`** - Tests for core business logic
   - Weather service functionality
   - Caching behavior and strategy
   - API integration mocking
   - Data storage integration
   - Input validation and error handling
   - Service dependencies and injection

3. **`test_validators.py`** - Tests for data validation utilities
   - Input validation functions
   - Data sanitization
   - Error handling for invalid inputs

4. **`test_cortana_integration.py`** - Tests for voice assistant integration
   - Voice command processing
   - Speech recognition functionality
   - Voice response generation

5. **`test_week14_features.py`** - Tests for advanced features and ML integration
   - Machine learning model integration
   - Advanced analytics features
   - Performance optimization tests

6. **`run_tests.py`** - Test runner and reporting utility
   - Comprehensive test execution
   - Detailed reporting and analytics
   - Module-specific test running
   - Test result summarization

## Running Tests

### Run All Tests

```powershell
# From the project root directory
python -m tests.run_tests

# Or from the tests directory
python run_tests.py
```

### Run Specific Test Modules

```powershell
# Test only the weather models
python -m tests.test_weather_models

# Test only the weather service
python -m tests.test_weather_service

# Run specific module via test runner
python tests/run_tests.py models
python tests/run_tests.py service
```

### Run Individual Test Classes

```powershell
# Run specific test class
python -m unittest tests.test_weather_models.TestLocationModel -v

# Run specific test method
python -m unittest tests.test_weather_models.TestLocationModel.test_valid_location_creation -v
```

## Test Coverage

### Weather Models (`test_weather_models.py`)

- **Location Model**: Geographic coordinate validation, display formatting
- **Temperature Model**: Unit conversions (Celsius, Fahrenheit, Kelvin)
- **Wind Model**: Direction name calculations, speed formatting
- **Current Weather**: Data integrity, severe weather detection
- **Weather Forecast**: Multi-day forecast structure, data access
- **Precipitation**: Total precipitation calculations
- **Weather Enums**: Enumeration values and validation

### Weather Service (`test_weather_service.py`)

- **Core Functionality**: Weather retrieval, forecast generation
- **Caching Strategy**: Cache hits/misses, expiration handling
- **API Integration**: Mock API interactions, error handling
- **Data Validation**: Input sanitization, parameter validation
- **Storage Integration**: Favorite cities, data persistence
- **Error Handling**: Graceful degradation, exception management

## Test Dependencies

The tests use Python's built-in `unittest` framework and include:

- **Mock Objects**: For API and dependency isolation
- **Test Fixtures**: Reusable test data and configurations
- **Assertion Helpers**: Custom validation and comparison utilities
- **Test Utilities**: Shared test setup and teardown functions

## Test Data

Test cases use realistic sample data including:

- **Weather Conditions**: Clear, cloudy, rainy, stormy scenarios
- **Global Locations**: Major cities worldwide with valid coordinates
- **Temperature Ranges**: Realistic values in multiple units
- **API Responses**: Simulated OpenWeatherMap API data structures

## Continuous Integration

These tests are designed to run in CI/CD environments:

- **Environment Independence**: No external API dependencies during testing
- **Deterministic Results**: Consistent outcomes across environments
- **Fast Execution**: Optimized for quick feedback cycles
- **Comprehensive Coverage**: Validates all critical application paths

## Test Best Practices

The test suite follows industry best practices:

- **Isolation**: Each test is independent and can run in any order
- **Mocking**: External dependencies are mocked for reliability
- **Naming**: Clear, descriptive test method names
- **Documentation**: Each test includes purpose and expected behavior
- **Assertions**: Comprehensive validation of expected outcomes
- **Setup/Teardown**: Proper test environment management

## Resources & Attribution

For information about testing frameworks, best practices, and tools used in this test suite, please refer to the [Works Cited section](../docs/README.md#works-cited) in the documentation index.

---

**Last Updated**: June 27, 2025  
**Test Framework**: Python unittest  
**Coverage Target**: >90% code coverage
