"""Pydantic schemas for AI-powered scheme eligibility reasoning."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from app.models.profile import CitizenProfileBase


EligibilityStatus = Literal["Likely Eligible", "Likely Ineligible", "More Information Required"]
CriterionStatus = Literal["Satisfied", "Not Satisfied", "Missing Info"]


class CriterionEvaluation(BaseModel):
    """Detailed itemized evaluation of a single scheme eligibility condition."""

    criterion_name: str = Field(..., description="Name of the eligibility parameter (e.g. Annual Income Limit)")
    condition: str = Field(..., description="Official condition requirement from government guidelines")
    citizen_value: Optional[str] = Field(None, description="Actual value or status extracted from citizen profile")
    status: CriterionStatus = Field(..., description="Evaluation outcome for this specific condition")
    reasoning: str = Field(..., description="AI or rule-based reasoning explaining the match or mismatch")
    official_citation: str = Field(..., description="Specific authoritative guideline citation (e.g. Section 3.2)")


class EligibilityEvaluationRequest(BaseModel):
    """Request payload for custom or overridden profile evaluation."""

    citizen_profile: Optional[CitizenProfileBase] = Field(
        None, description="Optional profile override data; if omitted, authenticated user profile is used"
    )


class EligibilityEvaluationResponse(BaseModel):
    """Structured response schema returned by AI reasoning engine and API endpoint."""

    service_id: str = Field(..., description="Evaluated scheme identifier")
    service_name: str = Field(..., description="Official title of the evaluated scheme")
    status: EligibilityStatus = Field(..., description="Overall eligibility determination")
    summary: str = Field(..., description="Human-readable synthesis explaining the determination")
    confidence_score: float = Field(0.95, ge=0.0, le=1.0, description="Confidence score of the evaluation")
    criteria: List[CriterionEvaluation] = Field(default_factory=list, description="Itemized condition breakdown")
    missing_fields: List[str] = Field(
        default_factory=list, description="List of citizen profile fields required to complete assessment"
    )
    next_steps: List[str] = Field(
        default_factory=list, description="Actionable recommendations for the citizen"
    )
    disclaimer: str = Field(
        default="This automated evaluation is an advisory assessment based on official published guidelines and the information provided in your profile. Final legal eligibility is determined exclusively by the competent government department upon formal application submission.",
        description="Statutory advisory notice",
    )
