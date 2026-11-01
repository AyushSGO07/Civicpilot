# Phase 04: Live Government Scheme Discovery & Search — UI Specification

**Status:** APPROVED
**Design Language:** MakeMyTrip Consumer Travel Aesthetic (Navy `#1A2B4C`, Vibrant Blue `#0056D2`, Cyan Accent `#00B4D8`, Canvas `#F5F7FB`)

---

## 1. Color Palette & Semantic Tokens

| Token | Hex | Usage |
|-------|-----|-------|
| `navy.DEFAULT` | `#1A2B4C` | Headers, authoritative titles, card headers |
| `civic-blue.DEFAULT` | `#0056D2` | Primary buttons ("Search", "Check Eligibility") |
| `civic-blue.hover` | `#0046AB` | Button hover states |
| `civic-blue.light` | `#E8F0FE` | Active filter pill, focus rings |
| `civic-cyan.DEFAULT` | `#00B4D8` | Verification checkmarks, AI badges, active tabs |
| `canvas.DEFAULT` | `#F5F7FB` | Base page background canvas |
| `card.background` | `#FFFFFF` | Elevated scheme cards |
| `border.subtle` | `#E5E9F2` | Card borders, divider lines |

---

## 2. Layout & Responsive Structure

- **Page Container:** `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12`
- **Layout Sections:**
  1. **Header Banner:** Elevated dark gradient card (`from-navy to-navy-dark`) with search input, active category filter, and verified dataset badge.
  2. **Filter Controls:**
     - Category Tabs Bar (8 categories with Lucide icons)
     - State/UT Selector dropdown (`All India / Central` + 36 States/UTs)
     - Result Count indicator
  3. **Scheme Deck Grid:** Responsive 1-col on mobile, 2-col on desktop (`grid grid-cols-1 lg:grid-cols-2 gap-6`).
  4. **Scheme Card Component:**
     - Category and State badges (`variant="secondary"`, `variant="outline"`).
     - Title: `text-lg font-bold text-navy hover:text-civic-blue transition-colors`.
     - Department: `text-xs font-semibold uppercase tracking-wider text-slate-500`.
     - Eligibility Summary: Clear bulleted criteria.
     - Required Documents Tags: Tags for Aadhaar, Marksheet, Income Certificate, etc.
     - Footer:
       - External Link: "Official Portal" with `ExternalLink` icon linking to verified gov.in URL.
       - Action CTA: "Check Eligibility" button.

---

## 3. Element Specifications

### 3.1 Search Input Bar
- Magnifying glass icon, clear button, and submit action.
- Autofocused or pre-populated from `?q=...` URL parameter.

### 3.2 Category Filter Strip
- 8 Categories matching Hero Search:
  - Education
  - Scholarships
  - Identity & Documents
  - Transport
  - Agriculture
  - Healthcare
  - Business & MSME
  - Financial Assistance
- Active category has vibrant blue fill or cyan underline.

---

## 4. Interaction & Motion

- **Card Elevation:** Subtle shadow on hover (`transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5`).
- **Instant Filtering:** Client-side updates when changing category or state filter without page reloads.
- **External Portal Security:** All official links use `target="_blank" rel="noopener noreferrer"`.
