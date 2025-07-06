.PHONY: help dev dev-build infra prod prod-build stop clean reset logs health install test

# Default target
help: ## Show this help message
	@echo "🎯 Menu Visualizer Development Commands"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""
	@echo "🚀 Quick Start:"
	@echo "  make dev        # Start development environment"
	@echo "  make infra      # Start only infrastructure"
	@echo "  make stop       # Stop everything"

# Environment setup
.env:
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file from template..."; \
		cp env.example .env; \
		echo "⚠️  Please edit .env file with your API keys"; \
	fi

# Development commands
dev: .env ## Start full development environment with hot reload
	@echo "🔥 Starting development environment with hot reload..."
	docker-compose -f docker-compose.dev.yml up --build

dev-build: .env ## Rebuild and start development environment
	@echo "🔨 Rebuilding development environment..."
	docker-compose -f docker-compose.dev.yml up --build --force-recreate

infra: .env ## Start only infrastructure (MongoDB + MinIO)
	@echo "🐳 Starting infrastructure services..."
	docker-compose -f docker-compose.dev.yml up -d mongo minio minio-client
	@echo "⏳ Waiting for services to be ready..."
	@sleep 10
	@echo "✅ Infrastructure ready!"
	@echo "📊 MongoDB: http://localhost:27018"
	@echo "🗄️  MinIO Console: http://localhost:9001 (admin/password123)"
	@echo ""
	@echo "🎯 Now you can run locally:"
	@echo "  make start-frontend"
	@echo "  make start-backend"

# Production commands
prod: .env ## Start production environment
	@echo "🚀 Starting production environment..."
	docker-compose up --build

prod-build: .env ## Rebuild and start production environment
	@echo "🔨 Rebuilding production environment..."
	docker-compose up --build --force-recreate

# Control commands
stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	docker-compose -f docker-compose.dev.yml down
	docker-compose down

clean: ## Stop services and remove containers
	@echo "🧹 Cleaning up containers..."
	docker-compose -f docker-compose.dev.yml down --remove-orphans
	docker-compose down --remove-orphans

reset: ## Reset all data and volumes
	@echo "🗑️  Resetting all data and volumes..."
	docker-compose -f docker-compose.dev.yml down -v
	docker-compose down -v
	@echo "✅ Reset complete!"

# Logs and monitoring
logs: ## Show logs from all services
	docker-compose -f docker-compose.dev.yml logs -f

logs-api: ## Show only backend API logs
	docker-compose -f docker-compose.dev.yml logs -f api

logs-web: ## Show only frontend logs
	docker-compose -f docker-compose.dev.yml logs -f web

# Health checks
health: ## Check service health
	@echo "🏥 Checking service health..."
	@echo "Backend API:"
	@curl -s http://localhost:8000/health || echo "❌ Backend not responding"
	@echo ""
	@echo "Frontend:"
	@curl -s -I http://localhost:3000 | head -1 || echo "❌ Frontend not responding"

# Local development
install: ## Install dependencies locally
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "📦 Setting up Python virtual environment..."
	cd backend && python3 -m venv venv
	@echo "📦 Installing backend dependencies..."
	cd backend && source venv/bin/activate && pip install -r requirements.txt

start-frontend: ## Start frontend locally (requires infra)
	@echo "⚛️  Starting frontend with hot reload..."
	cd frontend && npm run dev

start-backend: ## Start backend locally (requires infra)
	@echo "🐍 Starting backend with hot reload..."
	cd backend && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0

# Testing
test: ## Run basic API tests
	@echo "🧪 Testing API endpoints..."
	@echo "Health check:"
	@curl -s http://localhost:8000/health | cat
	@echo ""
	@echo "Products endpoint:"
	@curl -s http://localhost:8000/products | head -c 200 && echo "..."

test-upload: ## Test file upload (requires test image)
	@echo "📤 Testing file upload..."
	@if [ -f test-menu.jpg ]; then \
		curl -X POST -F "file=@test-menu.jpg" http://localhost:8000/parse-image; \
	else \
		echo "❌ No test-menu.jpg found. Please add a test image."; \
	fi

# Database operations
db-seed: ## Reseed database with fresh data
	@echo "🌱 Reseeding database..."
	docker-compose -f docker-compose.dev.yml restart api

db-shell: ## Open MongoDB shell
	docker-compose -f docker-compose.dev.yml exec mongo mongosh menu_matcher

# Utility commands
ps: ## Show running containers
	docker-compose -f docker-compose.dev.yml ps

build-frontend: ## Build frontend only
	cd frontend && npm run build

build-backend: ## Build backend Docker image
	docker build -t menu-visualizer-api ./backend

# Documentation
docs: ## Open API documentation
	@echo "📖 Opening API documentation..."
	@open http://localhost:8000/docs || echo "Visit: http://localhost:8000/docs"

# Quick development workflows
quick-start: infra start-frontend start-backend ## Quick start: infra + local dev

full-restart: stop dev ## Full restart of development environment

# Production deployment helpers
deploy-check: ## Check if ready for deployment
	@echo "🔍 Deployment readiness check..."
	@echo "✅ Docker Compose files exist"
	@test -f .env && echo "✅ Environment file exists" || echo "❌ Missing .env file"
	@test -f README.md && echo "✅ Documentation exists" || echo "❌ Missing README.md" 