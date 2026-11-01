---
phase: "02"
name: "authentication-citizen-profile-management"
created: 2026-11-01
---

# Phase 02: Authentication & Citizen Profile Management — Context

## User Constraints

### Locked Decisions
- **D-01 (Supabase Auth & Session Management):** Implement Supabase authentication using `@supabase/supabase-js` and `@supabase/ssr` with persistent sessions across page reloads. Provide an `AuthProvider` React context exposing `user`, `session`, `loading`, `signInWithPassword`, `signUp`, and `signOut`.
- **D-02 (MakeMyTrip Authentication UI):** Build a dedicated `/auth` route featuring MakeMyTrip aesthetic (deep navy header, vibrant blue CTA, elevated white card) with seamless tabs to toggle between "Sign In" and "Create Account", with validation and error toast feedback.
- **D-03 (Protected Route Guard):** Protect private citizen routes (`/profile`, `/documents`, `/applications`) by redirecting unauthenticated users to `/auth`. Update Navbar to reflect authenticated session status with citizen profile avatar, name, and Sign Out dropdown.
- **D-04 (Citizen Profile PostgreSQL Schema & RLS):** Create `citizen_profiles` schema linked to `auth.users.id` with fields for personal, address, educational, and voluntary eligibility attributes, guarded by strict Row Level Security (RLS) (`auth.uid() = id`). Provide an offline development fallback so tests run reliably.
- **D-05 (MakeMyTrip Multi-Section Profile Form):** Build `/profile` page with MakeMyTrip styled card sections: Personal Details, Address & Domicile, Academic Profile, and Voluntary Eligibility Attributes with instant client-side validation and save feedback.
- **D-06 (FastAPI Profile Endpoints):** Implement modular `backend/app/routers/profile.py` with `GET /api/profile` and `PUT /api/profile` using strict Pydantic models (`CitizenProfileResponse`, `CitizenProfileUpdate`), token authentication dependency, and automated pytest coverage.

### Discretion Areas
- Field layout arrangements (2-column grid on desktop, single column on mobile).
- Dropdown options for Indian States, Social Categories, and Education Levels.
- Toast notification library / inline alert feedback style for profile save.

### Deferred Ideas
- Digilocker OAuth login (v2 requirement INT-01).
- SMS OTP-based login (v2).
