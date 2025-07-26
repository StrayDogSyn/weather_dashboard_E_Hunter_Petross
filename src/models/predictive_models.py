"""
Predictive Weather Models for Advanced Forecasting

This module implements machine learning models for weather prediction
including temperature forecasting, weather pattern recognition, and
seasonal trend analysis.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

# For static type checking and type hints
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from sklearn.ensemble import GradientBoostingRegressor as _GradientBoostingRegressor
    from sklearn.ensemble import RandomForestRegressor as _RandomForestRegressor
    from sklearn.linear_model import LinearRegression as _LinearRegression
    from sklearn.metrics import mean_absolute_error as _mean_absolute_error
    from sklearn.metrics import mean_squared_error as _mean_squared_error
    from sklearn.metrics import r2_score as _r2_score
    from sklearn.model_selection import cross_val_score as _cross_val_score
    from sklearn.model_selection import train_test_split as _train_test_split
    from sklearn.preprocessing import LabelEncoder as _LabelEncoder
    from sklearn.preprocessing import StandardScaler as _StandardScaler

import joblib
import numpy as np
import pandas as pd

# ML Libraries
try:
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.model_selection import cross_val_score, train_test_split
    from sklearn.preprocessing import LabelEncoder, StandardScaler

    SKLEARN_AVAILABLE = True
except ImportError:
    GradientBoostingRegressor = None  # type: ignore
    RandomForestRegressor = None  # type: ignore
    LinearRegression = None  # type: ignore
    mean_absolute_error = None  # type: ignore
    mean_squared_error = None  # type: ignore
    r2_score = None  # type: ignore
    cross_val_score = None  # type: ignore
    train_test_split = None  # type: ignore
    LabelEncoder = None  # type: ignore
    StandardScaler = None  # type: ignore
    SKLEARN_AVAILABLE = False
    logging.warning(
        "scikit-learn not available. Install with: pip install scikit-learn"
    )

try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False


class ModelType(Enum):
    """Available predictive model types."""

    LINEAR_REGRESSION = "linear_regression"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    ENSEMBLE = "ensemble"


@dataclass
class PredictionResult:
    """Result of a weather prediction."""

    timestamp: datetime
    predicted_temperature: float
    confidence_interval: Tuple[float, float]
    weather_pattern: str
    prediction_accuracy: float
    features_used: List[str]


@dataclass
class ModelMetrics:
    """Model performance metrics."""

    mae: float  # Mean Absolute Error
    mse: float  # Mean Squared Error
    rmse: float  # Root Mean Squared Error
    r2: float  # R-squared
    cv_score: float  # Cross-validation score


class WeatherPredictor:

    def _check_sklearn(self):
        if not SKLEARN_AVAILABLE:
            raise ImportError(
                "scikit-learn is required for this operation. Please install it with 'pip install scikit-learn'."
            )

    def predict(self, features: List[Dict[str, Any]]) -> List["PredictionResult"]:
        """
        Predict weather outcomes given a list of feature dictionaries.

        Args:
            features: List of feature dictionaries for prediction.

        Returns:
            List of PredictionResult objects.
        """
        raise NotImplementedError("Subclasses must implement the predict method.")

    models: Dict[str, Any]
    scalers: Dict[str, Any]
    encoders: Dict[str, Any]
    feature_columns: List[str]
    target_columns: List[str]
    is_trained: bool
    model_metrics: Dict[str, ModelMetrics]

    def __init__(self, model_type: ModelType = ModelType.ENSEMBLE):
        """Initialize the weather predictor.

        Args:
            model_type: Type of model to use for predictions
        """
        self.model_type = model_type
        self.models = {}
        self.scalers = {}
        self.encoders = {}
        self.feature_columns = []
        self.target_columns = []
        self.is_trained = False
        self.model_metrics = {}

        # Data storage
        self.training_data = pd.DataFrame()
        self.historical_data = pd.DataFrame()
        self._check_sklearn()

        # Model storage path
        self.model_path = Path("data/models")
        self.model_path.mkdir(exist_ok=True)

        self.logger = logging.getLogger(__name__)

    def prepare_features(self, weather_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepare features for model training from weather data.

        Args:
            weather_data: List of weather observations

        Returns:
            DataFrame with engineered features
        """
        if not weather_data:
            return pd.DataFrame()

        df = pd.DataFrame(weather_data)

        # Convert timestamp to datetime if needed
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

        # Time-based features
        df["hour"] = df["timestamp"].dt.hour
        df["day_of_week"] = df["timestamp"].dt.dayofweek
        df["month"] = df["timestamp"].dt.month
        df["season"] = df["month"].apply(self._get_season)

        # Weather features
        if "temperature" in df.columns:
            df["temp_celsius"] = df["temperature"]

        # Lag features (previous weather conditions)
        for lag in [1, 3, 6, 12, 24]:  # hours
            if len(df) > lag:
                df[f"temp_lag_{lag}h"] = df["temp_celsius"].shift(lag)
                if "humidity" in df.columns:
                    df[f"humidity_lag_{lag}h"] = df["humidity"].shift(lag)
                if "pressure" in df.columns:
                    df[f"pressure_lag_{lag}h"] = df["pressure"].shift(lag)

        # Rolling statistics
        for window in [3, 6, 12, 24]:  # hours
            if len(df) >= window:
                df[f"temp_mean_{window}h"] = (
                    df["temp_celsius"].rolling(window=window).mean()
                )
                df[f"temp_std_{window}h"] = (
                    df["temp_celsius"].rolling(window=window).std()
                )
                if "humidity" in df.columns:
                    df[f"humidity_mean_{window}h"] = (
                        df["humidity"].rolling(window=window).mean()
                    )
                if "pressure" in df.columns:
                    df[f"pressure_mean_{window}h"] = (
                        df["pressure"].rolling(window=window).mean()
                    )

        # Weather pattern encoding
        if (
            "description" in df.columns
            and SKLEARN_AVAILABLE
            and LabelEncoder is not None
        ):
            le = LabelEncoder()
            df["weather_pattern_encoded"] = le.fit_transform(df["description"])
            self.encoders["weather_pattern"] = le

        # Geographic features (if location data available)
        if "latitude" in df.columns and "longitude" in df.columns:
            df["lat"] = df["latitude"]
            df["lon"] = df["longitude"]

        # Drop rows with NaN values (from lag/rolling features)
        df = df.dropna()

        return df

    def _get_season(self, month: int) -> str:
        """Get season from month number."""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"

    def train_models(
        self, training_data: pd.DataFrame, target_column: str = "temp_celsius"
    ) -> Dict[str, ModelMetrics]:
        """Train predictive models on historical weather data.

        Args:
            training_data: DataFrame with weather features
            target_column: Column to predict

        Returns:
            Dictionary of model metrics
        """
        if (
            not SKLEARN_AVAILABLE
            or train_test_split is None
            or StandardScaler is None
            or LinearRegression is None
            or RandomForestRegressor is None
            or GradientBoostingRegressor is None
        ):
            raise ImportError("scikit-learn is required for model training.")

        self.training_data = training_data.copy()

        # Select feature columns (exclude timestamp and target)
        exclude_cols = ["timestamp", target_column, "description"]
        self.feature_columns = [
            col for col in training_data.columns if col not in exclude_cols
        ]
        self.target_columns = [target_column]

        X = training_data[self.feature_columns]
        y = training_data[target_column]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )

        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers["features"] = scaler

        # Initialize models
        models = {
            "linear_regression": LinearRegression(),
            "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "gradient_boosting": GradientBoostingRegressor(
                n_estimators=100, random_state=42
            ),
        }

        # Train models and collect metrics
        metrics = {}
        for name, model in models.items():
            if name == "linear_regression":
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

            # Calculate metrics
            if (
                not SKLEARN_AVAILABLE
                or mean_absolute_error is None
                or mean_squared_error is None
                or r2_score is None
                or cross_val_score is None
            ):
                raise ImportError("scikit-learn is required for model evaluation.")
            mae = mean_absolute_error(y_test, y_pred)
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_test, y_pred)

            # Cross-validation score
            if name == "linear_regression":
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            cv_score = cv_scores.mean()

            metrics[name] = ModelMetrics(mae, mse, rmse, r2, cv_score)
            self.models[name] = model

            logging.info(f"{name} - MAE: {mae: .2f}, RMSE: {rmse: .2f}, R²: {r2: .3f}")

        self.model_metrics = metrics
        self.is_trained = True

        # Save models
        self._save_models()

        return metrics

    def predict_temperature(
        self, current_conditions: Dict[str, Any], hours_ahead: int = 24
    ) -> List[PredictionResult]:
        """Predict temperature for specified hours ahead.

        Args:
            current_conditions: Current weather conditions
            hours_ahead: Number of hours to predict ahead

        Returns:
            List of prediction results
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        predictions = []
        base_time = datetime.now()

        for hour in range(1, hours_ahead + 1):
            prediction_time = base_time + timedelta(hours=hour)

            # Create feature vector for this prediction
            features = self._create_prediction_features(
                current_conditions, prediction_time
            )

            # Get predictions from all models
            model_predictions = {}
            for name, model in self.models.items():
                if model is not None:
                    if name == "linear_regression":
                        scaler = self.scalers.get("features")
                        if scaler is not None:
                            features_scaled = scaler.transform([features])
                            pred = model.predict(features_scaled)[0]
                        else:
                            pred = 0.0
                    else:
                        pred = model.predict([features])[0]
                    # Cast numpy types to float
                    try:
                        pred_float = float(pred)
                    except Exception:
                        pred_float = 0.0
                    model_predictions[name] = pred_float
            if not model_predictions:
                # If no models are available, skip this prediction
                continue

            # Ensemble prediction (average of all models)
            if self.model_type == ModelType.ENSEMBLE:
                predicted_temp = float(np.mean(list(model_predictions.values())))
            else:
                predicted_temp = float(
                    model_predictions.get(self.model_type.value, 0.0)
                )

            # Calculate confidence interval (simplified)
            model_std = float(np.std(list(model_predictions.values())))
            confidence_interval = (
                float(predicted_temp - 1.96 * model_std),
                float(predicted_temp + 1.96 * model_std),
            )

            # Determine weather pattern
            weather_pattern = self._predict_weather_pattern(features)

            # Get prediction accuracy based on model performance
            accuracy = float(self._get_prediction_accuracy())

            result = PredictionResult(
                timestamp=prediction_time,
                predicted_temperature=predicted_temp,
                confidence_interval=confidence_interval,
                weather_pattern=weather_pattern,
                prediction_accuracy=accuracy,
                features_used=self.feature_columns,
            )

            predictions.append(result)

        return predictions

    def _create_prediction_features(
        self, conditions: Dict[str, Any], prediction_time: datetime
    ) -> List[float]:
        """Create feature vector for prediction."""
        features = []

        # Time features
        features.extend(
            [
                prediction_time.hour,
                prediction_time.weekday(),
                prediction_time.month,
                self._get_season(prediction_time.month),
            ]
        )

        # Current weather features
        features.append(conditions.get("temperature", 20.0))
        features.append(conditions.get("humidity", 50.0))
        features.append(conditions.get("pressure", 1013.25))

        # Simplified lag features (use current conditions)
        current_temp = conditions.get("temperature", 20.0)
        for _ in range(4):  # lag features
            features.append(current_temp)

        # Rolling statistics (simplified)
        for _ in range(4):  # rolling means
            features.append(current_temp)

        # Weather pattern (encoded)
        if "weather_pattern" in self.encoders:
            pattern = conditions.get("description", "clear")
            try:
                encoded_pattern = self.encoders["weather_pattern"].transform([pattern])[
                    0
                ]
            except ValueError:
                encoded_pattern = 0  # Unknown pattern
            features.append(encoded_pattern)

        # Pad or trim to match expected feature count
        while len(features) < len(self.feature_columns):
            features.append(0.0)

        # Ensure all elements are float and compatible with float()
        from typing import SupportsFloat

        float_features: List[float] = []
        for f in features[: len(self.feature_columns)]:
            if isinstance(f, (int, float, str)):
                try:
                    float_features.append(float(f))
                except Exception:
                    float_features.append(0.0)
            elif isinstance(f, SupportsFloat):
                try:
                    float_features.append(float(f))
                except Exception:
                    float_features.append(0.0)
            else:
                float_features.append(0.0)
        return float_features

    def _predict_weather_pattern(self, features: List[float]) -> str:
        """Predict weather pattern from features."""
        # Simplified pattern prediction
        temp = features[4] if len(features) > 4 else 20.0
        humidity = features[5] if len(features) > 5 else 50.0

        if temp < 0:
            return "snow"
        elif temp < 10 and humidity > 80:
            return "rain"
        elif humidity > 90:
            return "cloudy"
        elif humidity < 30:
            return "clear"
        else:
            return "partly_cloudy"

    def _get_prediction_accuracy(self) -> float:
        """Get overall prediction accuracy based on model performance."""
        if not self.model_metrics:
            return 0.7  # Default accuracy

        # Use R² score as accuracy measure
        r2_scores = [metrics.r2 for metrics in self.model_metrics.values()]
        mean_r2 = float(np.mean(r2_scores))
        return max(0.0, min(1.0, mean_r2))

    def _save_models(self):
        """Save trained models to disk."""
        for name, model in self.models.items():
            model_file = self.model_path / f"{name}_model.joblib"
            joblib.dump(model, model_file)

        # Save scalers and encoders
        for name, scaler in self.scalers.items():
            scaler_file = self.model_path / f"{name}_scaler.joblib"
            joblib.dump(scaler, scaler_file)

        for name, encoder in self.encoders.items():
            encoder_file = self.model_path / f"{name}_encoder.joblib"
            joblib.dump(encoder, encoder_file)

        # Save metadata
        metadata = {
            "model_type": self.model_type.value,
            "feature_columns": self.feature_columns,
            "target_columns": self.target_columns,
            "is_trained": self.is_trained,
            "training_date": datetime.now().isoformat(),
        }

        metadata_file = self.model_path / "model_metadata.joblib"
        joblib.dump(metadata, metadata_file)

        logging.info(f"Models saved to {self.model_path}")

    def load_models(self) -> bool:
        """Load trained models from disk."""
        try:
            # Load metadata
            metadata_file = self.model_path / "model_metadata.joblib"
            if not metadata_file.exists():
                return False

            metadata = joblib.load(metadata_file)
            self.model_type = ModelType(metadata["model_type"])
            self.feature_columns = metadata["feature_columns"]
            self.target_columns = metadata["target_columns"]
            self.is_trained = metadata["is_trained"]

            # Load models
            for model_name in [
                "linear_regression",
                "random_forest",
                "gradient_boosting",
            ]:
                model_file = self.model_path / f"{model_name}_model.joblib"
                if model_file.exists():
                    self.models[model_name] = joblib.load(model_file)

            # Load scalers and encoders
            for scaler_name in ["features"]:
                scaler_file = self.model_path / f"{scaler_name}_scaler.joblib"
                if scaler_file.exists():
                    self.scalers[scaler_name] = joblib.load(scaler_file)

            for encoder_name in ["weather_pattern"]:
                encoder_file = self.model_path / f"{encoder_name}_encoder.joblib"
                if encoder_file.exists():
                    self.encoders[encoder_name] = joblib.load(encoder_file)

            logging.info("Models loaded successfully")
            return True

        except Exception as e:
            logging.error(f"Error loading models: {e}")
            return False

    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """Get feature importance from tree-based models."""
        importance = {}

        for name, model in self.models.items():
            if hasattr(model, "feature_importances_"):
                model_importance = dict(
                    zip(self.feature_columns, model.feature_importances_)
                )
                importance[name] = model_importance

        return importance

    def generate_model_report(self) -> str:
        """Generate a comprehensive model performance report."""
        if not self.model_metrics:
            return "No model metrics available. Train models first."

        report = []
        report.append("=== Weather Prediction Model Report ===\n")

        # Model performance
        report.append("Model Performance Metrics:")
        for name, metrics in self.model_metrics.items():
            report.append(f"\n{name.replace('_', ' ').title()}:")
            report.append(f"  • Mean Absolute Error: {metrics.mae: .2f}°C")
            report.append(f"  • Root Mean Square Error: {metrics.rmse: .2f}°C")
            report.append(f"  • R² Score: {metrics.r2: .3f}")
            report.append(f"  • Cross-validation Score: {metrics.cv_score: .3f}")

        # Feature importance
        importance = self.get_feature_importance()
        if importance:
            report.append("\nTop Important Features:")
            for model_name, features in importance.items():
                if isinstance(features, dict) and features:
                    sorted_features = sorted(
                        features.items(), key=lambda x: x[1], reverse=True
                    )
                    report.append(f"\n{model_name.replace('_', ' ').title()}:")
                    for feature, importance_score in sorted_features[:5]:
                        report.append(f"  • {feature}: {importance_score: .3f}")

        # Training data info
        if not self.training_data.empty:
            report.append(f"\nTraining Data: ")
            report.append(f"  • Total samples: {len(self.training_data)}")
            report.append(f"  • Features used: {len(self.feature_columns)}")
            report.append(
                f"  • Date range: {self.training_data['timestamp'].min()} to {self.training_data['timestamp'].max()}"
            )

        return "\n".join(report)


class WeatherPatternClassifier:
    """Classifier for weather pattern recognition."""

    def __init__(self):
        """Initialize the weather pattern classifier."""
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.is_trained = False

    def train(self, weather_data: pd.DataFrame):
        """Train the weather pattern classifier."""
        if (
            not SKLEARN_AVAILABLE
            or LabelEncoder is None
            or StandardScaler is None
            or RandomForestRegressor is None
        ):
            raise ImportError("scikit-learn is required for classification")

        # Feature preparation
        features = ["temperature", "humidity", "pressure", "hour", "month"]
        X = weather_data[features]
        y = weather_data["description"]

        # Encode labels
        self.label_encoder = LabelEncoder()
        y_encoded = self.label_encoder.fit_transform(y)

        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Train classifier
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y_encoded)

        self.is_trained = True

    def predict_pattern(self, conditions: Dict[str, Any]) -> str:
        """Predict weather pattern from conditions."""
        if (
            not self.is_trained
            or self.scaler is None
            or self.model is None
            or self.label_encoder is None
        ):
            return "unknown"

        # Create feature vector
        features = [
            conditions.get("temperature", 20.0),
            conditions.get("humidity", 50.0),
            conditions.get("pressure", 1013.25),
            datetime.now().hour,
            datetime.now().month,
        ]

        # Scale and predict
        try:
            features_scaled = self.scaler.transform([features])
            prediction = self.model.predict(features_scaled)[0]
        except Exception:
            return "unknown"

        # Decode prediction
        try:
            pattern_index = int(round(prediction))
            if 0 <= pattern_index < len(self.label_encoder.classes_):
                return self.label_encoder.classes_[pattern_index]
            else:
                return "unknown"
        except Exception:
            return "unknown"
