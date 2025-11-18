"""Unit tests for settings module."""

from __future__ import annotations

import pytest

from backend.universal_copilot.settings import Settings, get_settings


def test_settings_initialization() -> None:
    """Test that settings can be initialized with default values."""
    settings = Settings(
        env="test",
        database={"url": "sqlite:///:memory:"},
    )

    assert settings.env == "test"
    assert settings.app.name == "Universal Copilot Platform"
    assert settings.database.url == "sqlite:///:memory:"


def test_get_settings_returns_singleton() -> None:
    """Test that get_settings returns the same instance."""
    settings1 = get_settings()
    settings2 = get_settings()

    assert settings1 is settings2


def test_settings_with_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that settings can be overridden with environment variables.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setenv("UCP_ENV", "production")
    monkeypatch.setenv("UCP_APP__LOG_LEVEL", "ERROR")

    # Clear cached settings
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.env == "production"
    assert settings.app.log_level == "ERROR"

    # Clean up
    get_settings.cache_clear()
