"""Unit and integration tests for citizen profile endpoints and models."""

import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_get_profile_authenticated():
    """Verify GET /api/profile returns 200 with valid citizen profile schema."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/profile",
            headers={"Authorization": "Bearer test-valid-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "full_name" in data
    assert "state" in data
    assert "annual_income" in data
    assert data["full_name"] == "Aarav Sharma"


@pytest.mark.asyncio
async def test_put_profile_update():
    """Verify PUT /api/profile successfully updates attributes and returns 200."""
    transport = httpx.ASGITransport(app=app)
    update_payload = {
        "full_name": "Priya Patel",
        "state": "Gujarat",
        "district": "Ahmedabad",
        "pincode": "380001",
        "education_level": "Postgraduate",
        "institution_name": "Gujarat University",
        "course": "M.Sc Data Science",
        "academic_year": "1st Year",
        "occupation": "Student",
        "annual_income": 320000.0,
        "social_category": "General",
        "disability_status": False,
        "minority_status": False,
    }

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/profile",
            json=update_payload,
            headers={"Authorization": "Bearer test-valid-token"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Priya Patel"
    assert data["state"] == "Gujarat"
    assert data["district"] == "Ahmedabad"
    assert data["pincode"] == "380001"
    assert data["annual_income"] == 320000.0
    assert data["education_level"] == "Postgraduate"


@pytest.mark.asyncio
async def test_put_profile_validation_negative_income():
    """Verify PUT /api/profile rejects negative income with 422 Unprocessable Entity."""
    transport = httpx.ASGITransport(app=app)
    invalid_payload = {
        "annual_income": -50000.0,
    }

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/profile",
            json=invalid_payload,
            headers={"Authorization": "Bearer test-valid-token"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_put_profile_validation_invalid_pincode():
    """Verify PUT /api/profile rejects invalid non-6-digit PIN code."""
    transport = httpx.ASGITransport(app=app)
    invalid_payload = {
        "pincode": "1234",  # Less than 6 digits
    }

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/profile",
            json=invalid_payload,
            headers={"Authorization": "Bearer test-valid-token"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_put_profile_validation_invalid_category():
    """Verify PUT /api/profile rejects invalid social category."""
    transport = httpx.ASGITransport(app=app)
    invalid_payload = {
        "social_category": "NonExistentCategory",
    }

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put(
            "/api/profile",
            json=invalid_payload,
            headers={"Authorization": "Bearer test-valid-token"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_profile_unauthorized_token():
    """Verify endpoint rejects invalid token with 401 Unauthorized."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/api/profile",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
