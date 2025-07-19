"""
Unified Machine Learning Model Service for Weather Dashboard.

This service consolidates model training, integration, and prediction functionality
into a single, cohesive service following best practices.
"""

import logging
import os
import pickle
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

from ..models.weather_models import CurrentWeather


class ModelType(Enum):
    """Available machine learning model types."""
    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"


class PredictionTarget(Enum):
    """Prediction target types."""
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    PRESSURE = "pressure"


class ConfidenceLevel(Enum):
    """Prediction confidence levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class ModelInfo:
    """Information about a trained model."""
    model_type: ModelType
    target: PredictionTarget
    accuracy: float
    trained_date: datetime
    feature_importance: Dict[str, float]
    file_path: str


@dataclass
class SimpleModelMetrics:
    """Simple model performance metrics."""
    mae: float  # Mean Absolute Error
    mse: float  # Mean Squared Error
    rmse: float  # Root Mean Squared Error
    r2: float  # R-squared
    cv_score: float  # Cross-validation score


@dataclass
class WeatherPrediction:
    """Weather prediction result."""
    predicted_temperature: Optional[float]
    predicted_humidity: Optional[float]
    prediction_time: datetime
    confidence: ConfidenceLevel
    model_used: str
    created_at: datetime


class UnifiedModelService:
    """Unified service for all machine learning model operations."""

    def __init__(self):
        """Initialize the unified model service."""
        self.logger = logging.getLogger(__name__)
        self.models_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models')
        self.trained_models: Dict[str, ModelInfo] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Create models directory if it doesn't exist
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Load existing models
        self._load_existing_models()

    def _load_existing_models(self):
        """Load previously trained models from disk."""
        try:
            model_files = [f for f in os.listdir(self.models_dir) if f.endswith('.pkl')]
            for model_file in model_files:
                try:
                    model_info = self._load_model_info(model_file)
                    if model_info:
                        key = f"{model_info.target.value}_{model_info.model_type.value}"
                        self.trained_models[key] = model_info
                        self.logger.info(f"Loaded model: {key}")
                except Exception as e:
                    self.logger.warning(f"Failed to load model {model_file}: {e}")
        except Exception as e:
            self.logger.warning(f"Error loading models directory: {e}")

    def _load_model_info(self, filename: str) -> Optional[ModelInfo]:
        """Load model information from a file."""
        try:
            filepath = os.path.join(self.models_dir, filename)
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            return ModelInfo(
                model_type=ModelType(model_data['model_type']),
                target=PredictionTarget(model_data['target']),
                accuracy=model_data['accuracy'],
                trained_date=model_data['trained_date'],
                feature_importance=model_data['feature_importance'],
                file_path=filepath
            )
        except Exception as e:
            self.logger.error(f"Error loading model info from {filename}: {e}")
            return None

    def train_models(self, weather_data: pd.DataFrame) -> Dict[str, SimpleModelMetrics]:
        """
        Train machine learning models on weather data.

        Args:
            weather_data: DataFrame containing weather data

        Returns:
            Dictionary of model metrics
        """
        results = {}
        
        if weather_data.empty or len(weather_data) < 10:
            self.logger.warning("Insufficient data for model training")
            return results

        try:
            # Prepare data
            X, y_temp, y_humidity = self._prepare_training_data(weather_data)
            
            if X.empty:
                self.logger.warning("No valid features for training")
                return results

            # Train temperature models
            for model_type in ModelType:
                temp_metrics = self._train_single_model(
                    X, y_temp, model_type, PredictionTarget.TEMPERATURE
                )
                if temp_metrics:
                    results[f"temperature_{model_type.value}"] = temp_metrics

                # Train humidity models
                humidity_metrics = self._train_single_model(
                    X, y_humidity, model_type, PredictionTarget.HUMIDITY
                )
                if humidity_metrics:
                    results[f"humidity_{model_type.value}"] = humidity_metrics

            self.logger.info(f"Successfully trained {len(results)} models")
            return results

        except Exception as e:
            self.logger.error(f"Error during model training: {e}")
            return results

    def _prepare_training_data(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
        """Prepare data for model training."""
        try:
            # Create features
            features = pd.DataFrame()
            
            # Time-based features
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                features['hour'] = data['timestamp'].dt.hour
                features['month'] = data['timestamp'].dt.month
                features['day_of_year'] = data['timestamp'].dt.dayofyear
            
            # Weather features
            if 'temperature' in data.columns:
                features['temperature'] = pd.to_numeric(data['temperature'], errors='coerce')
            if 'humidity' in data.columns:
                features['humidity'] = pd.to_numeric(data['humidity'], errors='coerce')
            if 'pressure' in data.columns:
                features['pressure'] = pd.to_numeric(data['pressure'], errors='coerce')
            if 'wind_speed' in data.columns:
                features['wind_speed'] = pd.to_numeric(data['wind_speed'], errors='coerce')

            # Create lag features for time series
            if 'temperature' in features.columns:
                features['temp_lag1'] = features['temperature'].shift(1)
                features['temp_lag2'] = features['temperature'].shift(2)
            
            # Drop rows with NaN values
            features = features.dropna()
            
            # Targets
            y_temp = features['temperature'] if 'temperature' in features.columns else pd.Series()
            y_humidity = features['humidity'] if 'humidity' in features.columns else pd.Series()
            
            # Remove targets from features
            X = features.drop(['temperature', 'humidity'], axis=1, errors='ignore')
            
            return X, y_temp, y_humidity

        except Exception as e:
            self.logger.error(f"Error preparing training data: {e}")
            return pd.DataFrame(), pd.Series(), pd.Series()

    def _train_single_model(self, X: pd.DataFrame, y: pd.Series, 
                          model_type: ModelType, target: PredictionTarget) -> Optional[SimpleModelMetrics]:
        """Train a single model."""
        try:
            if X.empty or y.empty or len(X) != len(y):
                return None

            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            # Create and train model
            model = self._create_model(model_type)
            model.fit(X_train_scaled, y_train)

            # Make predictions
            y_pred = model.predict(X_test_scaled)

            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)

            # Get feature importance
            feature_importance = {}
            if hasattr(model, 'feature_importances_'):
                for i, importance in enumerate(model.feature_importances_):
                    feature_importance[X.columns[i]] = float(importance)
            else:
                # For linear regression, use coefficient magnitude
                if hasattr(model, 'coef_'):
                    for i, coef in enumerate(model.coef_):
                        feature_importance[X.columns[i]] = float(abs(coef))

            # Save model
            model_key = f"{target.value}_{model_type.value}"
            model_path = os.path.join(self.models_dir, f"{model_key}.pkl")
            
            model_data = {
                'model': model,
                'scaler': scaler,
                'model_type': model_type.value,
                'target': target.value,
                'accuracy': r2,
                'mae': mae,
                'trained_date': datetime.now(),
                'feature_importance': feature_importance,
                'features': list(X.columns)
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)

            # Store model info
            self.trained_models[model_key] = ModelInfo(
                model_type=model_type,
                target=target,
                accuracy=r2,
                trained_date=datetime.now(),
                feature_importance=feature_importance,
                file_path=model_path
            )
            
            self.scalers[model_key] = scaler

            # Create metrics
            metrics = SimpleModelMetrics(
                mae=mae,
                mse=mse,
                rmse=rmse,
                r2=r2,
                cv_score=0.0  # Could add cross-validation later
            )

            self.logger.info(f"Trained {model_key} with R² = {r2:.3f}, MAE = {mae:.3f}")
            return metrics

        except Exception as e:
            self.logger.error(f"Error training {model_type.value} for {target.value}: {e}")
            return None

    def _create_model(self, model_type: ModelType):
        """Create a model instance based on type."""
        if model_type == ModelType.LINEAR_REGRESSION:
            return LinearRegression()
        elif model_type == ModelType.RANDOM_FOREST:
            return RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == ModelType.GRADIENT_BOOSTING:
            return GradientBoostingRegressor(n_estimators=100, random_state=42)
        else:
            raise ValueError(f"Unknown model type: {model_type}")

    def predict_weather(self, current_weather: CurrentWeather, 
                       hours_ahead: int = 24) -> Optional[WeatherPrediction]:
        """
        Predict future weather conditions.

        Args:
            current_weather: Current weather data
            hours_ahead: Hours into the future to predict

        Returns:
            WeatherPrediction object or None if prediction failed
        """
        try:
            # Use the best available models for prediction
            temp_model_key = self._get_best_model(PredictionTarget.TEMPERATURE)
            humidity_model_key = self._get_best_model(PredictionTarget.HUMIDITY)

            predictions = {}
            confidence = ConfidenceLevel.LOW

            # Predict temperature
            if temp_model_key:
                temp_pred, temp_conf = self._make_prediction(
                    temp_model_key, current_weather, hours_ahead
                )
                if temp_pred is not None:
                    predictions['temperature'] = temp_pred
                    confidence = max(confidence, temp_conf)

            # Predict humidity  
            if humidity_model_key:
                humidity_pred, humidity_conf = self._make_prediction(
                    humidity_model_key, current_weather, hours_ahead
                )
                if humidity_pred is not None:
                    predictions['humidity'] = humidity_pred
                    confidence = max(confidence, humidity_conf)

            if not predictions:
                return None

            # Create prediction object
            prediction_time = datetime.now() + timedelta(hours=hours_ahead)
            
            return WeatherPrediction(
                predicted_temperature=predictions.get('temperature'),
                predicted_humidity=predictions.get('humidity'),
                prediction_time=prediction_time,
                confidence=confidence,
                model_used=f"{temp_model_key or 'None'}, {humidity_model_key or 'None'}",
                created_at=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Error making weather prediction: {e}")
            return None

    def _get_best_model(self, target: PredictionTarget) -> Optional[str]:
        """Get the best model for a given target."""
        best_model = None
        best_accuracy = -1

        for key, model_info in self.trained_models.items():
            if model_info.target == target and model_info.accuracy > best_accuracy:
                best_accuracy = model_info.accuracy
                best_model = key

        return best_model

    def _make_prediction(self, model_key: str, current_weather: CurrentWeather, 
                        hours_ahead: int) -> Tuple[Optional[float], PredictionConfidence]:
        """Make a prediction using a specific model."""
        try:
            model_path = self.trained_models[model_key].file_path
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)

            model = model_data['model']
            scaler = model_data['scaler']
            features = model_data['features']

            # Create feature vector
            feature_values = self._extract_features(current_weather, hours_ahead, features)
            if feature_values is None:
                return None, PredictionConfidence.LOW

            # Scale and predict
            feature_scaled = scaler.transform([feature_values])
            prediction = model.predict(feature_scaled)[0]

            # Determine confidence based on model accuracy
            accuracy = self.trained_models[model_key].accuracy
            if accuracy > 0.8:
                confidence = PredictionConfidence.HIGH
            elif accuracy > 0.6:
                confidence = PredictionConfidence.MEDIUM
            else:
                confidence = PredictionConfidence.LOW

            return float(prediction), confidence

        except Exception as e:
            self.logger.error(f"Error making prediction with {model_key}: {e}")
            return None, PredictionConfidence.LOW

    def _extract_features(self, weather: CurrentWeather, hours_ahead: int, 
                         required_features: List[str]) -> Optional[List[float]]:
        """Extract features from current weather for prediction."""
        try:
            future_time = datetime.now() + timedelta(hours=hours_ahead)
            features = []

            for feature in required_features:
                if feature == 'hour':
                    features.append(future_time.hour)
                elif feature == 'month':
                    features.append(future_time.month)
                elif feature == 'day_of_year':
                    features.append(future_time.timetuple().tm_yday)
                elif feature == 'temperature':
                    features.append(weather.temperature.to_celsius())
                elif feature == 'humidity':
                    features.append(weather.humidity)
                elif feature == 'pressure':
                    features.append(weather.pressure.value)
                elif feature == 'wind_speed':
                    features.append(weather.wind.speed)
                elif feature.startswith('temp_lag'):
                    # For lag features, use current temperature as approximation
                    features.append(weather.temperature.to_celsius())
                else:
                    # Default value for unknown features
                    features.append(0.0)

            return features

        except Exception as e:
            self.logger.error(f"Error extracting features: {e}")
            return None

    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all trained models."""
        status = {
            "total_models": len(self.trained_models),
            "models": {},
            "last_updated": datetime.now().isoformat()
        }

        for key, model_info in self.trained_models.items():
            status["models"][key] = {
                "type": model_info.model_type.value,
                "target": model_info.target.value,
                "accuracy": model_info.accuracy,
                "trained_date": model_info.trained_date.isoformat(),
                "top_features": dict(list(sorted(
                    model_info.feature_importance.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                ))[:5])
            }

        return status

    def cleanup_old_models(self, max_age_days: int = 30):
        """Remove models older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            models_to_remove = []

            for key, model_info in self.trained_models.items():
                if model_info.trained_date < cutoff_date:
                    models_to_remove.append(key)

            for key in models_to_remove:
                model_info = self.trained_models[key]
                try:
                    os.remove(model_info.file_path)
                    del self.trained_models[key]
                    if key in self.scalers:
                        del self.scalers[key]
                    self.logger.info(f"Removed old model: {key}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove model {key}: {e}")

        except Exception as e:
            self.logger.error(f"Error during model cleanup: {e}")
