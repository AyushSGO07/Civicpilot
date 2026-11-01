"""Main FastAPI application entry point for CivicPilot backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health, profile, documents

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="CivicPilot API - Autonomous Public Service Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware (D-05: Restrict origins explicitly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(profile.router, prefix=settings.API_PREFIX)
app.include_router(documents.router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    """Root redirect / information endpoint."""
    return {
        "message": "Welcome to CivicPilot API",
        "health_check": f"{settings.API_PREFIX}/health",
        "docs": "/docs",
    }
