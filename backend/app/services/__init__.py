"""Service layer modules for CivicPilot backend."""

from app.services.ocr import extract_document_fields, ExtractedDocumentData

__all__ = ["extract_document_fields", "ExtractedDocumentData"]
