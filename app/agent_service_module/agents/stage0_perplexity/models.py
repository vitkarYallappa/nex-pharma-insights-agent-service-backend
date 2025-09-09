from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class ContentExtractionRequest(BaseModel):
    """Request for extracting content from URLs"""
    urls: List[HttpUrl] = Field(..., description="URLs to extract")
    request_id: str = Field(..., description="SERP request ID")
    extraction_mode: str = Field(default="summary", description="full|summary|metadata")
    max_content_length: int = Field(default=5000, description="Max content length")

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

class PerplexityResponse(BaseModel):
    """Complete content extraction response"""
    request_id: str = Field(..., description="Request ID")
    total_urls: int = Field(..., description="Total URLs processed")
    successful_extractions: int = Field(..., description="Successful extractions")
    failed_extractions: int = Field(..., description="Failed extractions")
    extracted_content: List[ExtractedContent] = Field(..., description="Content items")
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_successful_content(self) -> List[ExtractedContent]:
        """Get successfully extracted content"""
        return [content for content in self.extracted_content if content.content]
    
    def get_high_quality_content(self) -> List[ExtractedContent]:
        """Get high quality content only"""
        return [content for content in self.extracted_content if content.is_high_quality()]

class BatchExtractionStatus(BaseModel):
    """Batch processing status tracking"""
    batch_id: str = Field(..., description="Batch ID")
    total_urls: int = Field(..., description="Total URLs")
    completed: int = Field(default=0)
    failed: int = Field(default=0)
    in_progress: int = Field(default=0)
    status: str = Field(default="pending")
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_urls == 0:
            return 0.0
        return (self.completed + self.failed) / self.total_urls * 100

# Legacy models for backward compatibility with existing service structure
class Stage0PerplexityRequest(BaseModel):
    """Legacy request model for stage0_perplexity - maintained for compatibility"""
    request_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class Stage0PerplexityResponse(BaseModel):
    """Legacy response model for stage0_perplexity - maintained for compatibility"""
    request_id: str
    result: Dict[str, Any]
    status: str
    timestamp: datetime = datetime.utcnow()
