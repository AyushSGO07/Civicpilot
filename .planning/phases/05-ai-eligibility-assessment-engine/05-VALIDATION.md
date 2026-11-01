# Phase 05: AI Eligibility Assessment Engine — Validation Plan

## Test Strategy

Phase 05 introduces the AI eligibility assessment engine powered by Gemini 2.5 Flash with deterministic fallback logic and an interactive detail page at `/services/[serviceId]`.

Validation consists of:
1. Automated backend pytest tests (`backend/tests/test_eligibility.py`) covering all scenarios:
   - Full eligibility match (`Likely Eligible`).
   - Criteria violation (`Likely Ineligible`).
   - Missing required profile attributes (`More Information Required`).
   - Official citation presence on each criterion.
   - Non-existent service ID returning 404.
   - Bearer token / citizen profile extraction.
2. Full backend test regression verification (`pytest backend/tests/ -v`).
3. Next.js App Router static compilation and TypeScript verification (`npm --prefix frontend run build`).

---

## Backend Test Cases (`backend/tests/test_eligibility.py`)

| Test Name | Test Condition | Expected Result |
|---|---|---|
| `test_evaluate_eligible_citizen` | Citizen profile with income ₹2.5L, Undergraduate student evaluating PM-USP scholarship | `status == "Likely Eligible"`, all criteria `Satisfied`, confidence >= 0.9, citations present |
| `test_evaluate_ineligible_high_income` | Citizen profile with annual income ₹8.0L evaluating PM-USP scholarship (max ₹4.5L) | `status == "Likely Ineligible"`, income criterion `Not Satisfied`, citation references Section 3.2 |
| `test_evaluate_missing_information` | Incomplete citizen profile (null income, null education) evaluating PM-USP | `status == "More Information Required"`, missing fields reported (`annual_income`, `education_level`) |
| `test_evaluate_service_not_found` | Invalid service UUID or slug (e.g. `non-existent-scheme-999`) | HTTP 404 with detail message |
| `test_official_citations_present` | Any valid scheme evaluation | Every element in `criteria` has non-empty `official_citation` |
| `test_statutory_disclaimer_present` | Any valid scheme evaluation | Response contains official disclaimer indicating legal final authority rests with the government department |

---

## Acceptance Criteria Checklist

- [ ] `backend/tests/test_eligibility.py` passes 100% of test cases.
- [ ] Overall backend test suite (profile, documents, services, eligibility) passes without failures or warnings.
- [ ] Frontend page `/services/[serviceId]` builds cleanly with Next.js App Router (`npm --prefix frontend run build`).
- [ ] No regressions in existing routes (`/`, `/services`, `/profile`, `/documents`, `/auth`).
