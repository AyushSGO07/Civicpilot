<!-- GSD:project-start source:PROJECT.md -->

## Project

**CivicPilot**

CivicPilot is an AI-powered autonomous public service platform that simplifies access to government services by discovering relevant schemes, assessing citizen eligibility, preparing applications, and navigating complex government websites on behalf of citizens. It combines LLM-based reasoning, intelligent document extraction, browser automation via Playwright, and persistent workflow orchestration with LangGraph to transform bureaucratic hurdles into an intuitive, guided consumer experience inspired by MakeMyTrip.

**Core Value:** Autonomous, genuine navigation and execution of real government application workflows on official portals with verified eligibility and explicit human-in-the-loop approval — delivering real bureaucratic execution instead of another informational chatbot.

### Constraints

- **Integrity**: Zero dummy data. Official sources only; no fabricated numbers or simulated workflows.
- **Security**: Strict credential handling; sensitive personal data protected; explicit consent before submission.
- **Architecture**: Bounded agent actions with LangGraph state machine; browser must run in a persistent runtime environment.
- **Design System**: Consumer travel platform feel (MakeMyTrip-inspired visual hierarchy, responsive, accessible).

<!-- GSD:project-end -->

<!-- GSD:stack-start source:research/STACK.md -->

## Technology Stack

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Next.js (App Router) | 15.x | Web Frontend & Consumer Experience | Production-grade React SSR/SSG, fast routing, seamless API routes, optimal rendering performance for MakeMyTrip-style travel-grade discovery. |
| React | 19.x | UI Library | Concurrent rendering, standard component ecosystem, optimal reactivity for live agent status streaming. |
| TypeScript | 5.x | Type Safety | End-to-end type safety across domain models (citizen profiles, scheme definitions, agent events). |
| Tailwind CSS & shadcn/ui | 3.4+ / Radix | Design System & Styling | Rapid implementation of the MakeMyTrip-inspired UI (deep navy `#1A2B4C`, vibrant blue `#0056D2`, cyan accents, high-contrast cards, polished accessible primitives). |
| FastAPI | 0.115+ | Backend API & WebSocket Server | High-performance asynchronous Python runtime with native ASGI WebSocket streaming, tight Pydantic v2 integration, and clean background task management. |
| Playwright (Python) | 1.49+ | Browser Automation | Native async engine for Chromium automation, accessible tree locators, robust auto-waiting, dynamic DOM serialization, and headless/headful switching. |
| LangGraph | 0.2+ | Agent Orchestration & State Machine | Cyclical graph execution with state persistence, checkpointing, and clean human-in-the-loop interruption hooks for CAPTCHA/MFA and user approval. |
| Google GenAI SDK (`google-genai`) | 1.x / Gemini 2.5/3.0 | Multimodal Reasoning & OCR | Native structured outputs (`response_schema`), multimodal image/PDF document extraction, dynamic DOM field mapping, and zero-shot scheme eligibility evaluation. |
| Supabase (PostgreSQL + Auth + Storage) | 2.x | Cloud Database, Auth & Secure Vault | Instant robust auth (email/password, session tokens), relational schema with RLS policies, and encrypted object storage for sensitive identity documents. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| TanStack Query (React Query) | 5.x | Frontend State & Cache Management | Fetching schemes, managing profile queries, optimistic updates, and background refetches. |
| Framer Motion | 11.x | Micro-interactions & UI Transitions | Fluid card hovers, tab switches, and live progress timeline animations. |
| Lucide React | Latest | Consumer UI Iconography | Navigation, document vault icons, status indicators, and category tabs. |
| Pydantic | 2.10+ | Data Modeling & Validation | Defining strict schemas for citizen profiles, scheme models, agent execution steps, and tool payloads. |
| Beautiful Soup 4 / lxml | 4.12+ | DOM Pre-processing | Cleaning and pruning bloated government portal DOMs into accessible tree representations before LLM prompt injection. |
| PyPDF2 / pdfplumber | Latest | Document Text Preprocessing | Local extraction of text from standard digital PDFs prior to Gemini multimodal verification. |
| httpx | 0.28+ | Async HTTP Client | Calling external government data APIs (MyScheme, Data.gov.in) and web verification endpoints. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Uvicorn | ASGI Web Server | Runs FastAPI with auto-reload during development; worker processes in production. |
| Playwright CLI | Browser management | `playwright install chromium` ensures browser binaries are provisioned. |
| ESLint & Prettier | Code quality | Enforces standard TypeScript and React code conventions. |
| Python venv / uv | Python package management | Fast, isolated Python virtual environments. |

## Installation

### Frontend

# Core & UI

### Backend

# Windows:

# Linux/macOS:

# source venv/bin/activate

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Next.js App Router | Vite + React SPA | Use Vite if SSR and Next.js server actions are completely unnecessary; Next.js was selected for superior SEO, routing, and integrated API proxying. |
| FastAPI | Node.js / Express | Node is viable, but Python has vastly superior first-class libraries for browser automation (Playwright async), LangGraph state orchestration, and AI evaluation tooling. |
| LangGraph | Browser-Use standalone | Browser-Use is great for end-to-end unconstrained browsing, but LangGraph provides strict deterministic checkpoints (crucial for human approval and CAPTCHA pause gates). A hybrid approach (LangGraph controlling Playwright actions with Gemini vision/DOM analysis) provides predictable execution. |
| Gemini API (`google-genai`) | OpenAI GPT-4o | Gemini provides 1M+ token context windows (allowing complete DOM snapshots without severe truncation), built-in multimodal document processing, and ultra-fast structured outputs. |
| Supabase | Custom PostgreSQL + S3 | Custom setup requires significant DevOps boilerplate; Supabase gives instant PostgreSQL, RLS, Auth, and Storage in one unified platform. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Selenium WebDriver | Heavy, synchronous, prone to flakiness, lacks native modern async/await and accessibility locators. | Playwright (fast, async, robust auto-waiting, modern accessibility locators). |
| Hardcoded element coordinate clicking | Fragile; completely breaks on varying screen resolutions or responsive layout shifts on government portals. | Accessible locators (`getByRole`, `getByLabelText`, `getByText`) and semantic DOM parsing. |
| Client-side direct browser automation | Impossible to maintain persistent sessions, bypass CORS, or execute headless Playwright from a web browser. | Server-side FastAPI automation worker streaming live screenshots/events via WebSockets. |
| Unbounded autonomous execution loops | Agents can enter infinite loops or drain tokens on stubborn government forms. | LangGraph bounded retries (max 3 attempts per step) with human fallback. |
| Mock data / fabricated portal responses | Explicit violation of hackathon integrity rules. | Live portals, genuine MyScheme endpoints, and honest "unsupported" fallbacks. |

## Stack Patterns by Variant

- LangGraph enters `WAITING_FOR_USER_ACTION` state.
- WebSocket emits event to frontend asking citizen to complete step.
- Agent pauses browser interaction until user clicks "I have completed OTP/CAPTCHA" in the UI.
- Run local DOM prune via BeautifulSoup to extract only interactive elements (`<input>`, `<select>`, `<button>`, `<form>`, labels).
- Feed pruned semantic tree to Gemini structured output prompt.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| `fastapi@>=0.115` | `pydantic@>=2.10` | Uses Pydantic v2 Core for ultra-fast schema serialization. |
| `langgraph@>=0.2` | `langchain@>=0.3` | Modern LangGraph architecture with checkpointing. |
| `google-genai@>=1.0` | Python 3.10+ | Official Google GenAI SDK for Gemini 2.5/3.0. |
| `next@15.x` | `react@19.x` | Compatible with latest Next.js App Router patterns. |

## Sources

- Official Playwright Documentation: https://playwright.dev/python/
- Official LangGraph Documentation: https://langchain-ai.github.io/langgraph/
- Official Google GenAI SDK Documentation: https://github.com/googleapis/python-genai
- Official FastAPI Documentation: https://fastapi.tiangolo.com/
- Supabase Documentation: https://supabase.com/docs

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
