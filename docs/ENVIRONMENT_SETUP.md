# Environment Variables Setup Guide

This guide explains how to configure environment variables for Synapse LaunchPad in both development and production environments using 21st.dev secrets manager.

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Production Setup with 21st.dev](#production-setup-with-21stdev)
- [Environment Variables Reference](#environment-variables-reference)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

## 🛠️ Development Setup

### 1. Copy Sample Files

```bash
# Root environment file
cp .env.sample .env

# Service-specific environment files
cp apps/web/.env.sample apps/web/.env.local
cp services/api/.env.sample services/api/.env
cp services/ml-partner-matching/.env.sample services/ml-partner-matching/.env
cp services/ml-campaign-generator/.env.sample services/ml-campaign-generator/.env
cp services/data-pipeline/.env.sample services/data-pipeline/.env
cp services/analytics/.env.sample services/analytics/.env
```

### 2. Configure Required API Keys

#### External Data Sources
- **Crunchbase API**: [Get API key](https://data.crunchbase.com/docs/using-the-api)
- **LinkedIn API**: [LinkedIn Developer Portal](https://developer.linkedin.com/)
- **News API**: [NewsAPI.org](https://newsapi.org/)

#### AI/ML Services
- **OpenAI API**: [OpenAI Platform](https://platform.openai.com/api-keys)
- **NVIDIA API**: [NVIDIA Developer Portal](https://developer.nvidia.com/)

#### Payment Processing
- **Stripe**: [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
- **RevenueCat**: [RevenueCat Dashboard](https://app.revenuecat.com/)

#### Monitoring
- **Sentry**: [Sentry.io](https://sentry.io/)

### 3. Local Development Commands

```bash
# Load environment variables and start development
pnpm dev

# Or with Docker Compose
pnpm docker:up
```

## 🚀 Production Setup with 21st.dev

### 1. Install 21st.dev CLI

```bash
npm install -g @21st-dev/cli
```

### 2. Login to 21st.dev

```bash
21st auth login
```

### 3. Initialize Project

```bash
21st init synapse-launchpad
cd synapse-launchpad
```

### 4. Configure Secrets

#### Method 1: Using CLI Commands

```bash
# Database secrets
21st secrets set DATABASE_URL "postgresql://user:pass@host:5432/synapse_db"
21st secrets set REDIS_URL "redis://host:6379"

# Authentication
21st secrets set JWT_SECRET "your-super-secret-jwt-key-min-32-characters"

# External APIs
21st secrets set CRUNCHBASE_KEY "your-crunchbase-api-key"
21st secrets set LINKEDIN_TOKEN "your-linkedin-api-token"
21st secrets set NEWSAPI_KEY "your-newsapi-key"

# AI Services
21st secrets set OPENAI_API_KEY "sk-your-openai-api-key"
21st secrets set NVIDIA_API_KEY "your-nvidia-api-key"

# Payment Processing
21st secrets set STRIPE_SECRET "sk_live_your-stripe-secret-key"
21st secrets set REVENUECAT_PUBLIC_KEY "your-revenuecat-public-key"

# Monitoring
21st secrets set SENTRY_DSN "https://your-sentry-dsn@sentry.io/project-id"
```

#### Method 2: Using Environment File

```bash
# Upload all secrets from .env file
21st secrets import .env.production
```

#### Method 3: Using 21st.dev Dashboard

1. Go to [21st.dev Dashboard](https://dashboard.21st.dev)
2. Select your project
3. Navigate to "Secrets" section
4. Add secrets manually through the UI

### 5. Configure Deployment

Create `21st.config.yml`:

```yaml
# 21st.config.yml
name: synapse-launchpad
version: 1.0.0

services:
  frontend:
    type: nextjs
    build:
      command: pnpm build --filter=@synapse/web
      output: apps/web/.next
    env:
      - NEXT_PUBLIC_API_URL
      - NEXT_PUBLIC_SENTRY_DSN
      - NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY

  api:
    type: nodejs
    build:
      command: pnpm build --filter=@synapse/api
      output: services/api/dist
    env:
      - DATABASE_URL
      - REDIS_URL
      - JWT_SECRET
      - CRUNCHBASE_KEY
      - LINKEDIN_TOKEN
      - NEWSAPI_KEY
      - STRIPE_SECRET
      - SENTRY_DSN

  ml-partner-matching:
    type: python
    build:
      command: pip install -r requirements.txt
      output: services/ml-partner-matching
    env:
      - REDIS_URL
      - NVIDIA_API_KEY
      - CRUNCHBASE_KEY
      - SENTRY_DSN

  ml-campaign-generator:
    type: python
    build:
      command: pip install -r requirements.txt
      output: services/ml-campaign-generator
    env:
      - REDIS_URL
      - OPENAI_API_KEY
      - SENTRY_DSN

databases:
  postgres:
    type: postgresql
    version: 15
  
  redis:
    type: redis
    version: 7
```

### 6. Deploy to Production

```bash
# Deploy all services
21st deploy

# Deploy specific service
21st deploy --service=frontend
21st deploy --service=api
```

### 7. Monitor Deployment

```bash
# Check deployment status
21st status

# View logs
21st logs --service=api --follow

# Check secrets
21st secrets list
```

## 📚 Environment Variables Reference

### Core Services

| Variable | Service | Required | Description |
|----------|---------|----------|-------------|
| `DATABASE_URL` | All | ✅ | PostgreSQL connection string |
| `REDIS_URL` | All | ✅ | Redis connection string |
| `JWT_SECRET` | API | ✅ | JWT signing secret (min 32 chars) |
| `SENTRY_DSN` | All | ✅ | Sentry error tracking DSN |

### External APIs

| Variable | Service | Required | Description |
|----------|---------|----------|-------------|
| `CRUNCHBASE_KEY` | Data Pipeline, ML | ✅ | Crunchbase API key for startup data |
| `LINKEDIN_TOKEN` | Data Pipeline, ML | ✅ | LinkedIn API token |
| `NEWSAPI_KEY` | Data Pipeline | ✅ | News API key for sentiment analysis |
| `OPENAI_API_KEY` | Campaign Generator | ✅ | OpenAI API key for campaign generation |
| `NVIDIA_API_KEY` | Partner Matching | ✅ | NVIDIA API key for Merlin models |

### Payment Processing

| Variable | Service | Required | Description |
|----------|---------|----------|-------------|
| `STRIPE_SECRET` | API | ✅ | Stripe secret key |
| `STRIPE_PUBLISHABLE_KEY` | Frontend | ✅ | Stripe publishable key |
| `REVENUECAT_PUBLIC_KEY` | Frontend | ✅ | RevenueCat public key |
| `REVENUECAT_SECRET_KEY` | API | ✅ | RevenueCat secret key |

### Frontend Configuration

| Variable | Service | Required | Description |
|----------|---------|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Frontend | ✅ | API gateway URL |
| `NEXT_PUBLIC_SENTRY_DSN` | Frontend | ✅ | Sentry DSN for frontend |
| `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` | Frontend | ✅ | Stripe publishable key |

## 🔒 Security Best Practices

### 1. Secret Rotation

```bash
# Rotate secrets regularly
21st secrets rotate JWT_SECRET
21st secrets rotate DATABASE_URL
```

### 2. Environment Separation

```bash
# Use different secrets for different environments
21st secrets set --env=staging DATABASE_URL "staging-db-url"
21st secrets set --env=production DATABASE_URL "production-db-url"
```

### 3. Access Control

```bash
# Limit access to production secrets
21st access grant user@company.com --env=production --role=viewer
21st access grant admin@company.com --env=production --role=admin
```

### 4. Audit Logging

```bash
# View secret access logs
21st audit secrets --env=production
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Missing Environment Variables

```bash
# Check which secrets are missing
21st secrets validate

# List all configured secrets
21st secrets list --show-values=false
```

#### 2. Service Connection Issues

```bash
# Test database connection
21st exec --service=api -- node -e "console.log(process.env.DATABASE_URL)"

# Test Redis connection
21st exec --service=api -- node -e "console.log(process.env.REDIS_URL)"
```

#### 3. API Key Validation

```bash
# Test external API keys
21st exec --service=ml-campaign-generator -- python -c "
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')
print('OpenAI API key is valid')
"
```

### Debug Commands

```bash
# View service environment variables
21st env --service=api

# Check service health
21st health --service=all

# View deployment logs
21st logs --service=api --since=1h
```

### Support

- **21st.dev Documentation**: [docs.21st.dev](https://docs.21st.dev)
- **21st.dev Support**: [support@21st.dev](mailto:support@21st.dev)
- **Synapse LaunchPad Issues**: [GitHub Issues](https://github.com/synapse-launchpad/synapse-launchpad/issues)

## 📝 Additional Resources

- [21st.dev Secrets Management Guide](https://docs.21st.dev/secrets)
- [21st.dev Deployment Guide](https://docs.21st.dev/deployment)
- [Environment Variables Best Practices](https://12factor.net/config)
- [Docker Secrets Management](https://docs.docker.com/engine/swarm/secrets/)