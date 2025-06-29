from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import os
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import logging

from src.inference_engine import PartnerInferenceEngine
from src.model_manager import ModelManager
from src.feature_client import FeatureStoreClient
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    environment=os.getenv("ENVIRONMENT", "development"),
)

app = FastAPI(
    title="Synapse LaunchPad - Partner Recommender",
    description="NVIDIA Merlin HugeCTR two-tower model for startup partner matching",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
config = Config()
model_manager = ModelManager(config)
feature_client = FeatureStoreClient(config)
inference_engine = PartnerInferenceEngine(model_manager, feature_client, config)

class RecommendationRequest(BaseModel):
    company_id: str
    top_k: int = 10
    filters: Optional[Dict[str, Any]] = None
    include_scores: bool = True

class PartnerRecommendation(BaseModel):
    company_id: str
    company_name: str
    match_score: float
    confidence: float
    reasoning: Dict[str, Any]
    metadata: Dict[str, Any]

class RecommendationResponse(BaseModel):
    query_company_id: str
    recommendations: List[PartnerRecommendation]
    model_version: str
    inference_time_ms: float
    total_candidates: int

class TrainingRequest(BaseModel):
    dataset_path: str
    model_config: Dict[str, Any]
    training_params: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Initialize services and load models"""
    try:
        await feature_client.initialize()
        await model_manager.initialize()
        await inference_engine.initialize()
        logger.info("Partner Recommender service started successfully")
    except Exception as e:
        logger.error(f"Failed to start services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services"""
    try:
        await inference_engine.close()
        await feature_client.close()
        logger.info("Partner Recommender service stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    model_status = await model_manager.get_model_status()
    
    return {
        "status": "healthy",
        "service": "partner-recommender",
        "timestamp": datetime.utcnow(),
        "model_loaded": model_status["loaded"],
        "model_version": model_status["version"],
        "gpu_available": model_status["gpu_available"],
        "feature_store_connected": await feature_client.health_check()
    }

@app.post("/recommend", response_model=RecommendationResponse)
async def recommend_partners(request: RecommendationRequest):
    """
    Get partner recommendations using HugeCTR two-tower model
    """
    try:
        start_time = datetime.utcnow()
        
        # Get recommendations from inference engine
        recommendations = await inference_engine.get_recommendations(
            company_id=request.company_id,
            top_k=request.top_k,
            filters=request.filters,
            include_scores=request.include_scores
        )
        
        # Calculate inference time
        inference_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Get model info
        model_status = await model_manager.get_model_status()
        
        response = RecommendationResponse(
            query_company_id=request.company_id,
            recommendations=recommendations,
            model_version=model_status["version"],
            inference_time_ms=inference_time,
            total_candidates=len(recommendations)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Recommendation failed for {request.company_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.post("/batch-recommend")
async def batch_recommend_partners(
    company_ids: List[str],
    top_k: int = 10,
    background_tasks: BackgroundTasks = None
):
    """
    Get batch recommendations for multiple companies
    """
    try:
        if len(company_ids) > 100:
            # For large batches, process in background
            if background_tasks:
                background_tasks.add_task(
                    inference_engine.process_batch_recommendations,
                    company_ids,
                    top_k
                )
                return {
                    "status": "accepted",
                    "message": f"Batch processing started for {len(company_ids)} companies",
                    "estimated_completion": "5-10 minutes"
                }
        
        # Process smaller batches synchronously
        batch_results = await inference_engine.get_batch_recommendations(
            company_ids=company_ids,
            top_k=top_k
        )
        
        return {
            "status": "completed",
            "results": batch_results,
            "processed_count": len(batch_results)
        }
        
    except Exception as e:
        logger.error(f"Batch recommendation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch recommendation failed: {str(e)}")

@app.post("/train")
async def train_model(
    request: TrainingRequest,
    background_tasks: BackgroundTasks
):
    """
    Trigger model training with new data
    """
    try:
        # Start training in background
        background_tasks.add_task(
            model_manager.train_model,
            request.dataset_path,
            request.model_config,
            request.training_params
        )
        
        return {
            "status": "training_started",
            "dataset_path": request.dataset_path,
            "estimated_duration": "2-4 hours",
            "message": "Model training started in background"
        }
        
    except Exception as e:
        logger.error(f"Training initiation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@app.get("/model/status")
async def get_model_status():
    """
    Get current model status and metrics
    """
    try:
        status = await model_manager.get_model_status()
        metrics = await model_manager.get_model_metrics()
        
        return {
            "model_status": status,
            "performance_metrics": metrics,
            "last_updated": status.get("last_updated"),
            "training_history": await model_manager.get_training_history()
        }
        
    except Exception as e:
        logger.error(f"Failed to get model status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.post("/model/reload")
async def reload_model():
    """
    Reload the model from disk
    """
    try:
        await model_manager.reload_model()
        return {
            "status": "success",
            "message": "Model reloaded successfully",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Model reload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Model reload failed: {str(e)}")

@app.get("/explain/{company_id}")
async def explain_recommendations(
    company_id: str,
    partner_id: str,
    top_features: int = 10
):
    """
    Explain why a specific partner was recommended
    """
    try:
        explanation = await inference_engine.explain_recommendation(
            company_id=company_id,
            partner_id=partner_id,
            top_features=top_features
        )
        
        return explanation
        
    except Exception as e:
        logger.error(f"Explanation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)