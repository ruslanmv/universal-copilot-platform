from __future__ import annotations

from typing import Any, Dict, List

import httpx
from loguru import logger

from ..settings import Settings


class VectorClient:
    """
    Abstraction over your vector DB (Milvus, Qdrant, Weaviate, pgvector, etc.).

    This skeleton assumes a REST-style vector DB; adjust to your chosen engine.
    """

    def __init__(self, settings: Settings) -> None:
        if not settings.vector_store:
            raise RuntimeError("Vector store not configured")
        self._base_url = settings.vector_store.url
        self._client = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)

    async def create_index(self, index_name: str, dimension: int) -> None:
        """
        Create a new index/collection if your engine requires explicit creation.
        """
        logger.info("VectorClient.create_index name=%s dimension=%s", index_name, dimension)
        # Implement per your vector DB; for dev you can no-op.
        # await self._client.post("/indexes", json={"name": index_name, "dimension": dimension})

    async def upsert(
        self,
        index_name: str,
        docs: List[Dict[str, Any]],
    ) -> None:
        """
        Upsert a batch of documents into an index.

        Each doc should contain:
          - id (string)
          - text (string)
          - metadata (dict)
        """
        logger.info("VectorClient.upsert index=%s count=%s", index_name, len(docs))
        payload = {
            "index": index_name,
            "documents": docs,
        }
        # Replace endpoint and payload format with your engine’s API
        # await self._client.post("/upsert", json=payload)

    async def query(
        self,
        index_name: str,
        query_text: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for top_k documents given a query_text.
        """
        logger.debug(
            "VectorClient.query index=%s top_k=%s query=%s",
            index_name,
            top_k,
            query_text,
        )
        payload = {
            "index": index_name,
            "query": query_text,
            "top_k": top_k,
        }
        # Replace with call to your vector DB search endpoint
        # resp = await self._client.post("/query", json=payload)
        # resp.raise_for_status()
        # return resp.json().get("results", [])

        # For now, return empty list as safe placeholder
        return []
