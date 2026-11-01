"""Citizen document vault router for uploading, listing, viewing, and deleting documents."""

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse, Response

from app.models.document import (
    DocumentResponse,
    ConfirmExtractedRequest,
)
from app.routers.profile import get_current_user_id, _PROFILES_STORE
from app.services.ocr import extract_document_fields

router = APIRouter(prefix="/documents", tags=["Document Vault"])

# Storage directory for local secure vault fallback
VAULT_STORAGE_DIR = Path("storage/vault")
VAULT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# In-memory document metadata store for deterministic testing & offline execution
_DOCUMENTS_STORE: Dict[str, dict] = {}

ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload document to secure vault",
)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form("Other"),
    user_id: str = Depends(get_current_user_id),
):
    """Upload a PDF, JPG, or PNG document (max 10MB) into the citizen's secure vault."""
    # 1. Validate MIME type
    content_type = file.content_type or ""
    if content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{content_type}'. Supported types: PDF, JPG, PNG",
        )

    # 2. Read contents and check size
    contents = await file.read()
    file_size = len(contents)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size ({file_size} bytes) exceeds maximum limit of 10MB",
        )
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File cannot be empty",
        )

    # 3. Store file locally in private directory
    doc_id = str(uuid.uuid4())
    user_vault = VAULT_STORAGE_DIR / user_id
    user_vault.mkdir(parents=True, exist_ok=True)

    sanitized_filename = os.path.basename(file.filename or f"doc_{doc_id}")
    storage_path = user_vault / f"{doc_id}_{sanitized_filename}"

    with open(storage_path, "wb") as f:
        f.write(contents)

    now = datetime.now(timezone.utc)
    doc_record = {
        "id": doc_id,
        "user_id": user_id,
        "document_name": sanitized_filename,
        "document_type": document_type,
        "mime_type": content_type,
        "file_size_bytes": file_size,
        "storage_path": str(storage_path),
        "download_url": f"/api/documents/{doc_id}/download",
        "extracted_information": {},
        "verification_status": "Unverified",
        "created_at": now,
        "updated_at": now,
    }
    _DOCUMENTS_STORE[doc_id] = doc_record

    return DocumentResponse(**doc_record)


@router.get(
    "",
    response_model=List[DocumentResponse],
    summary="List all citizen documents",
)
async def list_documents(
    user_id: str = Depends(get_current_user_id),
):
    """Retrieve all uploaded documents owned by the authenticated citizen."""
    user_docs = [
        DocumentResponse(**doc)
        for doc in _DOCUMENTS_STORE.values()
        if doc["user_id"] == user_id
    ]
    # Sort newest first
    user_docs.sort(key=lambda d: d.created_at, reverse=True)
    return user_docs


@router.get(
    "/{doc_id}",
    response_model=DocumentResponse,
    summary="Get document metadata and download link",
)
async def get_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Retrieve document metadata by ID."""
    doc = _DOCUMENTS_STORE.get(doc_id)
    if not doc or doc["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in citizen vault",
        )
    return DocumentResponse(**doc)


@router.get(
    "/{doc_id}/download",
    summary="Download or stream document file",
)
async def download_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Stream protected document content."""
    doc = _DOCUMENTS_STORE.get(doc_id)
    if not doc or doc["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    file_path = Path(doc["storage_path"])
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored file content not found",
        )

    return FileResponse(
        path=file_path,
        media_type=doc["mime_type"],
        filename=doc["document_name"],
    )


@router.delete(
    "/{doc_id}",
    summary="Delete document from vault",
)
async def delete_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Permanently delete document and remove underlying stored file (DOC-05)."""
    doc = _DOCUMENTS_STORE.get(doc_id)
    if not doc or doc["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in citizen vault",
        )

    # Remove stored physical file if present
    file_path = Path(doc["storage_path"])
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass

    del _DOCUMENTS_STORE[doc_id]
    return {
        "message": "Document deleted successfully",
        "id": doc_id,
    }



@router.post(
    "/{doc_id}/ocr",
    summary="Trigger Gemini multimodal OCR on document (DOC-03)",
)
async def run_ocr_on_document(
    doc_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Trigger multimodal document extraction using Gemini 2.5 Flash."""
    doc = _DOCUMENTS_STORE.get(doc_id)
    if not doc or doc["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in citizen vault",
        )

    file_path = Path(doc["storage_path"])
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored document file not found on disk",
        )

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    extracted = await extract_document_fields(
        file_bytes=file_bytes,
        mime_type=doc["mime_type"],
        document_type=doc["document_type"],
        filename=doc["document_name"],
    )

    doc["extracted_information"] = extracted.model_dump()
    doc["verification_status"] = "Extracted"
    doc["updated_at"] = datetime.now(timezone.utc)
    _DOCUMENTS_STORE[doc_id] = doc

    return {
        "document_id": doc_id,
        "verification_status": "Extracted",
        "extracted_information": doc["extracted_information"],
    }


@router.post(
    "/{doc_id}/confirm",
    summary="Confirm extracted OCR fields into citizen profile (DOC-04)",
)
async def confirm_extracted_fields(
    doc_id: str,
    payload: ConfirmExtractedRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Merge citizen-approved extracted fields into citizen profile (DOC-04)."""
    doc = _DOCUMENTS_STORE.get(doc_id)
    if not doc or doc["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in citizen vault",
        )

    profile_data = _PROFILES_STORE.get(user_id)
    now = datetime.now(timezone.utc)
    if not profile_data:
        profile_data = {
            "id": user_id,
            "full_name": "Citizen User",
            "date_of_birth": None,
            "gender": None,
            "contact_number": None,
            "state": None,
            "district": None,
            "pincode": None,
            "education_level": None,
            "institution_name": None,
            "course": None,
            "academic_year": None,
            "occupation": None,
            "annual_income": None,
            "social_category": None,
            "disability_status": False,
            "minority_status": False,
            "created_at": now,
            "updated_at": now,
        }

    # Merge confirmed fields
    for field, val in payload.fields_to_confirm.items():
        if val is not None and field in profile_data:
            profile_data[field] = val

    profile_data["updated_at"] = now
    _PROFILES_STORE[user_id] = profile_data

    # Mark document as Verified
    doc["verification_status"] = "Verified"
    doc["updated_at"] = now
    _DOCUMENTS_STORE[doc_id] = doc

    return {
        "message": "Citizen profile successfully synchronized with verified document attributes",
        "document_id": doc_id,
        "verification_status": "Verified",
        "profile": profile_data,
    }
