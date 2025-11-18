from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..db.session import check_database_connection
from ..settings import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """
    Lightweight liveness probe: if this responds, the process is running.
    """
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> dict[str, str]:
    """
    Readiness probe: verifies DB connectivity and basic config.
    Extend this to also check MCP gateway, Langflow, etc.
    """
    settings = get_settings()

    try:
        await check_database_connection()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database not ready: {exc}",
        ) from exc

    # You can add extra checks here (Langflow, MCP, vector DB, etc.)
    return {
        "status": "ready",
        "env": settings.env,
        "db": "ok",
    }
