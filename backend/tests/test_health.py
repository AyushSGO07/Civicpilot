"""Tests for the health check router."""

import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_health_check_returns_ok():
    """Verify GET /api/health returns 200 with ok status and matching service name."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "CivicPilot API"
    assert "version" in data
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify GET / returns basic welcome metadata."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "health_check" in data
    assert data["health_check"] == "/api/health"
