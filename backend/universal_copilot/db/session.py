from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy import text

from ..settings import get_settings

_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    global _engine

    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database.url,
            echo=False,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=10,
        )

    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _async_session_factory

    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    return _async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession per request.
    """
    async_session = get_session_factory()
    async with async_session() as session:
        try:
            yield session
        finally:
            # no explicit close needed; context manager handles it
            ...


async def check_database_connection() -> bool:
    """
    Used by readiness probe: run a simple SELECT 1.
    """
    async_session = get_session_factory()
    async with async_session() as session:
        await session.execute(text("SELECT 1"))
    return True
