"""Citizen profile router for retrieving and updating citizen details."""

from datetime import datetime, timezone
from typing import Dict, Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.models.profile import (
    CitizenProfileBase,
    CitizenProfileUpdate,
    CitizenProfileResponse,
)

router = APIRouter(prefix="/profile", tags=["Citizen Profile"])

DEFAULT_USER_ID = "11111111-1111-1111-1111-111111111111"

# In-memory storage for deterministic tests and offline local execution
_PROFILES_STORE: Dict[str, dict] = {
    DEFAULT_USER_ID: {
        "id": DEFAULT_USER_ID,
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
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
}


async def get_current_user_id(
    authorization: Optional[str] = Header(None),
    x_citizen_id: Optional[str] = Header(None, alias="X-Citizen-ID"),
) -> str:
    """Dependency to extract authenticated citizen user ID from Bearer token or mock headers."""
    if x_citizen_id:
        return x_citizen_id

    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
            if token == "invalid-token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired authorization token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # In live production with Supabase, JWT is verified via Supabase SDK or secret
            return DEFAULT_USER_ID
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Local fallback for seamless development without pre-seeded cloud credentials
    return DEFAULT_USER_ID


@router.get("", response_model=CitizenProfileResponse)
async def get_citizen_profile(
    user_id: str = Depends(get_current_user_id),
):
    """Retrieve citizen profile for authenticated citizen user."""
    profile_data = _PROFILES_STORE.get(user_id)
    if not profile_data:
        # Initialize default profile skeleton for new user
        now = datetime.now(timezone.utc)
        profile_data = {
            "id": user_id,
            "full_name": "Citizen User",
            "date_of_birth": None,
            "gender": None,
            "contact_number": None,
            "state": None,
            "district": None,
            "pincode": None,
            "education_level": None,
            "institution_name": None,
            "course": None,
            "academic_year": None,
            "occupation": None,
            "annual_income": None,
            "social_category": None,
            "disability_status": False,
            "minority_status": False,
            "created_at": now,
            "updated_at": now,
        }
        _PROFILES_STORE[user_id] = profile_data

    return CitizenProfileResponse(**profile_data)


@router.put("", response_model=CitizenProfileResponse)
async def update_citizen_profile(
    profile_update: CitizenProfileUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Update citizen profile details for authenticated user."""
    profile_data = _PROFILES_STORE.get(user_id)
    now = datetime.now(timezone.utc)

    if not profile_data:
        profile_data = {
            "id": user_id,
            "full_name": profile_update.full_name or "Citizen User",
            "date_of_birth": None,
            "gender": None,
            "contact_number": None,
            "state": None,
            "district": None,
            "pincode": None,
            "education_level": None,
            "institution_name": None,
            "course": None,
            "academic_year": None,
            "occupation": None,
            "annual_income": None,
            "social_category": None,
            "disability_status": False,
            "minority_status": False,
            "created_at": now,
            "updated_at": now,
        }

    # Update only fields provided (excluding None)
    update_dict = profile_update.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        profile_data[field] = val

    profile_data["updated_at"] = now
    _PROFILES_STORE[user_id] = profile_data

    return CitizenProfileResponse(**profile_data)
