---
phase: 1
slug: project-foundation-makemytrip-design-system
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-11-01
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x (backend) + npm run build (frontend) |
| **Config file** | `backend/pytest.ini` & `frontend/tsconfig.json` |
| **Quick run command** | `pytest tests/test_health.py` (in `backend/`) |
| **Full suite command** | `pytest && npm --prefix ../frontend run build` |
| **Estimated runtime** | ~6 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | UI-01 | — | N/A | build | `npm --prefix frontend run build` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 2 | UI-02, UI-03, UI-04 | — | N/A | build | `npm --prefix frontend run build` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 1 | UI-01 | — | N/A | integration | `pytest backend/tests/test_health.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `backend/tests/test_health.py` — automated test for `/api/health`
- [ ] `backend/requirements.txt` — includes pytest and httpx
- [ ] `frontend/package.json` — includes build script

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| MakeMyTrip visual aesthetic | UI-01 | Visual design evaluation | Open `http://localhost:3000`, verify deep navy header, vibrant blue CTA, cyan badge, and light background. |
| Hero category tab hover/active | UI-03 | Interaction fluidity | Click across category tabs, verify active blue indicator line moves smoothly. |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-11-01
