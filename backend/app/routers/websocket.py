"""FastAPI WebSocket endpoint for live agent execution streaming and interactive controls (EXEC-02, EXEC-03)."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status
from pydantic import BaseModel, Field

from app.services.websocket_manager import websocket_manager
from app.services.execution_controller import controller_registry

router = APIRouter(prefix="/ws", tags=["Real-time Agent Streaming & WebSockets"])


class ControlActionRequest(BaseModel):
    action: str = Field(..., description="'pause', 'resume', or 'stop'")


class ControlActionResponse(BaseModel):
    session_id: str
    status: str
    message: str


@router.websocket("/agent/{session_id}")
async def agent_websocket_stream(websocket: WebSocket, session_id: str):
    """Real-time bi-directional WebSocket stream for live screenshots, milestones, and controls (EXEC-02, EXEC-03)."""
    await websocket_manager.connect(session_id, websocket)
    controller = controller_registry.get_or_create(session_id)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action", "").lower()

            if action == "pause":
                await controller.pause()
            elif action == "resume":
                await controller.resume()
            elif action == "stop":
                await controller.stop()
            elif action == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id, websocket)
    except Exception:
        websocket_manager.disconnect(session_id, websocket)


@router.post(
    "/agent/{session_id}/pause",
    response_model=ControlActionResponse,
    summary="Pause active agent browser execution via HTTP (EXEC-04)",
)
async def http_pause_agent(session_id: str):
    """Pause browser execution via HTTP POST."""
    controller = controller_registry.get_or_create(session_id)
    await controller.pause()
    return ControlActionResponse(session_id=session_id, status="paused", message="Agent execution paused")


@router.post(
    "/agent/{session_id}/resume",
    response_model=ControlActionResponse,
    summary="Resume paused agent browser execution via HTTP (EXEC-04)",
)
async def http_resume_agent(session_id: str):
    """Resume browser execution via HTTP POST."""
    controller = controller_registry.get_or_create(session_id)
    await controller.resume()
    return ControlActionResponse(session_id=session_id, status="resumed", message="Agent execution resumed")


@router.post(
    "/agent/{session_id}/stop",
    response_model=ControlActionResponse,
    summary="Abort and terminate agent browser execution via HTTP (EXEC-05)",
)
async def http_stop_agent(session_id: str):
    """Abort browser execution safely via HTTP POST."""
    controller = controller_registry.get_or_create(session_id)
    await controller.stop()
    return ControlActionResponse(session_id=session_id, status="stopped", message="Agent execution aborted safely")
