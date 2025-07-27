"""
Model Training Service for Weather Prediction

This service handles the training pipeline for weather prediction models,
including data preparation, model training, validation, and performance monitoring.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ..config import config_manager
from ..interfaces.weather_interfaces import IDataStorage, IWeatherAPI
from ..models.predictive_models import (
    ModelMetrics,
    ModelType,
    PredictionResult,
    WeatherPredictor,
)


@dataclass
class TrainingConfig:
    """Configuration for model training."""

    model_types: List[str]
    training_days: int
    validation_split: float
    retrain_threshold: float  # R² threshold below which to retrain
    auto_retrain_days: int  # Days after which to automatically retrain
    min_data_points: int  # Minimum data points required for training


@dataclass
class TrainingResult:
    """Result of model training session."""

    timestamp: datetime
    model_metrics: Dict[str, ModelMetrics]
    training_duration: float
    data_points_used: int
    validation_score: float
    status: str
    notes: str


class ModelTrainingService:
    """Service for training and managing weather prediction models."""

    def __init__(
        self, config_mgr, data_storage: IDataStorage, weather_api: IWeatherAPI
    ):
        """Initialize the model training service.

        Args:
            config_mgr: Configuration manager
            data_storage: Data storage service
            weather_api: Weather API service
        """
        self.config = config_mgr
        self.data_storage = data_storage
        self.weather_api = weather_api
        self.logger = logging.getLogger(__name__)

        # Training configuration
        self.training_config = TrainingConfig(
            model_types=["linear_regression", "random_forest", "gradient_boosting"],
            training_days=30,
            validation_split=0.2,
            retrain_threshold=0.7,
            auto_retrain_days=7,
            min_data_points=100,
        )

        # Model instances
        self.predictors = {}
        for model_type in ModelType:
            self.predictors[model_type.value] = WeatherPredictor(model_type)

        # Training history
        self.training_history = []
        self.load_training_history()

        # Paths
        self.training_data_path = Path("data/training")
        self.training_data_path.mkdir(exist_ok=True)

        self.model_reports_path = Path("data/reports")
        self.model_reports_path.mkdir(exist_ok=True)

    async def collect_training_data(self, days: int = 30) -> pd.DataFrame:
        """Collect historical weather data for training.

        Args:
            days: Number of days of historical data to collect

        Returns:
            DataFrame with training data
        """
        self.logger.info(f"Collecting training data for {days} days")

        # Get historical data from storage
        historical_data = self.data_storage.load_data("weather_history.json")

        if not historical_data or not historical_data.get("data"):
            self.logger.warning("No historical data found in storage")
            return pd.DataFrame()

        # Convert to DataFrame
        weather_records = historical_data.get("data", [])
        if not weather_records:
            return pd.DataFrame()

        df = pd.DataFrame(weather_records)

        # Filter by date range if timestamps are available
        if "timestamp" in df.columns:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df[(df["timestamp"] >= start_date) & (df["timestamp"] <= end_date)]

        # Ensure required columns exist
        required_columns = [
            "timestamp",
            "temperature",
            "humidity",
            "pressure",
            "description",
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return pd.DataFrame()

        # Clean and prepare data
        df = self._clean_training_data(df)

        self.logger.info(f"Collected {len(df)} data points for training")
        return df

    def _clean_training_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare training data.

        Args:
            df: Raw training data

        Returns:
            Cleaned DataFrame
        """
        # Convert timestamp to datetime
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Remove duplicates
        df = df.drop_duplicates(subset=["timestamp"])

        # Sort by timestamp
        df = df.sort_values("timestamp")

        # Remove outliers (temperatures outside reasonable range)
        temp_lower = df["temperature"].quantile(0.01)
        temp_upper = df["temperature"].quantile(0.99)
        df = df[(df["temperature"] >= temp_lower) & (df["temperature"] <= temp_upper)]

        # Remove rows with missing critical data
        df = df.dropna(subset=["temperature", "humidity", "pressure"])

        # Fill missing descriptions
        df["description"] = df["description"].fillna("unknown")

        # Add derived features
        df["temperature_celsius"] = df["temperature"]

        return df

    async def train_all_models(
        self, force_retrain: bool = False
    ) -> Dict[str, TrainingResult]:
        """Train all configured prediction models.

        Args:
            force_retrain: Force retraining even if models are recent

        Returns:
            Dictionary of training results by model type
        """
        self.logger.info("Starting model training for all model types")

        # Check if retraining is needed
        if not force_retrain and not self._should_retrain():
            self.logger.info("Models are recent and performing well, skipping training")
            return {}

        # Collect training data
        training_data = await self.collect_training_data(
            self.training_config.training_days
        )

        if len(training_data) < self.training_config.min_data_points:
            raise ValueError(
                f"Insufficient training data: {len(training_data)} < {self.training_config.min_data_points}"
            )

        results = {}

        for model_type in ModelType:
            try:
                result = await self._train_single_model(model_type, training_data)
                results[model_type.value] = result
                self.training_history.append(result)

            except Exception as e:
                self.logger.error(f"Error training {model_type.value}: {e}")
                results[model_type.value] = TrainingResult(
                    timestamp=datetime.now(),
                    model_metrics={},
                    training_duration=0.0,
                    data_points_used=len(training_data),
                    validation_score=0.0,
                    status="failed",
                    notes=str(e),
                )

        # Save training history
        self.save_training_history()

        # Generate training report
        await self._generate_training_report(results, training_data)

        self.logger.info("Model training completed")
        return results

    async def _train_single_model(
        self, model_type: ModelType, training_data: pd.DataFrame
    ) -> TrainingResult:
        """Train a single prediction model.

        Args:
            model_type: Type of model to train
            training_data: Training data DataFrame

        Returns:
            Training result
        """
        start_time = datetime.now()
        self.logger.info(f"Training {model_type.value} model")

        try:
            # Get predictor for this model type
            predictor = self.predictors[model_type.value]

            # Prepare features
            feature_data = predictor.prepare_features(training_data.to_dict("records"))

            if feature_data.empty:
                raise ValueError("No features could be prepared from training data")

            # Train the model
            metrics = predictor.train_models(feature_data, target_column="temp_celsius")

            # Calculate training duration
            training_duration = (datetime.now() - start_time).total_seconds()

            # Get validation score (average R² across all sub-models)
            validation_score = float(np.mean([m.r2 for m in metrics.values()]))

            # Create result
            result = TrainingResult(
                timestamp=start_time,
                model_metrics=metrics,
                training_duration=training_duration,
                data_points_used=len(feature_data),
                validation_score=validation_score,
                status="success",
                notes=f"Trained with {len(feature_data)} data points",
            )

            self.logger.info(
                f"Successfully trained {model_type.value} model (R²: {validation_score: .3f})"
            )
            return result

        except Exception as e:
            training_duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Failed to train {model_type.value} model: {e}")

            return TrainingResult(
                timestamp=start_time,
                model_metrics={},
                training_duration=training_duration,
                data_points_used=len(training_data),
                validation_score=0.0,
                status="failed",
                notes=str(e),
            )

    def _should_retrain(self) -> bool:
        """Check if models should be retrained based on performance and age."""
        if not self.training_history:
            return True

        # Get most recent training
        latest_training = max(self.training_history, key=lambda x: x.timestamp)

        # Check age
        days_since_training = (datetime.now() - latest_training.timestamp).days
        if days_since_training >= self.training_config.auto_retrain_days:
            self.logger.info(
                f"Models are {days_since_training} days old, retraining needed"
            )
            return True

        # Check performance
        if latest_training.validation_score < self.training_config.retrain_threshold:
            self.logger.info(
                f"Model performance below threshold ({latest_training.validation_score: .3f} < {self.training_config.retrain_threshold})"
            )
            return True

        return False

    async def validate_models(
        self, test_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, float]:
        """Validate trained models against test data.

        Args:
            test_data: Optional test data, will collect recent data if not provided

        Returns:
            Validation scores by model type
        """
        self.logger.info("Validating models")

        if test_data is None:
            # Collect recent data for validation
            test_data = await self.collect_training_data(days=7)

        if test_data.empty:
            self.logger.warning("No test data available for validation")
            return {}

        validation_scores = {}

        for model_type, predictor in self.predictors.items():
            if not predictor.is_trained:
                continue

            try:
                # Prepare test features
                feature_data = predictor.prepare_features(test_data.to_dict("records"))

                if feature_data.empty:
                    continue

                # Make predictions on test data
                X_test = feature_data[predictor.feature_columns]
                y_true = feature_data["temp_celsius"]

                # Get ensemble predictions
                predictions = []
                for _, model in predictor.models.items():
                    if hasattr(model, "predict"):
                        try:
                            if (
                                "linear_regression" in predictor.models
                                and model == predictor.models["linear_regression"]
                            ):
                                X_scaled = predictor.scalers["features"].transform(
                                    X_test
                                )
                                pred = model.predict(X_scaled)
                            else:
                                pred = model.predict(X_test)
                            predictions.append(pred)
                        except Exception as e:
                            self.logger.warning(f"Error in model prediction: {e}")

                if predictions:
                    # Ensemble prediction
                    y_pred = np.mean(predictions, axis=0)

                    # Calculate R² score manually
                    ss_res = np.sum((y_true - y_pred) ** 2)
                    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
                    score = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0.0
                    validation_scores[model_type] = score

                    self.logger.info(f"{model_type} validation R²: {score: .3f}")

            except Exception as e:
                self.logger.error(f"Error validating {model_type}: {e}")
                validation_scores[model_type] = 0.0

        return validation_scores

    async def _generate_training_report(
        self, results: Dict[str, TrainingResult], training_data: pd.DataFrame
    ):
        """Generate comprehensive training report.

        Args:
            results: Training results
            training_data: Training data used
        """
        report_lines = []
        report_lines.append("# Weather Prediction Model Training Report")
        report_lines.append(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        report_lines.append("")

        # Training summary
        report_lines.append("## Training Summary")
        report_lines.append(f"- Training data points: {len(training_data)}")
        report_lines.append(
            f"- Training period: {self.training_config.training_days} days"
        )
        report_lines.append(f"- Models trained: {len(results)}")
        report_lines.append("")

        # Model performance
        report_lines.append("## Model Performance")
        for model_type, result in results.items():
            report_lines.append(f"### {model_type.replace('_', ' ').title()}")
            report_lines.append(f"- Status: {result.status}")
            report_lines.append(
                f"- Training duration: {result.training_duration: .2f} seconds"
            )
            report_lines.append(
                f"- Validation score (R²): {result.validation_score: .3f}"
            )
            report_lines.append(f"- Data points used: {result.data_points_used}")

            if result.model_metrics:
                report_lines.append("- Sub-model metrics:")
                for sub_model, metrics in result.model_metrics.items():
                    report_lines.append(
                        f"  - {sub_model}: MAE={metrics.mae: .2f}, RMSE={metrics.rmse: .2f}, R²={metrics.r2: .3f}"
                    )

            if result.notes:
                report_lines.append(f"- Notes: {result.notes}")
            report_lines.append("")

        # Training data analysis
        report_lines.append("## Training Data Analysis")
        if not training_data.empty:
            report_lines.append(
                f"- Temperature range: {training_data['temperature'].min():.1f}°C to {training_data['temperature'].max():.1f}°C"
            )
            report_lines.append(
                f"- Average temperature: {training_data['temperature'].mean():.1f}°C"
            )
            report_lines.append(
                f"- Humidity range: {training_data['humidity'].min():.1f}% to {training_data['humidity'].max():.1f}%"
            )
            report_lines.append(
                f"- Pressure range: {training_data['pressure'].min():.1f} hPa to {training_data['pressure'].max():.1f} hPa"
            )

            # Weather pattern distribution
            if "description" in training_data.columns:
                pattern_counts = training_data["description"].value_counts()
                report_lines.append("- Weather pattern distribution:")
                for pattern, count in pattern_counts.head(5).items():
                    percentage = (count / len(training_data)) * 100
                    report_lines.append(f"  - {pattern}: {count} ({percentage:.1f}%)")

        # Recommendations
        report_lines.append("## Recommendations")
        best_model = (
            max(results.items(), key=lambda x: x[1].validation_score)
            if results
            else None
        )
        if best_model:
            report_lines.append(
                f"- Best performing model: {best_model[0]} (R²: {best_model[1].validation_score: .3f})"
            )

        failed_models = [
            name for name, result in results.items() if result.status == "failed"
        ]
        if failed_models:
            report_lines.append(
                f"- Failed models need attention: {', '.join(failed_models)}"
            )

        low_performance = [
            name for name, result in results.items() if result.validation_score < 0.6
        ]
        if low_performance:
            report_lines.append(
                f"- Models with low performance: {', '.join(low_performance)}"
            )

        if len(training_data) < 500:
            report_lines.append(
                "- Consider collecting more training data for better model performance"
            )

        # Save report
        report_content = "\n".join(report_lines)
        report_file = (
            self.model_reports_path
            / f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )

        with open(report_file, "w") as f:
            f.write(report_content)

        self.logger.info(f"Training report saved to {report_file}")

    def save_training_history(self):
        """Save training history to disk."""
        history_file = self.training_data_path / "training_history.json"

        # Convert to serializable format
        history_data = []
        for result in self.training_history:
            result_dict = asdict(result)
            result_dict["timestamp"] = result.timestamp.isoformat()

            # Convert ModelMetrics to dict
            metrics_dict = {}
            for name, metrics in result.model_metrics.items():
                metrics_dict[name] = asdict(metrics)
            result_dict["model_metrics"] = metrics_dict

            history_data.append(result_dict)

        with open(history_file, "w") as f:
            json.dump(history_data, f, indent=2)

        self.logger.debug(f"Training history saved to {history_file}")

    def load_training_history(self):
        """Load training history from disk."""
        history_file = self.training_data_path / "training_history.json"

        if not history_file.exists():
            return

        try:
            with open(history_file, "r") as f:
                history_data = json.load(f)

            for result_dict in history_data:
                # Convert timestamp back to datetime
                result_dict["timestamp"] = datetime.fromisoformat(
                    result_dict["timestamp"]
                )

                # Convert metrics back to ModelMetrics objects
                model_metrics = {}
                for name, metrics_dict in result_dict["model_metrics"].items():
                    model_metrics[name] = ModelMetrics(**metrics_dict)
                result_dict["model_metrics"] = model_metrics

                # Create TrainingResult object
                result = TrainingResult(**result_dict)
                self.training_history.append(result)

            self.logger.debug(
                f"Loaded {len(self.training_history)} training history entries"
            )

        except Exception as e:
            self.logger.error(f"Error loading training history: {e}")

    def get_model_status(self) -> Dict[str, Any]:
        """Get current status of all models.

        Returns:
            Dictionary with model status information
        """
        status = {
            "models": {},
            "last_training": None,
            "next_retrain_due": None,
            "training_data_points": 0,
        }

        # Model status
        for model_type, predictor in self.predictors.items():
            status["models"][model_type] = {
                "trained": predictor.is_trained,
                "feature_count": (
                    len(predictor.feature_columns) if predictor.feature_columns else 0
                ),
                "model_count": len(predictor.models),
            }

        # Training history
        if self.training_history:
            latest_training = max(self.training_history, key=lambda x: x.timestamp)
            status["last_training"] = {
                "timestamp": latest_training.timestamp.isoformat(),
                "validation_score": latest_training.validation_score,
                "status": latest_training.status,
            }

            # Calculate next retrain due
            next_retrain = latest_training.timestamp + timedelta(
                days=self.training_config.auto_retrain_days
            )
            status["next_retrain_due"] = next_retrain.isoformat()

        return status

    async def retrain_if_needed(self) -> bool:
        """Check if retraining is needed and perform it if necessary.

        Returns:
            True if retraining was performed, False otherwise
        """
        if self._should_retrain():
            self.logger.info("Automatic retraining triggered")
            results = await self.train_all_models(force_retrain=True)
            return len(results) > 0
        return False
