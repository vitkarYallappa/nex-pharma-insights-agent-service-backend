from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.base_schema import DataResponse, ListResponse
from app.models.project_model import ProjectModel


class ProjectCreateRequest(BaseModel):
    """Project creation request schema."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    created_by: str = Field(..., description="Creator user ID")
    status: Optional[str] = Field(None, description="Project status")
    project_metadata: Optional[dict] = Field(default_factory=dict, description="Project metadata")
    module_config: Optional[dict] = Field(default_factory=dict, description="Module configuration")


class ProjectUpdateRequest(BaseModel):
    """Project update request schema."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: Optional[str] = Field(None, description="Project status")
    project_metadata: Optional[dict] = Field(None, description="Project metadata")
    module_config: Optional[dict] = Field(None, description="Module configuration")


class ProjectResponse(BaseModel):
    """Project response schema."""
    
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    created_by: str = Field(..., description="Creator user ID")
    status: Optional[str] = Field(None, description="Project status")
    project_metadata: Optional[dict] = Field(default_factory=dict, description="Project metadata")
    module_config: Optional[dict] = Field(default_factory=dict, description="Module configuration")
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    class Config:
        from_attributes = True


class ProjectListResponse(ListResponse[ProjectResponse]):
    """Project list response schema."""
    pass


class ProjectDataResponse(DataResponse[ProjectResponse]):
    """Single project response schema."""
    pass 