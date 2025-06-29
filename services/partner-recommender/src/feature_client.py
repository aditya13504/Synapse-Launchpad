import grpc
import asyncio
import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)

class FeatureStoreClient:
    """
    Client for communicating with Feature Store service
    """
    
    def __init__(self, config):
        self.config = config
        self.http_client: Optional[httpx.AsyncClient] = None
        self.grpc_channel: Optional[grpc.aio.Channel] = None
        self.grpc_stub = None
    
    async def initialize(self):
        """Initialize feature store clients"""
        try:
            # Initialize HTTP client
            self.http_client = httpx.AsyncClient(
                base_url=self.config.feature_store_url,
                timeout=30.0
            )
            
            # Initialize gRPC client
            self.grpc_channel = grpc.aio.insecure_channel(self.config.feature_store_grpc_url)
            
            # Import protobuf stubs (would be generated from .proto file)
            # from feature_store_pb2_grpc import FeatureStoreStub
            # self.grpc_stub = FeatureStoreStub(self.grpc_channel)
            
            logger.info("Feature store client initialized")
            
        except Exception as e:
            logger.error(f"Feature store client initialization failed: {e}")
            raise
    
    async def close(self):
        """Close feature store connections"""
        try:
            if self.http_client:
                await self.http_client.aclose()
            
            if self.grpc_channel:
                await self.grpc_channel.close()
                
            logger.info("Feature store client closed")
            
        except Exception as e:
            logger.error(f"Error closing feature store client: {e}")
    
    async def health_check(self) -> bool:
        """Check feature store health"""
        try:
            if not self.http_client:
                return False
            
            response = await self.http_client.get("/health")
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Feature store health check failed: {e}")
            return False
    
    async def get_company_features(self, company_id: str) -> Dict[str, Any]:
        """
        Get features for a single company
        """
        try:
            response = await self.http_client.post(
                f"/features/company/{company_id}",
                params={"feature_view": "default"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get features for {company_id}: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get company features: {e}")
            return {}
    
    async def get_batch_features(self, company_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get features for multiple companies
        """
        try:
            request_data = {
                "company_ids": company_ids,
                "feature_names": [
                    "user_overlap_score",
                    "funding_amount", 
                    "employee_count",
                    "growth_rate",
                    "market_sentiment",
                    "culture_vector"
                ]
            }
            
            response = await self.http_client.post("/features/online", json=request_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Convert to company_id -> features mapping
                features_map = {}
                for feature in data.get("features", []):
                    company_id = feature.get("company_id")
                    if company_id:
                        features_map[company_id] = feature
                
                return features_map
            else:
                logger.warning(f"Failed to get batch features: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get batch features: {e}")
            return {}
    
    async def get_all_companies(self) -> List[str]:
        """
        Get list of all companies with features
        """
        try:
            response = await self.http_client.get("/features/stats")
            
            if response.status_code == 200:
                # This would need to be implemented in feature store
                # For now, return mock data
                return [
                    "TechFlow AI", "GreenStart Solutions", "DataViz Pro",
                    "CloudScale Systems", "AI Innovations", "FinTech Plus",
                    "HealthTech Solutions", "EduTech Platform", "RetailBot",
                    "LogiChain", "CyberGuard", "SmartCity Tech"
                ]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to get company list: {e}")
            return []
    
    def _prepare_features_for_model(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform feature store format to model input format
        """
        try:
            # Extract dense features
            dense_features = [
                features.get("user_overlap_score", 0.0),
                features.get("traction_metrics", {}).get("funding_amount", 0.0) / 1000000,  # Normalize
                features.get("traction_metrics", {}).get("employee_count", 0) / 1000,  # Normalize
                features.get("traction_metrics", {}).get("growth_rate", 0.0) / 100,  # Normalize
                features.get("traction_metrics", {}).get("market_sentiment", 0.0),
                # Add more dense features as needed
            ]
            
            # Pad to expected size
            while len(dense_features) < 13:
                dense_features.append(0.0)
            
            # Extract sparse features (categorical)
            company_id = features.get("company_id", "")
            company_hash = hash(company_id) % 100000  # Simple hash for categorical
            
            sparse_features = [company_hash] + [0] * 25  # Pad to 26 features
            
            return {
                "dense": dense_features,
                "sparse": sparse_features,
                "culture_vector": features.get("culture_vector", [0.0] * 128)
            }
            
        except Exception as e:
            logger.error(f"Feature preparation failed: {e}")
            return {
                "dense": [0.0] * 13,
                "sparse": [0] * 26,
                "culture_vector": [0.0] * 128
            }