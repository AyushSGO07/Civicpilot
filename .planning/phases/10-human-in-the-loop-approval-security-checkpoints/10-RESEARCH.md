# Phase 10: Human-in-the-Loop Approval & Security Checkpoints — Technical Research

## 1. Domain & Security Analysis

### Indian Government Portal Security Patterns
Indian public portals (National Scholarship Portal, PM-Kisan, PM-JAY, Sarathi/Parivahan) utilize specific security verification mechanisms designed to prevent automated bot submissions while allowing legitimate citizens access:
1. **Dynamic Image CAPTCHA:**
   - Elements commonly use IDs/classes/names like `txtCaptcha`, `captchaInput`, `imgCaptcha`, `captchaImg`, `regCaptcha`.
   - Text prompts: "Enter the code shown above", "Enter captcha", "Type characters".
2. **Aadhaar / Mobile SMS OTP:**
   - Elements commonly use IDs/classes/names like `txtOTP`, `otpInput`, `mobileOtp`, `aadhaarOtp`, `otpValue`.
   - Text prompts: "Enter 6-digit OTP sent to registered mobile", "One Time Password", "Resend OTP in 30s".
3. **Turnstile / reCAPTCHA v2/v3:**
   - Google reCAPTCHA iframes (`iframe[src*='recaptcha']`), `.g-recaptcha`, `hcaptcha`, Cloudflare Turnstile containers.

### Challenge Detection Heuristics
Rather than requiring complex computer vision to classify every portal layout, a high-reliability semantic heuristic inspects both the DOM tree and live page text for:
- Input names, IDs, placeholders, or aria-labels containing `captcha`, `recaptcha`, `hcaptcha`, `turnstile`, `otp`, `one-time-password`, `verification-code`.
- Images whose source URL contains `captcha` or `securimage`.
- On-page text containing phrases such as "Enter the characters", "Enter OTP", "Verification code sent".

When any such element is present and active, the agent identifies the challenge type (`captcha` vs `otp` vs `mfa`) and pauses automation.

---

## 2. LangGraph Human-in-the-Loop Interruption Architecture

### State Persistence & Breakpoint Execution
LangGraph supports human-in-the-loop patterns via state machine persistence (`MemorySaver` checkpointer):
1. **State Node: `waiting_approval` (HIL-01):**
   - After `validate_node` confirms all inputs are populated without errors, the graph routes to `waiting_approval`.
   - The node compiles `submission_summary` payload and halts.
   - The WebSocket manager broadcasts `status: "waiting_approval"` with milestone: "Form validation complete. Awaiting citizen authorization to submit."
2. **State Node: `waiting_security_challenge` (HIL-04):**
   - If `SecurityChallengeDetector` detects a CAPTCHA or OTP challenge at any stage (navigation, inspection, filling), the graph routes to `waiting_security_challenge`.
   - The execution controller pauses the session gate (`execution_controller.pause()`), and the WebSocket manager broadcasts `status: "waiting_security_challenge"`.
3. **Resumption via Thread Config:**
   - Calling `POST /api/agent/workflow/{thread_id}/approve` updates the state with `approval_decision: "approved"` and invokes the workflow from the saved checkpoint to complete the journey.
   - Calling `POST /api/agent/workflow/{thread_id}/reject` sets `approval_decision: "rejected"` and transitions to `cancelled` or returns to editing.
   - Calling `POST /api/agent/workflow/{thread_id}/resolve-challenge` sets `challenge_resolved: True`, unpauses the execution controller, and resumes from the interrupted stage.

---

## 3. Data Schema Models

### PreSubmissionSummary Payload (HIL-02)
```python
class PopulatedFormField(BaseModel):
    field_label: str
    element_name: str
    locator: str
    value_populated: str
    source_attribute: str
    confidence: float

class AttachedVaultDocument(BaseModel):
    document_name: str
    document_type: str
    vault_id: str
    verified: bool

class PreSubmissionSummary(BaseModel):
    service_id: str
    service_name: str
    portal_url: str
    populated_fields: List[PopulatedFormField]
    attached_documents: List[AttachedVaultDocument]
    generated_at: str
    total_fields: int
    all_mandatory_satisfied: bool
    disclaimer: str = (
        "Statutory Advisory: By approving this submission, you authorize CivicPilot to execute "
        "the final application submission on your behalf on the official portal."
    )
```

### SecurityChallenge Payload (HIL-04)
```python
class SecurityChallengeInfo(BaseModel):
    detected: bool
    challenge_type: Optional[Literal["captcha", "otp", "mfa"]] = None
    element_locator: Optional[str] = None
    instructions: str = ""
    prompt_message: str = ""
```

---

## 4. Frontend Operations UX (MakeMyTrip Design System)

1. **Pre-Submission Review Modal:**
   - Clean elevated modal dialog (`bg-slate-900 border-slate-800 text-white`).
   - Sticky header with scheme badge, target portal URL, and total field count.
   - Two-column structured summary:
     - Left column: Grouped applicant identity and eligibility fields with value chips.
     - Right column: Attached vault documents with green verified checkmarks.
   - High-contrast statutory warning banner with lock icon.
   - Dual action CTAs:
     - **"Approve & Submit Application"** (`bg-emerald-600 hover:bg-emerald-500 font-bold`).
     - **"Reject & Return to Edit"** (`variant="outline" border-slate-700`).

2. **Security Challenge Banner & Viewport Overlay:**
   - When `waiting_security_challenge` is active:
     - Viewport displays an amber pulsing alert banner above the live browser stream.
     - Center screen indicates: "Action Required: Solve CAPTCHA / Enter OTP on Portal".
     - Primary action button: **"I have completed CAPTCHA / OTP — Resume Automation"** (Civic Blue).
     - Clicking resumes the agent and unblocks the execution controller immediately.
