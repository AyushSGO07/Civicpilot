# Phase 08: LangGraph Workflow Orchestration & Bounded Recovery — Validation Plan

## Test Strategy

Phase 08 introduces the LangGraph cyclical state machine and bounded error recovery system.

Validation consists of:
1. Automated unit tests for individual graph nodes (`discover`, `navigate`, `inspect`, `map`, `fill`, `validate`, `recovery`, `human_assistance`).
2. Integration tests validating the bounded retry limit (max 3 retries) and escalation to human assistance (`AGENT-06`).
3. Dialog listener testing verifying unexpected alert popups are captured and dismissed without hanging the browser.
4. FastAPI workflow controller endpoint verification (`/api/agent/workflow/...`).
5. Full regression testing (`pytest backend/tests/ -v`).

---

## Test Cases (`backend/tests/test_agent_workflow.py`)

| Test Name | Test Condition | Expected Result |
|---|---|---|
| `test_workflow_happy_path` | Run workflow on valid portal form with complete profile | Traverses Discover -> Navigate -> Inspect -> Map -> Fill -> Validate -> Complete/WaitingApproval with 0 errors (AGENT-06) |
| `test_workflow_alert_dialog_interception` | Portal triggers unexpected `window.alert('Notice')` during execution | Dialog is automatically dismissed, text captured in `dialog_messages`, execution proceeds without blocking |
| `test_workflow_bounded_retry_recovery` | Inject transient failure on first fill attempt | `recovery_node` triggers, `error_count` increments, re-inspects DOM, succeeds on second attempt |
| `test_workflow_escalates_to_human_after_3_retries` | Persistent unresolvable element failure | Recovery attempts 3 retries; after 3rd failure, transitions cleanly to `human_assistance` without infinite loop (AGENT-06) |
| `test_workflow_checkpointer_state_persistence` | Inspect workflow thread state using LangGraph checkpointer | State snapshot reflects all intermediate steps, logs, and screenshots |
| `test_api_workflow_lifecycle_endpoints` | Call `POST /api/agent/workflow/start` and `GET /state` | HTTP 200, thread ID returned, step progression recorded |

---

## Acceptance Criteria Checklist

- [ ] All tests in `backend/tests/test_agent_workflow.py` pass.
- [ ] Bounded recovery strictly halts at max 3 retries and transitions to human assistance.
- [ ] JavaScript alert dialogs are handled gracefully.
- [ ] Full backend test suite passes without regressions.
