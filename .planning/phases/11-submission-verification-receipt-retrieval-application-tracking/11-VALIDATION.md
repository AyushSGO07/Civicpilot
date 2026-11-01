# Phase 11: Submission Verification, Receipt Retrieval & Application Tracking — Validation Plan

## Test Strategy

Phase 11 introduces authentic portal submission verification, acknowledgement reference extraction (`APP-01`), receipt PDF generation and storage (`APP-02`), and the MakeMyTrip "My Applications" dashboard with tracking and download (`APP-03`, `APP-04`, `APP-05`).

Validation consists of:
1. Automated backend pytest suite (`backend/tests/test_submission_and_applications.py`) validating:
   - Regex extraction of genuine reference numbers from government portal text and DOM elements (`APP-01`).
   - Submission confirmation verification (`APP-01`).
   - PDF receipt synthesis and storage (`APP-02`).
   - Application record creation, retrieval, and filtering (`APP-03`, `APP-04`).
   - Official receipt download endpoint streaming valid PDF (`APP-05`).
2. Next.js App Router build verification (`npm --prefix frontend run build`) verifying clean static and dynamic compilation of `/applications` and updated workspace.
3. Full backend test regression verification (`pytest backend/tests/ -v`).

---

## Test Cases (`backend/tests/test_submission_and_applications.py`)

| Test Name | Test Condition | Expected Result |
|---|---|---|
| `test_extract_acknowledgement_number_from_text` | Text containing "Application No: NSP/2026/894125" | Extracts "NSP/2026/894125" cleanly without trailing punctuation (APP-01) |
| `test_extract_acknowledgement_number_from_dom` | DOM containing `<span id="refNo">PMK-MH-948123</span>` | Extracts "PMK-MH-948123" with 100% confidence (APP-01) |
| `test_verify_submission_success` | Page renders confirmation alert and reference number | Returns `is_success=True`, acknowledgement number, and confirmation text (APP-01) |
| `test_generate_and_store_receipt_pdf` | Call receipt generator with application metadata and citizen details | Generates valid PDF starting with `%PDF` header, saves to storage, returns path (APP-02) |
| `test_api_create_and_list_applications` | Create application and query `GET /api/applications` | Returns 200 OK list including application status, timestamps, and portal URLs (APP-03, APP-04) |
| `test_api_download_application_receipt` | Call `GET /api/applications/{id}/receipt` on submitted application | Returns 200 OK with `application/pdf` Content-Type and attachment filename (APP-05) |
| `test_workflow_submission_integration` | Run workflow from `waiting_approval` with `decision="approved"` | Node executes submission, parses reference number, stores receipt, updates status to `submitted` (APP-01, APP-02) |

---

## Acceptance Criteria Checklist

- [ ] All tests in `backend/tests/test_submission_and_applications.py` pass.
- [ ] Acknowledgement reference numbers are extracted accurately across varied government portal formats.
- [ ] Submission receipt PDF is generated and downloadable via API.
- [ ] "My Applications" dashboard renders at `/applications` with status badges, timestamps, portal URLs, and download buttons.
- [ ] Frontend builds with 0 errors and 0 warnings (`npm --prefix frontend run build`).
- [ ] Full backend test regression passes (`pytest backend/tests/ -v`).
