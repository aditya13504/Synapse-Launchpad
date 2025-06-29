#!/bin/bash

# =============================================================================
# SYNAPSE LAUNCHPAD - PRODUCTION DEPLOYMENT SCRIPT
# =============================================================================
# This script deploys the Synapse LaunchPad application to Kubernetes using Helm

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}==============================================================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}==============================================================================${NC}"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    print_error "helm is not installed. Please install it first."
    exit 1
fi

# Check if 21st CLI is installed
if ! command -v 21st &> /dev/null; then
    print_warning "21st CLI is not installed. External Secrets sync may not work properly."
    print_warning "Install with: npm install -g @21st-dev/cli"
fi

# Default values
NAMESPACE="synapse-prod"
RELEASE_NAME="synapse"
VALUES_FILE="helm/synapse-launchpad/values.yaml"
CUSTOM_VALUES_FILE=""
TIMEOUT="10m"
WAIT=true
DRY_RUN=false
SKIP_SECRETS=false
SKIP_BUILD=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --namespace)
            NAMESPACE="$2"
            shift
            shift
            ;;
        --release)
            RELEASE_NAME="$2"
            shift
            shift
            ;;
        --values)
            CUSTOM_VALUES_FILE="$2"
            shift
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift
            shift
            ;;
        --no-wait)
            WAIT=false
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-secrets)
            SKIP_SECRETS=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --namespace NAME    Kubernetes namespace to deploy to (default: synapse-prod)"
            echo "  --release NAME      Helm release name (default: synapse)"
            echo "  --values FILE       Custom values file (default: none)"
            echo "  --timeout DURATION  Timeout for deployment (default: 10m)"
            echo "  --no-wait           Don't wait for deployment to complete"
            echo "  --dry-run           Perform a dry run without making changes"
            echo "  --skip-secrets      Skip syncing secrets from 21st.dev"
            echo "  --skip-build        Skip building and pushing Docker images"
            echo "  --help              Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_header "SYNAPSE LAUNCHPAD PRODUCTION DEPLOYMENT"

# Create namespace if it doesn't exist
if ! kubectl get namespace $NAMESPACE &> /dev/null; then
    print_status "Creating namespace: $NAMESPACE"
    kubectl create namespace $NAMESPACE
else
    print_status "Using existing namespace: $NAMESPACE"
fi

# Build and push Docker images if not skipped
if [ "$SKIP_BUILD" = false ]; then
    print_status "Building and pushing Docker images..."
    
    # Check if we're logged in to the container registry
    if ! docker info | grep -q "Username"; then
        print_warning "Not logged in to container registry. Please log in first."
        exit 1
    fi
    
    # Build and push images
    print_status "Building and pushing images with docker-compose..."
    docker-compose build
    docker-compose push
    
    print_status "Docker images built and pushed successfully."
fi

# Sync secrets from 21st.dev if not skipped
if [ "$SKIP_SECRETS" = false ]; then
    if command -v 21st &> /dev/null; then
        print_status "Syncing secrets from 21st.dev..."
        
        # Check if we're logged in to 21st.dev
        if ! 21st auth status &> /dev/null; then
            print_warning "Not logged in to 21st.dev. Please log in first with: 21st auth login"
            exit 1
        fi
        
        # Create Kubernetes secret for 21st.dev API key
        API_KEY=$(21st auth token)
        kubectl create secret generic twentyfirst-api-key \
            --namespace $NAMESPACE \
            --from-literal=api-key=$API_KEY \
            --dry-run=client -o yaml | kubectl apply -f -
        
        print_status "21st.dev API key secret created successfully."
    else
        print_warning "21st CLI not installed. Skipping secrets sync."
    fi
fi

# Set up Helm command
HELM_CMD="helm upgrade --install $RELEASE_NAME helm/synapse-launchpad \
    --namespace $NAMESPACE \
    --timeout $TIMEOUT"

# Add custom values file if provided
if [ -n "$CUSTOM_VALUES_FILE" ]; then
    if [ -f "$CUSTOM_VALUES_FILE" ]; then
        HELM_CMD="$HELM_CMD --values $CUSTOM_VALUES_FILE"
    else
        print_error "Custom values file not found: $CUSTOM_VALUES_FILE"
        exit 1
    fi
fi

# Add wait flag if enabled
if [ "$WAIT" = true ]; then
    HELM_CMD="$HELM_CMD --wait"
fi

# Add dry-run flag if enabled
if [ "$DRY_RUN" = true ]; then
    HELM_CMD="$HELM_CMD --dry-run"
fi

# Deploy with Helm
print_status "Deploying Synapse LaunchPad to Kubernetes..."
print_status "Command: $HELM_CMD"

if [ "$DRY_RUN" = true ]; then
    print_warning "DRY RUN: No changes will be made"
fi

eval $HELM_CMD

# Check deployment status
if [ "$DRY_RUN" = false ]; then
    print_status "Checking deployment status..."
    kubectl get pods -n $NAMESPACE -l release=$RELEASE_NAME
    
    # Check if any pods are not ready
    NOT_READY=$(kubectl get pods -n $NAMESPACE -l release=$RELEASE_NAME -o jsonpath='{.items[?(@.status.phase!="Running")].metadata.name}')
    if [ -n "$NOT_READY" ]; then
        print_warning "Some pods are not ready yet. Check their status with:"
        print_warning "kubectl get pods -n $NAMESPACE -l release=$RELEASE_NAME"
    else
        print_status "All pods are running!"
    fi
    
    # Get ingress URLs
    print_status "Application URLs:"
    kubectl get ingress -n $NAMESPACE -l release=$RELEASE_NAME -o jsonpath='{range .items[*]}{.spec.rules[0].host}{"\n"}{end}'
fi

print_header "DEPLOYMENT COMPLETED SUCCESSFULLY"
print_status "Synapse LaunchPad has been deployed to Kubernetes!"
print_status "To check the status of your deployment, run:"
print_status "kubectl get all -n $NAMESPACE -l release=$RELEASE_NAME"