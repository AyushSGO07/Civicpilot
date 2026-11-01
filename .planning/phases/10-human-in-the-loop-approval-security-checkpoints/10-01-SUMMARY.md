# Plan 10-01 Summary: Pre-Submission Summary Payload, Approval State Machine & Review Modal

## Overview
Implemented the mandatory pre-submission review and approval gate (`HIL-01`, `HIL-02`, `HIL-03`). The LangGraph agent pauses execution before taking any final submission action on official government portals, compiles a structured audit payload (`PreSubmissionSummary`), and presents an interactive verification modal allowing the citizen to inspect all populated form fields and attached vault certificates before explicitly authorizing submission or returning to edit.

## Implementation Details
1. **Approval Data Models (`backend/app/models/approval.py`)**:
   - `PopulatedFormField`: Contains field label, element name, Playwright locator, populated value, source profile attribute, and confidence score.
   - `AttachedVaultDocument`: Details attached certificates (Aadhaar, Income Certificate, etc.) with verified status flags.
   - `PreSubmissionSummary`: Complete audit payload with service metadata, populated fields list, attached documents list, timestamp, field count, and statutory legal disclaimer.
   - `ApprovalDecisionRequest` & `ApprovalDecisionResponse`: Handles citizen decisions (`approved` or `rejected`).

2. **LangGraph Approval Nodes & Routing (`backend/app/services/workflow_engine.py`)**:
   - `waiting_approval_node`: Aggregates planned form actions and vault documents into `PreSubmissionSummary`, persists into workflow checkpoint, and halts.
   - `submit_node`: Reached when `approval_decision == "approved"`; sets step to `submission_ready`.
   - `rejected_node`: Reached when `approval_decision == "rejected"`; sets step to `submission_rejected` and records rejection rationale.
   - `route_after_approval`: Conditional edge routing between `submit`, `rejected`, and `pause` (checkpoint).

3. **Backend Approval REST Endpoints (`backend/app/routers/agent.py`)**:
   - `GET /api/agent/workflow/{thread_id}/summary`: Retrieves the structured `PreSubmissionSummary` for citizen review.
   - `POST /api/agent/workflow/{thread_id}/approve`: Records approval decision and resumes workflow execution from checkpoint.
   - `POST /api/agent/workflow/{thread_id}/reject`: Records rejection decision with optional feedback and halts workflow.

4. **Frontend Pre-Submission Review Modal (`frontend/app/applications/workspace/[sessionId]/page.tsx`)**:
   - MakeMyTrip high-contrast modal with scheme header, category pill, and field count.
   - Section 1: Detailed matrix of populated citizen identity & voluntary attributes with confidence indicators.
   - Section 2: Attached Vault Documents cards with verified checkmarks.
   - Section 3: Statutory Consent Advisory callout banner.
   - Dual action CTAs:
     - **"Approve & Authorize Submission"** (Emerald) -> updates state, emits WS approval frame, and invokes approval endpoint.
     - **"Reject & Return to Edit"** (Outline) -> returns workflow to review/edit mode.

5. **Automated Pytest Suite (`backend/tests/test_agent_approval.py`)**:
   - 5/5 passed validating summary compilation, approval pause gate, approval submission transition, rejection halt, and REST API endpoints.
