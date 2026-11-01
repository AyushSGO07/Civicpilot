"""Execution controller managing pause, resume, and stop controls for browser agent sessions (EXEC-04, EXEC-05)."""

import asyncio
from typing import Dict, Optional
from app.services.websocket_manager import websocket_manager
from app.services.browser_manager import browser_manager


class SessionExecutionController:
    """Controls the execution cadence of an individual agent browser session."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.pause_event = asyncio.Event()
        self.pause_event.set()  # Unpaused initially
        self.stop_event = asyncio.Event()
        self.is_paused = False
        self.is_stopped = False

    async def pause(self) -> None:
        """Pause browser automation execution immediately without terminating context (EXEC-04)."""
        self.is_paused = True
        self.pause_event.clear()
        await websocket_manager.broadcast_status(self.session_id, status="paused")
        await websocket_manager.broadcast_milestone(
            self.session_id,
            step="control",
            message="Execution paused by citizen. Browser state preserved.",
            level="warning",
        )

    async def resume(self) -> None:
        """Resume paused browser automation execution (EXEC-04)."""
        self.is_paused = False
        self.pause_event.set()
        await websocket_manager.broadcast_status(self.session_id, status="resumed")
        await websocket_manager.broadcast_milestone(
            self.session_id,
            step="control",
            message="Execution resumed by citizen.",
            level="info",
        )

    async def stop(self) -> None:
        """Abort execution safely and terminate Chromium browser session (EXEC-05)."""
        self.is_stopped = True
        self.stop_event.set()
        self.pause_event.set()  # Unblock any suspended pause gate so loop can terminate

        # Clean up browser context immediately
        await browser_manager.close_session(self.session_id)

        await websocket_manager.broadcast_status(self.session_id, status="stopped")
        await websocket_manager.broadcast_milestone(
            self.session_id,
            step="control",
            message="Execution aborted by citizen. Browser session closed cleanly.",
            level="warning",
        )

    async def check_gate(self) -> None:
        """Check if session is paused or stopped before executing next action."""
        if self.is_stopped:
            raise asyncio.CancelledError(f"Session '{self.session_id}' aborted by citizen")
        await self.pause_event.wait()
        if self.is_stopped:
            raise asyncio.CancelledError(f"Session '{self.session_id}' aborted by citizen")


class ExecutionControllerRegistry:
    """Registry maintaining active session controllers."""

    def __init__(self):
        self._controllers: Dict[str, SessionExecutionController] = {}

    def get_or_create(self, session_id: str) -> SessionExecutionController:
        """Retrieve existing controller or initialize new controller for session."""
        if session_id not in self._controllers:
            self._controllers[session_id] = SessionExecutionController(session_id)
        return self._controllers[session_id]

    def remove(self, session_id: str) -> Optional[SessionExecutionController]:
        """Remove controller on session cleanup."""
        return self._controllers.pop(session_id, None)


# Shared global controller registry
controller_registry = ExecutionControllerRegistry()
