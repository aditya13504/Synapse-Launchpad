import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class Config:
    """Configuration for Partner Recommender service"""
    
    # Server configuration
    port: int = int(os.getenv("PORT", "8000"))
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Model configuration
    model_path: str = os.getenv("MODEL_PATH", "/app/models")
    model_version: str = os.getenv("MODEL_VERSION", "v1.0.0")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "128"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "1024"))
    
    # Feature store configuration
    feature_store_url: str = os.getenv("FEATURE_STORE_URL", "http://feature-store:8000")
    feature_store_grpc_url: str = os.getenv("FEATURE_STORE_GRPC_URL", "feature-store:50051")
    
    # Database configuration
    database_url: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/synapse_db")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    
    # GPU configuration
    cuda_visible_devices: str = os.getenv("CUDA_VISIBLE_DEVICES", "0")
    hugectr_gpu_count: int = int(os.getenv("HUGECTR_GPU_COUNT", "1"))
    
    # Training configuration
    training_data_path: str = os.getenv("TRAINING_DATA_PATH", "/app/data/training")
    validation_split: float = float(os.getenv("VALIDATION_SPLIT", "0.2"))
    learning_rate: float = float(os.getenv("LEARNING_RATE", "0.001"))
    epochs: int = int(os.getenv("EPOCHS", "100"))
    early_stopping_patience: int = int(os.getenv("EARLY_STOPPING_PATIENCE", "10"))
    
    # Inference configuration
    max_candidates: int = int(os.getenv("MAX_CANDIDATES", "10000"))
    similarity_threshold: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.1"))
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
    
    # Monitoring
    sentry_dsn: str = os.getenv("SENTRY_DSN", "")
    
    # Triton configuration (optional)
    triton_url: str = os.getenv("TRITON_URL", "localhost:8001")
    triton_model_name: str = os.getenv("TRITON_MODEL_NAME", "partner_recommender")
    
    # HugeCTR model configuration
    hugectr_config: Dict[str, Any] = None
    
    def __post_init__(self):
        """Initialize HugeCTR configuration"""
        self.hugectr_config = {
            "solver": {
                "lr_policy": "fixed",
                "display": 1000,
                "max_iter": self.epochs * 1000,
                "snapshot": 10000,
                "snapshot_prefix": f"{self.model_path}/partner_recommender",
                "eval_interval": 1000,
                "eval_batches": 100,
                "mixed_precision": 1024,
                "batchsize": self.batch_size,
                "batchsize_eval": self.batch_size,
                "lr": self.learning_rate,
                "warmup_steps": 1000,
                "decay_start": 48000,
                "decay_steps": 24000,
                "decay_power": 2.0,
                "end_lr": 0.0
            },
            "optimizer": {
                "type": "Adam",
                "adam_hparam": {
                    "learning_rate": self.learning_rate,
                    "beta1": 0.9,
                    "beta2": 0.999,
                    "epsilon": 0.0000001
                }
            },
            "layers": [
                {
                    "name": "data",
                    "type": "Data",
                    "source": f"{self.training_data_path}/train_data.parquet",
                    "eval_source": f"{self.training_data_path}/val_data.parquet",
                    "check": "None",
                    "label": {
                        "top": "label",
                        "label_dim": 1
                    },
                    "dense": {
                        "top": "dense",
                        "dense_dim": 13
                    },
                    "sparse": [
                        {
                            "top": "company_a_cat",
                            "type": "DistributedSlot",
                            "max_feature_num_per_sample": 30,
                            "slot_num": 26
                        },
                        {
                            "top": "company_b_cat",
                            "type": "DistributedSlot", 
                            "max_feature_num_per_sample": 30,
                            "slot_num": 26
                        }
                    ]
                }
            ]
        }