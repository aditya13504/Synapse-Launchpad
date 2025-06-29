import asyncio
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

import cudf
import nvtabular as nvt
from merlin.core.utils import Distributed
from merlin.models.tf import Model
from merlin.schema import Schema, Tags
import redis.asyncio as redis
from kafka import KafkaConsumer
import asyncpg

from .config import Config
from .schema import CompanyFeatures, TractionMetrics

logger = logging.getLogger(__name__)

class FeaturePipeline:
    """
    NVIDIA Merlin-based feature pipeline for processing market pulse events
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.feature_store_path = Path(config.feature_store_path)
        self.model_path = Path(config.model_path)
        
        # Ensure directories exist
        self.feature_store_path.mkdir(parents=True, exist_ok=True)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize Merlin components
        self.workflow: Optional[nvt.Workflow] = None
        self.schema: Optional[Schema] = None
        
    async def initialize(self):
        """Initialize pipeline components"""
        try:
            # Initialize Redis
            self.redis_client = redis.from_url(self.config.redis_url)
            
            # Initialize database pool
            self.db_pool = await asyncpg.create_pool(self.config.database_url)
            
            # Setup Merlin workflow
            await self._setup_merlin_workflow()
            
            # Start background pipeline
            asyncio.create_task(self._run_pipeline_scheduler())
            
            logger.info("Feature pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize pipeline: {e}")
            raise
    
    async def close(self):
        """Close pipeline connections"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            logger.info("Feature pipeline closed")
            
        except Exception as e:
            logger.error(f"Error closing pipeline: {e}")
    
    async def _setup_merlin_workflow(self):
        """Setup NVIDIA Merlin workflow for feature engineering"""
        try:
            # Define feature schema
            self.schema = Schema([
                ("company_id", Tags.CATEGORICAL),
                ("user_overlap_score", Tags.CONTINUOUS),
                ("funding_amount", Tags.CONTINUOUS),
                ("employee_count", Tags.CONTINUOUS),
                ("growth_rate", Tags.CONTINUOUS),
                ("market_sentiment", Tags.CONTINUOUS),
                ("culture_vector", Tags.LIST),
                ("match_outcome", Tags.TARGET)
            ])
            
            # Create preprocessing workflow
            categorical_features = ["company_id"] >> nvt.ops.Categorify()
            continuous_features = [
                "user_overlap_score", "funding_amount", "employee_count", 
                "growth_rate", "market_sentiment"
            ] >> nvt.ops.FillMissing() >> nvt.ops.Normalize()
            
            # Culture vector processing
            culture_features = ["culture_vector"] >> nvt.ops.ListSlice(0, self.config.embedding_dim)
            
            # Target processing
            target_features = ["match_outcome"] >> nvt.ops.LambdaOp(lambda x: x.astype('int32'))
            
            # Combine all features
            workflow_ops = categorical_features + continuous_features + culture_features + target_features
            
            self.workflow = nvt.Workflow(workflow_ops)
            
            logger.info("Merlin workflow setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup Merlin workflow: {e}")
            raise
    
    async def process_pulse_events(self, start_time: datetime, end_time: datetime) -> int:
        """
        Process pulse events and generate features
        """
        try:
            logger.info(f"Processing pulse events from {start_time} to {end_time}")
            
            # Fetch pulse events from database
            events = await self._fetch_pulse_events(start_time, end_time)
            
            if not events:
                logger.info("No events to process")
                return 0
            
            # Transform events to features
            features = await self._transform_events_to_features(events)
            
            # Process with Merlin
            processed_features = await self._process_with_merlin(features)
            
            # Store features
            await self._store_features(processed_features)
            
            logger.info(f"Processed {len(processed_features)} feature records")
            return len(processed_features)
            
        except Exception as e:
            logger.error(f"Failed to process pulse events: {e}")
            raise
    
    async def _fetch_pulse_events(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Fetch pulse events from database"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT 
                        company,
                        entities,
                        sentiment,
                        source,
                        timestamp,
                        content
                    FROM market_pulse_events 
                    WHERE timestamp BETWEEN $1 AND $2
                    ORDER BY timestamp
                """, start_time, end_time)
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to fetch pulse events: {e}")
            return []
    
    async def _transform_events_to_features(self, events: List[Dict[str, Any]]) -> List[CompanyFeatures]:
        """Transform pulse events into feature format"""
        features = []
        company_aggregates = {}
        
        try:
            # Aggregate events by company
            for event in events:
                company = event['company']
                
                if company not in company_aggregates:
                    company_aggregates[company] = {
                        'events': [],
                        'sentiment_scores': [],
                        'funding_mentions': 0,
                        'employee_mentions': 0,
                        'growth_mentions': 0
                    }
                
                company_aggregates[company]['events'].append(event)
                
                # Extract sentiment
                sentiment = event.get('sentiment', {})
                if isinstance(sentiment, str):
                    sentiment = json.loads(sentiment)
                
                if sentiment.get('compound'):
                    company_aggregates[company]['sentiment_scores'].append(sentiment['compound'])
                
                # Count specific mentions
                content = event.get('content', '').lower()
                if any(word in content for word in ['funding', 'raised', 'investment']):
                    company_aggregates[company]['funding_mentions'] += 1
                
                if any(word in content for word in ['employee', 'hiring', 'team']):
                    company_aggregates[company]['employee_mentions'] += 1
                
                if any(word in content for word in ['growth', 'expansion', 'scale']):
                    company_aggregates[company]['growth_mentions'] += 1
            
            # Generate features for each company
            for company_id, data in company_aggregates.items():
                # Calculate user overlap score (mock implementation)
                user_overlap_score = await self._calculate_user_overlap(company_id)
                
                # Calculate traction metrics
                avg_sentiment = np.mean(data['sentiment_scores']) if data['sentiment_scores'] else 0.0
                
                # Get company data from database
                company_data = await self._get_company_data(company_id)
                
                traction_metrics = TractionMetrics(
                    funding_amount=company_data.get('funding_amount', 0.0),
                    employee_count=company_data.get('employee_count', 0),
                    growth_rate=company_data.get('growth_rate', 0.0),
                    market_sentiment=avg_sentiment,
                    revenue_growth=data['growth_mentions'] * 0.1,  # Mock calculation
                    user_growth=data['employee_mentions'] * 0.05   # Mock calculation
                )
                
                # Generate culture vector (mock implementation using event content)
                culture_vector = await self._generate_culture_vector(data['events'])
                
                # Determine match outcome (for training data)
                match_outcome = await self._get_match_outcome(company_id)
                
                feature = CompanyFeatures(
                    company_id=company_id,
                    user_overlap_score=user_overlap_score,
                    traction_metrics=traction_metrics,
                    culture_vector=culture_vector,
                    match_outcome=match_outcome,
                    timestamp=datetime.utcnow()
                )
                
                features.append(feature)
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to transform events to features: {e}")
            return []
    
    async def _calculate_user_overlap(self, company_id: str) -> float:
        """Calculate user overlap score with other companies"""
        try:
            # Mock implementation - in reality, this would analyze user bases
            # Could use LinkedIn data, social media followers, etc.
            
            # Get from cache if available
            cache_key = f"user_overlap:{company_id}"
            cached_score = await self.redis_client.get(cache_key)
            
            if cached_score:
                return float(cached_score)
            
            # Calculate overlap (mock)
            overlap_score = np.random.beta(2, 5)  # Skewed towards lower values
            
            # Cache for 24 hours
            await self.redis_client.setex(cache_key, 86400, str(overlap_score))
            
            return overlap_score
            
        except Exception as e:
            logger.error(f"Failed to calculate user overlap: {e}")
            return 0.0
    
    async def _get_company_data(self, company_id: str) -> Dict[str, Any]:
        """Get company data from database"""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT funding_amount, employee_count, growth_rate
                    FROM companies 
                    WHERE name ILIKE $1
                    LIMIT 1
                """, f"%{company_id}%")
                
                if row:
                    return dict(row)
                
                # Return defaults if not found
                return {
                    'funding_amount': 0.0,
                    'employee_count': 10,
                    'growth_rate': 0.0
                }
                
        except Exception as e:
            logger.error(f"Failed to get company data: {e}")
            return {'funding_amount': 0.0, 'employee_count': 10, 'growth_rate': 0.0}
    
    async def _generate_culture_vector(self, events: List[Dict[str, Any]]) -> List[float]:
        """Generate culture embedding vector from events"""
        try:
            # Mock implementation - in reality, this would use NLP models
            # to extract cultural indicators from company communications
            
            # Combine all event content
            all_content = " ".join([event.get('content', '') for event in events])
            
            # Simple keyword-based culture vector (mock)
            culture_keywords = {
                'innovation': ['innovation', 'creative', 'breakthrough', 'cutting-edge'],
                'collaboration': ['team', 'together', 'partnership', 'collaborate'],
                'growth': ['growth', 'scale', 'expand', 'ambitious'],
                'customer_focus': ['customer', 'user', 'client', 'satisfaction'],
                'quality': ['quality', 'excellence', 'best', 'premium'],
                'agility': ['agile', 'fast', 'quick', 'responsive'],
                'transparency': ['transparent', 'open', 'honest', 'clear'],
                'diversity': ['diverse', 'inclusive', 'equality', 'belonging']
            }
            
            vector = []
            content_lower = all_content.lower()
            
            for category, keywords in culture_keywords.items():
                score = sum(content_lower.count(keyword) for keyword in keywords)
                vector.extend([score / max(len(all_content), 1)] * 16)  # 16 dims per category
            
            # Pad or truncate to exactly 128 dimensions
            if len(vector) < 128:
                vector.extend([0.0] * (128 - len(vector)))
            else:
                vector = vector[:128]
            
            # Normalize vector
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = (np.array(vector) / norm).tolist()
            
            return vector
            
        except Exception as e:
            logger.error(f"Failed to generate culture vector: {e}")
            return [0.0] * 128
    
    async def _get_match_outcome(self, company_id: str) -> Optional[int]:
        """Get match outcome for training data"""
        try:
            async with self.db_pool.acquire() as conn:
                # Check if company has successful partnerships
                row = await conn.fetchrow("""
                    SELECT COUNT(*) as successful_matches
                    FROM partnerships p
                    JOIN companies ca ON p.company_a = ca.id
                    JOIN companies cb ON p.company_b = cb.id
                    WHERE (ca.name ILIKE $1 OR cb.name ILIKE $1)
                    AND p.status = 'active'
                """, f"%{company_id}%")
                
                if row and row['successful_matches'] > 0:
                    return 1
                else:
                    return 0
                    
        except Exception as e:
            logger.error(f"Failed to get match outcome: {e}")
            return None
    
    async def _process_with_merlin(self, features: List[CompanyFeatures]) -> List[CompanyFeatures]:
        """Process features with NVIDIA Merlin workflow"""
        try:
            if not features:
                return features
            
            # Convert to DataFrame
            data = []
            for feature in features:
                row = {
                    'company_id': feature.company_id,
                    'user_overlap_score': feature.user_overlap_score,
                    'funding_amount': feature.traction_metrics.funding_amount,
                    'employee_count': feature.traction_metrics.employee_count,
                    'growth_rate': feature.traction_metrics.growth_rate,
                    'market_sentiment': feature.traction_metrics.market_sentiment,
                    'culture_vector': feature.culture_vector,
                    'match_outcome': feature.match_outcome or 0
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Convert to cuDF for GPU processing
            gdf = cudf.from_pandas(df)
            
            # Apply Merlin workflow if fitted
            workflow_path = self.model_path / "workflow"
            if workflow_path.exists():
                self.workflow = nvt.Workflow.load(str(workflow_path))
                processed_gdf = self.workflow.transform(nvt.Dataset(gdf)).to_ddf().compute()
            else:
                # Fit and save workflow
                dataset = nvt.Dataset(gdf)
                self.workflow.fit(dataset)
                self.workflow.save(str(workflow_path))
                processed_gdf = self.workflow.transform(dataset).to_ddf().compute()
            
            # Convert back to pandas and update features
            processed_df = processed_gdf.to_pandas()
            
            # Update features with processed values
            for i, feature in enumerate(features):
                if i < len(processed_df):
                    row = processed_df.iloc[i]
                    # Update with normalized values
                    feature.user_overlap_score = float(row.get('user_overlap_score', feature.user_overlap_score))
                    feature.traction_metrics.funding_amount = float(row.get('funding_amount', feature.traction_metrics.funding_amount))
                    feature.traction_metrics.employee_count = int(row.get('employee_count', feature.traction_metrics.employee_count))
                    feature.traction_metrics.growth_rate = float(row.get('growth_rate', feature.traction_metrics.growth_rate))
                    feature.traction_metrics.market_sentiment = float(row.get('market_sentiment', feature.traction_metrics.market_sentiment))
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to process with Merlin: {e}")
            return features
    
    async def _store_features(self, features: List[CompanyFeatures]):
        """Store features in parquet format and cache"""
        try:
            if not features:
                return
            
            # Convert to DataFrame
            data = []
            for feature in features:
                row = {
                    'company_id': feature.company_id,
                    'user_overlap_score': feature.user_overlap_score,
                    'funding_amount': feature.traction_metrics.funding_amount,
                    'employee_count': feature.traction_metrics.employee_count,
                    'growth_rate': feature.traction_metrics.growth_rate,
                    'market_sentiment': feature.traction_metrics.market_sentiment,
                    'revenue_growth': feature.traction_metrics.revenue_growth,
                    'user_growth': feature.traction_metrics.user_growth,
                    'culture_vector': feature.culture_vector,
                    'match_outcome': feature.match_outcome,
                    'timestamp': feature.timestamp
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Store as parquet with date partitioning
            date_str = datetime.utcnow().strftime("%Y-%m-%d")
            parquet_path = self.feature_store_path / f"features_{date_str}.parquet"
            
            df.to_parquet(parquet_path, index=False)
            
            # Cache latest features in Redis
            for feature in features:
                cache_key = f"features:{feature.company_id}"
                await self.redis_client.setex(
                    cache_key, 
                    3600,  # 1 hour TTL
                    feature.json()
                )
            
            logger.info(f"Stored {len(features)} features to {parquet_path}")
            
        except Exception as e:
            logger.error(f"Failed to store features: {e}")
    
    async def get_online_features(self, company_ids: List[str], feature_names: Optional[List[str]] = None) -> List[CompanyFeatures]:
        """Get features for online serving"""
        try:
            features = []
            
            for company_id in company_ids:
                # Try cache first
                cache_key = f"features:{company_id}"
                cached_data = await self.redis_client.get(cache_key)
                
                if cached_data:
                    feature = CompanyFeatures.parse_raw(cached_data)
                    features.append(feature)
                else:
                    # Fallback to latest parquet file
                    feature = await self._get_feature_from_storage(company_id)
                    if feature:
                        features.append(feature)
            
            return features
            
        except Exception as e:
            logger.error(f"Failed to get online features: {e}")
            return []
    
    async def _get_feature_from_storage(self, company_id: str) -> Optional[CompanyFeatures]:
        """Get feature from parquet storage"""
        try:
            # Find latest parquet file
            parquet_files = list(self.feature_store_path.glob("features_*.parquet"))
            
            if not parquet_files:
                return None
            
            # Sort by date and get latest
            latest_file = sorted(parquet_files)[-1]
            
            # Read and filter
            df = pd.read_parquet(latest_file)
            company_data = df[df['company_id'] == company_id]
            
            if company_data.empty:
                return None
            
            # Get latest record
            latest_record = company_data.iloc[-1]
            
            # Convert to CompanyFeatures
            traction_metrics = TractionMetrics(
                funding_amount=latest_record['funding_amount'],
                employee_count=latest_record['employee_count'],
                growth_rate=latest_record['growth_rate'],
                market_sentiment=latest_record['market_sentiment'],
                revenue_growth=latest_record.get('revenue_growth'),
                user_growth=latest_record.get('user_growth')
            )
            
            feature = CompanyFeatures(
                company_id=latest_record['company_id'],
                user_overlap_score=latest_record['user_overlap_score'],
                traction_metrics=traction_metrics,
                culture_vector=latest_record['culture_vector'],
                match_outcome=latest_record.get('match_outcome'),
                timestamp=latest_record['timestamp']
            )
            
            return feature
            
        except Exception as e:
            logger.error(f"Failed to get feature from storage: {e}")
            return None
    
    async def _run_pipeline_scheduler(self):
        """Run the pipeline scheduler"""
        try:
            while True:
                try:
                    # Calculate time range for processing
                    end_time = datetime.utcnow()
                    start_time = end_time - timedelta(hours=self.config.pipeline_interval_hours)
                    
                    # Process events
                    processed_count = await self.process_pulse_events(start_time, end_time)
                    
                    logger.info(f"Pipeline run completed: {processed_count} features processed")
                    
                    # Wait for next run
                    await asyncio.sleep(self.config.pipeline_interval_hours * 3600)
                    
                except Exception as e:
                    logger.error(f"Pipeline run failed: {e}")
                    # Wait 1 hour before retry
                    await asyncio.sleep(3600)
                    
        except asyncio.CancelledError:
            logger.info("Pipeline scheduler cancelled")
        except Exception as e:
            logger.error(f"Pipeline scheduler failed: {e}")
    
    async def get_feature_stats(self) -> Dict[str, Any]:
        """Get feature store statistics"""
        try:
            # Count parquet files
            parquet_files = list(self.feature_store_path.glob("features_*.parquet"))
            
            total_companies = 0
            feature_count = 0
            storage_size = 0
            last_updated = None
            
            for file_path in parquet_files:
                try:
                    df = pd.read_parquet(file_path)
                    total_companies += df['company_id'].nunique()
                    feature_count += len(df)
                    storage_size += file_path.stat().st_size
                    
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if not last_updated or file_time > last_updated:
                        last_updated = file_time
                        
                except Exception as e:
                    logger.error(f"Failed to read {file_path}: {e}")
                    continue
            
            return {
                'total_companies': total_companies,
                'feature_count': feature_count,
                'last_updated': last_updated or datetime.utcnow(),
                'storage_size_mb': storage_size / (1024 * 1024),
                'parquet_files': len(parquet_files)
            }
            
        except Exception as e:
            logger.error(f"Failed to get feature stats: {e}")
            return {
                'total_companies': 0,
                'feature_count': 0,
                'last_updated': datetime.utcnow(),
                'storage_size_mb': 0.0,
                'parquet_files': 0
            }