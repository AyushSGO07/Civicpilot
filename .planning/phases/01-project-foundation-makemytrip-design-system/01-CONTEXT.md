# Phase 01: Project Foundation & MakeMyTrip Design System - Context

**Gathered:** 2026-11-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Establishes the foundational dual-stack development environment and user experience foundation for CivicPilot:
1. Next.js 15 App Router frontend in `frontend/` initialized with TypeScript, Tailwind CSS, shadcn/ui, Lucide React, and Framer Motion.
2. The MakeMyTrip-inspired visual design system: deep navy (`#1A2B4C`), vibrant blue (`#0056D2`), cyan accent, light grey (`#F5F7FB`) page background, and card styling.
3. Responsive global navigation bar with links to Home, Explore Services, My Applications, Document Vault, and Profile.
4. Hero discovery section with natural language search input, example query chips, and category quick tabs.
5. FastAPI backend structure in `backend/` with modular routers, CORS middleware, and an operational `/api/health` health-check endpoint.

</domain>

<decisions>
## Implementation Decisions

### Design System & Theme Tokens
- **D-01:** Implement MakeMyTrip semantic tokens directly in `frontend/tailwind.config.ts` and CSS variables:
  - Primary Brand Navy: `#1A2B4C`
  - Action Vibrant Blue: `#0056D2`
  - Accent Cyan: `#00B4D8` / `#0077B6`
  - Canvas Background: `#F5F7FB`
  - Card Surfaces: Pure white `#FFFFFF` with subtle border `#E5E9F2` and soft shadows
  - Typography: Inter or Plus Jakarta Sans
  — **Reversibility:** costly — changing design tokens later requires refactoring shared component styles.

### Global Layout & Navigation
- **D-02:** Build a sticky responsive navbar with CivicPilot branding:
  - Brand identity: CivicPilot logo mark with tagline pill
  - Primary navigation links: Home (`/`), Explore Services (`/services`), My Applications (`/applications`), Document Vault (`/documents`)
  - User profile menu trigger and AI Assistant badge
  — **Reversibility:** reversible — component-level layout.

### Hero & Discovery Experience
- **D-03:** Construct a MakeMyTrip-style high-intent discovery Hero:
  - Headline: "Your Government Work, Simplified."
  - Subheading: "Discover services, check eligibility, and let AI handle the paperwork."
  - Natural language search bar with interactive example chips (e.g. "Scholarships for engineering", "Driving licence renewal")
  - Category quick-filter tabs: Education, Scholarships, Identity & Documents, Transport, Agriculture, Healthcare, Business & MSME, Financial Assistance
  — **Reversibility:** reversible — modular page composition.

### Backend Project Architecture
- **D-04:** Establish modular FastAPI structure under `backend/app/`:
  - `main.py`: ASGI application lifecycle, CORS middleware, and router mounts
  - `config.py`: Environment settings (Pydantic `BaseSettings`)
  - `routers/`: Modular route files (`health.py`, `auth.py`, `profile.py`, `documents.py`, `services.py`, `agent.py`, `ws.py`)
  - `models/`: Shared Pydantic domain models
  - Health endpoint at `GET /api/health` returning `{status: "ok", service: "CivicPilot API", version: "1.0.0"}`
  — **Reversibility:** costly — sets routing conventions and interface patterns for all subsequent phases.

### Development Environment & CORS
- **D-05:** Configure CORS in FastAPI for `http://localhost:3000` (Next.js development server) and define frontend environment variable `NEXT_PUBLIC_API_URL=http://localhost:8000`.
  — **Reversibility:** reversible — configuration parameter.

### Antigravity's Discretion
- Exact spacing, border-radius constants (`rounded-xl`), and micro-animation transition curves (Framer Motion spring presets) are left to engineering discretion adhering to MakeMyTrip visual quality.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Product & Design Specifications
- `specs.md` §1 — Project Overview, Vision & Core Value
- `specs.md` §2 — Design Direction, MakeMyTrip UI/UX Inspiration, and Palette
- `specs.md` §7 — Technical Architecture (Frontend & Backend Stack)
- `specs.md` §12 — API Structure & Endpoints

### Planning & Research
- `.planning/research/STACK.md` — Prescribed versions (Next.js 15, React 19, FastAPI, Tailwind, shadcn)
- `.planning/research/ARCHITECTURE.md` — Dual-stack directory structure and component hierarchy
- `.planning/REQUIREMENTS.md` — UI-01, UI-02, UI-03, UI-04

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Greenfield codebase; Phase 1 establishes the root foundational assets for the entire platform.

### Established Patterns
- Dual-stack repository: `frontend/` (Next.js App Router) and `backend/` (FastAPI).
- MakeMyTrip travel-grade UI pattern: high contrast cards, bold search hero, vibrant blue CTAs on light background.

### Integration Points
- Frontend client communicating with FastAPI backend via REST (`NEXT_PUBLIC_API_URL/api/health`).

</code_context>

<specifics>
## Specific Ideas

- The discovery card interface should evoke the polish and clarity of MakeMyTrip flight/hotel booking cards, making government schemes feel accessible, transparent, and modern.

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within Phase 1 scope.

</deferred>

---

*Phase: 01-Project-Foundation-MakeMyTrip-Design-System*
*Context gathered: 2026-11-01*
