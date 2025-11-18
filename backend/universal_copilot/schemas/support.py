from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SupportQuery(BaseModel):
    """
    Input payload for the Support Copilot.

    This represents a single user message or ticket that the support crew
    must process. It intentionally stays lean to be used across channels.
    """

    message: str = Field(..., description="End-user message or ticket body.")
    channel: str = Field(
        "web",
        description="Source channel, e.g. web, email, slack, sms.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context (ticket_id, customer_id, locale, etc.).",
    )


class SupportReply(BaseModel):
    """
    Standardized response from the Support Copilot.

    This is what UI layers or ticketing systems will consume directly.
    """

    answer: str = Field(..., description="Answer to present to the end-user or agent.")
    sources: List[str] = Field(
        default_factory=list,
        description="Identifiers / URLs of documents used to build this answer.",
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Optional confidence score between 0.0 and 1.0.",
    )
    escalation_flag: bool = Field(
        default=False,
        description="True if the interaction should be escalated to a human.",
    )
    escalation_reason: Optional[str] = Field(
        default=None,
        description="Explanation of why escalation is suggested.",
    )
