"""
API Endpoint Tests for ValorVista
"""

import pytest
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from config import TestingConfig


@pytest.fixture
def client():
    """Create test client."""
    app = create_app(TestingConfig())
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_property():
    """Sample property data for testing."""
    return {
        "GrLivArea": 1500,
        "OverallQual": 7,
        "OverallCond": 5,
        "YearBuilt": 2005,
        "BedroomAbvGr": 3,
        "FullBath": 2,
        "HalfBath": 1,
        "TotalBsmtSF": 1000,
        "GarageCars": 2,
        "Neighborhood": "NAmes"
    }


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test that health endpoint returns OK."""
        response = client.get('/api/v1/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


class TestPredictEndpoint:
    """Test prediction endpoint."""

    def test_predict_missing_data(self, client):
        """Test prediction with missing data."""
        response = client.post(
            '/api/v1/predict',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_predict_invalid_data(self, client):
        """Test prediction with invalid data."""
        response = client.post(
            '/api/v1/predict',
            data=json.dumps({"GrLivArea": "invalid"}),
            content_type='application/json'
        )
        assert response.status_code == 400


class TestBatchEndpoint:
    """Test batch prediction endpoint."""

    def test_batch_missing_properties(self, client):
        """Test batch with missing properties."""
        response = client.post(
            '/api/v1/predict/batch',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400


class TestFormOptionsEndpoint:
    """Test form options endpoint."""

    def test_get_options(self, client):
        """Test getting form options."""
        response = client.get('/api/v1/options')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert 'options' in data
        assert 'buildingTypes' in data['options']
        assert 'houseStyles' in data['options']


class TestNeighborhoodsEndpoint:
    """Test neighborhoods endpoint."""

    def test_get_neighborhoods(self, client):
        """Test getting neighborhoods list."""
        response = client.get('/api/v1/neighborhoods')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['success'] is True
        assert 'neighborhoods' in data
        assert len(data['neighborhoods']) > 0
        assert 'NAmes' in data['neighborhoods']
