# Phase 08: LangGraph Workflow Orchestration & Bounded Recovery — Research & Architecture

## Objective

Design and construct a deterministic cyclical LangGraph state machine orchestrating end-to-end browser agent operations (Discovery -> Navigation -> Inspection -> Dynamic Mapping -> Form Population -> Validation -> Bounded Recovery -> Human Assistance) with state checkpointing and a strict 3-retry limit.

---

## 1. Requirements Mapping

| ID | Requirement | Implementation Strategy |
|---|---|---|
| **AGENT-06** | Agent executes bounded recovery (max 3 retries) when encountering element timeouts or unexpected alert dialogs | LangGraph cyclical state machine with `recovery` node, tracking `error_count`. If `error_count < 3`, attempts recovery (dialog dismissal, DOM re-inspection, field retry); if `error_count >= 3`, transitions safely to `WAITING_FOR_HUMAN_ASSISTANCE`. |

---

## 2. LangGraph State Machine Architecture

```
                    ┌───────────────────────────┐
                    │          START            │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      discover_node        │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │      navigate_node        │
                    └─────────────┬─────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
        ┌───────────►       inspect_node        │
        │           └─────────────┬─────────────┘
        │                         │
        │                         ▼
        │           ┌───────────────────────────┐
        │           │         map_node          │
        │           └─────────────┬─────────────┘
        │                         │
        │                         ▼
        │           ┌───────────────────────────┐
        │           │         fill_node         │
        │           └─────────────┬─────────────┘
        │                         │
        │                         ▼
        │           ┌───────────────────────────┐
        │           │       validate_node       │
        │           └─────────────┬─────────────┘
        │                         │
        │             [Has Errors & Retries < 3?]
        │               /                     \
        │           YES /                       \ NO (Success)
        │              ▼                         ▼
        │   ┌────────────────────┐       ┌──────────────────────┐
        └───┤   recovery_node    │       │ waiting_for_approval │
            └─────────┬──────────┘       └──────────┬───────────┘
                      │                             │
          [Retries >= 3 exhausted]                  ▼
                      │                         ┌───────┐
                      ▼                         │  END  │
            ┌───────────────────┐               └───────┘
            │ human_assistance  │
            └─────────┬─────────┘
                      │
                      ▼
                  ┌───────┐
                  │  END  │
                  └───────┘
```

---

## 3. Workflow State Schema

```python
class AgentWorkflowState(TypedDict):
    session_id: str
    thread_id: str
    service_id: str
    portal_url: str
    citizen_profile: dict
    vault_documents: list
    current_step: str
    dom_tree: Optional[dict]
    fill_plan: Optional[dict]
    execution_result: Optional[dict]
    error_count: int
    max_retries: int
    error_message: Optional[str]
    dialog_messages: List[str]
    logs: List[dict]
    screenshot_base64: Optional[str]
```

---

## 4. Bounded Recovery Logic (AGENT-06)

### Recovery Triggers
1. **Element Timeout / Navigation Flakiness**: Portal DOM fails to load within expected window.
2. **Action Execution Failure**: One or more mandatory fields in `FormFillPlan` throw locator attachment errors.
3. **Portal Alert Dialog**: An unexpected JavaScript `alert()`, `confirm()`, or modal notification intercepts interaction.

### Recovery Execution
1. **Dialog Dismissal**: Automated `dialog.accept()` or `dialog.dismiss()` records dialog message in `dialog_messages` and unblocks page execution.
2. **DOM Re-inspection**: The DOM is re-extracted to detect responsive layout adjustments or dynamically inserted error labels.
3. **Bounded Retries**:
   - Iteration 1-2: Re-attempt mapping and filling.
   - Iteration 3: Final fallback retry.
   - Iteration > 3: Transitions immediately to `human_assistance`, logging exact failing locators and reasons. Zero infinite loops.
