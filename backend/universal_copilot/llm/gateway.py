from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from loguru import logger

from ..settings import get_settings
from ..db.session import get_session_factory
from ..db.models import LLMCallLog
from .providers.base import BaseProvider
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.watsonx_provider import WatsonxProvider
from .providers.ollama_provider import OllamaProvider


@dataclass
class ProviderSpec:
    name: str
    model: str


# Simple registry. You can make this dynamic later.
_PROVIDER_REGISTRY: dict[str, BaseProvider] | None = None


def _init_providers() -> dict[str, BaseProvider]:
    settings = get_settings()
    providers: dict[str, BaseProvider] = {}

    providers["openai"] = OpenAIProvider(settings=settings)
    providers["anthropic"] = AnthropicProvider(settings=settings)
    providers["watsonx"] = WatsonxProvider(settings=settings)
    providers["ollama"] = OllamaProvider(settings=settings)

    return providers


def get_provider_registry() -> dict[str, BaseProvider]:
    global _PROVIDER_REGISTRY

    if _PROVIDER_REGISTRY is None:
        _PROVIDER_REGISTRY = _init_providers()
    return _PROVIDER_REGISTRY


def resolve_provider_spec(tenant_id: str, use_case: str) -> ProviderSpec:
    """
    Resolve which provider/model to use for a given tenant + use_case.

    In a real system this would:
      - Read TenantUseCaseConfig from DB
      - Fallback to global default from Settings

    For now, we read the defaults from Settings (config YAML).
    """
    settings = get_settings()
    default_provider = getattr(settings, "llm_default_provider", None) or "openai"
    default_model = getattr(settings, "llm_default_model", None) or "gpt-4.1-mini"
    return ProviderSpec(name=default_provider, model=default_model)


async def _log_llm_call(
    *,
    tenant_id: str | None,
    use_case: str | None,
    provider_name: str,
    model_name: str,
    tokens_input: int,
    tokens_output: int,
    latency_ms: int,
    status: str,
    error_type: str | None = None,
    error_message: str | None = None,
) -> None:
    """
    Persist a log entry in the DB for governance, analytics and cost tracking.
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        log = LLMCallLog(
            tenant_id=tenant_id,
            use_case_id=use_case,
            provider_name=provider_name,
            model_name=model_name,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            latency_ms=latency_ms,
            status=status,
            error_type=error_type,
            error_message=error_message,
        )
        session.add(log)
        await session.commit()


async def generate(
    tenant_id: str,
    use_case: str,
    messages: List[Dict[str, Any]],
    tools: Optional[List[Dict[str, Any]]] = None,
    stream: bool = False,
    **kwargs: Any,
) -> Any:
    """
    Unified entrypoint to all LLM calls.

    - Selects provider & model based on tenant/use_case.
    - Delegates to provider implementation.
    - Applies quota limits (TODO: quotas.py).
    - Logs to DB and (optionally) external governance.

    Returns either:
      - full response object (non-stream)
      - async generator of chunks (if stream=True)
    """
    spec = resolve_provider_spec(tenant_id=tenant_id, use_case=use_case)
    providers = get_provider_registry()

    provider = providers.get(spec.name)
    if provider is None:
        raise ValueError(f"Unknown provider '{spec.name}'")

    logger.debug(
        "LLM.generate provider=%s model=%s tenant=%s use_case=%s",
        spec.name,
        spec.model,
        tenant_id,
        use_case,
    )

    # TODO: call quotas.enforce(tenant_id, use_case, spec, messages, tools)

    try:
        response = await provider.generate(
            model=spec.model,
            messages=messages,
            tools=tools,
            stream=stream,
            **kwargs,
        )
        # TODO: derive tokens & latency from provider response
        await _log_llm_call(
            tenant_id=tenant_id,
            use_case=use_case,
            provider_name=spec.name,
            model_name=spec.model,
            tokens_input=0,
            tokens_output=0,
            latency_ms=0,
            status="success",
        )
        return response
    except Exception as exc:  # noqa: BLE001
        logger.exception("LLM call failed: %s", exc)
        await _log_llm_call(
            tenant_id=tenant_id,
            use_case=use_case,
            provider_name=spec.name,
            model_name=spec.model,
            tokens_input=0,
            tokens_output=0,
            latency_ms=0,
            status="error",
            error_type=exc.__class__.__name__,
            error_message=str(exc),
        )
        raise
