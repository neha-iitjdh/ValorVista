"""
Feature Engineering Module for ValorVista.
Handles creation of derived features and domain-specific transformations.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple, Optional


class FeatureEngineer:
    """
    Feature engineering class for house price prediction.
    Creates domain-specific features to improve model performance.
    """

    def __init__(self):
        self.created_features: List[str] = []

    def create_all_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering transformations.

        Args:
            df: Input DataFrame with raw features.

        Returns:
            DataFrame with engineered features.
        """
        df = df.copy()

        # Apply all feature engineering steps
        df = self._create_age_features(df)
        df = self._create_area_features(df)
        df = self._create_quality_features(df)
        df = self._create_bathroom_features(df)
        df = self._create_garage_features(df)
        df = self._create_basement_features(df)
        df = self._create_porch_features(df)
        df = self._create_interaction_features(df)
        df = self._create_binary_features(df)

        return df

    def _create_age_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create age-related features."""
        current_year = 2024

        if "YearBuilt" in df.columns:
            df["HouseAge"] = current_year - df["YearBuilt"]
            self.created_features.append("HouseAge")

        if "YearRemodAdd" in df.columns:
            df["RemodAge"] = current_year - df["YearRemodAdd"]
            self.created_features.append("RemodAge")

        if "YearBuilt" in df.columns and "YearRemodAdd" in df.columns:
            df["YearsSinceRemod"] = df["YearRemodAdd"] - df["YearBuilt"]
            df["IsRemodeled"] = (df["YearRemodAdd"] != df["YearBuilt"]).astype(int)
            self.created_features.extend(["YearsSinceRemod", "IsRemodeled"])

        if "GarageYrBlt" in df.columns:
            df["GarageAge"] = current_year - df["GarageYrBlt"].fillna(current_year)
            self.created_features.append("GarageAge")

        return df

    def _create_area_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create area-related features."""
        # Total square footage
        sf_cols = ["TotalBsmtSF", "1stFlrSF", "2ndFlrSF"]
        if all(col in df.columns for col in sf_cols):
            df["TotalSF"] = df["TotalBsmtSF"].fillna(0) + df["1stFlrSF"] + df["2ndFlrSF"]
            self.created_features.append("TotalSF")

        # Living area ratio
        if "GrLivArea" in df.columns and "LotArea" in df.columns:
            df["LivAreaRatio"] = df["GrLivArea"] / (df["LotArea"] + 1)
            self.created_features.append("LivAreaRatio")

        # Above ground living area
        if "1stFlrSF" in df.columns and "2ndFlrSF" in df.columns:
            df["TotalAbvGrdSF"] = df["1stFlrSF"] + df["2ndFlrSF"]
            self.created_features.append("TotalAbvGrdSF")

        # Average room size
        if "GrLivArea" in df.columns and "TotRmsAbvGrd" in df.columns:
            df["AvgRoomSize"] = df["GrLivArea"] / (df["TotRmsAbvGrd"] + 1)
            self.created_features.append("AvgRoomSize")

        return df

    def _create_quality_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create quality-related features."""
        # Overall quality score
        if "OverallQual" in df.columns and "OverallCond" in df.columns:
            df["OverallScore"] = df["OverallQual"] * df["OverallCond"]
            df["QualCondDiff"] = df["OverallQual"] - df["OverallCond"]
            self.created_features.extend(["OverallScore", "QualCondDiff"])

        # Quality per square foot
        if "OverallQual" in df.columns and "GrLivArea" in df.columns:
            df["QualPerSF"] = df["OverallQual"] / (df["GrLivArea"] / 1000)
            self.created_features.append("QualPerSF")

        return df

    def _create_bathroom_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create bathroom-related features."""
        bath_cols = ["FullBath", "HalfBath", "BsmtFullBath", "BsmtHalfBath"]
        available_cols = [col for col in bath_cols if col in df.columns]

        if available_cols:
            df["TotalBaths"] = sum(
                df[col].fillna(0) * (0.5 if "Half" in col else 1)
                for col in available_cols
            )
            self.created_features.append("TotalBaths")

        # Bathrooms per bedroom
        if "TotalBaths" in df.columns and "BedroomAbvGr" in df.columns:
            df["BathPerBed"] = df["TotalBaths"] / (df["BedroomAbvGr"] + 1)
            self.created_features.append("BathPerBed")

        return df

    def _create_garage_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create garage-related features."""
        if "GarageCars" in df.columns and "GarageArea" in df.columns:
            df["GarageAreaPerCar"] = df["GarageArea"] / (df["GarageCars"].replace(0, 1))
            df["HasGarage"] = (df["GarageCars"] > 0).astype(int)
            self.created_features.extend(["GarageAreaPerCar", "HasGarage"])

        return df

    def _create_basement_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create basement-related features."""
        if "TotalBsmtSF" in df.columns:
            df["HasBasement"] = (df["TotalBsmtSF"] > 0).astype(int)
            self.created_features.append("HasBasement")

        bsmt_fin_cols = ["BsmtFinSF1", "BsmtFinSF2"]
        if all(col in df.columns for col in bsmt_fin_cols) and "TotalBsmtSF" in df.columns:
            df["TotalBsmtFinSF"] = df["BsmtFinSF1"].fillna(0) + df["BsmtFinSF2"].fillna(0)
            df["BsmtFinRatio"] = df["TotalBsmtFinSF"] / (df["TotalBsmtSF"].replace(0, 1))
            self.created_features.extend(["TotalBsmtFinSF", "BsmtFinRatio"])

        return df

    def _create_porch_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create porch-related features."""
        porch_cols = ["OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch"]
        available_cols = [col for col in porch_cols if col in df.columns]

        if available_cols:
            df["TotalPorchSF"] = sum(df[col].fillna(0) for col in available_cols)
            df["HasPorch"] = (df["TotalPorchSF"] > 0).astype(int)
            self.created_features.extend(["TotalPorchSF", "HasPorch"])

        return df

    def _create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between important variables."""
        # Age * Quality interaction
        if "HouseAge" in df.columns and "OverallQual" in df.columns:
            df["AgeQualInteraction"] = df["HouseAge"] * df["OverallQual"]
            self.created_features.append("AgeQualInteraction")

        # Area * Quality interaction
        if "GrLivArea" in df.columns and "OverallQual" in df.columns:
            df["AreaQualInteraction"] = df["GrLivArea"] * df["OverallQual"]
            self.created_features.append("AreaQualInteraction")

        # Neighborhood quality proxy
        if "TotalSF" in df.columns and "OverallQual" in df.columns:
            df["SFQualProduct"] = df["TotalSF"] * df["OverallQual"]
            self.created_features.append("SFQualProduct")

        return df

    def _create_binary_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create binary indicator features."""
        if "PoolArea" in df.columns:
            df["HasPool"] = (df["PoolArea"] > 0).astype(int)
            self.created_features.append("HasPool")

        if "Fireplaces" in df.columns:
            df["HasFireplace"] = (df["Fireplaces"] > 0).astype(int)
            self.created_features.append("HasFireplace")

        if "WoodDeckSF" in df.columns:
            df["HasDeck"] = (df["WoodDeckSF"] > 0).astype(int)
            self.created_features.append("HasDeck")

        if "MiscVal" in df.columns:
            df["HasMiscFeature"] = (df["MiscVal"] > 0).astype(int)
            self.created_features.append("HasMiscFeature")

        return df

    def get_created_features(self) -> List[str]:
        """Return list of created feature names."""
        return list(set(self.created_features))
