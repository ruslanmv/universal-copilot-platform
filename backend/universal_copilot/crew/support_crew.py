from __future__ import annotations

from typing import Any, Dict

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ..schemas.support import SupportQuery, SupportReply
from .base_crew import DomainCrew


class SupportCrew(DomainCrew):
    """
    Concrete crew for Support Copilot.

    In a full implementation, this would:
      - Instantiate CrewAI agents (Intake, RAG, Answer, Guardrail)
      - Wire MCP and RAG tools
      - Orchestrate them via CrewAI's Crew object
    """

    USE_CASE_NAME = "support"

    def __init__(self, tenant_id: str, db: AsyncSession) -> None:
        super().__init__(tenant_id=tenant_id, db=db)
        # TODO: instantiate CrewAI Crew here using agents + tools
        self._crew = None

    async def run(self, payload: Any) -> Dict[str, Any]:
        """
        Generic run, delegating to a more strongly-typed method.
        """
        if isinstance(payload, SupportQuery):
            return await self.run_support_flow(payload)
        # If payload is dict (from API), coerce it into SupportQuery.
        return await self.run_support_flow(SupportQuery(**payload))

    async def run_support_flow(self, payload: SupportQuery) -> Dict[str, Any]:
        """
        End-to-end orchestration for a support query.

        For now:
        - Use LLM directly with RAG tool as context (placeholder logic).
        - Later: delegate to CrewAI Crew for richer agent flows.
        """
        logger.info(
            "SupportCrew.run_support_flow tenant=%s channel=%s",
            self.tenant_id,
            payload.channel,
        )

        # Example RAG query via helper:
        rag_tool = self.rag_tool(use_case=self.USE_CASE_NAME)
        docs = await rag_tool(query=payload.message, source="kb", top_k=5)

        # Build simple messages list for LLM
        context_snippets = "\n\n".join(d["text"] for d in docs if "text" in d)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful support copilot. Answer using ONLY the context provided. "
                    "If you are unsure, say you are unsure and recommend escalation."
                ),
            },
            {
                "role": "user",
                "content": f"User message: {payload.message}\n\nContext:\n{context_snippets}",
            },
        ]

        llm_response = await self.call_llm(
            use_case=self.USE_CASE_NAME,
            messages=messages,
        )

        # You will adapt this based on provider response shape.
        answer_text = llm_response.get("choices", [{}])[0].get("message", {}).get("content", "")

        reply = SupportReply(
            answer=answer_text,
            sources=[d.get("id", "") for d in docs],
            confidence=None,
            escalation_flag=False,
        )
        return reply.model_dump()
