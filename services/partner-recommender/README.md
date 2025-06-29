# Partner Recommender Service

NVIDIA Merlin HugeCTR-powered partner recommendation system using two-tower architecture for startup matching.

## 🏗️ Architecture

### Two-Tower Model
```
Company A Features → Tower A (512→256→128) ↘
                                            → Dot Product → Sigmoid → Match Score
Company B Features → Tower B (512→256→128) ↗
```

### Features
- **Dense**: user_overlap_score, funding_amount, employee_count, growth_rate, market_sentiment
- **Sparse**: company_id (categorical embeddings)
- **Culture Vector**: 128-dimensional embeddings from NLP analysis

## 🚀 Quick Start

### 1. GPU Requirements
```bash
# Ensure NVIDIA GPU with CUDA support
nvidia-smi

# Set GPU visibility
export CUDA_VISIBLE_DEVICES=0
```

### 2. Build and Run
```bash
# Build container
docker build -t partner-recommender .

# Run with GPU support
docker run --gpus all -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  partner-recommender
```

### 3. Training
```bash
# Open Jupyter notebook
jupyter notebook notebooks/training_pipeline.ipynb

# Or run training script
python scripts/train_model.py
```

## 📊 API Endpoints

### Get Recommendations
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "TechFlow AI",
    "top_k": 10,
    "include_scores": true
  }'
```

### Batch Recommendations
```bash
curl -X POST "http://localhost:8000/batch-recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "company_ids": ["TechFlow AI", "GreenStart Solutions"],
    "top_k": 5
  }'
```

### Explain Recommendation
```bash
curl -X GET "http://localhost:8000/explain/TechFlow%20AI?partner_id=GreenStart%20Solutions&top_features=10"
```

### Model Status
```bash
curl -X GET "http://localhost:8000/model/status"
```

## 🧪 Training Pipeline

### 1. Data Preparation
```python
# Generate synthetic training data
df = generate_synthetic_data(100000)

# Features include:
# - Company A/B categorical IDs
# - Funding amounts, employee counts
# - Growth rates, market sentiment
# - 128-dimensional culture vectors
# - Binary match labels
```

### 2. NVTabular Preprocessing
```python
# GPU-accelerated preprocessing
categorical_features = categorical_cols >> Categorify()
continuous_features = continuous_cols >> FillMissing() >> Normalize()
culture_features = culture_cols >> FillMissing() >> Normalize()

workflow = nvt.Workflow(categorical_features + continuous_features + culture_features)
```

### 3. HugeCTR Model Training
```python
# Two-tower architecture
config = {
    "layers": [
        # Data layer with dense + sparse features
        # Company A tower: 512 → 256 → 128
        # Company B tower: 512 → 256 → 128  
        # Dot product similarity
        # Sigmoid activation
        # Binary cross-entropy loss
    ]
}

model = hugectr.Model(config)
model.fit(max_iter=20000)
```

## 🎯 Performance Metrics

### Model Performance
- **AUC**: 0.85+ (target)
- **Accuracy**: 0.80+ (target)
- **Precision**: 0.75+ (target)
- **Recall**: 0.70+ (target)

### Inference Performance
- **Latency**: <50ms per recommendation
- **Throughput**: 1000+ recommendations/second
- **GPU Memory**: ~2GB for inference

## 🔧 Configuration

### Environment Variables
```bash
# Model configuration
MODEL_PATH=/app/models
EMBEDDING_DIM=128
BATCH_SIZE=1024

# Feature store
FEATURE_STORE_URL=http://feature-store:8000
FEATURE_STORE_GRPC_URL=feature-store:50051

# GPU settings
CUDA_VISIBLE_DEVICES=0
HUGECTR_GPU_COUNT=1

# Training parameters
LEARNING_RATE=0.001
EPOCHS=100
VALIDATION_SPLIT=0.2
```

### Model Configuration
```json
{
  "solver": {
    "lr_policy": "fixed",
    "max_iter": 20000,
    "batchsize": 1024,
    "lr": 0.001
  },
  "optimizer": {
    "type": "Adam",
    "adam_hparam": {
      "learning_rate": 0.001,
      "beta1": 0.9,
      "beta2": 0.999
    }
  }
}
```

## 🐳 Docker GPU Runtime

### Requirements
```dockerfile
FROM nvidia/merlin-hugectr:23.08

# GPU runtime required
# --gpus all flag needed for container
```

### Docker Compose
```yaml
services:
  partner-recommender:
    build: .
    runtime: nvidia
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

## 📈 Monitoring

### Model Metrics
- Training loss convergence
- Validation AUC progression
- Inference latency distribution
- GPU utilization

### Business Metrics
- Recommendation click-through rate
- Partnership conversion rate
- User engagement with recommendations

## 🔄 Model Updates

### Retraining Pipeline
1. **Data Collection**: Gather new partnership outcomes
2. **Feature Engineering**: Update culture vectors and traction metrics
3. **Model Training**: Retrain HugeCTR model with new data
4. **A/B Testing**: Compare new model against current
5. **Deployment**: Hot-swap model weights

### Continuous Learning
```python
# Trigger retraining
curl -X POST "http://localhost:8000/train" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_path": "/app/data/training_v2",
    "model_config": {...},
    "training_params": {...}
  }'
```

## 🚨 GPU Notes

⚠️ **CRITICAL**: This service requires NVIDIA GPU with CUDA support

### Minimum Requirements
- **GPU**: NVIDIA Tesla V100, RTX 3080, or better
- **CUDA**: 11.8+
- **GPU Memory**: 8GB+ recommended
- **Driver**: 470.57.02+

### Docker GPU Setup
```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### Verify GPU Access
```bash
# Test GPU in container
docker run --gpus all nvidia/cuda:11.8-base-ubuntu20.04 nvidia-smi
```

## 🔗 Integration

### Feature Store Integration
```python
# Get company features
features = await feature_client.get_company_features("TechFlow AI")

# Batch feature retrieval
batch_features = await feature_client.get_batch_features([
    "TechFlow AI", "GreenStart Solutions", "DataViz Pro"
])
```

### API Integration
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://partner-recommender:8000/recommend",
        json={
            "company_id": "TechFlow AI",
            "top_k": 10,
            "filters": {"min_funding": 1000000}
        }
    )
    
    recommendations = response.json()
```

This service provides enterprise-grade partner recommendations using state-of-the-art NVIDIA Merlin HugeCTR technology, optimized for high-performance GPU inference.