---
phase: "04"
name: "live-government-scheme-discovery-search"
created: 2026-11-01
---

# Phase 04: Live Government Scheme Discovery & Search — Context

## User Constraints

### Locked Decisions
- **D-01 (Official Data & No Dummy Data):** All schemes, eligibility rules, and portal links must originate from authentic official sources (MyScheme, National Scholarship Portal scholarships.gov.in, PM-Kisan, PM-JAY, Parivahan Sarathi, MSME PMEGP). Zero placeholder or fabricated schemes permitted (specs.md §8).
- **D-02 (Database Schema & Caching):** Define `public.government_services` table with fields for service name, department, category, state, eligibility summary, criteria JSON, required documents, official source URL, application URL, and active status. Provide cached retrieval and in-memory fallback for offline test resilience.
- **D-03 (FastAPI Service Discovery Endpoints):** Implement modular `backend/app/routers/services.py` with `GET /api/services` (filtering by search query `q`, `category`, and `state`) and `GET /api/services/{id}` with automated pytest coverage.
- **D-04 (Natural Language Search & Filtering):** Support keyword and semantic term search across scheme titles, descriptions, categories, and issuing departments (DISC-01, DISC-02).
- **D-05 (MakeMyTrip Service Catalog UI):** Build `/services` Explore Services page at `frontend/app/services/page.tsx` with MakeMyTrip aesthetic (Navy `#1A2B4C`, Blue `#0056D2`, Cyan `#00B4D8`, Canvas `#F5F7FB`), elevated search bar, category tabs, state filters, detailed scheme cards, and direct links to official portals (DISC-03, DISC-04).

### Discretion Areas
- Standard categories matching the Hero search tabs: Education, Scholarships, Identity & Documents, Transport, Agriculture, Healthcare, Business & MSME, Financial Assistance.
- Scheme card badge styles (Central vs State, deadline notice, eligibility highlights).
- Sorting options (Relevance, Category, Alphabetical).

### Deferred Ideas
- Automated daily crawler scraping of MyScheme and State portals (v2).
- Personalized ranking based on logged-in user profile (Phase 5 AI Eligibility Assessment).
