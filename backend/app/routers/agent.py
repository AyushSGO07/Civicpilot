"""Router for managing Playwright browser automation sessions and DOM inspection."""

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.agent import (
    BrowserSessionInfo,
    BrowserNavigateRequest,
    BrowserNavigateResponse,
    SanitizedDOMTree,
)
from app.services.browser_manager import browser_manager
from app.services.dom_inspector import DOMInspector

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
