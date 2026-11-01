-- CivicPilot PostgreSQL Schema: Citizen Profiles
-- Links to Supabase auth.users with strict Row Level Security (RLS)

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
    annual_income NUMERIC(12, 2) CHECK (annual_income >= 0),
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
