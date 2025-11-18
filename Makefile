# ============================================================================
# Universal Copilot Platform - Production Makefile
# ============================================================================
# Author: Ruslan Magana (ruslanmv.com)
# License: Apache-2.0
# ============================================================================

.DEFAULT_GOAL := help

# ============================================================================
# Configuration Variables
# ============================================================================

# Python & UV
PYTHON := python3
UV := uv
UV_RUN := $(UV) run

# Project
PROJECT_NAME := universal-copilot-platform
BACKEND_MODULE := backend.universal_copilot

# Docker & Registry
REGISTRY ?= ghcr.io/ruslanmv
IMAGE_NAME ?= universal-copilot-backend
IMAGE_TAG ?= latest
FULL_IMAGE ?= $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

# Kubernetes / OpenShift
K8S_NAMESPACE ?= universal-copilot
K8S_STACK_FILE ?= infra/k8s/stack.yaml

# Directories
SRC_DIRS := backend scripts mcp
TEST_DIR := tests
DOCS_DIR := docs
BUILD_DIR := dist
COV_DIR := htmlcov

# Colors for output
CYAN := \033[0;36m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ============================================================================
# Help Target (Self-Documenting)
# ============================================================================

.PHONY: help
help: ## Show this help message
	@echo "$(CYAN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(CYAN)║   Universal Copilot Platform - Makefile Commands              ║$(NC)"
	@echo "$(CYAN)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /Development/ {next} /Testing/ {exit} {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Testing & Quality:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /Testing/,/Docker/ {if (!/Testing/) printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Docker & Deployment:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /Docker/,/Utilities/ {if (!/Docker/) printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; /Utilities/ {found=1; next} found {printf "  $(CYAN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""

# ============================================================================
# Development
# ============================================================================

.PHONY: install
install: ## Install all dependencies using uv
	@echo "$(GREEN)Installing dependencies with uv...$(NC)"
	@command -v $(UV) >/dev/null 2>&1 || { \
		echo "$(RED)Error: uv is not installed. Installing now...$(NC)"; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	}
	$(UV) sync --all-extras
	@echo "$(GREEN)✓ Dependencies installed successfully$(NC)"

.PHONY: install-dev
install-dev: ## Install with dev dependencies only
	@echo "$(GREEN)Installing dev dependencies...$(NC)"
	$(UV) sync --extra dev
	@echo "$(GREEN)✓ Dev dependencies installed$(NC)"

.PHONY: update
update: ## Update all dependencies
	@echo "$(GREEN)Updating dependencies...$(NC)"
	$(UV) lock --upgrade
	$(UV) sync --all-extras
	@echo "$(GREEN)✓ Dependencies updated$(NC)"

.PHONY: dev
dev: ## Run backend in development mode with auto-reload
	@echo "$(GREEN)Starting development server...$(NC)"
	$(UV_RUN) uvicorn $(BACKEND_MODULE).main:app \
		--reload --host 0.0.0.0 --port 8000

.PHONY: serve
serve: ## Run backend in production mode
	@echo "$(GREEN)Starting production server...$(NC)"
	$(UV_RUN) uvicorn $(BACKEND_MODULE).main:app \
		--host 0.0.0.0 --port 8000 --workers 4

.PHONY: shell
shell: ## Start Python REPL with project context
	@echo "$(GREEN)Starting Python shell...$(NC)"
	$(UV_RUN) python

.PHONY: clean-pyc
clean-pyc: ## Remove Python bytecode files
	@echo "$(YELLOW)Cleaning Python bytecode...$(NC)"
	find . -type f -name '*.py[co]' -delete
	find . -type d -name '__pycache__' -delete
	@echo "$(GREEN)✓ Python bytecode cleaned$(NC)"

# ============================================================================
# Testing & Quality
# ============================================================================

.PHONY: test
test: ## Run all tests with pytest
	@echo "$(GREEN)Running tests...$(NC)"
	$(UV_RUN) pytest -v

.PHONY: test-cov
test-cov: ## Run tests with coverage report
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	$(UV_RUN) pytest -v --cov=$(BACKEND_MODULE) \
		--cov-report=term-missing \
		--cov-report=html \
		--cov-report=xml
	@echo "$(GREEN)✓ Coverage report generated in $(COV_DIR)/$(NC)"

.PHONY: test-watch
test-watch: ## Run tests in watch mode
	@echo "$(GREEN)Running tests in watch mode...$(NC)"
	$(UV_RUN) pytest-watch

.PHONY: lint
lint: ## Run ruff linter
	@echo "$(GREEN)Running linter...$(NC)"
	$(UV_RUN) ruff check $(SRC_DIRS)

.PHONY: lint-fix
lint-fix: ## Run ruff linter with auto-fix
	@echo "$(GREEN)Running linter with auto-fix...$(NC)"
	$(UV_RUN) ruff check --fix $(SRC_DIRS)

.PHONY: format
format: ## Format code with ruff
	@echo "$(GREEN)Formatting code...$(NC)"
	$(UV_RUN) ruff format $(SRC_DIRS)

.PHONY: format-check
format-check: ## Check code formatting without making changes
	@echo "$(GREEN)Checking code formatting...$(NC)"
	$(UV_RUN) ruff format --check $(SRC_DIRS)

.PHONY: typecheck
typecheck: ## Run mypy type checker
	@echo "$(GREEN)Running type checker...$(NC)"
	$(UV_RUN) mypy $(SRC_DIRS)

.PHONY: security
security: ## Run bandit security checks
	@echo "$(GREEN)Running security checks with bandit...$(NC)"
	$(UV_RUN) bandit -c pyproject.toml -r $(SRC_DIRS)

.PHONY: audit
audit: lint format-check typecheck security ## Run comprehensive code audit (lint, format, types, security)
	@echo "$(GREEN)✓ Code audit completed successfully$(NC)"

.PHONY: qa
qa: audit ## Run all quality checks (alias for audit)

.PHONY: ci
ci: audit test-cov ## Run full CI pipeline (audit + tests with coverage)
	@echo "$(GREEN)✓ CI pipeline completed successfully$(NC)"

.PHONY: pre-commit-install
pre-commit-install: ## Install pre-commit hooks
	@echo "$(GREEN)Installing pre-commit hooks...$(NC)"
	$(UV_RUN) pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

.PHONY: pre-commit
pre-commit: ## Run pre-commit on all files
	@echo "$(GREEN)Running pre-commit checks...$(NC)"
	$(UV_RUN) pre-commit run --all-files

# ============================================================================
# Docker & Deployment
# ============================================================================

.PHONY: docker-build
docker-build: ## Build backend Docker image
	@echo "$(GREEN)Building Docker image: $(FULL_IMAGE)$(NC)"
	docker build -f backend/Dockerfile -t $(FULL_IMAGE) .
	@echo "$(GREEN)✓ Docker image built successfully$(NC)"

.PHONY: docker-push
docker-push: ## Push Docker image to registry
	@echo "$(GREEN)Pushing Docker image: $(FULL_IMAGE)$(NC)"
	docker push $(FULL_IMAGE)
	@echo "$(GREEN)✓ Docker image pushed successfully$(NC)"

.PHONY: docker-run
docker-run: ## Run backend container locally
	@echo "$(GREEN)Running Docker container...$(NC)"
	docker run -p 8000:8000 --env-file .env $(FULL_IMAGE)

.PHONY: compose-up
compose-up: ## Start full stack with docker-compose
	@echo "$(GREEN)Starting docker-compose stack...$(NC)"
	docker compose up -d
	@echo "$(GREEN)✓ Stack started$(NC)"
	@echo "$(CYAN)Backend API: http://localhost:8000/docs$(NC)"
	@echo "$(CYAN)Langflow UI: http://localhost:7860/$(NC)"

.PHONY: compose-down
compose-down: ## Stop docker-compose stack
	@echo "$(YELLOW)Stopping docker-compose stack...$(NC)"
	docker compose down
	@echo "$(GREEN)✓ Stack stopped$(NC)"

.PHONY: compose-logs
compose-logs: ## Show docker-compose logs
	docker compose logs -f

.PHONY: compose-ps
compose-ps: ## Show docker-compose services status
	docker compose ps

.PHONY: k8s-apply
k8s-apply: ## Deploy to Kubernetes
	@echo "$(GREEN)Deploying to Kubernetes namespace: $(K8S_NAMESPACE)$(NC)"
	kubectl create namespace $(K8S_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl -n $(K8S_NAMESPACE) apply -f $(K8S_STACK_FILE)
	@echo "$(GREEN)✓ Deployed to Kubernetes$(NC)"

.PHONY: k8s-destroy
k8s-destroy: ## Remove from Kubernetes
	@echo "$(YELLOW)Removing from Kubernetes...$(NC)"
	-kubectl -n $(K8S_NAMESPACE) delete -f $(K8S_STACK_FILE)
	-kubectl delete namespace $(K8S_NAMESPACE)
	@echo "$(GREEN)✓ Removed from Kubernetes$(NC)"

.PHONY: k8s-logs
k8s-logs: ## Show Kubernetes pod logs
	kubectl -n $(K8S_NAMESPACE) logs -f -l app=universal-copilot-backend

# ============================================================================
# Database
# ============================================================================

.PHONY: db-migrate
db-migrate: ## Run database migrations
	@echo "$(GREEN)Running database migrations...$(NC)"
	$(UV_RUN) alembic upgrade head
	@echo "$(GREEN)✓ Migrations applied$(NC)"

.PHONY: db-revision
db-revision: ## Create new migration revision (use MSG="description")
	@echo "$(GREEN)Creating migration revision...$(NC)"
	$(UV_RUN) alembic revision --autogenerate -m "$(MSG)"
	@echo "$(GREEN)✓ Migration created$(NC)"

.PHONY: db-downgrade
db-downgrade: ## Downgrade database by one revision
	@echo "$(YELLOW)Downgrading database...$(NC)"
	$(UV_RUN) alembic downgrade -1
	@echo "$(GREEN)✓ Database downgraded$(NC)"

# ============================================================================
# Utilities
# ============================================================================

.PHONY: clean
clean: clean-pyc ## Clean all build artifacts
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	rm -rf $(BUILD_DIR)
	rm -rf $(COV_DIR)
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf *.egg-info
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Build artifacts cleaned$(NC)"

.PHONY: clean-all
clean-all: clean ## Clean everything including venv
	@echo "$(RED)Cleaning everything...$(NC)"
	rm -rf .venv
	rm -rf uv.lock
	@echo "$(GREEN)✓ Everything cleaned$(NC)"

.PHONY: init-dev-data
init-dev-data: ## Initialize development database with sample data
	@echo "$(GREEN)Initializing development data...$(NC)"
	$(UV_RUN) python scripts/init_dev_data.py
	@echo "$(GREEN)✓ Development data loaded$(NC)"

.PHONY: load-demo-docs
load-demo-docs: ## Load demo documents for RAG
	@echo "$(GREEN)Loading demo documents...$(NC)"
	$(UV_RUN) python scripts/load_demo_documents.py
	@echo "$(GREEN)✓ Demo documents loaded$(NC)"

.PHONY: import-flows
import-flows: ## Import Langflow flows
	@echo "$(GREEN)Importing Langflow flows...$(NC)"
	$(UV_RUN) python scripts/import_flows_to_langflow.py
	@echo "$(GREEN)✓ Flows imported$(NC)"

.PHONY: docs
docs: ## Generate documentation (TODO)
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"

.PHONY: version
version: ## Show version information
	@echo "$(CYAN)Universal Copilot Platform$(NC)"
	@echo "Version: $(shell grep '^version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "Python: $(shell $(PYTHON) --version)"
	@echo "UV: $(shell $(UV) --version)"

.PHONY: info
info: ## Show project information
	@echo "$(CYAN)Project Information:$(NC)"
	@echo "  Name: $(PROJECT_NAME)"
	@echo "  Image: $(FULL_IMAGE)"
	@echo "  K8s Namespace: $(K8S_NAMESPACE)"
	@echo "  Python: $(shell $(PYTHON) --version)"
	@echo "  UV: $(shell $(UV) --version 2>/dev/null || echo 'not installed')"

# ============================================================================
# Composite Targets
# ============================================================================

.PHONY: setup
setup: install pre-commit-install ## Complete development setup
	@echo "$(GREEN)✓ Development environment setup complete!$(NC)"
	@echo "$(CYAN)Next steps:$(NC)"
	@echo "  1. Copy .env.example to .env and configure"
	@echo "  2. Run 'make compose-up' to start services"
	@echo "  3. Run 'make dev' to start development server"

.PHONY: build-all
build-all: qa test docker-build ## Build everything (QA, tests, Docker)
	@echo "$(GREEN)✓ Build completed successfully$(NC)"

.PHONY: deploy
deploy: docker-build docker-push k8s-apply ## Full deployment pipeline
	@echo "$(GREEN)✓ Deployment completed successfully$(NC)"

# ============================================================================
# Special Targets
# ============================================================================

.PHONY: all
all: install qa test ## Run install, quality checks, and tests

.SILENT: help
