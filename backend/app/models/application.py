"""CivicPilot Application Models.

Defines schemas and models for citizen application tracking, submission verification,
and official receipt generation.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

ApplicationStatus = Literal[
    "draft",
    "in_progress",
    "waiting_approval",
    "submitted",
    "approved",
    "rejected",
    "failed",
]


class ApplicationRecord(BaseModel):
    """Complete application record tracking citizen journey on an official portal."""

    id: str = Field(description="Unique application UUID or session identifier")
    user_id: str = Field(default="demo-citizen-id", description="Citizen account identifier")
    service_id: str = Field(description="Official scheme identifier (e.g. nsp-post-matric-sc)")
    service_name: str = Field(description="Full scheme title")
    department: str = Field(description="Issuing government ministry or department")
    category: str = Field(default="Social Welfare", description="Scheme functional category")
    portal_url: str = Field(description="Official government application portal URL (.gov.in / .nic.in)")
    status: ApplicationStatus = Field(default="draft", description="Current lifecycle state")
    acknowledgement_number: Optional[str] = Field(
        default=None,
        description="Authentic government acknowledgement/reference number (e.g. NSP2026/APPL/894125)",
    )
    confirmation_text: Optional[str] = Field(
        default=None,
        description="Verbatim confirmation phrase captured from official portal DOM",
    )
    submission_timestamp: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when submission was verified",
    )
    receipt_url: Optional[str] = Field(
        default=None,
        description="Public or signed download URL for official receipt PDF",
    )
    receipt_path: Optional[str] = Field(
        default=None,
        description="Filesystem path where receipt PDF is stored",
    )
    populated_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of citizen profile attributes populated into portal",
    )
    attached_documents: List[str] = Field(
        default_factory=list,
        description="List of verified vault document certificates attached",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SubmissionVerificationResult(BaseModel):
    """Outcome of automated post-submission audit on government portal."""

    is_success: bool = Field(description="True if authentic confirmation criteria met")
    acknowledgement_number: Optional[str] = Field(
        default=None,
        description="Extracted genuine reference number without trailing punctuation",
    )
    confirmation_text: Optional[str] = Field(
        default=None,
        description="Extracted confirmation message",
    )
    submission_timestamp: Optional[datetime] = Field(
        default=None,
        description="Timestamp of verification",
    )
    receipt_filename: Optional[str] = Field(
        default=None,
        description="Generated receipt filename",
    )
    receipt_bytes: Optional[bytes] = Field(
        default=None,
        description="PDF byte contents if generated during verification",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error details if verification failed or was inconclusive",
    )


class CreateApplicationRequest(BaseModel):
    """Payload to register a new application workflow."""

    id: Optional[str] = None
    service_id: str
    service_name: str
    department: str
    category: str = "Social Welfare"
    portal_url: str
    status: ApplicationStatus = "draft"
    populated_data: Dict[str, Any] = Field(default_factory=dict)
    attached_documents: List[str] = Field(default_factory=list)


class UpdateApplicationRequest(BaseModel):
    """Payload to update an existing application state."""

    status: Optional[ApplicationStatus] = None
    acknowledgement_number: Optional[str] = None
    confirmation_text: Optional[str] = None
    submission_timestamp: Optional[datetime] = None
    receipt_url: Optional[str] = None
    receipt_path: Optional[str] = None
    populated_data: Optional[Dict[str, Any]] = None
    attached_documents: Optional[List[str]] = None
