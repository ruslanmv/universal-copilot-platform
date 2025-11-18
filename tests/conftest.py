"""Pytest configuration and shared fixtures.

This module provides common fixtures and configuration for all tests.
"""

from __future__ import annotations

from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.universal_copilot.db.models import Base
from backend.universal_copilot.main import create_app
from backend.universal_copilot.settings import Settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Provide test settings.

    Returns:
        Settings instance configured for testing.
    """
    return Settings(
        env="test",
        database={"url": "sqlite:///:memory:"},
        app={"name": "Test Universal Copilot", "log_level": "DEBUG"},
    )


@pytest.fixture(scope="function")
def db_engine():
    """Provide a test database engine.

    Yields:
        SQLAlchemy engine for testing.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """Provide a test database session.

    Args:
        db_engine: Database engine fixture.

    Yields:
        SQLAlchemy session for testing.
    """
    SessionLocal = sessionmaker(bind=db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_client(test_settings) -> TestClient:
    """Provide a test client for the FastAPI application.

    Args:
        test_settings: Test settings fixture.

    Returns:
        FastAPI test client.
    """
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_tenant() -> dict:
    """Provide a mock tenant for testing.

    Returns:
        Dictionary representing a test tenant.
    """
    return {
        "id": "test-tenant-001",
        "name": "Test Corporation",
        "default_provider": "openai",
        "enabled_use_cases": ["support", "hr"],
        "is_active": True,
    }


@pytest.fixture
def mock_llm_response() -> dict:
    """Provide a mock LLM response.

    Returns:
        Dictionary representing a mock LLM API response.
    """
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Test response"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


@pytest.fixture
async def mock_http_client() -> AsyncGenerator[MagicMock, None]:
    """Provide a mock HTTP client for testing external API calls.

    Yields:
        Mock HTTP client.
    """
    mock_client = MagicMock()
    yield mock_client
