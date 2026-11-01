"""Tests for LangGraph agent workflow orchestration and bounded recovery (AGENT-06)."""

import pytest
import httpx
import uuid

from app.main import app
from app.models.workflow import AgentWorkflowState
from app.services.browser_manager import browser_manager
from app.services.workflow_engine import (
    agent_workflow_app,
    build_agent_workflow,
    discover_node,
    navigate_node,
    inspect_node,
    map_node,
    fill_node,
    validate_node,
    recovery_node,
    human_assistance_node,
)


@pytest.fixture(autouse=True)
async def cleanup_browser():
    """Ensure clean browser state before and after each test."""
    yield
    await browser_manager.shutdown()


@pytest.mark.asyncio
async def test_workflow_happy_path():
    """Verify complete LangGraph workflow from discovery to waiting_approval (AGENT-06)."""
    thread_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    sample_form_html = (
        "data:text/html,<html><head><title>NSP Registration Portal</title></head><body>"
        "<form id='appForm'>"
        "<label for='fullName'>Applicant Name</label><input type='text' id='fullName' name='fullName' required/>"
        "<label for='income'>Annual Income</label><input type='number' id='income' name='income' required/>"
        "<label for='state'>Domicile State</label><select id='state' name='state'><option value='MH'>Maharashtra</option></select>"
        "<button type='submit'>Submit Application</button>"
        "</form></body></html>"
    )

    initial_state: AgentWorkflowState = {
        "session_id": session_id,
        "thread_id": thread_id,
        "service_id": "pm-usp-scholarship",
        "portal_url": sample_form_html,
        "citizen_profile": {
            "full_name": "Aarav Sharma",
            "annual_income": 250000.0,
            "state": "Maharashtra",
        },
        "vault_documents": [],
        "current_step": "discovery",
        "error_count": 0,
        "max_retries": 3,
        "logs": [],
        "dialog_messages": [],
    }

    config = {"configurable": {"thread_id": thread_id}}
    final_state = await agent_workflow_app.ainvoke(initial_state, config=config)

    # Reaches waiting_approval on happy path
    assert final_state["current_step"] == "waiting_approval"
    assert final_state["error_count"] == 0
    assert final_state["execution_result"] is not None
    assert final_state["execution_result"]["successful_actions"] >= 2
    assert final_state["screenshot_base64"] is not None
    assert len(final_state["logs"]) >= 6


@pytest.mark.asyncio
async def test_workflow_dialog_interception():
    """Verify Playwright alert listener captures and dismisses unexpected modals without blocking."""
    thread_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    alert_html = (
        "data:text/html,<html><head><title>Alert Test</title></head><body>"
        "<script>window.addEventListener('DOMContentLoaded', () => { setTimeout(() => alert('Important Government Notice: Aadhaar is mandatory'), 100); });</script>"
        "<form><label for='candName'>Candidate Name</label><input type='text' id='candName' name='candName'/></form>"
        "</body></html>"
    )

    initial_state: AgentWorkflowState = {
        "session_id": session_id,
        "thread_id": thread_id,
        "service_id": "pm-usp-scholarship",
        "portal_url": alert_html,
        "citizen_profile": {"full_name": "Aarav Sharma"},
        "vault_documents": [],
        "current_step": "discovery",
        "error_count": 0,
        "max_retries": 3,
        "logs": [],
        "dialog_messages": [],
    }

    config = {"configurable": {"thread_id": thread_id}}
    final_state = await agent_workflow_app.ainvoke(initial_state, config=config)

    # Check alert was intercepted into dialog_messages
    assert final_state["current_step"] in ["waiting_approval", "completed"]
    assert any("Aadhaar is mandatory" in msg for msg in final_state.get("dialog_messages", []))


@pytest.mark.asyncio
async def test_workflow_bounded_recovery_retries_and_escalates_to_human():
    """Verify bounded recovery increments error_count and halts at max_retries=3, escalating to human assistance (AGENT-06)."""
    thread_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    # Form with no matching inputs but simulated failure
    empty_html = "data:text/html,<html><head><title>Broken Form</title></head><body><p>Maintenance</p></body></html>"

    # Test recovery node directly
    state: AgentWorkflowState = {
        "session_id": session_id,
        "thread_id": thread_id,
        "service_id": "pm-usp-scholarship",
        "portal_url": empty_html,
        "citizen_profile": {"full_name": "Aarav Sharma"},
        "vault_documents": [],
        "current_step": "validation",
        "error_count": 0,
        "max_retries": 3,
        "logs": [],
        "dialog_messages": [],
        "execution_result": {"failed_actions": 1, "successful_actions": 0},
    }

    # First retry
    state = await recovery_node(state)
    assert state["error_count"] == 1
    assert state["current_step"] == "recovery"

    # Second retry
    state = await recovery_node(state)
    assert state["error_count"] == 2

    # Third retry
    state = await recovery_node(state)
    assert state["error_count"] == 3

    # On exceeding max retries, escalate to human assistance
    state = await human_assistance_node(state)
    assert state["current_step"] == "human_assistance"
    assert "Escalated to Human Assistance" in state["error_message"]


@pytest.mark.asyncio
async def test_api_workflow_lifecycle_endpoints():
    """Verify FastAPI endpoints for starting workflow and retrieving state from checkpointer (AGENT-06)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        sample_url = (
            "data:text/html,<html><head><title>API Workflow Test</title></head><body>"
            "<form><label for='stdName'>Student Name</label><input type='text' id='stdName' name='stdName'/></form>"
            "</body></html>"
        )

        # 1. Start workflow
        start_res = await client.post(
            "/api/agent/workflow/start",
            json={
                "service_id": "pm-usp-scholarship",
                "portal_url_override": sample_url,
                "custom_profile": {"full_name": "Aarav Sharma"},
            },
        )
        assert start_res.status_code == 200
        start_data = start_res.json()
        thread_id = start_data["thread_id"]
        assert thread_id is not None
        assert start_data["current_step"] in ["waiting_approval", "completed"]

        # 2. Get workflow state from checkpointer
        state_res = await client.get(f"/api/agent/workflow/{thread_id}/state")
        assert state_res.status_code == 200
        state_data = state_res.json()
        assert state_data["thread_id"] == thread_id
        assert state_data["service_id"] == "pm-usp-scholarship"
        assert len(state_data["logs"]) >= 5


@pytest.mark.asyncio
async def test_api_workflow_not_found_404():
    """Verify querying non-existent workflow thread returns HTTP 404."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/agent/workflow/non-existent-thread-12345/state")
        assert res.status_code == 404
