# Synapse LaunchPad

AI-powered startup matchmaking platform that combines data-driven insights with behavioral science to accelerate growth through strategic partnerships.

## 🚀 Features

- **Market Pulse Scanner**: Real-time analysis of funding news, industry trends, and sentiment
- **Smart Matchmaking**: AI-powered partner recommendations with 96% accuracy
- **Campaign Generation**: Psychologically-optimized marketing campaigns
- **Behavioral Analytics**: Deep insights using psychological triggers and user behavior
- **Adaptive Learning**: Continuously improving recommendations based on performance

## 🏗️ Architecture

This is a mono-repo containing:

- **Frontend**: Next.js 14 + Tailwind CSS + Expo SDK (for future mobile)
- **Backend Services**: Python 3.11 microservices managed by Nodely
- **API Gateway**: Node.js/Express with TypeScript
- **ML Services**: NVIDIA Merlin for partner matching, OpenAI for campaign generation
- **Infrastructure**: Docker Compose, PostgreSQL, Redis

## 📁 Project Structure

```
synapse-launchpad/
├── apps/
│   ├── web/                    # Next.js frontend application
│   └── mobile/                 # Expo/React Native mobile app
├── services/
│   ├── api/                    # Node.js API gateway
│   ├── ml-partner-matching/    # Python ML service for partner matching
│   ├── ml-campaign-generator/  # Python ML service for campaign generation
│   ├── data-pipeline/          # Data ingestion and processing
│   └── analytics/              # Analytics and reporting service
├── packages/
│   └── shared/                 # Shared TypeScript types and utilities
├── docker-compose.yml          # Container orchestration
├── .github/workflows/          # CI/CD pipelines
└── README.md
```

## 🛠️ Development Setup

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- pnpm 8+

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd synapse-launchpad
   ```

2. **Install dependencies**
   ```bash
   pnpm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start development environment**
   ```bash
   # Start all services with Docker
   pnpm docker:up
   
   # Or start individual services
   pnpm dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - API Gateway: http://localhost:8000
   - ML Partner Matching: http://localhost:8001
   - ML Campaign Generator: http://localhost:8002

## 🧪 Testing

```bash
# Run all tests
pnpm test

# Run specific service tests
pnpm test --filter=@synapse/web
pnpm test --filter=@synapse/api

# Run end-to-end tests
pnpm test:e2e
```

## 🚀 Deployment

### Using 21st.dev (Recommended)

The project is configured for deployment on 21st.dev with GitHub Actions:

1. Push to `main` branch
2. GitHub Actions will automatically build and deploy
3. Monitor deployment in 21st.dev dashboard

### Manual Docker Deployment

```bash
# Build all services
pnpm docker:build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Monitoring

- **Error Tracking**: Sentry integration across all services
- **Performance**: Built-in analytics dashboard
- **Logs**: Centralized logging with Docker Compose
- **Health Checks**: Available at `/health` endpoints

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example`):

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `OPENAI_API_KEY`: For AI campaign generation
- `CRUNCHBASE_API_KEY`: For market data
- `SENTRY_DSN`: Error monitoring
- `JWT_SECRET`: Authentication secret

### Service Configuration

Each service has its own configuration:

- **Frontend**: `apps/web/next.config.js`
- **API**: `services/api/src/config/index.ts`
- **ML Services**: Environment-based configuration

## 🔒 Security

We take security seriously. For details on our security practices, including:

- OWASP security measures
- Rate limiting implementation
- API key rotation guidelines
- GDPR/CCPA compliance
- Data deletion processes
- PII scrubbing in Sentry

Please see our [Security Documentation](docs/security.md).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- Documentation: [docs.synapse-launchpad.com](https://docs.synapse-launchpad.com)
- Issues: [GitHub Issues](https://github.com/synapse-launchpad/synapse-launchpad/issues)
- Email: support@synapse-launchpad.com

## 🎯 Roadmap

- [ ] Mobile app with React Native/Expo
- [ ] Advanced ML models with NVIDIA Merlin
- [ ] Real-time collaboration features
- [ ] Enterprise SSO integration
- [ ] Advanced analytics and reporting
- [ ] API marketplace for third-party integrations

---

Built with ❤️ by the Synapse LaunchPad Team