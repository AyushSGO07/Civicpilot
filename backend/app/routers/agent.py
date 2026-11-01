"""Router for managing Playwright browser automation sessions, DOM inspection, form filling, and LangGraph workflows."""

import base64
import uuid
from datetime import datetime, timezone
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
from app.models.workflow import (
    WorkflowStartRequest,
    WorkflowStateResponse,
    AgentWorkflowState,
)
from app.models.approval import (
    PreSubmissionSummary,
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
)
from app.models.security_challenge import (
    ResolveChallengeRequest,
    ResolveChallengeResponse,
)
from app.services.browser_manager import browser_manager
from app.services.dom_inspector import DOMInspector
from app.services.field_mapper import DynamicFieldMapper
from app.services.form_executor import FormActionExecutor
from app.services.workflow_engine import agent_workflow_app
from app.routers.profile import _PROFILES_STORE, DEFAULT_USER_ID
from app.routers.documents import _DOCUMENTS_STORE

router = APIRouter(prefix="/agent", tags=["Agent & Browser Automation"])


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
    return list(_DOCUMENTS_STORE.values())


# -------------------------------------------------------------------------
# Browser Automation & Session Endpoints
# -------------------------------------------------------------------------

@router.post(
    "/browser/session/start",
    response_model=SessionStartResponse,
    summary="Start an isolated Playwright browser session (AGENT-01)",
)
async def start_session(session_id: Optional[str] = None):
    """Launch an isolated Playwright Chromium context with desktop viewport and return session ID."""
    sid = await browser_manager.create_session(session_id)
    return SessionStartResponse(session_id=sid, status="idle")


@router.get(
    "/browser/session/{session_id}",
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
    "/browser/session/{session_id}/navigate",
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
    "/browser/session/{session_id}/inspect",
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
    "/browser/session/{session_id}/form/plan",
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
    "/browser/session/{session_id}/form/execute",
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
    "/browser/session/{session_id}/form/fill",
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
    "/browser/session/{session_id}/screenshot",
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
    "/browser/session/{session_id}/close",
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


# -------------------------------------------------------------------------
# LangGraph Workflow Controller Endpoints (AGENT-06)
# -------------------------------------------------------------------------

@router.post(
    "/workflow/start",
    response_model=WorkflowStateResponse,
    summary="Start a stateful LangGraph agent workflow with bounded recovery (AGENT-06)",
)
async def start_workflow(request: WorkflowStartRequest):
    """Launch end-to-end agent workflow (Discover -> Navigate -> Inspect -> Map -> Fill -> Validate)."""
    thread_id = request.thread_id or request.session_id or str(uuid.uuid4())
    session_id = request.session_id or thread_id

    profile_dict = request.custom_profile or _get_active_profile().model_dump()
    vault_docs = request.custom_vault_documents or _get_active_vault_documents()

    initial_state: AgentWorkflowState = {
        "session_id": session_id,
        "thread_id": thread_id,
        "service_id": request.service_id,
        "portal_url": request.portal_url_override or "",
        "citizen_profile": profile_dict,
        "vault_documents": vault_docs,
        "current_step": "discovery",
        "error_count": 0,
        "max_retries": 3,
        "logs": [],
        "dialog_messages": [],
    }

    config = {"configurable": {"thread_id": thread_id}}

    try:
        final_state = await agent_workflow_app.ainvoke(initial_state, config=config)
        return WorkflowStateResponse(
            thread_id=thread_id,
            session_id=final_state.get("session_id", session_id),
            service_id=final_state.get("service_id", request.service_id),
            portal_url=final_state.get("portal_url", ""),
            current_step=final_state.get("current_step", "completed"),
            error_count=final_state.get("error_count", 0),
            max_retries=final_state.get("max_retries", 3),
            error_message=final_state.get("error_message"),
            dialog_messages=final_state.get("dialog_messages", []),
            logs=final_state.get("logs", []),
            screenshot_base64=final_state.get("screenshot_base64"),
            execution_result=final_state.get("execution_result"),
            fill_plan=final_state.get("fill_plan"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}",
        )


@router.get(
    "/workflow/{thread_id}/state",
    response_model=WorkflowStateResponse,
    summary="Retrieve state snapshot of a workflow thread from checkpointer",
)
async def get_workflow_state(thread_id: str):
    """Query persisted LangGraph state snapshot by thread ID."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await agent_workflow_app.aget_state(config)

    if not snapshot or not snapshot.values:
        # Graceful fallback: check if active browser session exists
        page = await browser_manager.get_page(thread_id)
        if page:
            screenshot_b64 = None
            try:
                buf = await page.screenshot(type="jpeg", quality=60)
                screenshot_b64 = base64.b64encode(buf).decode("utf-8")
            except Exception:
                pass
            return WorkflowStateResponse(
                thread_id=thread_id,
                session_id=thread_id,
                service_id="active",
                portal_url=page.url if page else "",
                current_step="navigation",
                logs=[{
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": "info",
                    "message": "Browser session active on portal",
                    "step": "navigation",
                }],
                screenshot_base64=screenshot_b64,
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow thread '{thread_id}' not found in checkpointer",
        )

    values = snapshot.values
    return WorkflowStateResponse(
        thread_id=thread_id,
        session_id=values.get("session_id", ""),
        service_id=values.get("service_id", ""),
        portal_url=values.get("portal_url", ""),
        current_step=values.get("current_step", "unknown"),
        error_count=values.get("error_count", 0),
        max_retries=values.get("max_retries", 3),
        error_message=values.get("error_message"),
        dialog_messages=values.get("dialog_messages", []),
        logs=values.get("logs", []),
        screenshot_base64=values.get("screenshot_base64"),
        execution_result=values.get("execution_result"),
        fill_plan=values.get("fill_plan"),
        pre_submission_summary=values.get("pre_submission_summary"),
        approval_decision=values.get("approval_decision"),
        rejection_reason=values.get("rejection_reason"),
    )


@router.post(
    "/workflow/{thread_id}/resume",
    response_model=WorkflowStateResponse,
    summary="Resume execution on a paused workflow thread",
)
async def resume_workflow(thread_id: str):
    """Resume execution on an interrupted or paused workflow thread."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await agent_workflow_app.aget_state(config)

    if not snapshot or not snapshot.values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow thread '{thread_id}' not found in checkpointer",
        )

    # Continue execution from current checkpoint
    final_state = await agent_workflow_app.ainvoke(None, config=config)
    return WorkflowStateResponse(
        thread_id=thread_id,
        session_id=final_state.get("session_id", ""),
        service_id=final_state.get("service_id", ""),
        portal_url=final_state.get("portal_url", ""),
        current_step=final_state.get("current_step", "completed"),
        error_count=final_state.get("error_count", 0),
        max_retries=final_state.get("max_retries", 3),
        error_message=final_state.get("error_message"),
        dialog_messages=final_state.get("dialog_messages", []),
        logs=final_state.get("logs", []),
        screenshot_base64=final_state.get("screenshot_base64"),
        execution_result=final_state.get("execution_result"),
        fill_plan=final_state.get("fill_plan"),
        pre_submission_summary=final_state.get("pre_submission_summary"),
        approval_decision=final_state.get("approval_decision"),
        rejection_reason=final_state.get("rejection_reason"),
    )


@router.get(
    "/workflow/{thread_id}/summary",
    response_model=PreSubmissionSummary,
    summary="Retrieve pre-submission summary of all populated form values and vault documents (HIL-02)",
)
async def get_workflow_summary(thread_id: str):
    """Retrieve structured pre-submission audit for human review."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await agent_workflow_app.aget_state(config)

    if not snapshot or not snapshot.values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow thread '{thread_id}' not found in checkpointer",
        )

    summary = snapshot.values.get("pre_submission_summary")
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pre-submission summary has not yet been compiled for thread '{thread_id}'",
        )

    return PreSubmissionSummary(**summary)


@router.post(
    "/workflow/{thread_id}/approve",
    response_model=ApprovalDecisionResponse,
    summary="Citizen grants explicit approval to submit application (HIL-01, HIL-03)",
)
async def approve_workflow_submission(thread_id: str):
    """Grant explicit user authorization to submit the completed application."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await agent_workflow_app.aget_state(config)

    if not snapshot or not snapshot.values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow thread '{thread_id}' not found in checkpointer",
        )

    # Update state with citizen approval decision
    await agent_workflow_app.aupdate_state(
        config,
        {"approval_decision": "approved", "rejection_reason": None},
    )

    # Resume workflow from waiting_approval to submit_node
    final_state = await agent_workflow_app.ainvoke(None, config=config)

    return ApprovalDecisionResponse(
        thread_id=thread_id,
        status="approved",
        decision="approved",
        message="Application submission authorized by citizen. Ready for official portal submission.",
        current_step=final_state.get("current_step", "submission_ready"),
    )


@router.post(
    "/workflow/{thread_id}/reject",
    response_model=ApprovalDecisionResponse,
    summary="Citizen rejects application submission to edit or cancel (HIL-03)",
)
async def reject_workflow_submission(thread_id: str, request: Optional[ApprovalDecisionRequest] = None):
    """Reject application submission and return workflow to review or editing mode."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await agent_workflow_app.aget_state(config)

    if not snapshot or not snapshot.values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow thread '{thread_id}' not found in checkpointer",
        )

    reason = request.rejection_reason if request else "Rejected by citizen"

    # Update state with citizen rejection decision
    await agent_workflow_app.aupdate_state(
        config,
        {"approval_decision": "rejected", "rejection_reason": reason},
    )

    # Resume workflow from waiting_approval to rejected_node
    final_state = await agent_workflow_app.ainvoke(None, config=config)

    return ApprovalDecisionResponse(
        thread_id=thread_id,
        status="rejected",
        decision="rejected",
        message=f"Application submission rejected: {reason}",
        current_step=final_state.get("current_step", "submission_rejected"),
    )


@router.post(
    "/workflow/{thread_id}/resolve-challenge",
    response_model=ResolveChallengeResponse,
    summary="Citizen confirms completion of security challenge (CAPTCHA / OTP / MFA) (HIL-04)",
)
async def resolve_workflow_challenge(
    thread_id: str,
    request: Optional[ResolveChallengeRequest] = None,
):
    """Confirm security challenge resolution and resume workflow from paused checkpoint."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = await agent_workflow_app.aget_state(config)

    if not snapshot or not snapshot.values:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow thread '{thread_id}' not found in checkpointer",
        )

    # Mark challenge as resolved in LangGraph state
    await agent_workflow_app.aupdate_state(
        config,
        {
            "challenge_resolved": True,
            "security_challenge": None,
        },
    )

    # Resume workflow from checkpoint
    final_state = await agent_workflow_app.ainvoke(None, config=config)

    return ResolveChallengeResponse(
        thread_id=thread_id,
        status="resumed",
        message="Security challenge resolved by citizen. Automation resumed.",
        challenge_resolved=True,
    )
