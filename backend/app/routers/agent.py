"""Router for managing Playwright browser automation sessions, DOM inspection, and form filling."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.agent import (
    BrowserSessionInfo,
    BrowserNavigateRequest,
    BrowserNavigateResponse,
    SanitizedDOMTree,
)
from app.models.profile import CitizenProfileBase
from app.models.form_filling import (
    FormFillPlan,
    FormExecutionResult,
)
from app.services.browser_manager import browser_manager
from app.services.dom_inspector import DOMInspector
from app.services.field_mapper import DynamicFieldMapper
from app.services.form_executor import FormActionExecutor
from app.routers.profile import _PROFILES_STORE, DEFAULT_USER_ID
from app.routers.documents import _DOCUMENTS_STORE

router = APIRouter(prefix="/agent/browser", tags=["Agent & Browser Automation"])


class SessionStartResponse(BaseModel):
    session_id: str = Field(..., description="Initialized browser session UUID")
    status: str = Field("idle", description="Session state")


class SessionCloseResponse(BaseModel):
    session_id: str = Field(..., description="Terminated session UUID")
    status: str = Field("closed", description="Session state")


class ScreenshotResponse(BaseModel):
    session_id: str
    screenshot_base64: str


class PlanFormRequest(BaseModel):
    citizen_profile: Optional[CitizenProfileBase] = Field(
        None, description="Citizen profile attributes override; if omitted, authenticated profile is used"
    )
    vault_documents: Optional[List[Dict[str, Any]]] = Field(
        None, description="Optional vault document metadata list override"
    )


def _get_active_profile(override: Optional[CitizenProfileBase] = None) -> CitizenProfileBase:
    """Retrieve citizen profile for form filling from override or default store."""
    if override:
        return override
    profile_data = _PROFILES_STORE.get(DEFAULT_USER_ID, {})
    return CitizenProfileBase(
        full_name=profile_data.get("full_name", "Aarav Sharma"),
        date_of_birth=profile_data.get("date_of_birth"),
        gender=profile_data.get("gender"),
        contact_number=profile_data.get("contact_number"),
        state=profile_data.get("state"),
        district=profile_data.get("district"),
        pincode=profile_data.get("pincode"),
        education_level=profile_data.get("education_level"),
        institution_name=profile_data.get("institution_name"),
        course=profile_data.get("course"),
        academic_year=profile_data.get("academic_year"),
        occupation=profile_data.get("occupation"),
        annual_income=profile_data.get("annual_income"),
        social_category=profile_data.get("social_category"),
        disability_status=profile_data.get("disability_status", False),
        minority_status=profile_data.get("minority_status", False),
    )


def _get_active_vault_documents(override: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Retrieve list of documents available in the citizen's vault."""
    if override is not None:
        return override
    # Convert _DOCUMENTS_STORE values to list
    return list(_DOCUMENTS_STORE.values())


@router.post(
    "/session/start",
    response_model=SessionStartResponse,
    summary="Start an isolated Playwright browser session (AGENT-01)",
)
async def start_session(session_id: Optional[str] = None):
    """Launch an isolated Playwright Chromium context with desktop viewport and return session ID."""
    sid = await browser_manager.create_session(session_id)
    return SessionStartResponse(session_id=sid, status="idle")


@router.get(
    "/session/{session_id}",
    response_model=BrowserSessionInfo,
    summary="Get status of an active browser session",
)
async def get_session(session_id: str):
    """Retrieve metadata and active state for the specified browser session."""
    info = await browser_manager.get_session_info(session_id)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Browser session '{session_id}' not found or has been closed",
        )
    return info


@router.post(
    "/session/{session_id}/navigate",
    response_model=BrowserNavigateResponse,
    summary="Navigate browser session to target URL (AGENT-01)",
)
async def navigate_page(session_id: str, request: BrowserNavigateRequest):
    """Navigate session to a verified government portal URL and return screenshot buffer."""
    page = await browser_manager.get_page(session_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Browser session '{session_id}' is not active",
        )

    try:
        return await browser_manager.navigate(
            session_id=session_id,
            url=request.url,
            wait_until=request.wait_until,
            timeout_ms=request.timeout_ms,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Navigation failed: {str(e)}",
        )


@router.get(
    "/session/{session_id}/inspect",
    response_model=SanitizedDOMTree,
    summary="Extract sanitized semantic DOM element tree (AGENT-02)",
)
async def inspect_dom(session_id: str):
    """Inspect active webpage and extract actionable form elements, labels, and locators."""
    page = await browser_manager.get_page(session_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Browser session '{session_id}' is not active",
        )

    try:
        return await DOMInspector.inspect_page(page)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DOM inspection failed: {str(e)}",
        )


@router.post(
    "/session/{session_id}/form/plan",
    response_model=FormFillPlan,
    summary="Generate dynamic form filling plan from DOM and profile (AGENT-03, AGENT-05)",
)
async def plan_form_filling(
    session_id: str,
    request: Optional[PlanFormRequest] = None,
):
    """Inspect current webpage and generate structured action plan without hardcoded CSS selectors."""
    page = await browser_manager.get_page(session_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Browser session '{session_id}' is not active",
        )

    dom_tree = await DOMInspector.inspect_page(page)
    profile = _get_active_profile(request.citizen_profile if request else None)
    vault_docs = _get_active_vault_documents(request.vault_documents if request else None)

    return await DynamicFieldMapper.generate_fill_plan(dom_tree, profile, vault_docs)


@router.post(
    "/session/{session_id}/form/execute",
    response_model=FormExecutionResult,
    summary="Autonomously execute form actions on the browser page (AGENT-04, AGENT-05)",
)
async def execute_form_filling(
    session_id: str,
    plan: FormFillPlan,
):
    """Populate inputs, dropdowns, checkboxes, and attach vault files according to the plan."""
    page = await browser_manager.get_page(session_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Browser session '{session_id}' is not active",
        )

    return await FormActionExecutor.execute_plan(page, session_id, plan)


@router.post(
    "/session/{session_id}/form/fill",
    response_model=FormExecutionResult,
    summary="Inspect, plan, and populate form in one autonomous operation (AGENT-03, AGENT-04, AGENT-05)",
)
async def fill_form_composite(
    session_id: str,
    request: Optional[PlanFormRequest] = None,
):
    """Convenience endpoint combining DOM inspection, Gemini field mapping, and Playwright execution."""
    page = await browser_manager.get_page(session_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Browser session '{session_id}' is not active",
        )

    dom_tree = await DOMInspector.inspect_page(page)
    profile = _get_active_profile(request.citizen_profile if request else None)
    vault_docs = _get_active_vault_documents(request.vault_documents if request else None)

    plan = await DynamicFieldMapper.generate_fill_plan(dom_tree, profile, vault_docs)
    return await FormActionExecutor.execute_plan(page, session_id, plan)


@router.get(
    "/session/{session_id}/screenshot",
    response_model=ScreenshotResponse,
    summary="Capture Base64 screenshot of current browser page",
)
async def get_screenshot(session_id: str):
    """Capture and return JPEG screenshot buffer of active browser session."""
    page = await browser_manager.get_page(session_id)
    if not page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Browser session '{session_id}' is not active",
        )

    screenshot_b64 = await browser_manager.capture_screenshot_base64(session_id)
    if not screenshot_b64:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to capture page screenshot buffer",
        )

    return ScreenshotResponse(session_id=session_id, screenshot_base64=screenshot_b64)


@router.post(
    "/session/{session_id}/close",
    response_model=SessionCloseResponse,
    summary="Cleanly terminate browser session and context (AGENT-07)",
)
async def close_session(session_id: str):
    """Close browser page and context, preventing orphaned/zombie processes."""
    closed = await browser_manager.close_session(session_id)
    if not closed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Browser session '{session_id}' not found or already closed",
        )
    return SessionCloseResponse(session_id=session_id, status="closed")
