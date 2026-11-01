"""Tests for Security Challenge Detector (CAPTCHA / OTP / MFA) and Citizen Pause Gate (HIL-04)."""

import pytest
import httpx
import uuid

from app.main import app
from app.models.agent import SanitizedDOMTree, DOMElementNode
from app.models.workflow import AgentWorkflowState
from app.services.security_detector import SecurityChallengeDetector
from app.services.browser_manager import browser_manager
from app.services.workflow_engine import agent_workflow_app


@pytest.fixture(autouse=True)
async def cleanup_browser():
    """Ensure clean browser state before and after each test."""
    yield
    await browser_manager.shutdown()


def test_security_detector_identifies_captcha_element():
    """Test detection of CAPTCHA input element signatures (HIL-04)."""
    elements = [
        DOMElementNode(
            tag="input",
            element_id="txtCaptcha",
            name="txtCaptcha",
            element_type="text",
            label="Enter the security code shown above",
            suggested_locator="input#txtCaptcha",
        ),
        DOMElementNode(
            tag="button",
            element_id="btnSubmit",
            element_type="submit",
            label="Submit",
            suggested_locator="button#btnSubmit",
        ),
    ]
    tree = SanitizedDOMTree(
        url="https://portal.gov.in/register",
        title="Portal Registration",
        forms_count=1,
        interactive_elements_count=2,
        elements=elements,
    )

    info = SecurityChallengeDetector.detect_challenge(dom_tree=tree)
    assert info.detected is True
    assert info.challenge_type == "captcha"
    assert "CAPTCHA" in info.instructions
    assert "txtCaptcha" in info.element_locator


def test_security_detector_identifies_otp_element():
    """Test detection of OTP input element signatures (HIL-04)."""
    elements = [
        DOMElementNode(
            tag="input",
            element_id="mobile_otp",
            name="otp",
            element_type="text",
            label="Enter 6-digit OTP sent to registered mobile",
            suggested_locator="input#mobile_otp",
        )
    ]
    tree = SanitizedDOMTree(
        url="https://portal.gov.in/verify",
        title="Mobile Verification",
        forms_count=1,
        interactive_elements_count=1,
        elements=elements,
    )

    info = SecurityChallengeDetector.detect_challenge(dom_tree=tree)
    assert info.detected is True
    assert info.challenge_type == "otp"
    assert "OTP" in info.instructions


def test_security_detector_identifies_challenge_in_text():
    """Test detection of CAPTCHA or OTP prompt text in page content (HIL-04)."""
    text_captcha = "Please enter the characters shown in the image below to proceed."
    info_captcha = SecurityChallengeDetector.detect_challenge(page_text=text_captcha)
    assert info_captcha.detected is True
    assert info_captcha.challenge_type == "captcha"

    text_otp = "An OTP has been sent to your registered mobile number ending with 4321."
    info_otp = SecurityChallengeDetector.detect_challenge(page_text=text_otp)
    assert info_otp.detected is True
    assert info_otp.challenge_type == "otp"


def test_security_detector_negative_normal_form():
    """Test that standard profile inputs do NOT trigger false-positive challenge detection."""
    elements = [
        DOMElementNode(
            tag="input",
            element_id="fullName",
            name="fullName",
            element_type="text",
            label="Applicant Full Name",
            suggested_locator="input#fullName",
        ),
        DOMElementNode(
            tag="input",
            element_id="annualIncome",
            name="annualIncome",
            element_type="number",
            label="Annual Family Income (INR)",
            suggested_locator="input#annualIncome",
        ),
    ]
    tree = SanitizedDOMTree(
        url="https://scholarships.gov.in/",
        title="Scholarship Application",
        forms_count=1,
        interactive_elements_count=2,
        elements=elements,
    )

    info = SecurityChallengeDetector.detect_challenge(dom_tree=tree)
    assert info.detected is False
    assert info.challenge_type is None


@pytest.mark.asyncio
async def test_workflow_pauses_on_security_challenge():
    """Verify workflow enters waiting_security_challenge when CAPTCHA is detected (HIL-04)."""
    thread_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    html_with_captcha = (
        "data:text/html,<html><body><form>"
        "<input id='name' name='name'/>"
        "<label for='txtCaptcha'>Enter Captcha</label>"
        "<input id='txtCaptcha' name='captcha'/>"
        "<button type='submit'>Register</button>"
        "</form></body></html>"
    )

    initial_state: AgentWorkflowState = {
        "session_id": session_id,
        "thread_id": thread_id,
        "service_id": "pm-usp-scholarship",
        "portal_url": html_with_captcha,
        "citizen_profile": {"full_name": "Aarav Sharma"},
        "vault_documents": [],
        "current_step": "discovery",
        "error_count": 0,
        "max_retries": 3,
    }

    config = {"configurable": {"thread_id": thread_id}}
    result_state = await agent_workflow_app.ainvoke(initial_state, config=config)

    # Workflow must pause at waiting_security_challenge
    assert result_state["current_step"] == "waiting_security_challenge"
    assert result_state.get("security_challenge") is not None
    assert result_state["security_challenge"]["detected"] is True
    assert result_state["security_challenge"]["challenge_type"] == "captcha"


@pytest.mark.asyncio
async def test_resolve_challenge_resumes_workflow():
    """Verify resolving security challenge unblocks execution and continues workflow (HIL-04)."""
    thread_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    html_with_captcha = (
        "data:text/html,<html><body><form>"
        "<input id='name' name='name'/>"
        "<input id='txtCaptcha' name='captcha'/>"
        "</form></body></html>"
    )

    initial_state: AgentWorkflowState = {
        "session_id": session_id,
        "thread_id": thread_id,
        "service_id": "pm-usp-scholarship",
        "portal_url": html_with_captcha,
        "citizen_profile": {"full_name": "Aarav Sharma"},
        "vault_documents": [],
        "current_step": "discovery",
    }

    config = {"configurable": {"thread_id": thread_id}}
    paused_state = await agent_workflow_app.ainvoke(initial_state, config=config)
    assert paused_state["current_step"] == "waiting_security_challenge"

    # Now simulate resolving the challenge
    await agent_workflow_app.aupdate_state(
        config,
        {"challenge_resolved": True, "security_challenge": None},
    )

    resumed_state = await agent_workflow_app.ainvoke(None, config=config)
    # The workflow moves forward from inspect -> map -> fill -> validate -> waiting_approval
    assert resumed_state["current_step"] == "waiting_approval"
    assert resumed_state.get("challenge_resolved") is True
