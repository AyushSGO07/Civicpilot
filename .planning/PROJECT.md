# CivicPilot

## What This Is

CivicPilot is an AI-powered autonomous public service platform that simplifies access to government services by discovering relevant schemes, assessing citizen eligibility, preparing applications, and navigating complex government websites on behalf of citizens. It combines LLM-based reasoning, intelligent document extraction, browser automation via Playwright, and persistent workflow orchestration with LangGraph to transform bureaucratic hurdles into an intuitive, guided consumer experience inspired by MakeMyTrip.

## Core Value

Autonomous, genuine navigation and execution of real government application workflows on official portals with verified eligibility and explicit human-in-the-loop approval — delivering real bureaucratic execution instead of another informational chatbot.

## Business Context

- **Customer**: Indian citizens, students, farmers, and business owners navigating complex public schemes and certificates.
- **Revenue model**: Public digital infrastructure / civic-tech SaaS / assisted service model (free citizen tier, institutional/enterprise tier).
- **Success metric**: 100% verified application workflows executed on genuine government portals with authentic acknowledgement numbers and receipts retrieved.
- **Strategy notes**: Hackathon MVP demonstrating one complete, verified end-to-end scholarship/scheme workflow on an official government portal.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] **UI-01**: MakeMyTrip-inspired UI/UX design system with deep navy, vibrant blue, cyan accents, responsive layout, and modern typography
- [ ] **AUTH-01**: User registration, login, logout, and session persistence via Supabase Authentication
- [ ] **PROF-01**: Citizen profile management for personal, educational, address, and voluntary scheme eligibility attributes
- [ ] **DOC-01**: Secure Document Vault supporting PDF, JPG, and PNG uploads to Supabase Storage with preview and management
- [ ] **DOC-02**: Intelligent document processing with Gemini OCR for metadata extraction, field classification, and user verification
- [ ] **DISC-01**: Live government service discovery and natural language search powered by official sources (MyScheme, National Scholarship Portal, India.gov.in)
- [ ] **ELIG-01**: AI Eligibility Assistant evaluating citizen profile data against official scheme rules with transparent reasoning and citations
- [ ] **AGENT-01**: LangGraph-orchestrated autonomous browser automation workflow with state persistence and pause/resume capability
- [ ] **AGENT-02**: Playwright browser agent utilizing accessible DOM locators, dynamic field mapping, and form population
- [ ] **AGENT-03**: Bounded error detection and recovery for navigation timeouts, unexpected popups, and portal UI variations
- [ ] **AGENT-04**: Human-in-the-loop approval gate displaying entered data summaries and pausing for mandatory CAPTCHA/MFA steps
- [ ] **AGENT-05**: Authentic portal submission verification, acknowledgement number capture, and receipt document generation/archival
- [ ] **EXEC-01**: Real-time Agent Execution Workspace featuring live browser preview, WebSocket event streaming, and execution controls
- [ ] **APP-01**: My Applications dashboard tracking legitimate portal submission statuses, timelines, and downloadable receipts

### Out of Scope

- [ ] Bypassing CAPTCHA, OTP, biometric, or MFA mechanisms — Prohibited security/legal boundary; handled via clean human-in-the-loop pause.
- [ ] Simulated or hardcoded dummy portal interactions — Prohibited by hackathon zero-dummy-data rules; all data and interactions must be authentic.
- [ ] Fabricating reference numbers or application receipts — Strict integrity constraint.
- [ ] Automating all 1000+ national and state portals in v1 — Initial focus on robust, flawless execution of primary targeted workflows (e.g. National Scholarship Portal / MyScheme).
- [ ] Financial transaction execution / automated fee payments — User must handle payment gates manually in the browser session.

## Context

- Hackathon prototype built to address bureaucratic friction in Indian public services.
- Indian government portals frequently suffer from session timeouts, complex multi-step forms, rigid validation, and non-standard HTML.
- Strict compliance: Zero dummy data. Information must come from live official government sources.
- Tech Stack:
  - Frontend: Next.js (App Router), TypeScript, Tailwind CSS, shadcn/ui, Lucide Icons, Framer Motion.
  - Backend: Python FastAPI, Pydantic, WebSockets, Playwright.
  - AI Layer: Gemini API (structured outputs, OCR extraction, reasoning), LangGraph for orchestration.
  - Database & Storage: Supabase PostgreSQL and Supabase Storage.

## Constraints

- **Integrity**: Zero dummy data. Official sources only; no fabricated numbers or simulated workflows.
- **Security**: Strict credential handling; sensitive personal data protected; explicit consent before submission.
- **Architecture**: Bounded agent actions with LangGraph state machine; browser must run in a persistent runtime environment.
- **Design System**: Consumer travel platform feel (MakeMyTrip-inspired visual hierarchy, responsive, accessible).

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Next.js + FastAPI split | Next.js provides modern UI/UX components; FastAPI provides native async Python support for Playwright, LangGraph, and WebSockets | — Pending |
| Gemini API for OCR & Reasoning | Powerful multimodal capabilities for document analysis and dynamic HTML form mapping | — Pending |
| LangGraph State Machine | Deterministic workflow states ensure safe pauses for human approval and CAPTCHA handling | — Pending |
| Playwright with Accessible Locators | More resilient to portal UI changes than coordinate-based vision models | — Pending |
| MakeMyTrip Visual Aesthetic | Shifts government paperwork from dreary bureaucracy to an engaging, trustworthy consumer discovery journey | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-11-01 after initialization*
