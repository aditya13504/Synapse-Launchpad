import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks import get_openai_callback

from .config import Config

logger = logging.getLogger(__name__)

class CampaignGenerator:
    """
    AI-powered campaign generation using OpenAI GPT-4o with function calling
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.llm = None
        self.openai_client = None
    
    async def initialize(self):
        """Initialize OpenAI clients"""
        try:
            # Initialize OpenAI client
            openai.api_key = self.config.openai_api_key
            self.openai_client = openai.AsyncOpenAI(api_key=self.config.openai_api_key)
            
            # Initialize LangChain ChatOpenAI
            self.llm = ChatOpenAI(
                model=self.config.openai_model,
                temperature=self.config.openai_temperature,
                max_tokens=self.config.openai_max_tokens,
                openai_api_key=self.config.openai_api_key
            )
            
            logger.info("Campaign generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Campaign generator initialization failed: {e}")
            raise
    
    async def close(self):
        """Close connections"""
        try:
            if self.openai_client:
                await self.openai_client.close()
            logger.info("Campaign generator closed")
        except Exception as e:
            logger.error(f"Error closing campaign generator: {e}")
    
    async def health_check(self) -> bool:
        """Check OpenAI API health"""
        try:
            if not self.openai_client:
                return False
            
            # Simple API test
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return bool(response.choices)
            
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False
    
    async def generate_campaign_brief(
        self,
        partner_pair: Dict[str, Any],
        launch_window: Dict[str, Any],
        audience_segment: Dict[str, Any],
        objectives: List[str]
    ) -> Dict[str, Any]:
        """
        Generate campaign brief using GPT-4o function calling
        """
        try:
            # Prepare context for GPT-4o
            context = self._prepare_campaign_context(
                partner_pair, launch_window, audience_segment, objectives
            )
            
            # Create function calling prompt
            system_prompt = """You are an expert marketing strategist specializing in B2B partnership campaigns. 
            You understand psychological triggers, behavioral science, and how to create compelling campaigns that drive action.
            
            Generate a comprehensive campaign brief that leverages psychological insights and creates urgency through FOMO.
            Consider the partner companies' synergies, target audience psychology, and optimal timing."""
            
            user_prompt = f"""
            Create a campaign brief for a partnership announcement between {partner_pair['company_a']['name']} and {partner_pair['company_b']['name']}.
            
            Context:
            {context}
            
            Focus on:
            1. Clear, compelling objective that highlights partnership value
            2. Key message that resonates with the target audience's pain points
            3. Multiple hooks for different channels and psychological triggers
            4. Strong FOMO angle that creates urgency
            5. Psychological triggers based on audience segment analysis
            6. Measurable success metrics
            """
            
            # Call GPT-4o with function calling
            response = await self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=[self.config.campaign_brief_schema],
                function_call={"name": "generate_campaign_brief"},
                temperature=self.config.openai_temperature,
                max_tokens=self.config.openai_max_tokens
            )
            
            # Extract function call result
            function_call = response.choices[0].message.function_call
            campaign_brief = json.loads(function_call.arguments)
            
            logger.info(f"Generated campaign brief with {len(campaign_brief['hooks'])} hooks")
            return campaign_brief
            
        except Exception as e:
            logger.error(f"Campaign brief generation failed: {e}")
            raise
    
    async def generate_channel_mix_plan(
        self,
        campaign_brief: Dict[str, Any],
        audience_segment: Dict[str, Any],
        budget_range: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate optimal channel mix plan
        """
        try:
            # Prepare context
            context = f"""
            Campaign Brief: {json.dumps(campaign_brief, indent=2)}
            
            Audience Segment:
            - Demographics: {audience_segment.get('demographics', {})}
            - Psychographics: {audience_segment.get('psychographics', {})}
            - Big Five Traits: {audience_segment.get('big_five_traits', {})}
            - Preferred Channels: {audience_segment.get('preferred_channels', [])}
            
            Budget Range: {budget_range or 'Not specified'}
            """
            
            system_prompt = """You are a media planning expert who understands channel effectiveness, audience behavior, and psychological targeting.
            
            Create an optimal channel mix plan that maximizes reach and engagement while considering:
            - Audience channel preferences and behavior
            - Psychological triggers for each channel
            - Budget efficiency and ROI potential
            - Timing optimization for maximum impact
            - Content type suitability for each channel"""
            
            user_prompt = f"""
            Create a channel mix plan for this campaign:
            
            {context}
            
            Consider these channels: social media, email marketing, influencer partnerships, personalized video (Tavus).
            
            For each recommended channel, provide:
            1. Budget allocation percentage
            2. Strategic rationale
            3. Optimal timing within the launch window
            4. Recommended content types
            5. Psychological approach for that channel
            """
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=[self.config.channel_mix_schema],
                function_call={"name": "generate_channel_mix_plan"},
                temperature=self.config.openai_temperature,
                max_tokens=self.config.openai_max_tokens
            )
            
            function_call = response.choices[0].message.function_call
            channel_mix = json.loads(function_call.arguments)
            
            logger.info(f"Generated channel mix plan with {len(channel_mix['channels'])} channels")
            return channel_mix['channels']
            
        except Exception as e:
            logger.error(f"Channel mix generation failed: {e}")
            raise
    
    def _prepare_campaign_context(
        self,
        partner_pair: Dict[str, Any],
        launch_window: Dict[str, Any],
        audience_segment: Dict[str, Any],
        objectives: List[str]
    ) -> str:
        """
        Prepare comprehensive context for campaign generation
        """
        context = f"""
        PARTNERSHIP DETAILS:
        Company A: {partner_pair['company_a']['name']}
        - Industry: {partner_pair['company_a'].get('industry', 'Not specified')}
        - Stage: {partner_pair['company_a'].get('stage', 'Not specified')}
        - Key Strengths: {partner_pair['company_a'].get('strengths', [])}
        
        Company B: {partner_pair['company_b']['name']}
        - Industry: {partner_pair['company_b'].get('industry', 'Not specified')}
        - Stage: {partner_pair['company_b'].get('stage', 'Not specified')}
        - Key Strengths: {partner_pair['company_b'].get('strengths', [])}
        
        Partnership Synergies: {partner_pair.get('synergies', [])}
        Match Score: {partner_pair.get('match_score', 0)}/1.0
        
        LAUNCH TIMING:
        Launch Window: {launch_window.get('start_date')} to {launch_window.get('end_date')}
        Optimal Timing: {launch_window.get('optimal_timing', 'Not specified')}
        Market Conditions: {launch_window.get('market_conditions', {})}
        
        TARGET AUDIENCE:
        Segment: {audience_segment.get('segment_name', 'Not specified')}
        Demographics: {audience_segment.get('demographics', {})}
        Psychographics: {audience_segment.get('psychographics', {})}
        Big Five Personality Traits: {audience_segment.get('big_five_traits', {})}
        Preferred Channels: {audience_segment.get('preferred_channels', [])}
        Messaging Preferences: {audience_segment.get('messaging_preferences', {})}
        
        CAMPAIGN OBJECTIVES:
        {', '.join(objectives)}
        """
        
        return context