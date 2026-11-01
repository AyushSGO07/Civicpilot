"""Router for searching and discovering verified government schemes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.models.service import GovernmentServiceResponse
from app.services.scheme_search import search_services, get_service_by_id

router = APIRouter(prefix="/services", tags=["Government Services & Schemes"])


@router.get(
    "",
    response_model=List[GovernmentServiceResponse],
    summary="Search and filter government schemes (DISC-01, DISC-02)",
)
async def list_services(
    q: Optional[str] = Query(None, description="Natural language search keyword"),
    category: Optional[str] = Query(None, description="Category filter"),
    state: Optional[str] = Query(None, description="State / UT domicile filter"),
):
    """Retrieve verified official schemes filtered by keyword, category, or state."""
    return search_services(query=q, category=category, state=state)


@router.get(
    "/{service_id}",
    response_model=GovernmentServiceResponse,
    summary="Get scheme details by ID (DISC-03, DISC-04)",
)
async def get_service(service_id: str):
    """Retrieve complete official scheme criteria, required documents, and portal URLs."""
    service = get_service_by_id(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Government service '{service_id}' not found in official catalog",
        )
    return service
