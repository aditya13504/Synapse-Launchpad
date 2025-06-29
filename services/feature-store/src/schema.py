from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import numpy as np

class TractionMetrics(BaseModel):
    """Traction metrics for a company"""
    funding_amount: float = Field(ge=0, description="Total funding amount in USD")
    employee_count: int = Field(ge=0, description="Number of employees")
    growth_rate: float = Field(description="Growth rate percentage")
    market_sentiment: float = Field(ge=-1.0, le=1.0, description="Market sentiment score")
    revenue_growth: Optional[float] = Field(None, description="Revenue growth rate")
    user_growth: Optional[float] = Field(None, description="User growth rate")

class CompanyFeatures(BaseModel):
    """Complete feature set for a company"""
    company_id: str = Field(description="Unique company identifier")
    user_overlap_score: float = Field(ge=0.0, le=1.0, description="User overlap score with other companies")
    traction_metrics: TractionMetrics = Field(description="Company traction metrics")
    culture_vector: List[float] = Field(description="Culture embedding vector", min_items=128, max_items=128)
    match_outcome: Optional[int] = Field(None, description="Match outcome label (0/1)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Feature timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FeatureRequest(BaseModel):
    """Request for feature retrieval"""
    company_ids: List[str] = Field(description="List of company IDs to retrieve features for")
    feature_names: Optional[List[str]] = Field(None, description="Specific features to retrieve")
    as_of_time: Optional[datetime] = Field(None, description="Point-in-time for feature retrieval")

class FeatureResponse(BaseModel):
    """Response containing features"""
    features: List[CompanyFeatures] = Field(description="Retrieved features")
    metadata: Dict[str, Any] = Field(description="Response metadata")

class BatchFeatureRequest(BaseModel):
    """Request for batch feature processing"""
    start_time: datetime = Field(description="Start time for batch processing")
    end_time: datetime = Field(description="End time for batch processing")
    company_filter: Optional[List[str]] = Field(None, description="Filter by specific companies")

class PipelineStatus(BaseModel):
    """Status of the feature pipeline"""
    status: str = Field(description="Pipeline status")
    last_run: Optional[datetime] = Field(None, description="Last successful run")
    next_run: Optional[datetime] = Field(None, description="Next scheduled run")
    processed_events: int = Field(description="Number of events processed in last run")
    error_message: Optional[str] = Field(None, description="Error message if failed")

class FeatureStats(BaseModel):
    """Statistics about features in the store"""
    total_companies: int = Field(description="Total number of companies with features")
    feature_count: int = Field(description="Total number of feature records")
    last_updated: datetime = Field(description="Last update timestamp")
    storage_size_mb: float = Field(description="Storage size in MB")
    avg_culture_vector_norm: float = Field(description="Average norm of culture vectors")

class OnlineFeatureRequest(BaseModel):
    """Request for online feature serving"""
    company_id: str = Field(description="Company ID for feature lookup")
    feature_view: str = Field(description="Feature view name")
    
class OnlineFeatureResponse(BaseModel):
    """Response for online feature serving"""
    company_id: str = Field(description="Company ID")
    features: Dict[str, Any] = Field(description="Feature values")
    timestamp: datetime = Field(description="Feature timestamp")
    ttl_seconds: int = Field(description="Time to live in seconds")