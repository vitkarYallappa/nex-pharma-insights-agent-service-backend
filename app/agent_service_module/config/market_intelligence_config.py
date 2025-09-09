from typing import List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, HttpUrl


class MarketIntelligenceSource(BaseModel):
    """Configuration for a market intelligence source"""
    name: str = Field(..., description="Source name")
    base_url: HttpUrl = Field(..., description="Base URL for the source")
    source_type: str = Field(..., description="Source category: regulatory, clinical, academic")
    priority: int = Field(default=1, ge=1, le=5, description="Source priority (1=highest)")
    max_results_per_query: int = Field(default=5, ge=1, le=20)
    
    
class MarketIntelligenceConfig(BaseModel):
    """Configuration for Semaglutide and Tirzepatide market intelligence"""
    
    # Project metadata
    title: str = "Semaglutide and Tirzepatide Market Intelligence"
    objective: str = "Monitor regulatory, clinical, and academic market developments for Wegovy (Semaglutide) and emerging Tirzepatide therapies"
    priority: str = "High"
    created_by: str = "user-uuid-here"
    
    # Time range
    start_date: datetime = Field(default_factory=lambda: datetime(2024, 1, 1))
    end_date: datetime = Field(default_factory=lambda: datetime(2025, 12, 31))
    
    # Keywords for search
    primary_keywords: List[str] = Field(default=[
        "semaglutide",
        "tirzepatide", 
        "wegovy",
        "obesity drug",
        "weight loss medication",
        "GLP-1 receptor agonist",
        "diabetes treatment",
        "clinical trials obesity"
    ])
    
    # Base sources
    sources: List[MarketIntelligenceSource] = Field(default=[
        MarketIntelligenceSource(
            name="FDA",
            base_url="https://www.fda.gov",
            source_type="regulatory",
            priority=1,
            max_results_per_query=5
        ),
        MarketIntelligenceSource(
            name="NIH", 
            base_url="https://www.nih.gov",
            source_type="academic",
            priority=2,
            max_results_per_query=5
        ),
        MarketIntelligenceSource(
            name="ClinicalTrials.gov",
            base_url="https://clinicaltrials.gov",
            source_type="clinical", 
            priority=1,
            max_results_per_query=5
        )
    ])
    
    # Processing configuration
    extraction_mode: str = Field(default="summary", description="Content extraction mode")
    batch_size: int = Field(default=5, description="Batch size for content extraction")
    quality_threshold: float = Field(default=0.7, description="Minimum quality threshold")
    
    # Error handling
    max_retries: int = Field(default=2, description="Max retries for failed operations")
    retry_delay: float = Field(default=2.0, description="Delay between retries in seconds")
    
    def get_search_query(self) -> str:
        """Generate search query from keywords"""
        return " OR ".join(self.primary_keywords)
    
    def get_site_specific_query(self, source: MarketIntelligenceSource) -> str:
        """Generate site-specific search query"""
        base_query = self.get_search_query()
        return f"site:{source.base_url} {base_query}"
    
    def get_total_expected_urls(self) -> int:
        """Calculate total expected URLs from all sources"""
        return sum(source.max_results_per_query for source in self.sources)
    
    def get_sources_by_type(self, source_type: str) -> List[MarketIntelligenceSource]:
        """Get sources filtered by type"""
        return [source for source in self.sources if source.source_type == source_type]
    
    def get_processing_metadata(self) -> Dict[str, Any]:
        """Get metadata for processing tracking"""
        return {
            "title": self.title,
            "objective": self.objective,
            "priority": self.priority,
            "created_by": self.created_by,
            "time_range": {
                "start": self.start_date.isoformat(),
                "end": self.end_date.isoformat()
            },
            "sources_count": len(self.sources),
            "keywords_count": len(self.primary_keywords),
            "expected_urls": self.get_total_expected_urls(),
            "extraction_mode": self.extraction_mode
        }


# Default configuration instance
DEFAULT_SEMAGLUTIDE_CONFIG = MarketIntelligenceConfig()


class MarketIntelligenceWorkflow:
    """Workflow orchestrator for market intelligence processing"""
    
    def __init__(self, config: MarketIntelligenceConfig = None):
        self.config = config or DEFAULT_SEMAGLUTIDE_CONFIG
    
    def generate_search_requests(self) -> List[Dict[str, Any]]:
        """Generate individual search requests for each source"""
        requests = []
        
        for source in self.config.sources:
            request = {
                "source_name": source.name,
                "source_type": source.source_type,
                "query": self.config.get_site_specific_query(source),
                "base_url": str(source.base_url),
                "num_results": source.max_results_per_query,
                "priority": source.priority
            }
            requests.append(request)
        
        return requests
    
    def calculate_api_calls(self) -> Dict[str, int]:
        """Calculate expected API calls for the workflow"""
        search_calls = len(self.config.sources)  # One SERP call per source
        expected_urls = self.config.get_total_expected_urls()
        extraction_calls = expected_urls  # One Perplexity call per URL
        
        return {
            "serp_calls": search_calls,
            "perplexity_calls": extraction_calls,
            "total_calls": search_calls + extraction_calls,
            "expected_urls": expected_urls
        }
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get comprehensive workflow summary"""
        api_calls = self.calculate_api_calls()
        
        return {
            "workflow_config": self.config.get_processing_metadata(),
            "search_requests": self.generate_search_requests(),
            "api_call_estimates": api_calls,
            "processing_parameters": {
                "extraction_mode": self.config.extraction_mode,
                "batch_size": self.config.batch_size,
                "quality_threshold": self.config.quality_threshold,
                "max_retries": self.config.max_retries
            }
        } 