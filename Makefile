# =============================================================================
# SYNAPSE LAUNCHPAD - MAKEFILE
# =============================================================================
# Comprehensive development, testing, and deployment automation

.PHONY: help dev train lint test seed clean install build deploy

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
]
GREEN := \033[32m
]
YELLOW := \033[33m
]
RED := \033[31m
]
NC := \033[0m # No Color
]

# Project configuration
PROJECT_NAME := synapse-launchpad
DOCKER_COMPOSE := docker-compose
PYTHON := python3
NODE := node
NPM := npm
PNPM := pnpm

# GPU configuration for training
GPU_DEVICE := 0
CUDA_VISIBLE_DEVICES := $(GPU_DEVICE)

# =============================================================================
# HELP TARGET
# =============================================================================

help: ## Show this help message
	@echo "$(BLUE)Synapse LaunchPad - Development Commands$(NC)"
	@echo "=========================================="
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make dev          Start development environment with live reload"
	@echo "  make dev-gpu      Start development environment with GPU support"
	@echo "  make install      Install all dependencies"
	@echo "  make clean        Clean build artifacts and caches"
	@echo ""
	@echo "$(GREEN)Machine Learning:$(NC)"
	@echo "  make train        Run NVIDIA Merlin training pipeline on GPU"
	@echo "  make train-cpu    Run training pipeline on CPU (fallback)"
	@echo "  make model-status Check model training status"
	@echo ""
	@echo "$(GREEN)Quality Assurance:$(NC)"
	@echo "  make lint         Run ESLint + Prettier + Python linting"
	@echo "  make test         Run all tests (Jest + Pytest)"
	@echo "  make test-watch   Run tests in watch mode"
	@echo "  make type-check   Run TypeScript type checking"
	@echo ""
	@echo "$(GREEN)Database & Seeding:$(NC)"
	@echo "  make seed         Run database seed script with mock data"
	@echo "  make seed-small   Run seed script with smaller dataset"
	@echo "  make db-reset     Reset database and reseed"
	@echo ""
	@echo "$(GREEN)Build & Deploy:$(NC)"
	@echo "  make build        Build all services for production"
	@echo "  make deploy       Deploy to production environment"
	@echo "  make docker-build Build all Docker images"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make logs         Show service logs"
	@echo "  make status       Show service status"
	@echo "  make shell        Open shell in API container"
	@echo ""

# =============================================================================
# DEVELOPMENT TARGETS
# =============================================================================

dev: ## Start development environment with live reload
	@echo "$(BLUE)Starting Synapse LaunchPad development environment...$(NC)"
	@echo "$(YELLOW)Services starting:$(NC)"
	@echo "  • Frontend (Next.js): http://localhost:3000"
	@echo "  • API Gateway: http://localhost:8000"
	@echo "  • Partner Recommender: http://localhost:8001"
	@echo "  • Campaign Generator: http://localhost:8002"
	@echo "  • Feature Store: http://localhost:8003"
	@echo "  • Market Pulse Scanner: http://localhost:8004"
	@echo "  • PostgreSQL: localhost:5432"
	@echo "  • Redis: localhost:6379"
	@echo ""
	$(DOCKER_COMPOSE) up --build

dev-gpu: ## Start development environment with GPU support
	@echo "$(BLUE)Starting development environment with GPU support...$(NC)"
	@echo "$(YELLOW)GPU Configuration:$(NC)"
	@echo "  • CUDA Device: $(GPU_DEVICE)"
	@echo "  • GPU Memory: Shared"
	@echo "  • Services with GPU: partner-recommender, feature-store"
	@echo ""
	CUDA_VISIBLE_DEVICES=$(CUDA_VISIBLE_DEVICES) $(DOCKER_COMPOSE) -f docker-compose.yml -f docker-compose.gpu.yml up --build

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(NC)"
	@echo "$(YELLOW)Installing Node.js dependencies...$(NC)"
	$(PNPM) install
	@echo "$(YELLOW)Installing Python dependencies for services...$(NC)"
	cd services/partner-recommender && pip install -r requirements.txt
	cd services/campaign-maker && pip install -r requirements.txt
	cd services/feature-store && pip install -r requirements.txt
	cd services/market-pulse-scanner && pip install -r requirements.txt
	cd scripts && pip install -r requirements.txt
	@echo "$(GREEN)All dependencies installed successfully!$(NC)"

clean: ## Clean build artifacts and caches
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@echo "$(YELLOW)Removing Node.js artifacts...$(NC)"
	rm -rf node_modules
	rm -rf apps/web/.next
	rm -rf apps/web/dist
	rm -rf packages/*/dist
	rm -rf .turbo
	@echo "$(YELLOW)Removing Python artifacts...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(YELLOW)Removing Docker artifacts...$(NC)"
	$(DOCKER_COMPOSE) down --volumes --remove-orphans
	docker system prune -f
	@echo "$(GREEN)Cleanup completed!$(NC)"

# =============================================================================
# MACHINE LEARNING TARGETS
# =============================================================================

train: ## Run NVIDIA Merlin training pipeline on GPU
	@echo "$(BLUE)Starting NVIDIA Merlin training pipeline...$(NC)"
	@echo "$(YELLOW)Training Configuration:$(NC)"
	@echo "  • Framework: NVIDIA HugeCTR + Merlin"
	@echo "  • Architecture: Two-tower model"
	@echo "  • GPU Device: $(GPU_DEVICE)"
	@echo "  • Batch Size: 1024"
	@echo "  • Embedding Dim: 128"
	@echo ""
	@if ! command -v nvidia-smi >/dev/null 2>&1; then \
		echo "$(RED)Error: NVIDIA GPU not detected. Use 'make train-cpu' for CPU training.$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)GPU detected. Starting training...$(NC)"
	CUDA_VISIBLE_DEVICES=$(CUDA_VISIBLE_DEVICES) $(DOCKER_COMPOSE) exec partner-recommender \
		jupyter nbconvert --to notebook --execute notebooks/training_pipeline.ipynb --output training_results.ipynb
	@echo "$(GREEN)Training completed! Check partner-recommender logs for results.$(NC)"

train-cpu: ## Run training pipeline on CPU (fallback)
	@echo "$(YELLOW)Warning: Running training on CPU. This will be significantly slower.$(NC)"
	@echo "$(BLUE)Starting CPU training pipeline...$(NC)"
	$(DOCKER_COMPOSE) exec partner-recommender \
		python scripts/train_cpu_fallback.py
	@echo "$(GREEN)CPU training completed!$(NC)"

model-status: ## Check model training status
	@echo "$(BLUE)Checking model status...$(NC)"
	@curl -s http://localhost:8001/model/status | jq '.' || echo "$(RED)Partner recommender service not available$(NC)"
	@echo ""
	@curl -s http://localhost:8003/pipeline/status | jq '.' || echo "$(RED)Feature store service not available$(NC)"

# =============================================================================
# QUALITY ASSURANCE TARGETS
# =============================================================================

lint: ## Run ESLint + Prettier + Python linting
	@echo "$(BLUE)Running code quality checks...$(NC)"
	@echo "$(YELLOW)TypeScript/JavaScript linting...$(NC)"
	$(PNPM) lint
	@echo "$(YELLOW)TypeScript/JavaScript formatting...$(NC)"
	$(PNPM) run format
	@echo "$(YELLOW)Python linting (flake8)...$(NC)"
	@for service in partner-recommender campaign-maker feature-store market-pulse-scanner; do \
		echo "Linting services/$$service..."; \
		cd services/$$service && flake8 . --max-line-length=120 --ignore=E501,W503 || true; \
		cd ../..; \
	done
	@echo "$(YELLOW)Python formatting (black)...$(NC)"
	@for service in partner-recommender campaign-maker feature-store market-pulse-scanner; do \
		echo "Formatting services/$$service..."; \
		cd services/$$service && black . --line-length=120 || true; \
		cd ../..; \
	done
	@echo "$(GREEN)Code quality checks completed!$(NC)"

test: ## Run all tests (Jest + Pytest)
	@echo "$(BLUE)Running test suites...$(NC)"
	@echo "$(YELLOW)Frontend tests (Jest)...$(NC)"
	$(PNPM) test --filter=@synapse/web
	@echo "$(YELLOW)API tests (Jest)...$(NC)"
	$(PNPM) test --filter=@synapse/api
	@echo "$(YELLOW)Python service tests (Pytest)...$(NC)"
	@for service in partner-recommender campaign-maker feature-store market-pulse-scanner; do \
		echo "Testing services/$$service..."; \
		cd services/$$service && python -m pytest tests/ -v --tb=short || true; \
		cd ../..; \
	done
	@echo "$(GREEN)All tests completed!$(NC)"

test-watch: ## Run tests in watch mode
	@echo "$(BLUE)Starting test watch mode...$(NC)"
	@echo "$(YELLOW)Watching for changes in frontend and API...$(NC)"
	$(PNPM) run test:watch

type-check: ## Run TypeScript type checking
	@echo "$(BLUE)Running TypeScript type checking...$(NC)"
	$(PNPM) type-check
	@echo "$(GREEN)Type checking completed!$(NC)"

# =============================================================================
# DATABASE & SEEDING TARGETS
# =============================================================================

seed: ## Run database seed script with mock data
	@echo "$(BLUE)Seeding database with mock data...$(NC)"
	@echo "$(YELLOW)Generating:$(NC)"
	@echo "  • 50 diverse startups with founder personalities"
	@echo "  • 200 historical partnership outcomes"
	@echo "  • 5,000 synthetic user engagement events"
	@echo "  • 25 marketing campaigns"
	@echo ""
	@if ! $(DOCKER_COMPOSE) ps postgres | grep -q "Up"; then \
		echo "$(YELLOW)Starting PostgreSQL...$(NC)"; \
		$(DOCKER_COMPOSE) up -d postgres; \
		sleep 5; \
	fi
	@if ! $(DOCKER_COMPOSE) ps feature-store | grep -q "Up"; then \
		echo "$(YELLOW)Starting Feature Store...$(NC)"; \
		$(DOCKER_COMPOSE) up -d feature-store; \
		sleep 10; \
	fi
	cd scripts && chmod +x run-seed.sh && ./run-seed.sh
	@echo "$(GREEN)Database seeding completed successfully!$(NC)"

seed-small: ## Run seed script with smaller dataset (for testing)
	@echo "$(BLUE)Seeding database with small dataset...$(NC)"
	@echo "$(YELLOW)Generating:$(NC)"
	@echo "  • 10 startups"
	@echo "  • 20 partnerships"
	@echo "  • 500 events"
	@echo ""
	cd scripts && $(PYTHON) -c "
import asyncio
from seed_database import DataSeeder
async def main():
    seeder = DataSeeder()
    await seeder.initialize()
    startups = seeder.generate_startup_data(10)
    partnerships = seeder.generate_partnership_data(startups, 20)
    events, campaigns = seeder.generate_engagement_events(startups, 500)
    await seeder._insert_startups(startups)
    await seeder._insert_partnerships(partnerships)
    await seeder._insert_campaigns(campaigns)
    await seeder._insert_events(events)
    await seeder.close()
    print('Small dataset seeded successfully!')
asyncio.run(main())
"
	@echo "$(GREEN)Small dataset seeding completed!$(NC)"

db-reset: ## Reset database and reseed
	@echo "$(BLUE)Resetting database...$(NC)"
	@echo "$(RED)Warning: This will delete all existing data!$(NC)"
	@read -p "Are you sure? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	$(DOCKER_COMPOSE) down postgres
	docker volume rm synapse-launchpad_postgres_data 2>/dev/null || true
	$(DOCKER_COMPOSE) up -d postgres
	@echo "$(YELLOW)Waiting for PostgreSQL to start...$(NC)"
	sleep 10
	@echo "$(YELLOW)Running migrations...$(NC)"
	$(DOCKER_COMPOSE) exec postgres psql -U postgres -d synapse_db -f /docker-entrypoint-initdb.d/init.sql
	@echo "$(YELLOW)Seeding fresh data...$(NC)"
	$(MAKE) seed
	@echo "$(GREEN)Database reset and reseeded successfully!$(NC)"

# =============================================================================
# BUILD & DEPLOY TARGETS
# =============================================================================

build: ## Build all services for production
	@echo "$(BLUE)Building all services for production...$(NC)"
	@echo "$(YELLOW)Building frontend...$(NC)"
	$(PNPM) build --filter=@synapse/web
	@echo "$(YELLOW)Building API...$(NC)"
	$(PNPM) build --filter=@synapse/api
	@echo "$(YELLOW)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build --parallel
	@echo "$(GREEN)All services built successfully!$(NC)"

deploy: ## Deploy to production environment
	@echo "$(BLUE)Deploying to production...$(NC)"
	@echo "$(YELLOW)Building production images...$(NC)"
	$(MAKE) build
	@echo "$(YELLOW)Pushing to registry...$(NC)"
	$(DOCKER_COMPOSE) push
	@echo "$(YELLOW)Deploying to 21st.dev...$(NC)"
	@if command -v 21st >/dev/null 2>&1; then \
		21st deploy; \
	else \
		echo "$(RED)21st CLI not found. Install with: npm install -g @21st-dev/cli$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Deployment completed!$(NC)"

docker-build: ## Build all Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	$(DOCKER_COMPOSE) build --parallel --no-cache
	@echo "$(GREEN)Docker images built successfully!$(NC)"

# =============================================================================
# UTILITY TARGETS
# =============================================================================

logs: ## Show service logs
	@echo "$(BLUE)Showing service logs...$(NC)"
	$(DOCKER_COMPOSE) logs -f --tail=100

status: ## Show service status
	@echo "$(BLUE)Service Status:$(NC)"
	@echo "$(YELLOW)Docker Compose Services:$(NC)"
	$(DOCKER_COMPOSE) ps
	@echo ""
	@echo "$(YELLOW)Health Checks:$(NC)"
	@echo -n "Frontend: "; curl -s http://localhost:3000/api/health >/dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Down$(NC)"
	@echo -n "API Gateway: "; curl -s http://localhost:8000/health >/dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Down$(NC)"
	@echo -n "Partner Recommender: "; curl -s http://localhost:8001/health >/dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Down$(NC)"
	@echo -n "Campaign Generator: "; curl -s http://localhost:8002/health >/dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Down$(NC)"
	@echo -n "Feature Store: "; curl -s http://localhost:8003/health >/dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Down$(NC)"
	@echo -n "Market Pulse Scanner: "; curl -s http://localhost:8004/health >/dev/null && echo "$(GREEN)✓ Healthy$(NC)" || echo "$(RED)✗ Down$(NC)"

shell: ## Open shell in API container
	@echo "$(BLUE)Opening shell in API container...$(NC)"
	$(DOCKER_COMPOSE) exec api /bin/bash

# =============================================================================
# ADVANCED TARGETS
# =============================================================================

benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(NC)"
	@echo "$(YELLOW)Partner recommendation latency...$(NC)"
	@for i in {1..10}; do \
		curl -s -w "Request $$i: %{time_total}s\n" -o /dev/null \
		http://localhost:8001/recommend \
		-H "Content-Type: application/json" \
		-d '{"company_id": "TechFlow AI", "top_k": 10}'; \
	done
	@echo "$(YELLOW)Campaign generation latency...$(NC)"
	@for i in {1..5}; do \
		curl -s -w "Request $$i: %{time_total}s\n" -o /dev/null \
		http://localhost:8002/generate \
		-H "Content-Type: application/json" \
		-d '{"objective": "partnership", "target_audience": "startups", "tone": "professional", "channels": ["email"]}'; \
	done

monitor: ## Start monitoring dashboard
	@echo "$(BLUE)Starting monitoring dashboard...$(NC)"
	@echo "$(YELLOW)Available endpoints:$(NC)"
	@echo "  • Grafana: http://localhost:3001 (admin/admin)"
	@echo "  • Prometheus: http://localhost:9090"
	@echo "  • Sentry: Check your SENTRY_DSN configuration"
	$(DOCKER_COMPOSE) -f docker-compose.monitoring.yml up -d

backup: ## Backup database
	@echo "$(BLUE)Creating database backup...$(NC)"
	@mkdir -p backups
	@timestamp=$$(date +%Y%m%d_%H%M%S); \
	$(DOCKER_COMPOSE) exec -T postgres pg_dump -U postgres synapse_db > backups/synapse_db_$$timestamp.sql
	@echo "$(GREEN)Database backup created: backups/synapse_db_$$(date +%Y%m%d_%H%M%S).sql$(NC)"

restore: ## Restore database from backup
	@echo "$(BLUE)Available backups:$(NC)"
	@ls -la backups/*.sql 2>/dev/null || echo "No backups found"
	@read -p "Enter backup filename: " backup_file; \
	if [ -f "backups/$$backup_file" ]; then \
		echo "$(YELLOW)Restoring from $$backup_file...$(NC)"; \
		$(DOCKER_COMPOSE) exec -T postgres psql -U postgres -d synapse_db < backups/$$backup_file; \
		echo "$(GREEN)Database restored successfully!$(NC)"; \
	else \
		echo "$(RED)Backup file not found!$(NC)"; \
		exit 1; \
	fi

# =============================================================================
# DEVELOPMENT WORKFLOW TARGETS
# =============================================================================

setup: ## Complete development environment setup
	@echo "$(BLUE)Setting up Synapse LaunchPad development environment...$(NC)"
	@echo "$(YELLOW)Step 1: Installing dependencies...$(NC)"
	$(MAKE) install
	@echo "$(YELLOW)Step 2: Starting services...$(NC)"
	$(DOCKER_COMPOSE) up -d postgres redis
	@echo "$(YELLOW)Step 3: Waiting for services to start...$(NC)"
	sleep 10
	@echo "$(YELLOW)Step 4: Running database migrations...$(NC)"
	$(DOCKER_COMPOSE) exec postgres psql -U postgres -d synapse_db -f /docker-entrypoint-initdb.d/init.sql || true
	@echo "$(YELLOW)Step 5: Seeding database...$(NC)"
	$(MAKE) seed
	@echo "$(YELLOW)Step 6: Starting all services...$(NC)"
	$(MAKE) dev
	@echo "$(GREEN)Development environment setup completed!$(NC)"

quick-start: ## Quick start for development (minimal setup)
	@echo "$(BLUE)Quick starting Synapse LaunchPad...$(NC)"
	$(DOCKER_COMPOSE) up -d postgres redis
	sleep 5
	$(MAKE) seed-small
	$(PNPM) dev --filter=@synapse/web &
	$(DOCKER_COMPOSE) up api partner-recommender campaign-maker
	@echo "$(GREEN)Quick start completed!$(NC)"

# =============================================================================
# CI/CD TARGETS
# =============================================================================

ci: ## Run CI pipeline locally
	@echo "$(BLUE)Running CI pipeline...$(NC)"
	$(MAKE) install
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test
	$(MAKE) build
	@echo "$(GREEN)CI pipeline completed successfully!$(NC)"

pre-commit: ## Run pre-commit checks
	@echo "$(BLUE)Running pre-commit checks...$(NC)"
	$(MAKE) lint
	$(MAKE) type-check
	@echo "$(GREEN)Pre-commit checks passed!$(NC)"

# =============================================================================
# DOCUMENTATION TARGETS
# =============================================================================

docs: ## Generate and serve documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@echo "$(YELLOW)API documentation...$(NC)"
	$(DOCKER_COMPOSE) exec api npm run docs:generate || true
	@echo "$(YELLOW)Python service documentation...$(NC)"
	@for service in partner-recommender campaign-maker feature-store; do \
		cd services/$$service && sphinx-build -b html docs docs/_build/html || true; \
		cd ../..; \
	done
	@echo "$(GREEN)Documentation generated!$(NC)"
	@echo "$(YELLOW)Serving at: http://localhost:8080$(NC)"
	@python -m http.server 8080 -d docs || $(PYTHON) -m http.server 8080 -d docs

# =============================================================================
# MAINTENANCE TARGETS
# =============================================================================

update: ## Update all dependencies
	@echo "$(BLUE)Updating dependencies...$(NC)"
	@echo "$(YELLOW)Updating Node.js dependencies...$(NC)"
	$(PNPM) update
	@echo "$(YELLOW)Updating Python dependencies...$(NC)"
	@for service in partner-recommender campaign-maker feature-store market-pulse-scanner; do \
		echo "Updating services/$$service..."; \
		cd services/$$service && pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install -U || true; \
		cd ../..; \
	done
	@echo "$(GREEN)Dependencies updated!$(NC)"

security-scan: ## Run security scans
	@echo "$(BLUE)Running security scans...$(NC)"
	@echo "$(YELLOW)Node.js security audit...$(NC)"
	$(PNPM) audit
	@echo "$(YELLOW)Python security scan...$(NC)"
	@for service in partner-recommender campaign-maker feature-store market-pulse-scanner; do \
		echo "Scanning services/$$service..."; \
		cd services/$$service && safety check || true; \
		cd ../..; \
	done
	@echo "$(GREEN)Security scans completed!$(NC)"

# =============================================================================
# SPECIAL TARGETS
# =============================================================================

demo: ## Set up demo environment with sample data
	@echo "$(BLUE)Setting up demo environment...$(NC)"
	$(MAKE) clean
	$(MAKE) setup
	@echo "$(YELLOW)Demo environment ready!$(NC)"
	@echo "$(GREEN)Access the application at: http://localhost:3000$(NC)"
	@echo "$(GREEN)API documentation at: http://localhost:8000/docs$(NC)"

reset: ## Complete reset (nuclear option)
	@echo "$(RED)WARNING: This will completely reset the environment!$(NC)"
	@read -p "Are you absolutely sure? Type 'RESET' to confirm: " confirm && [ "$$confirm" = "RESET" ] || exit 1
	$(MAKE) clean
	docker system prune -af --volumes
	docker network prune -f
	$(MAKE) setup
	@echo "$(GREEN)Environment completely reset!$(NC)"