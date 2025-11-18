from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..rag.vector_client import VectorClient
from ..rag.indexes import index_name
from ..settings import get_settings
from ..mcp_host.client import MCPClient  # you’ll implement this later


class MCPTool:
    """
    Lightweight wrapper around MCP calls via Context Forge.

    Agents will use this as a Python tool; internally it calls MCPClient
    with the given tool_name, passing tenant context.
    """

    def __init__(self, tool_name: str, tenant_id: str) -> None:
        self.tool_name = tool_name
        self.tenant_id = tenant_id
        self._client = MCPClient()

    async def __call__(self, **kwargs: Any) -> Any:
        logger.debug("MCPTool(%s) tenant=%s args=%s", self.tool_name, self.tenant_id, kwargs)
        return await self._client.call_tool(
            tool_name=self.tool_name,
            tenant_id=self.tenant_id,
            arguments=kwargs,
        )


class VectorSearchTool:
    """
    RAG tool that talks to the vector store abstraction.

    Agents call this tool with a query and optionally a source.
    """

    def __init__(self, tenant_id: str, use_case: str) -> None:
        self.tenant_id = tenant_id
        self.use_case = use_case
        self._client = VectorClient(settings=get_settings())

    async def __call__(
        self,
        query: str,
        source: str = "kb",
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        idx = index_name(self.tenant_id, self.use_case, source)
        logger.debug(
            "VectorSearchTool tenant=%s use_case=%s index=%s query=%s",
            self.tenant_id,
            self.use_case,
            idx,
            query,
        )
        return await self._client.query(index_name=idx, query_text=query, top_k=top_k)


class DBTool:
    """
    Very restricted DB tool for analytics / lookups.

    IMPORTANT: this should only expose safe, read-only queries.
    Never expose arbitrary SQL to the model.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """
        Example: fetch tenant config snapshot for an agent.
        """
        from ..db.models import Tenant  # lazy import to avoid circular deps

        tenant = await self.db.get(Tenant, tenant_id)
        if not tenant:
            return {}
        return {
            "id": tenant.id,
            "name": tenant.name,
            "default_provider": tenant.default_provider,
            "enabled_use_cases": tenant.enabled_use_cases,
        }
