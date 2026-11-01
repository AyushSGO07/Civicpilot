# Phase 09: Real-time Agent Execution Workspace & WebSockets — UI Specification

## Overview

The Agent Execution Workspace lives at `/applications/workspace/[sessionId]` (with fast-track redirect from `/applications/new?serviceId=...`). It delivers an operations control room experience inspired by MakeMyTrip with deep navy accents, vibrant civic blue, glowing status pills, live browser canvas, and streaming AI reasoning logs.

---

## 1. Visual Hierarchy & Tokens

### Palette Tokens
- **Navy Primary**: `#1A2B4C` (Header bar, panel titles, elevated cards)
- **Civic Blue Accent**: `#0056D2` (Primary CTAs, active timeline dots)
- **Civic Cyan Accent**: `#00B4D8` (Live broadcast pulsing glow, scan line accents)
- **Dark Viewport Canvas**: `#0F172A` / `#020617` (Browser stream viewport background)
- **Live Indicator**:
  - Live Streaming: Pulsing Emerald Green (`bg-emerald-500`, ring `ring-emerald-400/50`)
  - Paused: Pulsing Amber (`bg-amber-500`, ring `ring-amber-400/50`)
  - Stopped / Aborted: Rose Red (`bg-rose-500`)

---

## 2. 3-Panel Layout Grid

```
+---------------------------------------------------------------------------------------------------+
| Workspace Header Bar                                                                              |
| [Scheme Title] [Category Badge] [Target Portal URL Pill]            [Live Status Pill] [Exit Btn] |
+---------------------------------------------------------------------------------------------------+
| 3-PANEL OPERATIONS GRID                                                                           |
|                                                                                                   |
| [PANEL 1: 1/4 WIDTH]            [PANEL 2: 2/4 WIDTH]                    [PANEL 3: 1/4 WIDTH]      |
| Citizen Profile Summary         Live Browser Viewport Stream            AI Reasoning & Audit Log  |
|                                                                                                   |
| • Applicant Identity:           • Viewport Canvas (1280x800 aspect)     • Live Log Feed (Stream)  |
|   - Full Name, DOB, Gender        - Real-time screenshot display          - [Discovery] ...       |
|   - Mobile, Address, State        - Active locator highlight overlay      - [Navigation] ...      |
|                                   - Loading spinner during transitions    - [Inspection] ...      |
| • Voluntary Attributes:                                                   - [Mapping] ...         |
|   - Income (₹), Category        • Execution Controls Bar:                 - [Filling] ...         |
|                                   - [Pause / Resume] (Amber/Blue)         - [Validation] ...      |
| • Attached Vault Docs:            - [Stop / Abort] (Rose Red)                                     |
|   - Aadhaar Card (Verified)       - Step Indicator: Step 3 of 6         • Reason Breakdown:       |
|   - Income Cert (Verified)                                                - Why field was filled  |
|   - Marksheet (Verified)                                                  - Vault source used     |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Interactive States & Controls

### 1. Connecting State
- Pulsing skeleton with spinner: "Establishing WebSocket connection to Playwright agent runtime..."

### 2. Live Streaming State
- Center viewport displays incoming Base64 JPEG frames from browser.
- Green pulsing "LIVE STREAMING" indicator.
- Controls bar shows enabled **Pause** and **Stop** buttons.

### 3. Paused State (EXEC-04)
- Viewport dims slightly with amber overlay: "Execution Paused by Citizen".
- Controls bar toggles button to **Resume Execution** (Civic Blue).
- Playwright browser remains frozen at current DOM location.

### 4. Aborted State (EXEC-05)
- Viewport shows: "Session Aborted".
- Browser is completely terminated on backend.
- Option to "Start New Execution" or "Return to Schemes".

---

## 4. Accessibility & Responsiveness
- Desktop: Full 3-panel split view (25% / 50% / 25%).
- Tablet & Mobile: Tabbed segmented control switching between `Live Viewport`, `Profile`, and `Reasoning Log`.
- Keyboard Shortcuts: Spacebar to toggle Pause/Resume, Escape to Abort.
