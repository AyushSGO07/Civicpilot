---
phase: "05"
name: "ai-eligibility-assessment-engine"
created: 2026-11-01
---

# Phase 05: AI Eligibility Assessment Engine — Context

## User Constraints

### Locked Decisions
- **D-01 (Eligibility Reasoning with Citations):** Build an automated AI evaluation engine using the official Google GenAI SDK (`google-genai`) with `gemini-2.5-flash` to evaluate citizen profile data against official scheme requirements. Every evaluation must produce one of three official statuses: `Likely Eligible`, `Likely Ineligible`, or `More Information Required` (ELIG-01, ELIG-02).
- **D-02 (Itemized Breakdown & Official Citations):** Return an itemized comparison matrix showing the official scheme condition, the citizen's actual profile value, evaluation status (`Satisfied`, `Not Satisfied`, `Missing Info`), and specific citations to authoritative guidelines (ELIG-03, ELIG-05).
- **D-03 (Missing Fields Prompting):** Explicitly identify incomplete or missing citizen attributes (e.g. undisclosed income, missing caste category, unverified marksheet) and provide actionable guidance to complete them in `/profile` (ELIG-04).
- **D-04 (FastAPI Eligibility Endpoint):** Implement modular `POST /api/services/{service_id}/evaluate` in FastAPI with authenticated citizen profile extraction and deterministic rule-based fallback for test/offline resilience.
- **D-05 (MakeMyTrip Eligibility UI & Detail Page):** Build `/services/[serviceId]/page.tsx` with MakeMyTrip aesthetic (Navy `#1A2B4C`, Blue `#0056D2`, Cyan `#00B4D8`, Canvas `#F5F7FB`), featuring scheme details, real-time eligibility evaluation card, criteria comparison table, and CTA to launch autonomous application execution.
- **D-06 (Advisory Disclaimer):** AI assessment must always display an explicit advisory disclaimer that evaluations are based on official guidelines and provided profile data, while final legal determination is made by the official government issuing authority (specs.md §3.6).

### Discretion Areas
- Criteria weighting and threshold handling (e.g., income limits <= ₹4.5 lakh, age boundaries).
- Layout arrangement of the criteria breakdown (accordion vs card matrix).
- Direct link from "Missing Info" prompt into specific sections of `/profile`.

### Deferred Ideas
- Cross-scheme portfolio eligibility optimizer (evaluating all 8 schemes simultaneously on profile save - v2).
- Real-time Digilocker certificate verification (v2 requirement INT-01).
