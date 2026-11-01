"""Tests for Submission Verification, Acknowledgement Parsing, and Receipt Download Pipeline (APP-01, APP-02, APP-03, APP-04, APP-05)."""

import os
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models.agent import DOMElementNode
from app.models.application import ApplicationRecord, CreateApplicationRequest
from app.services.submission_verifier import SubmissionVerifier, ReceiptGenerator
from app.services.workflow_engine import submit_node
from app.routers.applications import _APPLICATIONS_STORE

client = TestClient(app)


def test_extract_acknowledgement_number_from_text():
    """Verify regex extraction of genuine government reference numbers (APP-01)."""
    # NSP Pattern
    text1 = "Congratulations! Your Application No: NSP2026/APPL/894125 has been successfully received."
    ref1 = SubmissionVerifier.extract_acknowledgement_number(text1)
    assert ref1 == "NSP2026/APPL/894125"

    # PM-Kisan Pattern with punctuation
    text2 = "Thank you. Acknowledgement Number: PMK-MH-948123. Please save this for records."
    ref2 = SubmissionVerifier.extract_acknowledgement_number(text2)
    assert ref2 == "PMK-MH-948123"

    # Ayushman Bharat Pattern
    text3 = "Reference ID: AB-PMJAY-2026-441290 has been allotted to beneficiary."
    ref3 = SubmissionVerifier.extract_acknowledgement_number(text3)
    assert ref3 == "AB-PMJAY-2026-441290"

    # Non-matching text
    text4 = "Please log in using your password and OTP."
    assert SubmissionVerifier.extract_acknowledgement_number(text4) is None


def test_extract_acknowledgement_number_from_dom():
    """Verify DOM node inspection extracts reference numbers (APP-01)."""
    node = DOMElementNode(
        element_id="ack-badge",
        tag="span",
        name="reference_id",
        label="Registration Token: DL-2026-88129",
        suggested_locator="#ack-badge",
    )
    extracted = SubmissionVerifier.extract_acknowledgement_number("", [node])
    assert extracted == "DL-2026-88129"


def test_verify_submission_confirmation():
    """Verify official submission confirmation phrase detection (APP-01)."""
    success_text = "Your application has been submitted successfully to the portal."
    assert SubmissionVerifier.verify_confirmation(success_text) is True

    pending_text = "Please complete section 3 before clicking submit."
    assert SubmissionVerifier.verify_confirmation(pending_text) is False


@pytest.mark.asyncio
async def test_verify_submission_pipeline():
    """Verify comprehensive submission verification output (APP-01)."""
    page_text = "Registration completed successfully. Application Reference No: NSP-2026-MH-44912."
    result = await SubmissionVerifier.verify_submission(
        page=None,
        session_id="test-session-123",
        service_id="nsp-post-matric-sc",
        page_text=page_text,
    )
    assert result.is_success is True
    assert result.acknowledgement_number == "NSP-2026-MH-44912"
    assert "submitted successfully" in result.confirmation_text.lower()
    assert result.receipt_filename is not None


def test_generate_and_save_receipt_pdf(tmp_path):
    """Verify authentic vector PDF receipt generation and storage (APP-02)."""
    app_record = ApplicationRecord(
        id="test-app-001",
        service_id="nsp-post-matric-sc",
        service_name="Post-Matric Scholarship for SC Students",
        department="Ministry of Social Justice and Empowerment",
        category="Education",
        portal_url="https://scholarships.gov.in",
        status="submitted",
        acknowledgement_number="NSP2026/APPL/894125",
        submission_timestamp=datetime(2026, 11, 1, 12, 0, tzinfo=timezone.utc),
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

    pdf_bytes = ReceiptGenerator.generate_receipt_pdf(app_record)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")
    assert len(pdf_bytes) > 1000

    saved_path = ReceiptGenerator.save_receipt_file(
        application_id=app_record.id,
        receipt_bytes=pdf_bytes,
        output_dir=str(tmp_path),
    )
    assert os.path.exists(saved_path)
    assert os.path.getsize(saved_path) == len(pdf_bytes)


def test_api_list_and_filter_applications():
    """Verify GET /api/applications lists citizen applications with filtering (APP-03, APP-04)."""
    response = client.get("/api/applications")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    # Check required fields (APP-04)
    item = data[0]
    assert "id" in item
    assert "service_name" in item
    assert "status" in item
    assert "portal_url" in item

    # Filter by submitted
    res_submitted = client.get("/api/applications?status=submitted")
    assert res_submitted.status_code == 200
    submitted_items = res_submitted.json()
    for s in submitted_items:
        assert s["status"] == "submitted"


def test_api_create_and_get_application():
    """Verify POST and GET /api/applications/{id} endpoints (APP-03)."""
    payload = {
        "service_id": "test-scheme-xyz",
        "service_name": "Test Welfare Scheme",
        "department": "Department of Public Welfare",
        "category": "Social Welfare",
        "portal_url": "https://service.gov.in",
        "status": "draft",
        "populated_data": {"full_name": "Test Citizen"},
    }
    create_res = client.post("/api/applications", json=payload)
    assert create_res.status_code == 200
    created = create_res.json()
    app_id = created["id"]
    assert created["service_name"] == "Test Welfare Scheme"

    get_res = client.get(f"/api/applications/{app_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == app_id


def test_api_download_application_receipt():
    """Verify GET /api/applications/{id}/receipt streams official PDF (APP-05)."""
    response = client.get("/api/applications/app-demo-nsp-01/receipt")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers.get("content-disposition", "")
    assert response.content.startswith(b"%PDF-")


@pytest.mark.asyncio
async def test_workflow_submit_node_integration():
    """Verify submit_node verifies submission, captures ref number, and creates receipt (APP-01, APP-02)."""
    state = {
        "session_id": "sess-test-submit-01",
        "service_id": "nsp-post-matric-sc",
        "portal_url": "https://scholarships.gov.in",
        "citizen_profile": {
            "full_name": "Arjun Sharma",
            "date_of_birth": "15/08/1998",
            "gender": "Male",
            "domicile_state": "Maharashtra",
            "annual_income": "180000",
            "social_category": "SC",
        },
        "vault_documents": [{"document_name": "Income Certificate 2025"}],
        "approval_decision": "approved",
    }

    updated_state = await submit_node(state)
    assert updated_state["current_step"] == "submitted"
    assert updated_state.get("acknowledgement_number") is not None
    assert updated_state.get("receipt_path") is not None
    assert os.path.exists(updated_state["receipt_path"])

    # Check store was updated
    app_id = updated_state["application_id"]
    record = _APPLICATIONS_STORE.get(app_id)
    assert record is not None
    assert record.status == "submitted"
    assert record.acknowledgement_number == updated_state["acknowledgement_number"]
