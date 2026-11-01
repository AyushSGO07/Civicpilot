# Phase 06: Playwright Browser Automation Core & DOM Inspection — Validation Plan

## Test Strategy

Phase 06 establishes the core browser automation runtime and semantic DOM inspection engine.

Validation consists of:
1. Automated pytest unit and integration tests (`backend/tests/test_agent_browser.py`).
2. Verification of clean Chromium process teardown (no dangling `chrome.exe` processes).
3. FastAPI endpoint integration for session lifecycle and DOM inspection.
4. Full regression testing (`pytest backend/tests/ -v`).

---

## Test Cases (`backend/tests/test_agent_browser.py`)

| Test Name | Test Condition | Expected Result |
|---|---|---|
| `test_browser_manager_lifecycle` | Initialize `BrowserSessionManager`, create session, verify active page | Browser instance starts, isolated context created with desktop viewport (1280x800) |
| `test_navigate_and_capture_screenshot` | Navigate page to HTML content and request Base64 screenshot | Navigation succeeds, valid Base64 JPEG/PNG buffer returned |
| `test_sanitized_dom_extraction` | Load HTML form with inputs, select dropdowns, radio buttons, file inputs, and submit button | `DOMInspector.inspect_page` returns `SanitizedDOMTree` with all interactive elements, matching labels, and suggested Playwright locators |
| `test_dom_extraction_prunes_noise` | Load HTML with heavy inline scripts, svg graphics, analytics tags, and styling | Non-interactive tags are pruned; only actionable form elements are in `elements` |
| `test_session_close_and_zombie_cleanup` | Close session via `close_session(session_id)` | Page and context close cleanly, session removed from registry, process count returns to baseline (AGENT-07) |
| `test_api_browser_session_endpoints` | Call `POST /api/agent/browser/session/start`, `/navigate`, and `/close` | HTTP 200 on all calls with session data, title, and termination confirmation |
| `test_api_invalid_session_404` | Call `/navigate` with invalid or already-closed `session_id` | HTTP 404 with meaningful error message |

---

## Acceptance Criteria Checklist

- [ ] All tests in `backend/tests/test_agent_browser.py` pass.
- [ ] Chromium process initializes and closes cleanly without leaving orphan processes.
- [ ] Pruned DOM tree accurately maps input names, labels, and roles.
- [ ] Full backend test suite passes without regressions.
