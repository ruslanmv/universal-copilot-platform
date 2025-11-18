from __future__ import annotations

from typing import Any, Dict, Iterable, List

from loguru import logger

from ..settings import get_settings
from .indexes import index_name
from .vector_client import VectorClient


async def ingest_documents(
    *,
    tenant_id: str,
    use_case: str,
    source: str,
    documents: Iterable[Dict[str, Any]],
    dimension: int = 1536,
) -> None:
    """
    Generic ingestion pipeline: embed & store docs in vector index.

    'documents' should be an iterable of dicts with at least:
      - id: unique identifier
      - text: raw content
      - metadata: dict (optional)
    """
    settings = get_settings()
    client = VectorClient(settings=settings)
    idx = index_name(tenant_id, use_case, source)

    logger.info(
        "Ingesting documents for tenant=%s use_case=%s source=%s index=%s",
        tenant_id,
        use_case,
        source,
        idx,
    )

    # Optionally create index (if required by engine)
    await client.create_index(index_name=idx, dimension=dimension)

    # TODO: call embedding model here (or delegate to Langflow/MCP)
    # For now we store docs as-is; actual vector embedding happens in the vector engine,
    # or you can pre-compute embeddings here.

    docs_list = list(documents)
    if not docs_list:
        logger.info("No documents to ingest for index=%s", idx)
        return

    await client.upsert(index_name=idx, docs=docs_list)


# Examples of source-specific ingestion entrypoints

async def ingest_from_sharepoint(
    tenant_id: str,
    use_case: str,
    site_url: str,
    **kwargs: Any,
) -> None:
    """
    Load documents from SharePoint and send them to the generic ingestion pipeline.
    """
    # TODO: implement SharePoint loader.
    # Example shape:
    docs: List[Dict[str, Any]] = []
    # docs.append({"id": "...", "text": "...", "metadata": {"source": "sharepoint", ...}})
    await ingest_documents(
        tenant_id=tenant_id,
        use_case=use_case,
        source="sharepoint",
        documents=docs,
    )


async def ingest_from_confluence(
    tenant_id: str,
    use_case: str,
    base_url: str,
    **kwargs: Any,
) -> None:
    """
    Load documents from Confluence and send them to the generic ingestion pipeline.
    """
    # TODO: implement Confluence loader.
    docs: List[Dict[str, Any]] = []
    await ingest_documents(
        tenant_id=tenant_id,
        use_case=use_case,
        source="confluence",
        documents=docs,
    )
