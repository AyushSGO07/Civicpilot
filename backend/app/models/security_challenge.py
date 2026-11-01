"""Pydantic models for security challenge detection (CAPTCHA / OTP / MFA) and citizen resolution (HIL-04)."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class SecurityChallengeInfo(BaseModel):
    """Information regarding a detected security challenge on the official portal."""

    detected: bool = Field(False, description="Whether a security challenge is currently active")
    challenge_type: Optional[Literal["captcha", "otp", "mfa"]] = Field(
        None, description="Class of security challenge detected"
    )
    element_locator: Optional[str] = Field(
        None, description="Playwright locator or identifier of the challenge input"
    )
    instructions: str = Field(
        "", description="Actionable guidance for the citizen to solve the challenge"
    )
    prompt_message: str = Field(
        "", description="Portal prompt text extracted from DOM or alert"
    )
    detected_at: Optional[str] = Field(
        None, description="ISO timestamp when challenge was intercepted"
    )


class ResolveChallengeRequest(BaseModel):
    """Payload sent when citizen has completed the security challenge in the browser."""

    challenge_type: Literal["captcha", "otp", "mfa"] = Field(
        ..., description="Type of challenge solved by citizen"
    )
    resolution_notes: Optional[str] = Field(
        None, description="Optional notes on manual intervention"
    )


class ResolveChallengeResponse(BaseModel):
    """Response returned after recording challenge resolution."""

    thread_id: str = Field(..., description="LangGraph execution thread UUID")
    status: str = Field(..., description="Updated execution status ('resumed', 'active')")
    message: str = Field(..., description="Status summary message")
    challenge_resolved: bool = Field(True, description="Resolution confirmation")
