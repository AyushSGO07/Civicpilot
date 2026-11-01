# Phase 02: Authentication & Citizen Profile Management — Research

**Researched:** 2026-11-01
**Domain:** Supabase Auth, Next.js 15 Client/SSR Sessions, FastAPI Profile CRUD, PostgreSQL RLS
**Confidence:** HIGH

---

## 1. Architectural Strategy

Phase 2 establishes persistent citizen identity and comprehensive profile management, which forms the single source of truth for:
1. Dynamic field mapping onto government portal forms (Phase 7).
2. AI-driven scheme eligibility assessment (Phase 5).
3. Private document associations in the document vault (Phase 3).

```
                      Browser (Next.js 15)
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
      Supabase Auth API               CivicPilot FastAPI
    (JWT / Session Tokens)           (Bearer Auth Header)
               │                               │
               ▼                               ▼
       auth.users table               citizen_profiles table
       (PostgreSQL)                   (PostgreSQL + RLS)
```

---

## 2. Standard Stack

| Technology | Version | Purpose | Why Selected |
|------------|---------|---------|--------------|
| `@supabase/supabase-js` | Latest (^2.48.0) | Frontend Auth & DB Client | Official client for authentication and database querying |
| `@supabase/ssr` | Latest (^0.5.0) | Cookie-based Auth for Next.js | Handles cookie serialization across Next.js App Router |
| `FastAPI` | 0.115+ | Backend Profile API | High performance, strict Pydantic v2 schemas |
| `pydantic` | 2.10+ | Schema Validation | Data validation for citizen profile fields |
| `supabase` (Python) | 2.10+ | Backend DB Client | Python SDK for Supabase PostgreSQL operations |

---

## 3. Database Schema: `citizen_profiles`

```sql
-- Create citizen_profiles table linked to auth.users
CREATE TABLE IF NOT EXISTS public.citizen_profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT CHECK (gender IN ('Male', 'Female', 'Other', 'Prefer not to say')),
    contact_number TEXT,
    state TEXT,
    district TEXT,
    pincode VARCHAR(6),
    education_level TEXT,
    institution_name TEXT,
    course TEXT,
    academic_year TEXT,
    occupation TEXT,
    annual_income NUMERIC(12, 2),
    social_category TEXT CHECK (social_category IN ('General', 'OBC', 'SC', 'ST', 'EWS')),
    disability_status BOOLEAN DEFAULT FALSE,
    minority_status BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.citizen_profiles ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Citizens can only manage their own profile
CREATE POLICY "Users can view their own profile"
    ON public.citizen_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile"
    ON public.citizen_profiles FOR INSERT
    WITH CHECK (auth.uid() = id);

CREATE POLICY "Users can update their own profile"
    ON public.citizen_profiles FOR UPDATE
    USING (auth.uid() = id);
```

---

## 4. Patterns & Best Practices

### Pattern 1: Safe Authentication Context
```tsx
// frontend/context/auth-context.tsx
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        setLoading(false);
      }
    );

    return () => subscription.unsubscribe();
  }, []);
  ...
}
```

### Pattern 2: Backend JWT Authentication Dependency
In FastAPI, endpoints extract the Bearer token from the `Authorization` header and verify it. For unit tests without network connectivity to Supabase, an in-memory/mock authenticated test client is provided to test profile CRUD deterministically.

---

## 5. Pitfalls & Anti-Patterns to Avoid

1. **Anti-pattern:** Allowing unauthenticated requests to modify citizen profiles.
   - *Fix:* Check `auth.uid() == profile.id` in RLS and verify JWT in FastAPI.
2. **Anti-pattern:** Fabricating simulated citizen profiles or credentials.
   - *Fix:* User manually enters their actual data or signs up with their genuine email.
3. **Anti-pattern:** Blocking local development when Supabase env vars are not yet configured in `.env.local`.
   - *Fix:* Provide graceful fallback notifications and mock auth provider when environment variables are missing during initial developer onboarding.
