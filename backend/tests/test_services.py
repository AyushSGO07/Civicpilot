"""Tests for official government scheme discovery and search endpoints."""

import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_list_all_services():
    """Verify GET /api/services returns verified government schemes catalog (HTTP 200)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/services")

    assert response.status_code == 200
    services = response.json()
    assert isinstance(services, list)
    assert len(services) >= 8

    # Verify official zero-dummy data integrity
    service_ids = [s["id"] for s in services]
    assert "pm-usp-scholarship" in service_ids
    assert "pm-kisan-samman-nidhi" in service_ids
    assert "pm-jay-ayushman-bharat" in service_ids


@pytest.mark.asyncio
async def test_search_services_natural_language():
    """Verify natural language search queries return matching schemes (DISC-01)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Search for scholarships
        res_scholarship = await client.get("/api/services", params={"q": "scholarship for college students"})
        assert res_scholarship.status_code == 200
        scholarships = res_scholarship.json()
        assert len(scholarships) >= 1
        assert "scholarship" in scholarships[0]["service_name"].lower() or "scholarship" in scholarships[0]["category"].lower()

        # Search for farmer / agriculture
        res_farmer = await client.get("/api/services", params={"q": "kisan support"})
        assert res_farmer.status_code == 200
        farmers = res_farmer.json()
        assert len(farmers) >= 1
        assert "pm-kisan" in farmers[0]["id"]


@pytest.mark.asyncio
async def test_filter_services_by_category():
    """Verify category tab filtering returns matching category schemes (DISC-02)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Agriculture category
        res_agri = await client.get("/api/services", params={"category": "Agriculture"})
        assert res_agri.status_code == 200
        agri_services = res_agri.json()
        assert len(agri_services) >= 1
        for s in agri_services:
            assert s["category"] == "Agriculture"

        # Healthcare category
        res_health = await client.get("/api/services", params={"category": "Healthcare"})
        assert res_health.status_code == 200
        health_services = res_health.json()
        assert len(health_services) >= 1
        assert health_services[0]["category"] == "Healthcare"
        assert "Ayushman" in health_services[0]["service_name"]


@pytest.mark.asyncio
async def test_get_service_detail_and_official_urls():
    """Verify GET /api/services/{id} returns scheme details and authentic official portal URLs (DISC-03, DISC-04)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/services/pm-usp-scholarship")

    assert response.status_code == 200
    service = response.json()
    assert service["id"] == "pm-usp-scholarship"
    assert "Department of Higher Education" in service["department"]
    assert "Class 12 Marksheet" in service["required_documents"]
    # Authentic government endpoints (DISC-04)
    assert "scholarships.gov.in" in service["official_application_url"]
    assert "myscheme.gov.in" in service["official_source_url"]


@pytest.mark.asyncio
async def test_get_nonexistent_service_404():
    """Verify GET /api/services/{id} returns 404 for non-existent service."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/services/non-existent-scheme-slug")

    assert response.status_code == 404
