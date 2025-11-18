from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import AnyUrl, BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict, YamlConfigSettingsSource

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


class AppConfig(BaseModel):
    name: str = "Universal Copilot Platform"
    log_level: str = "INFO"
    http_port: int = 8000
    feature_flags: dict[str, bool] = {}


class DatabaseConfig(BaseModel):
    url: str


class VectorStoreConfig(BaseModel):
    url: str


class LangflowConfig(BaseModel):
    base_url: AnyUrl


class MCPConfig(BaseModel):
    context_forge_url: AnyUrl


class ProviderEndpointConfig(BaseModel):
    api_base: AnyUrl | str


class ProvidersConfig(BaseModel):
    openai: Optional[ProviderEndpointConfig] = None
    anthropic: Optional[ProviderEndpointConfig] = None
    watsonx: Optional[ProviderEndpointConfig] = None
    ollama: Optional[ProviderEndpointConfig] = None


class Settings(BaseSettings):
    """
    Central application settings.

    Priority:
    1. Values passed directly to Settings(...)
    2. Environment variables (and .env file)
    3. YAML configs: config/{env}.yaml then config/base.yaml
    4. Defaults declared in models above
    """

    # Environment (dev / stage / prod)
    env: str = "dev"

    # Nested config objects
    app: AppConfig = AppConfig()
    database: DatabaseConfig
    vector_store: Optional[VectorStoreConfig] = None
    langflow: Optional[LangflowConfig] = None
    mcp: Optional[MCPConfig] = None
    providers: ProvidersConfig = ProvidersConfig()

    # LLM keys / secrets (never put in YAML)
    openai_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    watsonx_api_key: Optional[SecretStr] = None
    watsonx_project_id: Optional[str] = None
    ollama_api_base: Optional[str] = None  # may differ from providers.ollama.api_base

    model_config = SettingsConfigDict(
        env_prefix="UCP_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """
        Combine:
        - init params
        - environment + .env
        - YAML config (env-specific then base) as lowest priority
        """

        # Determine env *before* reading YAML
        env_name = os.getenv("UCP_ENV", "dev")
        base_yaml = CONFIG_DIR / "base.yaml"
        env_yaml = CONFIG_DIR / f"{env_name}.yaml"

        yaml_env_source = YamlConfigSettingsSource(settings_cls, yaml_file=env_yaml)
        yaml_base_source = YamlConfigSettingsSource(settings_cls, yaml_file=base_yaml)

        # Order: init > env > dotenv > env.yaml > base.yaml > secrets
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            yaml_env_source,
            yaml_base_source,
            file_secret_settings,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Cached global settings object (standard FastAPI pattern).
    Environment and YAML are only read once at process startup.
    """
    return Settings()
