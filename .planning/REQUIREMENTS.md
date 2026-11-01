# Requirements: CivicPilot

**Defined:** 2026-11-01
**Core Value:** Autonomous, genuine navigation and execution of real government application workflows on official portals with verified eligibility and explicit human-in-the-loop approval.

## v1 Requirements

Requirements for initial hackathon release. Each maps to roadmap phases.

### User Interface & Design System

- [ ] **UI-01**: User experiences a MakeMyTrip-inspired consumer visual hierarchy with deep navy (`#1A2B4C`), vibrant blue (`#0056D2`), cyan accents, and clean card spacing
- [ ] **UI-02**: User can navigate using a sticky global navbar with links to Home, Services, Applications, Documents, and Profile
- [ ] **UI-03**: User can view a responsive Hero section with natural language search bar and category quick-filter tabs
- [ ] **UI-04**: User can interact with accessible, keyboard-navigable components with smooth micro-interactions and loading skeletons

### Authentication & Sessions

- [ ] **AUTH-01**: User can register an account using email and password via Supabase Auth
- [ ] **AUTH-02**: User can log in and maintain a persistent authenticated session across page reloads
- [ ] **AUTH-03**: User can log out securely from any screen
- [ ] **AUTH-04**: User cannot access private profile, documents, or application execution routes without authentication

### Citizen Profile

- [ ] **PROF-01**: User can input and update personal identity information (full name, date of birth, gender, contact number)
- [ ] **PROF-02**: User can input and update address details (state, district, PIN code)
- [ ] **PROF-03**: User can input and update educational background (current education level, institution name, course, academic year)
- [ ] **PROF-04**: User can voluntarily provide scheme-specific eligibility attributes (annual family income, occupation, social category)
- [ ] **PROF-05**: User can review and save profile updates with instant client validation

### Document Vault & OCR Processing

- [ ] **DOC-01**: User can upload PDF, JPG, and PNG documents to a secure private Supabase Storage bucket
- [ ] **DOC-02**: User can view a preview and metadata of all uploaded documents in the vault
- [ ] **DOC-03**: User can trigger Gemini multimodal OCR extraction on uploaded documents (Aadhaar, PAN, Marksheet, Certificates)
- [ ] **DOC-04**: User can inspect and verify extracted OCR fields before confirming them into their profile
- [ ] **DOC-05**: User can delete uploaded documents from their vault with server-side storage cleanup

### Scheme Discovery & Search

- [ ] **DISC-01**: User can search government schemes using natural language queries (e.g., "scholarships for engineering in Bihar")
- [ ] **DISC-02**: User can filter schemes by category (Education, Scholarships, Transport, Agriculture, MSME, Healthcare)
- [ ] **DISC-03**: User can view detailed scheme cards displaying issuing department, summary, required documents, and official source URL
- [ ] **DISC-04**: User can access verified official portal links directly from the scheme detail view

### AI Eligibility Assistant

- [ ] **ELIG-01**: User can query scheme eligibility ("Am I eligible for this scholarship?") and receive an automated assessment
- [ ] **ELIG-02**: User receives an eligibility determination (Likely Eligible, Likely Ineligible, or More Information Required)
- [ ] **ELIG-03**: User sees an itemized breakdown comparing their profile data against official scheme conditions
- [ ] **ELIG-04**: User is notified of missing profile fields required to complete eligibility evaluation
- [ ] **ELIG-05**: User sees citations to official scheme guidelines for every eligibility evaluation

### Autonomous Browser Automation Core

- [ ] **AGENT-01**: Backend launches an asynchronous Playwright Chromium browser instance targeting the official portal URL
- [ ] **AGENT-02**: Agent inspects the portal webpage structure and extracts a sanitized semantic DOM element tree
- [ ] **AGENT-03**: Agent dynamically maps citizen profile fields to portal input elements using Gemini structured mapping
- [ ] **AGENT-04**: Agent autonomously populates text fields, radio buttons, dropdowns, and checkboxes on the portal
- [ ] **AGENT-05**: Agent attaches required documents from the citizen's vault into portal file upload fields
- [ ] **AGENT-06**: Agent executes bounded recovery (max 3 retries) when encountering element timeouts or unexpected alert dialogs
- [ ] **AGENT-07**: Agent terminates browser processes cleanly on completion, error, or session abort without zombie processes

### Agent Execution Workspace & Controls

- [ ] **EXEC-01**: User can monitor real-time execution in a 3-panel operations workspace (Profile Summary, Live Browser Stream, AI Reasoning Log)
- [ ] **EXEC-02**: User receives real-time progress events streamed over WebSockets (`/ws/agent/{sessionId}`)
- [ ] **EXEC-03**: User can watch live browser visual screenshots updated as the agent interacts with the portal
- [ ] **EXEC-04**: User can pause and resume the browser agent's autonomous execution
- [ ] **EXEC-05**: User can abort execution at any time, halting the browser safely

### Human-in-the-Loop Approval & Verification

- [ ] **HIL-01**: Agent pauses execution before final application submission and requests explicit user approval
- [ ] **HIL-02**: User can review a pre-submission summary of all populated form values and attached documents
- [ ] **HIL-03**: User can approve submission or reject it to return to editing
- [ ] **HIL-04**: Agent detects CAPTCHA, OTP, or MFA challenges and pauses execution for the citizen to solve in the browser session

### Submission Verification & Application Tracking

- [ ] **APP-01**: Agent detects portal submission success, verifies acknowledgement confirmation text, and extracts genuine reference number
- [ ] **APP-02**: Agent captures or downloads the authentic portal submission receipt PDF and stores it in Supabase
- [ ] **APP-03**: User can view submitted and draft applications on the "My Applications" dashboard
- [ ] **APP-04**: User can view submission timestamp, official portal link, and current application status
- [ ] **APP-05**: User can download their official submission receipt from the dashboard

## v2 Requirements

Deferred to future releases after initial hackathon validation.

### Localization & Accessibility

- **LOC-01**: User can switch the interface language to Hindi or major regional Indian languages
- **LOC-02**: User can listen to scheme descriptions and instructions via text-to-speech

### Integrations

- **INT-01**: User can import verified documents directly from Digilocker via official OAuth integration
- **INT-02**: User can receive WhatsApp notifications when their application status changes on the government portal
- **INT-03**: User can track recurring status updates via automated background portal polling

## Out of Scope

Explicitly excluded to protect security, legal compliance, and hackathon evaluation criteria.

| Feature | Reason |
|---------|--------|
| Automated CAPTCHA / OTP / Biometric bypassing | Severe violation of IT laws and portal security terms; handled securely via Human-in-the-Loop pause. |
| Autonomous payment of government fees | High financial fraud risk; handled by pausing for user payment at the official gateway. |
| Simulated or mocked portal submissions | Prohibited by hackathon Zero-Dummy-Data rules; only genuine portals and real HTTP/DOM actions are permitted. |
| Fabricating application acknowledgement numbers | Dishonest and invalid; unverified submissions must be flagged transparently. |
| Universal coverage for all 1000+ government portals in v1 | Focused on delivering a verified, resilient workflow on high-impact target schemes (scholarship/welfare). |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| UI-01 | Phase 1 | Pending |
| UI-02 | Phase 1 | Pending |
| UI-03 | Phase 1 | Pending |
| UI-04 | Phase 1 | Pending |
| AUTH-01 | Phase 2 | Pending |
| AUTH-02 | Phase 2 | Pending |
| AUTH-03 | Phase 2 | Pending |
| AUTH-04 | Phase 2 | Pending |
| PROF-01 | Phase 2 | Pending |
| PROF-02 | Phase 2 | Pending |
| PROF-03 | Phase 2 | Pending |
| PROF-04 | Phase 2 | Pending |
| PROF-05 | Phase 2 | Pending |
| DOC-01 | Phase 3 | Pending |
| DOC-02 | Phase 3 | Pending |
| DOC-03 | Phase 3 | Pending |
| DOC-04 | Phase 3 | Pending |
| DOC-05 | Phase 3 | Pending |
| DISC-01 | Phase 4 | Pending |
| DISC-02 | Phase 4 | Pending |
| DISC-03 | Phase 4 | Pending |
| DISC-04 | Phase 4 | Pending |
| ELIG-01 | Phase 5 | Pending |
| ELIG-02 | Phase 5 | Pending |
| ELIG-03 | Phase 5 | Pending |
| ELIG-04 | Phase 5 | Pending |
| ELIG-05 | Phase 5 | Pending |
| AGENT-01 | Phase 6 | Pending |
| AGENT-02 | Phase 6 | Pending |
| AGENT-07 | Phase 6 | Pending |
| AGENT-03 | Phase 7 | Pending |
| AGENT-04 | Phase 7 | Pending |
| AGENT-05 | Phase 7 | Pending |
| AGENT-06 | Phase 8 | Pending |
| EXEC-01 | Phase 9 | Pending |
| EXEC-02 | Phase 9 | Pending |
| EXEC-03 | Phase 9 | Pending |
| EXEC-04 | Phase 9 | Pending |
| EXEC-05 | Phase 9 | Pending |
| HIL-01 | Phase 10 | Pending |
| HIL-02 | Phase 10 | Pending |
| HIL-03 | Phase 10 | Pending |
| HIL-04 | Phase 10 | Pending |
| APP-01 | Phase 11 | Pending |
| APP-02 | Phase 11 | Pending |
| APP-03 | Phase 11 | Pending |
| APP-04 | Phase 11 | Pending |
| APP-05 | Phase 11 | Pending |

**Coverage:**
- v1 requirements: 44 total
- Mapped to phases: 44
- Unmapped: 0 ✓

---
*Requirements defined: 2026-11-01*
*Last updated: 2026-11-01 after initial definition*
