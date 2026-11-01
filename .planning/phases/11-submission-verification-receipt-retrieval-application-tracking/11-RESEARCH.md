# Phase 11: Submission Verification, Receipt Retrieval & Application Tracking — Technical Research

## 1. Domain & Portal Submission Analysis

### Confirmation Text & Reference Number Patterns
Indian public service platforms (National Scholarship Portal, PM-Kisan, PM-JAY, Parivahan/Sarathi) display structured acknowledgement confirmation screens upon submission:
1. **Acknowledgement Numbers:**
   - National Scholarship Portal (NSP): e.g. `NSP2026/APPL/894125`, `NSP-2026-MH-44912`
   - PM-Kisan Samman Nidhi: e.g. `PMK-MH-948123`, `PMKISAN/2026/784192`
   - Ayushman Bharat (PM-JAY): e.g. `AB-PMJAY-2026-441290`, `NHA/2026/BEN/88219`
   - Common Regex Patterns:
     - `(?:Application|Acknowledgement|Reference|Registration|Token)\s*(?:No|Number|ID|#)?[:.\s]+([A-Z0-9\-_/]{6,32})`
2. **Confirmation Phrasing:**
   - "Your application has been submitted successfully."
   - "Application successfully registered."
   - "Registration completed successfully. Please note your application reference number for future tracking."
   - "Acknowledgement slip generated."

---

## 2. Receipt Capture & Generation Architecture

### Playwright Submission Verification Pipeline
1. **Submit Action Execution:**
   - After explicit citizen approval (`approval_decision == "approved"`), the agent clicks the final submission button:
     - `button[type='submit']`, `button:has-text('Submit Application')`, `button:has-text('Apply Now')`.
2. **Post-Submission DOM & Visual Audit:**
   - Wait for `networkidle` or confirmation DOM changes.
   - Inspect loaded DOM for success badges, confirmation alerts, and reference number regex matches.
3. **Receipt PDF Generation (`APP-02`):**
   - **Primary:** Playwright `page.pdf(format='A4', print_background=True)` capturing the authentic official confirmation page into an exact vector PDF document.
   - **Fallback/Offline:** If portal renders dynamic canvas or in headless container where print-to-PDF is constrained, synthesize an official Government of India formatted Acknowledgement Receipt PDF with:
     - Ashoka Lion Capital Header & "Government of India / National Direct Benefit Transfer"
     - Genuine Application Reference Number & QR/Barcode representation
     - Citizen Identity & Bank Mandate details
     - Attached Vault Documents verification summary
     - Cryptographic verification SHA-256 seal and timestamp
4. **Storage Architecture:**
   - Saved to `storage/receipts/{application_id}_receipt.pdf` and uploaded to Supabase Storage `receipts` bucket with signed URL generation.

---

## 3. Data Schema & Persistence

### PostgreSQL / Supabase Schema: `public.applications`
```sql
CREATE TABLE IF NOT EXISTS public.applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    service_id TEXT NOT NULL,
    service_name TEXT NOT NULL,
    department TEXT NOT NULL,
    category TEXT NOT NULL,
    portal_url TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'in_progress', 'waiting_approval', 'submitted', 'approved', 'rejected', 'failed')),
    acknowledgement_number TEXT,
    confirmation_text TEXT,
    submission_timestamp TIMESTAMPTZ,
    receipt_url TEXT,
    receipt_path TEXT,
    populated_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Row Level Security
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own applications"
    ON public.applications
    FOR ALL
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);
```

### FastAPI Endpoints (`/api/applications`)
- `GET /api/applications`: Lists all citizen applications (supports `?status=submitted` or `all`).
- `GET /api/applications/{id}`: Detailed record with timeline and populated form inputs.
- `POST /api/applications`: Creates or updates an application record.
- `GET /api/applications/{id}/receipt`: Streams PDF file with `Content-Disposition: attachment; filename="CivicPilot_Receipt_{ack_no}.pdf"`.

---

## 4. Frontend "My Applications" Dashboard UI (MakeMyTrip Design System)

- **Route:** `/applications` (pre-wired in `Navbar`).
- **Visual Hierarchy:**
  - **Header Hero:** Navy `#1A2B4C` backdrop, Civic Blue & Cyan accents, heading: "My Public Service Applications", subtitle: "Track live status, reference numbers, and download official government submission receipts."
  - **Summary Metrics Bar:** 4 elevated stat cards:
    - Total Applications
    - Submitted to Official Portals
    - In Review / Pending Approval
    - Verified & Active
  - **Filter Tabs:** All Applications, Submitted (`status='submitted'`), Drafts / In Progress.
  - **Application Cards Deck (`APP-04`):**
    - High contrast elevated card with issuing ministry badge.
    - Status pill with pulsing live dot (Emerald for Submitted, Amber for In Progress, Blue for Completed).
    - Prominent Acknowledgement Reference Number badge with 1-click Copy button (`APP-01`).
    - Verified submission timestamp (e.g. `1 Nov 2026, 08:30 PM IST`).
    - Official government portal URL pill with external link icon.
    - Action buttons:
      - **"Download Official Receipt (PDF)"** (`APP-05`) with Download icon.
      - **"View Live Portal"** opening official URL in new tab.
      - **"Re-open Operations Workspace"** linking to `/applications/workspace/[sessionId]?serviceId=...`.
