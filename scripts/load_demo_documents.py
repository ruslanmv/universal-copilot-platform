from __future__ import annotations

import asyncio
from typing import Dict, List

from backend.universal_copilot.rag.ingestion import ingest_documents


async def main() -> None:
    # Very simple sample documents; replace with real loaders.
    support_docs: List[Dict] = [
        {"id": "faq-1", "text": "How to reset my password?", "metadata": {"topic": "password"}},
        {"id": "faq-2", "text": "How to change my billing address?", "metadata": {"topic": "billing"}},
    ]

    hr_docs: List[Dict] = [
        {"id": "hr-1", "text": "Our vacation policy is …", "metadata": {"region": "global"}},
    ]

    legal_docs: List[Dict] = [
        {"id": "legal-1", "text": "Standard NDA clause …", "metadata": {"type": "nda"}},
    ]

    await ingest_documents(
        tenant_id="tenant_a",
        use_case="support",
        source="kb",
        documents=support_docs,
    )
    await ingest_documents(
        tenant_id="tenant_a",
        use_case="hr",
        source="kb",
        documents=hr_docs,
    )
    await ingest_documents(
        tenant_id="tenant_a",
        use_case="legal",
        source="kb",
        documents=legal_docs,
    )


if __name__ == "__main__":
    asyncio.run(main())
