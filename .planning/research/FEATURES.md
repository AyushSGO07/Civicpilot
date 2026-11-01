# Feature Research

**Domain:** Autonomous Public Service & Bureaucracy Execution Agent
**Researched:** 2026-11-01
**Confidence:** HIGH

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Email Authentication & Session Persistence | Users need their profile, uploaded docs, and applications saved securely across visits. | LOW | Supabase Auth (email/password signup, login, session tokens, JWT). |
| Citizen Profile Center | Required to avoid re-entering personal, educational, and address data for every scheme. | MEDIUM | Personal info, educational qualifications, address (State, District, PIN), voluntary scheme criteria. |
| Secure Document Vault | Government applications require uploading proofs (Aadhaar, income certificate, marksheets). | MEDIUM | Encrypted file uploads (PDF/JPG/PNG) to Supabase Storage with signed private URLs. |
| Scheme Discovery & Filterable Catalog | Users need to find available schemes by sector (Scholarships, Agriculture, MSME, Transport). | MEDIUM | Live integration with MyScheme and India.gov.in data; search by keyword, state, and category. |
| AI Eligibility Assessment | Citizens want to know "Am I eligible?" before starting a tedious application. | MEDIUM | Gemini evaluates saved citizen profile against official scheme criteria with citations and missing fields report. |
| My Applications Dashboard | Citizens expect to see past and active applications with their official statuses. | MEDIUM | Stores service name, official portal URL, submission timestamp, acknowledgement number, and downloaded receipt. |
| Responsive, Consumer-Grade UI | Sterile government portals create anxiety; users expect a consumer-grade experience. | MEDIUM | MakeMyTrip-inspired design (Deep navy `#1A2B4C`, vibrant blue `#0056D2`, cyan accents, light background `#F5F7FB`). |

### Differentiators (Competitive Advantage)

Features that set CivicPilot apart. Not required, but provide massive competitive advantage.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Autonomous Browser Execution Agent | Actually navigates government portals and completes the paperwork instead of just giving instructions. | HIGH | Playwright async engine controlled by LangGraph state machine with DOM inspection and auto-filling. |
| Live Agent Operations Workspace | Builds total trust by letting the citizen watch the agent's live browser stream and reasoning timeline in real-time. | HIGH | Three-panel layout: Left (Citizen Summary), Center (Live Browser Canvas/Stream), Right (AI Reasoning & Action History). |
| Real-time WebSocket Event Streaming | Real-time transparency showing genuine automation steps as they happen. | MEDIUM | Streams genuine execution milestones (`PORTAL_DISCOVERED`, `FIELDS_MAPPED`, `FILLING_INPUT`, `APPROVAL_REQUIRED`). |
| Dynamic Semantic DOM Mapping | Works across varying government portal HTML layouts without rigid, hardcoded CSS selectors. | HIGH | Uses Gemini to map citizen profile JSON fields to DOM input elements extracted by Playwright. |
| Human-in-the-Loop Approval Gate | Total safety: agent presents exact data entered and selected documents before any irreversible submit. | MEDIUM | Explicit "Approve & Submit" or "Reject / Edit" controls; pauses for CAPTCHA/OTP input. |
| Intelligent Multimodal OCR Extraction | Automatically parses uploaded identity documents and marksheets to auto-populate the citizen profile. | MEDIUM | Gemini vision OCR extracts name, DOB, ID numbers, grades, and validates document readability. |
| Authentic Receipt & Ack Retrieval | Retrieves genuine confirmation numbers, verifies portal confirmation text, and stores official PDF receipts. | MEDIUM | Captures confirmation DOM screenshot, extracts reference number, and downloads portal acknowledgement PDF. |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create severe security, legal, or architectural problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Automated CAPTCHA / OTP Bypassing | "Fully autonomous submission without user interruption." | Violates government terms of service, breaks security laws, and fails unpredictably. | Seamless Human-in-the-Loop Pause: Agent pauses, notifies user via WebSocket, user solves CAPTCHA, agent resumes. |
| Autonomous Fee Payments / Credit Card Auto-fill | "Pay government registration fees automatically." | Extreme liability, high financial fraud risk, and bank OTP constraints. | Pause execution at the payment gateway and hand over the session to the citizen to complete transaction safely. |
| Simulated / Mock Portal Interactions | "Easier to show a demo without worrying about portal downtime." | Violates hackathon zero-dummy-data policy; destroys credibility with judges. | Interact with genuine government portals (e.g. National Scholarship Portal / MyScheme) or test sandboxes with genuine HTTP/DOM. |
| Fabricated Reference Numbers / Fake Receipts | "Show a green 'Success' screen even if portal submission times out." | Dishonest and misleading; violates specification rules. | Transparent error reporting: "Submission unverified on portal; draft saved; manual review needed." |
| Universal Scraper for All 1000+ Portals in v1 | "Support every single state and central scheme immediately." | Massive scope creep; impossible to test in hackathon timeline. | Build a modular, extensible agent architecture demonstrated flawlessly on high-impact official workflows. |

## Feature Dependencies

```
[Citizen Profile] ──required-by──> [AI Eligibility Assistant]
      │
      ├──required-by──> [Dynamic Form Mapping] ──required-by──> [Autonomous Form Filling]
      │                                                                │
[Document Vault] ──required-by──> [Document Upload to Portal] ─────────┘
                                                                       │
                                                       [Human Approval Gate]
                                                                       │
                                                       [Submission & Verification]
                                                                       │
                                                       [My Applications Tracking]
```

### Dependency Notes

- **Dynamic Form Mapping requires Citizen Profile & Document Vault:** The agent cannot map and fill portal fields without verified citizen data and uploaded files.
- **Autonomous Form Filling requires LangGraph & Playwright:** The execution loop requires Playwright for DOM actions and LangGraph to maintain checkpointed state.
- **Submission requires Human Approval Gate:** To comply with security and user control requirements, submission can never proceed without explicit user sign-off.
- **My Applications depends on Submission Verification:** Applications are only marked submitted once authentic acknowledgement numbers or confirmation texts are detected.

## MVP Definition

### Launch With (v1)

Minimum viable product required for end-to-end hackathon demonstration:

- [ ] **MakeMyTrip-inspired UI**: Responsive navbar, Hero with natural language search, service category filters, and polished card deck.
- [ ] **Authentication & Profile**: Supabase email auth, persistent citizen profile (personal, educational, address).
- [ ] **Document Vault**: Upload, preview, and Gemini OCR extraction for Aadhaar, PAN, Marksheets, and Certificates.
- [ ] **Live Service Discovery**: Integration with verified government schemes (MyScheme data).
- [ ] **AI Eligibility Assistant**: Gemini-powered evaluation with transparent criteria comparison and citations.
- [ ] **LangGraph Execution Engine**: State machine handling planning, portal opening, field inspection, form filling, approval, and receipt retrieval.
- [ ] **Playwright Browser Agent**: Server-side Chromium automation with accessible locators and dynamic field filling.
- [ ] **Agent Operations Workspace**: Split-view UI with live browser screen streaming, WebSocket event log, and Pause/Resume/Approve controls.
- [ ] **Human-in-the-Loop Safety**: Pausing for user review and manual CAPTCHA/OTP resolution.
- [ ] **My Applications Tracking**: Dashboard displaying genuine submission status, reference numbers, and receipts.

### Add After Validation (v1.x)

- [ ] Multi-lingual interface supporting Hindi and regional Indian languages.
- [ ] WhatsApp notification integration for application status alerts.
- [ ] Digilocker API integration for instant official document import.

### Future Consideration (v2+)

- [ ] Voice-assisted application filing for low-literacy rural citizens.
- [ ] Multi-agent collaborative execution (e.g. one agent verifying documents while another navigates the portal).
- [ ] Citizen grievance filing and RTI (Right to Information) automated escalation.

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Citizen Profile & Document Vault | HIGH | MEDIUM | P1 |
| Scheme Discovery & Search | HIGH | MEDIUM | P1 |
| AI Eligibility Assistant | HIGH | MEDIUM | P1 |
| Autonomous Playwright Agent | HIGH | HIGH | P1 |
| Agent Execution Workspace & WebSockets | HIGH | HIGH | P1 |
| Human Approval & Bounded Recovery | HIGH | MEDIUM | P1 |
| My Applications Dashboard | HIGH | LOW | P1 |
| Multilingual Support | MEDIUM | MEDIUM | P2 |
| Digilocker Direct Integration | HIGH | HIGH | P2 |
| Voice Interface | MEDIUM | HIGH | P3 |

## Competitor Feature Analysis

| Feature | Traditional Govt Portals (e.g. National Scholarship Portal) | Generic AI Chatbots (ChatGPT / Perplexity) | CivicPilot Approach |
|---------|-------------------------------------------------------------|--------------------------------------------|---------------------|
| Scheme Discovery | Cluttered, confusing, siloed by department | Provides text list of schemes, often hallucinated | Curated, verified live schemes from official sources with consumer UI |
| Eligibility Check | Complex multi-page manuals and PDF criteria | Basic text comparison without profile memory | Automated deep comparison against user's saved profile with source citations |
| Form Filling | 100% manual, repetitive, confusing validation errors | Zero form filling capability (text only) | Autonomous Playwright agent maps and populates fields automatically |
| Document Handling | Strict manual file size/format compressions | Can read files, but cannot upload to portals | Secure vault with OCR extraction and automated portal attachment |
| Execution Visibility | Blank loading spinners or server crashes | None | Live visual stream of the browser agent navigating in real-time |
| Safety & Control | User does everything manually | No execution risk | LangGraph human approval gate with explicit review before submission |

## Sources

- National Scholarship Portal (NSP): https://scholarships.gov.in/
- MyScheme Portal: https://www.myscheme.gov.in/
- India.gov.in National Portal: https://www.india.gov.in/
- MakeMyTrip UX Design Patterns (Industry standard for consumer discovery & high-trust flows)

---
*Feature research for: Autonomous Public Service & Bureaucracy Execution Agent*
*Researched: 2026-11-01*
