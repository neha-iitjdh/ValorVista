"""
Data Processing Module for ValorVista.
Handles data cleaning, imputation, encoding, and scaling.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
from pathlib import Path

from .feature_engineer import FeatureEngineer


class DataProcessor:
    """
    Complete data processing pipeline for house price prediction.
    Handles missing values, encoding, scaling, and feature engineering.
    """

    # Columns expected from the Kaggle dataset
    NUMERIC_FEATURES = [
        "LotFrontage", "LotArea", "OverallQual", "OverallCond",
        "YearBuilt", "YearRemodAdd", "MasVnrArea", "BsmtFinSF1",
        "BsmtFinSF2", "BsmtUnfSF", "TotalBsmtSF", "1stFlrSF",
        "2ndFlrSF", "LowQualFinSF", "GrLivArea", "BsmtFullBath",
        "BsmtHalfBath", "FullBath", "HalfBath", "BedroomAbvGr",
        "KitchenAbvGr", "TotRmsAbvGrd", "Fireplaces", "GarageYrBlt",
        "GarageCars", "GarageArea", "WoodDeckSF", "OpenPorchSF",
        "EnclosedPorch", "3SsnPorch", "ScreenPorch", "PoolArea",
        "MiscVal", "MoSold", "YrSold"
    ]

    CATEGORICAL_FEATURES = [
        "MSSubClass", "MSZoning", "Street", "Alley", "LotShape",
        "LandContour", "Utilities", "LotConfig", "LandSlope",
        "Neighborhood", "Condition1", "Condition2", "BldgType",
        "HouseStyle", "RoofStyle", "RoofMatl", "Exterior1st",
        "Exterior2nd", "MasVnrType", "ExterQual", "ExterCond",
        "Foundation", "BsmtQual", "BsmtCond", "BsmtExposure",
        "BsmtFinType1", "BsmtFinType2", "Heating", "HeatingQC",
        "CentralAir", "Electrical", "KitchenQual", "Functional",
        "FireplaceQu", "GarageType", "GarageFinish", "GarageQual",
        "GarageCond", "PavedDrive", "PoolQC", "Fence", "MiscFeature",
        "SaleType", "SaleCondition"
    ]

    # Quality mappings for ordinal encoding
    QUALITY_MAPPING = {
        "Ex": 5, "Gd": 4, "TA": 3, "Fa": 2, "Po": 1, "NA": 0, np.nan: 0
    }

    BASEMENT_EXPOSURE_MAPPING = {
        "Gd": 4, "Av": 3, "Mn": 2, "No": 1, "NA": 0, np.nan: 0
    }

    BASEMENT_FINISH_MAPPING = {
        "GLQ": 6, "ALQ": 5, "BLQ": 4, "Rec": 3, "LwQ": 2, "Unf": 1, "NA": 0, np.nan: 0
    }

    GARAGE_FINISH_MAPPING = {
        "Fin": 3, "RFn": 2, "Unf": 1, "NA": 0, np.nan: 0
    }

    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.numeric_imputer = SimpleImputer(strategy="median")
        self.categorical_imputer = SimpleImputer(strategy="constant", fill_value="None")
        self.scaler = StandardScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: List[str] = []
        self.is_fitted = False

    def fit(self, df: pd.DataFrame, target_col: str = "SalePrice") -> "DataProcessor":
        """
        Fit the processor on training data.

        Args:
            df: Training DataFrame.
            target_col: Name of target column.

        Returns:
            Self for method chaining.
        """
        df = df.copy()

        # Separate target if present
        if target_col in df.columns:
            df = df.drop(columns=[target_col])

        # Apply feature engineering
        df = self.feature_engineer.create_all_features(df)

        # Get available numeric and categorical columns
        numeric_cols = [c for c in self.NUMERIC_FEATURES if c in df.columns]
        categorical_cols = [c for c in self.CATEGORICAL_FEATURES if c in df.columns]

        # Add engineered features to numeric columns
        engineered_features = self.feature_engineer.get_created_features()
        numeric_cols.extend([f for f in engineered_features if f in df.columns])
        numeric_cols = list(set(numeric_cols))

        # Fit numeric imputer and scaler
        if numeric_cols:
            numeric_data = df[numeric_cols].copy()
            numeric_data = self._apply_ordinal_encoding(numeric_data)
            self.numeric_imputer.fit(numeric_data)
            imputed_numeric = self.numeric_imputer.transform(numeric_data)
            self.scaler.fit(imputed_numeric)

        # Fit label encoders for categorical columns
        for col in categorical_cols:
            if col in df.columns:
                le = LabelEncoder()
                # Handle missing values before fitting
                values = df[col].fillna("None").astype(str)
                le.fit(values)
                self.label_encoders[col] = le

        # Store feature names
        self.feature_names = numeric_cols + categorical_cols
        self.is_fitted = True

        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        """
        Transform data using fitted processor.

        Args:
            df: DataFrame to transform.

        Returns:
            Transformed numpy array.
        """
        if not self.is_fitted:
            raise ValueError("Processor must be fitted before transform.")

        df = df.copy()

        # Apply feature engineering
        df = self.feature_engineer.create_all_features(df)

        # Get columns
        numeric_cols = [c for c in self.NUMERIC_FEATURES if c in df.columns]
        engineered_features = self.feature_engineer.get_created_features()
        numeric_cols.extend([f for f in engineered_features if f in df.columns])
        numeric_cols = list(set(numeric_cols))
        categorical_cols = [c for c in self.CATEGORICAL_FEATURES if c in df.columns]

        result_parts = []

        # Process numeric columns
        if numeric_cols:
            numeric_data = df[numeric_cols].copy()
            numeric_data = self._apply_ordinal_encoding(numeric_data)

            # Handle missing columns
            for col in numeric_cols:
                if col not in numeric_data.columns:
                    numeric_data[col] = 0

            imputed_numeric = self.numeric_imputer.transform(numeric_data)
            scaled_numeric = self.scaler.transform(imputed_numeric)
            result_parts.append(scaled_numeric)

        # Process categorical columns
        if categorical_cols:
            categorical_data = []
            for col in categorical_cols:
                if col in df.columns:
                    values = df[col].fillna("None").astype(str)
                    # Handle unseen categories
                    le = self.label_encoders.get(col)
                    if le:
                        encoded = []
                        for v in values:
                            if v in le.classes_:
                                encoded.append(le.transform([v])[0])
                            else:
                                encoded.append(0)  # Default for unseen categories
                        categorical_data.append(encoded)
                else:
                    categorical_data.append([0] * len(df))

            if categorical_data:
                result_parts.append(np.array(categorical_data).T)

        if result_parts:
            return np.hstack(result_parts)
        return np.array([])

    def fit_transform(self, df: pd.DataFrame, target_col: str = "SalePrice") -> np.ndarray:
        """Fit and transform in one step."""
        self.fit(df, target_col)
        return self.transform(df)

    def _apply_ordinal_encoding(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply ordinal encoding to quality-related columns."""
        df = df.copy()

        # Quality columns
        quality_cols = ["ExterQual", "ExterCond", "BsmtQual", "BsmtCond",
                        "HeatingQC", "KitchenQual", "FireplaceQu",
                        "GarageQual", "GarageCond", "PoolQC"]

        for col in quality_cols:
            if col in df.columns:
                df[col] = df[col].map(self.QUALITY_MAPPING).fillna(0)

        # Basement exposure
        if "BsmtExposure" in df.columns:
            df["BsmtExposure"] = df["BsmtExposure"].map(
                self.BASEMENT_EXPOSURE_MAPPING
            ).fillna(0)

        # Basement finish type
        for col in ["BsmtFinType1", "BsmtFinType2"]:
            if col in df.columns:
                df[col] = df[col].map(self.BASEMENT_FINISH_MAPPING).fillna(0)

        # Garage finish
        if "GarageFinish" in df.columns:
            df["GarageFinish"] = df["GarageFinish"].map(
                self.GARAGE_FINISH_MAPPING
            ).fillna(0)

        return df

    def save(self, path: Path) -> None:
        """Save processor to disk."""
        joblib.dump({
            "numeric_imputer": self.numeric_imputer,
            "categorical_imputer": self.categorical_imputer,
            "scaler": self.scaler,
            "label_encoders": self.label_encoders,
            "feature_names": self.feature_names,
            "is_fitted": self.is_fitted
        }, path)

    def load(self, path: Path) -> "DataProcessor":
        """Load processor from disk."""
        data = joblib.load(path)
        self.numeric_imputer = data["numeric_imputer"]
        self.categorical_imputer = data["categorical_imputer"]
        self.scaler = data["scaler"]
        self.label_encoders = data["label_encoders"]
        self.feature_names = data["feature_names"]
        self.is_fitted = data["is_fitted"]
        return self

    def get_feature_names(self) -> List[str]:
        """Return list of feature names after transformation."""
        return self.feature_names


def prepare_input_data(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Prepare input data from API request for prediction.

    Args:
        data: Dictionary containing property features.

    Returns:
        DataFrame ready for preprocessing.
    """
    # Create DataFrame from input
    df = pd.DataFrame([data])

    # Ensure proper data types
    for col in DataProcessor.NUMERIC_FEATURES:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
