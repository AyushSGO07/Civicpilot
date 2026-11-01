# Phase 03: Secure Document Vault & Multimodal OCR Extraction — Research

**Researched:** 2026-11-01
**Domain:** Supabase Storage, FastAPI File Uploads, Google GenAI Multimodal OCR (`google-genai`), Next.js Document Vault UI
**Confidence:** HIGH

---

## 1. Architectural Strategy

Phase 3 implements the citizen's secure personal document vault and the multimodal AI extraction pipeline.
Uploaded identity and academic documents provide verified ground-truth data that feeds directly into:
1. Dynamic field mapping onto government portal forms (Phase 7).
2. AI-driven scheme eligibility assessment (Phase 5).
3. Citizen profile enrichment with verified attributes (Phase 2 & 3).

```
[ Citizen (Browser) ]
         │
         │ Upload File (PDF / JPG / PNG)
         ▼
[ FastAPI /api/documents/upload ] ───────► [ Supabase Storage (citizen-vault) ]
         │                                 (Private bucket, signed URLs only)
         │ Creates record
         ▼
[ PostgreSQL: public.documents ]
         │
         │ Trigger OCR (/api/documents/{id}/ocr)
         ▼
[ Gemini 2.5 Flash via google-genai ]
         │ Multimodal Image/PDF Parsing + Structured Outputs
         ▼
[ Extracted JSON Metadata ]
         │
         │ Citizen Reviews & Approves in Modal
         ▼
[ Merged into citizen_profiles (/api/profile) ]
```

---

## 2. Standard Stack & Dependencies

| Technology | Purpose | Implementation Notes |
|------------|---------|----------------------|
| `python-multipart` | FastAPI multipart/form-data upload | Required for `UploadFile` parameter parsing in FastAPI |
| `google-genai` (0.3.0+) | Multimodal reasoning & OCR extraction | Official SDK; calls `gemini-2.5-flash` with structured Pydantic schemas |
| `Supabase Storage` | Encrypted cloud bucket | Private bucket `citizen-vault` with signed URLs (1-hour expiry) |
| Next.js App Router | Document Vault UI (`/documents`) | MakeMyTrip cards, file upload drag-and-drop, preview modal, diff modal |

---

## 3. Database Schema: `public.documents`

```sql
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
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes <= 10485760), -- Max 10MB
    storage_path TEXT NOT NULL,
    extracted_information JSONB DEFAULT '{}'::jsonb,
    verification_status TEXT DEFAULT 'Unverified' CHECK (verification_status IN ('Unverified', 'Extracted', 'Verified', 'Rejected')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Row Level Security (RLS)
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

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
```

---

## 4. Google GenAI Multimodal Extraction Pattern

Using the official Google GenAI SDK (`google-genai`):

```python
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Optional

class ExtractedDocumentData(BaseModel):
    document_type: str
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    id_number_masked: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    pincode: Optional[str] = None
    annual_income: Optional[float] = None
    social_category: Optional[str] = None
    institution_name: Optional[str] = None
    course: Optional[str] = None
    academic_score: Optional[str] = None
    confidence_score: float = 0.95

# Invocation:
client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        types.Part.from_bytes(data=file_bytes, mime_type=mime_type),
        "Analyze this official Indian document. Extract all citizen profile fields accurately. "
        "Mask all sensitive ID numbers (e.g. XXXX-XXXX-1234 for Aadhaar). Never fabricate data."
    ],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=ExtractedDocumentData,
    ),
)
```

---

## 5. Threat Model & Security Considerations (ASVS Level 1)

1. **Private Storage Only:** The Supabase Storage bucket `citizen-vault` must be marked `public = false`. Public URLs are strictly prohibited.
2. **Access via Signed URLs:** Document downloads or previews must use signed URLs expiring within 3600 seconds.
3. **MIME & Size Enforcement:** Strictly validate file extensions and MIME types (`application/pdf`, `image/jpeg`, `image/png`) and limit upload size to 10MB to prevent DoS attacks.
4. **Masked Identifiers:** Mask national identity numbers (e.g., Aadhaar `XXXX-XXXX-1234`, PAN `XXXXX1234X`) in extracted OCR outputs to prevent plain text exposure of sensitive credentials.
5. **No Data Hallucination:** If a field is illegible or not present on the document, Gemini returns `null`. The citizen always reviews and approves before data touches their profile.
