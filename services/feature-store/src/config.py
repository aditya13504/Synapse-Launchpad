import os
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration for Feature Store service"""
    
    # Server configuration
    rest_port: int = int(os.getenv("REST_PORT", "8000"))
    grpc_port: int = int(os.getenv("GRPC_PORT", "50051"))
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/synapse_db")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # Kafka configuration
    kafka_servers: List[str] = os.getenv("KAFKA_SERVERS", "localhost:9092").split(",")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "pulse.events")
    
    # Feature store configuration
    feature_store_path: str = os.getenv("FEATURE_STORE_PATH", "/data/feature_store")
    model_path: str = os.getenv("MODEL_PATH", "/app/models")
    
    # Pipeline configuration
    pipeline_interval_hours: int = int(os.getenv("PIPELINE_INTERVAL_HOURS", "24"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "10000"))
    
    # NVIDIA Merlin configuration
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "128"))
    max_sequence_length: int = int(os.getenv("MAX_SEQUENCE_LENGTH", "100"))
    
    # Monitoring
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    
    # Feature schema
    feature_schema: Dict[str, Any] = {
        "company_id": {"type": "string", "required": True},
        "user_overlap_score": {"type": "float", "min": 0.0, "max": 1.0},
        "traction_metrics": {
            "type": "object",
            "properties": {
                "funding_amount": {"type": "float"},
                "employee_count": {"type": "integer"},
                "growth_rate": {"type": "float"},
                "market_sentiment": {"type": "float", "min": -1.0, "max": 1.0}
            }
        },
        "culture_vector": {"type": "array", "items": {"type": "float"}, "length": 128},
        "match_outcome": {"type": "integer", "enum": [0, 1]}  # Label for training
    }