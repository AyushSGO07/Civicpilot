# Phase 04: Live Government Scheme Discovery & Search — Research

**Researched:** 2026-11-01
**Domain:** Government Scheme Catalog, Full-Text & Category Search, FastAPI Endpoints, MakeMyTrip Service Discovery Deck
**Confidence:** HIGH

---

## 1. Architectural Strategy

Phase 4 delivers the single source of truth for government service discovery.
Official government schemes ingested into CivicPilot provide the bedrock for:
1. Scheme browsing and natural language discovery (Phase 4).
2. AI eligibility evaluation against user profiles (Phase 5).
3. Browser automation portal workflows (Phases 6–8).

```
                      Browser (Next.js 15)
                               │
               GET /services?q=...&category=...
                               │
                               ▼
                    FastAPI /api/services
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
       PostgreSQL Database           In-Memory Verified Cache
   (public.government_services)      (8 Official Seed Schemes)
```

---

## 2. Official Government Scheme Sources (Zero Dummy Data)

Every service in CivicPilot originates from an authoritative Indian government portal:

| Scheme Name | Department / Ministry | Category | Official Source & Application URLs |
|-------------|-----------------------|----------|-----------------------------------|
| **Central Sector Scholarship (PM-USP)** | Ministry of Education, Dept of Higher Education | Scholarships / Education | Source: `https://www.myscheme.gov.in/schemes/pm-usp`<br>App: `https://scholarships.gov.in/` |
| **PM-KISAN (Kisan Samman Nidhi)** | Ministry of Agriculture and Farmers Welfare | Agriculture / Financial | Source: `https://pmkisan.gov.in/`<br>App: `https://pmkisan.gov.in/RegistrationFormNew.aspx` |
| **Ayushman Bharat (PM-JAY)** | National Health Authority, MoHFW | Healthcare | Source: `https://pmjay.gov.in/`<br>App: `https://beneficiary.nha.gov.in/` |
| **Post-Matric Scholarship for SC Students** | Ministry of Social Justice and Empowerment | Scholarships | Source: `https://www.myscheme.gov.in/schemes/pmsss-sc`<br>App: `https://scholarships.gov.in/` |
| **PMEGP (MSME Employment Generation)** | Ministry of Micro, Small and Medium Enterprises | Business & MSME | Source: `https://www.kviconline.gov.in/pmegpeportal/`<br>App: `https://www.kviconline.gov.in/pmegpeportal/jsp/pmegponline.jsp` |
| **Sarathi Parivahan Driving Licence** | Ministry of Road Transport and Highways (MoRTH) | Transport / Identity | Source: `https://parivahan.gov.in/parivahan/`<br>App: `https://sarathi.parivahan.gov.in/sarathiservice/stateSelection.do` |
| **National Apprenticeship (NAPS)** | Ministry of Skill Development and Entrepreneurship | Education / MSME | Source: `https://www.apprenticeshipindia.gov.in/`<br>App: `https://www.apprenticeshipindia.gov.in/candidate-registration` |
| **PMAY-U (Housing for All Urban)** | Ministry of Housing and Urban Affairs | Financial Assistance | Source: `https://pmay-urban.gov.in/`<br>App: `https://pmaymis.gov.in/` |

---

## 3. Database Schema: `public.government_services`

```sql
CREATE TABLE IF NOT EXISTS public.government_services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name TEXT NOT NULL,
    department TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'Education', 'Scholarships', 'Identity & Documents', 'Transport',
        'Agriculture', 'Healthcare', 'Business & MSME', 'Financial Assistance', 'Other'
    )),
    state TEXT DEFAULT 'Central',
    eligibility_summary TEXT NOT NULL,
    eligibility_criteria JSONB DEFAULT '{}'::jsonb,
    required_documents TEXT[] DEFAULT ARRAY[]::TEXT[],
    official_source_url TEXT NOT NULL,
    official_application_url TEXT NOT NULL,
    application_deadline TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Public read access
ALTER TABLE public.government_services ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view active government services"
    ON public.government_services FOR SELECT
    USING (is_active = TRUE);
```

---

## 4. Search and Ranking Engine

The search endpoint `GET /api/services` performs:
1. **Query Matching (`q`):** Case-insensitive tokenized matching over `service_name`, `department`, `description`, `eligibility_summary`, and `category`.
2. **Category Filter (`category`):** Exact or mapped filter matching.
3. **State Filter (`state`):** Matches either `Central` (nationwide) or user-specified state.
4. **Relevance Scoring:** Schemes matching the query in their title rank higher than description-only matches.
