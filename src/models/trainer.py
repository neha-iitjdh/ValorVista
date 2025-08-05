"""
Model Training Module for ValorVista.
Handles training, hyperparameter tuning, and model evaluation.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List, Any
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import (
    train_test_split, cross_val_score, GridSearchCV, KFold
)
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    mean_absolute_percentage_error
)
import joblib
from pathlib import Path
import logging

from src.preprocessing import DataProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Model training pipeline for house price prediction.
    Uses Gradient Boosting with hyperparameter tuning.
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize trainer with configuration.

        Args:
            config: Model configuration dictionary.
        """
        self.config = config or {}
        self.model = None
        self.processor = DataProcessor()
        self.metrics: Dict[str, float] = {}
        self.feature_importance: Optional[pd.DataFrame] = None

    def train(
        self,
        data_path: Path,
        model_save_path: Path,
        processor_save_path: Path,
        tune_hyperparameters: bool = False
    ) -> Dict[str, float]:
        """
        Train the model on provided data.

        Args:
            data_path: Path to training data CSV.
            model_save_path: Path to save trained model.
            processor_save_path: Path to save fitted processor.
            tune_hyperparameters: Whether to perform GridSearchCV.

        Returns:
            Dictionary of evaluation metrics.
        """
        logger.info(f"Loading training data from {data_path}")
        df = pd.read_csv(data_path)

        # Prepare target variable
        if "SalePrice" not in df.columns:
            raise ValueError("Training data must contain 'SalePrice' column")

        y = np.log1p(df["SalePrice"])  # Log transform target
        X_df = df.drop(columns=["SalePrice", "Id"], errors="ignore")

        # Fit processor and transform data
        logger.info("Fitting data processor and transforming features")
        self.processor.fit(X_df)
        X = self.processor.transform(X_df)

        # Split data
        X_train, X_val, y_train, y_val = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Get model parameters
        if tune_hyperparameters:
            logger.info("Performing hyperparameter tuning...")
            best_params = self._tune_hyperparameters(X_train, y_train)
        else:
            best_params = self._get_default_params()

        # Train final model
        logger.info("Training final model with best parameters")
        self.model = GradientBoostingRegressor(**best_params)
        self.model.fit(X_train, y_train)

        # Evaluate model
        logger.info("Evaluating model performance")
        self.metrics = self._evaluate(X_val, y_val)

        # Calculate feature importance
        self._calculate_feature_importance()

        # Save model and processor
        logger.info(f"Saving model to {model_save_path}")
        joblib.dump(self.model, model_save_path)

        logger.info(f"Saving processor to {processor_save_path}")
        self.processor.save(processor_save_path)

        # Log metrics
        logger.info("Training completed. Metrics:")
        for metric, value in self.metrics.items():
            logger.info(f"  {metric}: {value:.4f}")

        return self.metrics

    def _get_default_params(self) -> Dict[str, Any]:
        """Get default model parameters."""
        return {
            "n_estimators": 500,
            "learning_rate": 0.05,
            "max_depth": 5,
            "min_samples_split": 10,
            "min_samples_leaf": 4,
            "subsample": 0.8,
            "max_features": "sqrt",
            "random_state": 42,
            "validation_fraction": 0.1,
            "n_iter_no_change": 20,
            "tol": 1e-4
        }

    def _tune_hyperparameters(
        self,
        X: np.ndarray,
        y: np.ndarray
    ) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning using GridSearchCV.

        Args:
            X: Training features.
            y: Training target.

        Returns:
            Best parameters dictionary.
        """
        param_grid = {
            "n_estimators": [300, 500],
            "learning_rate": [0.05, 0.1],
            "max_depth": [4, 5, 6],
            "min_samples_split": [5, 10],
            "min_samples_leaf": [2, 4],
            "subsample": [0.8, 0.9],
        }

        base_model = GradientBoostingRegressor(
            random_state=42,
            max_features="sqrt"
        )

        cv = KFold(n_splits=5, shuffle=True, random_state=42)

        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=cv,
            scoring="neg_root_mean_squared_error",
            n_jobs=-1,
            verbose=1
        )

        grid_search.fit(X, y)

        logger.info(f"Best CV Score: {-grid_search.best_score_:.4f}")
        logger.info(f"Best Parameters: {grid_search.best_params_}")

        # Combine with fixed parameters
        best_params = {
            **grid_search.best_params_,
            "random_state": 42,
            "max_features": "sqrt",
            "validation_fraction": 0.1,
            "n_iter_no_change": 20,
            "tol": 1e-4
        }

        return best_params

    def _evaluate(self, X_val: np.ndarray, y_val: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model on validation set.

        Args:
            X_val: Validation features.
            y_val: Validation target (log-transformed).

        Returns:
            Dictionary of metrics.
        """
        # Predictions (in log scale)
        y_pred_log = self.model.predict(X_val)

        # Convert back to original scale
        y_val_orig = np.expm1(y_val)
        y_pred_orig = np.expm1(y_pred_log)

        # Calculate metrics
        rmse = np.sqrt(mean_squared_error(y_val_orig, y_pred_orig))
        mae = mean_absolute_error(y_val_orig, y_pred_orig)
        r2 = r2_score(y_val_orig, y_pred_orig)
        mape = mean_absolute_percentage_error(y_val_orig, y_pred_orig) * 100

        # Cross-validation score
        cv_scores = cross_val_score(
            self.model, X_val, y_val,
            cv=5, scoring="neg_root_mean_squared_error"
        )

        return {
            "rmse": rmse,
            "mae": mae,
            "r2": r2,
            "mape": mape,
            "cv_rmse_mean": -cv_scores.mean(),
            "cv_rmse_std": cv_scores.std()
        }

    def _calculate_feature_importance(self) -> None:
        """Calculate and store feature importance."""
        if self.model is None:
            return

        feature_names = self.processor.get_feature_names()
        importances = self.model.feature_importances_

        # Handle case where feature count differs
        n_features = min(len(feature_names), len(importances))

        self.feature_importance = pd.DataFrame({
            "feature": feature_names[:n_features],
            "importance": importances[:n_features]
        }).sort_values("importance", ascending=False)

    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """
        Get top N most important features.

        Args:
            top_n: Number of top features to return.

        Returns:
            DataFrame with feature names and importance scores.
        """
        if self.feature_importance is None:
            return pd.DataFrame()
        return self.feature_importance.head(top_n)

    def cross_validate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_splits: int = 5
    ) -> Dict[str, float]:
        """
        Perform cross-validation.

        Args:
            X: Features array.
            y: Target array.
            n_splits: Number of CV folds.

        Returns:
            Cross-validation results.
        """
        cv = KFold(n_splits=n_splits, shuffle=True, random_state=42)

        scores = {
            "rmse": [],
            "mae": [],
            "r2": []
        }

        for train_idx, val_idx in cv.split(X):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]

            model = GradientBoostingRegressor(**self._get_default_params())
            model.fit(X_train, y_train)

            y_pred = model.predict(X_val)
            y_val_orig = np.expm1(y_val)
            y_pred_orig = np.expm1(y_pred)

            scores["rmse"].append(np.sqrt(mean_squared_error(y_val_orig, y_pred_orig)))
            scores["mae"].append(mean_absolute_error(y_val_orig, y_pred_orig))
            scores["r2"].append(r2_score(y_val_orig, y_pred_orig))

        return {
            f"cv_{metric}_mean": np.mean(values)
            for metric, values in scores.items()
        }
