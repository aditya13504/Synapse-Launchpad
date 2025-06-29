import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

from .config import Config

logger = logging.getLogger(__name__)

class PsychologyEngine:
    """
    Psychology engine for analyzing and optimizing campaign psychology
    """
    
    def __init__(self, config: Config):
        self.config = config
        
        # Psychological frameworks and models
        self.big_five_profiles = self._initialize_big_five_profiles()
        self.psychological_triggers = self._initialize_psychological_triggers()
        self.persuasion_principles = self._initialize_persuasion_principles()
    
    async def initialize(self):
        """Initialize psychology engine"""
        try:
            logger.info("Psychology engine initialized successfully")
        except Exception as e:
            logger.error(f"Psychology engine initialization failed: {e}")
            raise
    
    async def close(self):
        """Close psychology engine"""
        try:
            logger.info("Psychology engine closed")
        except Exception as e:
            logger.error(f"Error closing psychology engine: {e}")
    
    def _initialize_big_five_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize Big Five personality trait profiles
        """
        return {
            "openness": {
                "characteristics": [
                    "Creative and imaginative",
                    "Open to new experiences",
                    "Intellectually curious",
                    "Appreciates art and beauty",
                    "Values independence"
                ],
                "messaging_preferences": {
                    "tone": "innovative, creative, forward-thinking",
                    "content_style": "visually appealing, novel concepts",
                    "triggers": ["novelty", "creativity", "innovation", "exploration"],
                    "avoid": ["routine", "conventional", "restrictive"]
                },
                "decision_factors": [
                    "Uniqueness of opportunity",
                    "Innovation potential",
                    "Creative possibilities",
                    "Learning opportunities"
                ]
            },
            "conscientiousness": {
                "characteristics": [
                    "Organized and disciplined",
                    "Goal-oriented",
                    "Reliable and responsible",
                    "Plans ahead",
                    "Values achievement"
                ],
                "messaging_preferences": {
                    "tone": "professional, structured, results-focused",
                    "content_style": "detailed, organized, step-by-step",
                    "triggers": ["efficiency", "results", "planning", "reliability"],
                    "avoid": ["chaos", "uncertainty", "impulsiveness"]
                },
                "decision_factors": [
                    "Clear ROI and metrics",
                    "Structured implementation plan",
                    "Risk mitigation strategies",
                    "Long-term benefits"
                ]
            },
            "extraversion": {
                "characteristics": [
                    "Outgoing and social",
                    "Energetic and assertive",
                    "Enjoys interaction",
                    "Optimistic",
                    "Seeks stimulation"
                ],
                "messaging_preferences": {
                    "tone": "energetic, social, enthusiastic",
                    "content_style": "interactive, social proof, testimonials",
                    "triggers": ["social_proof", "networking", "collaboration", "excitement"],
                    "avoid": ["isolation", "solitary", "quiet"]
                },
                "decision_factors": [
                    "Social benefits",
                    "Networking opportunities",
                    "Team collaboration",
                    "Public recognition"
                ]
            },
            "agreeableness": {
                "characteristics": [
                    "Cooperative and trusting",
                    "Empathetic",
                    "Values harmony",
                    "Helpful and supportive",
                    "Avoids conflict"
                ],
                "messaging_preferences": {
                    "tone": "collaborative, supportive, harmonious",
                    "content_style": "cooperative benefits, mutual gains",
                    "triggers": ["cooperation", "mutual_benefit", "trust", "harmony"],
                    "avoid": ["conflict", "competition", "aggression"]
                },
                "decision_factors": [
                    "Mutual benefits",
                    "Positive relationships",
                    "Collaborative approach",
                    "Ethical considerations"
                ]
            },
            "neuroticism": {
                "characteristics": [
                    "Emotionally sensitive",
                    "Prone to anxiety",
                    "Seeks security",
                    "Cautious",
                    "Values stability"
                ],
                "messaging_preferences": {
                    "tone": "reassuring, supportive, stable",
                    "content_style": "risk mitigation, guarantees, support",
                    "triggers": ["security", "reassurance", "risk_reduction", "support"],
                    "avoid": ["uncertainty", "risk", "pressure"]
                },
                "decision_factors": [
                    "Risk mitigation",
                    "Security and stability",
                    "Support and guidance",
                    "Proven track record"
                ]
            }
        }
    
    def _initialize_psychological_triggers(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize psychological triggers and their applications
        """
        return {
            "scarcity": {
                "description": "Limited availability creates urgency",
                "applications": [
                    "Limited-time partnership opportunities",
                    "Exclusive access to resources",
                    "First-mover advantages"
                ],
                "phrases": [
                    "Limited time offer",
                    "Exclusive opportunity",
                    "Only available to select partners",
                    "First 100 companies only"
                ]
            },
            "social_proof": {
                "description": "Others' actions influence behavior",
                "applications": [
                    "Success stories from similar companies",
                    "Industry leader endorsements",
                    "Partnership statistics"
                ],
                "phrases": [
                    "Join 500+ successful partnerships",
                    "Trusted by industry leaders",
                    "95% of partners report growth",
                    "Featured in TechCrunch"
                ]
            },
            "authority": {
                "description": "Expertise and credibility influence decisions",
                "applications": [
                    "Industry expert endorsements",
                    "Awards and recognition",
                    "Thought leadership content"
                ],
                "phrases": [
                    "Industry-leading expertise",
                    "Award-winning platform",
                    "Recognized by Gartner",
                    "Trusted by Fortune 500"
                ]
            },
            "reciprocity": {
                "description": "People feel obligated to return favors",
                "applications": [
                    "Free resources and tools",
                    "Valuable insights sharing",
                    "No-cost partnership assessment"
                ],
                "phrases": [
                    "Complimentary partnership audit",
                    "Free strategic consultation",
                    "Exclusive industry report",
                    "No-obligation assessment"
                ]
            },
            "commitment": {
                "description": "People align actions with commitments",
                "applications": [
                    "Partnership goal setting",
                    "Public commitment ceremonies",
                    "Milestone celebrations"
                ],
                "phrases": [
                    "Commit to mutual growth",
                    "Partnership pledge",
                    "Shared success goals",
                    "Joint mission statement"
                ]
            },
            "liking": {
                "description": "People prefer to work with those they like",
                "applications": [
                    "Shared values and culture",
                    "Similar company backgrounds",
                    "Personal connection building"
                ],
                "phrases": [
                    "Shared vision and values",
                    "Cultural alignment",
                    "Like-minded partners",
                    "Common goals and aspirations"
                ]
            }
        }
    
    def _initialize_persuasion_principles(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize Cialdini's principles of persuasion
        """
        return {
            "consistency": {
                "principle": "People align actions with previous commitments",
                "application": "Reference past decisions and commitments",
                "examples": [
                    "Building on your previous innovation initiatives",
                    "Consistent with your growth strategy",
                    "Aligns with your stated objectives"
                ]
            },
            "consensus": {
                "principle": "People follow what others like them do",
                "application": "Show similar companies' success",
                "examples": [
                    "Companies like yours have seen 40% growth",
                    "Similar-stage startups report success",
                    "Industry peers are adopting this approach"
                ]
            },
            "contrast": {
                "principle": "Perception is relative to comparison points",
                "application": "Compare to alternatives or status quo",
                "examples": [
                    "Unlike traditional partnerships",
                    "Compared to going it alone",
                    "While competitors struggle"
                ]
            }
        }
    
    async def analyze_campaign_psychology(
        self,
        campaign_brief: Dict[str, Any],
        channel_content: List[Dict[str, Any]],
        audience_segment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze psychological aspects of the campaign
        """
        try:
            analysis = {
                "personality_alignment": self._analyze_personality_alignment(
                    channel_content, audience_segment
                ),
                "psychological_triggers_analysis": self._analyze_psychological_triggers(
                    campaign_brief, channel_content
                ),
                "persuasion_principles_usage": self._analyze_persuasion_principles(
                    campaign_brief, channel_content
                ),
                "emotional_journey": self._map_emotional_journey(channel_content),
                "cognitive_load_assessment": self._assess_cognitive_load(channel_content),
                "behavioral_predictions": self._predict_behavioral_responses(
                    campaign_brief, audience_segment
                ),
                "optimization_opportunities": self._identify_psychology_optimizations(
                    campaign_brief, channel_content, audience_segment
                )
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Campaign psychology analysis failed: {e}")
            return {}
    
    def _analyze_personality_alignment(
        self,
        channel_content: List[Dict[str, Any]],
        audience_segment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze how well content aligns with audience personality traits
        """
        big_five_traits = audience_segment.get('big_five_traits', {})
        alignment_scores = {}
        
        for trait, score in big_five_traits.items():
            if score > 0.6:  # High trait score
                trait_profile = self.big_five_profiles.get(trait, {})
                preferred_triggers = trait_profile.get('messaging_preferences', {}).get('triggers', [])
                
                # Count trigger usage across content
                trigger_usage = 0
                total_variants = 0
                
                for content in channel_content:
                    for variant in content.get('copy_variants', []):
                        total_variants += 1
                        variant_triggers = variant.get('psychological_triggers', [])
                        trigger_usage += len(set(variant_triggers) & set(preferred_triggers))
                
                if total_variants > 0:
                    alignment_scores[trait] = {
                        "score": min(1.0, trigger_usage / total_variants),
                        "preferred_triggers": preferred_triggers,
                        "usage_count": trigger_usage,
                        "recommendations": self._get_trait_recommendations(trait, trigger_usage / total_variants)
                    }
        
        return {
            "trait_alignment_scores": alignment_scores,
            "overall_alignment": np.mean([scores["score"] for scores in alignment_scores.values()]) if alignment_scores else 0.5,
            "strongest_alignment": max(alignment_scores.items(), key=lambda x: x[1]["score"])[0] if alignment_scores else None,
            "improvement_areas": [trait for trait, data in alignment_scores.items() if data["score"] < 0.7]
        }
    
    def _analyze_psychological_triggers(
        self,
        campaign_brief: Dict[str, Any],
        channel_content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze usage of psychological triggers across the campaign
        """
        trigger_usage = {}
        total_variants = 0
        
        # Count trigger usage
        for content in channel_content:
            for variant in content.get('copy_variants', []):
                total_variants += 1
                for trigger in variant.get('psychological_triggers', []):
                    trigger_usage[trigger] = trigger_usage.get(trigger, 0) + 1
        
        # Analyze trigger effectiveness
        trigger_analysis = {}
        for trigger, count in trigger_usage.items():
            trigger_info = self.psychological_triggers.get(trigger, {})
            trigger_analysis[trigger] = {
                "usage_count": count,
                "usage_percentage": count / total_variants if total_variants > 0 else 0,
                "description": trigger_info.get('description', ''),
                "effectiveness_score": self._calculate_trigger_effectiveness(trigger, count, total_variants)
            }
        
        return {
            "trigger_usage": trigger_analysis,
            "most_used_triggers": sorted(trigger_usage.items(), key=lambda x: x[1], reverse=True)[:5],
            "trigger_diversity": len(trigger_usage),
            "recommended_additions": self._recommend_additional_triggers(trigger_usage),
            "balance_assessment": self._assess_trigger_balance(trigger_usage)
        }
    
    def _analyze_persuasion_principles(
        self,
        campaign_brief: Dict[str, Any],
        channel_content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze usage of Cialdini's persuasion principles
        """
        principle_usage = {}
        
        # Map triggers to principles
        trigger_to_principle = {
            "scarcity": "scarcity",
            "social_proof": "consensus",
            "authority": "authority",
            "reciprocity": "reciprocity",
            "commitment": "consistency",
            "liking": "liking"
        }
        
        # Count principle usage
        for content in channel_content:
            for variant in content.get('copy_variants', []):
                for trigger in variant.get('psychological_triggers', []):
                    principle = trigger_to_principle.get(trigger)
                    if principle:
                        principle_usage[principle] = principle_usage.get(principle, 0) + 1
        
        return {
            "principle_usage": principle_usage,
            "principles_covered": len(principle_usage),
            "missing_principles": [p for p in self.persuasion_principles.keys() if p not in principle_usage],
            "balance_score": self._calculate_principle_balance(principle_usage)
        }
    
    def _map_emotional_journey(self, channel_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Map the emotional journey across different channels
        """
        emotional_stages = {
            "awareness": {"channels": ["social"], "emotions": ["curiosity", "interest"]},
            "consideration": {"channels": ["email", "content"], "emotions": ["trust", "confidence"]},
            "decision": {"channels": ["video", "personal"], "emotions": ["excitement", "commitment"]},
            "action": {"channels": ["all"], "emotions": ["urgency", "determination"]}
        }
        
        journey_analysis = {}
        
        for stage, info in emotional_stages.items():
            relevant_content = [
                content for content in channel_content
                if content['channel'] in info['channels'] or 'all' in info['channels']
            ]
            
            if relevant_content:
                # Analyze emotional tone in content
                emotional_alignment = self._analyze_emotional_tone(relevant_content, info['emotions'])
                journey_analysis[stage] = {
                    "target_emotions": info['emotions'],
                    "content_alignment": emotional_alignment,
                    "channel_coverage": [content['channel'] for content in relevant_content]
                }
        
        return {
            "emotional_stages": journey_analysis,
            "journey_completeness": len(journey_analysis) / len(emotional_stages),
            "emotional_consistency": self._assess_emotional_consistency(journey_analysis)
        }
    
    def _assess_cognitive_load(self, channel_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assess cognitive load of campaign content
        """
        load_assessment = {}
        
        for content in channel_content:
            channel = content['channel']
            variants = content.get('copy_variants', [])
            
            if variants:
                # Analyze complexity metrics
                avg_headline_length = np.mean([len(v.get('headline', '')) for v in variants])
                avg_body_length = np.mean([len(v.get('body_text', '')) for v in variants])
                avg_trigger_count = np.mean([len(v.get('psychological_triggers', [])) for v in variants])
                
                # Calculate cognitive load score (0-1, lower is better)
                load_score = min(1.0, (
                    (avg_headline_length / 100) * 0.3 +
                    (avg_body_length / 500) * 0.5 +
                    (avg_trigger_count / 5) * 0.2
                ))
                
                load_assessment[channel] = {
                    "cognitive_load_score": load_score,
                    "complexity_level": "high" if load_score > 0.7 else "medium" if load_score > 0.4 else "low",
                    "avg_headline_length": avg_headline_length,
                    "avg_body_length": avg_body_length,
                    "avg_trigger_count": avg_trigger_count,
                    "recommendations": self._get_cognitive_load_recommendations(load_score)
                }
        
        return {
            "channel_assessments": load_assessment,
            "overall_load": np.mean([assessment["cognitive_load_score"] for assessment in load_assessment.values()]) if load_assessment else 0.5,
            "optimization_priority": sorted(load_assessment.items(), key=lambda x: x[1]["cognitive_load_score"], reverse=True)
        }
    
    def _predict_behavioral_responses(
        self,
        campaign_brief: Dict[str, Any],
        audience_segment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Predict likely behavioral responses based on psychology
        """
        big_five_traits = audience_segment.get('big_five_traits', {})
        
        predictions = {
            "engagement_likelihood": self._predict_engagement(big_five_traits),
            "decision_speed": self._predict_decision_speed(big_five_traits),
            "information_seeking": self._predict_information_seeking(big_five_traits),
            "social_sharing": self._predict_social_sharing(big_five_traits),
            "risk_tolerance": self._predict_risk_tolerance(big_five_traits)
        }
        
        return {
            "behavioral_predictions": predictions,
            "dominant_behaviors": self._identify_dominant_behaviors(predictions),
            "optimization_strategies": self._generate_behavior_optimization_strategies(predictions)
        }
    
    def _identify_psychology_optimizations(
        self,
        campaign_brief: Dict[str, Any],
        channel_content: List[Dict[str, Any]],
        audience_segment: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify psychology-based optimization opportunities
        """
        optimizations = []
        
        # Personality alignment optimizations
        big_five_traits = audience_segment.get('big_five_traits', {})
        for trait, score in big_five_traits.items():
            if score > 0.7:  # High trait score
                trait_profile = self.big_five_profiles.get(trait, {})
                optimizations.append({
                    "type": "personality_alignment",
                    "trait": trait,
                    "priority": "high",
                    "description": f"Enhance {trait} targeting across all channels",
                    "specific_actions": trait_profile.get('messaging_preferences', {}).get('triggers', [])
                })
        
        # Trigger diversity optimization
        trigger_usage = {}
        for content in channel_content:
            for variant in content.get('copy_variants', []):
                for trigger in variant.get('psychological_triggers', []):
                    trigger_usage[trigger] = trigger_usage.get(trigger, 0) + 1
        
        if len(trigger_usage) < 4:
            optimizations.append({
                "type": "trigger_diversity",
                "priority": "medium",
                "description": "Increase psychological trigger diversity",
                "specific_actions": ["Add reciprocity triggers", "Include authority elements", "Enhance social proof"]
            })
        
        # Emotional journey optimization
        optimizations.append({
            "type": "emotional_journey",
            "priority": "medium",
            "description": "Optimize emotional progression across channels",
            "specific_actions": [
                "Build curiosity in social content",
                "Establish trust in email content",
                "Create excitement in video content"
            ]
        })
        
        return optimizations
    
    async def get_segment_insights(self, audience_segment: str) -> Dict[str, Any]:
        """
        Get psychological insights for a specific audience segment
        """
        try:
            # This would typically query a database or ML model
            # For now, return mock insights based on segment name
            
            insights = {
                "segment_name": audience_segment,
                "psychological_profile": {
                    "dominant_traits": ["conscientiousness", "openness"],
                    "decision_factors": ["ROI", "innovation_potential", "risk_mitigation"],
                    "preferred_communication": "data-driven, professional, detailed"
                },
                "behavioral_patterns": {
                    "information_seeking": "high",
                    "decision_speed": "moderate",
                    "social_influence": "medium",
                    "risk_tolerance": "low-medium"
                },
                "optimization_recommendations": [
                    "Use data and metrics to support claims",
                    "Provide detailed implementation plans",
                    "Include risk mitigation strategies",
                    "Highlight innovation aspects"
                ]
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Segment insights generation failed: {e}")
            return {}
    
    # Helper methods for analysis
    
    def _get_trait_recommendations(self, trait: str, alignment_score: float) -> List[str]:
        """Get recommendations for improving trait alignment"""
        if alignment_score < 0.5:
            trait_profile = self.big_five_profiles.get(trait, {})
            triggers = trait_profile.get('messaging_preferences', {}).get('triggers', [])
            return [f"Incorporate more {trigger} elements" for trigger in triggers[:3]]
        return ["Maintain current trait alignment"]
    
    def _calculate_trigger_effectiveness(self, trigger: str, count: int, total: int) -> float:
        """Calculate effectiveness score for a psychological trigger"""
        usage_rate = count / total if total > 0 else 0
        
        # Optimal usage rates for different triggers
        optimal_rates = {
            "scarcity": 0.3,
            "social_proof": 0.5,
            "authority": 0.4,
            "reciprocity": 0.2,
            "commitment": 0.3,
            "liking": 0.4
        }
        
        optimal = optimal_rates.get(trigger, 0.3)
        effectiveness = 1.0 - abs(usage_rate - optimal) / optimal
        return max(0.0, effectiveness)
    
    def _recommend_additional_triggers(self, current_usage: Dict[str, int]) -> List[str]:
        """Recommend additional psychological triggers"""
        all_triggers = set(self.psychological_triggers.keys())
        used_triggers = set(current_usage.keys())
        unused_triggers = all_triggers - used_triggers
        
        # Prioritize high-impact triggers
        priority_triggers = ["social_proof", "authority", "scarcity"]
        recommendations = [t for t in priority_triggers if t in unused_triggers]
        
        return recommendations[:3]
    
    def _assess_trigger_balance(self, trigger_usage: Dict[str, int]) -> Dict[str, Any]:
        """Assess balance of psychological triggers"""
        if not trigger_usage:
            return {"balance_score": 0.0, "assessment": "No triggers used"}
        
        total_usage = sum(trigger_usage.values())
        usage_distribution = [count / total_usage for count in trigger_usage.values()]
        
        # Calculate balance using entropy
        entropy = -sum(p * np.log2(p) for p in usage_distribution if p > 0)
        max_entropy = np.log2(len(trigger_usage))
        balance_score = entropy / max_entropy if max_entropy > 0 else 0
        
        return {
            "balance_score": balance_score,
            "assessment": "well-balanced" if balance_score > 0.8 else "moderately balanced" if balance_score > 0.5 else "imbalanced"
        }
    
    def _calculate_principle_balance(self, principle_usage: Dict[str, int]) -> float:
        """Calculate balance score for persuasion principles"""
        if not principle_usage:
            return 0.0
        
        total_principles = len(self.persuasion_principles)
        used_principles = len(principle_usage)
        
        return used_principles / total_principles
    
    def _analyze_emotional_tone(self, content_list: List[Dict[str, Any]], target_emotions: List[str]) -> float:
        """Analyze emotional tone alignment"""
        # Simplified emotional analysis
        # In production, this would use NLP sentiment analysis
        
        emotional_keywords = {
            "curiosity": ["discover", "explore", "learn", "find out"],
            "interest": ["exciting", "innovative", "breakthrough", "opportunity"],
            "trust": ["reliable", "proven", "trusted", "secure"],
            "confidence": ["guaranteed", "certain", "assured", "confident"],
            "excitement": ["amazing", "incredible", "revolutionary", "game-changing"],
            "commitment": ["dedicated", "committed", "pledge", "promise"],
            "urgency": ["now", "limited", "hurry", "deadline"],
            "determination": ["achieve", "succeed", "accomplish", "win"]
        }
        
        alignment_scores = []
        
        for content in content_list:
            for variant in content.get('copy_variants', []):
                text = (variant.get('headline', '') + ' ' + variant.get('body_text', '')).lower()
                
                for emotion in target_emotions:
                    keywords = emotional_keywords.get(emotion, [])
                    keyword_count = sum(1 for keyword in keywords if keyword in text)
                    alignment_scores.append(min(1.0, keyword_count / len(keywords)))
        
        return np.mean(alignment_scores) if alignment_scores else 0.5
    
    def _assess_emotional_consistency(self, journey_analysis: Dict[str, Any]) -> float:
        """Assess emotional consistency across the journey"""
        if not journey_analysis:
            return 0.0
        
        alignment_scores = [
            stage_data.get('content_alignment', 0.5)
            for stage_data in journey_analysis.values()
        ]
        
        return np.mean(alignment_scores)
    
    def _get_cognitive_load_recommendations(self, load_score: float) -> List[str]:
        """Get recommendations for cognitive load optimization"""
        if load_score > 0.7:
            return [
                "Simplify headlines and messaging",
                "Reduce number of psychological triggers per variant",
                "Break complex information into digestible chunks"
            ]
        elif load_score > 0.4:
            return [
                "Consider A/B testing simpler variants",
                "Optimize information hierarchy"
            ]
        else:
            return ["Cognitive load is optimal"]
    
    def _predict_engagement(self, big_five_traits: Dict[str, float]) -> str:
        """Predict engagement likelihood based on personality traits"""
        extraversion = big_five_traits.get('extraversion', 0.5)
        openness = big_five_traits.get('openness', 0.5)
        
        engagement_score = (extraversion * 0.6) + (openness * 0.4)
        
        if engagement_score > 0.7:
            return "high"
        elif engagement_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _predict_decision_speed(self, big_five_traits: Dict[str, float]) -> str:
        """Predict decision-making speed"""
        conscientiousness = big_five_traits.get('conscientiousness', 0.5)
        neuroticism = big_five_traits.get('neuroticism', 0.5)
        
        # High conscientiousness = slower (more deliberate)
        # High neuroticism = slower (more anxious)
        speed_score = 1.0 - ((conscientiousness * 0.5) + (neuroticism * 0.5))
        
        if speed_score > 0.6:
            return "fast"
        elif speed_score > 0.3:
            return "moderate"
        else:
            return "slow"
    
    def _predict_information_seeking(self, big_five_traits: Dict[str, float]) -> str:
        """Predict information-seeking behavior"""
        openness = big_five_traits.get('openness', 0.5)
        conscientiousness = big_five_traits.get('conscientiousness', 0.5)
        
        seeking_score = (openness * 0.6) + (conscientiousness * 0.4)
        
        if seeking_score > 0.6:
            return "high"
        elif seeking_score > 0.3:
            return "medium"
        else:
            return "low"
    
    def _predict_social_sharing(self, big_five_traits: Dict[str, float]) -> str:
        """Predict social sharing likelihood"""
        extraversion = big_five_traits.get('extraversion', 0.5)
        agreeableness = big_five_traits.get('agreeableness', 0.5)
        
        sharing_score = (extraversion * 0.7) + (agreeableness * 0.3)
        
        if sharing_score > 0.6:
            return "high"
        elif sharing_score > 0.3:
            return "medium"
        else:
            return "low"
    
    def _predict_risk_tolerance(self, big_five_traits: Dict[str, float]) -> str:
        """Predict risk tolerance"""
        openness = big_five_traits.get('openness', 0.5)
        neuroticism = big_five_traits.get('neuroticism', 0.5)
        
        # High openness = higher risk tolerance
        # High neuroticism = lower risk tolerance
        tolerance_score = openness - neuroticism
        
        if tolerance_score > 0.2:
            return "high"
        elif tolerance_score > -0.2:
            return "medium"
        else:
            return "low"
    
    def _identify_dominant_behaviors(self, predictions: Dict[str, str]) -> List[str]:
        """Identify dominant behavioral patterns"""
        dominant = []
        
        if predictions.get('engagement_likelihood') == 'high':
            dominant.append('high_engagement')
        
        if predictions.get('decision_speed') == 'fast':
            dominant.append('quick_decision')
        
        if predictions.get('information_seeking') == 'high':
            dominant.append('research_oriented')
        
        if predictions.get('social_sharing') == 'high':
            dominant.append('social_amplifier')
        
        return dominant
    
    def _generate_behavior_optimization_strategies(self, predictions: Dict[str, str]) -> List[str]:
        """Generate optimization strategies based on behavioral predictions"""
        strategies = []
        
        if predictions.get('engagement_likelihood') == 'low':
            strategies.append("Use stronger hooks and interactive elements to boost engagement")
        
        if predictions.get('decision_speed') == 'slow':
            strategies.append("Provide comprehensive information and reduce perceived risk")
        
        if predictions.get('information_seeking') == 'high':
            strategies.append("Include detailed resources and supporting documentation")
        
        if predictions.get('social_sharing') == 'high':
            strategies.append("Add social sharing incentives and shareable content formats")
        
        if predictions.get('risk_tolerance') == 'low':
            strategies.append("Emphasize security, guarantees, and risk mitigation")
        
        return strategies