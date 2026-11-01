"""Citizen profile Pydantic models with validation."""

from datetime import date, datetime
from typing import Optional, Literal
import re
from pydantic import BaseModel, Field, field_validator


GenderType = Literal["Male", "Female", "Other", "Prefer not to say"]
SocialCategoryType = Literal["General", "OBC", "SC", "ST", "EWS"]


class CitizenProfileBase(BaseModel):
    """Base schema for citizen personal, academic, address and eligibility attributes."""

    # Personal Details (PROF-01)
    full_name: str = Field(..., min_length=1, max_length=150, description="Citizen's full legal name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth in YYYY-MM-DD")
    gender: Optional[GenderType] = Field(None, description="Gender identity")
    contact_number: Optional[str] = Field(None, description="10-digit primary mobile contact number")

    # Address & Domicile (PROF-02)
    state: Optional[str] = Field(None, max_length=100, description="State or Union Territory of domicile")
    district: Optional[str] = Field(None, max_length=100, description="District of residence")
    pincode: Optional[str] = Field(None, description="6-digit postal PIN code")

    # Academic Profile (PROF-03)
    education_level: Optional[str] = Field(None, max_length=100, description="Highest or current education level")
    institution_name: Optional[str] = Field(None, max_length=200, description="School, college or university name")
    course: Optional[str] = Field(None, max_length=150, description="Course, stream, or degree program")
    academic_year: Optional[str] = Field(None, max_length=50, description="Current academic year or status")

    # Voluntary Eligibility Attributes (PROF-04)
    occupation: Optional[str] = Field(None, max_length=100, description="Current occupation status")
    annual_income: Optional[float] = Field(None, ge=0, description="Annual family income in Indian Rupees (₹)")
    social_category: Optional[SocialCategoryType] = Field(None, description="Reservation or social category")
    disability_status: bool = Field(False, description="Person with benchmark disability status")
    minority_status: bool = Field(False, description="Recognized religious or linguistic minority status")

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "":
            v_cleaned = v.strip()
            if not re.match(r"^\d{6}$", v_cleaned):
                raise ValueError("PIN code must be exactly 6 numeric digits")
            return v_cleaned
        return None

    @field_validator("contact_number")
    @classmethod
    def validate_contact_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "":
            v_cleaned = re.sub(r"[\s\-\+]", "", v)
            if v_cleaned.startswith("91") and len(v_cleaned) == 12:
                v_cleaned = v_cleaned[2:]
            if not re.match(r"^\d{10}$", v_cleaned):
                raise ValueError("Contact number must be a valid 10-digit mobile number")
            return v_cleaned
        return None

    @field_validator("annual_income")
    @classmethod
    def validate_annual_income(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Annual income cannot be negative")
        return v


class CitizenProfileUpdate(BaseModel):
    """Schema for updating citizen profile fields."""

    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    date_of_birth: Optional[date] = None
    gender: Optional[GenderType] = None
    contact_number: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None
    education_level: Optional[str] = None
    institution_name: Optional[str] = None
    course: Optional[str] = None
    academic_year: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: Optional[float] = Field(None, ge=0)
    social_category: Optional[SocialCategoryType] = None
    disability_status: Optional[bool] = None
    minority_status: Optional[bool] = None

    @field_validator("pincode")
    @classmethod
    def validate_pincode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "":
            v_cleaned = v.strip()
            if not re.match(r"^\d{6}$", v_cleaned):
                raise ValueError("PIN code must be exactly 6 numeric digits")
            return v_cleaned
        return None

    @field_validator("contact_number")
    @classmethod
    def validate_contact_number(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v != "":
            v_cleaned = re.sub(r"[\s\-\+]", "", v)
            if v_cleaned.startswith("91") and len(v_cleaned) == 12:
                v_cleaned = v_cleaned[2:]
            if not re.match(r"^\d{10}$", v_cleaned):
                raise ValueError("Contact number must be a valid 10-digit mobile number")
            return v_cleaned
        return None

    @field_validator("annual_income")
    @classmethod
    def validate_annual_income(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Annual income cannot be negative")
        return v


class CitizenProfileResponse(CitizenProfileBase):
    """Complete citizen profile response with identifier and audit timestamps."""

    id: str = Field(..., description="Unique citizen user ID matching auth.users")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "11111111-1111-1111-1111-111111111111",
                "full_name": "Aarav Sharma",
                "date_of_birth": "2002-05-14",
                "gender": "Male",
                "contact_number": "9876543210",
                "state": "Maharashtra",
                "district": "Pune",
                "pincode": "411001",
                "education_level": "Undergraduate",
                "institution_name": "Savitribai Phule Pune University",
                "course": "B.Tech Computer Science",
                "academic_year": "3rd Year",
                "occupation": "Student",
                "annual_income": 250000.0,
                "social_category": "OBC",
                "disability_status": False,
                "minority_status": False,
                "created_at": "2026-11-01T12:00:00Z",
                "updated_at": "2026-11-01T12:00:00Z",
            }
        },
    }
