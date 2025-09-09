from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class SerpRequest(BaseModel):
    """Request model for SERP API calls"""
    query: str = Field(..., description="Search query")
    num_results: int = Field(default=10, ge=1, le=100)
    language: str = Field(default="en")
    country: str = Field(default="us")
    engine: str = Field(default="google")

class SerpResult(BaseModel):
    """Individual search result"""
    title: str = Field(..., description="Page title")
    url: HttpUrl = Field(..., description="Page URL")
    snippet: str = Field(..., description="Search snippet")
    position: int = Field(..., description="Result position")
    domain: str = Field(..., description="Website domain")
    published_date: Optional[datetime] = Field(default=None)

class SerpResponse(BaseModel):
    """Complete SERP API response"""
    request_id: str = Field(..., description="Request identifier")
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total results")
    results: List[SerpResult] = Field(..., description="Search results")
    search_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_urls(self) -> List[str]:
        """Extract URLs from results"""
        return [str(result.url) for result in self.results]
