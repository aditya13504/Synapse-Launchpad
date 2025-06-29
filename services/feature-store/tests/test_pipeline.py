import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd
import numpy as np

from src.pipeline import FeaturePipeline
from src.config import Config
from src.schema import CompanyFeatures, TractionMetrics

@pytest.fixture
def config():
    """Test configuration"""
    return Config(
        database_url="postgresql://test:test@localhost:5432/test_db",
        redis_url="redis://localhost:6379/1",
        feature_store_path="/tmp/test_feature_store",
        model_path="/tmp/test_models",
        pipeline_interval_hours=1,
        batch_size=100
    )

@pytest.fixture
async def pipeline(config):
    """Test pipeline instance"""
    pipeline = FeaturePipeline(config)
    
    # Mock external dependencies
    pipeline.redis_client = AsyncMock()
    pipeline.db_pool = AsyncMock()
    
    return pipeline

@pytest.mark.asyncio
async def test_pipeline_initialization(pipeline):
    """Test pipeline initialization"""
    with patch('src.pipeline.redis.from_url') as mock_redis, \
         patch('src.pipeline.asyncpg.create_pool') as mock_pool:
        
        mock_redis.return_value = AsyncMock()
        mock_pool.return_value = AsyncMock()
        
        await pipeline.initialize()
        
        assert pipeline.redis_client is not None
        assert pipeline.db_pool is not None

@pytest.mark.asyncio
async def test_fetch_pulse_events(pipeline):
    """Test fetching pulse events from database"""
    # Mock database response
    mock_rows = [
        {
            'company': 'TestCorp',
            'entities': '{"companies": [{"text": "TestCorp"}]}',
            'sentiment': '{"compound": 0.5}',
            'source': 'news',
            'timestamp': datetime.utcnow(),
            'content': 'TestCorp raises $10M in Series A funding'
        }
    ]
    
    pipeline.db_pool.acquire.return_value.__aenter__.return_value.fetch.return_value = mock_rows
    
    start_time = datetime.utcnow() - timedelta(hours=24)
    end_time = datetime.utcnow()
    
    events = await pipeline._fetch_pulse_events(start_time, end_time)
    
    assert len(events) == 1
    assert events[0]['company'] == 'TestCorp'
    assert events[0]['source'] == 'news'

@pytest.mark.asyncio
async def test_transform_events_to_features(pipeline):
    """Test transforming events to features"""
    # Mock events
    events = [
        {
            'company': 'TestCorp',
            'entities': '{"companies": [{"text": "TestCorp"}]}',
            'sentiment': '{"compound": 0.5, "positive": 0.7}',
            'source': 'news',
            'timestamp': datetime.utcnow(),
            'content': 'TestCorp raises $10M in Series A funding and is hiring 50 new employees'
        },
        {
            'company': 'TestCorp',
            'entities': '{"companies": [{"text": "TestCorp"}]}',
            'sentiment': '{"compound": 0.3, "positive": 0.6}',
            'source': 'twitter',
            'timestamp': datetime.utcnow(),
            'content': 'TestCorp shows strong growth metrics this quarter'
        }
    ]
    
    # Mock helper methods
    pipeline._calculate_user_overlap = AsyncMock(return_value=0.75)
    pipeline._get_company_data = AsyncMock(return_value={
        'funding_amount': 10000000.0,
        'employee_count': 150,
        'growth_rate': 25.5
    })
    pipeline._generate_culture_vector = AsyncMock(return_value=[0.1] * 128)
    pipeline._get_match_outcome = AsyncMock(return_value=1)
    
    features = await pipeline._transform_events_to_features(events)
    
    assert len(features) == 1
    assert features[0].company_id == 'TestCorp'
    assert features[0].user_overlap_score == 0.75
    assert features[0].traction_metrics.funding_amount == 10000000.0
    assert features[0].traction_metrics.employee_count == 150
    assert features[0].traction_metrics.market_sentiment == 0.4  # Average of 0.5 and 0.3
    assert len(features[0].culture_vector) == 128
    assert features[0].match_outcome == 1

@pytest.mark.asyncio
async def test_calculate_user_overlap(pipeline):
    """Test user overlap calculation"""
    # Mock Redis cache miss
    pipeline.redis_client.get.return_value = None
    pipeline.redis_client.setex = AsyncMock()
    
    with patch('numpy.random.beta') as mock_beta:
        mock_beta.return_value = 0.65
        
        overlap_score = await pipeline._calculate_user_overlap('TestCorp')
        
        assert overlap_score == 0.65
        pipeline.redis_client.setex.assert_called_once()

@pytest.mark.asyncio
async def test_calculate_user_overlap_cached(pipeline):
    """Test user overlap calculation with cache hit"""
    # Mock Redis cache hit
    pipeline.redis_client.get.return_value = "0.85"
    
    overlap_score = await pipeline._calculate_user_overlap('TestCorp')
    
    assert overlap_score == 0.85

@pytest.mark.asyncio
async def test_generate_culture_vector(pipeline):
    """Test culture vector generation"""
    events = [
        {
            'content': 'We are an innovative company focused on collaboration and growth. Our team values quality and transparency.'
        },
        {
            'content': 'Customer satisfaction is our priority. We believe in agile development and diverse teams.'
        }
    ]
    
    culture_vector = await pipeline._generate_culture_vector(events)
    
    assert len(culture_vector) == 128
    assert all(isinstance(x, float) for x in culture_vector)
    
    # Check that vector is normalized
    norm = np.linalg.norm(culture_vector)
    assert abs(norm - 1.0) < 0.01 or norm == 0.0

@pytest.mark.asyncio
async def test_get_company_data(pipeline):
    """Test getting company data from database"""
    # Mock database response
    mock_row = {
        'funding_amount': 5000000.0,
        'employee_count': 75,
        'growth_rate': 15.2
    }
    
    pipeline.db_pool.acquire.return_value.__aenter__.return_value.fetchrow.return_value = mock_row
    
    company_data = await pipeline._get_company_data('TestCorp')
    
    assert company_data['funding_amount'] == 5000000.0
    assert company_data['employee_count'] == 75
    assert company_data['growth_rate'] == 15.2

@pytest.mark.asyncio
async def test_get_company_data_not_found(pipeline):
    """Test getting company data when not found"""
    # Mock database response - no data found
    pipeline.db_pool.acquire.return_value.__aenter__.return_value.fetchrow.return_value = None
    
    company_data = await pipeline._get_company_data('UnknownCorp')
    
    # Should return defaults
    assert company_data['funding_amount'] == 0.0
    assert company_data['employee_count'] == 10
    assert company_data['growth_rate'] == 0.0

@pytest.mark.asyncio
async def test_get_match_outcome(pipeline):
    """Test getting match outcome"""
    # Mock database response - successful matches found
    mock_row = {'successful_matches': 3}
    
    pipeline.db_pool.acquire.return_value.__aenter__.return_value.fetchrow.return_value = mock_row
    
    outcome = await pipeline._get_match_outcome('TestCorp')
    
    assert outcome == 1

@pytest.mark.asyncio
async def test_get_match_outcome_no_matches(pipeline):
    """Test getting match outcome with no matches"""
    # Mock database response - no matches found
    mock_row = {'successful_matches': 0}
    
    pipeline.db_pool.acquire.return_value.__aenter__.return_value.fetchrow.return_value = mock_row
    
    outcome = await pipeline._get_match_outcome('TestCorp')
    
    assert outcome == 0

@pytest.mark.asyncio
async def test_store_features(pipeline):
    """Test storing features"""
    features = [
        CompanyFeatures(
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
    ]
    
    with patch('pandas.DataFrame.to_parquet') as mock_to_parquet:
        await pipeline._store_features(features)
        
        # Verify parquet file was written
        mock_to_parquet.assert_called_once()
        
        # Verify Redis cache was updated
        pipeline.redis_client.setex.assert_called()

@pytest.mark.asyncio
async def test_get_online_features(pipeline):
    """Test getting online features"""
    # Mock cached feature
    cached_feature = CompanyFeatures(
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
    
    pipeline.redis_client.get.return_value = cached_feature.json()
    
    features = await pipeline.get_online_features(['TestCorp'])
    
    assert len(features) == 1
    assert features[0].company_id == 'TestCorp'
    assert features[0].user_overlap_score == 0.75

@pytest.mark.asyncio
async def test_get_feature_stats(pipeline):
    """Test getting feature statistics"""
    with patch('pathlib.Path.glob') as mock_glob, \
         patch('pandas.read_parquet') as mock_read_parquet, \
         patch('pathlib.Path.stat') as mock_stat:
        
        # Mock parquet files
        mock_file = MagicMock()
        mock_file.stat.return_value.st_size = 1024 * 1024  # 1MB
        mock_file.stat.return_value.st_mtime = datetime.utcnow().timestamp()
        mock_glob.return_value = [mock_file]
        
        # Mock DataFrame
        mock_df = pd.DataFrame({
            'company_id': ['TestCorp', 'TestCorp', 'AnotherCorp'],
            'user_overlap_score': [0.75, 0.80, 0.65]
        })
        mock_read_parquet.return_value = mock_df
        
        stats = await pipeline.get_feature_stats()
        
        assert stats['total_companies'] == 2  # Unique companies
        assert stats['feature_count'] == 3
        assert stats['storage_size_mb'] == 1.0
        assert stats['parquet_files'] == 1

@pytest.mark.asyncio
async def test_process_pulse_events_integration(pipeline):
    """Test full pulse events processing pipeline"""
    # Mock all dependencies
    pipeline._fetch_pulse_events = AsyncMock(return_value=[
        {
            'company': 'TestCorp',
            'entities': '{"companies": [{"text": "TestCorp"}]}',
            'sentiment': '{"compound": 0.5}',
            'source': 'news',
            'timestamp': datetime.utcnow(),
            'content': 'TestCorp raises funding'
        }
    ])
    
    pipeline._transform_events_to_features = AsyncMock(return_value=[
        CompanyFeatures(
            company_id='TestCorp',
            user_overlap_score=0.75,
            traction_metrics=TractionMetrics(
                funding_amount=10000000.0,
                employee_count=150,
                growth_rate=25.5,
                market_sentiment=0.5
            ),
            culture_vector=[0.1] * 128,
            match_outcome=1,
            timestamp=datetime.utcnow()
        )
    ])
    
    pipeline._process_with_merlin = AsyncMock(side_effect=lambda x: x)
    pipeline._store_features = AsyncMock()
    
    start_time = datetime.utcnow() - timedelta(hours=24)
    end_time = datetime.utcnow()
    
    processed_count = await pipeline.process_pulse_events(start_time, end_time)
    
    assert processed_count == 1
    pipeline._fetch_pulse_events.assert_called_once_with(start_time, end_time)
    pipeline._transform_events_to_features.assert_called_once()
    pipeline._process_with_merlin.assert_called_once()
    pipeline._store_features.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])