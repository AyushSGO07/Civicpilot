# Phase 07: Dynamic Field Mapping & Form Filling Engine — Validation Plan

## Test Strategy

Phase 07 introduces dynamic Gemini-driven field mapping and autonomous Playwright form execution.

Validation consists of:
1. Automated unit tests for `DynamicFieldMapper` (field resolution, select option matching, and file attachment linking).
2. Integration tests for `FormActionExecutor` validating that Playwright actually populates DOM elements (text inputs, selects, radios, checkboxes, and file attachments).
3. FastAPI endpoint tests (`/api/agent/form/...`).
4. Full regression testing (`pytest backend/tests/ -v`).

---

## Test Cases (`backend/tests/test_agent_form_filling.py`)

| Test Name | Test Condition | Expected Result |
|---|---|---|
| `test_dynamic_field_mapping_semantic_resolution` | Pass sanitized DOM tree containing applicant name, annual income, pincode, and citizen profile | `FormFillPlan` generates `fill_text` actions with source attributes mapped correctly (AGENT-03) |
| `test_dynamic_field_mapping_select_dropdown` | Pass `<select>` node with multiple state options and citizen profile with state="Maharashtra" | Action has `action_type="select_option"` matching Maharashtra value/label (AGENT-04) |
| `test_dynamic_field_mapping_document_attachment` | Pass `input[type="file"]` with label "Upload Aadhaar Card" and vault document list | Action has `action_type="upload_file"` linking the Aadhaar file (AGENT-05) |
| `test_form_executor_populates_browser_elements` | Load HTML form with text inputs, select dropdowns, and checkboxes into Playwright page; execute plan | Page inputs have matching `.input_value()`, select has matching value, checkbox is `.is_checked()` (AGENT-04) |
| `test_form_executor_attaches_file` | Load HTML form with file upload input; execute plan with sample document | Input has `.input_files()` populated with the test file (AGENT-05) |
| `test_api_form_plan_and_execute_lifecycle` | Call `POST /api/agent/form/plan` then `POST /api/agent/form/execute` on active browser session | HTTP 200, plan generated, actions executed with audit log and post-fill screenshot |
| `test_api_form_fill_composite` | Call `POST /api/agent/form/fill` on active browser session | HTTP 200, one-shot inspect -> plan -> fill execution succeeds with post-fill screenshot buffer |

---

## Acceptance Criteria Checklist

- [ ] All tests in `backend/tests/test_agent_form_filling.py` pass.
- [ ] Playwright autonomously populates inputs, dropdowns, checkboxes, and files on the browser page.
- [ ] Audit trail logs duration and status for every executed action.
- [ ] Full backend test suite passes without regressions.
