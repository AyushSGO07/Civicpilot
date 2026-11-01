---
phase: "06"
name: "playwright-browser-automation-core-dom-inspection"
created: 2026-11-01
---

# Phase 06: Playwright Browser Automation Core & DOM Inspection — Context

## User Constraints

### Locked Decisions
- **D-01 (Asynchronous Playwright Runtime):** Build an asynchronous Chromium browser engine using `playwright.async_api`. Must support isolated browser contexts per execution session with desktop viewport (`1280x800`), standard browser user agent, and auto-waiting timeouts (AGENT-01).
- **D-02 (Sanitized Semantic DOM Extraction):** Government portals contain extensive scripts, banners, nested divs, and styling. The inspection engine must extract a sanitized semantic DOM tree containing only actionable elements (`<form>`, `<input>`, `<select>`, `<button>`, `<textarea>`, `<label>`) with their attributes (`id`, `name`, `type`, `placeholder`, `aria-label`, `label_text`, `options`) and Playwright-compatible locators (AGENT-02).
- **D-03 (Guaranteed Zombie Cleanup):** Browser lifecycle must prevent zombie/orphaned Chromium processes. Implement async context managers, explicit session termination, and an active context registry that closes all browser instances on completion, error, or session abort (AGENT-07).
- **D-04 (FastAPI Browser Session Endpoints):** Provide modular backend endpoints (`POST /api/agent/browser/session/start`, `POST /api/agent/browser/session/navigate`, `POST /api/agent/browser/session/close`) to control and inspect browser sessions asynchronously.
- **D-05 (Integrity & Real Portals):** Support navigation to genuine government portal URLs (e.g. `scholarships.gov.in`, `pmkisan.gov.in`) with robust timeout handling and local test server/HTML validation for unit tests.

### Discretion Areas
- HTML pruning strategy: BeautifulSoup vs Playwright page evaluations (hybrid approach: evaluate interactive element positions and attributes directly via page JS and BeautifulSoup semantic normalization).
- Screenshot capture format: Base64 JPEG/PNG for live streaming buffer.

### Deferred Ideas
- Dynamic LLM field-to-input mapping (Phase 7 - AGENT-03, AGENT-04).
- LangGraph cyclical state machine orchestration (Phase 8).
- Live WebSocket streaming of browser frames to frontend canvas (Phase 9).
