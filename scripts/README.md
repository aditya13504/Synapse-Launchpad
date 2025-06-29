# Synapse LaunchPad Deployment Scripts

This directory contains scripts for deploying and managing the Synapse LaunchPad application.

## 🚀 Production Deployment

### Prerequisites

- Kubernetes cluster with GPU support
- kubectl configured to connect to your cluster
- Helm 3.2.0+
- Docker CLI with registry access
- 21st.dev CLI installed and configured

### One-Command Deployment

The `deploy-prod.sh` script provides a one-command deployment solution:

```bash
./scripts/deploy-prod.sh
```

This script:
1. Builds and pushes Docker images
2. Syncs secrets from 21st.dev
3. Deploys the application using Helm
4. Configures auto-scaling
5. Sets up monitoring

### Options

```
Usage: ./scripts/deploy-prod.sh [options]

Options:
  --namespace NAME    Kubernetes namespace to deploy to (default: synapse-prod)
  --release NAME      Helm release name (default: synapse)
  --values FILE       Custom values file (default: none)
  --timeout DURATION  Timeout for deployment (default: 10m)
  --no-wait           Don't wait for deployment to complete
  --dry-run           Perform a dry run without making changes
  --skip-secrets      Skip syncing secrets from 21st.dev
  --skip-build        Skip building and pushing Docker images
  --help              Show this help message
```

### Examples

```bash
# Deploy to a different namespace
./scripts/deploy-prod.sh --namespace synapse-staging

# Use custom values
./scripts/deploy-prod.sh --values my-custom-values.yaml

# Dry run to see what would be deployed
./scripts/deploy-prod.sh --dry-run

# Skip building images (use existing ones)
./scripts/deploy-prod.sh --skip-build
```

## 🔄 Continuous Deployment

The deployment script is designed to work with CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        
      - name: Set up Helm
        uses: azure/setup-helm@v3
        
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          kubeconfig: ${{ secrets.KUBE_CONFIG }}
          
      - name: Login to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Deploy to Production
        run: ./scripts/deploy-prod.sh
        env:
          TWENTYFIRST_API_KEY: ${{ secrets.TWENTYFIRST_API_KEY }}
```

## 🔍 Monitoring Deployment

After deployment, you can monitor the status with:

```bash
# Check pod status
kubectl get pods -n synapse-prod

# Check services
kubectl get svc -n synapse-prod

# Check ingress
kubectl get ingress -n synapse-prod

# Check HPA status
kubectl get hpa -n synapse-prod

# View logs
kubectl logs -n synapse-prod deployment/frontend
kubectl logs -n synapse-prod deployment/api
kubectl logs -n synapse-prod deployment/partner-recommender
```

## 🔄 Rollback

To rollback to a previous release:

```bash
# List Helm releases
helm list -n synapse-prod

# Rollback to previous release
helm rollback synapse 1 -n synapse-prod
```

## 🚨 Troubleshooting

### Common Issues

1. **GPU not available**
   - Check if GPU node pool exists
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