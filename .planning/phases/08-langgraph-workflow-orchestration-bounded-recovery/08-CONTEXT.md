---
phase: "08"
name: "langgraph-workflow-orchestration-bounded-recovery"
created: 2026-11-01
---

# Phase 08: LangGraph Workflow Orchestration & Bounded Recovery — Context

## User Constraints

### Locked Decisions
- **D-01 (LangGraph State Machine):** Construct a cyclical graph using LangGraph 0.2+ (`StateGraph`) with state persistence and checkpoints. Nodes represent: Discovery, Navigation, Inspection, Mapping, Filling, Validation, Recovery, and Human Assistance.
- **D-02 (Bounded Error Recovery - Max 3 Retries):** Agent detects element timeouts, validation alerts, and unexpected popup/dialog challenges. It attempts bounded recovery up to a strict maximum of 3 retries (AGENT-06).
- **D-03 (Graceful Fallback to Human Assistance):** If errors persist after 3 retries, or if an unresolvable portal blocker is detected, the workflow transitions safely to `WAITING_FOR_HUMAN_ASSISTANCE` rather than failing catastrophically or looping indefinitely (AGENT-06).
- **D-04 (Dialog & Alert Handlers):** Attach automated Playwright dialog handlers (`page.on("dialog")`) to dismiss unexpected informational alerts while recording message text in workflow state for transparency.
- **D-05 (State Persistence & Checkpoints):** Utilize LangGraph checkpointing (`MemorySaver`) so execution state can be paused, inspected, and resumed seamlessly.
- **D-06 (FastAPI Workflow Controller Endpoints):**
  - `POST /api/agent/workflow/start`: Launches LangGraph workflow for a scheme and returns `thread_id` and initial state.
  - `GET /api/agent/workflow/{thread_id}/state`: Retrieves current node, step logs, screenshot, and status.
  - `POST /api/agent/workflow/{thread_id}/resume`: Resumes a paused workflow (e.g. after human review).

### Discretion Areas
- Routing conditions between `validate` and `recovery` (e.g. criteria for failed vs warning actions).
- Checkpointer type (in-memory `MemorySaver` for MVP performance and zero external dependencies).

### Deferred Ideas
- Real-time WebSocket streaming of node transitions and reasoning logs to frontend (Phase 9).
- Mandatory pre-submission user approval gate (Phase 10 - HIL-01).
