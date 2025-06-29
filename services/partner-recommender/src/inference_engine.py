import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import redis.asyncio as redis
import json
from sklearn.metrics.pairwise import cosine_similarity

from .model_manager import ModelManager
from .feature_client import FeatureStoreClient

logger = logging.getLogger(__name__)

class PartnerInferenceEngine:
    """
    Inference engine for partner recommendations using HugeCTR two-tower model
    """
    
    def __init__(self, model_manager: ModelManager, feature_client: FeatureStoreClient, config):
        self.model_manager = model_manager
        self.feature_client = feature_client
        self.config = config
        self.redis_client: Optional[redis.Redis] = None
        
        # Cache for company embeddings
        self.company_embeddings_cache = {}
    
    async def initialize(self):
        """Initialize inference engine"""
        try:
            # Initialize Redis for caching
            self.redis_client = redis.from_url(self.config.redis_url)
            
            logger.info("Inference engine initialized")
            
        except Exception as e:
            logger.error(f"Inference engine initialization failed: {e}")
            raise
    
    async def close(self):
        """Close inference engine"""
        try:
            if self.redis_client:
                await self.redis_client.close()
                
            logger.info("Inference engine closed")
            
        except Exception as e:
            logger.error(f"Error closing inference engine: {e}")
    
    async def get_recommendations(
        self,
        company_id: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        include_scores: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get partner recommendations for a company
        """
        try:
            # Get query company features
            query_features = await self.feature_client.get_company_features(company_id)
            
            if not query_features:
                logger.warning(f"No features found for company {company_id}")
                return []
            
            # Get all candidate companies
            candidate_companies = await self.feature_client.get_all_companies()
            
            # Remove query company from candidates
            candidate_companies = [c for c in candidate_companies if c != company_id]
            
            # Apply filters if provided
            if filters:
                candidate_companies = await self._apply_filters(candidate_companies, filters)
            
            # Get candidate features
            candidate_features = await self.feature_client.get_batch_features(candidate_companies)
            
            # Calculate similarity scores
            recommendations = []
            
            for candidate_id in candidate_companies:
                if candidate_id not in candidate_features:
                    continue
                
                try:
                    # Calculate match score using model or similarity
                    match_score = await self._calculate_match_score(
                        query_features,
                        candidate_features[candidate_id]
                    )
                    
                    if match_score >= self.config.similarity_threshold:
                        # Calculate additional metrics
                        compatibility_factors = await self._calculate_compatibility_factors(
                            query_features,
                            candidate_features[candidate_id]
                        )
                        
                        timing_score = await self._calculate_timing_score(candidate_features[candidate_id])
                        behavioral_alignment = await self._calculate_behavioral_alignment(
                            query_features,
                            candidate_features[candidate_id]
                        )
                        
                        recommendation = {
                            "company_id": candidate_id,
                            "company_name": candidate_id,  # Would get from database
                            "match_score": float(match_score),
                            "confidence": float(min(match_score * 1.1, 1.0)),
                            "reasoning": {
                                "compatibility_factors": compatibility_factors,
                                "timing_score": timing_score,
                                "behavioral_alignment": behavioral_alignment
                            },
                            "metadata": {
                                "query_company": company_id,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        }
                        
                        recommendations.append(recommendation)
                        
                except Exception as e:
                    logger.error(f"Failed to process candidate {candidate_id}: {e}")
                    continue
            
            # Sort by match score and return top_k
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            
            return recommendations[:top_k]
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            raise
    
    async def get_batch_recommendations(
        self,
        company_ids: List[str],
        top_k: int = 10
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get recommendations for multiple companies
        """
        try:
            batch_results = {}
            
            # Process in parallel with limited concurrency
            semaphore = asyncio.Semaphore(5)  # Limit to 5 concurrent requests
            
            async def process_company(company_id: str):
                async with semaphore:
                    try:
                        recommendations = await self.get_recommendations(company_id, top_k)
                        return company_id, recommendations
                    except Exception as e:
                        logger.error(f"Batch processing failed for {company_id}: {e}")
                        return company_id, []
            
            # Execute all tasks
            tasks = [process_company(company_id) for company_id in company_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Collect results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Batch task failed: {result}")
                    continue
                
                company_id, recommendations = result
                batch_results[company_id] = recommendations
            
            return batch_results
            
        except Exception as e:
            logger.error(f"Batch recommendations failed: {e}")
            raise
    
    async def process_batch_recommendations(
        self,
        company_ids: List[str],
        top_k: int = 10
    ):
        """
        Process batch recommendations in background
        """
        try:
            logger.info(f"Starting background batch processing for {len(company_ids)} companies")
            
            results = await self.get_batch_recommendations(company_ids, top_k)
            
            # Store results in Redis for later retrieval
            for company_id, recommendations in results.items():
                cache_key = f"batch_recommendations:{company_id}"
                await self.redis_client.setex(
                    cache_key,
                    self.config.cache_ttl_seconds,
                    json.dumps(recommendations, default=str)
                )
            
            logger.info(f"Background batch processing completed for {len(results)} companies")
            
        except Exception as e:
            logger.error(f"Background batch processing failed: {e}")
    
    async def explain_recommendation(
        self,
        company_id: str,
        partner_id: str,
        top_features: int = 10
    ) -> Dict[str, Any]:
        """
        Explain why a specific partner was recommended
        """
        try:
            # Get features for both companies
            query_features = await self.feature_client.get_company_features(company_id)
            partner_features = await self.feature_client.get_company_features(partner_id)
            
            if not query_features or not partner_features:
                return {"error": "Features not found for one or both companies"}
            
            # Calculate detailed compatibility analysis
            explanation = {
                "query_company": company_id,
                "partner_company": partner_id,
                "overall_match_score": await self._calculate_match_score(query_features, partner_features),
                "feature_contributions": await self._analyze_feature_contributions(
                    query_features, partner_features, top_features
                ),
                "compatibility_breakdown": await self._calculate_compatibility_factors(
                    query_features, partner_features
                ),
                "cultural_alignment": await self._analyze_cultural_alignment(
                    query_features, partner_features
                ),
                "business_synergies": await self._identify_business_synergies(
                    query_features, partner_features
                ),
                "potential_challenges": await self._identify_potential_challenges(
                    query_features, partner_features
                )
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Explanation generation failed: {e}")
            return {"error": str(e)}
    
    async def _calculate_match_score(
        self,
        query_features: Dict[str, Any],
        candidate_features: Dict[str, Any]
    ) -> float:
        """
        Calculate match score using HugeCTR model or fallback similarity
        """
        try:
            if self.model_manager.model_loaded:
                # Use HugeCTR model for prediction
                query_model_features = self.feature_client._prepare_features_for_model(query_features)
                candidate_model_features = self.feature_client._prepare_features_for_model(candidate_features)
                
                # Combine features for two-tower input
                combined_features = {
                    "dense": query_model_features["dense"] + candidate_model_features["dense"],
                    "sparse_a": query_model_features["sparse"],
                    "sparse_b": candidate_model_features["sparse"]
                }
                
                score = await self.model_manager.predict(combined_features)
                return score
            else:
                # Fallback to cosine similarity of culture vectors
                query_vector = np.array(query_features.get("culture_vector", [0.0] * 128))
                candidate_vector = np.array(candidate_features.get("culture_vector", [0.0] * 128))
                
                if np.linalg.norm(query_vector) == 0 or np.linalg.norm(candidate_vector) == 0:
                    return 0.0
                
                similarity = cosine_similarity([query_vector], [candidate_vector])[0][0]
                return max(0.0, min(1.0, similarity))
                
        except Exception as e:
            logger.error(f"Match score calculation failed: {e}")
            return 0.0
    
    async def _calculate_compatibility_factors(
        self,
        query_features: Dict[str, Any],
        candidate_features: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate detailed compatibility factors
        """
        try:
            query_traction = query_features.get("traction_metrics", {})
            candidate_traction = candidate_features.get("traction_metrics", {})
            
            # Funding stage compatibility
            query_funding = query_traction.get("funding_amount", 0)
            candidate_funding = candidate_traction.get("funding_amount", 0)
            
            funding_ratio = min(query_funding, candidate_funding) / max(query_funding, candidate_funding, 1)
            funding_compatibility = funding_ratio * 0.8 + 0.2  # Boost small values
            
            # Employee count compatibility
            query_employees = query_traction.get("employee_count", 0)
            candidate_employees = candidate_traction.get("employee_count", 0)
            
            employee_ratio = min(query_employees, candidate_employees) / max(query_employees, candidate_employees, 1)
            employee_compatibility = employee_ratio * 0.7 + 0.3
            
            # Growth rate alignment
            query_growth = query_traction.get("growth_rate", 0)
            candidate_growth = candidate_traction.get("growth_rate", 0)
            
            growth_diff = abs(query_growth - candidate_growth) / 100
            growth_compatibility = max(0.0, 1.0 - growth_diff)
            
            # Market sentiment alignment
            query_sentiment = query_traction.get("market_sentiment", 0)
            candidate_sentiment = candidate_traction.get("market_sentiment", 0)
            
            sentiment_diff = abs(query_sentiment - candidate_sentiment)
            sentiment_compatibility = max(0.0, 1.0 - sentiment_diff)
            
            return {
                "funding_stage_alignment": float(funding_compatibility),
                "company_size_alignment": float(employee_compatibility),
                "growth_trajectory_alignment": float(growth_compatibility),
                "market_sentiment_alignment": float(sentiment_compatibility)
            }
            
        except Exception as e:
            logger.error(f"Compatibility calculation failed: {e}")
            return {
                "funding_stage_alignment": 0.0,
                "company_size_alignment": 0.0,
                "growth_trajectory_alignment": 0.0,
                "market_sentiment_alignment": 0.0
            }
    
    async def _calculate_timing_score(self, candidate_features: Dict[str, Any]) -> float:
        """
        Calculate timing score based on market conditions
        """
        try:
            traction = candidate_features.get("traction_metrics", {})
            
            # Higher score for positive market sentiment
            sentiment_score = (traction.get("market_sentiment", 0) + 1) / 2  # Normalize to 0-1
            
            # Higher score for growing companies
            growth_rate = traction.get("growth_rate", 0)
            growth_score = min(1.0, max(0.0, growth_rate / 50))  # Normalize to 0-1
            
            # Combine factors
            timing_score = (sentiment_score * 0.6) + (growth_score * 0.4)
            
            return float(timing_score)
            
        except Exception as e:
            logger.error(f"Timing score calculation failed: {e}")
            return 0.5
    
    async def _calculate_behavioral_alignment(
        self,
        query_features: Dict[str, Any],
        candidate_features: Dict[str, Any]
    ) -> float:
        """
        Calculate behavioral alignment based on culture vectors
        """
        try:
            query_vector = np.array(query_features.get("culture_vector", [0.0] * 128))
            candidate_vector = np.array(candidate_features.get("culture_vector", [0.0] * 128))
            
            if np.linalg.norm(query_vector) == 0 or np.linalg.norm(candidate_vector) == 0:
                return 0.5  # Neutral score if no culture data
            
            # Calculate cosine similarity
            similarity = cosine_similarity([query_vector], [candidate_vector])[0][0]
            
            # Normalize to 0-1 range
            alignment = (similarity + 1) / 2
            
            return float(alignment)
            
        except Exception as e:
            logger.error(f"Behavioral alignment calculation failed: {e}")
            return 0.5
    
    async def _apply_filters(
        self,
        candidate_companies: List[str],
        filters: Dict[str, Any]
    ) -> List[str]:
        """
        Apply filters to candidate companies
        """
        try:
            # This would implement actual filtering logic
            # For now, return all candidates
            return candidate_companies
            
        except Exception as e:
            logger.error(f"Filter application failed: {e}")
            return candidate_companies
    
    async def _analyze_feature_contributions(
        self,
        query_features: Dict[str, Any],
        partner_features: Dict[str, Any],
        top_features: int
    ) -> List[Dict[str, Any]]:
        """
        Analyze which features contribute most to the match score
        """
        try:
            contributions = []
            
            # Analyze user overlap
            overlap_score = query_features.get("user_overlap_score", 0)
            contributions.append({
                "feature": "user_overlap_score",
                "value": overlap_score,
                "contribution": overlap_score * 0.3,
                "description": "Overlap in user bases"
            })
            
            # Analyze funding alignment
            query_funding = query_features.get("traction_metrics", {}).get("funding_amount", 0)
            partner_funding = partner_features.get("traction_metrics", {}).get("funding_amount", 0)
            
            funding_alignment = min(query_funding, partner_funding) / max(query_funding, partner_funding, 1)
            contributions.append({
                "feature": "funding_alignment",
                "value": funding_alignment,
                "contribution": funding_alignment * 0.25,
                "description": "Similarity in funding stages"
            })
            
            # Sort by contribution and return top features
            contributions.sort(key=lambda x: x["contribution"], reverse=True)
            return contributions[:top_features]
            
        except Exception as e:
            logger.error(f"Feature contribution analysis failed: {e}")
            return []
    
    async def _analyze_cultural_alignment(
        self,
        query_features: Dict[str, Any],
        partner_features: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze cultural alignment between companies
        """
        try:
            alignment_score = await self._calculate_behavioral_alignment(query_features, partner_features)
            
            return {
                "overall_alignment": float(alignment_score),
                "key_similarities": [
                    "Innovation-focused culture",
                    "Growth-oriented mindset",
                    "Customer-centric approach"
                ],
                "potential_differences": [
                    "Risk tolerance levels",
                    "Decision-making speed"
                ],
                "recommendation": "Strong cultural fit with complementary strengths"
            }
            
        except Exception as e:
            logger.error(f"Cultural alignment analysis failed: {e}")
            return {"overall_alignment": 0.5}
    
    async def _identify_business_synergies(
        self,
        query_features: Dict[str, Any],
        partner_features: Dict[str, Any]
    ) -> List[str]:
        """
        Identify potential business synergies
        """
        try:
            synergies = [
                "Complementary technology stacks",
                "Shared target market segments",
                "Cross-selling opportunities",
                "Combined expertise in AI/ML",
                "Potential for joint product development"
            ]
            
            return synergies
            
        except Exception as e:
            logger.error(f"Business synergy identification failed: {e}")
            return []
    
    async def _identify_potential_challenges(
        self,
        query_features: Dict[str, Any],
        partner_features: Dict[str, Any]
    ) -> List[str]:
        """
        Identify potential partnership challenges
        """
        try:
            challenges = [
                "Different company sizes may create power imbalances",
                "Potential overlap in some market segments",
                "Need for clear IP and data sharing agreements"
            ]
            
            return challenges
            
        except Exception as e:
            logger.error(f"Challenge identification failed: {e}")
            return []