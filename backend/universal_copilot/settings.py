"""Application Settings and Configuration Management.

This module provides centralized configuration management for the Universal
Copilot Platform using Pydantic Settings with support for environment variables,
YAML files, and default values.

The settings system follows a hierarchical priority:
    1. Environment variables (UCP_* prefix)
    2. .env file
    3. config/{env}.yaml (environment-specific)
    4. config/base.yaml (defaults)

Author:
    Ruslan Magana (ruslanmv.com)

License:
    Apache-2.0

Example:
    Get application settings:

        >>> from backend.universal_copilot.settings import get_settings
        >>> settings = get_settings()
        >>> print(settings.database.url)
        postgresql+asyncpg://user:pass@localhost:5432/copilot

    Override with environment variables:

        $ export UCP_DATABASE__URL="postgresql://..."
        $ export UCP_APP__LOG_LEVEL="DEBUG"
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from pydantic import AnyUrl, BaseModel, Field, SecretStr, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

# Configuration directory path
CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


class AppConfig(BaseModel):
    """Application-level configuration.

    Attributes:
        name: Application name displayed in logs and UI.
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        http_port: HTTP server port number.
        feature_flags: Dictionary of feature flags for toggling functionality.
    """

    name: str = Field(
        default="Universal Copilot Platform",
        description="Application name",
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
    )
    http_port: int = Field(
        default=8000,
        description="HTTP server port",
        ge=1,
        le=65535,
    )
    feature_flags: dict[str, bool] = Field(
        default_factory=dict,
        description="Feature flags for toggling functionality",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate and normalize log level.

        Args:
            v: Log level string.

        Returns:
            Normalized uppercase log level.

        Raises:
            ValueError: If log level is invalid.
        """
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        normalized = v.upper()
        if normalized not in valid_levels:
            msg = f"Invalid log level: {v}. Must be one of {valid_levels}"
            raise ValueError(msg)
        return normalized


class DatabaseConfig(BaseModel):
    """Database configuration.

    Attributes:
        url: Database connection URL (SQLAlchemy format).
        pool_size: Connection pool size for production.
        max_overflow: Maximum overflow connections.
        pool_timeout: Connection pool timeout in seconds.
    """

    url: str = Field(
        description="Database connection URL",
    )
    pool_size: int = Field(
        default=10,
        description="Connection pool size",
        ge=1,
        le=100,
    )
    max_overflow: int = Field(
        default=20,
        description="Maximum overflow connections",
        ge=0,
        le=100,
    )
    pool_timeout: int = Field(
        default=30,
        description="Connection pool timeout in seconds",
        ge=1,
        le=300,
    )


class VectorStoreConfig(BaseModel):
    """Vector store configuration for RAG.

    Attributes:
        url: Vector database connection URL.
        collection_prefix: Prefix for collection/index names.
        dimension: Vector embedding dimension.
    """

    url: str = Field(
        description="Vector database connection URL",
    )
    collection_prefix: str = Field(
        default="ucp",
        description="Prefix for vector collections",
    )
    dimension: int = Field(
        default=1536,
        description="Vector embedding dimension",
        ge=1,
        le=4096,
    )


class LangflowConfig(BaseModel):
    """Langflow integration configuration.

    Attributes:
        base_url: Langflow instance base URL.
        timeout: Request timeout in seconds.
    """

    base_url: AnyUrl = Field(
        description="Langflow instance base URL",
    )
    timeout: int = Field(
        default=60,
        description="Request timeout in seconds",
        ge=1,
        le=600,
    )


class MCPConfig(BaseModel):
    """MCP (Model Context Protocol) configuration.

    Attributes:
        context_forge_url: IBM mcp-context-forge gateway URL.
        timeout: Request timeout in seconds.
    """

    context_forge_url: AnyUrl = Field(
        description="MCP Context Forge gateway URL",
    )
    timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=1,
        le=300,
    )


class ProviderEndpointConfig(BaseModel):
    """LLM provider endpoint configuration.

    Attributes:
        api_base: Provider API base URL.
    """

    api_base: AnyUrl | str = Field(
        description="Provider API base URL",
    )


class ProvidersConfig(BaseModel):
    """Configuration for all LLM providers.

    Attributes:
        openai: OpenAI provider configuration.
        anthropic: Anthropic Claude provider configuration.
        watsonx: IBM watsonx.ai provider configuration.
        ollama: Ollama (self-hosted) provider configuration.
    """

    openai: Optional[ProviderEndpointConfig] = Field(
        default=None,
        description="OpenAI provider config",
    )
    anthropic: Optional[ProviderEndpointConfig] = Field(
        default=None,
        description="Anthropic provider config",
    )
    watsonx: Optional[ProviderEndpointConfig] = Field(
        default=None,
        description="watsonx.ai provider config",
    )
    ollama: Optional[ProviderEndpointConfig] = Field(
        default=None,
        description="Ollama provider config",
    )


class Settings(BaseSettings):
    """Central application settings.

    This class aggregates all configuration from multiple sources with the
    following priority (highest to lowest):
        1. Explicit values passed to Settings(...)
        2. Environment variables with UCP_ prefix
        3. .env file
        4. config/{env}.yaml (environment-specific YAML)
        5. config/base.yaml (base YAML defaults)
        6. Model defaults

    Attributes:
        env: Environment name (dev/staging/prod).
        app: Application-level configuration.
        database: Database configuration.
        vector_store: Vector database configuration.
        langflow: Langflow integration configuration.
        mcp: MCP protocol configuration.
        providers: LLM provider configurations.
        openai_api_key: OpenAI API key (from env/secrets only).
        anthropic_api_key: Anthropic API key (from env/secrets only).
        watsonx_api_key: IBM watsonx.ai API key (from env/secrets only).
        watsonx_project_id: IBM watsonx.ai project ID.
        ollama_api_base: Ollama API base URL.

    Example:
        >>> settings = Settings(env="production")
        >>> print(settings.database.url)
        >>> print(settings.app.log_level)
    """

    # Environment
    env: str = Field(
        default="dev",
        description="Environment name (dev/staging/prod)",
        pattern="^(dev|staging|prod|test)$",
    )

    # Nested config objects
    app: AppConfig = Field(
        default_factory=AppConfig,
        description="Application configuration",
    )
    database: DatabaseConfig = Field(
        description="Database configuration (required)",
    )
    vector_store: Optional[VectorStoreConfig] = Field(
        default=None,
        description="Vector store configuration",
    )
    langflow: Optional[LangflowConfig] = Field(
        default=None,
        description="Langflow configuration",
    )
    mcp: Optional[MCPConfig] = Field(
        default=None,
        description="MCP configuration",
    )
    providers: ProvidersConfig = Field(
        default_factory=ProvidersConfig,
        description="LLM providers configuration",
    )

    # API Keys & Secrets (never put in YAML files)
    openai_api_key: Optional[SecretStr] = Field(
        default=None,
        description="OpenAI API key",
    )
    anthropic_api_key: Optional[SecretStr] = Field(
        default=None,
        description="Anthropic API key",
    )
    watsonx_api_key: Optional[SecretStr] = Field(
        default=None,
        description="IBM watsonx.ai API key",
    )
    watsonx_project_id: Optional[str] = Field(
        default=None,
        description="IBM watsonx.ai project ID",
    )
    ollama_api_base: Optional[str] = Field(
        default=None,
        description="Ollama API base URL",
    )

    model_config = SettingsConfigDict(
        env_prefix="UCP_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> tuple:
        """Customize settings sources and their priority.

        This method is called by Pydantic Settings to determine the order
        and sources of configuration values. We add YAML config file sources
        to the standard environment variable and .env file sources.

        Args:
            settings_cls: The Settings class being configured.
            init_settings: Settings from explicit initialization.
            env_settings: Settings from environment variables.
            dotenv_settings: Settings from .env file.
            file_secret_settings: Settings from Docker secrets.

        Returns:
            Tuple of settings sources in priority order (highest first).

        Note:
            The environment name is determined early to load the correct
            environment-specific YAML file.
        """
        # Determine environment before reading YAML files
        # Priority: explicit init > env var > .env file > default
        env_name = os.getenv("UCP_ENV", "dev")

        # Construct paths to YAML config files
        base_yaml = CONFIG_DIR / "base.yaml"
        env_yaml = CONFIG_DIR / f"{env_name}.yaml"

        # Create YAML config sources
        yaml_env_source = None
        yaml_base_source = None

        if env_yaml.exists():
            yaml_env_source = YamlConfigSettingsSource(
                settings_cls,
                yaml_file=env_yaml,
            )

        if base_yaml.exists():
            yaml_base_source = YamlConfigSettingsSource(
                settings_cls,
                yaml_file=base_yaml,
            )

        # Build sources tuple in priority order (highest to lowest)
        sources = [
            init_settings,
            env_settings,
            dotenv_settings,
        ]

        # Add YAML sources if they exist
        if yaml_env_source:
            sources.append(yaml_env_source)
        if yaml_base_source:
            sources.append(yaml_base_source)

        sources.append(file_secret_settings)

        return tuple(sources)

    def get_provider_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider.

        Args:
            provider: Provider name (openai, anthropic, watsonx, ollama).

        Returns:
            API key string if available, None otherwise.

        Raises:
            ValueError: If provider name is invalid.

        Example:
            >>> settings = get_settings()
            >>> key = settings.get_provider_api_key("openai")
        """
        provider_lower = provider.lower()
        key_mapping = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "watsonx": self.watsonx_api_key,
        }

        if provider_lower not in key_mapping:
            msg = f"Invalid provider: {provider}"
            raise ValueError(msg)

        secret_str = key_mapping[provider_lower]
        return secret_str.get_secret_value() if secret_str else None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached global settings instance.

    This function provides a singleton settings object that is created once
    and cached for the lifetime of the application. This is the standard
    FastAPI pattern for dependency injection of settings.

    Returns:
        Settings: Cached settings instance.

    Example:
        Use in FastAPI dependencies:

        >>> from fastapi import Depends
        >>> from backend.universal_copilot.settings import Settings, get_settings
        >>>
        >>> @app.get("/config")
        >>> def get_config(settings: Settings = Depends(get_settings)):
        ...     return {"env": settings.env}

        Use directly in code:

        >>> settings = get_settings()
        >>> print(settings.database.url)

    Note:
        To force reload settings (e.g., in tests), clear the cache:

        >>> get_settings.cache_clear()
        >>> new_settings = get_settings()
    """
    return Settings()
