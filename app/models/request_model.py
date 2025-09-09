from typing import Optional, Dict, Any
from pydantic import Field
from app.models.base_model import BaseDataModel


class RequestModel(BaseDataModel):
    """Request data model."""
    
    project_id: str = Field(..., description="Associated project ID")
    request_type: str = Field(..., description="Type of request")
    status: str = Field(default="pending", description="Request status")
    priority: str = Field(default="medium", description="Request priority")
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Request payload")
    response_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Response data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "req_123456789",
                "project_id": "proj_123456789",
                "request_type": "data_analysis",
                "status": "pending",
                "priority": "high",
                "payload": {"data_source": "api", "filters": {}},
                "response_data": {},
                "error_message": None
            }
        } 