# Walking Skeleton — CivicPilot

**Phase:** 1
**Generated:** 2026-11-01

## Capability Proven End-to-End

A user opening CivicPilot at `http://localhost:3000` experiences the MakeMyTrip-inspired consumer discovery interface (deep navy, vibrant blue, cyan accents), navigates across 8 category filter tabs, and confirms end-to-end full-stack connectivity with the FastAPI backend at `http://localhost:8000/api/health`.

## Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Frontend Framework | Next.js 15 (App Router) + React 19 | Production SSR/SSG, fast routing, optimal hydration for real-time agent updates. |
| Styling & Theme | Tailwind CSS + shadcn/ui + CSS Variables | Rapid MakeMyTrip design system implementation with semantic color tokens. |
| Backend Framework | FastAPI (Python 3.11+) | Asynchronous ASGI runtime native to Playwright automation and WebSocket streaming. |
| API Contract | REST JSON with CORS | Standard decoupled client-server architecture with direct CORS during local development. |
| Directory Layout | `frontend/` and `backend/` dual-stack | Complete isolation of Node.js frontend tooling and Python backend virtual environment. |

## Stack Touched in Phase 1

- [ ] Project scaffold (Next.js 15 App Router, TypeScript, Tailwind CSS, FastAPI, Uvicorn, pytest)
- [ ] Routing — Root landing page (`/`) and FastAPI health route (`/api/health`)
- [ ] UI — Responsive MakeMyTrip navigation bar, Hero search bar, and 8 interactive category quick tabs
- [ ] Backend — Modular FastAPI application structure with CORS middleware and Pydantic health response
- [ ] Full-Stack Run — Documented dev run commands for both frontend and backend

## Out of Scope (Deferred to Later Slices)

- Supabase Auth registration and login (Phase 2)
- Citizen profile persistent database tables (Phase 2)
- Encrypted Document Vault storage and OCR (Phase 3)
- Live Playwright browser launching (Phase 6)
- LangGraph agent loop (Phase 8)

## Subsequent Slice Plan

Each later phase adds one vertical capability on top of this skeleton:
- Phase 2: Citizen Authentication & Profile Management
- Phase 3: Secure Document Vault & Multimodal OCR Extraction
- Phase 4: Live Government Scheme Discovery & Search
- Phase 5: AI Eligibility Assessment Engine
- Phase 6: Playwright Browser Automation Core & DOM Inspection
- Phase 7: Dynamic Field Mapping & Form Filling Engine
- Phase 8: LangGraph Workflow Orchestration & Bounded Recovery
- Phase 9: Real-time Agent Execution Workspace & WebSockets
- Phase 10: Human-in-the-Loop Approval & Security Checkpoints
- Phase 11: Submission Verification, Receipt Retrieval & Application Tracking
- Phase 12: End-to-End Integration, Demonstration Polish & Production Hardening
