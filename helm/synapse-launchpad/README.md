# Synapse LaunchPad Helm Chart

This Helm chart deploys the Synapse LaunchPad application to Kubernetes, including all microservices, databases, and supporting infrastructure.

## 🚀 Features

- **Complete Deployment**: Deploys all Synapse LaunchPad components
- **GPU Support**: Configures GPU node pools for ML services
- **Auto-scaling**: Horizontal Pod Autoscaling based on CPU and memory usage
- **External Secrets**: Integration with 21st.dev for secure secret management
- **Ingress Configuration**: TLS-enabled ingress for web and API services
- **Monitoring**: Prometheus and Grafana integration

## 📋 Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- kubectl configured to connect to your Kubernetes cluster
- NVIDIA GPU Operator installed (for GPU support)
- External Secrets Operator installed
- 21st.dev CLI installed and configured

## 🛠️ Installation

```bash
# Add the Helm repository (if hosted)
helm repo add synapse-launchpad https://charts.synapse-launchpad.com
helm repo update

# Install the chart
helm install synapse helm/synapse-launchpad \
  --namespace synapse-prod \
  --create-namespace

# Or use the deployment script
./scripts/deploy-prod.sh
```

## ⚙️ Configuration

### GPU Node Pool

This chart is configured to use a dedicated GPU node pool for ML services. Ensure your Kubernetes cluster has a node pool with the following label:

```yaml
cloud.google.com/gke-accelerator: nvidia-tesla-t4
```

### Auto-scaling Configuration

The chart configures Horizontal Pod Autoscalers (HPAs) with the following default settings:

- CPU threshold: 70%
- Memory threshold: 80%
- Scale up: Add up to 100% more pods every 15 seconds
- Scale down: Remove up to 10% of pods every 60 seconds
- Scale up stabilization window: 5 minutes
- Scale down stabilization window: 10 minutes

### External Secrets

The chart integrates with External Secrets Operator to sync secrets from 21st.dev:

1. Create a SecretStore that connects to 21st.dev
2. Define ExternalSecret resources that map to 21st.dev secrets
3. Automatically sync secrets to Kubernetes

## 📊 Monitoring

The chart includes Prometheus and Grafana for monitoring:

- **Prometheus**: Collects metrics from all services
- **Grafana**: Provides dashboards for visualizing metrics
- **Alertmanager**: Sends alerts to Slack and email

## 🔍 Values

| Parameter | Description | Default |
|-----------|-------------|---------|
| `global.environment` | Environment name | `production` |
| `global.domain` | Base domain for the application | `synapse-launchpad.com` |
| `global.imageRegistry` | Container image registry | `ghcr.io` |
| `frontend.replicaCount` | Number of frontend replicas | `2` |
| `frontend.autoscaling.enabled` | Enable autoscaling for frontend | `true` |
| `frontend.autoscaling.minReplicas` | Minimum frontend replicas | `2` |
| `frontend.autoscaling.maxReplicas` | Maximum frontend replicas | `10` |
| `partnerRecommender.gpuEnabled` | Enable GPU for partner recommender | `true` |
| `partnerRecommender.resources.limits.nvidia.com/gpu` | Number of GPUs per pod | `1` |
| `featureStore.gpuEnabled` | Enable GPU for feature store | `true` |
| `postgresql.auth.username` | PostgreSQL username | `postgres` |
| `postgresql.primary.persistence.size` | PostgreSQL storage size | `20Gi` |

## 📝 Examples

### Production Deployment with Custom Domain

```bash
helm install synapse helm/synapse-launchpad \
  --namespace synapse-prod \
  --set global.domain=app.mycompany.com \
  --set frontend.ingress.hosts[0].host=app.mycompany.com \
  --set api.ingress.hosts[0].host=api.mycompany.com
```

### Deployment with Increased Resources

```bash
helm install synapse helm/synapse-launchpad \
  --namespace synapse-prod \
  --set api.resources.requests.cpu=2000m \
  --set api.resources.requests.memory=4Gi \
  --set partnerRecommender.resources.limits.nvidia.com/gpu=2
```

### Deployment without GPU Support

```bash
helm install synapse helm/synapse-launchpad \
  --namespace synapse-prod \
  --set partnerRecommender.gpuEnabled=false \
  --set featureStore.gpuEnabled=false
```

## 🔄 Upgrading

To upgrade the deployment:

```bash
helm upgrade synapse helm/synapse-launchpad \
  --namespace synapse-prod
```

## 🧹 Uninstalling

To uninstall/delete the deployment:

```bash
helm uninstall synapse --namespace synapse-prod
```

## 🔒 Security Considerations

- All sensitive data is stored in Kubernetes secrets
- Secrets are managed through External Secrets Operator
- TLS is enabled for all ingress resources
- Pod Security Policies are applied
- Network Policies restrict communication between services

## 🚨 Troubleshooting

### Common Issues

1. **GPU not available**
   - Check if the GPU node pool exists
   - Verify NVIDIA device plugin is installed
   - Check GPU quota in your cloud provider

2. **External Secrets not syncing**
   - Verify 21st.dev API key is correct
   - Check External Secrets Operator logs
   - Ensure secrets exist in 21st.dev

3. **Pods stuck in Pending state**
   - Check if resources are available
   - Verify node selectors and tolerations
   - Check PersistentVolumeClaims

### Debugging Commands

```bash
# Check pod status
kubectl get pods -n synapse-prod

# Check pod logs
kubectl logs -n synapse-prod deployment/partner-recommender

# Check HPA status
kubectl get hpa -n synapse-prod

# Check External Secrets
kubectl get externalsecret -n synapse-prod
```