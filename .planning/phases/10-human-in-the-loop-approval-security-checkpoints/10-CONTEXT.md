---
phase: "10"
name: "human-in-the-loop-approval-security-checkpoints"
created: 2026-11-01
---

# Phase 10: Human-in-the-Loop Approval & Security Checkpoints — Context

## User Constraints & Architectural Directives

### Locked Decisions
- **D-01 (Mandatory Approval Gate before Submission - HIL-01):** The agent MUST pause execution before taking any irreversible submission action (such as clicking final "Submit" or "Apply" buttons). Automation will never self-submit government applications without unambiguous user consent.
- **D-02 (Comprehensive Pre-Submission Summary - HIL-02):** Before requesting approval, the agent must compile a structured summary detailing every field populated into the form (element label, attribute source, mapped value, confidence) and all attached vault documents.
- **D-03 (Approve or Reject Branching - HIL-03):** The citizen can explicitly grant approval to submit (`approval_status = "approved"`), or reject submission (`approval_status = "rejected"`) with optional feedback to return to editing mode.
- **D-04 (Automated CAPTCHA & OTP Challenge Detection - HIL-04):** The agent scans page DOM and text patterns for security challenges (reCAPTCHA, hCaptcha, Turnstile, image CAPTCHAs, SMS OTP, Aadhaar OTP inputs). Upon detection, it pauses automation immediately, transitions state to `waiting_security_challenge`, broadcasts a challenge alert over WebSockets, and prompts the user to solve it.
- **D-05 (Seamless Challenge Resolution):** When the citizen solves the CAPTCHA/OTP in the browser and clicks "I have completed OTP/CAPTCHA", the execution controller unblocks the gate and resumes the LangGraph workflow seamlessly.
- **D-06 (Zero Dummy Data & Security Integrity):** All approvals and challenge notices strictly reflect real live portal states and real citizen vault documents. No mock submission bypasses or fabricated OTPs.

### Discretion Areas
- Presentation layout for Pre-Submission Review (modal dialog vs full-screen overlay in the 3-panel operations workspace).
- Mechanism for challenge detection (heuristic DOM element query matching common Indian government portal CAPTCHA and OTP element IDs/names/labels).
- Workflow resumption API (`POST /api/agent/workflow/{thread_id}/approval`, `POST /api/agent/workflow/{thread_id}/challenge-resolved`, and WebSocket action messages).

### Deferred Ideas
- Authentic submission confirmation parsing and application tracking receipt generation (Phase 11 - APP-01 through APP-05).
- Multi-factor Biometric / DigiLocker direct e-Sign integration (Post-v1.0 roadmap).
