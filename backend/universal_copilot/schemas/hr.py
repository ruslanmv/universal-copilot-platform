from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class HRQuestion(BaseModel):
    """
    Generic HR policy / benefits / procedure question from an employee.
    """

    question: str = Field(..., description="Employee's HR question.")
    employee_id: Optional[str] = Field(
        default=None,
        description="Internal employee identifier. Used only for personalization.",
    )
    locale: Optional[str] = Field(
        default=None,
        description="Locale/region (e.g. 'en-US', 'de-DE') to route to correct policies.",
    )


class CVMatchRequest(BaseModel):
    """
    Request to match a candidate CV to a specific job.
    """

    job_id: str = Field(..., description="Internal job requisition identifier.")
    cv_text: str = Field(..., description="Plain text representation of the CV.")
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of best matches / rationale entries to return.",
    )


class CVMatchResult(BaseModel):
    """
    One candidate–job match result, including explanation.
    """

    candidate_name: Optional[str] = Field(
        default=None,
        description="Candidate name if known / extracted.",
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score between 0 and 1.",
    )
    explanation: Optional[str] = Field(
        default=None,
        description="Short explanation (skills, experience, etc.) for the score.",
    )


class HRAnswer(BaseModel):
    """
    Standardized HR copilot response for a question.
    """

    answer: str = Field(..., description="Answer for the employee.")
    references: List[str] = Field(
        default_factory=list,
        description="Policy doc IDs or URLs referenced in the answer.",
    )
