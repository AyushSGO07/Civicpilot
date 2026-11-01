# Project Research Summary

**Project:** CivicPilot
**Domain:** Autonomous Public Service & Bureaucracy Execution Agent
**Researched:** 2026-11-01
**Confidence:** HIGH

## Executive Summary

CivicPilot is an AI-powered autonomous public service execution platform that simplifies access to Indian government services by discovering legitimate schemes, evaluating citizen eligibility, extracting information from identity documents, and navigating complex government web portals on behalf of citizens. Built with a MakeMyTrip-inspired visual hierarchy, it replaces the frustrating, opaque experience of public bureaucracy with an intuitive, trustworthy, guided consumer flow.

Unlike traditional informational chatbots that merely link to external portals or recite rules, CivicPilot actively executes application workflows. The system is engineered around a dual-engine architecture: a responsive Next.js 15 frontend providing real-time transparency via WebSockets, paired with a FastAPI backend orchestrating a stateful LangGraph agent and an asynchronous Playwright browser engine. Google Gemini API powers multimodal document OCR extraction, dynamic semantic form mapping, and eligibility reasoning.

A primary technical imperative is strict compliance with the hackathon's "Zero Dummy Data" policy. The system strictly interacts with live official portals and scheme databases (MyScheme, National Scholarship Portal, India.gov.in), maintains authentic timestamps and source URLs, enforces bounded error recovery, and includes explicit human-in-the-loop checkpoints before any irreversible submission or security verification (CAPTCHA/OTP).

## Key Findings

### Recommended Stack

The architecture combines Next.js 15 for a polished, consumer-grade travel-style discovery experience with a robust Python FastAPI backend for AI and browser automation.

**Core technologies:**
- **Next.js 15 (App Router) + Tailwind CSS + shadcn/ui**: Consumer-grade visual hierarchy inspired by MakeMyTrip (deep navy `#1A2B4C`, vibrant blue `#0056D2`, cyan accents, light background `#F5F7FB`).
- **FastAPI (Python 3.11+)**: Asynchronous API gateway with native WebSocket streaming for real-time agent event broadcast.
- **Playwright (Python)**: Modern, async browser automation using accessible tree locators and dynamic DOM inspection.
- **LangGraph**: Stateful, cyclical workflow engine with checkpointing and human-in-the-loop interruption capabilities.
- **Google GenAI SDK (`google-genai` / Gemini 2.5/3.0)**: Multimodal document OCR, dynamic DOM-to-profile field mapping, and zero-shot eligibility evaluation.
- **Supabase (PostgreSQL, Auth, Storage)**: Unified user authentication, relational schemas with RLS, and secure private vault for citizen documents.

### Expected Features

**Must have (table stakes):**
- Supabase email authentication and persistent sessions.
- Comprehensive citizen profile (personal, educational, address, voluntary eligibility criteria).
- Secure Document Vault with Gemini multimodal OCR extraction for auto-filling.
- Live scheme discovery and natural language search powered by official government sources.
- AI Eligibility Assistant comparing profile attributes against scheme criteria with citations.
- Human Approval Gate presenting a full summary of entered data and files before submission.
- My Applications dashboard tracking genuine submission statuses and receipts.

**Should have (competitive differentiators):**
- Autonomous Playwright browser agent capable of dynamic multi-step form population.
- Agent Operations Workspace with live browser preview, WebSocket event timeline, and execution controls (Pause, Resume, Stop, Approve).
- Dynamic semantic DOM mapping resilient to changes in government portal HTML.
- Bounded error recovery handling timeouts, modal dialogs, and field validation mismatches.
- Genuine receipt and acknowledgement number retrieval and archiving.

**Defer (v2+):**
- Multilingual regional voice navigation and WhatsApp notification alerts.
- Direct Digilocker API integration.

### Architecture Approach

The system employs a client-server architecture with bidirectional real-time communication. The Next.js frontend connects to FastAPI via REST and WebSockets (`/ws/agent/{sessionId}`). The FastAPI backend spins up a LangGraph state machine which commands an async Playwright browser. As the browser navigates official government portals, Playwright extracts sanitized semantic DOM trees and transmits them to Gemini for dynamic field mapping. Screenshots and progress events are streamed back to the user's workspace in real-time.

**Major components:**
1. **Frontend Operations UI**: MakeMyTrip discovery dashboard, Document Vault, and the 3-panel Agent Workspace.
2. **LangGraph Workflow Orchestrator**: Stateful state machine managing the application lifecycle and approval pauses.
3. **Playwright Browser Worker**: Async Chromium process executing concrete webpage actions and capturing receipts.
4. **Gemini Multimodal Reasoning Engine**: Document parser, dynamic field mapper, and eligibility evaluator.
5. **Supabase Cloud Infrastructure**: PostgreSQL relational database, Auth, and encrypted document storage.

### Critical Pitfalls

1. **Fragile Portal Selectors**: Government portals change HTML IDs frequently. *Avoided by using semantic DOM extraction and Gemini field mapping rather than hardcoded CSS selectors.*
2. **Infinite Loops & Stalls**: Unhandled validation errors causing repeated clicks. *Avoided by enforcing bounded retries (max 3) and page-state diffing before re-action.*
3. **Zero-Dummy-Data Violation**: Mocking data or fabricating receipts. *Avoided by exclusively querying live government sources (MyScheme) and executing against real portal URLs.*
4. **CAPTCHA / Security Bypassing**: Trying to solve or bypass security checks. *Avoided by implementing clean Human-in-the-Loop pause and resume flows.*
5. **Orphaned Browser Instances**: Playwright processes consuming RAM. *Avoided by using async context managers and automated session reaping.*

## Implications for Roadmap

Based on the research and the user's choice of **Fine Granularity (8-12 focused phases)**, the proposed roadmap breaks down into cohesive, verifiable increments:

### Phase 1: Project Foundation & Design System
**Rationale:** Establishes the dual-stack development environment, base UI components, and design language.
**Delivers:** Initialized Next.js frontend with MakeMyTrip styling (navy/blue/cyan theme), FastAPI backend shell with health endpoints, and database schema setup in Supabase.
**Addresses:** UI design system, development infrastructure.

### Phase 2: Authentication & Citizen Profile Management
**Rationale:** Citizen profile data is the prerequisite for both eligibility checking and form mapping.
**Delivers:** Supabase email registration, login, session persistence, and full citizen profile management (personal, address, educational info).
**Addresses:** AUTH-01, PROF-01.

### Phase 3: Secure Document Vault & Multimodal OCR Extraction
**Rationale:** Government forms require supporting proofs; uploading and extracting them upfront enables automated form filling.
**Delivers:** Supabase private storage bucket, file upload/preview, and Gemini multimodal OCR pipeline that extracts data from Aadhaar, PAN, and marksheets into the citizen profile.
**Addresses:** DOC-01, DOC-02.
**Avoids:** Insecure local file storage pitfall.

### Phase 4: Live Government Scheme Discovery & Search
**Rationale:** Citizens must discover verified schemes before applying.
**Delivers:** Ingestion and caching of genuine government schemes (MyScheme / National Portal), category-based filtering, and natural language semantic search.
**Addresses:** DISC-01.
**Avoids:** Zero-dummy-data violation pitfall.

### Phase 5: AI Eligibility Assessment Engine
**Rationale:** Citizens need definitive guidance on whether they qualify before launching an application agent.
**Delivers:** Gemini reasoning endpoint that compares citizen profile data against official scheme rules, surfaces missing information, and provides reasoned verdicts with citations.
**Addresses:** ELIG-01.

### Phase 6: Playwright Browser Automation Core & DOM Inspection
**Rationale:** Foundation for all autonomous portal execution.
**Delivers:** Asynchronous Playwright browser management service, page navigation, accessibility-based DOM extraction, and lifecycle cleanup (preventing zombie processes).
**Addresses:** AGENT-02 (Foundation).
**Avoids:** Browser process leak pitfall.

### Phase 7: Dynamic Field Mapping & Form Filling Engine
**Rationale:** Bridges citizen profile data with portal input fields dynamically.
**Delivers:** Gemini-powered semantic field mapper, automated form population (text, dropdowns, checkboxes, file attachments), and pre-submission validation.
**Addresses:** AGENT-02 (Mapping & Filling).
**Avoids:** Fragile hardcoded selector pitfall.

### Phase 8: LangGraph Workflow Orchestration & Bounded Recovery
**Rationale:** Unifies browser actions into a reliable state machine with error handling.
**Delivers:** LangGraph state graph with checkpointing, bounded retry logic (max 3 retries), unexpected modal detection, and state restoration.
**Addresses:** AGENT-01, AGENT-03.
**Avoids:** Infinite loop pitfall.

### Phase 9: Real-time Agent Execution Workspace & WebSockets
**Rationale:** Gives citizens complete visibility and control over the autonomous agent.
**Delivers:** Three-panel operations dashboard: citizen profile on left, live browser visual stream in center, AI reasoning & event timeline on right, with Pause/Resume/Stop controls.
**Addresses:** EXEC-01.

### Phase 10: Human-in-the-Loop Approval & Security Checkpoints
**Rationale:** Ensures citizen consent, safety, and compliance with government security controls.
**Delivers:** Pre-submission summary modal, explicit "Approve & Submit" gate, and detection/pausing for manual CAPTCHA/OTP resolution.
**Addresses:** AGENT-04.
**Avoids:** CAPTCHA bypassing / legal violation pitfall.

### Phase 11: Submission Verification, Receipt Retrieval & Application Tracking
**Rationale:** Completes the end-to-end execution loop and provides persistent tracking.
**Delivers:** Genuine portal submission confirmation check, reference number capture, official receipt document download/storage, and the "My Applications" dashboard.
**Addresses:** AGENT-05, APP-01.
**Avoids:** Fabricated receipt pitfall.

### Phase 12: End-to-End Integration, Demonstration Polish & Production Hardening
**Rationale:** Final packaging and stress testing for hackathon demonstration.
**Delivers:** Polished end-to-end flow on targeted official scholarship/scheme portal, comprehensive documentation, error scenario fallbacks, and performance optimization.
**Addresses:** System reliability, hackathon demo readiness.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Next.js 15, FastAPI, Playwright, LangGraph, and Gemini are well-documented, proven industry standards. |
| Features | HIGH | Detailed in specification; table stakes vs differentiators clearly delineated. |
| Architecture | HIGH | Decoupled client-server model with WebSocket streaming ensures stability and clean separation of concerns. |
| Pitfalls | HIGH | Specific public-sector automation failure modes identified with concrete mitigations. |

**Overall confidence:** HIGH

### Gaps to Address During Implementation

- **Target Portal Selection**: Selecting the most reliable official portal for live demonstration (e.g. National Scholarship Portal demo/registration workflow or MyScheme guided application flow) to ensure high uptime during demo day.
- **WebSocket Reconnection**: Ensuring the frontend gracefully reconnects and restores the browser view if a temporary network blip occurs during agent execution.

## Sources

### Primary (HIGH confidence)
- Official Playwright Documentation: https://playwright.dev/python/docs/library
- Official LangGraph StateGraph Documentation: https://langchain-ai.github.io/langgraph/
- Google GenAI SDK: https://github.com/googleapis/python-genai
- Next.js Documentation: https://nextjs.org/docs

### Secondary (MEDIUM confidence)
- MyScheme Public API & Scheme Data structures: https://www.myscheme.gov.in/
- National Scholarship Portal Workflow Guide: https://scholarships.gov.in/

---
*Research completed: 2026-11-01*
*Ready for roadmap: yes*
