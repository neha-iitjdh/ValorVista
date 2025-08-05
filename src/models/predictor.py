"""
Prediction Module for ValorVista.
Handles model loading and inference with uncertainty estimation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import joblib
import logging

from src.preprocessing import DataProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HousePricePredictor:
    """
    House price prediction class with uncertainty estimation.
    Loads trained model and provides prediction interface.
    """

    def __init__(
        self,
        model_path: Optional[Path] = None,
        processor_path: Optional[Path] = None
    ):
        """
        Initialize predictor with model and processor paths.

        Args:
            model_path: Path to saved model file.
            processor_path: Path to saved processor file.
        """
        self.model = None
        self.processor = DataProcessor()
        self.model_loaded = False

        if model_path and processor_path:
            self.load(model_path, processor_path)

    def load(self, model_path: Path, processor_path: Path) -> None:
        """
        Load model and processor from disk.

        Args:
            model_path: Path to saved model.
            processor_path: Path to saved processor.
        """
        try:
            logger.info(f"Loading model from {model_path}")
            self.model = joblib.load(model_path)

            logger.info(f"Loading processor from {processor_path}")
            self.processor.load(processor_path)

            self.model_loaded = True
            logger.info("Model and processor loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def predict(
        self,
        data: Union[Dict[str, Any], pd.DataFrame],
        return_interval: bool = True,
        confidence: float = 0.95
    ) -> Dict[str, Any]:
        """
        Make prediction for single property or batch.

        Args:
            data: Property features as dict or DataFrame.
            return_interval: Whether to return prediction intervals.
            confidence: Confidence level for intervals.

        Returns:
            Dictionary with predictions and optional intervals.
        """
        if not self.model_loaded:
            raise ValueError("Model not loaded. Call load() first.")

        # Convert dict to DataFrame if needed
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        else:
            df = data.copy()

        # Transform features
        X = self.processor.transform(df)

        # Make predictions (model predicts in log scale)
        log_predictions = self.model.predict(X)

        # Convert back to original scale
        predictions = np.expm1(log_predictions)

        result = {
            "predictions": predictions.tolist(),
            "formatted_predictions": [
                f"${p:,.0f}" for p in predictions
            ]
        }

        if return_interval:
            intervals = self._calculate_prediction_intervals(
                X, log_predictions, confidence
            )
            result["prediction_intervals"] = intervals
            result["confidence_level"] = confidence

        return result

    def _calculate_prediction_intervals(
        self,
        X: np.ndarray,
        log_predictions: np.ndarray,
        confidence: float = 0.95
    ) -> List[Dict[str, float]]:
        """
        Calculate prediction intervals using model variance estimation.

        Uses staged predictions to estimate variance across trees.

        Args:
            X: Transformed features.
            log_predictions: Log-scale predictions.
            confidence: Confidence level.

        Returns:
            List of interval dictionaries.
        """
        intervals = []

        # Use staged predictions to estimate uncertainty
        staged_preds = np.array(list(self.model.staged_predict(X)))

        for i in range(X.shape[0]):
            # Get predictions at each stage for this sample
            sample_staged = staged_preds[:, i]

            # Calculate variance from staged predictions
            # Use last 50% of stages for stability
            n_stages = len(sample_staged)
            stable_preds = sample_staged[n_stages // 2:]
            pred_std = np.std(stable_preds)

            # Add base uncertainty (model can't be more precise than ~5%)
            base_uncertainty = 0.05 * np.abs(log_predictions[i])
            total_std = np.sqrt(pred_std ** 2 + base_uncertainty ** 2)

            # Calculate z-score for confidence level
            from scipy import stats
            z = stats.norm.ppf((1 + confidence) / 2)

            # Calculate intervals in log scale
            lower_log = log_predictions[i] - z * total_std
            upper_log = log_predictions[i] + z * total_std

            # Convert to original scale
            lower = np.expm1(lower_log)
            upper = np.expm1(upper_log)
            point_estimate = np.expm1(log_predictions[i])

            intervals.append({
                "lower": float(lower),
                "upper": float(upper),
                "point_estimate": float(point_estimate),
                "formatted": {
                    "lower": f"${lower:,.0f}",
                    "upper": f"${upper:,.0f}",
                    "point_estimate": f"${point_estimate:,.0f}"
                }
            })

        return intervals

    def predict_batch(
        self,
        data: List[Dict[str, Any]],
        return_interval: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Make predictions for multiple properties.

        Args:
            data: List of property feature dictionaries.
            return_interval: Whether to return prediction intervals.

        Returns:
            List of prediction results.
        """
        df = pd.DataFrame(data)
        result = self.predict(df, return_interval=return_interval)

        # Format as list of individual results
        batch_results = []
        for i in range(len(data)):
            item_result = {
                "input": data[i],
                "prediction": result["predictions"][i],
                "formatted_prediction": result["formatted_predictions"][i]
            }
            if return_interval and "prediction_intervals" in result:
                item_result["interval"] = result["prediction_intervals"][i]
            batch_results.append(item_result)

        return batch_results

    def get_feature_importance(self, top_n: int = 20) -> List[Dict[str, Any]]:
        """
        Get feature importance from the model.

        Args:
            top_n: Number of top features to return.

        Returns:
            List of feature importance dictionaries.
        """
        if not self.model_loaded:
            raise ValueError("Model not loaded.")

        feature_names = self.processor.get_feature_names()
        importances = self.model.feature_importances_

        n_features = min(len(feature_names), len(importances))

        importance_list = [
            {"feature": feature_names[i], "importance": float(importances[i])}
            for i in range(n_features)
        ]

        # Sort by importance
        importance_list.sort(key=lambda x: x["importance"], reverse=True)

        return importance_list[:top_n]

    def explain_prediction(
        self,
        data: Dict[str, Any],
        top_factors: int = 10
    ) -> Dict[str, Any]:
        """
        Provide explanation for a single prediction.

        Args:
            data: Property features.
            top_factors: Number of top factors to show.

        Returns:
            Dictionary with prediction and explanation.
        """
        prediction = self.predict(data)

        # Get feature importance
        importance = self.get_feature_importance(top_factors)

        # Identify key factors from input
        key_factors = []
        for feat in importance:
            feature_name = feat["feature"]
            if feature_name in data:
                key_factors.append({
                    "feature": feature_name,
                    "value": data[feature_name],
                    "importance": feat["importance"]
                })

        return {
            "prediction": prediction["predictions"][0],
            "formatted_prediction": prediction["formatted_predictions"][0],
            "interval": prediction.get("prediction_intervals", [{}])[0],
            "key_factors": key_factors,
            "explanation": self._generate_explanation(data, key_factors)
        }

    def _generate_explanation(
        self,
        data: Dict[str, Any],
        key_factors: List[Dict]
    ) -> str:
        """Generate human-readable explanation."""
        lines = ["Key factors influencing this valuation:"]

        for factor in key_factors[:5]:
            name = factor["feature"]
            value = factor["value"]
            importance = factor["importance"] * 100

            # Format based on feature type
            if name in ["GrLivArea", "TotalBsmtSF", "1stFlrSF", "2ndFlrSF"]:
                lines.append(f"- {name}: {value:,} sq ft ({importance:.1f}% importance)")
            elif name in ["OverallQual", "OverallCond"]:
                lines.append(f"- {name}: {value}/10 ({importance:.1f}% importance)")
            elif "Year" in name:
                lines.append(f"- {name}: {value} ({importance:.1f}% importance)")
            else:
                lines.append(f"- {name}: {value} ({importance:.1f}% importance)")

        return "\n".join(lines)
