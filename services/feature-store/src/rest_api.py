from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from .schema import (
    CompanyFeatures, FeatureRequest, FeatureResponse, 
    BatchFeatureRequest, PipelineStatus, FeatureStats,
    OnlineFeatureRequest, OnlineFeatureResponse
)
from .pipeline import FeaturePipeline

logger = logging.getLogger(__name__)

def create_rest_app(pipeline: FeaturePipeline) -> FastAPI:
    """Create FastAPI application for feature store"""
    
    # Initialize Sentry
    if pipeline.config.sentry_dsn:
        sentry_sdk.init(
            dsn=pipeline.config.sentry_dsn,
            integrations=[FastApiIntegration()],
            environment=pipeline.config.environment,
        )
    
    app = FastAPI(
        title="Synapse LaunchPad - Feature Store",
        description="NVIDIA Merlin-powered feature store with FEAST-like API",
        version="1.0.0"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "feature-store",
            "timestamp": datetime.utcnow(),
            "pipeline_active": True
        }
    
    @app.post("/features/online", response_model=FeatureResponse)
    async def get_online_features(request: FeatureRequest):
        """
        Get features for online serving (low latency)
        """
        try:
            features = await pipeline.get_online_features(
                company_ids=request.company_ids,
                feature_names=request.feature_names
            )
            
            return FeatureResponse(
                features=features,
                metadata={
                    "request_id": f"online_{int(datetime.utcnow().timestamp())}",
                    "feature_count": len(features),
                    "latency_ms": 0,  # Would measure actual latency
                    "cache_hit_rate": 1.0  # Would calculate actual cache hit rate
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get online features: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get features: {str(e)}")
    
    @app.post("/features/historical", response_model=FeatureResponse)
    async def get_historical_features(
        company_ids: List[str],
        start_time: datetime,
        end_time: datetime,
        feature_names: Optional[List[str]] = None
    ):
        """
        Get historical features for training/analysis
        """
        try:
            # For historical features, we'd read from parquet files
            # This is a simplified implementation
            features = await pipeline.get_online_features(company_ids, feature_names)
            
            # Filter by time range (simplified)
            filtered_features = [
                f for f in features 
                if start_time <= f.timestamp <= end_time
            ]
            
            return FeatureResponse(
                features=filtered_features,
                metadata={
                    "request_id": f"historical_{int(datetime.utcnow().timestamp())}",
                    "feature_count": len(filtered_features),
                    "time_range": f"{start_time} to {end_time}",
                    "total_available": len(features)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get historical features: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get historical features: {str(e)}")
    
    @app.post("/features/batch")
    async def trigger_batch_processing(
        background_tasks: BackgroundTasks,
        request: BatchFeatureRequest
    ):
        """
        Trigger batch feature processing
        """
        try:
            # Add batch processing task to background
            background_tasks.add_task(
                pipeline.process_pulse_events,
                request.start_time,
                request.end_time
            )
            
            return {
                "status": "accepted",
                "message": "Batch processing started",
                "start_time": request.start_time,
                "end_time": request.end_time,
                "estimated_completion": datetime.utcnow() + timedelta(minutes=30)
            }
            
        except Exception as e:
            logger.error(f"Failed to trigger batch processing: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to start batch processing: {str(e)}")
    
    @app.get("/features/stats", response_model=FeatureStats)
    async def get_feature_stats():
        """
        Get feature store statistics
        """
        try:
            stats_data = await pipeline.get_feature_stats()
            
            return FeatureStats(
                total_companies=stats_data['total_companies'],
                feature_count=stats_data['feature_count'],
                last_updated=stats_data['last_updated'],
                storage_size_mb=stats_data['storage_size_mb'],
                avg_culture_vector_norm=1.0  # Would calculate actual norm
            )
            
        except Exception as e:
            logger.error(f"Failed to get feature stats: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")
    
    @app.get("/pipeline/status", response_model=PipelineStatus)
    async def get_pipeline_status():
        """
        Get pipeline status
        """
        try:
            # This would track actual pipeline runs
            return PipelineStatus(
                status="running",
                last_run=datetime.utcnow() - timedelta(hours=1),
                next_run=datetime.utcnow() + timedelta(hours=23),
                processed_events=1500,
                error_message=None
            )
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")
    
    @app.post("/features/company/{company_id}")
    async def get_company_features(
        company_id: str,
        feature_view: str = "default"
    ) -> OnlineFeatureResponse:
        """
        Get features for a specific company (FEAST-like interface)
        """
        try:
            features = await pipeline.get_online_features([company_id])
            
            if not features:
                raise HTTPException(status_code=404, detail="Company features not found")
            
            feature = features[0]
            
            return OnlineFeatureResponse(
                company_id=company_id,
                features={
                    "user_overlap_score": feature.user_overlap_score,
                    "funding_amount": feature.traction_metrics.funding_amount,
                    "employee_count": feature.traction_metrics.employee_count,
                    "growth_rate": feature.traction_metrics.growth_rate,
                    "market_sentiment": feature.traction_metrics.market_sentiment,
                    "culture_vector": feature.culture_vector,
                    "match_outcome": feature.match_outcome
                },
                timestamp=feature.timestamp,
                ttl_seconds=3600
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get company features: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get company features: {str(e)}")
    
    @app.post("/features/write")
    async def write_features(features: List[CompanyFeatures]):
        """
        Write features to the store
        """
        try:
            await pipeline._store_features(features)
            
            return {
                "status": "success",
                "message": f"Wrote {len(features)} feature records",
                "features_written": len(features)
            }
            
        except Exception as e:
            logger.error(f"Failed to write features: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to write features: {str(e)}")
    
    return app