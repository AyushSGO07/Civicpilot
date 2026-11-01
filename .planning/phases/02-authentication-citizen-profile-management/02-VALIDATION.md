---
phase: 2
slug: authentication-citizen-profile-management
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-11-01
---

# Phase 02 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend) + Next.js build (frontend) |
| **Config file** | `backend/pytest.ini` & `frontend/tsconfig.json` |
| **Quick run command** | `pytest backend/tests/test_profile.py` |
| **Full suite command** | `pytest backend/tests/ && npm --prefix frontend run build` |
| **Estimated runtime** | ~8 seconds |

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
| 02-01-01 | 01 | 1 | AUTH-01, AUTH-02 | unit / schema | `pytest backend/tests/test_profile.py` | ⬜ pending |
| 02-02-01 | 02 | 2 | AUTH-01, AUTH-02, AUTH-03, AUTH-04 | build / integration | `npm --prefix frontend run build` | ⬜ pending |
| 02-03-01 | 03 | 2 | PROF-01, PROF-02, PROF-03, PROF-04, PROF-05 | unit / build | `pytest backend/tests/test_profile.py && npm --prefix frontend run build` | ⬜ pending |

---

## Wave 0 Requirements

- [ ] `backend/tests/test_profile.py` — automated test for profile schema & endpoints
- [ ] `frontend/lib/supabase.ts` — Supabase client configuration
- [ ] `database/schema.sql` — PostgreSQL DDL for `citizen_profiles` with RLS

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Auth modal toggle | AUTH-01 | Visual interactive UX | Toggle between Sign In and Create Account tabs on `/auth` |
| Profile field validation | PROF-05 | Client UX | Enter invalid PIN code (<6 digits) and verify validation warning |

---

## Validation Sign-Off

- [x] All tasks have automated verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-11-01
