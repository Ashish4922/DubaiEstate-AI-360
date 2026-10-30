"""Common Pydantic schemas for API responses and metadata."""

from typing import Any, Optional
from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    """Schema for root API status response."""
    message: str = Field(..., description="API greeting or service status message")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="API semantic version")
    docs_url: str = Field(..., description="URL to interactive Swagger API documentation")


class ErrorResponse(BaseModel):
    """Standardized error response payload."""
    detail: str = Field(..., description="Descriptive error explanation")
    code: Optional[str] = Field(None, description="Optional error classification code")


class StatusResponse(BaseModel):
    """Generic status response container."""
    status: str = Field(..., description="Status indicator")
    data: Optional[Any] = Field(None, description="Optional payload content")
