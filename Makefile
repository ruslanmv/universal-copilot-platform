# Makefile at repository root

# Registry / image config
REGISTRY        ?= ghcr.io/your-org
IMAGE_NAME      ?= universal-copilot-backend
IMAGE_TAG       ?= latest
FULL_IMAGE      ?= $(REGISTRY)/$(IMAGE_NAME):$(IMAGE_TAG)

# Kubernetes / OpenShift config
K8S_NAMESPACE   ?= universal-copilot
K8S_STACK_FILE  ?= infra/k8s/stack.yaml

# Tools
UV              ?= uv

.PHONY: help
help:
	@echo "Common targets:"
	@echo "  make dev             - run backend in dev mode with uvicorn"
	@echo "  make test            - run pytest"
	@echo "  make lint            - run ruff lint"
	@echo "  make format          - format Python code"
	@echo "  make typecheck       - run mypy"
	@echo "  make ci              - run lint + tests (CI pipeline)"
	@echo "  make docker-build    - build backend container image"
	@echo "  make docker-push     - push backend image to registry"
	@echo "  make compose-up      - start full stack via docker compose"
	@echo "  make compose-down    - stop stack"
	@echo "  make k8s-apply       - deploy stack to Kubernetes"
	@echo "  make k8s-destroy     - remove stack from Kubernetes"

.PHONY: dev
dev:
	$(UV) run uvicorn backend.universal_copilot.main:app \
	--reload --host 0.0.0.0 --port 8000

.PHONY: test
test:
	$(UV) run pytest

.PHONY: lint
lint:
	$(UV) run ruff check backend tests

.PHONY: format
format:
	$(UV) run ruff format backend tests

.PHONY: typecheck
typecheck:
	$(UV) run mypy backend

.PHONY: ci
ci: lint test

.PHONY: docker-build
docker-build:
	docker build -f backend/Dockerfile -t $(FULL_IMAGE) .

.PHONY: docker-push
docker-push:
	docker push $(FULL_IMAGE)

.PHONY: compose-up
compose-up:
	docker compose up -d

.PHONY: compose-down
compose-down:
	docker compose down

.PHONY: k8s-apply
k8s-apply:
	kubectl create namespace $(K8S_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	kubectl -n $(K8S_NAMESPACE) apply -f $(K8S_STACK_FILE)

.PHONY: k8s-destroy
k8s-destroy:
	-kubectl -n $(K8S_NAMESPACE) delete -f $(K8S_STACK_FILE)
	-kubectl delete namespace $(K8S_NAMESPACE)
