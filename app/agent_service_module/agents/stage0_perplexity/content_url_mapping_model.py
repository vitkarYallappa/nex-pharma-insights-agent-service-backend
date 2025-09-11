"""
Content URL Mapping Model - Matches SQLAlchemy schema structure
Handles content URL mapping data operations with DynamoDB
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from decimal import Decimal

from app.config.table_configs.content_url_mapping_table import ContentUrlMappingTableConfig
from app.config.settings import settings

class ContentUrlMappingModel(BaseModel):
    """Content URL mapping model matching SQLAlchemy schema"""
    
    # SQLAlchemy: url_id (UUID) -> DynamoDB: pk (String)
    pk: str = Field(..., description="URL ID (UUID as string)")
    
    # SQLAlchemy: discovered_url (String) -> DynamoDB: discovered_url (String)
    discovered_url: str = Field(..., description="Discovered URL")
    
    # SQLAlchemy: title (String) -> DynamoDB: title (String)
    title: str = Field(..., description="Content title")
    
    # SQLAlchemy: content_id (UUID) -> DynamoDB: content_id (String)
    content_id: str = Field(..., description="Content ID reference (UUID as string)")
    
    # SQLAlchemy: source_domain (String) -> DynamoDB: source_domain (String)
    source_domain: Optional[str] = Field(None, description="Source domain")
    
    # SQLAlchemy: is_canonical (Boolean) -> DynamoDB: is_canonical (Boolean)
    is_canonical: Optional[bool] = Field(None, description="Canonical flag")
    
    # SQLAlchemy: dedup_confidence (Numeric) -> DynamoDB: dedup_confidence (Number)
    dedup_confidence: Optional[float] = Field(None, description="Deduplication confidence score")
    
    # SQLAlchemy: dedup_method (String) -> DynamoDB: dedup_method (String)
    dedup_method: Optional[str] = Field(None, description="Deduplication method")
    
    # SQLAlchemy: discovered_at (DateTime) -> DynamoDB: discovered_at (String)
    discovered_at: Optional[str] = Field(None, description="Discovery timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return ContentUrlMappingTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
    
    @classmethod
    def create_new(cls, discovered_url: str, title: str, content_id: str,
                   source_domain: Optional[str] = None, is_canonical: Optional[bool] = None,
                   dedup_confidence: Optional[float] = None, dedup_method: Optional[str] = None) -> 'ContentUrlMappingModel':
        """Create a new content URL mapping instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            discovered_url=discovered_url,
            title=title,
            content_id=content_id,
            source_domain=source_domain,
            is_canonical=is_canonical,
            dedup_confidence=dedup_confidence,
            dedup_method=dedup_method,
            discovered_at=now
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
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentUrlMappingModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "url_id": self.pk,  # Return as 'url_id' for API consistency
            "discovered_url": self.discovered_url,
            "title": self.title,
            "content_id": self.content_id,
            "source_domain": self.source_domain,
            "is_canonical": self.is_canonical,
            "dedup_confidence": self.dedup_confidence,
            "dedup_method": self.dedup_method,
            "discovered_at": self.discovered_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ['pk', 'discovered_at']:
                setattr(self, key, value)
    
    def mark_as_canonical(self) -> None:
        """Mark URL mapping as canonical"""
        self.is_canonical = True
    
    def mark_as_duplicate(self, confidence: float, method: str) -> None:
        """Mark URL mapping as duplicate with confidence score"""
        self.is_canonical = False
        self.dedup_confidence = confidence
        self.dedup_method = method
    
    def update_dedup_info(self, confidence: float, method: str) -> None:
        """Update deduplication information"""
        self.dedup_confidence = confidence
        self.dedup_method = method 