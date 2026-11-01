"""Pydantic schemas and TypedDict state for LangGraph workflow orchestration."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

WorkflowStep = Literal[
    "discovery",
    "navigation",
    "inspection",
    "mapping",
    "filling",
    "validation",
    "recovery",
    "waiting_approval",
    "human_assistance",
    "completed",
    "failed",
]


class AgentWorkflowState(TypedDict, total=False):
    """Complete LangGraph state container persisted across nodes and checkpoints."""

    session_id: str
    thread_id: str
    service_id: str
    portal_url: str
    citizen_profile: Dict[str, Any]
    vault_documents: List[Dict[str, Any]]
    current_step: str
    dom_tree: Optional[Dict[str, Any]]
    fill_plan: Optional[Dict[str, Any]]
    execution_result: Optional[Dict[str, Any]]
    error_count: int
    max_retries: int
    error_message: Optional[str]
    dialog_messages: List[str]
    logs: List[Dict[str, Any]]
    screenshot_base64: Optional[str]


class WorkflowStartRequest(BaseModel):
    """Payload to initiate a stateful LangGraph agent execution workflow."""

    service_id: str = Field(..., description="Target government scheme identifier")
    session_id: Optional[str] = Field(None, description="Optional existing browser session ID")
    portal_url_override: Optional[str] = Field(None, description="Optional custom portal URL (e.g. for testing)")
    custom_profile: Optional[Dict[str, Any]] = Field(None, description="Optional citizen profile override")
    custom_vault_documents: Optional[List[Dict[str, Any]]] = Field(None, description="Optional document vault override")


class WorkflowStateResponse(BaseModel):
    """Real-time workflow execution state snapshot returned to frontend or supervisor."""

    thread_id: str = Field(..., description="Unique LangGraph execution thread UUID")
    session_id: str = Field(..., description="Associated Playwright browser session ID")
    service_id: str = Field(..., description="Target scheme identifier")
    portal_url: str = Field(..., description="Current portal URL")
    current_step: str = Field(..., description="Active workflow node / step")
    error_count: int = Field(0, description="Total errors encountered and handled")
    max_retries: int = Field(3, description="Bounded retry threshold before human escalation")
    error_message: Optional[str] = Field(None, description="Active error description if any")
    dialog_messages: List[str] = Field(default_factory=list, description="Intercepted modal alerts/dialogs")
    logs: List[Dict[str, Any]] = Field(default_factory=list, description="Chronological execution milestone log")
    screenshot_base64: Optional[str] = Field(None, description="Latest browser visual snapshot buffer")
    execution_result: Optional[Dict[str, Any]] = Field(None, description="Form fill action execution audit")
    fill_plan: Optional[Dict[str, Any]] = Field(None, description="Planned action mapping")
