from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class SerpRequest(BaseModel):
    """Request model for SERP API calls"""
    query: str = Field(..., description="Search query")
    num_results: int = Field(default=10, ge=1, le=100)
    language: str = Field(default="en")
    country: str = Field(default="us")
    engine: str = Field(default="google")
    # Date filtering parameters
    date_filter: Optional[str] = Field(default=None, description="Date filter: d (day), w (week), m (month), y (year)")
    start_date: Optional[str] = Field(default=None, description="Start date in YYYY-MM-DD format")
    end_date: Optional[str] = Field(default=None, description="End date in YYYY-MM-DD format")

    @validator('query')
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

    @validator('num_results')
    def validate_num_results(cls, v):
        if v < 1:
            return 1
        if v > 100:
            return 100
        return v

class SerpResult(BaseModel):
    """Individual search result with flexible URL handling"""
    title: str = Field(..., description="Page title")
    url: str = Field(..., description="Page URL")  # Changed from HttpUrl to str for flexibility
    snippet: str = Field(..., description="Search snippet")
    position: int = Field(..., description="Result position")
    domain: str = Field(..., description="Website domain")
    published_date: Optional[datetime] = Field(default=None)

    @validator('url')
    def validate_url(cls, v):
        if not v:
            return ""
        
        # Basic URL validation and cleaning
        v = v.strip()
        
        # Add protocol if missing
        if v and not v.startswith(('http://', 'https://', 'ftp://')):
            v = f"https://{v}"
        
        return v

    @validator('title')
    def validate_title(cls, v):
        return v.strip() if v else ""

    @validator('snippet')
    def validate_snippet(cls, v):
        return v.strip() if v else ""

class SerpResponse(BaseModel):
    """Complete SERP API response with enhanced metadata"""
    request_id: str = Field(..., description="Request identifier")
    query: str = Field(..., description="Original query")
    total_results: int = Field(default=0, description="Total results")
    results: List[SerpResult] = Field(default_factory=list, description="Search results")
    search_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_urls(self) -> List[str]:
        """Extract URLs from results"""
        return [result.url for result in self.results if result.url]
    
    def get_domains(self) -> List[str]:
        """Extract unique domains from results"""
        domains = [result.domain for result in self.results if result.domain]
        return list(set(domains))
    
    def get_top_results(self, count: int = 5) -> List[SerpResult]:
        """Get top N results"""
        return self.results[:count]
    
    def filter_by_domain(self, domain: str) -> List[SerpResult]:
        """Filter results by domain"""
        return [result for result in self.results if domain.lower() in result.domain.lower()]
