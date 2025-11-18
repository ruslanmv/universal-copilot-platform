from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseProvider(ABC):
    """
    Abstract provider interface for all LLM backends.

    Concrete implementations must translate our generic request schema
    into the provider-specific API shape.
    """

    name: str
    supports_tools: bool = False
    supports_streaming: bool = False

    @abstractmethod
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
        Execute a chat completion / generation call.

        Implementations must:
        - Accept our generic 'messages' array (role/content style).
        - Optionally accept 'tools' (if supports_tools is True).
        - Support non-stream and (optionally) stream mode.
        """
        raise NotImplementedError
