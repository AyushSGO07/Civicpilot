"""LangGraph Agent Workflow State Machine with bounded recovery and checkpointer (AGENT-06)."""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.models.workflow import AgentWorkflowState, WorkflowStep
from app.models.agent import SanitizedDOMTree
from app.models.profile import CitizenProfileBase
from app.models.form_filling import FormFillPlan, FormExecutionResult
from app.services.scheme_search import get_service_by_id
from app.services.browser_manager import browser_manager
from app.services.dom_inspector import DOMInspector
from app.services.field_mapper import DynamicFieldMapper
from app.services.form_executor import FormActionExecutor


def _add_log(state: AgentWorkflowState, message: str, level: str = "info") -> None:
    """Helper to append timestamped audit milestone log into workflow state."""
    if "logs" not in state or state["logs"] is None:
        state["logs"] = []
    state["logs"].append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "step": state.get("current_step", "unknown"),
        }
    )


# -------------------------------------------------------------------------
# Node Implementations
# -------------------------------------------------------------------------

async def discover_node(state: AgentWorkflowState) -> AgentWorkflowState:
    """Resolve target scheme criteria, issuing authority, and genuine application URL."""
    state["current_step"] = "discovery"
    service_id = state.get("service_id", "")
    _add_log(state, f"Starting discovery for government service '{service_id}'")

    service = get_service_by_id(service_id)
    if not service and not state.get("portal_url"):
        state["error_message"] = f"Service '{service_id}' not found in official catalog"
        _add_log(state, state["error_message"], level="error")
        return state

    if not state.get("portal_url") and service:
        state["portal_url"] = service.official_application_url or service.official_source_url

    _add_log(state, f"Resolved target official portal URL: {state['portal_url']}")
    return state


async def navigate_node(state: AgentWorkflowState) -> AgentWorkflowState:
    """Launch Playwright browser context, attach dialog interceptor, and navigate to portal."""
    state["current_step"] = "navigation"
    session_id = state.get("session_id")

    if not session_id or not await browser_manager.get_page(session_id):
        session_id = await browser_manager.create_session(session_id)
        state["session_id"] = session_id

    page = await browser_manager.get_page(session_id)
    assert page is not None

    # Attach automated JavaScript dialog/alert listener to prevent blocking
    if "dialog_messages" not in state or state["dialog_messages"] is None:
        state["dialog_messages"] = []

    def on_dialog(dialog):
        msg = dialog.message
        state["dialog_messages"].append(msg)
        _add_log(state, f"Intercepted portal alert/popup: '{msg}'", level="warning")
        asyncio.create_task(dialog.dismiss())

    # Avoid duplicate listener registration
    page.remove_listener("dialog", on_dialog) if hasattr(page, "remove_listener") else None
    page.on("dialog", on_dialog)

    portal_url = state.get("portal_url", "")
    _add_log(state, f"Navigating browser session '{session_id}' to {portal_url}")

    try:
        nav_res = await browser_manager.navigate(
            session_id=session_id,
            url=portal_url,
            wait_until="domcontentloaded",
            capture_screenshot=True,
        )
        state["screenshot_base64"] = nav_res.screenshot_base64
        _add_log(state, f"Successfully loaded portal page: '{nav_res.page_title}'")
    except Exception as e:
        state["error_message"] = f"Navigation failed: {str(e)}"
        _add_log(state, state["error_message"], level="error")

    return state


async def inspect_node(state: AgentWorkflowState) -> AgentWorkflowState:
    """Extract pruned semantic interactive element tree from loaded portal page."""
    state["current_step"] = "inspection"
    session_id = state.get("session_id", "")
    page = await browser_manager.get_page(session_id)

    if not page:
        state["error_message"] = f"Active browser page for session '{session_id}' not found"
        _add_log(state, state["error_message"], level="error")
        return state

    _add_log(state, "Extracting and sanitizing semantic DOM interactive tree")
    tree = await DOMInspector.inspect_page(page)
    state["dom_tree"] = tree.model_dump()
    _add_log(
        state,
        f"Inspected DOM: found {tree.interactive_elements_count} interactive form elements across {tree.forms_count} form(s)",
    )
    return state


async def map_node(state: AgentWorkflowState) -> AgentWorkflowState:
    """Dynamically map citizen profile attributes to portal form inputs using Gemini."""
    state["current_step"] = "mapping"
    dom_dict = state.get("dom_tree")

    if not dom_dict:
        state["error_message"] = "No DOM tree available for mapping"
        _add_log(state, state["error_message"], level="error")
        return state

    dom_tree = SanitizedDOMTree(**dom_dict)
    profile_dict = state.get("citizen_profile", {})
    profile = CitizenProfileBase(**profile_dict)
    vault_docs = state.get("vault_documents", [])

    _add_log(state, "Generating dynamic field mapping plan without hardcoded CSS selectors")
    plan = await DynamicFieldMapper.generate_fill_plan(dom_tree, profile, vault_docs)
    state["fill_plan"] = plan.model_dump()

    _add_log(
        state,
        f"Generated {len(plan.actions)} form filling actions ({len(plan.unmapped_elements)} unmapped elements)",
    )
    return state


async def fill_node(state: AgentWorkflowState) -> AgentWorkflowState:
    """Autonomously execute planned form actions on the active browser page."""
    state["current_step"] = "filling"
    session_id = state.get("session_id", "")
    page = await browser_manager.get_page(session_id)
    plan_dict = state.get("fill_plan")

    if not page or not plan_dict:
        state["error_message"] = "Cannot execute fill: page or fill plan missing"
        _add_log(state, state["error_message"], level="error")
        return state

    plan = FormFillPlan(**plan_dict)
    _add_log(state, f"Executing {len(plan.actions)} actions on browser session '{session_id}'")

    result = await FormActionExecutor.execute_plan(page, session_id, plan)
    state["execution_result"] = result.model_dump()
    if result.screenshot_base64:
        state["screenshot_base64"] = result.screenshot_base64

    _add_log(
        state,
        f"Form filling executed: {result.successful_actions} successful, {result.failed_actions} failed",
    )
    return state


async def validate_node(state: AgentWorkflowState) -> AgentWorkflowState:
    """Verify executed form actions and check for validation errors or failures."""
    state["current_step"] = "validation"
    exec_dict = state.get("execution_result", {})
    failed_actions = exec_dict.get("failed_actions", 0)

    if failed_actions > 0:
        state["error_message"] = f"{failed_actions} form action(s) failed during execution"
        _add_log(state, state["error_message"], level="warning")
    else:
        state["error_message"] = None
        _add_log(state, "Validation successful: all planned form inputs populated cleanly")

    return state


async def recovery_node(state: AgentWorkflowState) -> AgentWorkflowState:
    """Bounded recovery handler attempting recovery up to max 3 retries (AGENT-06)."""
    state["current_step"] = "recovery"
    state["error_count"] = state.get("error_count", 0) + 1
    max_retries = state.get("max_retries", 3)

    _add_log(
        state,
        f"Bounded recovery attempt {state['error_count']}/{max_retries} (AGENT-06). Dismissing modals & re-evaluating DOM.",
        level="warning",
    )

    # Capture fresh screenshot
    session_id = state.get("session_id", "")
    shot = await browser_manager.capture_screenshot_base64(session_id)
    if shot:
        state["screenshot_base64"] = shot

    return state


async def human_assistance_node(state: AgentWorkflowState) -> AgentWorkflowState:
    """Escalate to human assistance when bounded recovery threshold is exceeded (AGENT-06)."""
    state["current_step"] = "human_assistance"
    error_cnt = state.get("error_count", 0)
    max_ret = state.get("max_retries", 3)

    msg = f"Escalated to Human Assistance: exceeded maximum recovery threshold ({error_cnt}/{max_ret} attempts)."
    state["error_message"] = msg
    _add_log(state, msg, level="critical")

    # Capture visual snapshot for the citizen to inspect
    session_id = state.get("session_id", "")
    shot = await browser_manager.capture_screenshot_base64(session_id)
    if shot:
        state["screenshot_base64"] = shot

    return state


async def waiting_approval_node(state: AgentWorkflowState) -> AgentWorkflowState:
    """All form fields populated; pauses for human-in-the-loop review and approval (HIL-01)."""
    state["current_step"] = "waiting_approval"
    _add_log(state, "Form filling completed. Pausing automation for citizen pre-submission review.")
    return state


# -------------------------------------------------------------------------
# Conditional Routing Functions
# -------------------------------------------------------------------------

def route_after_validation(state: AgentWorkflowState) -> str:
    """Determine next node after validation based on error count and retry thresholds."""
    exec_dict = state.get("execution_result", {})
    failed_actions = exec_dict.get("failed_actions", 0)
    error_msg = state.get("error_message")

    if failed_actions > 0 or error_msg:
        if state.get("error_count", 0) < state.get("max_retries", 3):
            return "recovery"
        return "human_assistance"

    return "waiting_approval"


def route_after_recovery(state: AgentWorkflowState) -> str:
    """Determine whether to re-attempt inspection or escalate to human assistance."""
    if state.get("error_count", 0) >= state.get("max_retries", 3):
        return "human_assistance"
    return "inspect"


# -------------------------------------------------------------------------
# Graph Compilation with Checkpointer
# -------------------------------------------------------------------------

def build_agent_workflow() -> Any:
    """Construct and compile the stateful LangGraph agent workflow."""
    workflow = StateGraph(AgentWorkflowState)

    # Register Nodes
    workflow.add_node("discover", discover_node)
    workflow.add_node("navigate", navigate_node)
    workflow.add_node("inspect", inspect_node)
    workflow.add_node("map", map_node)
    workflow.add_node("fill", fill_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("recovery", recovery_node)
    workflow.add_node("human_assistance", human_assistance_node)
    workflow.add_node("waiting_approval", waiting_approval_node)

    # Linear Execution Edges
    workflow.add_edge(START, "discover")
    workflow.add_edge("discover", "navigate")
    workflow.add_edge("navigate", "inspect")
    workflow.add_edge("inspect", "map")
    workflow.add_edge("map", "fill")
    workflow.add_edge("fill", "validate")

    # Conditional Routing from Validate
    workflow.add_conditional_edges(
        "validate",
        route_after_validation,
        {
            "recovery": "recovery",
            "human_assistance": "human_assistance",
            "waiting_approval": "waiting_approval",
        },
    )

    # Conditional Routing from Recovery (Cyclical with bounded retries)
    workflow.add_conditional_edges(
        "recovery",
        route_after_recovery,
        {
            "inspect": "inspect",
            "human_assistance": "human_assistance",
        },
    )

    # Termination Edges
    workflow.add_edge("human_assistance", END)
    workflow.add_edge("waiting_approval", END)

    # Checkpoint Persistence
    checkpointer = MemorySaver()
    return workflow.compile(checkpointer=checkpointer)


# Global compiled workflow runner
agent_workflow_app = build_agent_workflow()
