# Phase 02: Authentication & Citizen Profile Management — UI Specification

**Status:** APPROVED
**Design Language:** MakeMyTrip Consumer Travel Aesthetic (Deep Navy `#1A2B4C`, Vibrant Blue `#0056D2`, Cyan Accent `#00B4D8`, Canvas `#F5F7FB`)

---

## 1. Color Palette & Semantic Tokens

| Token | Hex | Usage |
|-------|-----|-------|
| `navy.DEFAULT` | `#1A2B4C` | Authoritative section headings, primary text, dark cards |
| `civic-blue.DEFAULT` | `#0056D2` | Primary action buttons ("Sign In", "Create Account", "Save Profile") |
| `civic-blue.hover` | `#0046AB` | Hover state for buttons and links |
| `civic-blue.light` | `#E8F0FE` | Active tab backgrounds, focus ring accents |
| `civic-cyan.DEFAULT` | `#00B4D8` | Verification badges, progress indicators, status chips |
| `canvas.DEFAULT` | `#F5F7FB` | Base page background canvas |
| `card.background` | `#FFFFFF` | Elevated white card containers |
| `border.subtle` | `#E5E9F2` | Card borders, input field borders, divider lines |
| `destructive` | `#DC2626` | Error text, invalid input border, destructive alerts |
| `success` | `#16A34A` | Verification checkmarks, profile save confirmation pill |

---

## 2. Typography Hierarchy

- **Font Family:** `Inter`, system-ui, sans-serif
- **Page Titles:** `text-2xl sm:text-3xl font-extrabold tracking-tight text-navy` (e.g., "Citizen Identity & Profile", "Sign In to CivicPilot")
- **Section Headers:** `text-lg font-bold text-navy` (e.g., "Personal Details", "Address & Domicile")
- **Field Labels:** `text-xs font-semibold uppercase tracking-wider text-slate-500`
- **Input Text:** `text-sm font-medium text-navy placeholder:text-slate-400`
- **Helper/Validation Text:** `text-xs font-normal text-slate-500` (or `text-destructive` on error)

---

## 3. Spacing & Layout Scale

- **Page Container:** `max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12`
- **Form Card Grid:** `grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6`
- **Form Sections:** `space-y-6` between elevated white cards
- **Card Padding:** `p-6 sm:p-8` for spacious travel-grade readability
- **Border Radius:** `rounded-2xl` for main cards, `rounded-lg` for inputs and buttons

---

## 4. Element Styles & Component Specifications

### 4.1 Authentication Page (`/auth`)
- **Card Container:** Floating `max-w-md mx-auto` elevated white card (`rounded-2xl shadow-xl border border-slate-200/80 p-8`).
- **Tab Switcher:** 2 segmented buttons (`Sign In` vs. `Create Account`) styled with MakeMyTrip active blue highlight.
- **Form Inputs:**
  - Email: `type="email"`, auto-complete `email`, required.
  - Password: `type="password"`, toggleable visibility eye icon, minimum 6 characters.
  - Full Name: (visible on registration mode), required.
- **Submit Button:** Full-width `Button` (`size="lg"`, variant `default`, with loading spinner on submission).
- **Security Notice:** "Protected by end-to-end encryption. Your credentials are never stored in plain text."

### 4.2 Citizen Profile Page (`/profile`)
- **Header Banner:** Profile summary banner with citizen avatar, completion percentage badge (`Badge variant="cyan"`), and last updated timestamp.
- **Section 1 — Personal Information Card:**
  - Full Name (`text`), Date of Birth (`date`), Gender (`select`: Male, Female, Other, Prefer not to say), Contact Number (`tel`).
- **Section 2 — Address & Domicile Card:**
  - State (`select` of Indian States/UTs), District (`text`), PIN Code (`text`, 6-digit pattern).
- **Section 3 — Academic Background Card:**
  - Current Education Level (`select`: 10th Standard, 12th Standard, Diploma, Undergraduate, Postgraduate, Doctorate), Institution Name (`text`), Course/Degree (`text`), Academic Year (`select`: 1st Year, 2nd Year, 3rd Year, 4th Year, Completed).
- **Section 4 — Voluntary Eligibility Attributes Card:**
  - Occupation (`select`: Student, Employed, Self-Employed, Farmer, Unemployed), Annual Family Income in ₹ (`number`, with helper "Required for income-based scholarships & subsidies"), Social Category (`select`: General, OBC, SC, ST, EWS).
- **Sticky Action Bar:** "Save Profile" CTA with loading state, and inline success banner ("Profile updated successfully").

---

## 5. Interaction & Motion

- **Card Hovers:** Subtle elevate effect (`transition-all duration-200 hover:shadow-md`).
- **Input Focus:** Smooth ring glow (`focus:border-civic-blue focus:ring-2 focus:ring-civic-blue/20`).
- **Tab Transitions:** Instant snappy switch with zero layout shift.
- **Save State:** Button shows `Loader2` rotating icon while saving, switches to checkmark upon success.

---

## 6. Responsive Breakpoints

- **Mobile (<640px):** Single column form fields, full-width buttons, collapsible sticky nav.
- **Tablet (640px - 1024px):** 2-column input grid inside sections, comfortable finger tap targets (min 44px).
- **Desktop (>1024px):** Centered max-4xl layout with prominent visual hierarchy and sidebar breadcrumb navigation.
