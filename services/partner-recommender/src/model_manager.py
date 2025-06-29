import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import hugectr
import cudf
import pandas as pd
import numpy as np
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Manages HugeCTR two-tower model lifecycle
    """
    
    def __init__(self, config):
        self.config = config
        self.model: Optional[hugectr.Model] = None
        self.model_loaded = False
        self.model_version = config.model_version
        self.training_history = []
        
        # Ensure model directory exists
        Path(config.model_path).mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize model manager and load existing model"""
        try:
            # Check if model exists
            model_file = Path(self.config.model_path) / "partner_recommender_dense_1000.model"
            
            if model_file.exists():
                await self.load_model()
            else:
                logger.info("No existing model found. Model will be created on first training.")
                
            logger.info("Model manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Model manager initialization failed: {e}")
            raise
    
    async def load_model(self):
        """Load HugeCTR model for inference"""
        try:
            # Create HugeCTR inference session
            self.model = hugectr.inference.CreateInferenceSession(
                model_config_path=f"{self.config.model_path}/partner_recommender.json",
                model_weights_path=f"{self.config.model_path}/partner_recommender_dense_1000.model",
                device_id=0,
                cache_size_percentage=0.5,
                i64_input_key=True
            )
            
            self.model_loaded = True
            logger.info(f"Model loaded successfully: {self.model_version}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model_loaded = False
            raise
    
    async def reload_model(self):
        """Reload model from disk"""
        try:
            if self.model:
                # Clean up existing model
                del self.model
                self.model = None
                self.model_loaded = False
            
            await self.load_model()
            logger.info("Model reloaded successfully")
            
        except Exception as e:
            logger.error(f"Model reload failed: {e}")
            raise
    
    async def train_model(
        self, 
        dataset_path: str, 
        model_config: Dict[str, Any], 
        training_params: Dict[str, Any]
    ):
        """
        Train HugeCTR two-tower model
        """
        try:
            logger.info("Starting model training...")
            
            # Update configuration with training parameters
            config = self._create_training_config(dataset_path, model_config, training_params)
            
            # Save configuration
            config_path = f"{self.config.model_path}/partner_recommender.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Create and train model
            model = hugectr.Model(config, hugectr.Check_t.Sum)
            model.compile()
            model.summary()
            
            # Train the model
            model.fit(
                max_iter=training_params.get("max_iter", self.config.epochs * 1000),
                display=training_params.get("display", 1000),
                eval_interval=training_params.get("eval_interval", 1000),
                snapshot=training_params.get("snapshot", 10000)
            )
            
            # Save training history
            training_record = {
                "timestamp": datetime.utcnow().isoformat(),
                "dataset_path": dataset_path,
                "config": model_config,
                "params": training_params,
                "model_version": self.model_version
            }
            
            self.training_history.append(training_record)
            
            # Save training history
            history_path = f"{self.config.model_path}/training_history.json"
            with open(history_path, 'w') as f:
                json.dump(self.training_history, f, indent=2)
            
            # Reload model for inference
            await self.load_model()
            
            logger.info("Model training completed successfully")
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    def _create_training_config(
        self, 
        dataset_path: str, 
        model_config: Dict[str, Any], 
        training_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create HugeCTR training configuration for two-tower model
        """
        config = {
            "solver": {
                "lr_policy": "fixed",
                "display": training_params.get("display", 1000),
                "max_iter": training_params.get("max_iter", self.config.epochs * 1000),
                "snapshot": training_params.get("snapshot", 10000),
                "snapshot_prefix": f"{self.config.model_path}/partner_recommender",
                "eval_interval": training_params.get("eval_interval", 1000),
                "eval_batches": training_params.get("eval_batches", 100),
                "mixed_precision": 1024,
                "batchsize": self.config.batch_size,
                "batchsize_eval": self.config.batch_size,
                "lr": self.config.learning_rate,
                "warmup_steps": 1000,
                "decay_start": 48000,
                "decay_steps": 24000,
                "decay_power": 2.0,
                "end_lr": 0.0
            },
            "optimizer": {
                "type": "Adam",
                "adam_hparam": {
                    "learning_rate": self.config.learning_rate,
                    "beta1": 0.9,
                    "beta2": 0.999,
                    "epsilon": 0.0000001
                }
            },
            "layers": [
                # Data layer
                {
                    "name": "data",
                    "type": "Data",
                    "source": f"{dataset_path}/train_data.parquet",
                    "eval_source": f"{dataset_path}/val_data.parquet",
                    "check": "None",
                    "label": {
                        "top": "label",
                        "label_dim": 1
                    },
                    "dense": {
                        "top": "dense",
                        "dense_dim": model_config.get("dense_features", 13)
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
                },
                
                # Sparse embedding layers for company A
                {
                    "name": "sparse_embedding_a",
                    "type": "DistributedSlotSparseEmbeddingHash",
                    "bottom": "company_a_cat",
                    "top": "sparse_embedding_a",
                    "sparse_embedding_hparam": {
                        "vocabulary_size": model_config.get("vocab_size", 100000),
                        "embedding_vec_size": self.config.embedding_dim,
                        "combiner": "sum"
                    }
                },
                
                # Sparse embedding layers for company B
                {
                    "name": "sparse_embedding_b",
                    "type": "DistributedSlotSparseEmbeddingHash",
                    "bottom": "company_b_cat",
                    "top": "sparse_embedding_b", 
                    "sparse_embedding_hparam": {
                        "vocabulary_size": model_config.get("vocab_size", 100000),
                        "embedding_vec_size": self.config.embedding_dim,
                        "combiner": "sum"
                    }
                },
                
                # Company A tower
                {
                    "name": "reshape_a",
                    "type": "Reshape",
                    "bottom": "sparse_embedding_a",
                    "top": "reshape_a",
                    "leading_dim": self.config.embedding_dim * 26
                },
                {
                    "name": "concat_a",
                    "type": "Concat",
                    "bottom": ["dense", "reshape_a"],
                    "top": "concat_a"
                },
                {
                    "name": "fc1_a",
                    "type": "InnerProduct",
                    "bottom": "concat_a",
                    "top": "fc1_a",
                    "fc_param": {
                        "num_output": 512
                    }
                },
                {
                    "name": "relu1_a",
                    "type": "ReLU",
                    "bottom": "fc1_a",
                    "top": "relu1_a"
                },
                {
                    "name": "dropout1_a",
                    "type": "Dropout",
                    "rate": 0.5,
                    "bottom": "relu1_a",
                    "top": "dropout1_a"
                },
                {
                    "name": "fc2_a",
                    "type": "InnerProduct",
                    "bottom": "dropout1_a",
                    "top": "fc2_a",
                    "fc_param": {
                        "num_output": 256
                    }
                },
                {
                    "name": "relu2_a",
                    "type": "ReLU",
                    "bottom": "fc2_a",
                    "top": "relu2_a"
                },
                {
                    "name": "tower_a",
                    "type": "InnerProduct",
                    "bottom": "relu2_a",
                    "top": "tower_a",
                    "fc_param": {
                        "num_output": self.config.embedding_dim
                    }
                },
                
                # Company B tower (similar structure)
                {
                    "name": "reshape_b",
                    "type": "Reshape",
                    "bottom": "sparse_embedding_b",
                    "top": "reshape_b",
                    "leading_dim": self.config.embedding_dim * 26
                },
                {
                    "name": "concat_b",
                    "type": "Concat",
                    "bottom": ["dense", "reshape_b"],
                    "top": "concat_b"
                },
                {
                    "name": "fc1_b",
                    "type": "InnerProduct",
                    "bottom": "concat_b",
                    "top": "fc1_b",
                    "fc_param": {
                        "num_output": 512
                    }
                },
                {
                    "name": "relu1_b",
                    "type": "ReLU",
                    "bottom": "fc1_b",
                    "top": "relu1_b"
                },
                {
                    "name": "dropout1_b",
                    "type": "Dropout",
                    "rate": 0.5,
                    "bottom": "relu1_b",
                    "top": "dropout1_b"
                },
                {
                    "name": "fc2_b",
                    "type": "InnerProduct",
                    "bottom": "dropout1_b",
                    "top": "fc2_b",
                    "fc_param": {
                        "num_output": 256
                    }
                },
                {
                    "name": "relu2_b",
                    "type": "ReLU",
                    "bottom": "fc2_b",
                    "top": "relu2_b"
                },
                {
                    "name": "tower_b",
                    "type": "InnerProduct",
                    "bottom": "relu2_b",
                    "top": "tower_b",
                    "fc_param": {
                        "num_output": self.config.embedding_dim
                    }
                },
                
                # Dot product for similarity
                {
                    "name": "dot_product",
                    "type": "DotProduct",
                    "bottom": ["tower_a", "tower_b"],
                    "top": "dot_product"
                },
                
                # Sigmoid activation for final score
                {
                    "name": "sigmoid",
                    "type": "Sigmoid",
                    "bottom": "dot_product",
                    "top": "sigmoid"
                },
                
                # Binary cross-entropy loss
                {
                    "name": "loss",
                    "type": "BinaryCrossEntropyLoss",
                    "bottom": ["sigmoid", "label"],
                    "top": "loss"
                }
            ]
        }
        
        return config
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get current model status"""
        try:
            gpu_available = self._check_gpu_availability()
            
            status = {
                "loaded": self.model_loaded,
                "version": self.model_version,
                "gpu_available": gpu_available,
                "model_path": self.config.model_path,
                "last_updated": None
            }
            
            # Check if model files exist
            model_file = Path(self.config.model_path) / "partner_recommender_dense_1000.model"
            if model_file.exists():
                status["last_updated"] = datetime.fromtimestamp(model_file.stat().st_mtime).isoformat()
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get model status: {e}")
            return {"loaded": False, "error": str(e)}
    
    async def get_model_metrics(self) -> Dict[str, Any]:
        """Get model performance metrics"""
        try:
            metrics_file = Path(self.config.model_path) / "metrics.json"
            
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    return json.load(f)
            
            return {
                "auc": 0.0,
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get model metrics: {e}")
            return {}
    
    async def get_training_history(self) -> list:
        """Get training history"""
        try:
            history_file = Path(self.config.model_path) / "training_history.json"
            
            if history_file.exists():
                with open(history_file, 'r') as f:
                    return json.load(f)
            
            return self.training_history
            
        except Exception as e:
            logger.error(f"Failed to get training history: {e}")
            return []
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available for HugeCTR"""
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            return device_count > 0
        except:
            return False
    
    async def predict(self, features: Dict[str, Any]) -> float:
        """
        Make prediction using loaded model
        """
        try:
            if not self.model_loaded:
                raise ValueError("Model not loaded")
            
            # Prepare input data for HugeCTR
            dense_features = np.array([features.get("dense", [])], dtype=np.float32)
            sparse_features_a = np.array([features.get("sparse_a", [])], dtype=np.int64)
            sparse_features_b = np.array([features.get("sparse_b", [])], dtype=np.int64)
            
            # Run inference
            predictions = self.model.predict(
                dense_features,
                [sparse_features_a, sparse_features_b]
            )
            
            return float(predictions[0][0])
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise