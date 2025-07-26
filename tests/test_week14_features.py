"""
Week 14 Testing & Debugging Suite

Comprehensive testing suite for ML-powered weather prediction features
including model training, integration, and forecast UI components.
"""

import asyncio
import json
import logging
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)

# Import modules to test
from src.models.predictive_models import (
    ModelMetrics,
    ModelType,
    PredictionResult,
    WeatherPredictor,
)
from src.services.model_integration_service import (
    IntegratedForecast,
    ModelIntegrationService,
)
from src.services.model_training_service import ModelTrainingService, TrainingResult


class TestWeatherPredictor(unittest.TestCase):
    """Test cases for WeatherPredictor class."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.predictor = WeatherPredictor(ModelType.LINEAR_REGRESSION)

        # Mock data for testing
        self.sample_weather_data = [
            {
                "timestamp": "2024-01-01T12:00:00",
                "temperature": 20.0,
                "humidity": 65.0,
                "pressure": 1013.25,
                "description": "clear sky",
            },
            {
                "timestamp": "2024-01-02T12:00:00",
                "temperature": 22.0,
                "humidity": 60.0,
                "pressure": 1015.0,
                "description": "few clouds",
            },
            {
                "timestamp": "2024-01-03T12:00:00",
                "temperature": 18.0,
                "humidity": 70.0,
                "pressure": 1010.0,
                "description": "scattered clouds",
            },
        ]

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_predictor_initialization(self):
        """Test WeatherPredictor initialization."""
        self.assertEqual(self.predictor.model_type, ModelType.LINEAR_REGRESSION)
        self.assertFalse(self.predictor.is_trained)
        self.assertEqual(len(self.predictor.models), 0)
        self.assertEqual(len(self.predictor.feature_columns), 0)

    def test_feature_preparation(self):
        """Test feature preparation from weather data."""
        features_df = self.predictor.prepare_features(self.sample_weather_data)

        self.assertFalse(features_df.empty)
        self.assertIn("temp_celsius", features_df.columns)
        self.assertIn("humidity", features_df.columns)
        self.assertIn("pressure", features_df.columns)

        # Check data types
        self.assertTrue(features_df["temp_celsius"].dtype in ["float64", "int64"])
        self.assertTrue(features_df["humidity"].dtype in ["float64", "int64"])

    def test_model_training_with_insufficient_data(self):
        """Test model training with insufficient data."""
        # Single data point should raise an error
        single_data = [self.sample_weather_data[0]]
        features_df = self.predictor.prepare_features(single_data)

        with self.assertRaises(ValueError):
            self.predictor.train_models(features_df, target_column="temp_celsius")

    def test_prediction_without_training(self):
        """Test prediction attempt without training."""
        # Test with sample conditions
        test_conditions = {
            "temperature": 20.0,
            "humidity": 65.0,
            "pressure": 1013.25,
            "description": "clear sky",
        }

        result = self.predictor.predict_temperature(test_conditions, hours_ahead=24)

        # Should return empty list for untrained model
        self.assertEqual(result, [])

    @patch("src.models.predictive_models.SKLEARN_AVAILABLE", True)
    def test_model_training_success(self):
        """Test successful model training."""
        # Create larger dataset for training
        extended_data = []
        for i in range(50):
            data_point = {
                "timestamp": f"2024-01-{i+1: 02d}T12: 00: 00",
                "temperature": 20.0 + (i % 10),
                "humidity": 60.0 + (i % 20),
                "pressure": 1013.0 + (i % 5),
                "description": "clear sky",
            }
            extended_data.append(data_point)

        features_df = self.predictor.prepare_features(extended_data)

        try:
            metrics = self.predictor.train_models(
                features_df, target_column="temp_celsius"
            )
            self.assertIsInstance(metrics, dict)
            self.assertTrue(self.predictor.is_trained)
        except ImportError:
            # Skip if sklearn not available
            self.skipTest("scikit-learn not available")


class TestModelTrainingService(unittest.TestCase):
    """Test cases for ModelTrainingService."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()

        # Mock dependencies
        self.mock_config = Mock()
        self.mock_data_storage = Mock()
        self.mock_weather_api = Mock()

        # Configure mock data storage
        self.mock_data_storage.load_data.return_value = {
            "data": [
                {
                    "timestamp": "2024-01-01T12:00:00",
                    "temperature": 20.0,
                    "humidity": 65.0,
                    "pressure": 1013.25,
                    "description": "clear sky",
                }
            ]
        }

        self.training_service = ModelTrainingService(
            self.mock_config, self.mock_data_storage, self.mock_weather_api
        )

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_service_initialization(self):
        """Test ModelTrainingService initialization."""
        self.assertIsNotNone(self.training_service.predictors)
        self.assertEqual(len(self.training_service.training_history), 0)
        self.assertIsNotNone(self.training_service.training_config)

    async def test_collect_training_data(self):
        """Test training data collection."""
        data = await self.training_service.collect_training_data(days=30)

        self.mock_data_storage.load_data.assert_called_once_with("weather_history.json")
        # Check if data was processed correctly
        self.assertIsNotNone(data)

    def test_should_retrain_with_no_history(self):
        """Test retrain decision with no training history."""
        self.assertTrue(self.training_service._should_retrain())

    def test_training_config_defaults(self):
        """Test default training configuration."""
        config = self.training_service.training_config

        self.assertIn("linear_regression", config.model_types)
        self.assertIn("random_forest", config.model_types)
        self.assertIn("gradient_boosting", config.model_types)
        self.assertEqual(config.training_days, 30)
        self.assertEqual(config.validation_split, 0.2)
        self.assertGreater(config.retrain_threshold, 0)

    def test_save_and_load_training_history(self):
        """Test training history persistence."""
        # Create sample training result
        sample_result = TrainingResult(
            timestamp=datetime.now(),
            model_metrics={
                "test_model": ModelMetrics(
                    mae=1.0, mse=2.0, rmse=1.4, r2=0.8, cv_score=0.75
                )
            },
            training_duration=120.0,
            data_points_used=100,
            validation_score=0.8,
            status="success",
            notes="Test training",
        )

        self.training_service.training_history.append(sample_result)

        # Test save
        self.training_service.save_training_history()

        # Test load
        self.training_service.training_history = []
        self.training_service.load_training_history()

        self.assertEqual(len(self.training_service.training_history), 1)
        loaded_result = self.training_service.training_history[0]
        self.assertEqual(loaded_result.status, "success")
        self.assertEqual(loaded_result.validation_score, 0.8)


class TestModelIntegrationService(unittest.TestCase):
    """Test cases for ModelIntegrationService."""

    def setUp(self):
        """Set up test environment."""
        # Mock dependencies
        self.mock_weather_api = Mock()
        self.mock_data_storage = Mock()
        self.mock_training_service = Mock()

        # Configure mock weather API
        self.mock_weather_api.get_forecast.return_value = Mock()
        self.mock_weather_api.get_current_weather.return_value = Mock()

        # Configure mock training service
        self.mock_training_service.predictors = {
            "linear_regression": Mock(),
            "random_forest": Mock(),
        }
        self.mock_training_service.training_history = []

        self.integration_service = ModelIntegrationService(
            self.mock_weather_api, self.mock_data_storage, self.mock_training_service
        )

    def test_service_initialization(self):
        """Test ModelIntegrationService initialization."""
        self.assertIsNotNone(self.integration_service.predictors)
        self.assertIsNotNone(self.integration_service.model_weights)
        self.assertFalse(self.integration_service.models_loaded)

    def test_prediction_cache_operations(self):
        """Test prediction cache functionality."""
        # Test cache is initially empty
        self.assertEqual(len(self.integration_service.prediction_cache), 0)

        # Test cache clearing
        self.integration_service.prediction_cache["test_key"] = {"data": "test"}
        self.integration_service.clear_prediction_cache()
        self.assertEqual(len(self.integration_service.prediction_cache), 0)

    def test_model_weights_calculation(self):
        """Test model weight calculation."""
        # Mock training history
        sample_metrics = {
            "linear_regression": ModelMetrics(
                mae=1.0, mse=2.0, rmse=1.4, r2=0.9, cv_score=0.85
            ),
            "random_forest": ModelMetrics(
                mae=0.8, mse=1.5, rmse=1.2, r2=0.95, cv_score=0.90
            ),
        }

        sample_training = TrainingResult(
            timestamp=datetime.now(),
            model_metrics=sample_metrics,
            training_duration=120.0,
            data_points_used=100,
            validation_score=0.9,
            status="success",
            notes="Test",
        )

        self.mock_training_service.training_history = [sample_training]

        # Run async method
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.integration_service._calculate_model_weights())

        # Check weights were calculated
        self.assertIn("linear_regression", self.integration_service.model_weights)
        self.assertIn("random_forest", self.integration_service.model_weights)

    def test_service_status(self):
        """Test service status retrieval."""
        status = self.integration_service.get_service_status()

        self.assertIsInstance(status.models_loaded, bool)
        self.assertIsInstance(status.active_models, list)
        self.assertIsInstance(status.prediction_accuracy, dict)
        self.assertIsNotNone(status.service_uptime)

    async def test_validation_integration(self):
        """Test integration validation."""
        # Mock successful API calls
        self.mock_weather_api.get_current_weather.return_value = Mock()
        self.mock_data_storage.load_data.return_value = {"test": "data"}

        validation_results = await self.integration_service.validate_integration()

        self.assertIsInstance(validation_results, dict)
        self.assertIn("models_loaded", validation_results)
        self.assertIn("weather_api_connected", validation_results)
        self.assertIn("data_storage_accessible", validation_results)


class TestPredictionAccuracy(unittest.TestCase):
    """Test prediction accuracy and performance metrics."""

    def test_prediction_result_creation(self):
        """Test PredictionResult data class."""
        result = PredictionResult(
            timestamp=datetime.now(),
            predicted_temperature=25.5,
            confidence_interval=(23.0, 28.0),
            weather_pattern="sunny",
            prediction_accuracy=0.85,
            features_used=["temperature", "humidity", "pressure"],
        )

        self.assertEqual(result.predicted_temperature, 25.5)
        self.assertEqual(result.confidence_interval, (23.0, 28.0))
        self.assertEqual(result.weather_pattern, "sunny")
        self.assertEqual(result.prediction_accuracy, 0.85)
        self.assertIn("temperature", result.features_used)

    def test_model_metrics_creation(self):
        """Test ModelMetrics data class."""
        metrics = ModelMetrics(mae=1.5, mse=3.2, rmse=1.8, r2=0.92, cv_score=0.88)

        self.assertEqual(metrics.mae, 1.5)
        self.assertEqual(metrics.r2, 0.92)
        self.assertGreater(metrics.cv_score, 0.8)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    def setUp(self):
        """Set up test environment."""
        self.mock_config = Mock()
        self.mock_data_storage = Mock()
        self.mock_weather_api = Mock()

    def test_training_with_no_data(self):
        """Test training service with no historical data."""
        # Mock empty data
        self.mock_data_storage.load_data.return_value = None

        training_service = ModelTrainingService(
            self.mock_config, self.mock_data_storage, self.mock_weather_api
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Should handle empty data gracefully
        data = loop.run_until_complete(training_service.collect_training_data(30))
        self.assertTrue(data.empty)

    def test_integration_with_failed_api(self):
        """Test integration service with failed API calls."""
        # Mock API failure
        self.mock_weather_api.get_forecast.return_value = None
        self.mock_weather_api.get_current_weather.return_value = None

        training_service = Mock()
        integration_service = ModelIntegrationService(
            self.mock_weather_api, self.mock_data_storage, training_service
        )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Should raise error for failed forecast
        with self.assertRaises(ValueError):
            loop.run_until_complete(
                integration_service.get_enhanced_forecast("NonexistentCity", 5)
            )

    def test_predictor_with_invalid_data(self):
        """Test predictor with invalid input data."""
        predictor = WeatherPredictor(ModelType.LINEAR_REGRESSION)

        # Test with empty data
        result = predictor.prepare_features([])
        self.assertTrue(result.empty)

        # Test with malformed data
        malformed_data = [{"invalid": "data"}]
        result = predictor.prepare_features(malformed_data)
        # Should handle gracefully, might be empty or have default values
        self.assertIsNotNone(result)


class TestPerformanceBenchmarks(unittest.TestCase):
    """Performance testing for ML components."""

    def test_training_performance(self):
        """Test training performance with various data sizes."""
        predictor = WeatherPredictor(ModelType.LINEAR_REGRESSION)

        # Test with different data sizes
        for size in [10, 50, 100]:
            with self.subTest(size=size):
                # Generate test data
                test_data = []
                for i in range(size):
                    test_data.append(
                        {
                            "timestamp": f"2024-01-{i+1: 02d}T12: 00: 00",
                            "temperature": 20.0 + (i % 10),
                            "humidity": 60.0 + (i % 20),
                            "pressure": 1013.0 + (i % 5),
                            "description": "clear",
                        }
                    )

                start_time = datetime.now()
                features_df = predictor.prepare_features(test_data)
                processing_time = (datetime.now() - start_time).total_seconds()

                # Should process quickly
                self.assertLess(processing_time, 5.0)  # Less than 5 seconds
                self.assertEqual(len(features_df), size)

    def test_prediction_speed(self):
        """Test prediction generation speed."""
        predictor = WeatherPredictor(ModelType.LINEAR_REGRESSION)

        # Mock trained predictor
        predictor.is_trained = True
        predictor.feature_columns = ["temp_celsius", "humidity", "pressure"]

        test_data = [
            {
                "timestamp": "2024-01-01T12:00:00",
                "temperature": 20.0,
                "humidity": 65.0,
                "pressure": 1013.25,
                "description": "clear",
            }
        ]

        start_time = datetime.now()
        # Test prediction with mock data
        test_conditions = test_data[0]
        result = predictor.predict_temperature(test_conditions, hours_ahead=24)
        prediction_time = (datetime.now() - start_time).total_seconds()

        # Should be very fast
        self.assertLess(prediction_time, 1.0)  # Less than 1 second


def run_all_tests():
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestWeatherPredictor,
        TestModelTrainingService,
        TestModelIntegrationService,
        TestPredictionAccuracy,
        TestErrorHandling,
        TestPerformanceBenchmarks,
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


def run_integration_tests():
    """Run integration tests specifically."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add integration-focused tests
    integration_classes = [TestModelIntegrationService, TestErrorHandling]

    for test_class in integration_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


def run_performance_tests():
    """Run performance tests specifically."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestPerformanceBenchmarks)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "integration":
            print("Running integration tests...")
            result = run_integration_tests()
        elif sys.argv[1] == "performance":
            print("Running performance tests...")
            result = run_performance_tests()
        else:
            print("Running all tests...")
            result = run_all_tests()
    else:
        print("Running all tests...")
        result = run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
