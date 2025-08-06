"""
Preprocessing Module Tests for ValorVista
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.preprocessing import FeatureEngineer, DataProcessor


class TestFeatureEngineer:
    """Test feature engineering functionality."""

    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame({
            'YearBuilt': [2000, 2010, 1990],
            'YearRemodAdd': [2000, 2015, 2005],
            'GrLivArea': [1500, 2000, 1200],
            'LotArea': [8000, 10000, 6000],
            'OverallQual': [7, 8, 6],
            'OverallCond': [5, 6, 5],
            'TotalBsmtSF': [1000, 1200, 800],
            '1stFlrSF': [1000, 1200, 800],
            '2ndFlrSF': [500, 800, 400],
            'FullBath': [2, 3, 1],
            'HalfBath': [1, 1, 0],
            'GarageCars': [2, 2, 1],
            'GarageArea': [500, 600, 300],
            'Fireplaces': [1, 2, 0],
            'WoodDeckSF': [100, 200, 0],
            'OpenPorchSF': [50, 100, 30],
            'PoolArea': [0, 0, 0]
        })

    def test_create_age_features(self, sample_df):
        """Test age feature creation."""
        fe = FeatureEngineer()
        result = fe.create_all_features(sample_df)

        assert 'HouseAge' in result.columns
        assert 'RemodAge' in result.columns
        assert result['HouseAge'].iloc[0] == 2024 - 2000

    def test_create_area_features(self, sample_df):
        """Test area feature creation."""
        fe = FeatureEngineer()
        result = fe.create_all_features(sample_df)

        assert 'TotalSF' in result.columns
        assert 'LivAreaRatio' in result.columns

    def test_create_quality_features(self, sample_df):
        """Test quality feature creation."""
        fe = FeatureEngineer()
        result = fe.create_all_features(sample_df)

        assert 'OverallScore' in result.columns
        assert result['OverallScore'].iloc[0] == 7 * 5

    def test_create_bathroom_features(self, sample_df):
        """Test bathroom feature creation."""
        fe = FeatureEngineer()
        result = fe.create_all_features(sample_df)

        assert 'TotalBaths' in result.columns
        # 2 full + 0.5 * 1 half = 2.5
        assert result['TotalBaths'].iloc[0] == 2.5

    def test_create_binary_features(self, sample_df):
        """Test binary feature creation."""
        fe = FeatureEngineer()
        result = fe.create_all_features(sample_df)

        assert 'HasPool' in result.columns
        assert 'HasFireplace' in result.columns
        assert result['HasFireplace'].iloc[0] == 1
        assert result['HasFireplace'].iloc[2] == 0


class TestDataProcessor:
    """Test data processing functionality."""

    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame for testing."""
        return pd.DataFrame({
            'GrLivArea': [1500, 2000, 1200],
            'LotArea': [8000, 10000, 6000],
            'OverallQual': [7, 8, 6],
            'OverallCond': [5, 6, 5],
            'YearBuilt': [2000, 2010, 1990],
            'YearRemodAdd': [2000, 2015, 2005],
            'TotalBsmtSF': [1000, 1200, 800],
            '1stFlrSF': [1000, 1200, 800],
            '2ndFlrSF': [500, 800, 400],
            'FullBath': [2, 3, 1],
            'HalfBath': [1, 1, 0],
            'BedroomAbvGr': [3, 4, 2],
            'TotRmsAbvGrd': [6, 8, 5],
            'GarageCars': [2, 2, 1],
            'GarageArea': [500, 600, 300],
            'Fireplaces': [1, 2, 0],
            'MSZoning': ['RL', 'RL', 'RM'],
            'Neighborhood': ['NAmes', 'CollgCr', 'OldTown'],
            'SalePrice': [200000, 300000, 150000]
        })

    def test_fit_transform(self, sample_df):
        """Test fit and transform."""
        processor = DataProcessor()
        result = processor.fit_transform(sample_df)

        assert isinstance(result, np.ndarray)
        assert result.shape[0] == 3
        assert processor.is_fitted

    def test_transform_without_fit(self, sample_df):
        """Test transform raises error without fit."""
        processor = DataProcessor()

        with pytest.raises(ValueError):
            processor.transform(sample_df)

    def test_get_feature_names(self, sample_df):
        """Test feature names retrieval."""
        processor = DataProcessor()
        processor.fit(sample_df)

        names = processor.get_feature_names()
        assert isinstance(names, list)
        assert len(names) > 0
