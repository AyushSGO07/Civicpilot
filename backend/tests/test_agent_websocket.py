"""Tests for FastAPI WebSocket streaming and execution controller (EXEC-02, EXEC-03, EXEC-04, EXEC-05)."""

import pytest
from fastapi.testclient import TestClient
import httpx

from app.main import app
from app.services.websocket_manager import websocket_manager
from app.services.execution_controller import controller_registry


def test_websocket_connection_and_handshake():
    """Verify WebSocket client connection and initial handshake frame (EXEC-02)."""
    client = TestClient(app)
    session_id = "test-ws-session-001"

    with client.websocket_connect(f"/ws/agent/{session_id}") as ws:
        frame = ws.receive_json()
        assert frame["type"] == "connected"
        assert frame["session_id"] == session_id
        assert "Connected" in frame["message"]


def test_websocket_milestone_broadcasting():
    """Verify broadcasting milestone reasoning events to connected clients (EXEC-02)."""
    client = TestClient(app)
    session_id = "test-ws-session-002"

    with client.websocket_connect(f"/ws/agent/{session_id}") as ws:
        # Discard welcome frame
        ws.receive_json()

        # Send ping
        ws.send_json({"action": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"


def test_websocket_pause_and_resume_controls():
    """Verify Pause and Resume control actions over WebSocket (EXEC-04)."""
    client = TestClient(app)
    session_id = "test-ws-session-003"
    controller = controller_registry.get_or_create(session_id)

    with client.websocket_connect(f"/ws/agent/{session_id}") as ws:
        ws.receive_json()  # Handshake

        # Send Pause action
        ws.send_json({"action": "pause"})
        status_frame = ws.receive_json()
        assert status_frame["type"] == "status"
        assert status_frame["status"] == "paused"
        assert controller.is_paused is True
        assert not controller.pause_event.is_set()

        # Receive milestone confirmation
        milestone_frame = ws.receive_json()
        assert milestone_frame["type"] == "milestone"
        assert "paused" in milestone_frame["message"].lower()

        # Send Resume action
        ws.send_json({"action": "resume"})
        resume_frame = ws.receive_json()
        assert resume_frame["type"] == "status"
        assert resume_frame["status"] == "resumed"
        assert controller.is_paused is False
        assert controller.pause_event.is_set()


def test_websocket_stop_control():
    """Verify Abort / Stop control action terminates session cleanly (EXEC-05)."""
    client = TestClient(app)
    session_id = "test-ws-session-004"
    controller = controller_registry.get_or_create(session_id)

    with client.websocket_connect(f"/ws/agent/{session_id}") as ws:
        ws.receive_json()  # Handshake

        # Send Stop action
        ws.send_json({"action": "stop"})
        status_frame = ws.receive_json()
        assert status_frame["type"] == "status"
        assert status_frame["status"] == "stopped"
        assert controller.is_stopped is True
        assert controller.stop_event.is_set()


@pytest.mark.asyncio
async def test_http_control_endpoints():
    """Verify HTTP fallback endpoints for pause, resume, and stop."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        session_id = "test-http-session-005"

        # 1. Pause
        pause_res = await client.post(f"/ws/agent/{session_id}/pause")
        assert pause_res.status_code == 200
        assert pause_res.json()["status"] == "paused"

        # 2. Resume
        resume_res = await client.post(f"/ws/agent/{session_id}/resume")
        assert resume_res.status_code == 200
        assert resume_res.json()["status"] == "resumed"

        # 3. Stop
        stop_res = await client.post(f"/ws/agent/{session_id}/stop")
        assert stop_res.status_code == 200
        assert stop_res.json()["status"] == "stopped"
