from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..settings import get_settings
from ..llm import gateway as llm_gateway
from .tools import MCPTool, VectorSearchTool


class DomainCrew(ABC):
    """
    Base class for all domain-specific crews (support, hr, legal, ...).

    Encapsulates cross-cutting dependencies like:
    - tenant_id
    - DB session
    - LLM gateway
    - tool helpers (MCP, RAG, etc.)
    """

    def __init__(self, tenant_id: str, db: AsyncSession) -> None:
        self.tenant_id = tenant_id
        self.db = db
        self.settings = get_settings()

    @abstractmethod
    async def run(self, payload: Any) -> Dict[str, Any]:
        """
        Main entrypoint for the crew. Concrete subclasses will:
        - interpret the payload (schemas)
        - orchestrate agents and tools
        - return a normalized dict for the API schema.
        """
        raise NotImplementedError

    async def call_llm(self, use_case: str, messages: list[dict], **kwargs: Any) -> Any:
        """
        Helper to call the multi-provider LLM gateway with this crew's tenant context.
        """
        return await llm_gateway.generate(
            tenant_id=self.tenant_id,
            use_case=use_case,
            messages=messages,
            **kwargs,
        )

    def mcp_tool(self, name: str) -> MCPTool:
        """
        Convenience factory for MCP tools bound to this tenant.
        """
        return MCPTool(tool_name=name, tenant_id=self.tenant_id)

    def rag_tool(self, use_case: str) -> VectorSearchTool:
        """
        Convenience factory for RAG tools bound to this tenant + use case.
        """
        return VectorSearchTool(tenant_id=self.tenant_id, use_case=use_case)


def build_base_tools(tenant_id: str, use_case: str) -> dict[str, Any]:
    """
    Optionally build a set of shared tools that can be injected into CrewAI agents.
    """
    return {
        "mcp": MCPTool,
        "rag": lambda: VectorSearchTool(tenant_id=tenant_id, use_case=use_case),
    }
