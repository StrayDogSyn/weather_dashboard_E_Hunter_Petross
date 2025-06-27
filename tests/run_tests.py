"""
Test runner for the Weather Dashboard project.

This script runs all test suites and provides a comprehensive
testing report for the Weather Dashboard application.
"""

import unittest
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import all test modules
from tests.test_weather_models import *
from tests.test_weather_service import *


def run_all_tests():
    """Run all test suites and generate a report."""
    print("=" * 60)
    print("WEATHER DASHBOARD - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Create test loader
    loader = unittest.TestLoader()
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test cases from test_weather_models
    test_suite.addTest(loader.loadTestsFromModule(sys.modules['tests.test_weather_models']))
    
    # Add all test cases from test_weather_service  
    test_suite.addTest(loader.loadTestsFromModule(sys.modules['tests.test_weather_service']))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    # Print comprehensive summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Successful Tests: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed Tests: {len(result.failures)}")
    print(f"Error Tests: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "N/A")
    print(f"Overall Result: {'PASS' if result.wasSuccessful() else 'FAIL'}")
    
    # Print failure details if any
    if result.failures:
        print("\n" + "-" * 40)
        print("FAILURE DETAILS:")
        print("-" * 40)
        for test, failure in result.failures:
            print(f"FAILED: {test}")
            print(f"Reason: {failure}")
            print("-" * 40)
    
    # Print error details if any
    if result.errors:
        print("\n" + "-" * 40)
        print("ERROR DETAILS:")
        print("-" * 40)
        for test, error in result.errors:
            print(f"ERROR: {test}")
            print(f"Details: {error}")
            print("-" * 40)
    
    print(f"\nTest run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return result.wasSuccessful()


def run_specific_test_module(module_name):
    """Run tests from a specific module."""
    print(f"Running tests from: {module_name}")
    print("-" * 40)
    
    # Import specific module
    if module_name == "models":
        from tests.test_weather_models import *
        test_module = sys.modules['tests.test_weather_models']
    elif module_name == "service":
        from tests.test_weather_service import *
        test_module = sys.modules['tests.test_weather_service']
    else:
        print(f"Unknown test module: {module_name}")
        return False
    
    # Create test suite for specific module
    loader = unittest.TestLoader()
    test_suite = loader.loadTestsFromModule(test_module)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print(f"\nModule '{module_name}' Results:")
    print(f"Tests: {result.testsRun}, Failures: {len(result.failures)}, Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    # Check command line arguments
    if len(sys.argv) > 1:
        module_name = sys.argv[1]
        success = run_specific_test_module(module_name)
    else:
        success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
