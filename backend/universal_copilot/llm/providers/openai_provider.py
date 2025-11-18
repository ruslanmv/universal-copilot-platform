from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from ...settings import Settings, get_settings
from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    name = "openai"
    supports_tools = True
    supports_streaming = True

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.providers.openai.api_base if settings.providers.openai else "",
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
        Call OpenAI Chat Completions API.

        Assumes pydantic-settings has OPENAI_API_KEY in settings.openai_api_key.
        """
        if not self._settings.openai_api_key:
            raise RuntimeError("OpenAI API key not configured")

        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key.get_secret_value()}",
        }

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }
        if tools:
            payload["tools"] = tools

        logger.debug("OpenAIProvider.generate model=%s stream=%s", model, stream)

        resp = await self._client.post("/chat/completions", json=payload, headers=headers)
        resp.raise_for_status()

        if stream:
            # Return async iterator of SSE/stream chunks (simple wrapper)
            async def _iter_stream():
                async with self._client.stream(
                    "POST", "/chat/completions", json=payload, headers=headers
                ) as s:
                    async for chunk in s.aiter_text():
                        yield chunk

            return _iter_stream()

        return resp.json()
