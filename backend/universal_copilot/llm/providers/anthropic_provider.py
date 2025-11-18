from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from ...settings import Settings
from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    name = "anthropic"
    supports_tools = True
    supports_streaming = True

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.providers.anthropic.api_base if settings.providers.anthropic else "",
            timeout=30.0,
        )

    async def generate(
        self,
        *,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Any:
        """
        Call Anthropic Messages API.
        """
        if not self._settings.anthropic_api_key:
            raise RuntimeError("Anthropic API key not configured")

        headers = {
            "x-api-key": self._settings.anthropic_api_key.get_secret_value(),
            "anthropic-version": "2023-06-01",
        }

        # Convert OpenAI-style messages into Anthropic-style if needed.
        # For now we assume caller already sends appropriate structure.
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools

        logger.debug("AnthropicProvider.generate model=%s stream=%s", model, stream)

        resp = await self._client.post("/v1/messages", json=payload, headers=headers)
        resp.raise_for_status()

        if stream:
            async def _iter_stream():
                async with self._client.stream(
                    "POST", "/v1/messages", json=payload, headers=headers
                ) as s:
                    async for chunk in s.aiter_text():
                        yield chunk

            return _iter_stream()

        return resp.json()
