"""
Model Integration Service for Weather Dashboard

This service integrates machine learning prediction models with the existing
weather service and GUI components, providing seamless access to ML-powered
weather predictions throughout the application.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

from ..config import config_manager
from ..interfaces.weather_interfaces import IDataStorage, IWeatherAPI
from ..models.predictive_models import ModelType, PredictionResult, WeatherPredictor
from ..services.model_training_service import ModelTrainingService


@dataclass
class IntegratedForecast:
    """Enhanced forecast combining API data with ML predictions."""

    api_forecast: Dict[str, Any]
    ml_predictions: List[PredictionResult]
    confidence_score: float
    hybrid_forecast: Dict[str, Any]
    timestamp: datetime


@dataclass
class ModelServiceStatus:
    """Status of the integrated model service."""

    models_loaded: bool
    active_models: List[str]
    last_training: Optional[datetime]
    prediction_accuracy: Dict[str, float]
    service_uptime: timedelta


class ModelIntegrationService:
    """Service for integrating ML models with weather dashboard components."""

    def __init__(
        self,
        weather_api: IWeatherAPI,
        data_storage: IDataStorage,
        training_service: ModelTrainingService,
    ):
        """Initialize the model integration service.

        Args:
            weather_api: Weather API service
            data_storage: Data storage service
            training_service: Model training service
        """
        self.weather_api = weather_api
        self.data_storage = data_storage
        self.training_service = training_service
        self.logger = logging.getLogger(__name__)

        # Model predictors
        self.predictors = {}
        self.model_weights = {}  # Weights for ensemble predictions

        # Service status
        self.service_start_time = datetime.now()
        self.models_loaded = False
        self.prediction_cache = {}
        self.cache_ttl = 300  # 5 minutes

        # Load models on initialization
        asyncio.create_task(self._initialize_models())

    async def _initialize_models(self):
        """Initialize and load trained models."""
        try:
            self.logger.info("Initializing ML models for integration")

            # Load predictors from training service
            self.predictors = self.training_service.predictors.copy()

            # Check which models are trained
            trained_models = []
            for model_type, predictor in self.predictors.items():
                if predictor.is_trained:
                    trained_models.append(model_type)

            if not trained_models:
                self.logger.warning("No trained models found, triggering training")
                await self.training_service.train_all_models()

                # Reload after training
                for model_type, predictor in self.training_service.predictors.items():
                    if predictor.is_trained:
                        trained_models.append(model_type)

            # Set model weights based on performance
            await self._calculate_model_weights()

            self.models_loaded = len(trained_models) > 0
            self.logger.info(
                f"Loaded {len(trained_models)} trained models: {trained_models}"
            )

        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")
            self.models_loaded = False

    async def _calculate_model_weights(self):
        """Calculate ensemble weights based on model performance."""
        if not self.training_service.training_history:
            # Default equal weights
            num_models = len([p for p in self.predictors.values() if p.is_trained])
            default_weight = 1.0 / num_models if num_models > 0 else 0.0

            for model_type, predictor in self.predictors.items():
                if predictor.is_trained:
                    self.model_weights[model_type] = default_weight
            return

        # Get latest training results
        latest_training = max(
            self.training_service.training_history, key=lambda x: x.timestamp
        )

        # Calculate weights based on validation scores
        total_score = 0.0
        model_scores = {}

        for model_type, predictor in self.predictors.items():
            if predictor.is_trained and model_type in latest_training.model_metrics:
                # Use average R² from sub-models
                metrics = latest_training.model_metrics[model_type]
                if isinstance(metrics, dict):
                    avg_r2 = sum(m.r2 for m in metrics.values()) / len(metrics)
                else:
                    avg_r2 = metrics.r2

                model_scores[model_type] = max(avg_r2, 0.0)  # Ensure non-negative
                total_score += model_scores[model_type]

        # Normalize to weights
        if total_score > 0:
            for model_type, score in model_scores.items():
                self.model_weights[model_type] = score / total_score

        self.logger.info(f"Model weights calculated: {self.model_weights}")

    async def get_enhanced_forecast(
        self, city: str, days: int = 5, include_ml_predictions: bool = True
    ) -> IntegratedForecast:
        """Get enhanced forecast combining API data with ML predictions.

        Args:
            city: City name
            days: Number of days for forecast
            include_ml_predictions: Whether to include ML predictions

        Returns:
            IntegratedForecast with combined data
        """
        cache_key = f"forecast_{city}_{days}_{include_ml_predictions}"

        # Check cache
        if cache_key in self.prediction_cache:
            cache_entry = self.prediction_cache[cache_key]
            if (datetime.now() - cache_entry["timestamp"]).seconds < self.cache_ttl:
                return cache_entry["forecast"]

        self.logger.info(f"Generating enhanced forecast for {city}, {days} days")

        try:
            # Get API forecast
            api_forecast = self.weather_api.get_forecast(city, days)
            if not api_forecast:
                raise ValueError(f"No API forecast available for {city}")

            # Convert to dict for processing
            api_data = self._forecast_to_dict(api_forecast)

            ml_predictions = []
            confidence_score = 0.5  # Base confidence from API only

            if include_ml_predictions and self.models_loaded:
                # Generate ML predictions
                ml_predictions = await self._generate_ml_predictions(city, days)

                if ml_predictions:
                    # Calculate confidence based on model agreement
                    confidence_score = self._calculate_prediction_confidence(
                        ml_predictions
                    )

            # Create hybrid forecast
            hybrid_forecast = await self._create_hybrid_forecast(
                api_data, ml_predictions
            )

            # Create integrated forecast
            integrated_forecast = IntegratedForecast(
                api_forecast=api_data,
                ml_predictions=ml_predictions,
                confidence_score=confidence_score,
                hybrid_forecast=hybrid_forecast,
                timestamp=datetime.now(),
            )

            # Cache result
            self.prediction_cache[cache_key] = {
                "forecast": integrated_forecast,
                "timestamp": datetime.now(),
            }

            return integrated_forecast

        except Exception as e:
            self.logger.error(f"Error generating enhanced forecast: {e}")
            # Return basic API forecast on error if available
            try:
                api_forecast = self.weather_api.get_forecast(city, days)
                if api_forecast:
                    return IntegratedForecast(
                        api_forecast=self._forecast_to_dict(api_forecast),
                        ml_predictions=[],
                        confidence_score=0.3,
                        hybrid_forecast=self._forecast_to_dict(api_forecast),
                        timestamp=datetime.now(),
                    )
            except Exception:
                pass
            raise

    async def _generate_ml_predictions(
        self, city: str, days: int
    ) -> List[PredictionResult]:
        """Generate ML predictions for a city."""
        predictions = []

        try:
            # Get current weather for feature preparation
            current_weather = self.weather_api.get_current_weather(city)
            if not current_weather:
                return predictions

            # Convert current weather to feature data
            current_data = self._weather_to_dict(current_weather)

            # Generate predictions for each day
            for day_offset in range(days):
                prediction_date = datetime.now() + timedelta(days=day_offset)

                # Modify features for future prediction
                future_features = current_data.copy()
                future_features["timestamp"] = prediction_date.isoformat()

                # Get ensemble predictions from all models
                ensemble_predictions = []
                model_confidences = []

                for model_type, predictor in self.predictors.items():
                    if not predictor.is_trained:
                        continue

                    try:
                        # Generate prediction
                        result = predictor.predict([future_features])
                        if result and len(result) > 0:
                            ensemble_predictions.append(result[0])

                            # Get model weight as confidence
                            weight = self.model_weights.get(model_type, 0.0)
                            model_confidences.append(weight)

                    except Exception as e:
                        self.logger.warning(f"Error in {model_type} prediction: {e}")

                # Create weighted ensemble prediction
                if ensemble_predictions:
                    weighted_prediction = self._create_ensemble_prediction(
                        ensemble_predictions, model_confidences, prediction_date
                    )
                    predictions.append(weighted_prediction)

        except Exception as e:
            self.logger.error(f"Error generating ML predictions: {e}")

        return predictions

    def _create_ensemble_prediction(
        self,
        predictions: List[PredictionResult],
        weights: List[float],
        prediction_date: datetime,
    ) -> PredictionResult:
        """Create ensemble prediction from multiple model results."""
        if not predictions:
            raise ValueError("No predictions provided for ensemble")

        # Normalize weights
        total_weight = sum(weights) if weights else len(predictions)
        if total_weight == 0:
            normalized_weights = [1.0 / len(predictions)] * len(predictions)
        else:
            normalized_weights = (
                [w / total_weight for w in weights]
                if weights
                else [1.0 / len(predictions)] * len(predictions)
            )

        # Weighted average of predictions
        weighted_temp = sum(
            p.predicted_temperature * w for p, w in zip(predictions, normalized_weights)
        )

        # Average confidence (using prediction_accuracy as proxy)
        avg_confidence = sum(
            p.prediction_accuracy * w for p, w in zip(predictions, normalized_weights)
        )

        # Combine confidence intervals
        lower_bounds = [p.confidence_interval[0] for p in predictions]
        upper_bounds = [p.confidence_interval[1] for p in predictions]
        avg_lower = sum(lb * w for lb, w in zip(lower_bounds, normalized_weights))
        avg_upper = sum(ub * w for ub, w in zip(upper_bounds, normalized_weights))

        # Most common weather pattern
        patterns = [p.weather_pattern for p in predictions]
        most_common_pattern = max(set(patterns), key=patterns.count)

        # Combine features used
        all_features = set()
        for pred in predictions:
            all_features.update(pred.features_used)

        return PredictionResult(
            timestamp=prediction_date,
            predicted_temperature=weighted_temp,
            confidence_interval=(avg_lower, avg_upper),
            weather_pattern=most_common_pattern,
            prediction_accuracy=avg_confidence,
            features_used=list(all_features),
        )

    async def _create_hybrid_forecast(
        self, api_data: Dict[str, Any], ml_predictions: List[PredictionResult]
    ) -> Dict[str, Any]:
        """Create hybrid forecast combining API and ML data."""
        hybrid = api_data.copy()

        if not ml_predictions:
            return hybrid

        try:
            # Enhance forecast with ML predictions
            if "forecast_days" in hybrid:
                for i, day_forecast in enumerate(hybrid["forecast_days"]):
                    if i < len(ml_predictions):
                        ml_pred = ml_predictions[i]

                        # Blend API and ML temperatures
                        api_temp = day_forecast.get("temperature", {}).get("max", 0)
                        ml_temp = ml_pred.predicted_temperature

                        # Weight based on confidence
                        ml_weight = ml_pred.prediction_accuracy
                        api_weight = 1.0 - ml_weight

                        blended_temp = api_temp * api_weight + ml_temp * ml_weight

                        # Update forecast with blended prediction
                        if "temperature" not in day_forecast:
                            day_forecast["temperature"] = {}

                        day_forecast["temperature"]["ml_enhanced"] = blended_temp
                        day_forecast["ml_confidence"] = ml_pred.prediction_accuracy
                        day_forecast["prediction_source"] = "hybrid"

                        # Add ML-specific fields
                        day_forecast["ml_pattern"] = ml_pred.weather_pattern
                        day_forecast["confidence_interval"] = (
                            ml_pred.confidence_interval
                        )
                        day_forecast["features_used"] = ml_pred.features_used

        except Exception as e:
            self.logger.error(f"Error creating hybrid forecast: {e}")

        return hybrid

    def _calculate_prediction_confidence(
        self, predictions: List[PredictionResult]
    ) -> float:
        """Calculate overall confidence based on prediction agreement."""
        if not predictions:
            return 0.0

        if len(predictions) == 1:
            return predictions[0].prediction_accuracy

        # Calculate variance in predictions
        temps = [p.predicted_temperature for p in predictions]
        temp_variance = sum((t - sum(temps) / len(temps)) ** 2 for t in temps) / len(
            temps
        )

        # Lower variance = higher confidence
        variance_confidence = max(
            0.0, 1.0 - (temp_variance / 100.0)
        )  # Normalize by expected temp range

        # Average individual confidences
        avg_confidence = sum(p.prediction_accuracy for p in predictions) / len(
            predictions
        )

        # Combine confidences
        return (variance_confidence + avg_confidence) / 2.0

    def _forecast_to_dict(self, forecast) -> Dict[str, Any]:
        """Convert forecast object to dictionary."""
        try:
            if hasattr(forecast, "__dict__"):
                return self._convert_object_to_dict(forecast)
            elif isinstance(forecast, dict):
                return forecast
            else:
                return {"raw_forecast": str(forecast)}
        except Exception as e:
            self.logger.error(f"Error converting forecast to dict: {e}")
            return {"error": "conversion_failed"}

    def _weather_to_dict(self, weather) -> Dict[str, Any]:
        """Convert weather object to dictionary."""
        try:
            if hasattr(weather, "__dict__"):
                return self._convert_object_to_dict(weather)
            elif isinstance(weather, dict):
                return weather
            else:
                return {"raw_weather": str(weather)}
        except Exception as e:
            self.logger.error(f"Error converting weather to dict: {e}")
            return {"error": "conversion_failed"}

    def _convert_object_to_dict(self, obj) -> Any:
        """Recursively convert object to dictionary or appropriate type."""
        if isinstance(obj, dict):
            return {k: self._convert_object_to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, "__dict__"):
            result = {}
            for key, value in obj.__dict__.items():
                if not key.startswith("_"):
                    result[key] = self._convert_object_to_dict(value)
            return result
        elif isinstance(obj, (list, tuple)):
            return [self._convert_object_to_dict(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    async def get_prediction_explanation(self, city: str) -> Dict[str, Any]:
        """Get explanation of how predictions are generated."""
        explanation = {
            "timestamp": datetime.now().isoformat(),
            "city": city,
            "models_used": [],
            "ensemble_method": "weighted_average",
            "feature_sources": [],
            "accuracy_metrics": {},
            "limitations": [],
        }

        # Model information
        for model_type, predictor in self.predictors.items():
            if predictor.is_trained:
                model_info = {
                    "type": model_type,
                    "weight": self.model_weights.get(model_type, 0.0),
                    "features_used": (
                        list(predictor.feature_columns)
                        if predictor.feature_columns
                        else []
                    ),
                    "trained": True,
                }
                explanation["models_used"].append(model_info)

        # Feature sources
        explanation["feature_sources"] = [
            "Current weather conditions",
            "Historical weather patterns",
            "Seasonal trends",
            "Geographic location data",
        ]

        # Accuracy metrics from latest training
        if self.training_service.training_history:
            latest_training = max(
                self.training_service.training_history, key=lambda x: x.timestamp
            )

            for model_type, metrics in latest_training.model_metrics.items():
                if isinstance(metrics, dict):
                    avg_r2 = sum(m.r2 for m in metrics.values()) / len(metrics)
                    avg_mae = sum(m.mae for m in metrics.values()) / len(metrics)
                else:
                    avg_r2 = metrics.r2
                    avg_mae = metrics.mae

                explanation["accuracy_metrics"][model_type] = {
                    "r2_score": round(avg_r2, 3),
                    "mean_absolute_error": round(avg_mae, 2),
                }

        # Limitations
        explanation["limitations"] = [
            "Predictions based on historical patterns may not account for unusual weather events",
            "Accuracy decreases for longer-term forecasts (>3 days)",
            "Local microclimates may not be fully captured",
            "Model performance varies by season and geographic region",
        ]

        return explanation

    def get_service_status(self) -> ModelServiceStatus:
        """Get current service status."""
        uptime = datetime.now() - self.service_start_time

        active_models = []
        prediction_accuracy = {}

        for model_type, predictor in self.predictors.items():
            if predictor.is_trained:
                active_models.append(model_type)

        # Get accuracy from latest training
        if self.training_service.training_history:
            latest_training = max(
                self.training_service.training_history, key=lambda x: x.timestamp
            )

            for model_type, metrics in latest_training.model_metrics.items():
                if isinstance(metrics, dict):
                    avg_r2 = sum(m.r2 for m in metrics.values()) / len(metrics)
                else:
                    avg_r2 = metrics.r2
                prediction_accuracy[model_type] = round(avg_r2, 3)

            last_training = latest_training.timestamp
        else:
            last_training = None

        return ModelServiceStatus(
            models_loaded=self.models_loaded,
            active_models=active_models,
            last_training=last_training,
            prediction_accuracy=prediction_accuracy,
            service_uptime=uptime,
        )

    async def retrain_models_if_needed(self) -> bool:
        """Check and perform model retraining if needed."""
        try:
            retrained = await self.training_service.retrain_if_needed()
            if retrained:
                # Reload models after retraining
                await self._initialize_models()
                self.logger.info("Models retrained and reloaded")
            return retrained
        except Exception as e:
            self.logger.error(f"Error during model retraining: {e}")
            return False

    def clear_prediction_cache(self):
        """Clear the prediction cache."""
        self.prediction_cache.clear()
        self.logger.info("Prediction cache cleared")

    async def validate_integration(self) -> Dict[str, bool]:
        """Validate that all integration components are working."""
        validation_results = {
            "models_loaded": self.models_loaded,
            "weather_api_connected": False,
            "data_storage_accessible": False,
            "training_service_ready": False,
            "predictions_working": False,
        }

        try:
            # Test weather API
            test_weather = self.weather_api.get_current_weather("London")
            validation_results["weather_api_connected"] = test_weather is not None
        except Exception:
            pass

        try:
            # Test data storage
            test_data = self.data_storage.load_data("weather_history.json")
            validation_results["data_storage_accessible"] = True
        except Exception:
            pass

        try:
            # Test training service
            status = self.training_service.get_model_status()
            validation_results["training_service_ready"] = isinstance(status, dict)
        except Exception:
            pass

        try:
            # Test predictions
            if self.models_loaded:
                test_forecast = await self.get_enhanced_forecast("London", days=1)
                validation_results["predictions_working"] = test_forecast is not None
        except Exception:
            pass

        return validation_results
