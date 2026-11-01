# Phase 09: Real-time Agent Execution Workspace & WebSockets — Validation Plan

## Test Strategy

Phase 09 introduces the WebSocket streaming pipeline, execution controller (Pause, Resume, Stop), and the MakeMyTrip 3-panel operations workspace.

Validation consists of:
1. Automated backend pytest tests (`backend/tests/test_agent_websocket.py`) validating WebSocket connections, frame serialization, milestone broadcasting, and control signals (Pause, Resume, Stop).
2. Next.js App Router compilation (`npm --prefix frontend run build`) verifying clean static/dynamic compilation of `/applications/workspace/[sessionId]` and `/applications/new`.
3. Full backend test regression verification (`pytest backend/tests/ -v`).

---

## Test Cases (`backend/tests/test_agent_websocket.py`)

| Test Name | Test Condition | Expected Result |
|---|---|---|
| `test_websocket_connection_and_handshake` | Client connects to `/ws/agent/{sessionId}` | Handshake succeeds, welcome frame received with status `idle` or `active` |
| `test_websocket_milestone_broadcasting` | Emit milestone via `websocket_manager.broadcast_milestone()` | Connected client receives JSON frame with `type: "milestone"`, message, and step (EXEC-02) |
| `test_websocket_screenshot_broadcasting` | Emit visual frame via `websocket_manager.broadcast_screenshot()` | Connected client receives frame with `type: "screenshot"` and Base64 buffer (EXEC-03) |
| `test_websocket_pause_resume_signals` | Client sends `{"action": "pause"}` then `{"action": "resume"}` | Controller toggles `is_paused`, broadcasts status update, unblocks pause gate (EXEC-04) |
| `test_websocket_stop_signal` | Client sends `{"action": "stop"}` | Controller aborts execution, closes browser context, broadcasts status `stopped` (EXEC-05) |

---

## Acceptance Criteria Checklist

- [ ] All tests in `backend/tests/test_agent_websocket.py` pass.
- [ ] WebSocket streaming delivers milestone logs and visual frames without drops.
- [ ] Pause, Resume, and Stop controls respond immediately.
- [ ] Frontend 3-panel workspace builds with 0 errors and 0 warnings.
