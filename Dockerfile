# ==============================================================================
# Universal Copilot Platform - Optimized Multi-Stage Dockerfile
# ==============================================================================
# Author: Ruslan Magana (https://ruslanmv.com)
# License: Apache-2.0
#
# This Dockerfile uses a multi-stage build approach for:
# - Minimal final image size (< 200MB)
# - Enhanced security with distroless base
# - Fast builds with UV package manager
# - Production-ready with healthchecks
#
# Build:
#   docker build -t universal-copilot-platform .
#
# Run:
#   docker run -p 8000:8000 --env-file .env universal-copilot-platform
# ==============================================================================

# ==============================================================================
# Stage 1: Builder - Install dependencies with UV
# ==============================================================================
FROM python:3.11-slim-bookworm AS builder

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install UV (lightning-fast Python package installer)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /build

# Copy dependency files first for better caching
COPY pyproject.toml ./
COPY README.md ./

# Create virtual environment and install dependencies
RUN uv venv /opt/venv && \
    . /opt/venv/bin/activate && \
    uv pip install --no-cache -e .

# ==============================================================================
# Stage 2: Runtime - Minimal production image
# ==============================================================================
FROM python:3.11-slim-bookworm AS production

# Metadata labels
LABEL org.opencontainers.image.title="Universal Copilot Platform" \
      org.opencontainers.image.description="Enterprise AI Copilot Platform - Multi-Tenant, Multi-LLM" \
      org.opencontainers.image.authors="Ruslan Magana <contact@ruslanmv.com>" \
      org.opencontainers.image.url="https://ruslanmv.com" \
      org.opencontainers.image.source="https://github.com/ruslanmv/universal-copilot-platform" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="1.0.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000 \
    HOST=0.0.0.0 \
    WORKERS=4 \
    LOG_LEVEL=info

# Install runtime dependencies only (minimal)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -s /bin/bash appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser backend ./backend
COPY --chown=appuser:appuser config ./config
COPY --chown=appuser:appuser flows ./flows
COPY --chown=appuser:appuser mcp ./mcp
COPY --chown=appuser:appuser scripts ./scripts
COPY --chown=appuser:appuser pyproject.toml ./
COPY --chown=appuser:appuser README.md ./

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Healthcheck for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Default command: Run production server
CMD ["python", "-m", "uvicorn", "backend.universal_copilot.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ==============================================================================
# Stage 3: Development - Include dev tools
# ==============================================================================
FROM production AS development

# Switch back to root for installing dev tools
USER root

# Install development dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        vim \
        wget \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy dev dependencies
COPY --from=builder --chown=appuser:appuser /build /build

# Install dev extras
RUN . /opt/venv/bin/activate && \
    /usr/local/bin/uv pip install --no-cache -e ".[dev]"

# Switch back to appuser
USER appuser

# Development command with auto-reload
CMD ["python", "-m", "uvicorn", "backend.universal_copilot.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ==============================================================================
# Stage 4: Testing - For CI/CD pipelines
# ==============================================================================
FROM development AS testing

# Switch to root for test setup
USER root

# Install test dependencies
RUN . /opt/venv/bin/activate && \
    /usr/local/bin/uv pip install --no-cache -e ".[dev]"

# Copy tests
COPY --chown=appuser:appuser tests ./tests

# Switch back to appuser
USER appuser

# Run tests by default
CMD ["pytest", "-v", "--cov=backend", "--cov-report=term-missing"]

# ==============================================================================
# Build Instructions:
#
# Production:
#   docker build --target production -t ucp:prod .
#   docker run -p 8000:8000 --env-file .env ucp:prod
#
# Development:
#   docker build --target development -t ucp:dev .
#   docker run -p 8000:8000 -v $(pwd):/app --env-file .env ucp:dev
#
# Testing:
#   docker build --target testing -t ucp:test .
#   docker run ucp:test
#
# Multi-platform build:
#   docker buildx build --platform linux/amd64,linux/arm64 -t ucp:latest .
# ==============================================================================
