# Phase 01: Project Foundation & MakeMyTrip Design System - Research

**Researched:** 2026-11-01
**Domain:** Next.js 15 App Router, Tailwind CSS Design System, FastAPI REST API
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01 (MakeMyTrip Theme Tokens):** Deep navy (`#1A2B4C`), vibrant blue (`#0056D2`), cyan accent (`#00B4D8`), canvas background (`#F5F7FB`), and crisp white card styling configured in `tailwind.config.ts` and CSS variables.
- **D-02 (MakeMyTrip Navigation Bar):** Sticky responsive header displaying CivicPilot branding, navigation links (Home, Explore Services, My Applications, Document Vault), and profile/AI badge.
- **D-03 (Unified Discovery Hero):** High-intent travel-grade search interface with natural language input, example query chips, and 8 category quick-filter tabs.
- **D-04 (Modular FastAPI Structure):** `backend/app/` with `main.py`, `routers/` (`health.py`, `auth.py`, `profile.py`, etc.), `models/`, `config.py`, and `/api/health` endpoint.
- **D-05 (CORS & Direct REST):** FastAPI CORS enabled for `http://localhost:3000` with `NEXT_PUBLIC_API_URL=http://localhost:8000`.

### Antigravity's Discretion
- Micro-interaction transitions (Framer Motion spring curves), exact card border-radius values (`rounded-xl`), and responsive sheet layout.

### Deferred Ideas (OUT OF SCOPE)
- None — all decisions remain strictly within Phase 1 foundation scope.
</user_constraints>

<architectural_responsibility_map>
## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Next.js App Shell & Design System | Browser / Client | Frontend Server (SSR) | React 19 concurrent client components for interactive tabs; SSR for SEO and fast initial paint. |
| Global Navbar & Hero Search UI | Browser / Client | — | Client-side reactive state for active category filters and query auto-suggest. |
| FastAPI Application Gateway | API / Backend | — | Python ASGI server hosting business logic, session validation, and health checks. |
| Development CORS Proxy & Config | API / Backend | Frontend Server | Enables direct browser-to-FastAPI communication during local development. |
</architectural_responsibility_map>

<research_summary>
## Summary

Phase 1 establishes the structural and visual foundation for CivicPilot. The frontend leverages Next.js 15 (App Router) with Tailwind CSS, shadcn/ui primitives, and Lucide React to create the MakeMyTrip-inspired consumer discovery experience. The visual hierarchy utilizes deep navy (`#1A2B4C`) for authoritative brand presence, vibrant blue (`#0056D2`) for high-contrast primary actions, cyan accents for live badges, and an off-white canvas (`#F5F7FB`) with white elevated cards.

The backend is built with FastAPI (Python 3.11+), structured with modular APIRouters under `backend/app/routers/` to ensure clean separation of concerns as the project scales across 12 phases. A root health check (`GET /api/health`) verifies end-to-end network connectivity and CORS headers.

**Primary recommendation:** Initialize the dual-stack workspace (`frontend/` and `backend/`) with strict typing, custom Tailwind theme tokens matching the MakeMyTrip palette, and an operational `/api/health` route tested via automated requests.
</research_summary>

<standard_stack>
## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | 15.x | App Router & React Framework | Standard for SSR, client interactivity, and routing. |
| React | 19.x | UI Runtime | Concurrent rendering, native actions, optimal hydration. |
| Tailwind CSS | 3.4+ / 4.x | Utility-First Styling | Rapid design token composition and atomic CSS output. |
| shadcn/ui & Radix UI | Latest | Accessible UI Primitives | Accessible headless primitives styled directly with Tailwind. |
| FastAPI | 0.115+ | Python ASGI Framework | High performance, auto-generated OpenAPI docs, async native. |
| Uvicorn | 0.32+ | ASGI Server Worker | Production-grade async server for FastAPI. |
| Pydantic | 2.10+ | Schema Validation | Ultra-fast data parsing using Pydantic v2 Core. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Lucide React | Latest | Consumer Iconography | Navigation icons, category tab indicators, status badges. |
| clsx & tailwind-merge | Latest | Class Name Utility | Conditional CSS class merging in shadcn components. |
| httpx | 0.28+ | Async HTTP Client | Python health and integration verification tests. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Next.js App Router | Vite React SPA | Next.js selected for superior SEO, routing, and integrated SSR. |
| FastAPI | Flask / Express | FastAPI provides native async event loop needed for Playwright and WebSockets. |

**Installation:**
```bash
# Frontend
cd frontend
npm install lucide-react clsx tailwind-merge framer-motion

# Backend
cd ../backend
pip install fastapi "uvicorn[standard]" pydantic pydantic-settings httpx pytest
```
</standard_stack>

<architecture_patterns>
## Architecture Patterns

### Recommended Project Structure
```
CivicPilot/
├── frontend/
│   ├── app/
│   │   ├── layout.tsx         # Root layout with theme & navbar
│   │   ├── page.tsx           # MakeMyTrip Discovery Landing Page
│   │   └── globals.css        # CSS variables & theme tokens
│   ├── components/
│   │   ├── navbar.tsx         # Global sticky header
│   │   ├── hero-search.tsx    # Natural language search + category tabs
│   │   └── ui/                # shadcn primitives (button, card, input, badge)
│   ├── lib/
│   │   └── utils.ts           # cn helper function
│   ├── tailwind.config.ts     # MakeMyTrip color palette & tokens
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entry point & CORS
│   │   ├── config.py          # App settings via pydantic-settings
│   │   └── routers/
│   │       ├── __init__.py
│   │       └── health.py      # /api/health endpoint
│   ├── requirements.txt
│   └── tests/
│       └── test_health.py     # Backend health verification test
├── .planning/
└── specs.md
```

### Pattern 1: MakeMyTrip CSS Variables & Tailwind Extension
```css
/* frontend/app/globals.css */
:root {
  --background: 220 27% 97%; /* #F5F7FB */
  --foreground: 220 40% 15%; /* #1A2B4C */
  --card: 0 0% 100%;         /* #FFFFFF */
  --card-foreground: 220 40% 15%;
  --primary: 215 100% 41%;   /* #0056D2 - Vibrant Blue */
  --primary-foreground: 0 0% 100%;
  --accent: 191 100% 42%;    /* #00B4D8 - Cyan */
  --accent-foreground: 0 0% 100%;
  --border: 220 20% 90%;     /* #E5E9F2 */
}
```

### Pattern 2: Modular FastAPI Router Initialization
```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health

app = FastAPI(title="CivicPilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["System"])
```

### Anti-Patterns to Avoid
- Hardcoding colors with arbitrary hex values in components instead of using theme semantic tokens (`bg-primary`, `bg-canvas`, `text-navy`).
- Putting all API routes in a single monolithic `main.py` file.
- Mixing client and server rendering incorrectly in Next.js 15 (mark interactive components with `'use client'`).
</architecture_patterns>

<dont_hand_roll>
## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Headless accessibility | Custom ARIA dropdowns & modals | Radix UI / shadcn/ui | Keyboard navigation, focus trapping, screen reader compliance are complex. |
| CORS negotiation | Custom ASGI header injector | `fastapi.middleware.cors.CORSMiddleware` | Handles preflight `OPTIONS` requests and origin credentials reliably. |
| Class merging | String concatenation (`"btn " + variant`) | `clsx` + `tailwind-merge` (`cn()`) | Resolves Tailwind specificity collisions safely. |
</dont_hand_roll>

<common_pitfalls>
## Common Pitfalls

### Pitfall 1: Next.js 15 Client/Server Component Boundary Errors
**What goes wrong:** Using React state or hooks (`useState`, `useRouter`) in server components throws hydration errors.
**How to avoid:** Add `'use client';` directive to interactive components (`navbar.tsx`, `hero-search.tsx`).

### Pitfall 2: CORS Preflight Failures on Localhost
**What goes wrong:** Next.js fetch requests fail with `No 'Access-Control-Allow-Origin' header is present`.
**How to avoid:** Explicitly include `http://localhost:3000` and `http://127.0.0.1:3000` in FastAPI `allow_origins`.

### Pitfall 3: Visual Inconsistency with MakeMyTrip Design
**What goes wrong:** Generic grey-on-white appearance lacking travel-grade brand polish.
**How to avoid:** Consistently pair `#1A2B4C` deep navy with `#0056D2` vibrant blue and `#F5F7FB` background cards.
</common_pitfalls>

<code_examples>
## Code Examples

### Health Check Endpoint
```python
# backend/app/routers/health.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

@router.get("/health", response_model=HealthResponse)
async def get_health():
    return HealthResponse(
        status="ok",
        service="CivicPilot API",
        version="1.0.0"
    )
```
</code_examples>

## Validation Architecture

### Test Infrastructure
- **Frontend Validation:** `npm run build` in `frontend/` (TypeScript type check + ESLint).
- **Backend Validation:** `pytest` in `backend/` testing `GET /api/health` with `httpx.AsyncClient`.
- **E2E Smoke Verification:** `curl http://localhost:8000/api/health` returns `200 OK` with JSON status.

<sources>
### Primary (HIGH confidence)
- Official Next.js Documentation: https://nextjs.org/docs
- Official FastAPI Documentation: https://fastapi.tiangolo.com/
- shadcn/ui Theming Guide: https://ui.shadcn.com/docs/theming
</sources>

<metadata>
**Confidence:** HIGH
**Valid until:** 2026-12-01
</metadata>

---
*Phase: 01-project-foundation-makemytrip-design-system*
*Research completed: 2026-11-01*
*Ready for planning: yes*
