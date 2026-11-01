"""Tests for Pre-Submission Summary, Approval Gate, and Rejection Branching (HIL-01, HIL-02, HIL-03)."""

import pytest
import httpx
import uuid
from typing import Dict, Any

from app.main import app
from app.models.workflow import AgentWorkflowState
from app.models.approval import PreSubmissionSummary
from app.services.browser_manager import browser_manager
from app.services.workflow_engine import (
    agent_workflow_app,
    waiting_approval_node,
    submit_node,
    rejected_node,
    route_after_approval,
)


@pytest.fixture(autouse=True)
async def cleanup_browser():
    """Ensure clean browser state before and after each test."""
    yield
    await browser_manager.shutdown()


@pytest.mark.asyncio
async def test_presubmission_summary_compilation():
    """Test that waiting_approval_node compiles structured PreSubmissionSummary (HIL-02)."""
    state: AgentWorkflowState = {
        "service_id": "pm-usp-scholarship",
        "portal_url": "https://scholarships.gov.in/",
        "current_step": "validation",
        "fill_plan": {
            "actions": [
                {
                    "action_type": "fill_text",
                    "element_label": "Applicant Full Name",
                    "element_name": "applicant_name",
                    "locator": "input#applicant_name",
                    "value_to_fill": "Aarav Sharma",
                    "source_attribute": "full_name",
                    "confidence": 0.98,
                },
                {
                    "action_type": "fill_text",
                    "element_label": "Annual Family Income",
                    "element_name": "annual_income",
                    "locator": "input#annual_income",
                    "value_to_fill": "250000",
                    "source_attribute": "annual_income",
                    "confidence": 0.99,
                },
                {
                    "action_type": "upload_file",
                    "element_label": "Income Certificate",
                    "element_name": "income_doc",
                    "locator": "input#income_doc",
                    "value_to_fill": "Income_Cert_2025.pdf",
                    "source_attribute": "income_certificate",
                    "confidence": 0.95,
                },
            ],
            "unmapped_elements": [],
        },
        "vault_documents": [
            {
                "id": "doc-aadhaar-1",
                "document_name": "Aadhaar Card",
                "category": "Aadhaar",
                "status": "verified",
            }
        ],
    }

    updated = await waiting_approval_node(state)

    assert updated["current_step"] == "waiting_approval"
    assert "pre_submission_summary" in updated
    summary_data = updated["pre_submission_summary"]
    assert summary_data is not None

    summary = PreSubmissionSummary(**summary_data)
    assert summary.service_id == "pm-usp-scholarship"
    assert summary.total_fields == 2
    assert len(summary.populated_fields) == 2
    assert summary.populated_fields[0].field_label == "Applicant Full Name"
    assert summary.populated_fields[0].value_populated == "Aarav Sharma"
    assert len(summary.attached_documents) == 1
    assert summary.attached_documents[0].document_name == "Income Certificate"
    assert "Statutory Advisory" in summary.disclaimer


@pytest.mark.asyncio
async def test_workflow_pauses_at_waiting_approval():
    """Verify workflow execution pauses at waiting_approval checkpoint without self-submitting (HIL-01)."""
    thread_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    sample_html = (
        "data:text/html,<html><body><form>"
        "<input id='name' name='name'/>"
        "<button type='submit'>Submit</button>"
        "</form></body></html>"
    )

    initial_state: AgentWorkflowState = {
        "session_id": session_id,
        "thread_id": thread_id,
        "service_id": "pm-usp-scholarship",
        "portal_url": sample_html,
        "citizen_profile": {"full_name": "Aarav Sharma"},
        "vault_documents": [],
        "current_step": "discovery",
        "error_count": 0,
        "max_retries": 3,
    }

    config = {"configurable": {"thread_id": thread_id}}
    result_state = await agent_workflow_app.ainvoke(initial_state, config=config)

    # Workflow must halt at waiting_approval and NOT proceed to submit or completed
    assert result_state["current_step"] == "waiting_approval"
    assert "pre_submission_summary" in result_state
    assert result_state.get("approval_decision") is None


@pytest.mark.asyncio
async def test_workflow_approve_resumes_submission():
    """Verify approving submission updates state and transitions to submission_ready (HIL-03)."""
    thread_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    sample_html = "data:text/html,<html><body><form><input id='name'/></form></body></html>"

    initial_state: AgentWorkflowState = {
        "session_id": session_id,
        "thread_id": thread_id,
        "service_id": "pm-usp-scholarship",
        "portal_url": sample_html,
        "citizen_profile": {"full_name": "Aarav Sharma"},
        "vault_documents": [],
        "current_step": "discovery",
    }

    config = {"configurable": {"thread_id": thread_id}}
    await agent_workflow_app.ainvoke(initial_state, config=config)

    # Now simulate approval
    await agent_workflow_app.aupdate_state(
        config,
        {"approval_decision": "approved", "rejection_reason": None},
    )

    resumed_state = await agent_workflow_app.ainvoke(None, config=config)
    assert resumed_state["current_step"] == "submission_ready"
    assert resumed_state["approval_decision"] == "approved"


@pytest.mark.asyncio
async def test_workflow_reject_halts_submission():
    """Verify rejecting submission halts workflow and transitions to submission_rejected (HIL-03)."""
    thread_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())

    sample_html = "data:text/html,<html><body><form><input id='name'/></form></body></html>"

    initial_state: AgentWorkflowState = {
        "session_id": session_id,
        "thread_id": thread_id,
        "service_id": "pm-usp-scholarship",
        "portal_url": sample_html,
        "citizen_profile": {"full_name": "Aarav Sharma"},
        "vault_documents": [],
        "current_step": "discovery",
    }

    config = {"configurable": {"thread_id": thread_id}}
    await agent_workflow_app.ainvoke(initial_state, config=config)

    # Simulate rejection with reason
    await agent_workflow_app.aupdate_state(
        config,
        {"approval_decision": "rejected", "rejection_reason": "Income was entered incorrectly"},
    )

    resumed_state = await agent_workflow_app.ainvoke(None, config=config)
    assert resumed_state["current_step"] == "submission_rejected"
    assert resumed_state["approval_decision"] == "rejected"
    assert resumed_state["rejection_reason"] == "Income was entered incorrectly"


@pytest.mark.asyncio
async def test_api_approval_endpoints():
    """Verify REST API endpoints for summary, approve, and reject (HIL-01, HIL-02, HIL-03)."""
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        # Start a workflow
        start_payload = {
            "service_id": "pm-usp-scholarship",
            "portal_url_override": "data:text/html,<html><body><form><input id='name' name='name'/></form></body></html>",
        }
        res_start = await client.post("/api/agent/workflow/start", json=start_payload)
        assert res_start.status_code == 200
        thread_id = res_start.json()["thread_id"]

        # Fetch PreSubmissionSummary via API (HIL-02)
        res_summary = await client.get(f"/api/agent/workflow/{thread_id}/summary")
        assert res_summary.status_code == 200
        summary = res_summary.json()
        assert summary["service_id"] == "pm-usp-scholarship"
        assert "Statutory Advisory" in summary["disclaimer"]

        # Approve submission via API (HIL-03)
        res_approve = await client.post(f"/api/agent/workflow/{thread_id}/approve")
        assert res_approve.status_code == 200
        data_approve = res_approve.json()
        assert data_approve["decision"] == "approved"
        assert data_approve["current_step"] == "submission_ready"

        # 404 for invalid thread
        bad_res = await client.get("/api/agent/workflow/nonexistent-thread-id/summary")
        assert bad_res.status_code == 404
