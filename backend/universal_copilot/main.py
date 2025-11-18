"""Universal Copilot Platform - FastAPI Application.

This module provides the main FastAPI application factory and CLI interface
for the Universal Copilot Platform. It handles application initialization,
middleware configuration, and routing.

Author:
    Ruslan Magana (ruslanmv.com)

License:
    Apache-2.0

Example:
    Run the application in development mode:

        $ universal-copilot dev

    Run in production mode:

        $ universal-copilot serve --workers 4
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

import typer
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from .api.router import api_router
from .auth.middleware import AuthContextMiddleware
from .settings import get_settings

# Configure standard library logging to use loguru
logging.basicConfig(handlers=[logger], level=0)

# Typer CLI application
cli_app = typer.Typer(
    name="universal-copilot",
    help="Universal Copilot Platform - Enterprise AI Copilot System",
    add_completion=False,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifespan events.

    This context manager handles startup and shutdown events for the application,
    including initialization of database connections, LLM providers, and other
    resources.

    Args:
        app: FastAPI application instance.

    Yields:
        None: Control is yielded during application runtime.

    Example:
        This is automatically called by FastAPI when using the lifespan parameter.
    """
    settings = get_settings()
    logger.info(
        f"Starting Universal Copilot Platform (env={settings.env}, "
        f"version=1.0.0)"
    )

    # Initialize application components
    # TODO: Initialize database connection pool
    # TODO: Initialize LLM provider registry
    # TODO: Initialize MCP client connections
    # TODO: Warm up caches if needed

    logger.info("Application startup complete")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down Universal Copilot Platform")

    # TODO: Close database connections
    # TODO: Close HTTP client sessions
    # TODO: Cleanup MCP connections

    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    This factory function creates a FastAPI application instance with all
    necessary middleware, routers, and configuration applied.

    Returns:
        FastAPI: Configured FastAPI application instance.

    Raises:
        RuntimeError: If application initialization fails.

    Example:
        >>> app = create_app()
        >>> # Use with uvicorn
        >>> uvicorn.run(app, host="0.0.0.0", port=8000)
    """
    settings = get_settings()

    # Create FastAPI application
    app = FastAPI(
        title="Universal Copilot Platform API",
        description=(
            "Enterprise-grade multi-tenant AI copilot platform supporting "
            "10+ use cases with CrewAI, Langflow, and MCP integration"
        ),
        version="1.0.0",
        docs_url="/docs" if settings.app.feature_flags.get("enable_swagger", True) else None,
        redoc_url="/redoc" if settings.app.feature_flags.get("enable_redoc", False) else None,
        openapi_url="/openapi.json",
        lifespan=lifespan,
        contact={
            "name": "Ruslan Magana",
            "url": "https://ruslanmv.com",
            "email": "contact@ruslanmv.com",
        },
        license_info={
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
        },
    )

    # Configure CORS middleware
    if settings.app.feature_flags.get("enable_cors", True):
        # TODO: In production, configure allowed origins from settings
        allowed_origins = ["*"]  # Should come from settings in production

        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.debug("CORS middleware enabled")

    # Add authentication and tenant context middleware
    app.add_middleware(AuthContextMiddleware)
    logger.debug("Auth context middleware enabled")

    # Include API routers
    app.include_router(api_router)
    logger.debug("API routers registered")

    # Add custom exception handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request, exc: ValueError) -> JSONResponse:
        """Handle ValueError exceptions.

        Args:
            request: The request that caused the error.
            exc: The ValueError exception.

        Returns:
            JSONResponse with error details.
        """
        logger.error(f"ValueError: {exc}")
        return JSONResponse(
            status_code=400,
            content={"detail": str(exc), "type": "value_error"},
        )

    logger.info("FastAPI application created successfully")
    return app


# Global ASGI application instance
# This is the main entry point for ASGI servers like uvicorn/gunicorn
app = create_app()


@cli_app.command()
def dev(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    reload: bool = typer.Option(True, "--reload/--no-reload", help="Enable auto-reload"),
) -> None:
    """Run the development server with auto-reload.

    This command starts the Universal Copilot Platform in development mode
    with automatic code reloading enabled. Suitable for local development only.

    Args:
        host: Host address to bind the server to. Defaults to "0.0.0.0".
        port: Port number to bind the server to. Defaults to 8000.
        reload: Whether to enable auto-reload on code changes. Defaults to True.

    Example:
        $ universal-copilot dev
        $ universal-copilot dev --port 8080
        $ universal-copilot dev --host localhost --no-reload
    """
    logger.info(f"Starting development server on {host}:{port}")
    logger.warning(
        "Development mode is enabled. "
        "Do not use this configuration in production!"
    )

    try:
        uvicorn.run(
            "backend.universal_copilot.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info",
            access_log=True,
        )
    except KeyboardInterrupt:
        logger.info("Development server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start development server: {e}")
        raise typer.Exit(code=1) from e


@cli_app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind"),
    workers: Optional[int] = typer.Option(
        None,
        "--workers",
        "-w",
        help="Number of worker processes (defaults to CPU count)",
    ),
) -> None:
    """Run the production server.

    This command starts the Universal Copilot Platform in production mode
    with multiple worker processes for better performance and reliability.

    Args:
        host: Host address to bind the server to. Defaults to "0.0.0.0".
        port: Port number to bind the server to. Defaults to 8000.
        workers: Number of worker processes. If None, uses CPU count.

    Example:
        $ universal-copilot serve
        $ universal-copilot serve --port 8080 --workers 4
        $ universal-copilot serve --host 0.0.0.0
    """
    logger.info(f"Starting production server on {host}:{port}")

    # Determine worker count
    if workers is None:
        import multiprocessing

        workers = multiprocessing.cpu_count()
        logger.info(f"Auto-detected {workers} CPU cores, using {workers} workers")

    logger.info(f"Starting with {workers} worker processes")

    try:
        uvicorn.run(
            "backend.universal_copilot.main:app",
            host=host,
            port=port,
            workers=workers,
            reload=False,
            log_level="warning",
            access_log=True,
            proxy_headers=True,
            forwarded_allow_ips="*",
        )
    except KeyboardInterrupt:
        logger.info("Production server stopped by user")
    except Exception as e:
        logger.error(f"Failed to start production server: {e}")
        raise typer.Exit(code=1) from e


@cli_app.command()
def version() -> None:
    """Display version information.

    Shows the current version of the Universal Copilot Platform along
    with Python version and other relevant information.

    Example:
        $ universal-copilot version
    """
    import sys

    logger.info("Universal Copilot Platform v1.0.0")
    logger.info(f"Python {sys.version}")
    logger.info("License: Apache-2.0")
    logger.info("Author: Ruslan Magana (https://ruslanmv.com)")


def cli() -> None:
    """Main CLI entrypoint.

    This function is referenced by the [project.scripts] section in pyproject.toml
    and serves as the main entrypoint for the universal-copilot CLI command.

    Example:
        This function is automatically called when running:
        $ universal-copilot --help
    """
    cli_app()


if __name__ == "__main__":
    # Allow running the module directly with: python -m backend.universal_copilot.main
    cli()
