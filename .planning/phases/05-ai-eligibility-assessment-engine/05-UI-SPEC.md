# Phase 05: AI Eligibility Assessment Engine — UI Specification

## Overview

The Scheme Detail and AI Eligibility Assessment page lives at `/services/[serviceId]`. It provides a MakeMyTrip-grade consumer interface for discovering full scheme requirements and running an automated AI eligibility evaluation against the citizen's profile.

---

## 1. Visual Hierarchy & Tokens

### Palette Tokens
- **Navy Primary**: `#1A2B4C` (Header text, cards header, high contrast emphasis)
- **Civic Blue Accent**: `#0056D2` (Primary CTAs, active badges, links)
- **Civic Cyan Accent**: `#00B4D8` (Gradient highlights, focus rings)
- **Canvas Neutral**: `#F5F7FB` (Background canvas)
- **Success (Likely Eligible)**:
  - Background: `bg-emerald-50`
  - Text: `text-emerald-800`
  - Border: `border-emerald-300`
  - Icon: CheckCircle2 (`text-emerald-600`)
- **Warning (More Information Required)**:
  - Background: `bg-amber-50`
  - Text: `text-amber-800`
  - Border: `border-amber-300`
  - Icon: AlertCircle (`text-amber-600`)
- **Danger (Likely Ineligible)**:
  - Background: `bg-rose-50`
  - Text: `text-rose-800`
  - Border: `border-rose-300`
  - Icon: XCircle (`text-rose-600`)

---

## 2. Page Structure & Components

```
+-------------------------------------------------------------------------+
| Navbar (Sticky Global Header)                                           |
+-------------------------------------------------------------------------+
| Breadcrumb: Services / {Category} / {Scheme Name}                       |
+-------------------------------------------------------------------------+
| Scheme Header Banner                                                    |
| - Title & Department                                                    |
| - Badges: Category | State | Active / Deadline                         |
| - Official Portal External Link Button                                  |
+-------------------------------------------------------------------------+
| Main Grid (2/3 Main Column, 1/3 Side Column)                            |
|                                                                         |
| [Main Column]                                                           |
| 1. AI Eligibility Evaluation Card                                       |
|    - Instant / On-Demand Evaluation Trigger                             |
|    - Determination Pill: Likely Eligible / Ineligible / More Info       |
|    - Summary narrative with AI confidence score                         |
|    - Missing Profile Fields Alert (if any) -> Link to /profile          |
|    - Itemized Criteria Comparison Matrix:                               |
|        * Criterion Name & Condition                                     |
|        * Your Profile Data                                              |
|        * Match Status (Satisfied / Not Satisfied / Missing)             |
|        * Official Guideline Citation                                    |
| 2. Scheme Overview & Detailed Description                               |
| 3. Mandatory Documents Checklist                                        |
| 4. Statutory Advisory Disclaimer                                        |
|                                                                         |
| [Side Column]                                                           |
| 1. Application Fast-Track Card                                          |
|    - Autonomous Agent Execution CTA                                     |
|    - Official Portal Manual Execution CTA                               |
| 2. Scheme Snapshot Meta                                                 |
|    - Issuing Authority                                                  |
|    - Target Beneficiaries                                               |
|    - Application Period / Deadline                                      |
+-------------------------------------------------------------------------+
```

---

## 3. Interactive States

### 1. Loading State
- Pulsing skeleton cards for Scheme Details and AI Assessment card while fetching service data and evaluating profile.

### 2. Evaluated State
- Renders top-level evaluation card with dynamic color scheme based on status:
  - **`Likely Eligible`**: Highlights immediate path to autonomous application execution.
  - **`Likely Ineligible`**: Highlights specific unmet criteria in red with explanation and citation, without discouraging legal re-check.
  - **`More Information Required`**: Lists specific missing attributes with high-visibility button `Update Profile to Complete Check ->` opening `/profile`.

### 3. Unauthenticated State
- When visitor is not logged in, card displays: "Sign in to evaluate your personal eligibility against official criteria" with 1-click login button redirecting to `/auth`.

---

## 4. Accessibility & Security

- **Accessible Colors**: All text-to-background combinations exceed WCAG AA 4.5:1 contrast ratios.
- **Screen Reader Support**: ARIA live regions for eligibility evaluation status updates.
- **External Links**: All links to `.gov.in` portals enforce `target="_blank" rel="noopener noreferrer"`.
- **Zero Dummy Data**: Only official published schemes and actual citizen profile values are presented.
