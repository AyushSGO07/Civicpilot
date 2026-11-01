"""Pydantic schemas for verified government services and schemes."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

ServiceCategoryType = Literal[
    "Education",
    "Scholarships",
    "Identity & Documents",
    "Transport",
    "Agriculture",
    "Healthcare",
    "Business & MSME",
    "Financial Assistance",
    "Other",
]


class GovernmentServiceBase(BaseModel):
    """Base schema for an official government scheme or citizen service."""

    service_name: str = Field(..., min_length=1, max_length=255, description="Official scheme title")
    department: str = Field(..., min_length=1, max_length=255, description="Issuing ministry or department")
    description: str = Field(..., description="Comprehensive description of scheme purpose and benefits")
    category: ServiceCategoryType = Field("Other", description="Standardized category taxonomy")
    state: str = Field("Central", description="'Central' for nationwide or Indian State/UT name")
    eligibility_summary: str = Field(..., description="Human-readable eligibility requirements summary")
    eligibility_criteria: Dict[str, Any] = Field(default_factory=dict, description="Structured criteria rules for AI engine")
    required_documents: List[str] = Field(default_factory=list, description="Mandatory supporting certificates")
    official_source_url: str = Field(..., description="Authoritative portal informational source URL")
    official_application_url: str = Field(..., description="Official government portal execution/apply URL")
    application_deadline: Optional[str] = Field(None, description="Official closing deadline or 'Rolling / Open Throughout Year'")
    is_active: bool = Field(True, description="Whether scheme is currently active for applications")


class GovernmentServiceResponse(GovernmentServiceBase):
    """Full scheme schema with persistent ID and audit timestamps."""

    id: str = Field(..., description="Unique scheme UUID or slug")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "pm-usp-scholarship",
                "service_name": "Central Sector Scheme of Scholarship for College and University Students (PM-USP)",
                "department": "Ministry of Education, Department of Higher Education",
                "description": "Financial assistance to meritorious students from low-income families to pursue higher education.",
                "category": "Scholarships",
                "state": "Central",
                "eligibility_summary": "Students scoring above 80th percentile in relevant stream in Class 12, annual family income up to ₹4.5 lakh.",
                "eligibility_criteria": {
                    "min_marks_percentile": 80.0,
                    "max_annual_income": 450000.0,
                    "education_level": "Undergraduate",
                },
                "required_documents": [
                    "Class 12 Marksheet",
                    "Income Certificate",
                    "Aadhaar Card",
                    "Bank Passbook",
                    "Bonafide Student Certificate",
                ],
                "official_source_url": "https://www.myscheme.gov.in/schemes/pm-usp",
                "official_application_url": "https://scholarships.gov.in/",
                "application_deadline": "31st October 2026 (Annual Cycle)",
                "is_active": True,
            }
        },
    }
