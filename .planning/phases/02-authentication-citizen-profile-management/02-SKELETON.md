# Phase 02: Authentication & Citizen Profile Management — Skeleton

**Skeleton Type:** Walking Skeleton
**Wave:** 1 Tracer

---

## 1. End-to-End Vertical Slice

This phase's walking skeleton connects:
1. `database/schema.sql` defining `citizen_profiles` table and RLS policies.
2. `backend/app/routers/profile.py` implementing `GET /api/profile` and `PUT /api/profile` with Pydantic model validation.
3. `frontend/lib/supabase.ts` and `frontend/context/auth-context.tsx` providing user authentication and session management.
4. `frontend/app/auth/page.tsx` and `frontend/app/profile/page.tsx` offering MakeMyTrip-inspired UI for login/registration and citizen profile management.

---

## 2. Tracer Flow

```
User visits /auth 
  ──> Inputs credentials 
  ──> Supabase Auth authenticates user 
  ──> Session stored in AuthContext 
  ──> Redirected to /profile 
  ──> Views/edits Personal, Address, Education, Eligibility fields 
  ──> Saves profile 
  ──> PUT /api/profile validates and stores profile data
```

---

## 3. Thin Implementation Boundaries

- Real schema: PostgreSQL DDL with RLS.
- Real API endpoints: FastAPI router mounted on `/api/profile`.
- Real frontend components: MakeMyTrip themed forms in Next.js 15 App Router.
- Resilient fallback: If live Supabase credentials are not set during initial automated tests, the auth provider and backend router operate in offline fallback mode with passing tests.
