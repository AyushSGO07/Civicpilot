"""Health check endpoints for CivicPilot backend."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Schema for service health status."""

    status: str = Field(..., description="System health status indicator")
    service: str = Field(..., description="Name of the service")
    version: str = Field(..., description="Application version")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint",
    description="Returns service availability, application name, and running version.",
)
async def check_health() -> HealthResponse:
    """Return the health status of the CivicPilot backend service."""
    return HealthResponse(
        status="ok",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
    )
