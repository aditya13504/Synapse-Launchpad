import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from src.rest_api import create_rest_app
from src.pipeline import FeaturePipeline
from src.config import Config
from src.schema import CompanyFeatures, TractionMetrics

@pytest.fixture
def mock_pipeline():
    """Mock pipeline for testing"""
    pipeline = MagicMock(spec=FeaturePipeline)
    pipeline.config = Config()
    
    # Mock async methods
    pipeline.get_online_features = AsyncMock()
    pipeline.process_pulse_events = AsyncMock()
    pipeline.get_feature_stats = AsyncMock()
    pipeline._store_features = AsyncMock()
    
    return pipeline

@pytest.fixture
def client(mock_pipeline):
    """Test client"""
    app = create_rest_app(mock_pipeline)
    return TestClient(app)

@pytest.fixture
def sample_feature():
    """Sample feature for testing"""
    return CompanyFeatures(
        company_id='TestCorp',
        user_overlap_score=0.75,
        traction_metrics=TractionMetrics(
            funding_amount=10000000.0,
            employee_count=150,
            growth_rate=25.5,
            market_sentiment=0.4
        ),
        culture_vector=[0.1] * 128,
        match_outcome=1,
        timestamp=datetime.utcnow()
    )

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "feature-store"
    assert "timestamp" in data

def test_get_online_features(client, mock_pipeline, sample_feature):
    """Test getting online features"""
    mock_pipeline.get_online_features.return_value = [sample_feature]
    
    request_data = {
        "company_ids": ["TestCorp"],
        "feature_names": ["user_overlap_score", "funding_amount"]
    }
    
    response = client.post("/features/online", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["features"]) == 1
    assert data["features"][0]["company_id"] == "TestCorp"
    assert data["features"][0]["user_overlap_score"] == 0.75
    assert "metadata" in data

def test_get_online_features_empty(client, mock_pipeline):
    """Test getting online features with no results"""
    mock_pipeline.get_online_features.return_value = []
    
    request_data = {
        "company_ids": ["UnknownCorp"]
    }
    
    response = client.post("/features/online", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["features"]) == 0
    assert data["metadata"]["feature_count"] == 0

def test_get_historical_features(client, mock_pipeline, sample_feature):
    """Test getting historical features"""
    mock_pipeline.get_online_features.return_value = [sample_feature]
    
    start_time = datetime.utcnow() - timedelta(days=7)
    end_time = datetime.utcnow()
    
    params = {
        "company_ids": ["TestCorp"],
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }
    
    response = client.post("/features/historical", params=params)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["features"]) == 1
    assert "time_range" in data["metadata"]

def test_trigger_batch_processing(client, mock_pipeline):
    """Test triggering batch processing"""
    mock_pipeline.process_pulse_events.return_value = 100
    
    request_data = {
        "start_time": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "end_time": datetime.utcnow().isoformat()
    }
    
    response = client.post("/features/batch", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "estimated_completion" in data

def test_get_feature_stats(client, mock_pipeline):
    """Test getting feature statistics"""
    mock_pipeline.get_feature_stats.return_value = {
        'total_companies': 50,
        'feature_count': 1000,
        'last_updated': datetime.utcnow(),
        'storage_size_mb': 25.5,
        'parquet_files': 5
    }
    
    response = client.get("/features/stats")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_companies"] == 50
    assert data["feature_count"] == 1000
    assert data["storage_size_mb"] == 25.5

def test_get_pipeline_status(client, mock_pipeline):
    """Test getting pipeline status"""
    response = client.get("/pipeline/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "last_run" in data
    assert "next_run" in data

def test_get_company_features(client, mock_pipeline, sample_feature):
    """Test getting features for specific company"""
    mock_pipeline.get_online_features.return_value = [sample_feature]
    
    response = client.post("/features/company/TestCorp?feature_view=default")
    
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == "TestCorp"
    assert "features" in data
    assert data["features"]["user_overlap_score"] == 0.75
    assert data["ttl_seconds"] == 3600

def test_get_company_features_not_found(client, mock_pipeline):
    """Test getting features for non-existent company"""
    mock_pipeline.get_online_features.return_value = []
    
    response = client.post("/features/company/UnknownCorp")
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()

def test_write_features(client, mock_pipeline, sample_feature):
    """Test writing features"""
    features_data = [sample_feature.dict()]
    
    response = client.post("/features/write", json=features_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["features_written"] == 1
    
    mock_pipeline._store_features.assert_called_once()

def test_api_error_handling(client, mock_pipeline):
    """Test API error handling"""
    # Mock an exception
    mock_pipeline.get_online_features.side_effect = Exception("Database error")
    
    request_data = {
        "company_ids": ["TestCorp"]
    }
    
    response = client.post("/features/online", json=request_data)
    
    assert response.status_code == 500
    data = response.json()
    assert "Failed to get features" in data["detail"]

def test_invalid_request_data(client, mock_pipeline):
    """Test handling of invalid request data"""
    # Missing required field
    request_data = {
        "feature_names": ["user_overlap_score"]
        # Missing company_ids
    }
    
    response = client.post("/features/online", json=request_data)
    
    assert response.status_code == 422  # Validation error

if __name__ == "__main__":
    pytest.main([__file__])