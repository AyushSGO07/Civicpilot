"""Tests for dynamic field mapping and autonomous form filling (AGENT-03, AGENT-04, AGENT-05)."""

import pytest
import httpx
from datetime import date
from pathlib import Path

from app.main import app
from app.models.profile import CitizenProfileBase
from app.models.agent import DOMElementNode, SanitizedDOMTree
from app.models.form_filling import FormFillPlan, FieldAction
from app.services.browser_manager import browser_manager
from app.services.field_mapper import DynamicFieldMapper
from app.services.dom_inspector import DOMInspector
from app.services.form_executor import FormActionExecutor


@pytest.fixture(autouse=True)
async def cleanup_browser():
    """Ensure clean browser state before and after each test."""
    yield
    await browser_manager.shutdown()


@pytest.mark.asyncio
async def test_dynamic_field_mapping_semantic_resolution():
    """Verify Gemini/heuristic mapper resolves profile fields to DOM elements without hardcoded selectors (AGENT-03)."""
    # Create sample DOM nodes
    elements = [
        DOMElementNode(
            tag="input",
            element_id="txtApplicantName",
            name="applicant_name",
            element_type="text",
            label="Full Name of the Applicant",
            suggested_locator="#txtApplicantName",
        ),
        DOMElementNode(
            tag="input",
            element_id="txtAnnualIncome",
            name="family_income",
            element_type="number",
            label="Gross Annual Family Income (INR)",
            suggested_locator="#txtAnnualIncome",
        ),
        DOMElementNode(
            tag="input",
            element_id="txtPin",
            name="postal_code",
            element_type="text",
            label="Permanent PIN Code",
            suggested_locator="#txtPin",
        ),
    ]

    dom_tree = SanitizedDOMTree(
        url="https://scholarships.gov.in/register",
        title="Scholarship Registration",
        forms_count=1,
        interactive_elements_count=3,
        elements=elements,
    )

    profile = CitizenProfileBase(
        full_name="Aarav Sharma",
        annual_income=250000.0,
        pincode="411001",
        state="Maharashtra",
    )

    plan = await DynamicFieldMapper.generate_fill_plan(dom_tree, profile)

    assert len(plan.actions) == 3

    # Check name action
    name_action = next((a for a in plan.actions if a.source_attribute == "full_name"), None)
    assert name_action is not None
    assert name_action.value == "Aarav Sharma"
    assert name_action.target_locator == "#txtApplicantName"

    # Check income action
    income_action = next((a for a in plan.actions if a.source_attribute == "annual_income"), None)
    assert income_action is not None
    assert income_action.value == "250000"

    # Check pin action
    pin_action = next((a for a in plan.actions if a.source_attribute == "pincode"), None)
    assert pin_action is not None
    assert pin_action.value == "411001"


@pytest.mark.asyncio
async def test_dynamic_field_mapping_select_dropdown():
    """Verify mapper matches select dropdown option values by label (AGENT-04)."""
    elements = [
        DOMElementNode(
            tag="select",
            element_id="ddlDomicileState",
            name="domicileState",
            element_type="select",
            label="State of Domicile",
            options=["-- Select --", "KA: Karnataka", "MH: Maharashtra", "TN: Tamil Nadu"],
            suggested_locator="#ddlDomicileState",
        ),
    ]

    dom_tree = SanitizedDOMTree(
        url="https://scholarships.gov.in/apply",
        title="Apply",
        forms_count=1,
        interactive_elements_count=1,
        elements=elements,
    )

    profile = CitizenProfileBase(
        full_name="Aarav Sharma",
        state="Maharashtra",
    )

    plan = await DynamicFieldMapper.generate_fill_plan(dom_tree, profile)
    assert len(plan.actions) == 1
    action = plan.actions[0]
    assert action.action_type == "select_option"
    assert action.value == "MH"
    assert action.target_locator == "#ddlDomicileState"


@pytest.mark.asyncio
async def test_dynamic_field_mapping_vault_document_attachment():
    """Verify file upload fields link to matching certificates in the Document Vault (AGENT-05)."""
    elements = [
        DOMElementNode(
            tag="input",
            element_id="fileAadhaar",
            name="aadhaar_upload",
            element_type="file",
            label="Upload Self-Attested Aadhaar Card (PDF/JPG)",
            suggested_locator="#fileAadhaar",
            is_required=True,
        ),
    ]

    dom_tree = SanitizedDOMTree(
        url="https://pmkisan.gov.in/upload",
        title="Document Upload",
        forms_count=1,
        interactive_elements_count=1,
        elements=elements,
    )

    profile = CitizenProfileBase(full_name="Aarav Sharma")
    vault_docs = [
        {
            "id": "doc-123",
            "document_type": "Aadhaar Card",
            "file_name": "aarav_aadhaar.pdf",
            "file_path": "storage/vault/aarav_aadhaar.pdf",
        }
    ]

    plan = await DynamicFieldMapper.generate_fill_plan(dom_tree, profile, vault_docs)
    assert len(plan.actions) == 1
    action = plan.actions[0]
    assert action.action_type == "upload_file"
    assert "aarav_aadhaar.pdf" in action.value
    assert action.target_locator == "#fileAadhaar"


@pytest.mark.asyncio
async def test_form_executor_populates_browser_elements():
    """Verify FormActionExecutor populates inputs, dropdowns, and checkboxes on a live Playwright page (AGENT-04)."""
    async with browser_manager.session() as (page, session_id):
        test_form_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Form Execution Test</title></head>
        <body>
            <form id="testForm">
                <input type="text" id="custName" name="custName" />
                <select id="custState" name="custState">
                    <option value="">Choose</option>
                    <option value="MH">Maharashtra</option>
                    <option value="DL">Delhi</option>
                </select>
                <input type="checkbox" id="consentCheck" name="consentCheck" />
            </form>
        </body>
        </html>
        """
        await page.set_content(test_form_html)

        plan = FormFillPlan(
            actions=[
                FieldAction(
                    action_type="fill_text",
                    target_locator="#custName",
                    value="Aarav Sharma",
                    reasoning="Populating customer name",
                ),
                FieldAction(
                    action_type="select_option",
                    target_locator="#custState",
                    value="MH",
                    reasoning="Selecting Maharashtra state",
                ),
                FieldAction(
                    action_type="check_box",
                    target_locator="#consentCheck",
                    value="true",
                    reasoning="Checking citizen declaration",
                ),
            ]
        )

        result = await FormActionExecutor.execute_plan(page, session_id, plan)

        assert result.session_id == session_id
        assert result.total_actions == 3
        assert result.successful_actions == 3
        assert result.failed_actions == 0
        assert result.screenshot_base64 is not None

        # Verify DOM elements on page actually received values!
        name_val = await page.input_value("#custName")
        assert name_val == "Aarav Sharma"

        state_val = await page.input_value("#custState")
        assert state_val == "MH"

        is_checked = await page.is_checked("#consentCheck")
        assert is_checked is True


@pytest.mark.asyncio
async def test_form_executor_attaches_file():
    """Verify FormActionExecutor attaches files to input[type='file'] elements (AGENT-05)."""
    async with browser_manager.session() as (page, session_id):
        test_file_html = """
        <!DOCTYPE html>
        <html>
        <head><title>File Upload Test</title></head>
        <body>
            <form id="uploadForm">
                <input type="file" id="certFile" name="certFile" />
            </form>
        </body>
        </html>
        """
        await page.set_content(test_file_html)

        # Prepare dummy test file
        test_dir = Path("storage/vault")
        test_dir.mkdir(parents=True, exist_ok=True)
        test_doc_path = test_dir / "test_certificate.pdf"
        test_doc_path.write_bytes(b"%PDF-1.4 Mock Government Certificate Document")

        plan = FormFillPlan(
            actions=[
                FieldAction(
                    action_type="upload_file",
                    target_locator="#certFile",
                    value=str(test_doc_path),
                    reasoning="Attaching certificate document",
                ),
            ]
        )

        result = await FormActionExecutor.execute_plan(page, session_id, plan)
        assert result.successful_actions == 1
        assert result.failed_actions == 0

        # Verify input has files attached
        files_count = await page.evaluate("() => document.getElementById('certFile').files.length")
        assert files_count == 1


@pytest.mark.asyncio
async def test_api_form_plan_and_execute_endpoints():
    """Verify FastAPI endpoints for plan generation and execution on active session (AGENT-03, AGENT-04)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Start browser session
        start_res = await client.post("/api/agent/browser/session/start")
        assert start_res.status_code == 200
        session_id = start_res.json()["session_id"]

        # 2. Navigate page to a sample form
        sample_url = (
            "data:text/html,<html><head><title>Scholarship Form</title></head><body>"
            "<form><label for='sName'>Student Name</label><input type='text' id='sName' name='sName'/>"
            "<label for='sPin'>PIN Code</label><input type='text' id='sPin' name='sPin'/></form></body></html>"
        )
        await client.post(
            f"/api/agent/browser/session/{session_id}/navigate",
            json={"url": sample_url},
        )

        # 3. Request Form Fill Plan (AGENT-03)
        plan_res = await client.post(
            f"/api/agent/browser/session/{session_id}/form/plan",
            json={
                "citizen_profile": {
                    "full_name": "Aarav Sharma",
                    "pincode": "411001",
                }
            },
        )
        assert plan_res.status_code == 200
        plan = plan_res.json()
        assert len(plan["actions"]) >= 2
        assert any(a["value"] == "Aarav Sharma" for a in plan["actions"])

        # 4. Execute Form Plan (AGENT-04)
        exec_res = await client.post(
            f"/api/agent/browser/session/{session_id}/form/execute",
            json=plan,
        )
        assert exec_res.status_code == 200
        result = exec_res.json()
        assert result["successful_actions"] >= 2
        assert result["screenshot_base64"] is not None

        # 5. Clean up
        await client.post(f"/api/agent/browser/session/{session_id}/close")


@pytest.mark.asyncio
async def test_api_form_fill_composite():
    """Verify convenience composite endpoint /form/fill completes inspect, plan, and execute in one request."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Start and navigate
        start_res = await client.post("/api/agent/browser/session/start")
        session_id = start_res.json()["session_id"]

        sample_url = (
            "data:text/html,<html><head><title>Composite Test</title></head><body>"
            "<form><label for='applicant'>Applicant Name</label><input type='text' id='applicant' name='applicant'/></form></body></html>"
        )
        await client.post(
            f"/api/agent/browser/session/{session_id}/navigate",
            json={"url": sample_url},
        )

        # Composite fill request
        fill_res = await client.post(
            f"/api/agent/browser/session/{session_id}/form/fill",
            json={
                "citizen_profile": {
                    "full_name": "Aarav Sharma",
                }
            },
        )
        assert fill_res.status_code == 200
        fill_data = fill_res.json()
        assert fill_data["successful_actions"] >= 1
        assert fill_data["screenshot_base64"] is not None

        # Clean up
        await client.post(f"/api/agent/browser/session/{session_id}/close")
