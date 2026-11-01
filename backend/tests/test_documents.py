"""Tests for citizen document vault endpoints: upload, listing, download, and deletion."""

import io
import pytest
import httpx
from app.main import app


@pytest.mark.asyncio
async def test_upload_document_success():
    """Verify POST /api/documents/upload stores file and returns 201 with metadata."""
    transport = httpx.ASGITransport(app=app)
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"

    files = {
        "file": ("aadhaar_front.png", fake_png, "image/png"),
    }
    data = {
        "document_type": "Aadhaar Card",
    }

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": "Bearer test-valid-token"},
        )

    assert response.status_code == 201
    res_data = response.json()
    assert "id" in res_data
    assert res_data["document_name"] == "aadhaar_front.png"
    assert res_data["document_type"] == "Aadhaar Card"
    assert res_data["mime_type"] == "image/png"
    assert res_data["file_size_bytes"] == len(fake_png)
    assert res_data["verification_status"] == "Unverified"
    assert "download_url" in res_data


@pytest.mark.asyncio
async def test_upload_document_invalid_mime():
    """Verify POST /api/documents/upload rejects unallowed MIME type with 400."""
    transport = httpx.ASGITransport(app=app)
    fake_txt = b"Some plain text document"

    files = {
        "file": ("test.txt", fake_txt, "text/plain"),
    }
    data = {"document_type": "Other"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": "Bearer test-valid-token"},
        )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_documents():
    """Verify GET /api/documents returns list of user's uploaded documents."""
    transport = httpx.ASGITransport(app=app)
    fake_pdf = b"%PDF-1.4 header and content"

    files = {
        "file": ("marksheet_12th.pdf", fake_pdf, "application/pdf"),
    }
    data = {"document_type": "Academic Marksheet"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Upload
        await client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": "Bearer test-valid-token"},
        )
        # List
        response = await client.get(
            "/api/documents",
            headers={"Authorization": "Bearer test-valid-token"},
        )

    assert response.status_code == 200
    docs = response.json()
    assert isinstance(docs, list)
    assert len(docs) >= 1
    names = [d["document_name"] for d in docs]
    assert "marksheet_12th.pdf" in names


@pytest.mark.asyncio
async def test_get_and_download_document():
    """Verify GET /api/documents/{id} and download endpoint."""
    transport = httpx.ASGITransport(app=app)
    fake_img = b"\xff\xd8\xff\xe0\x00\x10JFIF"

    files = {
        "file": ("pan_card.jpg", fake_img, "image/jpeg"),
    }
    data = {"document_type": "PAN Card"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Upload
        up_res = await client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": "Bearer test-valid-token"},
        )
        doc_id = up_res.json()["id"]

        # Get Metadata
        get_res = await client.get(
            f"/api/documents/{doc_id}",
            headers={"Authorization": "Bearer test-valid-token"},
        )
        assert get_res.status_code == 200
        assert get_res.json()["document_name"] == "pan_card.jpg"

        # Download
        dl_res = await client.get(
            f"/api/documents/{doc_id}/download",
            headers={"Authorization": "Bearer test-valid-token"},
        )
        assert dl_res.status_code == 200
        assert dl_res.content == fake_img


@pytest.mark.asyncio
async def test_delete_document():
    """Verify DELETE /api/documents/{id} removes document permanently (DOC-05)."""
    transport = httpx.ASGITransport(app=app)
    fake_png = b"\x89PNG\r\n\x1a\n\x00"

    files = {
        "file": ("delete_me.png", fake_png, "image/png"),
    }
    data = {"document_type": "Other"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        up_res = await client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": "Bearer test-valid-token"},
        )
        doc_id = up_res.json()["id"]

        # Delete
        del_res = await client.delete(
            f"/api/documents/{doc_id}",
            headers={"Authorization": "Bearer test-valid-token"},
        )
        assert del_res.status_code == 200

        # Subsequent retrieval should return 404
        get_res = await client.get(
            f"/api/documents/{doc_id}",
            headers={"Authorization": "Bearer test-valid-token"},
        )
        assert get_res.status_code == 404



@pytest.mark.asyncio
async def test_ocr_document_extraction():
    """Verify POST /api/documents/{id}/ocr extracts structured fields with privacy masking (DOC-03)."""
    transport = httpx.ASGITransport(app=app)
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

    files = {
        "file": ("aadhaar_identity.png", fake_png, "image/png"),
    }
    data = {"document_type": "Aadhaar Card"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Upload
        up_res = await client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": "Bearer test-valid-token"},
        )
        assert up_res.status_code == 201
        doc_id = up_res.json()["id"]

        # 2. Trigger OCR
        ocr_res = await client.post(
            f"/api/documents/{doc_id}/ocr",
            headers={"Authorization": "Bearer test-valid-token"},
        )
        assert ocr_res.status_code == 200
        ocr_data = ocr_res.json()
        assert ocr_data["verification_status"] == "Extracted"
        extracted = ocr_data["extracted_information"]
        assert "full_name" in extracted
        assert "id_number_masked" in extracted
        assert extracted["id_number_masked"].startswith("XXXX")  # Privacy masking verified
        assert extracted["confidence_score"] > 0.8


@pytest.mark.asyncio
async def test_confirm_extracted_fields_into_profile():
    """Verify POST /api/documents/{id}/confirm merges approved attributes into profile (DOC-04)."""
    transport = httpx.ASGITransport(app=app)
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"

    files = {
        "file": ("caste_certificate.png", fake_png, "image/png"),
    }
    data = {"document_type": "Caste Certificate"}

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Upload
        up_res = await client.post(
            "/api/documents/upload",
            files=files,
            data=data,
            headers={"Authorization": "Bearer test-valid-token"},
        )
        doc_id = up_res.json()["id"]

        # 2. Trigger OCR
        await client.post(
            f"/api/documents/{doc_id}/ocr",
            headers={"Authorization": "Bearer test-valid-token"},
        )

        # 3. Citizen approves and confirms fields into profile
        confirm_payload = {
            "fields_to_confirm": {
                "social_category": "OBC",
                "state": "Maharashtra",
            }
        }
        confirm_res = await client.post(
            f"/api/documents/{doc_id}/confirm",
            json=confirm_payload,
            headers={"Authorization": "Bearer test-valid-token"},
        )
        assert confirm_res.status_code == 200
        assert confirm_res.json()["verification_status"] == "Verified"

        # 4. Verify profile was synchronized
        prof_res = await client.get(
            "/api/profile",
            headers={"Authorization": "Bearer test-valid-token"},
        )
        assert prof_res.status_code == 200
        prof_data = prof_res.json()
        assert prof_data["social_category"] == "OBC"
        assert prof_data["state"] == "Maharashtra"
