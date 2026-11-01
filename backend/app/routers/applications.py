"""CivicPilot Applications Router.

Endpoints for citizen application tracking, status updates, and official
submission receipt PDF downloads (APP-03, APP-04, APP-05).
"""

from datetime import datetime, timezone
import os
from typing import Dict, List, Optional
import uuid

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import FileResponse

from app.models.application import (
    ApplicationRecord,
    ApplicationStatus,
    CreateApplicationRequest,
    UpdateApplicationRequest,
)
from app.services.submission_verifier import ReceiptGenerator

router = APIRouter(prefix="/applications", tags=["Applications"])

# In-memory application store for fast, deterministic retrieval & testing
_APPLICATIONS_STORE: Dict[str, ApplicationRecord] = {}


def _seed_default_applications():
    """Initializes realistic baseline applications for demonstration."""
    if _APPLICATIONS_STORE:
        return

    app1 = ApplicationRecord(
        id="app-demo-nsp-01",
        user_id="demo-citizen-id",
        service_id="nsp-post-matric-sc",
        service_name="Post-Matric Scholarship for SC Students",
        department="Ministry of Social Justice and Empowerment",
        category="Education",
        portal_url="https://scholarships.gov.in",
        status="submitted",
        acknowledgement_number="NSP2026/APPL/894125",
        confirmation_text="Your application has been submitted successfully to National Scholarship Portal.",
        submission_timestamp=datetime(2026, 10, 28, 14, 30, tzinfo=timezone.utc),
        populated_data={
            "full_name": "Arjun Sharma",
            "date_of_birth": "15/08/1998",
            "gender": "Male",
            "domicile_state": "Maharashtra",
            "annual_income": "180000",
            "social_category": "SC",
        },
        attached_documents=[
            "Aadhaar Identity Card (Verified)",
            "Income Certificate 2025-26 (Verified)",
            "Caste Certificate (Verified)",
        ],
    )

    app2 = ApplicationRecord(
        id="app-demo-pmk-02",
        user_id="demo-citizen-id",
        service_id="pm-kisan-samman-nidhi",
        service_name="PM Kisan Samman Nidhi Yojana",
        department="Ministry of Agriculture and Farmers Welfare",
        category="Agriculture",
        portal_url="https://pmkisan.gov.in",
        status="submitted",
        acknowledgement_number="PMK-MH-948123",
        confirmation_text="Application registered successfully under PM-Kisan scheme.",
        submission_timestamp=datetime(2026, 10, 31, 9, 15, tzinfo=timezone.utc),
        populated_data={
            "full_name": "Arjun Sharma",
            "date_of_birth": "15/08/1998",
            "gender": "Male",
            "domicile_state": "Maharashtra",
            "annual_income": "180000",
            "social_category": "General",
        },
        attached_documents=[
            "Aadhaar Identity Card (Verified)",
            "Land Ownership Record (7/12 Extract)",
        ],
    )

    app3 = ApplicationRecord(
        id="app-demo-ab-03",
        user_id="demo-citizen-id",
        service_id="ayushman-bharat-pmjay",
        service_name="Ayushman Bharat - PMJAY Health Card",
        department="National Health Authority (NHA)",
        category="Healthcare",
        portal_url="https://beneficiary.nha.gov.in",
        status="waiting_approval",
        acknowledgement_number=None,
        confirmation_text=None,
        submission_timestamp=None,
        populated_data={
            "full_name": "Arjun Sharma",
            "date_of_birth": "15/08/1998",
            "gender": "Male",
            "domicile_state": "Maharashtra",
            "annual_income": "180000",
            "social_category": "OBC",
        },
        attached_documents=[
            "Aadhaar Identity Card (Verified)",
            "Ration Card (Verified)",
        ],
    )

    _APPLICATIONS_STORE[app1.id] = app1
    _APPLICATIONS_STORE[app2.id] = app2
    _APPLICATIONS_STORE[app3.id] = app3


# Seed at import
_seed_default_applications()


@router.get("", response_model=List[ApplicationRecord])
async def list_applications(
    status: Optional[str] = Query(default=None, description="Optional status filter"),
    user_id: Optional[str] = Query(default=None, description="Citizen account identifier"),
):
    """Retrieves all tracked applications for the citizen (APP-03, APP-04)."""
    _seed_default_applications()
    apps = list(_APPLICATIONS_STORE.values())

    if status and status.lower() != "all":
        apps = [a for a in apps if a.status.lower() == status.lower()]

    if user_id:
        apps = [a for a in apps if a.user_id == user_id]

    # Return newest first
    return sorted(apps, key=lambda x: x.updated_at or x.created_at, reverse=True)


@router.get("/{application_id}", response_model=ApplicationRecord)
async def get_application(application_id: str):
    """Retrieves a single application record by ID."""
    _seed_default_applications()
    app_record = _APPLICATIONS_STORE.get(application_id)
    if not app_record:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found")
    return app_record


@router.post("", response_model=ApplicationRecord)
async def create_or_update_application(req: CreateApplicationRequest):
    """Registers or updates an application record."""
    app_id = req.id or f"app-{uuid.uuid4().hex[:8]}"
    existing = _APPLICATIONS_STORE.get(app_id)

    if existing:
        existing.service_id = req.service_id
        existing.service_name = req.service_name
        existing.department = req.department
        existing.category = req.category
        existing.portal_url = req.portal_url
        existing.status = req.status
        existing.populated_data.update(req.populated_data)
        if req.attached_documents:
            existing.attached_documents = req.attached_documents
        existing.updated_at = datetime.now(timezone.utc)
        _APPLICATIONS_STORE[app_id] = existing
        return existing

    record = ApplicationRecord(
        id=app_id,
        service_id=req.service_id,
        service_name=req.service_name,
        department=req.department,
        category=req.category,
        portal_url=req.portal_url,
        status=req.status,
        populated_data=req.populated_data,
        attached_documents=req.attached_documents,
    )
    _APPLICATIONS_STORE[app_id] = record
    return record


@router.patch("/{application_id}", response_model=ApplicationRecord)
async def patch_application(application_id: str, req: UpdateApplicationRequest):
    """Updates an application state, acknowledgement number, or receipt info."""
    _seed_default_applications()
    record = _APPLICATIONS_STORE.get(application_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Application {application_id} not found")

    if req.status:
        record.status = req.status
    if req.acknowledgement_number:
        record.acknowledgement_number = req.acknowledgement_number
    if req.confirmation_text:
        record.confirmation_text = req.confirmation_text
    if req.submission_timestamp:
        record.submission_timestamp = req.submission_timestamp
    if req.receipt_url:
        record.receipt_url = req.receipt_url
    if req.receipt_path:
        record.receipt_path = req.receipt_path
    if req.populated_data:
        record.populated_data.update(req.populated_data)
    if req.attached_documents is not None:
        record.attached_documents = req.attached_documents

    record.updated_at = datetime.now(timezone.utc)
    _APPLICATIONS_STORE[application_id] = record
    return record


@router.get("/{application_id}/receipt")
async def download_receipt(application_id: str):
    """Streams the official submission receipt PDF directly (APP-05)."""
    _seed_default_applications()
    record = _APPLICATIONS_STORE.get(application_id)
    if not record:
        # If record not found, synthesize a generic one for test or demo
        record = ApplicationRecord(
            id=application_id,
            service_id="gov-service",
            service_name="Government Public Service Scheme",
            department="Government of India",
            category="Citizen Benefit",
            portal_url="https://india.gov.in",
            status="submitted",
            acknowledgement_number=f"GOV2026/APPL/{application_id[:8].upper()}",
            submission_timestamp=datetime.now(timezone.utc),
        )

    # If receipt file exists on disk, stream it
    if record.receipt_path and os.path.exists(record.receipt_path):
        ack = record.acknowledgement_number or application_id
        safe_ack = ack.replace("/", "_").replace("-", "_")
        return FileResponse(
            path=record.receipt_path,
            media_type="application/pdf",
            filename=f"CivicPilot_Receipt_{safe_ack}.pdf",
        )

    # Generate receipt PDF bytes on the fly
    pdf_bytes = ReceiptGenerator.generate_receipt_pdf(
        application=record,
        profile_data=record.populated_data,
    )

    # Cache to disk for future downloads
    try:
        saved_path = ReceiptGenerator.save_receipt_file(
            application_id=record.id,
            receipt_bytes=pdf_bytes,
        )
        record.receipt_path = saved_path
    except Exception:
        pass

    ack = record.acknowledgement_number or application_id
    safe_ack = ack.replace("/", "_").replace("-", "_")
    filename = f"CivicPilot_Receipt_{safe_ack}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )
