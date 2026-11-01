---
phase: "09"
name: "real-time-agent-execution-workspace-websockets"
created: 2026-11-01
---

# Phase 09: Real-time Agent Execution Workspace & WebSockets — Context

## User Constraints

### Locked Decisions
- **D-01 (3-Panel Operations Workspace):** Citizen monitors real-time browser execution in a dedicated 3-panel operations workspace: Left Panel = Citizen Profile & Vault Summary, Center Panel = Live Browser Stream & Viewport, Right Panel = AI Reasoning & Audit Log (EXEC-01).
- **D-02 (WebSocket Event Streaming):** All milestones, status changes, and Base64 visual frames stream live over native WebSockets at `/ws/agent/{sessionId}` with clean reconnect logic (EXEC-02, EXEC-03).
- **D-03 (Execution Controls - Pause, Resume, Abort):** Interactive controls allow the citizen to Pause, Resume, and Stop/Abort execution at any moment. Playwright browser and LangGraph state respond immediately (EXEC-04, EXEC-05).
- **D-04 (MakeMyTrip Theme Consistency):** Dark/sleek viewport canvas (`bg-slate-900`), Navy headers (`#1A2B4C`), Civic Blue accents (`#0056D2`), Cyan live indicators (`#00B4D8`), and high-contrast status pills (pulsing green "LIVE", amber "PAUSED", red "STOPPED").
- **D-05 (Fallback Offline Simulation):** When viewing workspace in preview or offline without live browser execution, provides an automated playback / mock frame generator so reviewers and judges can test the full 3-panel workspace experience.

### Discretion Areas
- Frame rate / screenshot throttling (1-2 FPS or milestone-driven snapshots to avoid saturating network while maintaining responsive live feel).
- Log filtering (toggle between "All Logs" and "AI Reasoning Only").

### Deferred Ideas
- Pre-submission approval summary modal (Phase 10 - HIL-01, HIL-02).
- Final portal receipt retrieval and downloading (Phase 11 - APP-01, APP-02).
