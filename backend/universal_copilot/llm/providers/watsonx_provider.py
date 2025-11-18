from __future__ import annotations

from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from ...settings import Settings
from .base import BaseProvider


class WatsonxProvider(BaseProvider):
    name = "watsonx"
    supports_tools = False
    supports_streaming = False  # update if you wire streaming

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = httpx.AsyncClient(
            base_url=settings.providers.watsonx.api_base if settings.providers.watsonx else "",
            timeout=60.0,
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
        Call IBM watsonx.ai generate endpoint.

        This assumes you have:
        - watsonx_api_key
        - watsonx_project_id
        configured in settings.
        """
        if not self._settings.watsonx_api_key or not self._settings.watsonx_project_id:
            raise RuntimeError("watsonx.ai credentials not fully configured")

        # Simple concatenation of messages into prompt; you can improve this mapping.
        prompt = "\n".join(m["content"] for m in messages if "content" in m)

        headers = {
            "Authorization": f"Bearer {self._settings.watsonx_api_key.get_secret_value()}",
        }

        payload: Dict[str, Any] = {
            "model_id": model,
            "input": prompt,
            "project_id": self._settings.watsonx_project_id,
            "parameters": kwargs.get("parameters", {}),
        }

        logger.debug("WatsonxProvider.generate model=%s", model)

        resp = await self._client.post("/ml/v1/text/generation", json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
