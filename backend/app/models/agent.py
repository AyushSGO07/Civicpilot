"""Pydantic schemas for browser automation, DOM inspection, and agent execution."""

from datetime import datetime, timezone
from typing import Optional, List, Literal
from pydantic import BaseModel, Field

BrowserSessionStatus = Literal[
    "idle",
    "navigating",
    "inspecting",
    "filling",
    "waiting_approval",
    "closed",
    "error",
]


class BrowserSessionInfo(BaseModel):
    """Metadata regarding an active or closed Playwright browser session."""

    session_id: str = Field(..., description="Unique browser session UUID")
    status: BrowserSessionStatus = Field("idle", description="Current execution state")
    current_url: Optional[str] = Field(None, description="Active page URL")
    page_title: Optional[str] = Field(None, description="Active page title")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BrowserNavigateRequest(BaseModel):
    """Payload to instruct browser to navigate to a target portal URL."""

    url: str = Field(..., min_length=1, description="Target government portal or web URL")
    wait_until: Literal["load", "domcontentloaded", "networkidle", "commit"] = Field(
        "domcontentloaded", description="Navigation wait state"
    )
    timeout_ms: int = Field(30000, ge=1000, le=120000, description="Navigation timeout in milliseconds")


class BrowserNavigateResponse(BaseModel):
    """Result returned after browser completes navigation."""

    session_id: str = Field(..., description="Active session ID")
    url: str = Field(..., description="Final resolved URL after redirects")
    page_title: str = Field(..., description="Page HTML document title")
    status_code: int = Field(200, description="HTTP response status code")
    screenshot_base64: Optional[str] = Field(None, description="Base64-encoded JPEG/PNG screenshot buffer")


class DOMElementNode(BaseModel):
    """A sanitized interactive form element extracted from the DOM tree."""

    tag: str = Field(..., description="HTML tag name (input, select, textarea, button)")
    element_id: Optional[str] = Field(None, description="HTML id attribute")
    name: Optional[str] = Field(None, description="Form input name attribute")
    element_type: Optional[str] = Field(None, description="Input type (text, email, tel, radio, checkbox, etc.)")
    label: Optional[str] = Field(None, description="Associated label, placeholder, or aria-label")
    placeholder: Optional[str] = Field(None, description="Input placeholder text")
    value: Optional[str] = Field(None, description="Pre-filled or default value")
    is_required: bool = Field(False, description="Whether the field is marked required")
    is_disabled: bool = Field(False, description="Whether the element is disabled")
    options: List[str] = Field(default_factory=list, description="Available option values and labels for select or radio")
    suggested_locator: str = Field(..., description="Playwright locator selector string")


class SanitizedDOMTree(BaseModel):
    """Pruned semantic interactive element representation of a webpage."""

    url: str = Field(..., description="URL of the inspected webpage")
    title: str = Field(..., description="Page title")
    forms_count: int = Field(0, description="Total count of <form> elements identified")
    interactive_elements_count: int = Field(0, description="Total count of actionable interactive elements")
    elements: List[DOMElementNode] = Field(default_factory=list, description="Extracted actionable elements")
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
