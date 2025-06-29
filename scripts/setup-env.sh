#!/bin/bash

# =============================================================================
# SYNAPSE LAUNCHPAD - ENVIRONMENT SETUP SCRIPT
# =============================================================================
# This script helps set up environment variables for development and production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate random secret
generate_secret() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-32
}

# Function to setup development environment
setup_development() {
    print_header "SETTING UP DEVELOPMENT ENVIRONMENT"
    
    # Copy sample files
    print_status "Copying environment sample files..."
    
    if [ ! -f .env ]; then
        cp .env.sample .env
        print_status "Created .env from .env.sample"
    else
        print_warning ".env already exists, skipping..."
    fi
    
    if [ ! -f apps/web/.env.local ]; then
        cp apps/web/.env.sample apps/web/.env.local
        print_status "Created apps/web/.env.local"
    else
        print_warning "apps/web/.env.local already exists, skipping..."
    fi
    
    # Copy service environment files
    services=("api" "ml-partner-matching" "ml-campaign-generator" "data-pipeline" "analytics")
    
    for service in "${services[@]}"; do
        if [ ! -f "services/$service/.env" ]; then
            cp "services/$service/.env.sample" "services/$service/.env"
            print_status "Created services/$service/.env"
        else
            print_warning "services/$service/.env already exists, skipping..."
        fi
    done
    
    # Generate JWT secret
    print_status "Generating JWT secret..."
    jwt_secret=$(generate_secret)
    
    # Update .env files with generated secret
    if command_exists sed; then
        sed -i.bak "s/your-super-secret-jwt-key-change-this-in-production-min-32-chars/$jwt_secret/g" .env
        sed -i.bak "s/your-super-secret-jwt-key-change-this-in-production-min-32-chars/$jwt_secret/g" services/api/.env
        rm -f .env.bak services/api/.env.bak
        print_status "Updated JWT secret in environment files"
    fi
    
    print_status "Development environment setup complete!"
    print_warning "Please update the following API keys in your .env files:"
    echo "  - CRUNCHBASE_KEY"
    echo "  - LINKEDIN_TOKEN"
    echo "  - NEWSAPI_KEY"
    echo "  - OPENAI_API_KEY"
    echo "  - NVIDIA_API_KEY"
    echo "  - STRIPE_SECRET"
    echo "  - REVENUECAT_PUBLIC_KEY"
    echo "  - SENTRY_DSN"
}

# Function to setup production environment with 21st.dev
setup_production() {
    print_header "SETTING UP PRODUCTION ENVIRONMENT WITH 21ST.DEV"
    
    # Check if 21st CLI is installed
    if ! command_exists 21st; then
        print_error "21st.dev CLI not found. Installing..."
        npm install -g @21st-dev/cli
    fi
    
    # Check if user is logged in
    if ! 21st auth status >/dev/null 2>&1; then
        print_status "Please log in to 21st.dev..."
        21st auth login
    fi
    
    # Initialize project if not already done
    if [ ! -f 21st.config.yml ]; then
        print_error "21st.config.yml not found. Please run this script from the project root."
        exit 1
    fi
    
    print_status "Setting up production secrets..."
    
    # Prompt for required secrets
    read -p "Enter your Crunchbase API key: " crunchbase_key
    read -p "Enter your LinkedIn API token: " linkedin_token
    read -p "Enter your News API key: " newsapi_key
    read -p "Enter your OpenAI API key: " openai_key
    read -p "Enter your NVIDIA API key: " nvidia_key
    read -p "Enter your Stripe secret key: " stripe_secret
    read -p "Enter your RevenueCat public key: " revenuecat_key
    read -p "Enter your Sentry DSN: " sentry_dsn
    read -p "Enter your production database URL: " database_url
    read -p "Enter your production Redis URL: " redis_url
    
    # Generate production JWT secret
    jwt_secret=$(generate_secret)
    
    # Set secrets in 21st.dev
    print_status "Uploading secrets to 21st.dev..."
    
    21st secrets set DATABASE_URL "$database_url"
    21st secrets set REDIS_URL "$redis_url"
    21st secrets set JWT_SECRET "$jwt_secret"
    21st secrets set CRUNCHBASE_KEY "$crunchbase_key"
    21st secrets set LINKEDIN_TOKEN "$linkedin_token"
    21st secrets set NEWSAPI_KEY "$newsapi_key"
    21st secrets set OPENAI_API_KEY "$openai_key"
    21st secrets set NVIDIA_API_KEY "$nvidia_key"
    21st secrets set STRIPE_SECRET "$stripe_secret"
    21st secrets set REVENUECAT_PUBLIC_KEY "$revenuecat_key"
    21st secrets set SENTRY_DSN "$sentry_dsn"
    
    print_status "Production environment setup complete!"
    print_status "You can now deploy with: 21st deploy"
}

# Function to validate environment
validate_environment() {
    print_header "VALIDATING ENVIRONMENT CONFIGURATION"
    
    required_vars=(
        "DATABASE_URL"
        "REDIS_URL"
        "JWT_SECRET"
        "SENTRY_DSN"
    )
    
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -eq 0 ]; then
        print_status "All required environment variables are set!"
    else
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        exit 1
    fi
}

# Function to show help
show_help() {
    echo "Synapse LaunchPad Environment Setup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  dev         Setup development environment"
    echo "  prod        Setup production environment with 21st.dev"
    echo "  validate    Validate current environment configuration"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev      # Setup development environment"
    echo "  $0 prod     # Setup production environment"
    echo "  $0 validate # Validate environment variables"
}

# Main script logic
case "${1:-}" in
    "dev")
        setup_development
        ;;
    "prod")
        setup_production
        ;;
    "validate")
        validate_environment
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac