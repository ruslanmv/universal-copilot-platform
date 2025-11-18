from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class ClauseRisk(BaseModel):
    """
    Risk evaluation for a single contract clause.
    """

    clause_id: str = Field(
        ...,
        description="Internal clause identifier or index within the contract.",
    )
    risk_level: str = Field(
        ...,
        description="Risk rating (e.g. 'low', 'medium', 'high', 'unacceptable').",
    )
    issues: List[str] = Field(
        default_factory=list,
        description="Specific issues or concerns detected in this clause.",
    )
    recommendation: Optional[str] = Field(
        default=None,
        description="Suggested change, fallback wording or negotiation guidance.",
    )


class ContractReviewRequest(BaseModel):
    """
    Input payload for the Legal Copilot contract review.
    """

    contract_text: str = Field(
        ...,
        description="Full contract text or key clauses to review.",
    )
    governing_law: Optional[str] = Field(
        default=None,
        description="Jurisdiction for the contract (e.g. 'DE', 'US-CA').",
    )
    counterparty_name: Optional[str] = Field(default=None)
    deal_value: Optional[float] = Field(
        default=None,
        description="Approximate value of the deal, used for risk calibration.",
    )


class ContractReviewResponse(BaseModel):
    """
    Structured contract review result from the Legal Copilot.
    """

    summary: str = Field(..., description="High-level summary of the contract.")
    overall_risk: str = Field(
        ...,
        description="Overall risk level (e.g. 'low', 'medium', 'high').",
    )
    clauses: List[ClauseRisk] = Field(
        default_factory=list,
        description="Per-clause risk evaluation.",
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="General suggestions, e.g. additional clauses or safeguards.",
    )
