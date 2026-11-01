---
phase: 3
slug: secure-document-vault-multimodal-ocr-extraction
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-11-01
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend) + Next.js build (frontend) |
| **Config file** | `backend/pytest.ini` & `frontend/tsconfig.json` |
| **Quick run command** | `pytest backend/tests/test_documents.py` |
| **Full suite command** | `pytest backend/tests/ && npm --prefix frontend run build` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before verification report:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 03-01-01 | 01 | 1 | DOC-01, DOC-05 | schema / unit | `pytest backend/tests/test_documents.py` | ⬜ pending |
| 03-01-02 | 01 | 1 | DOC-01, DOC-02, DOC-05 | api / integration | `pytest backend/tests/test_documents.py` | ⬜ pending |
| 03-02-01 | 02 | 2 | DOC-01, DOC-02, DOC-05 | frontend / build | `npm --prefix frontend run build` | ⬜ pending |
| 03-03-01 | 03 | 2 | DOC-03, DOC-04 | ocr / integration | `pytest backend/tests/test_documents.py && npm --prefix frontend run build` | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `database/schema.sql` — Add `public.documents` table with RLS
- [ ] `backend/app/routers/documents.py` — Upload, list, preview, and delete endpoints
- [ ] `backend/tests/test_documents.py` — Test suite for document storage and OCR
- [ ] `frontend/app/documents/page.tsx` — Document Vault UI

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Drag and drop file upload | DOC-01 | Browser mouse event | Drag file into dropzone on `/documents` and verify upload trigger |
| PDF/Image modal preview | DOC-02 | Interactive viewer | Click "Preview" button on uploaded card and inspect modal viewport |
| OCR diff verification modal | DOC-04 | Visual review UX | Click "Run AI OCR", verify extracted table, check/uncheck fields and sync |

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-11-01
