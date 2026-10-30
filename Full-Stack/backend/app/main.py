"""DubaiEstate AI 360 - Backend Application Entry Point.

Week 1 Day 1: Architecture skeleton foundation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.schemas.common import RootResponse
from app.utils.logger import logger

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Agentic AI-Powered Real Estate Investment, Brokerage & Property Management Intelligence Platform API",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get(
    "/",
    response_model=RootResponse,
    summary="Root Service Status",
    tags=["Root"],
)
async def root() -> RootResponse:
    """Return backend service metadata and documentation links."""
    return RootResponse(
        message="DubaiEstate AI 360 Backend API is running.",
        app=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
    )


@app.on_event("startup")
async def on_startup() -> None:
    """Log service startup information."""
    logger.info(
        "Started %s in %s mode (Host: %s, Port: %s)",
        settings.app_name,
        settings.app_env,
        settings.backend_host,
        settings.backend_port,
    )
