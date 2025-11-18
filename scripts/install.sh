#!/usr/bin/env bash
set -euo pipefail

echo "[UCP] Checking for uv…"
if ! command -v uv >/dev/null 2>&1; then
  echo "[UCP] uv not found. Installing via official installer…"
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

echo "[UCP] Syncing Python dependencies with uv…"
uv sync

echo "[UCP] Starting local infra with docker-compose…"
docker-compose up -d postgres vector-db langflow mcp-context-forge ollama || {
  echo "[UCP] docker-compose failed. Ensure Docker is running."
  exit 1
}

echo "[UCP] Starting backend (uvx universal-copilot dev)…"
uvx universal-copilot dev
