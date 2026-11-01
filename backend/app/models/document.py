"""Pydantic models for citizen document storage and OCR metadata."""

from datetime import datetime, timezone
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

DocumentType = Literal[
    "Aadhaar Card",
    "PAN Card",
    "Income Certificate",
    "Caste Certificate",
    "Domicile Certificate",
    "Academic Marksheet",
    "Bonafide Certificate",
    "Passport Photo",
    "Bank Passbook",
    "Other",
]

VerificationStatusType = Literal[
    "Unverified",
    "Extracted",
    "Verified",
    "Rejected",
]


class DocumentBase(BaseModel):
    """Base schema for document metadata."""

    document_name: str = Field(..., min_length=1, max_length=255, description="Original filename")
    document_type: DocumentType = Field("Other", description="Classified document category")
    mime_type: str = Field(..., description="File MIME type (PDF, JPEG, PNG)")
    file_size_bytes: int = Field(..., gt=0, le=10485760, description="Size in bytes, max 10MB")


class DocumentResponse(DocumentBase):
    """Complete document record schema with audit metadata and signed download URL."""

    id: str = Field(..., description="Unique document UUID")
    user_id: str = Field(..., description="Owning citizen auth user ID")
    storage_path: str = Field(..., description="Private storage relative path")
    download_url: Optional[str] = Field(None, description="Short-lived signed URL or streaming endpoint")
    extracted_information: Dict[str, Any] = Field(default_factory=dict, description="Parsed OCR attributes")
    verification_status: VerificationStatusType = Field("Unverified", description="Document verification state")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "e9127d14-38b8-4c8e-b52b-7c87c9c22e43",
                "user_id": "11111111-1111-1111-1111-111111111111",
                "document_name": "aadhaar_card.pdf",
                "document_type": "Aadhaar Card",
                "mime_type": "application/pdf",
                "file_size_bytes": 1048576,
                "storage_path": "vault/11111111-1111-1111-1111-111111111111/aadhaar_card.pdf",
                "download_url": "/api/documents/e9127d14-38b8-4c8e-b52b-7c87c9c22e43/download",
                "extracted_information": {
                    "full_name": "Aarav Sharma",
                    "date_of_birth": "2002-05-14",
                    "gender": "Male",
                    "pincode": "411001",
                    "id_number_masked": "XXXX-XXXX-4819",
                },
                "verification_status": "Extracted",
                "created_at": "2026-11-01T12:00:00Z",
                "updated_at": "2026-11-01T12:00:00Z",
            }
        },
    }


class ConfirmExtractedRequest(BaseModel):
    """Payload for selectively confirming extracted OCR fields into citizen profile."""

    fields_to_confirm: Dict[str, Any] = Field(
        ...,
        description="Key-value pairs of extracted fields confirmed by the citizen to update their profile",
    )
