"""Tests for AI-powered scheme eligibility reasoning engine (ELIG-01 through ELIG-05)."""

import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_evaluate_eligible_citizen():
    """Verify citizen meeting all conditions receives 'Likely Eligible' (ELIG-01, ELIG-02)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Default user (Aarav Sharma: Student, UG, Income ₹2.5L <= ₹4.5L ceiling)
        response = await client.post("/api/services/pm-usp-scholarship/evaluate")

    assert response.status_code == 200
    result = response.json()
    assert result["service_id"] == "pm-usp-scholarship"
    assert result["status"] == "Likely Eligible"
    assert result["confidence_score"] >= 0.85
    assert len(result["criteria"]) >= 1
    assert len(result["missing_fields"]) == 0

    # Verify criteria breakdown
    for crit in result["criteria"]:
        assert crit["status"] == "Satisfied"
        assert crit["official_citation"] != ""


@pytest.mark.asyncio
async def test_evaluate_ineligible_due_to_high_income():
    """Verify citizen exceeding income limit receives 'Likely Ineligible' (ELIG-02, ELIG-03)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "citizen_profile": {
                "full_name": "Rohan Verma",
                "annual_income": 850000.0,  # Exceeds ₹4.5L limit
                "education_level": "Undergraduate",
                "occupation": "Student",
                "state": "Maharashtra",
            }
        }
        response = await client.post("/api/services/pm-usp-scholarship/evaluate", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "Likely Ineligible"

    # Find income criterion
    income_crits = [c for c in result["criteria"] if "Income" in c["criterion_name"]]
    assert len(income_crits) > 0
    income_crit = income_crits[0]
    assert income_crit["status"] == "Not Satisfied"
    assert "850,000" in income_crit["citizen_value"]
    assert "exceeds" in income_crit["reasoning"].lower()


@pytest.mark.asyncio
async def test_evaluate_missing_information_alert():
    """Verify incomplete profile receives 'More Information Required' and missing fields list (ELIG-04)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Incomplete profile lacking income and education
        payload = {
            "citizen_profile": {
                "full_name": "Priya Nair",
                "state": "Karnataka",
            }
        }
        response = await client.post("/api/services/pm-usp-scholarship/evaluate", json=payload)

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "More Information Required"
    assert "annual_income" in result["missing_fields"]
    assert "education_level" in result["missing_fields"]

    # Check criteria status
    missing_crits = [c for c in result["criteria"] if c["status"] == "Missing Info"]
    assert len(missing_crits) >= 1
    assert missing_crits[0]["citizen_value"] == "Not Provided"


@pytest.mark.asyncio
async def test_evaluate_official_guideline_citations():
    """Verify itemized criteria contain authoritative guideline citations (ELIG-05)."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/services/pm-kisan-samman-nidhi/evaluate")

    assert response.status_code == 200
    result = response.json()
    for crit in result["criteria"]:
        assert crit["official_citation"] != ""
        assert "guidelines" in crit["official_citation"].lower() or "act" in crit["official_citation"].lower()


@pytest.mark.asyncio
async def test_evaluate_statutory_advisory_disclaimer():
    """Verify statutory advisory disclaimer is attached to evaluation response."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/services/pm-jay-ayushman-bharat/evaluate")

    assert response.status_code == 200
    result = response.json()
    assert "disclaimer" in result
    assert "advisory assessment" in result["disclaimer"].lower()
    assert "competent government department" in result["disclaimer"].lower()


@pytest.mark.asyncio
async def test_evaluate_service_not_found():
    """Verify evaluating non-existent scheme returns HTTP 404."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/services/non-existent-scheme-xyz/evaluate")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_evaluate_unauthorized_token():
    """Verify invalid token raises HTTP 401."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/services/pm-usp-scholarship/evaluate",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
