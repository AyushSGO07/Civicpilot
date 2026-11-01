# Phase 03: Secure Document Vault & Multimodal OCR Extraction — UI Specification

**Status:** APPROVED
**Design Language:** MakeMyTrip Consumer Travel Aesthetic (Navy `#1A2B4C`, Vibrant Blue `#0056D2`, Cyan Accent `#00B4D8`, Canvas `#F5F7FB`)

---

## 1. Color Palette & Semantic Tokens

| Token | Hex | Usage |
|-------|-----|-------|
| `navy.DEFAULT` | `#1A2B4C` | Headers, authoritative titles, card headers |
| `civic-blue.DEFAULT` | `#0056D2` | Primary buttons ("Upload Document", "Confirm & Sync") |
| `civic-blue.hover` | `#0046AB` | Button hover states |
| `civic-blue.light` | `#E8F0FE` | Dropzone drag active state, info banners |
| `civic-cyan.DEFAULT` | `#00B4D8` | "Run AI OCR" button, encryption badge, progress |
| `canvas.DEFAULT` | `#F5F7FB` | Page background |
| `card.background` | `#FFFFFF` | Document cards and modals |
| `status.verified` | `#16A34A` | Green badge for verified documents |
| `status.extracted` | `#0284C7` | Blue/cyan badge for extracted documents |
| `status.unverified`| `#EAB308` | Amber badge for uploaded but unextracted docs |
| `destructive` | `#DC2626` | Delete document action button and error alerts |

---

## 2. Layout & Responsive Structure

- **Page Container:** `max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12`
- **Layout:**
  1. **Vault Header:** Dark elevated gradient banner (`bg-gradient-to-r from-navy to-navy-dark`) with security shield, vault stats (total documents, verified count), and 256-bit AES encryption badge.
  2. **Upload Dropzone Card:** Elevated white card with dashed border, document type dropdown, file selector (PDF, JPG, PNG max 10MB), and instant validation feedback.
  3. **Filter Pills:** Horizontal scrollable category filters (`All Documents`, `Identity (Aadhaar/PAN)`, `Income & Caste`, `Academic Marksheets`, `Other`).
  4. **Document Cards Grid:** Responsive 1-col on mobile, 2-col on tablet, 3-col on desktop (`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6`).
  5. **Document Preview Modal:** Centered dialog displaying high-resolution file preview (image viewer or PDF iframe) with close and download options.
  6. **OCR Verification & Merge Modal:** Side-by-side comparison modal displaying extracted attributes with confidence scores and 1-click sync to citizen profile.

---

## 3. Element Specifications

### 3.1 Document Card Component
- File thumbnail / icon based on type (PDF red icon, image blue icon).
- Document name (`text-sm font-bold text-navy truncate`).
- Document type badge (`variant="secondary"`).
- Verification status pill (`Verified`, `Extracted`, `Unverified`).
- File size and upload timestamp (`text-xs text-slate-400`).
- Card Actions:
  - "Preview" (eye icon)
  - "Run AI OCR" (sparkles icon with cyan gradient)
  - "Delete" (trash icon with destructive confirmation)

### 3.2 OCR Verification Modal
- Title: "AI Document Extraction — Verification & Profile Sync"
- Document details and confidence badge.
- Extracted Fields Table:
  - Field name (e.g. Legal Name, Date of Birth, Address, Score)
  - Extracted Value (e.g. "Aarav Sharma", "2002-05-14")
  - Current Profile Value (e.g. "Citizen User" or matching value)
  - Checkbox to accept or skip field
- Action footer: "Sync Selected Fields to Profile" and "Cancel".

---

## 4. Interaction & Micro-Animations

- **Dropzone:** Border changes to `border-civic-blue bg-civic-blue/5 scale-[1.01]` on drag over.
- **OCR Progress:** Pulsing AI glow with `Loader2` rotating icon while Gemini models process the document.
- **Success Notification:** Instant toast/alert showing "Extracted 5 profile attributes from Aadhaar card".
