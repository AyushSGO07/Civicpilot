# Phase 01: Project Foundation & MakeMyTrip Design System - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-11-01
**Phase:** 01-project-foundation-makemytrip-design-system
**Areas discussed:** Design System & Theme Tokens, Global Layout & Navigation, Hero & Category Quick Tabs, Backend Architecture & CORS

---

## Design System & Theme Tokens

| Option | Description | Selected |
|--------|-------------|----------|
| MakeMyTrip Semantic Tokens (Recommended) | Configure custom Tailwind colors (Navy `#1A2B4C`, Blue `#0056D2`, Cyan `#00B4D8`, Canvas `#F5F7FB`) directly in theme and CSS variables. | ✓ |
| Default shadcn colors with inline overrides | Keep default zinc/slate palette and manually override classes on each component. | |

**User's choice:** MakeMyTrip Semantic Tokens (recommended default via `--auto`)
**Notes:** Creates the primary consumer-grade travel feel requested in `specs.md`.

---

## Global Layout & Navigation

| Option | Description | Selected |
|--------|-------------|----------|
| Sticky MakeMyTrip Navbar (Recommended) | Persistent header with CivicPilot logo, links to Home, Services, Applications, Documents, and Profile menu. | ✓ |
| Minimalist header | Unfixed header with basic text links. | |

**User's choice:** Sticky MakeMyTrip Navbar (recommended default via `--auto`)
**Notes:** Aligns with core navigation requirements in UI-02.

---

## Hero & Category Quick Tabs

| Option | Description | Selected |
|--------|-------------|----------|
| Unified Discovery Hero (Recommended) | Prominent natural language search bar, example query chips, and 8 category quick tabs on the home page. | ✓ |
| Simple search bar | Minimalist search without category filtering tabs. | |

**User's choice:** Unified Discovery Hero (recommended default via `--auto`)
**Notes:** Implements MakeMyTrip-inspired discovery pattern specified in `specs.md` §2.

---

## Backend Architecture & CORS

| Option | Description | Selected |
|--------|-------------|----------|
| Modular Router Architecture (Recommended) | `backend/app/` with `main.py`, `routers/` (modular endpoints), `models/` (Pydantic), and `config.py`. | ✓ |
| Monolithic single-file app | All initial endpoints written into a single `main.py`. | |

**User's choice:** Modular Router Architecture (recommended default via `--auto`)
**Notes:** Required for scalable growth across 12 phases and clean endpoint isolation.

---

## Antigravity's Discretion

- Exact button animation timing (Framer Motion spring curves) and card border-radius values.

## Deferred Ideas

- None — discussion stayed within Phase 1 scope.
