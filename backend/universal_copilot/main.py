from __future__ import annotations

import logging
from typing import Optional

import typer
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import api_router
from .auth.middleware import AuthContextMiddleware
from .settings import get_settings

logger = logging.getLogger("universal_copilot")

cli_app = typer.Typer(help="Universal Copilot Platform CLI")


def create_app() -> FastAPI:
    """
    FastAPI application factory.

    Wires:
    - Settings
    - Routers
    - Middleware
    - Startup / shutdown hooks
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.app.name,
        version="0.1.0",
        docs_url="/docs" if settings.app.feature_flags.get("enable_swagger", True) else None,
        redoc_url=None,
        openapi_url="/openapi.json",
    )

    # CORS (for widgets + admin UI)
    if settings.app.feature_flags.get("enable_cors", True):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # adjust for prod
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Auth / tenant context middleware
    app.add_middleware(AuthContextMiddleware)

    # Routers
    app.include_router(api_router)

    @app.on_event("startup")
    async def on_startup() -> None:  # noqa: D401
        """
        Application startup hook.
        """
        logger.info("Starting Universal Copilot Platform (env=%s)", settings.env)

        # Here you can eagerly warm up providers, MCP connections, etc.
        # e.g. from .llm.gateway import init_providers
        # await init_providers()

    @app.on_event("shutdown")
    async def on_shutdown() -> None:  # noqa: D401
        """
        Application shutdown hook.
        """
        logger.info("Shutting down Universal Copilot Platform")

    return app


# ASGI callable for uvicorn/gunicorn
app = create_app()


@cli_app.command()
def dev(
    host: str = typer.Option("0.0.0.0", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to bind"),
    reload: bool = typer.Option(True, help="Enable auto-reload"),
) -> None:
    """
    Run development server (typically with uvx universal-copilot dev).
    """
    uvicorn.run(
        "backend.universal_copilot.main:app",
        host=host,
        port=port,
        reload=reload,
        factory=False,
    )


@cli_app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to bind"),
    workers: Optional[int] = typer.Option(
        None, help="Number of workers (use None to let uvicorn decide)."
    ),
) -> None:
    """
    Run production server (single command, can also be used under a process manager).
    """
    uvicorn.run(
        "backend.universal_copilot.main:app",
        host=host,
        port=port,
        workers=workers,
        reload=False,
        factory=False,
    )


def cli() -> None:
    """
    Entrypoint referenced by [project.scripts] in pyproject.toml.
    """
    cli_app()
