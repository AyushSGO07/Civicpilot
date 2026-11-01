"""Pydantic models for pre-submission summary, citizen approval, and rejection (HIL-01, HIL-02, HIL-03)."""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class PopulatedFormField(BaseModel):
    """Details of a single form field populated autonomously by the agent."""

    field_label: str = Field(..., description="Human-readable label or inferred title of the form field")
    element_name: str = Field(..., description="HTML name, id, or accessible name of the input")
    locator: str = Field(..., description="Playwright locator string used to target element")
    value_populated: str = Field(..., description="Value entered into the form field")
    source_attribute: str = Field(..., description="Citizen profile attribute mapped to this field")
    confidence: float = Field(1.0, description="Mapping confidence score (0.0 - 1.0)")


class AttachedVaultDocument(BaseModel):
    """Details of an identity document attached from the citizen's secure vault."""

    document_name: str = Field(..., description="Official name of the document (e.g. Aadhaar Card, Income Certificate)")
    document_type: str = Field(..., description="Document category or MIME type")
    vault_id: str = Field(..., description="Unique vault identifier or file path")
    verified: bool = Field(True, description="Whether document passed OCR verification")


class PreSubmissionSummary(BaseModel):
    """Complete pre-submission audit payload for citizen review prior to irreversible portal submission."""

    service_id: str = Field(..., description="Target government scheme identifier")
    service_name: str = Field(..., description="Official name of the government scheme")
    portal_url: str = Field(..., description="Target official application portal URL")
    populated_fields: List[PopulatedFormField] = Field(
        default_factory=list, description="All form fields populated autonomously"
    )
    attached_documents: List[AttachedVaultDocument] = Field(
        default_factory=list, description="All vault certificates attached to the form"
    )
    generated_at: str = Field(..., description="ISO 8601 timestamp of summary compilation")
    total_fields: int = Field(0, description="Total count of populated form fields")
    all_mandatory_satisfied: bool = Field(True, description="Whether all required inputs are populated")
    disclaimer: str = Field(
        default=(
            "Statutory Advisory: By approving this submission, you explicitly authorize CivicPilot "
            "to execute the final application submission on your behalf on the official portal. "
            "Please review all values carefully."
        ),
        description="Explicit legal consent advisory",
    )


class ApprovalDecisionRequest(BaseModel):
    """Request payload sent by citizen to approve or reject application submission."""

    decision: Literal["approved", "rejected"] = Field(
        ..., description="Citizen decision: 'approved' to submit or 'rejected' to return to edit"
    )
    rejection_reason: Optional[str] = Field(
        None, description="Optional explanation if the citizen rejects submission"
    )


class ApprovalDecisionResponse(BaseModel):
    """Response returned upon recording citizen approval decision."""

    thread_id: str = Field(..., description="LangGraph execution thread UUID")
    status: str = Field(..., description="Execution status ('approved', 'rejected', 'paused')")
    decision: str = Field(..., description="Recorded citizen decision")
    message: str = Field(..., description="Status summary message")
    current_step: str = Field(..., description="Next workflow state / node")
