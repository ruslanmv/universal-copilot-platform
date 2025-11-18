# syntax=docker/dockerfile:1.9

############################
# 1. Build / dependency stage
############################
FROM python:3.12-slim AS build

# Install system build deps
RUN apt-get update -qy && \
    apt-get install -qy --no-install-recommends \
    build-essential \
    libpq-dev \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# uv tuning
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# Copy dependency metadata first for better cache
COPY pyproject.toml uv.lock* ./

# Install dependencies (no dev deps in image)
RUN --mount=type=cache,target=/root/.cache \
    uv sync --locked --no-dev

# Now copy application code
COPY backend ./backend
COPY config ./config
COPY flows ./flows

############################
# 2. Runtime stage
############################
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Create non-root user
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

# Copy virtualenv + app from build stage
COPY --from=build --chown=app:app /app /app

USER app

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

# Start FastAPI app with uvicorn
CMD ["uvicorn", "backend.universal_copilot.main:app", "--host", "0.0.0.0", "--port", "8000"]
