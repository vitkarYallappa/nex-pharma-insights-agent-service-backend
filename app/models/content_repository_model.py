from typing import Optional, List, Dict, Any
from pydantic import Field
from app.models.base_model import BaseDataModel


class ContentRepositoryModel(BaseDataModel):
    """Content repository data model."""
    
    title: str = Field(..., description="Content title")
    content_type: str = Field(..., description="Type of content")
    content_url: Optional[str] = Field(None, description="URL to content")
    content_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Content data")
    tags: Optional[List[str]] = Field(default_factory=list, description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    status: str = Field(default="active", description="Content status")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "content_123456789",
                "title": "Sample Content",
                "content_type": "article",
                "content_url": "https://example.com/content",
                "content_data": {"summary": "This is a sample content"},
                "tags": ["sample", "article"],
                "category": "documentation",
                "status": "active",
                "metadata": {"author": "John Doe"}
            }
        } 