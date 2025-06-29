import os
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration for Campaign Maker service"""
    
    # Server configuration
    port: int = int(os.getenv("PORT", "8000"))
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # OpenAI configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    openai_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))
    openai_temperature: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # External API configuration
    pica_api_key: str = os.getenv("PICA_API_KEY", "")
    pica_base_url: str = os.getenv("PICA_BASE_URL", "https://api.pica.ai/v1")
    
    tavus_api_key: str = os.getenv("TAVUS_API_KEY", "")
    tavus_base_url: str = os.getenv("TAVUS_BASE_URL", "https://api.tavus.io/v1")
    
    lingo_api_key: str = os.getenv("LINGO_API_KEY", "")
    lingo_base_url: str = os.getenv("LINGO_BASE_URL", "https://api.lingo.com/v1")
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/synapse_db")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Monitoring
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    
    # Campaign configuration
    max_copy_variants: int = int(os.getenv("MAX_COPY_VARIANTS", "3"))
    default_channels: List[str] = os.getenv("DEFAULT_CHANNELS", "social,email,influencer,video").split(",")
    big_five_traits: List[str] = os.getenv("BIG_FIVE_TRAITS", "openness,conscientiousness,extraversion,agreeableness,neuroticism").split(",")
    
    # Psychology engine
    psychology_model_path: str = os.getenv("PSYCHOLOGY_MODEL_PATH", "/app/models/psychology")
    enable_advanced_psychology: bool = os.getenv("ENABLE_ADVANCED_PSYCHOLOGY", "true").lower() == "true"
    
    # Content optimization
    enable_ab_testing: bool = os.getenv("ENABLE_A_B_TESTING", "true").lower() == "true"
    performance_prediction_model: str = os.getenv("PERFORMANCE_PREDICTION_MODEL", "xgboost")
    optimization_threshold: float = float(os.getenv("OPTIMIZATION_THRESHOLD", "0.15"))
    
    # Function calling schemas for GPT-4o
    campaign_brief_schema: Dict[str, Any] = {
        "name": "generate_campaign_brief",
        "description": "Generate a comprehensive campaign brief with psychological insights",
        "parameters": {
            "type": "object",
            "properties": {
                "objective": {
                    "type": "string",
                    "description": "Primary campaign objective"
                },
                "key_message": {
                    "type": "string", 
                    "description": "Core message that resonates with target audience"
                },
                "hooks": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Attention-grabbing hooks for different channels"
                },
                "fomo_angle": {
                    "type": "string",
                    "description": "Fear of missing out angle to drive urgency"
                },
                "psychological_triggers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Psychological triggers to employ (scarcity, authority, social proof, etc.)"
                },
                "success_metrics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Key metrics to measure campaign success"
                }
            },
            "required": ["objective", "key_message", "hooks", "fomo_angle", "psychological_triggers", "success_metrics"]
        }
    }
    
    channel_mix_schema: Dict[str, Any] = {
        "name": "generate_channel_mix_plan",
        "description": "Generate optimal channel mix plan with budget allocation",
        "parameters": {
            "type": "object",
            "properties": {
                "channels": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "channel": {"type": "string"},
                            "allocation_percentage": {"type": "number"},
                            "rationale": {"type": "string"},
                            "optimal_timing": {"type": "string"},
                            "content_types": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "psychological_approach": {"type": "string"}
                        },
                        "required": ["channel", "allocation_percentage", "rationale", "optimal_timing", "content_types", "psychological_approach"]
                    }
                }
            },
            "required": ["channels"]
        }
    }
    
    copy_generation_schema: Dict[str, Any] = {
        "name": "generate_copy_variants",
        "description": "Generate copy variants targeting different Big Five personality traits",
        "parameters": {
            "type": "object",
            "properties": {
                "variants": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "big_five_target": {"type": "string"},
                            "headline": {"type": "string"},
                            "body_text": {"type": "string"},
                            "cta": {"type": "string"},
                            "psychological_triggers": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "tone_analysis": {
                                "type": "object",
                                "properties": {
                                    "formality": {"type": "number"},
                                    "enthusiasm": {"type": "number"},
                                    "urgency": {"type": "number"},
                                    "trustworthiness": {"type": "number"}
                                }
                            }
                        },
                        "required": ["big_five_target", "headline", "body_text", "cta", "psychological_triggers", "tone_analysis"]
                    }
                }
            },
            "required": ["variants"]
        }
    }