from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import openai

# Initialize Sentry
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    environment=os.getenv("ENVIRONMENT", "development"),
)

app = FastAPI(
    title="Synapse LaunchPad - Campaign Generator Service",
    description="AI-powered campaign generation with psychological optimization",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class CampaignRequest(BaseModel):
    objective: str
    target_audience: str
    tone: str
    channels: List[str]
    company_info: Dict[str, Any]
    partner_info: Optional[Dict[str, Any]] = None
    psychological_triggers: List[str] = []

class CampaignContent(BaseModel):
    channel: str
    content_type: str
    subject_line: Optional[str] = None
    content: str
    psychological_triggers: List[str]
    estimated_performance: Dict[str, float]

class CampaignResponse(BaseModel):
    campaign_id: str
    contents: List[CampaignContent]
    overall_strategy: str
    behavioral_insights: Dict[str, Any]
    optimization_suggestions: List[str]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ml-campaign-generator"}

@app.post("/generate", response_model=CampaignResponse)
async def generate_campaign(request: CampaignRequest):
    """
    Generate psychologically-optimized marketing campaigns
    """
    try:
        # Mock implementation - replace with actual AI generation
        campaign_contents = []
        
        if "email" in request.channels:
            email_content = CampaignContent(
                channel="email",
                content_type="partnership_announcement",
                subject_line="Revolutionary AI Partnership Opportunity - Transform Your Growth Strategy",
                content="""Hi [Name],

I hope this message finds you well. I'm reaching out because our AI analysis has identified your company as an ideal strategic partner for an exciting collaboration opportunity.

At Synapse LaunchPad, we've developed breakthrough technology that combines real-time market intelligence with behavioral psychology to create unprecedented partnership success rates. Our platform has helped over 500 startups achieve 3.2x ROI improvement through strategic partnerships.

Here's why this partnership could be transformative for both our companies:

🎯 Perfect Timing: Our market pulse scanner indicates optimal conditions for your industry
🧠 Behavioral Insights: Psychographic profiling shows 94% audience alignment
📈 Proven Results: Our partners see average growth of 145% within 6 months

I'd love to schedule a brief 15-minute call to explore how we can accelerate each other's growth. Our AI has already generated a preliminary partnership strategy that I think you'll find compelling.

Are you available for a quick call this week?

Best regards,
[Your Name]

P.S. I've attached a personalized market analysis report that shows the specific opportunities we've identified for your company.""",
                psychological_triggers=["scarcity", "social_proof", "authority", "urgency", "reciprocity"],
                estimated_performance={
                    "open_rate": 0.34,
                    "click_rate": 0.12,
                    "response_rate": 0.08
                }
            )
            campaign_contents.append(email_content)
        
        if "social" in request.channels:
            social_content = CampaignContent(
                channel="social_media",
                content_type="partnership_announcement",
                content="🚀 Excited to announce our strategic partnership with [Partner Company]! Together, we're revolutionizing how startups discover and execute growth opportunities. Our AI-powered platform combines real-time market data with behavioral science to deliver unprecedented results. #StartupGrowth #AI #Partnerships",
                psychological_triggers=["social_proof", "excitement", "innovation"],
                estimated_performance={
                    "engagement_rate": 0.08,
                    "reach_amplification": 2.3,
                    "conversion_rate": 0.05
                }
            )
            campaign_contents.append(social_content)
        
        response = CampaignResponse(
            campaign_id=f"campaign_{hash(str(request.dict()))}",
            contents=campaign_contents,
            overall_strategy="Multi-channel partnership announcement leveraging authority, social proof, and urgency triggers to maximize engagement and conversion.",
            behavioral_insights={
                "primary_motivation": "Growth and competitive advantage",
                "decision_factors": ["ROI potential", "timing", "credibility"],
                "emotional_triggers": ["FOMO", "aspiration", "trust"],
                "optimal_timing": "Tuesday-Thursday, 2-4 PM"
            },
            optimization_suggestions=[
                "A/B test subject lines with different urgency levels",
                "Personalize industry-specific benefits",
                "Include video testimonials for higher engagement",
                "Follow up with behavioral retargeting campaigns"
            ]
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {str(e)}")

@app.post("/optimize")
async def optimize_campaign(campaign_id: str, performance_data: Dict[str, Any]):
    """
    Optimize campaign based on performance data and behavioral insights
    """
    try:
        optimization_results = {
            "campaign_id": campaign_id,
            "improvements": {
                "subject_line_variants": [
                    "🚀 Partnership Alert: 3.2x ROI Opportunity Inside",
                    "Limited Time: Strategic Partnership Proposal",
                    "[Company Name] + [Your Company] = Exponential Growth"
                ],
                "content_adjustments": [
                    "Increase urgency in CTA",
                    "Add more specific metrics",
                    "Include social proof elements"
                ],
                "timing_optimization": {
                    "best_send_time": "Tuesday 2:30 PM",
                    "follow_up_sequence": ["Day 3", "Day 7", "Day 14"]
                }
            },
            "predicted_improvement": {
                "open_rate": "+15%",
                "click_rate": "+23%",
                "conversion_rate": "+18%"
            }
        }
        
        return optimization_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign optimization failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)