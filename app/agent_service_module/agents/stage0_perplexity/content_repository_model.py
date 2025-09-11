"""
Content Repository Model - Matches SQLAlchemy schema structure
Handles content repository data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.content_repository_table import ContentRepositoryTableConfig
from app.config.settings import settings

class ContentRepositoryModel(BaseModel):
    """Content repository model matching SQLAlchemy schema"""
    
    # SQLAlchemy: content_id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Content ID (UUID as string)")
    
    # SQLAlchemy: request_id (UUID) -> DynamoDB: request_id (String)
    request_id: str = Field(..., description="Request ID reference (UUID as string)")
    
    # SQLAlchemy: project_id (UUID) -> DynamoDB: project_id (String)
    project_id: str = Field(..., description="Project ID reference (UUID as string)")
    
    # SQLAlchemy: canonical_url (String) -> DynamoDB: canonical_url (String)
    canonical_url: str = Field(..., description="Canonical URL")
    
    # SQLAlchemy: title (String) -> DynamoDB: title (String)
    title: str = Field(..., description="Content title")
    
    # SQLAlchemy: content_hash (String) -> DynamoDB: content_hash (String)
    content_hash: str = Field(..., description="Content hash")
    
    # SQLAlchemy: source_type (String) -> DynamoDB: source_type (String)
    source_type: str = Field(..., description="Source type")
    
    # SQLAlchemy: version (Integer) -> DynamoDB: version (Number)
    version: Optional[int] = Field(None, description="Version number")
    
    # SQLAlchemy: is_canonical (Boolean) -> DynamoDB: is_canonical (Boolean)
    is_canonical: Optional[bool] = Field(None, description="Canonical status")
    
    # SQLAlchemy: relevance_type (String) -> DynamoDB: relevance_type (String)
    relevance_type: str = Field(..., description="Relevance type")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: updated_at (DateTime) -> DynamoDB: updated_at (String)
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ContentRepositoryTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, request_id: str, project_id: str, canonical_url: str, title: str,
                   content_hash: str, source_type: str, relevance_type: str,
                   version: Optional[int] = None, is_canonical: Optional[bool] = None) -> 'ContentRepositoryModel':
        """Create a new content repository instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            request_id=request_id,
            project_id=project_id,
            canonical_url=canonical_url,
            title=title,
            content_hash=content_hash,
            source_type=source_type,
            version=version,
            is_canonical=is_canonical,
            relevance_type=relevance_type,
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentRepositoryModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "content_id": self.pk,  # Return as 'content_id' for API consistency
            "request_id": self.request_id,
            "project_id": self.project_id,
            "canonical_url": self.canonical_url,
            "title": self.title,
            "content_hash": self.content_hash,
            "source_type": self.source_type,
            "version": self.version,
            "is_canonical": self.is_canonical,
            "relevance_type": self.relevance_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow().isoformat() 