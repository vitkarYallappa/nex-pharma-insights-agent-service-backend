"""
Content Summary Model - Matches SQLAlchemy schema structure
Handles content summary data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.content_summary_table import ContentSummaryTableConfig
from app.config.settings import settings

class ContentSummaryModel(BaseModel):
    """Content summary model matching SQLAlchemy schema"""
    
    # SQLAlchemy: summary_id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Summary ID (UUID as string)")
    
    # SQLAlchemy: url_id (UUID) -> DynamoDB: url_id (String)
    url_id: str = Field(..., description="URL ID reference (UUID as string)")
    
    # SQLAlchemy: content_id (UUID) -> DynamoDB: content_id (String)
    content_id: str = Field(..., description="Content ID reference (UUID as string)")
    
    # SQLAlchemy: summary_text (String) -> DynamoDB: summary_text (String)
    summary_text: str = Field(..., description="Summary text")
    
    # SQLAlchemy: summary_content_file_path (String) -> DynamoDB: summary_content_file_path (String)
    summary_content_file_path: str = Field(..., description="Summary content file path")
    
    # SQLAlchemy: confidence_score (Numeric) -> DynamoDB: confidence_score (Number)
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    
    # SQLAlchemy: version (Integer) -> DynamoDB: version (Number)
    version: Optional[int] = Field(None, description="Version number")
    
    # SQLAlchemy: is_canonical (Boolean) -> DynamoDB: is_canonical (Boolean)
    is_canonical: Optional[bool] = Field(None, description="Canonical flag")
    
    # SQLAlchemy: preferred_choice (Boolean) -> DynamoDB: preferred_choice (Boolean)
    preferred_choice: Optional[bool] = Field(None, description="Preferred choice flag")
    
    # SQLAlchemy: created_at (DateTime) -> DynamoDB: created_at (String)
    created_at: Optional[str] = Field(None, description="Creation timestamp (ISO string)")
    
    # SQLAlchemy: created_by (String) -> DynamoDB: created_by (String)
    created_by: Optional[str] = Field(None, description="Creator identifier")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ContentSummaryTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, url_id: str, content_id: str, summary_text: str, summary_content_file_path: str,
                   confidence_score: Optional[float] = None, version: Optional[int] = None,
                   is_canonical: Optional[bool] = None, preferred_choice: Optional[bool] = None,
                   created_by: Optional[str] = None) -> 'ContentSummaryModel':
        """Create a new content summary instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            url_id=url_id,
            content_id=content_id,
            summary_text=summary_text,
            summary_content_file_path=summary_content_file_path,
            confidence_score=confidence_score,
            version=version if version is not None else 1,
            is_canonical=is_canonical,
            preferred_choice=preferred_choice,
            created_at=now,
            created_by=created_by
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        from decimal import Decimal
        
        data = self.model_dump()
        
        # Convert float values to Decimal for DynamoDB compatibility
        for key, value in data.items():
            if isinstance(value, float):
                data[key] = Decimal(str(value))
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentSummaryModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "summary_id": self.pk,  # Return as 'summary_id' for API consistency
            "url_id": self.url_id,
            "content_id": self.content_id,
            "summary_text": self.summary_text,
            "summary_content_file_path": self.summary_content_file_path,
            "confidence_score": self.confidence_score,
            "version": self.version,
            "is_canonical": self.is_canonical,
            "preferred_choice": self.preferred_choice,
            "created_at": self.created_at,
            "created_by": self.created_by
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'created_at']:
                setattr(self, key, value)
    
    def mark_as_canonical(self) -> None:
        """Mark summary as canonical"""
        self.is_canonical = True
    
    def mark_as_preferred(self) -> None:
        """Mark summary as preferred choice"""
        self.preferred_choice = True
    
    def update_confidence(self, score: float) -> None:
        """Update confidence score"""
        self.confidence_score = score
    
    def increment_version(self) -> None:
        """Increment version number"""
        if self.version is None:
            self.version = 1
        else:
            self.version += 1 