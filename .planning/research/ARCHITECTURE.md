# Architecture Research

**Domain:** Autonomous Public Service & Bureaucracy Execution Agent
**Researched:** 2026-11-01
**Confidence:** HIGH

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       Next.js Frontend (App Router)                         │
│  ┌───────────────────────┐ ┌────────────────────────┐ ┌───────────────────┐ │
│  │ MakeMyTrip Discovery  │ │ Document Vault / OCR   │ │ Agent Workspace   │ │
│  │ (Search, Filter, Rec) │ │ (Upload, Preview, Edit)│ │ (Canvas, Log, Ctls)│ │
│  └───────────┬───────────┘ └───────────┬────────────┘ └─────────┬─────────┘ │
├──────────────┼─────────────────────────┼────────────────────────┼───────────┤
│              │ REST API                │ File Upload            │ WebSocket │
│              ▼                         ▼                        ▼           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                     FastAPI Application Gateway                       │  │
│  │   Auth & Profile  │  Services & Search  │  Agent Session Manager      │  │
│  └───────────────────┴─────────────────────┴─────────────┬───────────────┘  │
├──────────────────────────────────────────────────────────┼──────────────────┤
│                                                          │ Dispatches       │
│  ┌─────────────────────────┐                             ▼                  │
│  │ LangGraph State Machine ├──────────► ┌────────────────────────────────┐  │
│  │  - Checkpoints & States │            │ Playwright Automation Worker   │  │
│  │  - Approval Gates       │            │  - Headless/Headful Chromium   │  │
│  │  - Error Recovery       │            │  - DOM Tree & Locators         │  │
│  └────────────┬────────────┘            │  - Screenshot Buffer Generator │  │
│               │                         └────────────────┬───────────────┘  │
│               │ Semantic Mapping                         │ DOM / Vision     │
│               ▼                                          ▼                  │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                 Google GenAI / Gemini API Reasoning Layer             │  │
│  │  - Document OCR Extraction   - Dynamic Field Mapper                   │  │
│  │  - Scheme Eligibility Logic  - Action Planner & Error Diagnoser       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────────┤
│                          Data & Storage Layer                                │
│  ┌───────────────────────────────────────┐ ┌─────────────────────────────┐  │
│  │         Supabase PostgreSQL           │ │      Supabase Storage       │  │
│  │  users, citizen_profiles, documents,  │ │  citizen-vault (Encrypted   │  │
│  │  government_services, applications,   │ │  Aadhaar, Marks, Receipts)  │  │
│  │  agent_sessions, agent_events         │ │                             │  │
│  └───────────────────────────────────────┘ └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Next.js Frontend** | MakeMyTrip-inspired visual presentation, user interaction, profile editing, real-time WebSocket consumption, and browser streaming view. | Next.js 15, Tailwind CSS, shadcn/ui, TanStack Query, native HTML5 canvas/image rendering for browser feed. |
| **FastAPI Backend** | API endpoint orchestration, Supabase authentication token verification, WebSocket lifecycle, file dispatch, and process supervision. | FastAPI async routers, Pydantic schemas, WebSocket manager. |
| **LangGraph Orchestrator** | Stateful execution workflow representing the public service lifecycle: understanding, discovery, planning, mapping, filling, approval, and submission. | LangGraph `StateGraph`, MemorySaver checkpointing, conditional interrupt nodes. |
| **Playwright Worker** | Concrete interaction with target government web pages: navigating URLs, taking DOM snapshots, typing, selecting dropdowns, uploading files, capturing receipts. | Async Playwright with Chromium, custom DOM extraction script, screenshot emitter. |
| **Gemini AI Engine** | High-level cognition: parsing uploaded document images/PDFs into structured data, evaluating user profile against official eligibility rules, and mapping citizen JSON fields to portal DOM elements. | Google GenAI SDK (`google-genai`), `gemini-2.5-pro` / `gemini-2.5-flash` with JSON structured outputs. |
| **Supabase Cloud** | Secure storage of citizen credentials, profile metadata, official service cache, execution event logs, and private encrypted document vaults. | Supabase PostgreSQL + Row Level Security (RLS) + Private Storage Buckets. |

## Recommended Project Structure

```
CivicPilot/
├── frontend/                     # Next.js 15 App Router Frontend
│   ├── app/                      # Application routes
│   │   ├── layout.tsx            # Root layout with MakeMyTrip theme & navbar
│   │   ├── page.tsx              # Landing & Discovery Dashboard
│   │   ├── services/             # Scheme discovery & search
│   │   │   └── page.tsx
│   │   ├── profile/              # Citizen profile management
│   │   │   └── page.tsx
│   │   ├── documents/            # Document Vault & OCR verification
│   │   │   └── page.tsx
│   │   ├── agent/                # Live Agent Execution Workspace
│   │   │   └── [sessionId]/page.tsx
│   │   └── applications/         # My Applications tracking
│   │       └── page.tsx
│   ├── components/               # Reusable UI components
│   │   ├── ui/                   # shadcn/ui primitive components
│   │   ├── navbar.tsx            # Global navigation bar
│   │   ├── hero-search.tsx       # MakeMyTrip-inspired search & category bar
│   │   ├── service-card.tsx      # Rich scheme card with eligibility badge
│   │   ├── agent-workspace/      # Live browser canvas, event timeline, controls
│   │   └── document-uploader.tsx # Document upload & OCR preview modal
│   ├── lib/                      # Utilities, API client, Supabase client
│   │   ├── api.ts                # Backend REST client
│   │   └── supabase.ts           # Supabase browser client
│   └── types/                    # Shared TypeScript interfaces
├── backend/                      # FastAPI Python Application
│   ├── app/
│   │   ├── main.py               # FastAPI entry point & CORS configuration
│   │   ├── config.py             # App settings (Supabase, Gemini API keys)
│   │   ├── routers/              # Modular API endpoints
│   │   │   ├── auth.py           # User registration & session checks
│   │   │   ├── profile.py        # Citizen profile CRUD
│   │   │   ├── documents.py      # Document upload, OCR trigger, deletion
│   │   │   ├── services.py       # Scheme catalog search & eligibility
│   │   │   ├── agent.py          # Session launch, control, and status
│   │   │   ├── applications.py   # Application records & status refresh
│   │   │   └── ws.py             # WebSocket endpoint `/ws/agent/{session_id}`
│   │   ├── agent/                # Autonomous Agent Core
│   │   │   ├── graph.py          # LangGraph state machine definition
│   │   │   ├── state.py          # AgentState TypedDict definition
│   │   │   ├── browser.py        # Playwright controller & DOM extractor
│   │   │   ├── mapper.py         # Dynamic Gemini DOM-to-Profile field mapper
│   │   │   └── recovery.py       # Bounded error detection and recovery logic
│   │   ├── services/             # Business logic & External integrations
│   │   │   ├── gemini_service.py # Gemini multimodal extraction & reasoning
│   │   │   ├── myscheme.py       # Official government scheme ingestion
│   │   │   ├── storage.py        # Supabase storage wrapper
│   │   │   └── db.py             # Supabase PostgreSQL client
│   │   └── models/               # Pydantic schemas
│   │       ├── profile.py
│   │       ├── document.py
│   │       ├── service.py
│   │       └── agent.py
│   ├── requirements.txt          # Python dependencies
│   └── tests/                    # Backend unit & integration tests
├── supabase/                     # Database migrations & schemas
│   └── schema.sql                # Complete PostgreSQL table definitions & RLS
├── specs.md                      # Product and engineering specification
└── README.md                     # Setup, architecture & running instructions
```

## Architectural Patterns

### Pattern 1: LangGraph Checkpointed State Machine with Human Interruption

**What:** A cyclical state machine where transitions between stages (Inspection → Mapping → Filling → Approval → Submission) are managed as a pure state object. Irreversible actions (submission) or user-required steps (CAPTCHA, OTP, Approval) yield execution control back to the client via WebSockets.

**When to use:** Crucial for public bureaucracy where accidental automated submission is prohibited, and external verification steps are mandatory.

**Example:**
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, List

class AgentState(TypedDict):
    session_id: str
    user_id: str
    service: dict
    citizen_profile: dict
    documents: List[dict]
    current_url: str
    dom_snapshot: Optional[str]
    mapped_fields: dict
    approval_granted: bool
    captcha_detected: bool
    status: str
    ack_number: Optional[str]
    error_count: int

def build_workflow():
    workflow = StateGraph(AgentState)
    workflow.add_node("discover_portal", discover_portal_node)
    workflow.add_node("inspect_and_map", inspect_and_map_node)
    workflow.add_node("fill_form", fill_form_node)
    workflow.add_node("await_approval", await_approval_node)
    workflow.add_node("submit_and_verify", submit_and_verify_node)

    workflow.set_entry_point("discover_portal")
    workflow.add_edge("discover_portal", "inspect_and_map")
    workflow.add_edge("inspect_and_map", "fill_form")
    workflow.add_edge("fill_form", "await_approval")
    workflow.add_conditional_edges(
        "await_approval",
        should_submit,
        {"approved": "submit_and_verify", "rejected": END, "retry": "inspect_and_map"}
    )
    workflow.add_edge("submit_and_verify", END)
    return workflow.compile(interrupt_before=["await_approval"])
```

### Pattern 2: Semantic DOM Extraction Before LLM Injection

**What:** Government portal HTML is notoriously verbose, filled with legacy inline styles, scripts, and invisible nested tables. Instead of passing raw HTML (which causes token bloat and hallucination), the browser worker parses the DOM with BeautifulSoup/Playwright, stripping scripts, SVG paths, and decorative elements to produce a concise semantic element tree.

**When to use:** In `inspect_and_map_node` before sending the page state to Gemini.

**Trade-offs:** Drops non-semantic visual positioning, but provides 90% token reduction and 100% deterministic field identification.

### Pattern 3: Dual WebSocket Stream (Events + Live Base64 Frame Buffer)

**What:** The FastAPI backend maintains an active WebSocket per session. When Playwright completes an action or state changes, it emits structured JSON events (`type: "LOG"`, `type: "FIELD_FILLED"`, `type: "SCREENSHOT"`). The frontend renders the screenshot frame on an HTML5 canvas and appends the log to the timeline without full page reloads.

## Data Flow

### Application Filing Flow

```
1. Citizen selects Scheme & clicks "Apply with CivicPilot"
       ↓
2. Backend generates Session ID & instantiates LangGraph Agent
       ↓
3. Frontend opens Execution Workspace & connects to `/ws/agent/{sessionId}`
       ↓
4. Agent opens Playwright Chromium & navigates to Official Portal URL
       ↓ (Emits SCREENSHOT & EVENT: PORTAL_OPENED)
5. Agent extracts DOM -> Gemini maps Citizen Profile fields to HTML inputs
       ↓ (Emits EVENT: FIELDS_MAPPED)
6. Agent populates inputs & attaches verified documents from Vault
       ↓ (Emits EVENT: FORM_POPULATED)
7. Agent triggers validation -> Detects clean state -> PAUSES for Approval
       ↓ (Emits EVENT: APPROVAL_REQUIRED with form summary)
8. User reviews summary in UI & clicks "Approve & Submit"
       ↓ (Frontend POST /api/agent/{sessionId}/approve)
9. Agent executes submission -> Captures genuine acknowledgement number
       ↓ (Emits EVENT: APPLICATION_SUBMITTED with Ref Number & Receipt)
10. Application record saved to Supabase -> Appears in "My Applications"
```

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **Development / Hackathon (1-10 concurrent sessions)** | Single FastAPI instance with Playwright running locally in async worker pool. |
| **Small Scale (10-100 concurrent sessions)** | Dockerized worker nodes on Railway/Render; Celery or Redis task queue distributing Playwright browser tasks across dedicated containers. |
| **Production Scale (10,000+ citizens)** | Decoupled Playwright pool on AWS Fargate or Kubernetes; ephemeral browser containers with Redis session storage and Supabase Realtime clustering. |

## Sources

- Playwright Async API Best Practices: https://playwright.dev/python/docs/library
- LangGraph Orchestration Reference: https://langchain-ai.github.io/langgraph/concepts/high_level/
- FastAPI WebSockets Specification: https://fastapi.tiangolo.com/advanced/websockets/

---
*Architecture research for: Autonomous Public Service & Bureaucracy Execution Agent*
*Researched: 2026-11-01*
