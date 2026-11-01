# Roadmap: CivicPilot

## Overview

CivicPilot transforms public service bureaucracy into a guided, autonomous consumer journey inspired by MakeMyTrip. This roadmap executes across 12 focused MVP phases, starting with foundational Next.js/FastAPI infrastructure and MakeMyTrip design language, progressing through Supabase authentication, citizen profile management, secure document vault with Gemini OCR, official scheme discovery, AI eligibility reasoning, and Playwright browser automation with dynamic field mapping. It culminates in LangGraph stateful orchestration, a live 3-panel operations workspace with WebSocket streaming, explicit human-in-the-loop approval, authentic receipt retrieval, and the My Applications dashboard.

## Phases

**Phase Numbering:**

- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

- [ ] **Phase 1: Project Foundation & MakeMyTrip Design System** - Next.js 15, FastAPI, Supabase setup, and MakeMyTrip visual identity
- [ ] **Phase 2: Authentication & Citizen Profile Management** - Supabase Auth, persistent sessions, and comprehensive citizen profile schema
- [ ] **Phase 3: Secure Document Vault & Multimodal OCR Extraction** - Private document storage, preview, and Gemini multimodal OCR parsing
- [ ] **Phase 4: Live Government Scheme Discovery & Search** - Ingesting verified official schemes with natural language search & filtering
- [ ] **Phase 5: AI Eligibility Assessment Engine** - Gemini-powered profile evaluation against official criteria with citations
- [ ] **Phase 6: Playwright Browser Automation Core & DOM Inspection** - Headless Chromium engine and accessible semantic DOM tree extraction
- [ ] **Phase 7: Dynamic Field Mapping & Form Filling Engine** - Dynamic Gemini field mapping and automated multi-step form population
- [ ] **Phase 8: LangGraph Workflow Orchestration & Bounded Recovery** - Stateful workflow state machine with checkpointing and bounded retries
- [ ] **Phase 9: Real-time Agent Execution Workspace & WebSockets** - 3-panel operations dashboard, live browser streaming, and controls
- [ ] **Phase 10: Human-in-the-Loop Approval & Security Checkpoints** - Pre-submission summary, explicit approval gate, and CAPTCHA/OTP pause
- [ ] **Phase 11: Submission Verification, Receipt Retrieval & Application Tracking** - Authentic reference capture, PDF receipt storage, and My Applications dashboard
- [ ] **Phase 12: End-to-End Integration, Demonstration Polish & Production Hardening** - Complete live flow verification on target portals and documentation

## Phase Details

### Phase 1: Project Foundation & MakeMyTrip Design System

**Goal**: Establish dual-stack Next.js and FastAPI environment with MakeMyTrip design language (navy/blue/cyan) and base layout.
**Mode:** mvp
**Depends on**: Nothing (first phase)
**Requirements**: UI-01, UI-02, UI-03, UI-04
**Success Criteria** (what must be TRUE):

  1. Next.js app renders responsive layout with deep navy (`#1A2B4C`), vibrant blue (`#0056D2`), and cyan accent styling.
  2. Sticky navigation bar displays links to Home, Services, Applications, Documents, and Profile.
  3. Hero section displays search bar and interactive category filter tabs.
  4. FastAPI backend responds with health status on `/api/health`.

**Plans**: 3 plans

Plans:
**Wave 1**

- [ ] 01-01: Initialize Next.js 15 project with Tailwind CSS, shadcn/ui, Lucide icons, and MakeMyTrip theme palette
- [ ] 01-03: Initialize FastAPI backend project structure, CORS middleware, and health check endpoint

**Wave 2** *(blocked on Wave 1 completion)*

- [ ] 01-02: Build responsive global navigation bar, MakeMyTrip Hero search interface, and category quick tabs

### Phase 2: Authentication & Citizen Profile Management

**Goal**: Implement user registration, login, persistent sessions, and comprehensive citizen profile CRUD.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, PROF-01, PROF-02, PROF-03, PROF-04, PROF-05
**Success Criteria** (what must be TRUE):

  1. User can register with email/password and log in using Supabase Auth.
  2. User sessions persist across browser refreshes, and protected routes redirect unauthenticated users.
  3. User can input, view, and update personal, address, and educational profile details.
  4. User can save voluntary scheme-specific eligibility attributes with instant client-side validation.

**Plans**: 3 plans

Plans:

- [ ] 02-01: Set up Supabase Auth configuration, database schema (`users`, `citizen_profiles`), and RLS policies
- [ ] 02-02: Implement authentication pages (login, registration, logout) and session context provider in frontend
- [ ] 02-03: Implement citizen profile management form (personal, address, educational, voluntary attributes) with FastAPI endpoints

### Phase 3: Secure Document Vault & Multimodal OCR Extraction

**Goal**: Build encrypted document storage with Gemini multimodal OCR to extract information into the citizen profile.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04, DOC-05
**Success Criteria** (what must be TRUE):

  1. User can upload PDF, JPG, and PNG files into a private Supabase Storage bucket.
  2. Document Vault displays uploaded files with preview, metadata, and deletion capability.
  3. Gemini multimodal OCR parses uploaded documents (Aadhaar, PAN, marksheets) into structured fields.
  4. User can review extracted fields and confirm them directly into their citizen profile.

**Plans**: 3 plans

Plans:

- [ ] 03-01: Configure Supabase Storage private vault bucket and `documents` database table with signed URL generation
- [ ] 03-02: Implement document upload, list, preview, and delete UI in Document Vault page
- [ ] 03-03: Integrate Google GenAI SDK to perform multimodal OCR extraction and provide an interactive verification modal

### Phase 4: Live Government Scheme Discovery & Search

**Goal**: Ingest verified official government schemes and provide natural language and category-based discovery.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: DISC-01, DISC-02, DISC-03, DISC-04
**Success Criteria** (what must be TRUE):

  1. User can browse verified schemes across categories (Scholarships, Education, Transport, Agriculture, MSME, Healthcare).
  2. User can execute natural language search queries and receive relevant matching schemes.
  3. Scheme cards display issuing department, eligibility summary, required documents, and verified official source URLs.
  4. Official portal links open authoritative government endpoints.

**Plans**: 2 plans

Plans:

- [ ] 04-01: Build backend government service ingestion and search engine querying verified official datasets with caching
- [ ] 04-02: Implement Explore Services page with category tabs, search filter, and MakeMyTrip-style service card deck

### Phase 5: AI Eligibility Assessment Engine

**Goal**: Build Gemini-powered reasoning engine that evaluates citizen profiles against official scheme criteria with citations.
**Mode:** mvp
**Depends on**: Phase 2, Phase 4
**Requirements**: ELIG-01, ELIG-02, ELIG-03, ELIG-04, ELIG-05
**Success Criteria** (what must be TRUE):

  1. User can request eligibility assessment for any scheme and receive an instant determination.
  2. System classifies eligibility as "Likely Eligible", "Likely Ineligible", or "More Information Required".
  3. User sees itemized comparison of their profile data against official criteria with source citations.
  4. Missing profile fields needed for evaluation are highlighted to the citizen.

**Plans**: 2 plans

Plans:

- [ ] 05-01: Implement backend Gemini eligibility reasoning service with structured JSON output and source citation logic
- [ ] 05-02: Build AI Eligibility Assistant modal/drawer in frontend showing comparison breakdown and missing field alerts

### Phase 6: Playwright Browser Automation Core & DOM Inspection

**Goal**: Establish asynchronous Playwright engine for navigating government portals and extracting clean semantic DOM element trees.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: AGENT-01, AGENT-02, AGENT-07
**Success Criteria** (what must be TRUE):

  1. Backend asynchronously launches and manages Playwright Chromium instances targeting official portal URLs.
  2. Engine inspects web pages and produces a sanitized, semantic interactive element tree.
  3. Browser instances cleanly close on task completion or abort without leaving orphaned/zombie processes.

**Plans**: 2 plans

Plans:

- [ ] 06-01: Build asynchronous Playwright browser manager with context pooling, viewport setup, and automated lifecycle cleanup
- [ ] 06-02: Implement semantic DOM extraction engine that strips non-functional markup into an accessible element tree

### Phase 7: Dynamic Field Mapping & Form Filling Engine

**Goal**: Build Gemini-driven dynamic mapping from citizen profiles to portal DOM elements and execute form population.
**Mode:** mvp
**Depends on**: Phase 3, Phase 6
**Requirements**: AGENT-03, AGENT-04, AGENT-05
**Success Criteria** (what must be TRUE):

  1. Gemini maps citizen profile attributes to portal inputs dynamically without hardcoded CSS selectors.
  2. Playwright automatically populates text inputs, selects dropdowns, and toggles checkboxes.
  3. Verified documents from the citizen's vault are attached to matching portal file upload inputs.

**Plans**: 2 plans

Plans:

- [ ] 07-01: Develop Gemini dynamic field mapping prompt generating structured action sequences from DOM trees and profile data
- [ ] 07-02: Implement Playwright form action executor for text input, select dropdowns, radio/checkboxes, and file uploads

### Phase 8: LangGraph Workflow Orchestration & Bounded Recovery

**Goal**: Orchestrate the browser agent with a stateful LangGraph workflow and bounded error recovery.
**Mode:** mvp
**Depends on**: Phase 6, Phase 7
**Requirements**: AGENT-06
**Success Criteria** (what must be TRUE):

  1. LangGraph manages end-to-end execution state with checkpoints across discovery, inspection, mapping, and filling.
  2. Agent detects timeouts, alert dialogs, and field validation errors and attempts bounded recovery (max 3 retries).
  3. If unresolvable errors persist, agent transitions safely to human assistance state.

**Plans**: 2 plans

Plans:

- [ ] 08-01: Construct LangGraph state graph with nodes for Discovery, Inspection, Mapping, Filling, and Validation
- [ ] 08-02: Implement bounded error recovery logic with state mutation checks and unexpected modal/popup handlers

### Phase 9: Real-time Agent Execution Workspace & WebSockets

**Goal**: Deliver a 3-panel operations dashboard streaming live browser screenshots, AI reasoning, and execution controls.
**Mode:** mvp
**Depends on**: Phase 1, Phase 8
**Requirements**: EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-05
**Success Criteria** (what must be TRUE):

  1. Citizen views 3-panel workspace: Profile summary (left), live browser stream (center), AI reasoning log (right).
  2. Genuine backend milestones stream live over WebSockets (`/ws/agent/{sessionId}`).
  3. User can watch live browser visual updates as the agent navigates the portal.
  4. Citizen can click Pause, Resume, or Stop, and the Playwright browser immediately responds.

**Plans**: 3 plans

Plans:

- [ ] 09-01: Build FastAPI WebSocket manager streaming JSON event frames and Base64 screenshot buffers for active sessions
- [ ] 09-02: Create frontend Agent Execution Workspace layout with canvas renderer, reasoning log, and profile summary panel
- [ ] 09-03: Implement execution controls (Start, Pause, Resume, Stop) communicating with backend agent controller

### Phase 10: Human-in-the-Loop Approval & Security Checkpoints

**Goal**: Enforce mandatory user approval prior to final submission and provide clean pauses for CAPTCHA/OTP resolution.
**Mode:** mvp
**Depends on**: Phase 8, Phase 9
**Requirements**: HIL-01, HIL-02, HIL-03, HIL-04
**Success Criteria** (what must be TRUE):

  1. Agent pauses before any irreversible submission action and displays a complete summary of entered data.
  2. Citizen must explicitly click "Approve & Submit" or "Reject / Edit" before submission proceeds.
  3. Agent detects CAPTCHA, SMS OTP, or MFA challenges and pauses execution with clear instructions for the citizen.
  4. Execution resumes smoothly after citizen completes the manual verification step.

**Plans**: 2 plans

Plans:

- [ ] 10-01: Implement pre-submission approval state in LangGraph with form values payload and frontend review modal
- [ ] 10-02: Implement security challenge detector (CAPTCHA/OTP/MFA) that pauses automation and prompts citizen intervention

### Phase 11: Submission Verification, Receipt Retrieval & Application Tracking

**Goal**: Verify genuine portal submission, capture acknowledgement reference numbers, retrieve official receipts, and display "My Applications".
**Mode:** mvp
**Depends on**: Phase 8, Phase 10
**Requirements**: APP-01, APP-02, APP-03, APP-04, APP-05
**Success Criteria** (what must be TRUE):

  1. Agent verifies authentic portal confirmation text and captures the genuine acknowledgement number.
  2. Official submission receipt PDF is downloaded, stored in Supabase, and linked to the application record.
  3. "My Applications" dashboard displays all user applications with timestamps, portal URLs, and current statuses.
  4. Citizen can view and download their official application submission receipt directly from the dashboard.

**Plans**: 2 plans

Plans:

- [ ] 11-01: Implement portal submission verification, acknowledgement number parsing, and receipt download pipeline
- [ ] 11-02: Build "My Applications" page displaying status badges, timeline history, and downloadable receipt links

### Phase 12: End-to-End Integration, Demonstration Polish & Production Hardening

**Goal**: Polish the complete end-to-end user journey on target official schemes, harden error handling, and finalize documentation.
**Mode:** mvp
**Depends on**: Phase 1, Phase 2, Phase 3, Phase 4, Phase 5, Phase 6, Phase 7, Phase 8, Phase 9, Phase 10, Phase 11
**Requirements**: UI-01, UI-02, UI-03, UI-04, AUTH-01, AUTH-02, AUTH-03, AUTH-04, PROF-01, PROF-02, PROF-03, PROF-04, PROF-05, DOC-01, DOC-02, DOC-03, DOC-04, DOC-05, DISC-01, DISC-02, DISC-03, DISC-04, ELIG-01, ELIG-02, ELIG-03, ELIG-04, ELIG-05, AGENT-01, AGENT-02, AGENT-03, AGENT-04, AGENT-05, AGENT-06, AGENT-07, EXEC-01, EXEC-02, EXEC-03, EXEC-04, EXEC-05, HIL-01, HIL-02, HIL-03, HIL-04, APP-01, APP-02, APP-03, APP-04, APP-05
**Success Criteria** (what must be TRUE):

  1. Complete live flow (Search -> Eligibility -> Profile -> Form Fill -> Approval -> Submission/Receipt) runs reliably.
  2. Network disconnects and edge cases gracefully display honest recovery guidance without mock fallbacks.
  3. System adheres strictly to zero-dummy-data and clean code standards.
  4. Complete setup, environment configuration, and demonstration guides are documented in `README.md`.

**Plans**: 2 plans

Plans:

- [ ] 12-01: Conduct end-to-end workflow testing against target official portals with error scenario verification
- [ ] 12-02: Finalize system documentation, README.md, .env.example, architecture diagrams, and demonstration walkthrough

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Project Foundation & MakeMyTrip Design System | 0/3 | Not started | - |
| 2. Authentication & Citizen Profile Management | 0/3 | Not started | - |
| 3. Secure Document Vault & Multimodal OCR Extraction | 0/3 | Not started | - |
| 4. Live Government Scheme Discovery & Search | 0/2 | Not started | - |
| 5. AI Eligibility Assessment Engine | 0/2 | Not started | - |
| 6. Playwright Browser Automation Core & DOM Inspection | 0/2 | Not started | - |
| 7. Dynamic Field Mapping & Form Filling Engine | 0/2 | Not started | - |
| 8. LangGraph Workflow Orchestration & Bounded Recovery | 0/2 | Not started | - |
| 9. Real-time Agent Execution Workspace & WebSockets | 0/3 | Not started | - |
| 10. Human-in-the-Loop Approval & Security Checkpoints | 0/2 | Not started | - |
| 11. Submission Verification, Receipt Retrieval & Application Tracking | 0/2 | Not started | - |
| 12. End-to-End Integration, Demonstration Polish & Production Hardening | 0/2 | Not started | - |
