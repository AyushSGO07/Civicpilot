"""Tests for Playwright asynchronous browser manager, DOM inspection, and agent API (AGENT-01, AGENT-02, AGENT-07)."""

import pytest
import httpx
from app.main import app
from app.services.browser_manager import browser_manager
from app.services.dom_inspector import DOMInspector


@pytest.fixture(autouse=True)
async def cleanup_browser():
    """Ensure clean browser state before and after each test."""
    yield
    await browser_manager.shutdown()


@pytest.mark.asyncio
async def test_browser_manager_initialization():
    """Verify Playwright Chromium initializes and maintains active connection (AGENT-01)."""
    await browser_manager.initialize()
    assert browser_manager._initialized is True
    assert browser_manager._browser is not None
    assert browser_manager._browser.is_connected() is True


@pytest.mark.asyncio
async def test_create_and_close_session():
    """Verify session creation with isolated context and clean termination (AGENT-01, AGENT-07)."""
    session_id = await browser_manager.create_session()
    assert session_id is not None

    page = await browser_manager.get_page(session_id)
    assert page is not None
    assert not page.is_closed()

    # Verify desktop viewport settings (1280x800)
    viewport = page.viewport_size
    assert viewport is not None
    assert viewport["width"] == 1280
    assert viewport["height"] == 800

    # Verify session info
    info = await browser_manager.get_session_info(session_id)
    assert info is not None
    assert info.session_id == session_id
    assert info.status == "idle"

    # Close session cleanly (AGENT-07)
    closed = await browser_manager.close_session(session_id)
    assert closed is True

    # Verify session is purged and page is closed
    assert await browser_manager.get_page(session_id) is None
    assert page.is_closed()


@pytest.mark.asyncio
async def test_navigate_and_capture_screenshot():
    """Verify navigating page and capturing Base64 screenshot buffer (AGENT-01)."""
    async with browser_manager.session() as (page, session_id):
        test_html = """
        <!DOCTYPE html>
        <html>
        <head><title>National Scholarship Portal - Login</title></head>
        <body style="background: #1A2B4C; color: white; padding: 20px;">
            <h1>National Scholarship Portal</h1>
            <p>Citizen Application Login</p>
        </body>
        </html>
        """
        await page.set_content(test_html)
        title = await page.title()
        assert "National Scholarship Portal" in title

        screenshot_b64 = await browser_manager.capture_screenshot_base64(session_id)
        assert screenshot_b64 is not None
        assert len(screenshot_b64) > 100


@pytest.mark.asyncio
async def test_dom_inspector_extracts_interactive_elements():
    """Verify DOMInspector extracts forms, inputs, selects, labels, and generates locators (AGENT-02)."""
    async with browser_manager.session() as (page, _):
        sample_portal_html = """
        <!DOCTYPE html>
        <html>
        <head><title>PM-KISAN Registration Portal</title></head>
        <body>
            <header><nav>Home | Guidelines | Help</nav></header>
            <form id="registrationForm" action="/submit" method="post">
                <div class="field-group">
                    <label for="farmerName">Full Name of Farmer</label>
                    <input type="text" id="farmerName" name="fullName" required placeholder="Enter full name" />
                </div>
                <div class="field-group">
                    <label for="aadhaarNum">Aadhaar Number</label>
                    <input type="text" id="aadhaarNum" name="aadhaarNumber" required maxlength="12" />
                </div>
                <div class="field-group">
                    <label for="stateSelect">State of Residence</label>
                    <select id="stateSelect" name="state" required>
                        <option value="">-- Choose State --</option>
                        <option value="MH">Maharashtra</option>
                        <option value="UP">Uttar Pradesh</option>
                    </select>
                </div>
                <div class="field-group">
                    <label>
                        <input type="checkbox" id="landholderConsent" name="consent" required />
                        I hereby declare I am a cultivable landholding farmer
                    </label>
                </div>
                <div class="field-group">
                    <label for="landRecord">Upload Land Document (Khatauni)</label>
                    <input type="file" id="landRecord" name="landDocument" accept=".pdf,.jpg" />
                </div>
                <button type="submit" id="btnSubmit">Submit Registration</button>
            </form>
        </body>
        </html>
        """
        await page.set_content(sample_portal_html)

        tree = await DOMInspector.inspect_page(page)

        assert tree.title == "PM-KISAN Registration Portal"
        assert tree.forms_count == 1
        assert tree.interactive_elements_count >= 5

        # Inspect extracted input elements
        name_node = next((el for el in tree.elements if el.name == "fullName"), None)
        assert name_node is not None
        assert name_node.label == "Full Name of Farmer"
        assert name_node.element_id == "farmerName"
        assert name_node.is_required is True
        assert name_node.suggested_locator == "#farmerName"

        # Inspect select element and options
        state_node = next((el for el in tree.elements if el.name == "state"), None)
        assert state_node is not None
        assert state_node.tag == "select"
        assert state_node.label == "State of Residence"
        assert len(state_node.options) >= 2
        assert any("Maharashtra" in opt for opt in state_node.options)

        # Inspect submit button
        submit_node = next((el for el in tree.elements if el.tag == "button"), None)
        assert submit_node is not None
        assert submit_node.label == "Submit Registration"
        assert submit_node.suggested_locator == "#btnSubmit"


@pytest.mark.asyncio
async def test_dom_inspector_prunes_noise():
    """Verify DOMInspector decomposes scripts, styles, SVGs, and hidden display:none elements (AGENT-02)."""
    async with browser_manager.session() as (page, _):
        noisy_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Portal with Bloat</title>
            <style>body { font-size: 16px; } .hidden { display: none; }</style>
            <script>console.log('tracker initialized');</script>
        </head>
        <body>
            <svg width="24" height="24"><circle cx="12" cy="12" r="10" /></svg>
            <form id="cleanForm">
                <label for="mobile">Mobile Number</label>
                <input type="tel" id="mobile" name="mobileNumber" />
                <input type="hidden" name="csrf_token" value="abc123xyz" />
                <input type="text" id="hiddenField" style="display:none;" />
                <button type="submit">Verify OTP</button>
            </form>
            <script src="https://cdn.example.gov.in/analytics.js"></script>
        </body>
        </html>
        """
        await page.set_content(noisy_html)

        tree = await DOMInspector.inspect_page(page)

        # Only mobile input and submit button should be in sanitized elements (hidden inputs and display:none pruned)
        element_names = [el.name for el in tree.elements if el.name]
        assert "mobileNumber" in element_names
        assert "csrf_token" not in element_names
        assert not any(el.element_id == "hiddenField" for el in tree.elements)
        assert tree.interactive_elements_count == 2


@pytest.mark.asyncio
async def test_api_browser_session_endpoints():
    """Verify FastAPI endpoints for session start, navigation, inspection, and termination (AGENT-01, AGENT-02, AGENT-07)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Start browser session
        start_res = await client.post("/api/agent/browser/session/start")
        assert start_res.status_code == 200
        start_data = start_res.json()
        session_id = start_data["session_id"]
        assert session_id is not None
        assert start_data["status"] == "idle"

        # 2. Get session info
        info_res = await client.get(f"/api/agent/browser/session/{session_id}")
        assert info_res.status_code == 200
        assert info_res.json()["session_id"] == session_id

        # 3. Navigate page using data URL
        data_url = "data:text/html,<html><head><title>Sarathi Parivahan</title></head><body><h1>Driving Licence Portal</h1><form><label for='licence'>Licence No</label><input type='text' id='licence' name='dl_number'/><button type='submit'>Check Status</button></form></body></html>"
        nav_res = await client.post(
            f"/api/agent/browser/session/{session_id}/navigate",
            json={"url": data_url, "wait_until": "domcontentloaded"},
        )
        assert nav_res.status_code == 200
        nav_data = nav_res.json()
        assert nav_data["page_title"] == "Sarathi Parivahan"
        assert nav_data["screenshot_base64"] is not None

        # 4. Inspect DOM
        inspect_res = await client.get(f"/api/agent/browser/session/{session_id}/inspect")
        assert inspect_res.status_code == 200
        dom_data = inspect_res.json()
        assert dom_data["title"] == "Sarathi Parivahan"
        assert dom_data["interactive_elements_count"] >= 2
        assert any(el["name"] == "dl_number" for el in dom_data["elements"])

        # 5. Capture screenshot
        shot_res = await client.get(f"/api/agent/browser/session/{session_id}/screenshot")
        assert shot_res.status_code == 200
        assert shot_res.json()["screenshot_base64"] is not None

        # 6. Close session cleanly (AGENT-07)
        close_res = await client.post(f"/api/agent/browser/session/{session_id}/close")
        assert close_res.status_code == 200
        assert close_res.json()["status"] == "closed"

        # 7. Verify subsequent calls to closed session return 404
        inspect_closed = await client.get(f"/api/agent/browser/session/{session_id}/inspect")
        assert inspect_closed.status_code == 404


@pytest.mark.asyncio
async def test_api_invalid_session_404():
    """Verify calling agent endpoints with invalid session ID returns 404."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/agent/browser/session/non-existent-session-12345/inspect")
        assert res.status_code == 404
