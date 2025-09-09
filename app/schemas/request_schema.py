from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.base_schema import DataResponse, ListResponse
from app.models.request_model import RequestModel


class RequestCreateRequest(BaseModel):
    """Request creation request schema."""
    
    project_id: str = Field(..., description="Associated project ID")
    request_type: str = Field(..., description="Type of request")
    priority: Optional[str] = Field("medium", description="Request priority")
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Request payload")


class RequestUpdateRequest(BaseModel):
    """Request update request schema."""
    
    status: Optional[str] = Field(None, description="Request status")
    priority: Optional[str] = Field(None, description="Request priority")
    payload: Optional[Dict[str, Any]] = Field(None, description="Request payload")
    response_data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class RequestResponse(RequestModel):
    """Request response schema."""
    pass


class RequestListResponse(ListResponse[RequestResponse]):
    """Request list response schema."""
    pass


class RequestDataResponse(DataResponse[RequestResponse]):
    """Single request response schema."""
    pass 