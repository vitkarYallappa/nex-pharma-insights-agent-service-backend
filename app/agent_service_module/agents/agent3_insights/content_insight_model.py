"""
Content Insight Model - Matches SQLAlchemy schema structure
Handles content insight data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.table_configs.content_insight_table import ContentInsightTableConfig
from app.config.settings import settings

class ContentInsightModel(BaseModel):
    """Content insight model matching SQLAlchemy schema"""
    
    # SQLAlchemy: insight_id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="Insight ID (UUID as string)")
    
    # SQLAlchemy: url_id (UUID) -> DynamoDB: url_id (String)
    url_id: str = Field(..., description="URL ID reference (UUID as string)")
    
    # SQLAlchemy: content_id (UUID) -> DynamoDB: content_id (String)
    content_id: str = Field(..., description="Content ID reference (UUID as string)")
    
    # SQLAlchemy: insight_text (String) -> DynamoDB: insight_text (String)
    insight_text: str = Field(..., description="Insight text")
    
    # SQLAlchemy: insight_content_file_path (String) -> DynamoDB: insight_content_file_path (String)
    insight_content_file_path: str = Field(..., description="Insight content file path")
    
    # SQLAlchemy: insight_category (String) -> DynamoDB: insight_category (String)
    insight_category: Optional[str] = Field(None, description="Insight category")
    
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
        return ContentInsightTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, url_id: str, content_id: str, insight_text: str, insight_content_file_path: str,
                   insight_category: Optional[str] = None, confidence_score: Optional[float] = None,
                   version: Optional[int] = None, is_canonical: Optional[bool] = None,
                   preferred_choice: Optional[bool] = None, created_by: Optional[str] = None) -> 'ContentInsightModel':
        """Create a new content insight instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            url_id=url_id,
            content_id=content_id,
            insight_text=insight_text,
            insight_content_file_path=insight_content_file_path,
            insight_category=insight_category,
            confidence_score=confidence_score,
            version=version if version is not None else 1,
            is_canonical=is_canonical,
            preferred_choice=preferred_choice,
            created_at=now,
            created_by=created_by
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentInsightModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "insight_id": self.pk,  # Return as 'insight_id' for API consistency
            "url_id": self.url_id,
            "content_id": self.content_id,
            "insight_text": self.insight_text,
            "insight_content_file_path": self.insight_content_file_path,
            "insight_category": self.insight_category,
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
        """Mark insight as canonical"""
        self.is_canonical = True
    
    def mark_as_preferred(self) -> None:
        """Mark insight as preferred choice"""
        self.preferred_choice = True
    
    def update_confidence(self, score: float) -> None:
        """Update confidence score"""
        self.confidence_score = score
    
    def update_category(self, category: str) -> None:
        """Update insight category"""
        self.insight_category = category
    
    def increment_version(self) -> None:
        """Increment version number"""
        if self.version is None:
            self.version = 1
        else:
            self.version += 1 