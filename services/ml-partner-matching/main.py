from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import os
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from pydantic import BaseModel

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    environment=os.getenv("ENVIRONMENT", "development"),
)

app = FastAPI(
    title="Synapse LaunchPad - Partner Matching Service",
    description="AI-powered partner matching using NVIDIA Merlin and behavioral science",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompanyProfile(BaseModel):
    id: str
    name: str
    industry: str
    stage: str
    funding_amount: float
    employee_count: int
    technologies: List[str]
    target_market: List[str]
    business_model: str
    growth_rate: float
    location: str

class MatchRequest(BaseModel):
    company_profile: CompanyProfile
    preferences: Dict[str, Any]
    limit: int = 10

class MatchResult(BaseModel):
    company_id: str
    company_name: str
    match_score: float
    compatibility_factors: Dict[str, float]
    timing_score: float
    behavioral_alignment: float

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ml-partner-matching"}

@app.post("/match", response_model=List[MatchResult])
async def find_matches(request: MatchRequest):
    """
    Find potential startup partners using AI-powered matching algorithm
    """
    try:
        # Mock implementation - replace with actual NVIDIA Merlin model
        matches = []
        
        # Simulate partner matching logic
        mock_partners = [
            {
                "company_id": "tech_flow_ai",
                "company_name": "TechFlow AI",
                "match_score": 96.5,
                "compatibility_factors": {
                    "industry_alignment": 0.95,
                    "stage_compatibility": 0.92,
                    "technology_overlap": 0.88,
                    "market_synergy": 0.94
                },
                "timing_score": 0.91,
                "behavioral_alignment": 0.89
            },
            {
                "company_id": "green_start",
                "company_name": "GreenStart Solutions",
                "match_score": 94.2,
                "compatibility_factors": {
                    "industry_alignment": 0.87,
                    "stage_compatibility": 0.95,
                    "technology_overlap": 0.82,
                    "market_synergy": 0.91
                },
                "timing_score": 0.88,
                "behavioral_alignment": 0.92
            }
        ]
        
        for partner in mock_partners[:request.limit]:
            matches.append(MatchResult(**partner))
        
        return matches
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Matching failed: {str(e)}")

@app.post("/analyze-timing")
async def analyze_market_timing(company_profile: CompanyProfile):
    """
    Analyze optimal timing for partnerships based on market conditions
    """
    try:
        # Mock timing analysis
        timing_analysis = {
            "optimal_timing_score": 0.87,
            "market_conditions": {
                "funding_climate": 0.82,
                "industry_momentum": 0.91,
                "competitive_landscape": 0.79
            },
            "recommended_action": "Initiate partnerships within next 30 days",
            "confidence_level": 0.89
        }
        
        return timing_analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timing analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)