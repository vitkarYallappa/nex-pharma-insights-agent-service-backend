from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from app.schemas.base_schema import DataResponse, ListResponse
from app.models.content_repository_model import ContentRepositoryModel


class ContentRepositoryCreateRequest(BaseModel):
    """Content repository creation request schema."""
    
    title: str = Field(..., min_length=1, max_length=255, description="Content title")
    content_type: str = Field(..., description="Type of content")
    content_url: Optional[str] = Field(None, description="URL to content")
    content_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Content data")
    tags: Optional[List[str]] = Field(default_factory=list, description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class ContentRepositoryUpdateRequest(BaseModel):
    """Content repository update request schema."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Content title")
    content_type: Optional[str] = Field(None, description="Type of content")
    content_url: Optional[str] = Field(None, description="URL to content")
    content_data: Optional[Dict[str, Any]] = Field(None, description="Content data")
    tags: Optional[List[str]] = Field(None, description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    status: Optional[str] = Field(None, description="Content status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ContentRepositoryResponse(ContentRepositoryModel):
    """Content repository response schema."""
    pass


class ContentRepositoryListResponse(ListResponse[ContentRepositoryResponse]):
    """Content repository list response schema."""
    pass


class ContentRepositoryDataResponse(DataResponse[ContentRepositoryResponse]):
    """Single content repository response schema."""
    pass 