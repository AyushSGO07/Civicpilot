---
phase: "07"
name: "dynamic-field-mapping-form-filling-engine"
created: 2026-11-01
---

# Phase 07: Dynamic Field Mapping & Form Filling Engine — Context

## User Constraints

### Locked Decisions
- **D-01 (Dynamic LLM Mapping without Hardcoded Selectors):** Gemini 2.5 Flash maps citizen profile fields and Document Vault files to portal input elements dynamically using the sanitized semantic DOM tree from Phase 6. No hardcoded portal CSS selectors or static element maps (AGENT-03).
- **D-02 (Robust Option Matching for Dropdowns & Radios):** Government portal `<select>` dropdowns and radio buttons use diverse encodings (state codes, ID numbers, capitalized names). The mapper must inspect available `<option>` labels and values in `DOMElementNode.options` and select the exact matching option value (AGENT-04).
- **D-03 (Secure Document Vault File Attachment):** When a file upload input is detected (`input[type="file"]`), the engine resolves matching verified documents from the citizen's vault (e.g. Aadhaar Card, Income Certificate, Marksheet) and attaches authentic local file bytes via `page.set_input_files()` (AGENT-05).
- **D-04 (Safe Sequential Execution & Audit Trail):** Form population executes actions sequentially with step-by-step audit logging (action type, target locator, value, success/failure status, duration, error message) and post-action screenshot verification (AGENT-04).
- **D-05 (Offline & CI Deterministic Fallback):** When `GEMINI_API_KEY` is not present, a deterministic semantic matcher maps profile attributes to elements using keyword/synonym rules, ensuring 100% offline test suite resilience.
- **D-06 (FastAPI Form Automation Endpoints):** Expose modular endpoints:
  - `POST /api/agent/form/plan`: Generates a structured `FormFillPlan` from the session's active DOM.
  - `POST /api/agent/form/execute`: Executes a fill plan on the active browser page.
  - `POST /api/agent/form/fill`: Combined one-shot inspect -> plan -> execute endpoint.

### Discretion Areas
- Action execution delay (e.g., 50-100ms realistic typing delay to prevent anti-bot throttle on public service portals).
- Error recovery on single field failure (continue remaining fields and report individual field error in audit log).

### Deferred Ideas
- Multi-step LangGraph cyclical state machine with checkpoints (Phase 8).
- Live WebSocket screenshot frame streaming to 3-panel UI (Phase 9).
- Pre-submission approval pause and human-in-the-loop CAPTCHA gate (Phase 10).
