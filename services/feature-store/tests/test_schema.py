import pytest
from datetime import datetime
from pydantic import ValidationError

from src.schema import (
    TractionMetrics, CompanyFeatures, FeatureRequest, 
    FeatureResponse, OnlineFeatureRequest, OnlineFeatureResponse
)

def test_traction_metrics_valid():
    """Test valid traction metrics"""
    metrics = TractionMetrics(
        funding_amount=10000000.0,
        employee_count=150,
        growth_rate=25.5,
        market_sentiment=0.4
    )
    
    assert metrics.funding_amount == 10000000.0
    assert metrics.employee_count == 150
    assert metrics.growth_rate == 25.5
    assert metrics.market_sentiment == 0.4

def test_traction_metrics_validation():
    """Test traction metrics validation"""
    # Test negative funding amount
    with pytest.raises(ValidationError):
        TractionMetrics(
            funding_amount=-1000.0,
            employee_count=150,
            growth_rate=25.5,
            market_sentiment=0.4
        )
    
    # Test negative employee count
    with pytest.raises(ValidationError):
        TractionMetrics(
            funding_amount=10000000.0,
            employee_count=-10,
            growth_rate=25.5,
            market_sentiment=0.4
        )
    
    # Test market sentiment out of range
    with pytest.raises(ValidationError):
        TractionMetrics(
            funding_amount=10000000.0,
            employee_count=150,
            growth_rate=25.5,
            market_sentiment=1.5  # Should be between -1 and 1
        )

def test_company_features_valid():
    """Test valid company features"""
    traction_metrics = TractionMetrics(
        funding_amount=10000000.0,
        employee_count=150,
        growth_rate=25.5,
        market_sentiment=0.4
    )
    
    features = CompanyFeatures(
        company_id="TestCorp",
        user_overlap_score=0.75,
        traction_metrics=traction_metrics,
        culture_vector=[0.1] * 128,
        match_outcome=1
    )
    
    assert features.company_id == "TestCorp"
    assert features.user_overlap_score == 0.75
    assert len(features.culture_vector) == 128
    assert features.match_outcome == 1
    assert isinstance(features.timestamp, datetime)

def test_company_features_validation():
    """Test company features validation"""
    traction_metrics = TractionMetrics(
        funding_amount=10000000.0,
        employee_count=150,
        growth_rate=25.5,
        market_sentiment=0.4
    )
    
    # Test user overlap score out of range
    with pytest.raises(ValidationError):
        CompanyFeatures(
            company_id="TestCorp",
            user_overlap_score=1.5,  # Should be between 0 and 1
            traction_metrics=traction_metrics,
            culture_vector=[0.1] * 128
        )
    
    # Test culture vector wrong length
    with pytest.raises(ValidationError):
        CompanyFeatures(
            company_id="TestCorp",
            user_overlap_score=0.75,
            traction_metrics=traction_metrics,
            culture_vector=[0.1] * 64  # Should be 128 elements
        )

def test_feature_request_valid():
    """Test valid feature request"""
    request = FeatureRequest(
        company_ids=["TestCorp", "AnotherCorp"],
        feature_names=["user_overlap_score", "funding_amount"]
    )
    
    assert len(request.company_ids) == 2
    assert len(request.feature_names) == 2
    assert request.as_of_time is None

def test_feature_request_with_time():
    """Test feature request with as_of_time"""
    as_of_time = datetime.utcnow()
    
    request = FeatureRequest(
        company_ids=["TestCorp"],
        as_of_time=as_of_time
    )
    
    assert request.as_of_time == as_of_time

def test_feature_response():
    """Test feature response"""
    traction_metrics = TractionMetrics(
        funding_amount=10000000.0,
        employee_count=150,
        growth_rate=25.5,
        market_sentiment=0.4
    )
    
    features = [
        CompanyFeatures(
            company_id="TestCorp",
            user_overlap_score=0.75,
            traction_metrics=traction_metrics,
            culture_vector=[0.1] * 128
        )
    ]
    
    response = FeatureResponse(
        features=features,
        metadata={"feature_count": 1, "latency_ms": 50.0}
    )
    
    assert len(response.features) == 1
    assert response.metadata["feature_count"] == 1

def test_online_feature_request():
    """Test online feature request"""
    request = OnlineFeatureRequest(
        company_id="TestCorp",
        feature_view="default"
    )
    
    assert request.company_id == "TestCorp"
    assert request.feature_view == "default"

def test_online_feature_response():
    """Test online feature response"""
    timestamp = datetime.utcnow()
    
    response = OnlineFeatureResponse(
        company_id="TestCorp",
        features={
            "user_overlap_score": 0.75,
            "funding_amount": 10000000.0
        },
        timestamp=timestamp,
        ttl_seconds=3600
    )
    
    assert response.company_id == "TestCorp"
    assert response.features["user_overlap_score"] == 0.75
    assert response.timestamp == timestamp
    assert response.ttl_seconds == 3600

def test_json_serialization():
    """Test JSON serialization of models"""
    traction_metrics = TractionMetrics(
        funding_amount=10000000.0,
        employee_count=150,
        growth_rate=25.5,
        market_sentiment=0.4
    )
    
    features = CompanyFeatures(
        company_id="TestCorp",
        user_overlap_score=0.75,
        traction_metrics=traction_metrics,
        culture_vector=[0.1] * 128,
        match_outcome=1
    )
    
    # Test JSON serialization
    json_str = features.json()
    assert isinstance(json_str, str)
    assert "TestCorp" in json_str
    
    # Test deserialization
    features_copy = CompanyFeatures.parse_raw(json_str)
    assert features_copy.company_id == features.company_id
    assert features_copy.user_overlap_score == features.user_overlap_score

if __name__ == "__main__":
    pytest.main([__file__])