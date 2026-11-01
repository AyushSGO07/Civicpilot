# Pitfalls Research

**Domain:** Autonomous Public Service & Bureaucracy Execution Agent
**Researched:** 2026-11-01
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: Fragile Selectors & Government Portal UI Variations

**What goes wrong:**
Hardcoded CSS selectors, exact XPath strings, or element ID references break without warning. Government portals routinely change minor markup, alter ID prefixes, or wrap inputs inside dynamically generated ASP.NET/JSP table structures.

**Why it happens:**
Developers apply standard web scraping patterns (e.g., `#txtApplicantName_01`), which are brittle across varying states and portal updates.

**How to avoid:**
Use semantic DOM mapping powered by Gemini and Playwright accessible locators (`getByLabel`, `getByRole`, ARIA attributes). Playwright extracts the interactive form tree; Gemini matches the intent ("Applicant Full Name") to the matching accessible handle dynamically.

**Warning signs:**
`Playwright.TimeoutError: Element locator "#applicant_name" not found within 30000ms`.

**Phase to address:**
Phase 3 (Autonomous Agent Core — Dynamic Field Mapping).

---

### Pitfall 2: Infinite Execution Loops on Unhandled Validation Errors

**What goes wrong:**
A form validation error (such as "PIN Code must be 6 digits" or an unexpected alert dialog) appears. The agent repeatedly attempts to click "Proceed" or "Submit", getting stuck in a loop, consuming tokens, and freezing.

**Why it happens:**
Unbounded retry loops without page-state mutation verification.

**How to avoid:**
Implement strict LangGraph bounded retries (maximum 3 attempts). Before re-executing any action, take a DOM diff to verify whether the previous action changed the page state. If a blocking validation error or modal is detected that the agent cannot resolve, transition immediately to `AWAITING_USER_ACTION`.

**Warning signs:**
Consecutive identical action events without URL or DOM change.

**Phase to address:**
Phase 3 & Phase 4 (Error Recovery & Execution Workspace).

---

### Pitfall 3: The "Zero Dummy Data" Hackathon Violation Trap

**What goes wrong:**
Mocking portal responses, displaying fake green "Application Approved" notifications, or generating random receipt numbers (e.g. `ACK-123456`). In a technical evaluation, judges inspect network tabs, database records, and server logs. Fabricated data leads to immediate disqualification.

**Why it happens:**
Government portals can be slow, require official working hours, or have intermittent connectivity, tempting teams to short-circuit with mocks.

**How to avoid:**
- Source all schemes from live official portals (MyScheme API/portal, National Scholarship Portal).
- Drive actual browser sessions against real public URLs.
- If a portal requires citizen credentials or payment that cannot be automated, execute up to the human checkpoint honestly.
- Store real timestamps, source URLs, and genuine acknowledgement numbers or honest status records ("Pending Official Verification").

**Warning signs:**
Hardcoded static JSON files masquerading as live API endpoints.

**Phase to address:**
Phase 2 (Real Government Data Integration) & Phase 5 (Application Management).

---

### Pitfall 4: Bypassing CAPTCHA / Security Controls

**What goes wrong:**
Attempting to build automated solvers for government CAPTCHAs, OTPs, or Aadhaar biometrics. This violates security policies, gets the agent IP blacklisted, and creates legal liability.

**Why it happens:**
Over-promising "100% end-to-end hands-off autonomy" without respecting security boundaries.

**How to avoid:**
Embrace Human-in-the-Loop as a core feature: when a CAPTCHA, SMS OTP, or MFA screen is detected, the agent pauses, streams the browser view to the user, and presents a clear prompt: "Please solve the security verification in the browser window to continue". Once completed, the agent resumes execution seamlessly.

**Warning signs:**
OCR scripts targeting distorted CAPTCHA images or trying to intercept SMS gateways.

**Phase to address:**
Phase 4 (Agent Execution Workspace & Human-in-the-Loop Gate).

---

### Pitfall 5: Browser Process Leaks & Zombie Chromium Instances

**What goes wrong:**
Playwright Chromium browser instances remain running in the background when sessions fail, disconnect, or time out, rapidly exhausting server memory (RAM) and crashing the FastAPI server.

**Why it happens:**
Lack of proper lifecycle cleanup in async Python when WebSocket connections drop abruptly.

**How to avoid:**
Wrap all browser operations in Python async context managers or robust `try...finally` blocks. Implement a background cleanup task that checks for abandoned sessions older than 15 minutes and calls `await browser_context.close()`.

**Warning signs:**
Server memory steadily increasing (`htop` showing multiple orphaned Chromium processes).

**Phase to address:**
Phase 3 (Browser Automation Infrastructure).

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Passing entire raw HTML string to LLM | Quick to write without HTML parsing | Huge token cost, slower latency, and context overflow errors | Never — always prune DOM before LLM mapping. |
| Storing user documents in local filesystem | No cloud bucket configuration needed | Files lost on server restarts; insecure and non-scalable | Never — use Supabase Storage with signed URLs. |
| Polling REST endpoints instead of WebSockets | Simpler frontend code | Delayed UI updates, heavy server polling load | Only as a fallback if WebSocket disconnects. |

## "Looks Done But Isn't" Checklist

- [ ] **Document Upload:** Looks done when file uploads — verify Gemini OCR actually extracted and validated fields into the profile.
- [ ] **Service Discovery:** Looks done with 5 cards — verify cards come from live official government sources with real source URLs.
- [ ] **Form Filling:** Looks done when fields populate — verify multi-step forms, dropdown selection triggers (`change` events), and radio buttons actually register in the DOM.
- [ ] **Pause/Resume:** Looks done with UI buttons — verify the Playwright browser actually halts and resumes execution when the user clicks Pause/Resume.
- [ ] **Submission Receipt:** Looks done with a "Success" message — verify an actual acknowledgement number or official PDF receipt was downloaded and saved.

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Fragile Selectors | Phase 3 (Agent Core) | Test field mapper against 3 distinct form layouts with differing HTML structures. |
| Infinite Loops | Phase 3 (Agent Core) | Inject synthetic invalid input and confirm agent aborts after 3 attempts. |
| Zero-Dummy-Data Violation | Phase 2 (Data Integration) | Verify all scheme records contain legitimate `official_source_url` and retrieval timestamps. |
| CAPTCHA Handling | Phase 4 (Workspace) | Verify agent correctly halts and yields control upon detecting CAPTCHA elements. |
| Zombie Browsers | Phase 3 (Agent Core) | Disconnect WebSocket abruptly and verify Chromium process is cleanly terminated. |

## Sources

- Playwright Python Best Practices on Process Management: https://playwright.dev/python/docs/library
- Web Automation Security & Anti-Bot Guidelines
- Hackathon Zero-Dummy-Data Compliance Rules

---
*Pitfalls research for: Autonomous Public Service & Bureaucracy Execution Agent*
*Researched: 2026-11-01*
