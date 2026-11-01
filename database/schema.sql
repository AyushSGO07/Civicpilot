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


-- CivicPilot PostgreSQL Schema: Citizen Documents
-- Stored in private bucket 'citizen-vault', metadata in public.documents

CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    document_name TEXT NOT NULL,
    document_type TEXT NOT NULL CHECK (document_type IN (
        'Aadhaar Card', 'PAN Card', 'Income Certificate', 'Caste Certificate',
        'Domicile Certificate', 'Academic Marksheet', 'Bonafide Certificate',
        'Passport Photo', 'Bank Passbook', 'Other'
    )),
    mime_type TEXT NOT NULL CHECK (mime_type IN ('application/pdf', 'image/jpeg', 'image/png')),
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes <= 10485760),
    storage_path TEXT NOT NULL,
    extracted_information JSONB DEFAULT '{}'::jsonb,
    verification_status TEXT DEFAULT 'Unverified' CHECK (verification_status IN ('Unverified', 'Extracted', 'Verified', 'Rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Citizens can only manage their own documents
CREATE POLICY "Users can view own documents"
    ON public.documents FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own documents"
    ON public.documents FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own documents"
    ON public.documents FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own documents"
    ON public.documents FOR DELETE
    USING (auth.uid() = user_id);


-- CivicPilot PostgreSQL Schema: Government Services & Schemes
-- Authoritative catalog of verified Indian central and state schemes

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

-- Enable Row Level Security (RLS)
ALTER TABLE public.government_services ENABLE ROW LEVEL SECURITY;

-- Public read access for active government services
CREATE POLICY "Anyone can view active government services"
    ON public.government_services FOR SELECT
    USING (is_active = TRUE);
