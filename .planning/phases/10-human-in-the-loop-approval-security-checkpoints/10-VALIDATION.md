# Phase 10: Human-in-the-Loop Approval & Security Checkpoints — Validation Plan

## Test Strategy

Phase 10 introduces the mandatory Pre-Submission Review gate (HIL-01, HIL-02, HIL-03) and automated Security Challenge Detection for CAPTCHA/OTP/MFA (HIL-04).

Validation consists of:
1. Automated backend pytest tests (`backend/tests/test_agent_approval.py`) validating pre-submission summary compilation, approval pause gate, approval submission trigger, and rejection flow.
2. Automated backend pytest tests (`backend/tests/test_agent_security_challenge.py`) validating semantic detection of CAPTCHA and OTP challenges, pause transition, and resumption upon user resolution.
3. Frontend Next.js production build (`npm --prefix frontend run build`) verifying clean static and dynamic compilation of the workspace with review modal and challenge overlays.
4. Full backend regression test pass (`pytest backend/tests/ -v`).

---

## Test Cases

### Approval Suite (`backend/tests/test_agent_approval.py`)

| Test Name | Test Condition | Expected Result |
|---|---|---|
| `test_presubmission_summary_compilation` | Workflow reaches validation node with populated fields and attached vault documents | Generates structured `PreSubmissionSummary` matching filled elements and vault docs (HIL-02) |
| `test_workflow_pauses_at_waiting_approval` | Graph execution completes form filling | Workflow stops at `waiting_approval` checkpoint, does NOT execute submission (HIL-01) |
| `test_workflow_approve_resumes_submission` | User calls `approve` endpoint on thread in `waiting_approval` | State updates `approval_decision = "approved"`, transitions toward submission (HIL-03) |
| `test_workflow_reject_halts_submission` | User calls `reject` endpoint on thread in `waiting_approval` | State updates `approval_decision = "rejected"`, prevents submission, records rejection reason (HIL-03) |
| `test_workflow_summary_api_endpoint` | Query `GET /api/agent/workflow/{thread_id}/summary` | Returns serialized `PreSubmissionSummary` payload with 200 OK |

### Security Challenge Suite (`backend/tests/test_agent_security_challenge.py`)

| Test Name | Test Condition | Expected Result |
|---|---|---|
| `test_security_detector_identifies_captcha` | Page contains `<input id="txtCaptcha">` or `<img id="imgCaptcha">` | `detect_challenge()` returns `detected=True`, `challenge_type="captcha"` (HIL-04) |
| `test_security_detector_identifies_otp` | Page contains `<input id="txtOtp">` or "Enter 6-digit OTP" text | `detect_challenge()` returns `detected=True`, `challenge_type="otp"` (HIL-04) |
| `test_security_detector_negative_normal_form` | Page contains standard name/email/state inputs without challenge | `detect_challenge()` returns `detected=False` |
| `test_workflow_pauses_on_security_challenge` | Injected CAPTCHA detected during inspection/filling | Workflow routes to `waiting_security_challenge`, controller pauses browser session (HIL-04) |
| `test_resolve_challenge_resumes_workflow` | User submits `resolve-challenge` endpoint or WebSocket event | Challenge resolved flag set, pause unblocked, workflow resumes smoothly (HIL-04) |

---

## Acceptance Criteria Checklist

- [ ] All tests in `backend/tests/test_agent_approval.py` pass.
- [ ] All tests in `backend/tests/test_agent_security_challenge.py` pass.
- [ ] Frontend Workspace displays pre-submission review modal with detailed field summary.
- [ ] Citizen can approve or reject application submission from UI.
- [ ] Security challenge banner appears when CAPTCHA/OTP detected, allowing 1-click resume after completion.
- [ ] Frontend builds with 0 errors and 0 warnings (`npm --prefix frontend run build`).
- [ ] Full backend test regression passes (`pytest backend/tests/ -v`).
