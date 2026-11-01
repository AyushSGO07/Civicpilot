# Phase 09: Real-time Agent Execution Workspace & WebSockets — Research & Architecture

## Objective

Design and implement a real-time 3-panel operations workspace streaming live browser visual updates, step-by-step AI reasoning logs, and interactive controls (Pause, Resume, Abort) over WebSockets at `/ws/agent/{sessionId}`.

---

## 1. Requirements Mapping

| ID | Requirement | Implementation Strategy |
|---|---|---|
| **EXEC-01** | User can monitor real-time execution in a 3-panel operations workspace | Frontend layout at `/applications/workspace/[sessionId]`: Left = Profile & Vault Summary, Center = Live Browser Viewport, Right = AI Reasoning Log. |
| **EXEC-02** | User receives real-time progress events streamed over WebSockets | FastAPI WebSocket endpoint at `/ws/agent/{sessionId}` emitting JSON status and milestone events. |
| **EXEC-03** | User can watch live browser visual screenshots updated as agent interacts | `broadcast_screenshot` streams Base64 JPEG frames to WebSocket clients on every navigation, step, and form fill action. |
| **EXEC-04** | User can pause and resume the browser agent's autonomous execution | `SessionExecutionController` manages `asyncio.Event` pause gates. Client sends `{"action": "pause"}` or `{"action": "resume"}`. |
| **EXEC-05** | User can abort execution at any time, halting the browser safely | Client sends `{"action": "stop"}`; controller halts loop and terminates Chromium context cleanly (`browser_manager.close_session()`). |

---

## 2. Real-time Communication Architecture

```
[Playwright Browser & LangGraph Engine]
           │
           │ (Milestones, DOM events, screenshots)
           ▼
[AgentWebSocketManager & SessionExecutionController]
           │
           │  WebSocket (/ws/agent/{sessionId})
           ▼
[Frontend 3-Panel Workspace]
 ├── Panel 1: Profile Summary (Left 1/4)
 ├── Panel 2: Live Viewport Canvas (Center 2/4)
 └── Panel 3: AI Reasoning Log (Right 1/4)
```

---

## 3. WebSocket Event Protocols

### Backend to Frontend (Outbound Frames)
1. **Status Update**:
```json
{
  "type": "status",
  "status": "navigating" | "inspecting" | "mapping" | "filling" | "paused" | "stopped" | "completed" | "error",
  "step": "navigation",
  "timestamp": "2026-11-01T12:00:00Z"
}
```
2. **Milestone / Reasoning Log**:
```json
{
  "type": "milestone",
  "step": "mapping",
  "message": "Dynamically mapped citizen full name 'Aarav Sharma' to #txtApplicantName",
  "level": "info" | "warning" | "success" | "error",
  "timestamp": "2026-11-01T12:00:01Z"
}
```
3. **Screenshot Buffer**:
```json
{
  "type": "screenshot",
  "screenshot_base64": "/9j/4AAQSkZJRg...",
  "timestamp": "2026-11-01T12:00:02Z"
}
```

### Frontend to Backend (Inbound Control Actions)
```json
{ "action": "pause" }
{ "action": "resume" }
{ "action": "stop" }
{ "action": "start", "service_id": "pm-usp-scholarship" }
```

---

## 4. Execution Controller & Pause Gate (EXEC-04, EXEC-05)

```python
class SessionExecutionController:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.pause_event = asyncio.Event()
        self.pause_event.set()  # Unpaused initially
        self.stop_event = asyncio.Event()
        self.is_paused = False
        self.is_stopped = False

    async def check_gate(self):
        """Await pause event or abort if stopped."""
        if self.is_stopped:
            raise asyncio.CancelledError("Execution aborted by citizen")
        await self.pause_event.wait()
```
Every form interaction step checks `await controller.check_gate()`. When the citizen clicks **Pause**, `pause_event.clear()` suspends execution in place without killing the browser. When they click **Resume**, `pause_event.set()` instantly resumes execution. When they click **Stop**, `stop_event.set()` cancels the loop and shuts down the browser context cleanly.
