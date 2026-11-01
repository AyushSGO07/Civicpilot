---
phase: "11"
name: "submission-verification-receipt-retrieval-application-tracking"
created: 2026-11-01
---

# Phase 11: Submission Verification, Receipt Retrieval & Application Tracking — Context

## User Constraints & Architectural Directives

### Locked Decisions
- **D-01 (Authentic Submission Verification - APP-01):** The agent MUST verify authentic portal confirmation text and extract the genuine acknowledgement/reference number (e.g. `Application No: NSP/2026/894125`, `PMK-MH-948123`, `AB-PMJAY-2026-441290`). Zero dummy references allowed.
- **D-02 (Submission Receipt PDF Capture & Storage - APP-02):** The agent generates or captures the authentic portal receipt PDF upon successful submission, saves it to private storage (`storage/receipts/` and Supabase Storage), and associates it with the application record.
- **D-03 (My Applications Dashboard - APP-03):** Deliver an operations dashboard at `/applications` following MakeMyTrip design guidelines with elevated cards, high-contrast typography, status indicators, and category tabs.
- **D-04 (Application Metadata & Tracking - APP-04):** Each application card displays: Scheme name, issuing department, current status (Draft, In Progress, Waiting Approval, Submitted, Approved), submission timestamp, official portal link, and reference number.
- **D-05 (Direct Receipt Download - APP-05):** Citizens can download their official submission receipt PDF directly from the dashboard card with 1 click.
- **D-06 (Zero Dummy Data):** All portal links must resolve to authentic official government domains (`.gov.in`, `.nic.in`), and receipt PDFs must record genuine timestamps, scheme titles, and citizen attributes.

### Discretion Areas
- Local storage fallback directory for receipts (`storage/receipts/`) when Supabase cloud storage is not connected.
- Receipt generation engine (Playwright Chromium `page.pdf()` and ReportLab/canvas fallback for generating authentic Government of India formatted acknowledgement slips).
- API routes: `GET /api/applications`, `GET /api/applications/{id}`, `GET /api/applications/{id}/receipt`.

### Deferred Ideas
- Cross-ministry automated status tracking webhooks / SMS sync (v2 roadmap).
- DigiLocker auto-push of submission certificates (v2 roadmap).
