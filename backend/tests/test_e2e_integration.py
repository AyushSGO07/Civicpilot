"""End-to-End Integration and Error Scenario Verification Test Suite (Phase 12).

Validates complete citizen lifecycle from Scheme Discovery to PDF Receipt Retrieval,
error boundary conditions, security challenges, and statutory compliance across all requirements.
"""

from datetime import datetime, timezone
import httpx
import pytest
import pymupdf
from fastapi.testclient import TestClient

from app.main import app
from app.models.workflow import AgentWorkflowState
from app.services.browser_manager import browser_manager
from app.services.workflow_engine import route_after_validation, route_after_recovery
from app.models.application import ApplicationRecord
from app.services.submission_verifier import ReceiptGenerator

client = TestClient(app)


@pytest.fixture(autouse=True)
async def cleanup_browser():
    """Ensure clean Playwright Chromium state before and after each test (AGENT-07)."""
    yield
    await browser_manager.shutdown()


@pytest.mark.asyncio
async def test_e2e_happy_path_lifecycle():
    """Complete E2E Citizen Lifecycle: Discovery -> Eligibility -> Form Fill -> HIL Approval -> Submission -> Receipt."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as a_client:
        # Step 1: Scheme Discovery & Search (DISC-01, DISC-02, DISC-03)
        res_search = await a_client.get("/api/services?q=scholarship")
        assert res_search.status_code == 200
        schemes = res_search.json()
        assert len(schemes) >= 1
        target_scheme = next((s for s in schemes if "scholarship" in s["service_name"].lower()), schemes[0])
        service_id = target_scheme["id"]
        assert target_scheme["official_application_url"].startswith("http")

        # Step 2: AI Eligibility Evaluation (ELIG-01, ELIG-02, ELIG-04, ELIG-05)
        res_elig = await a_client.post(f"/api/services/{service_id}/evaluate")
        assert res_elig.status_code == 200
        elig_data = res_elig.json()
        assert elig_data["status"] == "Likely Eligible"
        assert elig_data["confidence_score"] >= 0.85
        assert len(elig_data["criteria"]) >= 1
        assert "disclaimer" in elig_data

        # Step 3: Citizen Profile & Document Vault (PROF-01, DOC-01)
        res_profile = await a_client.get("/api/profile")
        assert res_profile.status_code == 200
        profile = res_profile.json()
        assert profile["full_name"] != ""

        res_docs = await a_client.get("/api/documents")
        assert res_docs.status_code == 200

        # Step 4: Stateful Workflow Initiation (AGENT-01, AGENT-02, AGENT-06)
        sample_portal = (
            "data:text/html,<html><head><title>NSP Portal</title></head><body>"
            "<form id='applForm'>"
            "<label for='name'>Full Legal Name</label><input id='name' name='name' required/>"
            "<label for='income'>Annual Income</label><input id='income' name='income' type='number' required/>"
            "<label for='category'>Category</label><input id='category' name='category'/>"
            "<button type='submit'>Submit Application</button>"
            "</form></body></html>"
        )
        start_payload = {
            "service_id": service_id,
            "portal_url_override": sample_portal,
        }
        res_start = await a_client.post("/api/agent/workflow/start", json=start_payload)
        assert res_start.status_code == 200
        wf_data = res_start.json()
        thread_id = wf_data["thread_id"]
        assert wf_data["current_step"] == "waiting_approval"

        # Step 5: Pre-Submission Review & Statutory Consent Gate (HIL-01, HIL-02)
        res_summary = await a_client.get(f"/api/agent/workflow/{thread_id}/summary")
        assert res_summary.status_code == 200
        summary = res_summary.json()
        assert summary["service_id"] == service_id
        assert len(summary["populated_fields"]) >= 1
        assert "Statutory Advisory" in summary["disclaimer"]

        # Step 6: Explicit Citizen Approval Gate (HIL-03)
        res_approve = await a_client.post(f"/api/agent/workflow/{thread_id}/approve")
        assert res_approve.status_code == 200
        approve_data = res_approve.json()
        assert approve_data["decision"] == "approved"
        assert approve_data["current_step"] in ["submitted", "submission_ready"]

        # Step 7: Submission Verification & Reference Extraction (APP-01, APP-02)
        session_id = wf_data["session_id"]
        app_id = f"app-{session_id[:8]}"

        # Step 8: PDF Receipt Retrieval & Streaming (APP-05)
        res_receipt = await a_client.get(f"/api/applications/{app_id}/receipt")
        assert res_receipt.status_code == 200
        assert res_receipt.headers["content-type"] == "application/pdf"
        assert "attachment" in res_receipt.headers.get("content-disposition", "")
        pdf_bytes = res_receipt.content
        assert pdf_bytes.startswith(b"%PDF-")
        assert len(pdf_bytes) > 1000

        # Step 9: My Applications Dashboard Tracking Sync (APP-03, APP-04)
        res_apps = await a_client.get("/api/applications")
        assert res_apps.status_code == 200
        apps_list = res_apps.json()
        assert len(apps_list) >= 1
        matched_app = next((a for a in apps_list if a["id"] == app_id), None)
        assert matched_app is not None
        assert matched_app["status"] == "submitted"
        assert matched_app["acknowledgement_number"] is not None
        assert matched_app["portal_url"] != ""


@pytest.mark.asyncio
async def test_e2e_ineligible_citizen_handling():
    """Verify high income citizen is flagged 'Likely Ineligible' with official citations (ELIG-02, ELIG-03)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as a_client:
        # PM-USP ceiling is ₹4,50,000; citizen earns ₹8,50,000
        payload = {
            "citizen_profile": {
                "full_name": "Rohan Verma",
                "annual_income": 850000.0,
                "education_level": "Undergraduate",
                "occupation": "Student",
                "state": "Maharashtra",
            }
        }
        res = await a_client.post("/api/services/pm-usp-scholarship/evaluate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "Likely Ineligible"
        assert data["confidence_score"] >= 0.85

        # Check official guideline citations
        income_crits = [c for c in data["criteria"] if "Income" in c["criterion_name"]]
        assert len(income_crits) > 0
        income_crit = income_crits[0]
        assert income_crit["status"] == "Not Satisfied"
        assert "850,000" in income_crit["citizen_value"]
        assert "exceeds" in income_crit["reasoning"].lower()
        assert "disclaimer" in data


@pytest.mark.asyncio
async def test_e2e_missing_information_alert():
    """Verify missing critical profile attributes triggers 'More Information Required' alert (ELIG-04)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as a_client:
        payload = {
            "citizen_profile": {
                "full_name": "Priya Nair",
                "state": "Karnataka",
            }
        }
        res = await a_client.post("/api/services/pm-usp-scholarship/evaluate", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "More Information Required"
        assert len(data["missing_fields"]) > 0


@pytest.mark.asyncio
async def test_e2e_security_checkpoint_flow():
    """Verify security challenge (CAPTCHA/OTP) interception, pausing, and resumption (HIL-04)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as a_client:
        captcha_portal = (
            "data:text/html,<html><body><form>"
            "<label for='name'>Full Name</label><input id='name' name='name'/>"
            "<label for='captcha'>Enter Security CAPTCHA</label><input id='captcha' name='captcha'/>"
            "<button type='submit'>Submit</button>"
            "</form></body></html>"
        )
        res_start = await a_client.post(
            "/api/agent/workflow/start",
            json={"service_id": "pm-usp-scholarship", "portal_url_override": captcha_portal},
        )
        assert res_start.status_code == 200
        thread_id = res_start.json()["thread_id"]

        # Intercepted: paused at waiting_security_challenge
        res_state = await a_client.get(f"/api/agent/workflow/{thread_id}/state")
        assert res_state.status_code == 200
        assert res_state.json()["current_step"] == "waiting_security_challenge"

        # Resolve challenge
        res_resolve = await a_client.post(
            f"/api/agent/workflow/{thread_id}/resolve-challenge",
            json={"challenge_type": "captcha"},
        )
        assert res_resolve.status_code == 200
        assert res_resolve.json()["challenge_resolved"] is True

        # Check resumed state
        res_state_after = await a_client.get(f"/api/agent/workflow/{thread_id}/state")
        assert res_state_after.status_code == 200
        assert res_state_after.json()["current_step"] == "waiting_approval"


@pytest.mark.asyncio
async def test_e2e_citizen_rejection_at_gate():
    """Verify citizen rejecting pre-submission audit halts workflow cleanly (HIL-03)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as a_client:
        res_start = await a_client.post(
            "/api/agent/workflow/start",
            json={
                "service_id": "pm-usp-scholarship",
                "portal_url_override": "data:text/html,<html><body><form><input id='name'/></form></body></html>",
            },
        )
        thread_id = res_start.json()["thread_id"]

        # Citizen rejects review
        reject_payload = {"decision": "rejected", "rejection_reason": "Applicant address needs updating"}
        res_reject = await a_client.post(f"/api/agent/workflow/{thread_id}/reject", json=reject_payload)
        assert res_reject.status_code == 200
        data_rej = res_reject.json()
        assert data_rej["decision"] == "rejected"
        assert data_rej["current_step"] == "submission_rejected"


def test_e2e_bounded_recovery_escalation():
    """Verify LangGraph cyclical recovery terminates after 3 failures without infinite loops (AGENT-06)."""
    state_retry: AgentWorkflowState = {
        "error_count": 2,
        "max_retries": 3,
        "execution_result": {"failed_actions": 1},
    }
    assert route_after_validation(state_retry) == "recovery"
    assert route_after_recovery(state_retry) == "inspect"

    state_exhausted: AgentWorkflowState = {
        "error_count": 3,
        "max_retries": 3,
        "execution_result": {"failed_actions": 1},
    }
    assert route_after_validation(state_exhausted) == "human_assistance"
    assert route_after_recovery(state_exhausted) == "human_assistance"


def test_e2e_receipt_pdf_integrity():
    """Verify generated PDF contains authentic government typography, structure, and SHA-256 seal (APP-02)."""
    record = ApplicationRecord(
        id="app-e2e-audit-01",
        service_id="nsp-post-matric-sc",
        service_name="Post-Matric Scholarship for SC Students",
        department="Ministry of Social Justice and Empowerment",
        category="Education",
        portal_url="https://scholarships.gov.in",
        status="submitted",
        acknowledgement_number="NSP2026/APPL/992817",
        submission_timestamp=datetime(2026, 11, 1, 15, 30, tzinfo=timezone.utc),
        populated_data={
            "full_name": "Arjun Sharma",
            "date_of_birth": "15/08/1998",
            "gender": "Male",
            "domicile_state": "Maharashtra",
            "annual_income": "180000",
            "social_category": "SC",
        },
        attached_documents=["Aadhaar Identity Card", "Income Certificate"],
    )

    pdf_bytes = ReceiptGenerator.generate_receipt_pdf(record)
    assert pdf_bytes.startswith(b"%PDF-")

    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    assert doc.page_count == 1
    page = doc[0]
    text = page.get_text()

    assert "GOVERNMENT OF INDIA" in text
    assert "OFFICIAL APPLICATION SUBMISSION ACKNOWLEDGEMENT" in text
    assert "NSP2026/APPL/992817" in text
    assert "STATUS: SUBMITTED (VERIFIED)" in text
    assert "Arjun Sharma" in text
    assert "SHA-256 Digital Verification Hash" in text
    assert "Information Technology Act, 2000" in text
    doc.close()


def test_e2e_applications_dashboard_sync():
    """Verify application store supports listing, status filtering, and completeness (APP-03, APP-04)."""
    res_all = client.get("/api/applications")
    assert res_all.status_code == 200
    all_apps = res_all.json()
    assert len(all_apps) >= 2

    res_sub = client.get("/api/applications?status=submitted")
    assert res_sub.status_code == 200
    for item in res_sub.json():
        assert item["status"] == "submitted"
        assert item["acknowledgement_number"] is not None
        assert len(item["portal_url"]) > 0

    res_wait = client.get("/api/applications?status=waiting_approval")
    assert res_wait.status_code == 200
    for item in res_wait.json():
        assert item["status"] == "waiting_approval"
