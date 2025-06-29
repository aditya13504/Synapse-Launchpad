import grpc
from concurrent import futures
import logging
from typing import List
from datetime import datetime

from .feature_store_pb2_grpc import FeatureStoreServicer as BaseFeatureStoreServicer
from .feature_store_pb2_grpc import add_FeatureStoreServicer_to_server
from . import feature_store_pb2 as pb2
from .pipeline import FeaturePipeline
from .schema import CompanyFeatures, TractionMetrics

logger = logging.getLogger(__name__)

class FeatureStoreServicer(BaseFeatureStoreServicer):
    """
    gRPC servicer for feature store
    """
    
    def __init__(self, pipeline: FeaturePipeline):
        self.pipeline = pipeline
    
    async def GetOnlineFeatures(self, request, context):
        """Get features for online serving"""
        try:
            features = await self.pipeline.get_online_features(
                company_ids=list(request.company_ids),
                feature_names=list(request.feature_names) if request.feature_names else None
            )
            
            # Convert to protobuf
            pb_features = []
            for feature in features:
                pb_traction = pb2.TractionMetrics(
                    funding_amount=feature.traction_metrics.funding_amount,
                    employee_count=feature.traction_metrics.employee_count,
                    growth_rate=feature.traction_metrics.growth_rate,
                    market_sentiment=feature.traction_metrics.market_sentiment,
                    revenue_growth=feature.traction_metrics.revenue_growth or 0.0,
                    user_growth=feature.traction_metrics.user_growth or 0.0
                )
                
                pb_feature = pb2.CompanyFeatures(
                    company_id=feature.company_id,
                    user_overlap_score=feature.user_overlap_score,
                    traction_metrics=pb_traction,
                    culture_vector=feature.culture_vector,
                    match_outcome=feature.match_outcome or 0,
                    timestamp=self._datetime_to_timestamp(feature.timestamp)
                )
                
                pb_features.append(pb_feature)
            
            metadata = pb2.ResponseMetadata(
                feature_count=len(features),
                query_time=self._datetime_to_timestamp(datetime.utcnow()),
                latency_ms=0.0  # Would measure actual latency
            )
            
            return pb2.OnlineFeaturesResponse(
                features=pb_features,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"GetOnlineFeatures failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get online features: {str(e)}")
            return pb2.OnlineFeaturesResponse()
    
    async def GetHistoricalFeatures(self, request, context):
        """Get historical features for training"""
        try:
            # Convert timestamps
            start_time = self._timestamp_to_datetime(request.start_time)
            end_time = self._timestamp_to_datetime(request.end_time)
            
            # Get features (simplified - would implement proper historical lookup)
            features = await self.pipeline.get_online_features(
                company_ids=list(request.company_ids),
                feature_names=list(request.feature_names) if request.feature_names else None
            )
            
            # Filter by time range
            filtered_features = [
                f for f in features 
                if start_time <= f.timestamp <= end_time
            ]
            
            # Convert to protobuf
            pb_features = []
            for feature in filtered_features:
                pb_traction = pb2.TractionMetrics(
                    funding_amount=feature.traction_metrics.funding_amount,
                    employee_count=feature.traction_metrics.employee_count,
                    growth_rate=feature.traction_metrics.growth_rate,
                    market_sentiment=feature.traction_metrics.market_sentiment,
                    revenue_growth=feature.traction_metrics.revenue_growth or 0.0,
                    user_growth=feature.traction_metrics.user_growth or 0.0
                )
                
                pb_feature = pb2.CompanyFeatures(
                    company_id=feature.company_id,
                    user_overlap_score=feature.user_overlap_score,
                    traction_metrics=pb_traction,
                    culture_vector=feature.culture_vector,
                    match_outcome=feature.match_outcome or 0,
                    timestamp=self._datetime_to_timestamp(feature.timestamp)
                )
                
                pb_features.append(pb_feature)
            
            metadata = pb2.ResponseMetadata(
                feature_count=len(filtered_features),
                query_time=self._datetime_to_timestamp(datetime.utcnow()),
                latency_ms=0.0
            )
            
            return pb2.HistoricalFeaturesResponse(
                features=pb_features,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"GetHistoricalFeatures failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get historical features: {str(e)}")
            return pb2.HistoricalFeaturesResponse()
    
    async def WriteFeatures(self, request, context):
        """Write features to store"""
        try:
            # Convert from protobuf
            features = []
            for pb_feature in request.features:
                traction_metrics = TractionMetrics(
                    funding_amount=pb_feature.traction_metrics.funding_amount,
                    employee_count=pb_feature.traction_metrics.employee_count,
                    growth_rate=pb_feature.traction_metrics.growth_rate,
                    market_sentiment=pb_feature.traction_metrics.market_sentiment,
                    revenue_growth=pb_feature.traction_metrics.revenue_growth,
                    user_growth=pb_feature.traction_metrics.user_growth
                )
                
                feature = CompanyFeatures(
                    company_id=pb_feature.company_id,
                    user_overlap_score=pb_feature.user_overlap_score,
                    traction_metrics=traction_metrics,
                    culture_vector=list(pb_feature.culture_vector),
                    match_outcome=pb_feature.match_outcome,
                    timestamp=self._timestamp_to_datetime(pb_feature.timestamp)
                )
                
                features.append(feature)
            
            # Store features
            await self.pipeline._store_features(features)
            
            return pb2.WriteFeaturesResponse(
                success=True,
                message=f"Successfully wrote {len(features)} features",
                features_written=len(features)
            )
            
        except Exception as e:
            logger.error(f"WriteFeatures failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to write features: {str(e)}")
            return pb2.WriteFeaturesResponse(
                success=False,
                message=f"Failed to write features: {str(e)}",
                features_written=0
            )
    
    async def GetFeatureStats(self, request, context):
        """Get feature store statistics"""
        try:
            stats = await self.pipeline.get_feature_stats()
            
            return pb2.FeatureStatsResponse(
                total_companies=stats['total_companies'],
                feature_count=stats['feature_count'],
                last_updated=self._datetime_to_timestamp(stats['last_updated']),
                storage_size_mb=stats['storage_size_mb']
            )
            
        except Exception as e:
            logger.error(f"GetFeatureStats failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to get feature stats: {str(e)}")
            return pb2.FeatureStatsResponse()
    
    async def HealthCheck(self, request, context):
        """Health check"""
        try:
            return pb2.HealthCheckResponse(
                status="healthy",
                timestamp=self._datetime_to_timestamp(datetime.utcnow())
            )
            
        except Exception as e:
            logger.error(f"HealthCheck failed: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Health check failed: {str(e)}")
            return pb2.HealthCheckResponse(status="unhealthy")
    
    def _datetime_to_timestamp(self, dt: datetime):
        """Convert datetime to protobuf timestamp"""
        from google.protobuf.timestamp_pb2 import Timestamp
        timestamp = Timestamp()
        timestamp.FromDatetime(dt)
        return timestamp
    
    def _timestamp_to_datetime(self, timestamp) -> datetime:
        """Convert protobuf timestamp to datetime"""
        return timestamp.ToDatetime()