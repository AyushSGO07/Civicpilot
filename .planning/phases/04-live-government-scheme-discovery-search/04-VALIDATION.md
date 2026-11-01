---
phase: 4
slug: live-government-scheme-discovery-search
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-11-01
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend) + Next.js build (frontend) |
| **Config file** | `backend/pytest.ini` & `frontend/tsconfig.json` |
| **Quick run command** | `pytest backend/tests/test_services.py` |
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
| 04-01-01 | 01 | 1 | DISC-01, DISC-02 | schema / unit | `pytest backend/tests/test_services.py` | ⬜ pending |
| 04-01-02 | 01 | 1 | DISC-01, DISC-02, DISC-03, DISC-04 | api / search | `pytest backend/tests/test_services.py` | ⬜ pending |
| 04-02-01 | 02 | 2 | DISC-01, DISC-02, DISC-03, DISC-04 | frontend / build | `npm --prefix frontend run build` | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `database/schema.sql` — Add `public.government_services` table with RLS
- [ ] `backend/app/models/service.py` — Service and search schemas
- [ ] `backend/app/services/scheme_search.py` — Official seed dataset and search filter engine
- [ ] `backend/app/routers/services.py` — API routes for listing and searching services
- [ ] `backend/tests/test_services.py` — Automated tests for scheme search and retrieval
- [ ] `frontend/app/services/page.tsx` — Explore Services page

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Official portal link click | DISC-04 | External window navigation | Click "Official Portal" link on card and verify new tab opens `gov.in` domain |
| Dynamic category pill filter | DISC-02 | Client UI interaction | Click "Agriculture" tab on `/services` and verify PM-KISAN appears |

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-11-01
