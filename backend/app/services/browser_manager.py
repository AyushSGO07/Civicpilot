"""Asynchronous Playwright Chromium Browser Manager with lifecycle control and zombie prevention."""

import asyncio
import base64
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional
from contextlib import asynccontextmanager

from playwright.async_api import (
    async_playwright,
    Playwright,
    Browser,
    BrowserContext,
    Page,
)

from app.models.agent import (
    BrowserSessionInfo,
    BrowserNavigateResponse,
)

DEFAULT_VIEWPORT = {"width": 1280, "height": 800}
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36 CivicPilot/1.0"
)


class BrowserSessionRecord:
    """Internal container tracking a Playwright page, context, and metadata."""

    def __init__(self, session_id: str, context: BrowserContext, page: Page):
        self.session_id = session_id
        self.context = context
        self.page = page
        self.info = BrowserSessionInfo(
            session_id=session_id,
            status="idle",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )


class BrowserSessionManager:
    """Singleton managing Chromium lifecycle, context pooling, and automated process teardown."""

    _instance: Optional["BrowserSessionManager"] = None

    def __init__(self):
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._sessions: Dict[str, BrowserSessionRecord] = {}
        self._lock = asyncio.Lock()
        self._initialized = False
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    @classmethod
    def get_instance(cls) -> "BrowserSessionManager":
        if cls._instance is None:
            cls._instance = BrowserSessionManager()
        return cls._instance

    async def initialize(self) -> None:
        """Initialize Playwright and launch the Chromium browser instance."""
        current_loop = asyncio.get_running_loop()

        # If event loop changed (e.g. between pytest test functions), reset state
        if self._loop != current_loop:
            self._initialized = False
            self._browser = None
            self._playwright = None
            self._sessions.clear()
            self._lock = asyncio.Lock()
            self._loop = current_loop

        async with self._lock:
            if self._initialized and self._browser and self._browser.is_connected():
                return

            headless = os.getenv("BROWSER_HEADLESS", "true").lower() != "false"
            self._playwright = await async_playwright().start()

            # Check for remote cloud browser (Browserless / Browserbase / CDP endpoint)
            cdp_url = os.getenv("PLAYWRIGHT_CDP_URL") or os.getenv("BROWSERLESS_URL")
            if not cdp_url and os.getenv("BROWSERLESS_API_KEY"):
                cdp_url = f"wss://chrome.browserless.io?token={os.getenv('BROWSERLESS_API_KEY')}"

            if cdp_url:
                self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)
            else:
                try:
                    self._browser = await self._playwright.chromium.launch(
                        headless=headless,
                        args=[
                            "--no-sandbox",
                            "--disable-setuid-sandbox",
                            "--disable-dev-shm-usage",
                            "--disable-blink-features=AutomationControlled",
                        ],
                    )
                except Exception as exc:
                    exc_str = str(exc).lower()
                    if "executable doesn't exist" in exc_str or "missing dependencies" in exc_str:
                        raise RuntimeError(
                            "Local Chromium is not installed in this serverless environment. "
                            "Please configure PLAYWRIGHT_CDP_URL or BROWSERLESS_API_KEY in your environment variables "
                            "to connect to a remote cloud browser (e.g. Browserless.io or Browserbase)."
                        ) from exc
                    raise
            self._initialized = True
            self._loop = current_loop

    async def create_session(self, session_id: Optional[str] = None) -> str:
        """Create an isolated BrowserContext and Page with desktop settings."""
        current_loop = asyncio.get_running_loop()
        if (
            not self._initialized
            or self._loop != current_loop
            or not self._browser
            or not self._browser.is_connected()
        ):
            await self.initialize()

        sid = session_id or str(uuid.uuid4())

        async with self._lock:
            if sid in self._sessions:
                # Close existing session with same ID if any
                await self._close_session_unlocked(sid)

            assert self._browser is not None
            context = await self._browser.new_context(
                viewport=DEFAULT_VIEWPORT,
                user_agent=DEFAULT_USER_AGENT,
                ignore_https_errors=True,
                java_script_enabled=True,
            )
            page = await context.new_page()

            # Set reasonable default navigation and script timeouts
            page.set_default_navigation_timeout(30000)
            page.set_default_timeout(15000)

            record = BrowserSessionRecord(session_id=sid, context=context, page=page)
            self._sessions[sid] = record
            return sid

    async def get_page(self, session_id: str) -> Optional[Page]:
        """Return the active Playwright Page for an existing session."""
        record = self._sessions.get(session_id)
        if record and not record.page.is_closed():
            return record.page
        return None

    async def get_session_info(self, session_id: str) -> Optional[BrowserSessionInfo]:
        """Return metadata for an active session."""
        record = self._sessions.get(session_id)
        if record:
            return record.info
        return None

    async def navigate(
        self,
        session_id: str,
        url: str,
        wait_until: str = "domcontentloaded",
        timeout_ms: int = 30000,
        capture_screenshot: bool = True,
    ) -> BrowserNavigateResponse:
        """Navigate session page to target portal URL and return screenshot buffer."""
        record = self._sessions.get(session_id)
        if not record or record.page.is_closed():
            raise ValueError(f"Active browser session '{session_id}' not found")

        page = record.page
        record.info.status = "navigating"
        record.info.updated_at = datetime.now(timezone.utc)

        try:
            # Type ignore for wait_until literal compatibility with Playwright
            response = await page.goto(url, wait_until=wait_until, timeout=timeout_ms)  # type: ignore
            status_code = response.status if response else 200

            title = await page.title()
            final_url = page.url

            screenshot_b64: Optional[str] = None
            if capture_screenshot:
                screenshot_bytes = await page.screenshot(type="jpeg", quality=65)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            record.info.status = "idle"
            record.info.current_url = final_url
            record.info.page_title = title
            record.info.updated_at = datetime.now(timezone.utc)

            return BrowserNavigateResponse(
                session_id=session_id,
                url=final_url,
                page_title=title,
                status_code=status_code,
                screenshot_base64=screenshot_b64,
            )
        except Exception as e:
            record.info.status = "error"
            record.info.updated_at = datetime.now(timezone.utc)
            raise RuntimeError(f"Navigation to '{url}' failed: {str(e)}") from e

    async def capture_screenshot_base64(self, session_id: str, quality: int = 65) -> Optional[str]:
        """Capture JPEG screenshot of current page state encoded as Base64."""
        record = self._sessions.get(session_id)
        if not record or record.page.is_closed():
            return None
        try:
            bytes_data = await record.page.screenshot(type="jpeg", quality=quality)
            return base64.b64encode(bytes_data).decode("utf-8")
        except Exception:
            return None

    async def close_session(self, session_id: str) -> bool:
        """Cleanly terminate an individual browser session and context (AGENT-07)."""
        async with self._lock:
            return await self._close_session_unlocked(session_id)

    async def _close_session_unlocked(self, session_id: str) -> bool:
        """Internal unlocked session closer."""
        record = self._sessions.pop(session_id, None)
        if record:
            try:
                if not record.page.is_closed():
                    await record.page.close()
                await record.context.close()
                record.info.status = "closed"
            except Exception:
                pass
            return True
        return False

    async def close_all_sessions(self) -> int:
        """Close all active sessions and contexts."""
        async with self._lock:
            count = len(self._sessions)
            session_ids = list(self._sessions.keys())
            for sid in session_ids:
                await self._close_session_unlocked(sid)
            return count

    async def shutdown(self) -> None:
        """Full graceful termination of all sessions, contexts, browser and runtime."""
        await self.close_all_sessions()
        async with self._lock:
            if self._browser:
                try:
                    await self._browser.close()
                except Exception:
                    pass
                self._browser = None

            if self._playwright:
                try:
                    await self._playwright.stop()
                except Exception:
                    pass
                self._playwright = None

            self._initialized = False

    @asynccontextmanager
    async def session(self, session_id: Optional[str] = None):
        """Context manager guaranteeing automated session cleanup on block exit."""
        sid = await self.create_session(session_id)
        try:
            page = await self.get_page(sid)
            assert page is not None
            yield page, sid
        finally:
            await self.close_session(sid)


# Shared global singleton accessor
browser_manager = BrowserSessionManager.get_instance()
