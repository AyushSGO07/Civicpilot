"""WebSocket manager for streaming real-time agent milestones and browser screenshots (EXEC-02, EXEC-03)."""

from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, Set, Any
from fastapi import WebSocket


class AgentWebSocketManager:
    """Manages active WebSocket subscriber connections and broadcasts real-time agent frames."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = defaultdict(set)

    async def connect(self, session_id: str, websocket: WebSocket) -> None:
        """Accept WebSocket connection and register subscriber for session stream."""
        await websocket.accept()
        self._connections[session_id].add(websocket)

        # Emit initial connection handshake frame
        await self.send_json(
            websocket,
            {
                "type": "connected",
                "session_id": session_id,
                "message": "Connected to CivicPilot Agent stream",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    def disconnect(self, session_id: str, websocket: WebSocket) -> None:
        """Remove disconnected client from active subscriber registry."""
        if session_id in self._connections:
            self._connections[session_id].discard(websocket)
            if not self._connections[session_id]:
                del self._connections[session_id]

    async def send_json(self, websocket: WebSocket, data: Dict[str, Any]) -> None:
        """Safely deliver a JSON frame to an individual WebSocket client."""
        try:
            await websocket.send_json(data)
        except Exception:
            pass

    async def broadcast_json(self, session_id: str, data: Dict[str, Any]) -> None:
        """Broadcast JSON payload to all active clients subscribed to the session."""
        subscribers = list(self._connections.get(session_id, set()))
        for ws in subscribers:
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(session_id, ws)

    async def broadcast_status(self, session_id: str, status: str, step: str = "") -> None:
        """Broadcast execution state change (EXEC-02)."""
        await self.broadcast_json(
            session_id,
            {
                "type": "status",
                "status": status,
                "step": step,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    async def broadcast_milestone(
        self,
        session_id: str,
        step: str,
        message: str,
        level: str = "info",
    ) -> None:
        """Broadcast reasoning log milestone event to subscribed clients (EXEC-02)."""
        await self.broadcast_json(
            session_id,
            {
                "type": "milestone",
                "step": step,
                "message": message,
                "level": level,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    async def broadcast_screenshot(self, session_id: str, screenshot_b64: str) -> None:
        """Broadcast Base64 visual frame buffer to subscribed clients (EXEC-03)."""
        await self.broadcast_json(
            session_id,
            {
                "type": "screenshot",
                "screenshot_base64": screenshot_b64,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


# Global singleton WebSocket manager
websocket_manager = AgentWebSocketManager()
