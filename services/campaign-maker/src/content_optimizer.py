import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import openai
from sklearn.ensemble import RandomForestRegressor
import redis.asyncio as redis

from .config import Config

logger = logging.getLogger(__name__)

class ContentOptimizer:
    """
    Content optimization engine with Big Five personality targeting and performance prediction
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.openai_client = None
        self.redis_client = None
        self.performance_model = None
    
    async def initialize(self):
        """Initialize content optimizer"""
        try:
            # Initialize OpenAI client
            self.openai_client = openai.AsyncOpenAI(api_key=self.config.openai_api_key)
            
            # Initialize Redis for caching
            self.redis_client = redis.from_url(self.config.redis_url)
            
            # Initialize performance prediction model
            self._initialize_performance_model()
            
            logger.info("Content optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Content optimizer initialization failed: {e}")
            raise
    
    async def close(self):
        """Close connections"""
        try:
            if self.openai_client:
                await self.openai_client.close()
            if self.redis_client:
                await self.redis_client.close()
            logger.info("Content optimizer closed")
        except Exception as e:
            logger.error(f"Error closing content optimizer: {e}")
    
    async def generate_copy_variants(
        self,
        channel: str,
        campaign_brief: Dict[str, Any],
        audience_segment: Dict[str, Any],
        partner_pair: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate copy variants targeting different Big Five personality traits
        """
        try:
            # Get Big Five traits for audience
            big_five_traits = audience_segment.get('big_five_traits', {})
            
            # Determine primary traits to target
            primary_traits = self._get_primary_traits(big_five_traits)
            
            # Generate variants for each primary trait
            variants = []
            
            for trait in primary_traits[:self.config.max_copy_variants]:
                variant = await self._generate_trait_specific_copy(
                    trait=trait,
                    channel=channel,
                    campaign_brief=campaign_brief,
                    audience_segment=audience_segment,
                    partner_pair=partner_pair
                )
                
                if variant:
                    # Add performance prediction
                    variant['estimated_performance'] = await self._predict_variant_performance(
                        variant, channel, audience_segment
                    )
                    variants.append(variant)
            
            logger.info(f"Generated {len(variants)} copy variants for {channel}")
            return variants
            
        except Exception as e:
            logger.error(f"Copy variant generation failed: {e}")
            raise
    
    async def _generate_trait_specific_copy(
        self,
        trait: str,
        channel: str,
        campaign_brief: Dict[str, Any],
        audience_segment: Dict[str, Any],
        partner_pair: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate copy variant targeting specific Big Five trait
        """
        try:
            # Define trait-specific approaches
            trait_approaches = {
                "openness": {
                    "approach": "Emphasize innovation, creativity, and new possibilities",
                    "tone": "Innovative and forward-thinking",
                    "triggers": ["novelty", "innovation", "creativity", "exploration"]
                },
                "conscientiousness": {
                    "approach": "Focus on reliability, planning, and systematic benefits",
                    "tone": "Professional and structured",
                    "triggers": ["reliability", "planning", "efficiency", "results"]
                },
                "extraversion": {
                    "approach": "Highlight social benefits, networking, and collaboration",
                    "tone": "Energetic and social",
                    "triggers": ["social_proof", "networking", "collaboration", "excitement"]
                },
                "agreeableness": {
                    "approach": "Emphasize cooperation, mutual benefit, and harmony",
                    "tone": "Collaborative and supportive",
                    "triggers": ["cooperation", "mutual_benefit", "trust", "harmony"]
                },
                "neuroticism": {
                    "approach": "Address concerns, provide reassurance, and reduce uncertainty",
                    "tone": "Reassuring and supportive",
                    "triggers": ["security", "reassurance", "risk_reduction", "support"]
                }
            }
            
            trait_config = trait_approaches.get(trait, trait_approaches["conscientiousness"])
            
            # Create trait-specific prompt
            system_prompt = f"""You are an expert copywriter specializing in psychological targeting and Big Five personality traits.
            
            Create compelling copy that specifically appeals to individuals high in {trait.upper()}.
            
            Trait-specific approach: {trait_config['approach']}
            Recommended tone: {trait_config['tone']}
            Key psychological triggers: {trait_config['triggers']}
            
            Channel: {channel}
            
            Guidelines:
            - Use language and messaging that resonates with {trait} personality trait
            - Include relevant psychological triggers
            - Adapt format and length for {channel} channel
            - Create urgency while maintaining trait-appropriate tone
            - Include clear, compelling call-to-action"""
            
            user_prompt = f"""
            Create copy for a {channel} campaign targeting individuals high in {trait}.
            
            Campaign Brief:
            - Objective: {campaign_brief.get('objective', '')}
            - Key Message: {campaign_brief.get('key_message', '')}
            - FOMO Angle: {campaign_brief.get('fomo_angle', '')}
            - Psychological Triggers: {campaign_brief.get('psychological_triggers', [])}
            
            Partnership:
            - Company A: {partner_pair['company_a']['name']}
            - Company B: {partner_pair['company_b']['name']}
            - Synergies: {partner_pair.get('synergies', [])}
            
            Target Audience:
            - Segment: {audience_segment.get('segment_name', '')}
            - Messaging Preferences: {audience_segment.get('messaging_preferences', {})}
            
            Generate:
            1. Compelling headline (optimized for {trait})
            2. Body text (appropriate length for {channel})
            3. Strong call-to-action
            4. List of psychological triggers used
            5. Tone analysis scores (0-1 scale)
            """
            
            response = await self.openai_client.chat.completions.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                functions=[self.config.copy_generation_schema],
                function_call={"name": "generate_copy_variants"},
                temperature=self.config.openai_temperature,
                max_tokens=self.config.openai_max_tokens
            )
            
            function_call = response.choices[0].message.function_call
            result = json.loads(function_call.arguments)
            
            if result.get('variants'):
                variant = result['variants'][0]  # Take first variant
                variant['variant_id'] = f"{channel}_{trait}_{int(datetime.utcnow().timestamp())}"
                return variant
            
            return None
            
        except Exception as e:
            logger.error(f"Trait-specific copy generation failed for {trait}: {e}")
            return None
    
    def _get_primary_traits(self, big_five_traits: Dict[str, float]) -> List[str]:
        """
        Identify primary Big Five traits to target based on scores
        """
        if not big_five_traits:
            return ["conscientiousness", "openness", "extraversion"]  # Default traits
        
        # Sort traits by score (highest first)
        sorted_traits = sorted(
            big_five_traits.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return top traits above threshold
        primary_traits = []
        for trait, score in sorted_traits:
            if score > 0.6 and len(primary_traits) < self.config.max_copy_variants:
                primary_traits.append(trait)
        
        # Ensure we have at least one trait
        if not primary_traits:
            primary_traits = [sorted_traits[0][0]]
        
        return primary_traits
    
    async def _predict_variant_performance(
        self,
        variant: Dict[str, Any],
        channel: str,
        audience_segment: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Predict performance metrics for copy variant
        """
        try:
            # Extract features for prediction
            features = self._extract_performance_features(variant, channel, audience_segment)
            
            # Use ML model for prediction (simplified)
            if self.performance_model:
                predictions = self.performance_model.predict([features])
                
                return {
                    "click_rate": float(max(0.01, min(0.5, predictions[0] * 0.1))),
                    "engagement_rate": float(max(0.02, min(0.3, predictions[0] * 0.05))),
                    "conversion_rate": float(max(0.005, min(0.1, predictions[0] * 0.02))),
                    "confidence": float(max(0.5, min(1.0, predictions[0])))
                }
            
            # Fallback to heuristic-based prediction
            return self._heuristic_performance_prediction(variant, channel)
            
        except Exception as e:
            logger.error(f"Performance prediction failed: {e}")
            return {
                "click_rate": 0.05,
                "engagement_rate": 0.03,
                "conversion_rate": 0.01,
                "confidence": 0.5
            }
    
    def _extract_performance_features(
        self,
        variant: Dict[str, Any],
        channel: str,
        audience_segment: Dict[str, Any]
    ) -> List[float]:
        """
        Extract numerical features for performance prediction
        """
        features = []
        
        # Channel encoding
        channel_encoding = {
            "social": 0.8,
            "email": 0.9,
            "influencer": 0.7,
            "video": 0.85
        }
        features.append(channel_encoding.get(channel, 0.5))
        
        # Tone analysis features
        tone_analysis = variant.get('tone_analysis', {})
        features.extend([
            tone_analysis.get('formality', 0.5),
            tone_analysis.get('enthusiasm', 0.5),
            tone_analysis.get('urgency', 0.5),
            tone_analysis.get('trustworthiness', 0.5)
        ])
        
        # Psychological triggers count
        triggers_count = len(variant.get('psychological_triggers', []))
        features.append(min(1.0, triggers_count / 5.0))  # Normalize
        
        # Text length features
        headline_length = len(variant.get('headline', ''))
        body_length = len(variant.get('body_text', ''))
        features.extend([
            min(1.0, headline_length / 100.0),  # Normalize headline length
            min(1.0, body_length / 500.0)      # Normalize body length
        ])
        
        # Audience alignment (simplified)
        big_five_traits = audience_segment.get('big_five_traits', {})
        trait_target = variant.get('big_five_target', 'conscientiousness')
        trait_score = big_five_traits.get(trait_target, 0.5)
        features.append(trait_score)
        
        return features
    
    def _heuristic_performance_prediction(
        self,
        variant: Dict[str, Any],
        channel: str
    ) -> Dict[str, float]:
        """
        Heuristic-based performance prediction
        """
        # Base rates by channel
        base_rates = {
            "social": {"click_rate": 0.03, "engagement_rate": 0.05, "conversion_rate": 0.008},
            "email": {"click_rate": 0.08, "engagement_rate": 0.12, "conversion_rate": 0.015},
            "influencer": {"click_rate": 0.05, "engagement_rate": 0.08, "conversion_rate": 0.012},
            "video": {"click_rate": 0.06, "engagement_rate": 0.10, "conversion_rate": 0.018}
        }
        
        base = base_rates.get(channel, base_rates["email"])
        
        # Adjust based on psychological triggers
        trigger_boost = len(variant.get('psychological_triggers', [])) * 0.01
        
        # Adjust based on tone analysis
        tone_analysis = variant.get('tone_analysis', {})
        tone_boost = (
            tone_analysis.get('enthusiasm', 0.5) * 0.02 +
            tone_analysis.get('urgency', 0.5) * 0.015 +
            tone_analysis.get('trustworthiness', 0.5) * 0.01
        )
        
        return {
            "click_rate": min(0.5, base["click_rate"] + trigger_boost + tone_boost),
            "engagement_rate": min(0.3, base["engagement_rate"] + trigger_boost + tone_boost),
            "conversion_rate": min(0.1, base["conversion_rate"] + trigger_boost + tone_boost),
            "confidence": 0.7
        }
    
    def _initialize_performance_model(self):
        """
        Initialize performance prediction model
        """
        try:
            # For now, use a simple RandomForest model
            # In production, this would be trained on historical campaign data
            self.performance_model = RandomForestRegressor(
                n_estimators=100,
                random_state=42
            )
            
            # Generate synthetic training data for demonstration
            # In production, use real campaign performance data
            X_train = np.random.rand(1000, 9)  # 9 features
            y_train = np.random.rand(1000)     # Performance scores
            
            self.performance_model.fit(X_train, y_train)
            
            logger.info("Performance prediction model initialized")
            
        except Exception as e:
            logger.error(f"Performance model initialization failed: {e}")
            self.performance_model = None
    
    async def predict_performance(
        self,
        channel_content: List[Dict[str, Any]],
        audience_segment: Dict[str, Any],
        launch_window: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict overall campaign performance
        """
        try:
            channel_predictions = {}
            overall_metrics = {
                "total_reach": 0,
                "total_engagement": 0,
                "total_conversions": 0,
                "roi_estimate": 0.0
            }
            
            for content in channel_content:
                channel = content['channel']
                variants = content.get('copy_variants', [])
                
                if variants:
                    # Use best performing variant for channel prediction
                    best_variant = max(
                        variants,
                        key=lambda v: v.get('estimated_performance', {}).get('conversion_rate', 0)
                    )
                    
                    performance = best_variant.get('estimated_performance', {})
                    
                    # Estimate reach based on channel and audience
                    estimated_reach = self._estimate_channel_reach(channel, audience_segment)
                    
                    channel_predictions[channel] = {
                        "estimated_reach": estimated_reach,
                        "click_rate": performance.get('click_rate', 0.05),
                        "engagement_rate": performance.get('engagement_rate', 0.03),
                        "conversion_rate": performance.get('conversion_rate', 0.01),
                        "estimated_clicks": int(estimated_reach * performance.get('click_rate', 0.05)),
                        "estimated_conversions": int(estimated_reach * performance.get('conversion_rate', 0.01))
                    }
                    
                    # Add to overall metrics
                    overall_metrics["total_reach"] += estimated_reach
                    overall_metrics["total_engagement"] += int(estimated_reach * performance.get('engagement_rate', 0.03))
                    overall_metrics["total_conversions"] += int(estimated_reach * performance.get('conversion_rate', 0.01))
            
            # Calculate ROI estimate
            overall_metrics["roi_estimate"] = self._calculate_roi_estimate(overall_metrics)
            
            return {
                "channel_predictions": channel_predictions,
                "overall_metrics": overall_metrics,
                "confidence_level": 0.75,
                "prediction_date": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Performance prediction failed: {e}")
            return {}
    
    def _estimate_channel_reach(self, channel: str, audience_segment: Dict[str, Any]) -> int:
        """
        Estimate potential reach for a channel
        """
        # Base reach estimates (would be based on actual audience data)
        base_reach = {
            "social": 50000,
            "email": 10000,
            "influencer": 25000,
            "video": 15000
        }
        
        # Adjust based on audience preferences
        preferred_channels = audience_segment.get('preferred_channels', [])
        if channel in preferred_channels:
            multiplier = 1.5
        else:
            multiplier = 0.8
        
        return int(base_reach.get(channel, 10000) * multiplier)
    
    def _calculate_roi_estimate(self, metrics: Dict[str, Any]) -> float:
        """
        Calculate estimated ROI
        """
        # Simplified ROI calculation
        # In production, this would consider actual costs and revenue per conversion
        conversions = metrics.get("total_conversions", 0)
        reach = metrics.get("total_reach", 1)
        
        # Assume $100 revenue per conversion and $0.50 cost per reach
        estimated_revenue = conversions * 100
        estimated_cost = reach * 0.50
        
        if estimated_cost > 0:
            roi = (estimated_revenue - estimated_cost) / estimated_cost
            return round(roi, 2)
        
        return 0.0
    
    async def optimize_based_on_performance(
        self,
        campaign_id: str,
        channel: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize content based on actual performance data
        """
        try:
            # Analyze performance gaps
            actual_performance = performance_data
            
            # Generate optimization recommendations
            optimizations = {
                "recommendations": [],
                "new_variants": [],
                "budget_reallocation": {},
                "timing_adjustments": {}
            }
            
            # Performance-based recommendations
            if actual_performance.get('click_rate', 0) < 0.03:
                optimizations["recommendations"].append({
                    "type": "headline_optimization",
                    "description": "Improve headline to increase click-through rate",
                    "priority": "high"
                })
            
            if actual_performance.get('conversion_rate', 0) < 0.01:
                optimizations["recommendations"].append({
                    "type": "cta_optimization",
                    "description": "Strengthen call-to-action to improve conversions",
                    "priority": "high"
                })
            
            # Cache optimizations for future reference
            cache_key = f"optimizations:{campaign_id}:{channel}"
            await self.redis_client.setex(
                cache_key,
                3600,  # 1 hour TTL
                json.dumps(optimizations, default=str)
            )
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Performance-based optimization failed: {e}")
            return {}
    
    async def generate_optimization_recommendations(
        self,
        campaign_brief: Dict[str, Any],
        channel_content: List[Dict[str, Any]],
        performance_predictions: Dict[str, Any]
    ) -> List[str]:
        """
        Generate optimization recommendations for the campaign
        """
        try:
            recommendations = []
            
            # Analyze channel performance predictions
            channel_predictions = performance_predictions.get('channel_predictions', {})
            
            for channel, prediction in channel_predictions.items():
                click_rate = prediction.get('click_rate', 0)
                conversion_rate = prediction.get('conversion_rate', 0)
                
                if click_rate < 0.05:
                    recommendations.append(
                        f"Consider A/B testing different headlines for {channel} to improve click-through rate"
                    )
                
                if conversion_rate < 0.015:
                    recommendations.append(
                        f"Strengthen the call-to-action in {channel} content to boost conversions"
                    )
            
            # Overall campaign recommendations
            total_conversions = performance_predictions.get('overall_metrics', {}).get('total_conversions', 0)
            
            if total_conversions < 100:
                recommendations.append(
                    "Consider expanding to additional channels or increasing budget allocation to top-performing channels"
                )
            
            # Psychological optimization recommendations
            recommendations.extend([
                "Implement sequential messaging to build trust before asking for action",
                "Use social proof elements to increase credibility",
                "Create urgency with limited-time partnership benefits",
                "Personalize content based on company size and industry"
            ])
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendations generation failed: {e}")
            return []