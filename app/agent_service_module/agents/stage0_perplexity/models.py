from typing import Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class ExtractedContent(BaseModel):
    """Individual extracted content item"""
    url: HttpUrl = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Extracted content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    author: Optional[str] = Field(default=None)
    published_date: Optional[datetime] = Field(default=None)
    word_count: int = Field(default=0)
    language: str = Field(default="en")
    content_type: str = Field(default="article")
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def is_high_quality(self) -> bool:
        """Check if content meets quality threshold"""
        return (self.extraction_confidence >= 0.7 and 
                self.word_count >= 100 and 
                len(self.title) >= 10)
