from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from ...settings import Settings
from .base import BaseProvider


class OllamaProvider(BaseProvider):
    name = "ollama"
    supports_tools = False  # could be extended with tool pattern
    supports_streaming = True

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        base_url = settings.providers.ollama.api_base if settings.providers.ollama else ""
        self._client = httpx.AsyncClient(base_url=base_url, timeout=60.0)

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
        Call Ollama /api/chat endpoint for local models.
        """
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
        }

        logger.debug("OllamaProvider.generate model=%s stream=%s", model, stream)

        if stream:
            async def _iter_stream():
                async with self._client.stream("POST", "/api/chat", json=payload) as s:
                    async for chunk in s.aiter_text():
                        yield chunk

            return _iter_stream()

        resp = await self._client.post("/api/chat", json=payload)
        resp.raise_for_status()
        return resp.json()
