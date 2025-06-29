from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
import os
import asyncio
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging

from src.campaign_generator import CampaignGenerator
from src.content_optimizer import ContentOptimizer
from src.external_apis import PicaClient, TavusClient, LingoClient
from src.psychology_engine import PsychologyEngine
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
    title="Synapse LaunchPad - Campaign Maker",
    description="AI-powered campaign generation with psychological optimization and multi-channel content creation",
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
campaign_generator = CampaignGenerator(config)
content_optimizer = ContentOptimizer(config)
psychology_engine = PsychologyEngine(config)

# External API clients
pica_client = PicaClient(config)
tavus_client = TavusClient(config)
lingo_client = LingoClient(config)

class PartnerPair(BaseModel):
    company_a: Dict[str, Any]
    company_b: Dict[str, Any]
    match_score: float
    synergies: List[str]

class LaunchWindow(BaseModel):
    start_date: datetime
    end_date: datetime
    optimal_timing: str
    market_conditions: Dict[str, Any]

class AudienceSegment(BaseModel):
    segment_name: str
    demographics: Dict[str, Any]
    psychographics: Dict[str, Any]
    big_five_traits: Dict[str, float]
    preferred_channels: List[str]
    messaging_preferences: Dict[str, Any]

class CampaignRequest(BaseModel):
    partner_pair: PartnerPair
    launch_window: LaunchWindow
    audience_segment: AudienceSegment
    campaign_objectives: List[str]
    budget_range: Optional[Dict[str, float]] = None
    brand_guidelines: Optional[Dict[str, Any]] = None
    localization_targets: Optional[List[str]] = None

class CampaignBrief(BaseModel):
    objective: str
    key_message: str
    hooks: List[str]
    fomo_angle: str
    psychological_triggers: List[str]
    success_metrics: List[str]

class ChannelMixPlan(BaseModel):
    channel: str
    allocation_percentage: float
    rationale: str
    optimal_timing: str
    content_types: List[str]
    psychological_approach: str

class CopyVariant(BaseModel):
    variant_id: str
    big_five_target: str
    headline: str
    body_text: str
    cta: str
    psychological_triggers: List[str]
    tone_analysis: Dict[str, float]
    estimated_performance: Dict[str, float]

class ChannelContent(BaseModel):
    channel: str
    content_type: str
    copy_variants: List[CopyVariant]
    creative_assets: List[Dict[str, Any]]
    localized_versions: Optional[Dict[str, Any]] = None

class CampaignResponse(BaseModel):
    campaign_id: str
    campaign_brief: CampaignBrief
    channel_mix_plan: List[ChannelMixPlan]
    channel_content: List[ChannelContent]
    psychological_insights: Dict[str, Any]
    performance_predictions: Dict[str, Any]
    optimization_recommendations: List[str]
    created_at: datetime

@app.on_event("startup")
async def startup_event():
    """Initialize services"""
    try:
        await campaign_generator.initialize()
        await content_optimizer.initialize()
        await psychology_engine.initialize()
        
        # Initialize external API clients
        await pica_client.initialize()
        await tavus_client.initialize()
        await lingo_client.initialize()
        
        logger.info("Campaign Maker service started successfully")
    except Exception as e:
        logger.error(f"Failed to start services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup services"""
    try:
        await campaign_generator.close()
        await content_optimizer.close()
        await psychology_engine.close()
        
        await pica_client.close()
        await tavus_client.close()
        await lingo_client.close()
        
        logger.info("Campaign Maker service stopped")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "campaign-maker",
        "timestamp": datetime.utcnow(),
        "openai_connected": await campaign_generator.health_check(),
        "external_apis": {
            "pica": await pica_client.health_check(),
            "tavus": await tavus_client.health_check(),
            "lingo": await lingo_client.health_check()
        }
    }

@app.post("/generate-campaign", response_model=CampaignResponse)
async def generate_campaign(request: CampaignRequest):
    """
    Generate a complete marketing campaign with psychological optimization
    """
    try:
        campaign_id = f"campaign_{int(datetime.utcnow().timestamp())}"
        
        logger.info(f"Generating campaign {campaign_id} for {request.partner_pair.company_a['name']} x {request.partner_pair.company_b['name']}")
        
        # Step 1: Generate campaign brief using GPT-4o
        campaign_brief = await campaign_generator.generate_campaign_brief(
            partner_pair=request.partner_pair,
            launch_window=request.launch_window,
            audience_segment=request.audience_segment,
            objectives=request.campaign_objectives
        )
        
        # Step 2: Create channel mix plan
        channel_mix_plan = await campaign_generator.generate_channel_mix_plan(
            campaign_brief=campaign_brief,
            audience_segment=request.audience_segment,
            budget_range=request.budget_range
        )
        
        # Step 3: Generate content for each channel
        channel_content = []
        
        for channel_plan in channel_mix_plan:
            # Generate copy variants targeting different Big Five traits
            copy_variants = await content_optimizer.generate_copy_variants(
                channel=channel_plan.channel,
                campaign_brief=campaign_brief,
                audience_segment=request.audience_segment,
                partner_pair=request.partner_pair
            )
            
            # Generate creative assets
            creative_assets = await _generate_creative_assets(
                channel=channel_plan.channel,
                copy_variants=copy_variants,
                partner_pair=request.partner_pair
            )
            
            # Generate localized versions if requested
            localized_versions = None
            if request.localization_targets:
                localized_versions = await lingo_client.localize_content(
                    copy_variants=copy_variants,
                    target_languages=request.localization_targets,
                    cultural_adaptations=True
                )
            
            channel_content.append(ChannelContent(
                channel=channel_plan.channel,
                content_type=channel_plan.content_types[0],  # Primary content type
                copy_variants=copy_variants,
                creative_assets=creative_assets,
                localized_versions=localized_versions
            ))
        
        # Step 4: Generate psychological insights
        psychological_insights = await psychology_engine.analyze_campaign_psychology(
            campaign_brief=campaign_brief,
            channel_content=channel_content,
            audience_segment=request.audience_segment
        )
        
        # Step 5: Predict performance
        performance_predictions = await content_optimizer.predict_performance(
            channel_content=channel_content,
            audience_segment=request.audience_segment,
            launch_window=request.launch_window
        )
        
        # Step 6: Generate optimization recommendations
        optimization_recommendations = await content_optimizer.generate_optimization_recommendations(
            campaign_brief=campaign_brief,
            channel_content=channel_content,
            performance_predictions=performance_predictions
        )
        
        # Create response
        response = CampaignResponse(
            campaign_id=campaign_id,
            campaign_brief=campaign_brief,
            channel_mix_plan=channel_mix_plan,
            channel_content=channel_content,
            psychological_insights=psychological_insights,
            performance_predictions=performance_predictions,
            optimization_recommendations=optimization_recommendations,
            created_at=datetime.utcnow()
        )
        
        logger.info(f"Campaign {campaign_id} generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Campaign generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Campaign generation failed: {str(e)}")

@app.post("/optimize-content")
async def optimize_content(
    campaign_id: str,
    channel: str,
    performance_data: Dict[str, Any]
):
    """
    Optimize existing campaign content based on performance data
    """
    try:
        optimizations = await content_optimizer.optimize_based_on_performance(
            campaign_id=campaign_id,
            channel=channel,
            performance_data=performance_data
        )
        
        return {
            "campaign_id": campaign_id,
            "channel": channel,
            "optimizations": optimizations,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Content optimization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.post("/generate-creative-assets")
async def generate_creative_assets(
    content_brief: Dict[str, Any],
    asset_types: List[str],
    dimensions: List[Dict[str, int]]
):
    """
    Generate creative assets using external APIs
    """
    try:
        assets = await _generate_creative_assets_standalone(
            content_brief=content_brief,
            asset_types=asset_types,
            dimensions=dimensions
        )
        
        return {
            "assets": assets,
            "generated_at": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Creative asset generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Asset generation failed: {str(e)}")

@app.get("/psychology-insights/{audience_segment}")
async def get_psychology_insights(audience_segment: str):
    """
    Get psychological insights for a specific audience segment
    """
    try:
        insights = await psychology_engine.get_segment_insights(audience_segment)
        return insights
        
    except Exception as e:
        logger.error(f"Psychology insights failed: {e}")
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")

async def _generate_creative_assets(
    channel: str,
    copy_variants: List[CopyVariant],
    partner_pair: PartnerPair
) -> List[Dict[str, Any]]:
    """
    Generate creative assets for a specific channel
    """
    assets = []
    
    try:
        if channel == "social":
            # Generate social media images
            for variant in copy_variants[:2]:  # Top 2 variants
                # Generate image using Pica
                image_asset = await pica_client.generate_social_image(
                    headline=variant.headline,
                    company_a=partner_pair.company_a["name"],
                    company_b=partner_pair.company_b["name"],
                    style="modern_partnership",
                    dimensions={"width": 1200, "height": 630}
                )
                
                assets.append({
                    "type": "image",
                    "variant_id": variant.variant_id,
                    "url": image_asset["url"],
                    "dimensions": image_asset["dimensions"],
                    "format": "png"
                })
        
        elif channel == "email":
            # Generate email header images
            header_image = await pica_client.generate_email_header(
                company_a=partner_pair.company_a["name"],
                company_b=partner_pair.company_b["name"],
                theme="partnership_announcement",
                dimensions={"width": 600, "height": 200}
            )
            
            assets.append({
                "type": "email_header",
                "url": header_image["url"],
                "dimensions": header_image["dimensions"],
                "format": "png"
            })
        
        elif channel == "video":
            # Generate personalized video placeholders using Tavus
            for variant in copy_variants[:1]:  # Top variant only
                video_placeholder = await tavus_client.create_video_placeholder(
                    script=variant.body_text,
                    company_a=partner_pair.company_a["name"],
                    company_b=partner_pair.company_b["name"],
                    style="professional_announcement"
                )
                
                assets.append({
                    "type": "video_placeholder",
                    "variant_id": variant.variant_id,
                    "placeholder_url": video_placeholder["placeholder_url"],
                    "script": video_placeholder["script"],
                    "duration_estimate": video_placeholder["duration_estimate"]
                })
        
        return assets
        
    except Exception as e:
        logger.error(f"Creative asset generation failed for {channel}: {e}")
        return []

async def _generate_creative_assets_standalone(
    content_brief: Dict[str, Any],
    asset_types: List[str],
    dimensions: List[Dict[str, int]]
) -> List[Dict[str, Any]]:
    """
    Generate creative assets standalone
    """
    assets = []
    
    try:
        for asset_type in asset_types:
            for dimension in dimensions:
                if asset_type == "image":
                    asset = await pica_client.generate_image(
                        brief=content_brief,
                        dimensions=dimension,
                        style="professional"
                    )
                elif asset_type == "video":
                    asset = await tavus_client.create_video_placeholder(
                        script=content_brief.get("script", ""),
                        style="professional"
                    )
                else:
                    continue
                
                assets.append(asset)
        
        return assets
        
    except Exception as e:
        logger.error(f"Standalone asset generation failed: {e}")
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)