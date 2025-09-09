from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class PipelineStatus(str, Enum):
    PENDING = "pending"
    SEARCHING = "searching"
    EXTRACTING = "extracting"
    AGGREGATING = "aggregating"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"

class IngestionRequest(BaseModel):
    """Complete ingestion pipeline request"""
    query: str = Field(..., description="Search query")
    num_results: int = Field(default=10, ge=1, le=100, description="Number of search results")
    extraction_mode: str = Field(default="summary", description="Content extraction mode")
    request_id: Optional[str] = Field(default=None, description="Optional request ID")
    search_engines: List[str] = Field(default=["google"], description="Search engines to use")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    
    def generate_request_id(self) -> str:
        """Generate unique request ID if not provided"""
        if not self.request_id:
            timestamp = int(datetime.utcnow().timestamp() * 1000)
            query_hash = abs(hash(self.query)) % 10000
            self.request_id = f"ing_{timestamp}_{query_hash}"
        return self.request_id

class PipelineState(BaseModel):
    """Pipeline execution state tracking"""
    request_id: str = Field(..., description="Request identifier")
    status: PipelineStatus = Field(default=PipelineStatus.PENDING)
    current_stage: str = Field(default="initialization")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Stage-specific tracking
    search_completed: bool = Field(default=False)
    extraction_completed: bool = Field(default=False)
    aggregation_completed: bool = Field(default=False)
    
    # Result counts
    urls_found: int = Field(default=0)
    content_extracted: int = Field(default=0)
    content_failed: int = Field(default=0)
    
    # Timing information
    started_at: datetime = Field(default_factory=datetime.utcnow)
    search_started_at: Optional[datetime] = Field(default=None)
    extraction_started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Error tracking
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    def add_error(self, error: str):
        """Add error to tracking"""
        self.errors.append(f"{datetime.utcnow().isoformat()}: {error}")
    
    def add_warning(self, warning: str):
        """Add warning to tracking"""
        self.warnings.append(f"{datetime.utcnow().isoformat()}: {warning}")
    
    def update_progress(self):
        """Update progress percentage based on completed stages"""
        completed_stages = 0
        total_stages = 3  # search, extraction, aggregation
        
        if self.search_completed:
            completed_stages += 1
        if self.extraction_completed:
            completed_stages += 1
        if self.aggregation_completed:
            completed_stages += 1
        
        self.progress_percentage = (completed_stages / total_stages) * 100

class IngestionResponse(BaseModel):
    """Complete ingestion pipeline response"""
    request_id: str = Field(..., description="Request identifier")
    status: PipelineStatus = Field(..., description="Final pipeline status")
    
    # Input data
    original_query: str = Field(..., description="Original search query")
    
    # Search results
    search_results: Dict[str, Any] = Field(default_factory=dict, description="SERP results")
    urls_found: int = Field(default=0)
    
    # Extraction results
    extraction_results: Dict[str, Any] = Field(default_factory=dict, description="Content extraction results")
    content_extracted: int = Field(default=0)
    content_failed: int = Field(default=0)
    
    # Aggregated data
    aggregated_content: List[Dict[str, Any]] = Field(default_factory=list, description="Combined results")
    high_quality_content: List[Dict[str, Any]] = Field(default_factory=list, description="High quality content")
    
    # Processing metadata
    processing_time: float = Field(default=0.0, description="Total processing time")
    stages_completed: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Storage information
    storage_paths: Dict[str, str] = Field(default_factory=dict, description="Storage locations")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_successful(self) -> bool:
        """Check if pipeline was successful"""
        return self.status in [PipelineStatus.COMPLETED, PipelineStatus.PARTIAL_SUCCESS]
    
    def get_success_rate(self) -> float:
        """Calculate content extraction success rate"""
        total = self.content_extracted + self.content_failed
        return (self.content_extracted / total * 100) if total > 0 else 0.0

class RetryConfig(BaseModel):
    """Retry configuration for pipeline operations"""
    max_retries: int = Field(default=3, ge=0, le=10)
    initial_delay: float = Field(default=1.0, ge=0.1, le=10.0)
    max_delay: float = Field(default=60.0, ge=1.0, le=300.0)
    exponential_base: float = Field(default=2.0, ge=1.1, le=5.0)
    retry_on_statuses: List[str] = Field(default=["failed", "timeout", "rate_limited"])

# Legacy models for backward compatibility
class Stage0OrchestratorRequest(BaseModel):
    """Legacy request model for stage0_orchestrator - maintained for compatibility"""
    request_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class Stage0OrchestratorResponse(BaseModel):
    """Legacy response model for stage0_orchestrator - maintained for compatibility"""
    request_id: str
    result: Dict[str, Any]
    status: str
    timestamp: datetime = datetime.utcnow()
