---
phase: "03"
name: "secure-document-vault-multimodal-ocr-extraction"
created: 2026-11-01
---

# Phase 03: Secure Document Vault & Multimodal OCR Extraction — Context

## User Constraints

### Locked Decisions
- **D-01 (Document Storage & Security):** Documents must be stored in protected private storage (Supabase Storage bucket `citizen-vault` or encrypted local server directory fallback) and accessed only via short-lived signed URLs. Raw document files must never be publicly accessible or leaked via unauthenticated public URLs (specs.md §3.4 & §11).
- **D-02 (Database Schema & RLS):** Create `public.documents` table linked to `auth.users(id)` with fields for document name, type, mime type, size, storage path, JSONB extracted fields, and verification status. Strict Row Level Security policies enforce user isolation (`auth.uid() = user_id`).
- **D-03 (FastAPI Document Endpoints):** Implement modular `backend/app/routers/documents.py` with endpoints for upload (`POST /api/documents/upload`), list (`GET /api/documents`), metadata & signed URL (`GET /api/documents/{id}`), deletion (`DELETE /api/documents/{id}`), OCR analysis (`POST /api/documents/{id}/ocr`), and profile sync (`POST /api/documents/{id}/confirm`).
- **D-04 (Gemini Multimodal OCR Extraction):** Use the official Google GenAI SDK (`google-genai`) with `gemini-2.5-flash` to extract structured citizen profile attributes from PDF, JPG, and PNG documents (Aadhaar, PAN, marksheets, income/caste certificates). Provide a deterministic OCR fallback when offline or in test environments.
- **D-05 (MakeMyTrip Document Vault UI):** Build `/documents` page featuring MakeMyTrip aesthetic (Navy `#1A2B4C`, Blue `#0056D2`, Cyan `#00B4D8`, Canvas `#F5F7FB`), elevated document cards, category filters, upload dropzone, document preview modal, and interactive OCR verification modal with 1-click sync to citizen profile.
- **D-06 (Integrity & Human Verification):** Zero dummy data. No fabricated documents or synthetic OCR results. The citizen retains explicit human-in-the-loop control to review, edit, or reject extracted fields before committing them to their profile.

### Discretion Areas
- Document types supported (Aadhaar Card, PAN Card, Income Certificate, Caste Certificate, Domicile Certificate, Academic Marksheet, Bonafide Certificate, Passport-size Photo, Bank Passbook/Statement).
- OCR extraction field mapping per document type (e.g., Aadhaar extracts name, DOB, gender, address; Marksheet extracts institution, course, academic score).
- Upload file size limits (up to 10MB per file) and supported MIME types (`application/pdf`, `image/jpeg`, `image/png`).

### Deferred Ideas
- Digilocker API automatic document pull (v2 requirement INT-01).
- Client-side WebAssembly OCR as offline backup (v2).
