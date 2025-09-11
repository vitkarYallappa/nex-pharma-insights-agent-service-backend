from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
import uuid


class RequestStatus(str, Enum):
    """Status of a market intelligence request"""
    PENDING = "pending"
    PROCESSING = "processing"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RequestType(str, Enum):
    """Type of market intelligence request"""
    SEMAGLUTIDE_INTELLIGENCE = "semaglutide_intelligence"
    # Future request types can be added here
    # CUSTOM_INTELLIGENCE = "custom_intelligence"
    # COMPETITIVE_ANALYSIS = "competitive_analysis"


class Priority(str, Enum):
    """Priority level for request processing"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProcessingStrategy(str, Enum):
    """Processing strategy for request handling"""
    TABLE = "table"
    SQS = "sqs"


class RequestProgress(BaseModel):
    """Progress tracking for market intelligence requests"""
    current_stage: str = Field(default="initialization", description="Current processing stage")
    percentage: float = Field(default=0.0, ge=0.0, le=100.0, description="Progress percentage")
    urls_found: int = Field(default=0, ge=0, description="Number of URLs discovered")
    content_extracted: int = Field(default=0, ge=0, description="Number of content items extracted")
    processing_errors: int = Field(default=0, ge=0, description="Number of processing errors encountered")
    estimated_completion: Optional[datetime] = Field(default=None, description="Estimated completion time")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last progress update")
    
    def update_progress(self, stage: str, percentage: float, **kwargs):
        """Update progress information"""
        self.current_stage = stage
        self.percentage = min(100.0, max(0.0, percentage))
        self.last_updated = datetime.utcnow()
        
        # Update optional fields if provided
        if "urls_found" in kwargs:
            self.urls_found = kwargs["urls_found"]
        if "content_extracted" in kwargs:
            self.content_extracted = kwargs["content_extracted"]
        if "processing_errors" in kwargs:
            self.processing_errors = kwargs["processing_errors"]
        if "estimated_completion" in kwargs:
            self.estimated_completion = kwargs["estimated_completion"]


class RequestResults(BaseModel):
    """Results of a completed market intelligence request"""
    report_path: Optional[str] = Field(default=None, description="Path to the generated report")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Summary of results")
    execution_summary: Dict[str, Any] = Field(default_factory=dict, description="Execution statistics")
    intelligence_data: Dict[str, Any] = Field(default_factory=dict, description="Categorized intelligence data")
    structured_outputs: List[Dict[str, Any]] = Field(default_factory=list, description="Structured output examples")
    quality_metrics: Dict[str, Any] = Field(default_factory=dict, description="Content quality metrics")
    processing_metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    
    def get_success_rate(self) -> float:
        """Calculate overall success rate"""
        execution = self.execution_summary
        total = execution.get("total_urls_discovered", 0)
        extracted = execution.get("total_content_extracted", 0)
        return (extracted / total * 100) if total > 0 else 0.0
    
    def get_content_count_by_type(self) -> Dict[str, int]:
        """Get content count by source type"""
        intelligence = self.intelligence_data
        return {
            "regulatory": intelligence.get("regulatory_content", {}).get("count", 0),
            "clinical": intelligence.get("clinical_content", {}).get("count", 0),
            "academic": intelligence.get("academic_content", {}).get("count", 0)
        }


class DateRangeConfig(BaseModel):
    """Date range configuration for searches"""
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    
    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        from datetime import datetime
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v


class SourceConfig(BaseModel):
    """Source configuration for data extraction"""
    name: str = Field(..., description="Source name")
    type: str = Field(..., description="Source type (clinical, academic, government, etc.)")
    url: str = Field(..., description="Source URL")
    
    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v


class MarketIntelligenceRequestConfig(BaseModel):
    """Configuration for market intelligence request"""
    keywords: List[str] = Field(
        default=[
            "semaglutide", "tirzepatide", "wegovy", "obesity drug", 
            "weight loss medication", "GLP-1 receptor agonist", 
            "diabetes treatment", "clinical trials obesity"
        ],
        min_items=1, 
        description="Search keywords"
    )
    sources: List[SourceConfig] = Field(
        default=[
            SourceConfig(name="FDA", type="government", url="https://www.fda.gov"),
            SourceConfig(name="NIH", type="academic", url="https://www.nih.gov"),
            SourceConfig(name="ClinicalTrials.gov", type="clinical", url="https://clinicaltrials.gov")
        ],
        min_items=1, 
        description="Data sources configuration"
    )
    extraction_mode: str = Field(default="summary", description="Content extraction mode")
    quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Quality threshold for content")
    batch_size: int = Field(default=5, ge=1, le=20, description="Processing batch size")
    max_retries: int = Field(default=2, ge=0, le=10, description="Maximum retry attempts")
    
    # New fields for SERP/Perplexity integration
    search_query: Optional[str] = Field(default=None, description="Custom search query")
    date_range: Optional[DateRangeConfig] = Field(default=None, description="Date range for searches")
    custom_params: Dict[str, Any] = Field(default_factory=dict, description="Custom parameters")
    
    @validator('extraction_mode')
    def validate_extraction_mode(cls, v):
        valid_modes = ["summary", "full", "metadata"]
        if v not in valid_modes:
            raise ValueError(f"extraction_mode must be one of {valid_modes}")
        return v
    
    @validator('sources', pre=True)
    def validate_sources(cls, v):
        """Convert dict sources to SourceConfig objects if needed"""
        if not v:
            return v
        
        result = []
        for source in v:
            if isinstance(source, dict):
                result.append(SourceConfig(**source))
            elif isinstance(source, SourceConfig):
                result.append(source)
            else:
                raise ValueError("Sources must be dictionaries or SourceConfig objects")
        return result


class MarketIntelligenceRequest(BaseModel):
    """Main model for market intelligence requests"""
    
    # Primary identifiers
    request_id: str = Field(default="", description="Unique request identifier")
    project_id: str = Field(..., description="Project identifier")
    project_request_id: str = Field(..., description="Project identifier")
    user_id: str = Field(..., description="User identifier")
    
    # Request metadata
    request_type: RequestType = Field(default=RequestType.SEMAGLUTIDE_INTELLIGENCE, description="Type of intelligence request")
    status: RequestStatus = Field(default=RequestStatus.PENDING, description="Current request status")
    status_message: Optional[str] = Field(default=None, description="Current status message")
    priority: Priority = Field(default=Priority.MEDIUM, description="Processing priority")
    processing_strategy: ProcessingStrategy = Field(default=ProcessingStrategy.TABLE, description="Processing strategy")
    
    # Configuration
    config: MarketIntelligenceRequestConfig = Field(default_factory=MarketIntelligenceRequestConfig, description="Request configuration")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Request creation time")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update time")
    started_at: Optional[datetime] = Field(default=None, description="Processing start time")
    completed_at: Optional[datetime] = Field(default=None, description="Processing completion time")
    
    # Progress and results
    progress: RequestProgress = Field(default_factory=RequestProgress, description="Progress tracking")
    results: Optional[RequestResults] = Field(default=None, description="Processing results")
    
    # Error tracking
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    
    # Processing metadata
    processing_metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    
    @validator('request_id', pre=True, always=True)
    def generate_request_id(cls, v):
        """Generate request ID if not provided"""
        if not v:
            timestamp = int(datetime.utcnow().timestamp() * 1000)
            unique_id = str(uuid.uuid4())[:8]
            return f"req_{timestamp}_{unique_id}"
        return v
    
    def add_error(self, error: str):
        """Add error message with timestamp"""
        timestamp = datetime.utcnow().isoformat()
        self.errors.append(f"{timestamp}: {error}")
    
    def add_warning(self, warning: str):
        """Add warning message with timestamp"""
        timestamp = datetime.utcnow().isoformat()
        self.warnings.append(f"{timestamp}: {warning}")
    
    def update_status(self, new_status: RequestStatus, message: Optional[str] = None):
        """Update request status with optional message"""
        old_status = self.status
        self.status = new_status
        self.status_message = message
        self.updated_at = datetime.utcnow()
        
        # Update timestamps based on status
        if new_status == RequestStatus.PROCESSING and not self.started_at:
            self.started_at = datetime.utcnow()
        elif new_status in [RequestStatus.COMPLETED, RequestStatus.FAILED, RequestStatus.CANCELLED]:
            self.completed_at = datetime.utcnow()
        
        # Log status change
        if message:
            log_message = f"Status changed from {old_status} to {new_status}: {message}"
        else:
            log_message = f"Status changed from {old_status} to {new_status}"
        
        self.processing_metadata.setdefault("status_history", []).append({
            "timestamp": datetime.utcnow().isoformat(),
            "old_status": old_status,
            "new_status": new_status,
            "message": message
        })
    
    def get_processing_duration(self) -> Optional[float]:
        """Get processing duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.utcnow() - self.started_at).total_seconds()
        return None
    
    def is_active(self) -> bool:
        """Check if request is in active processing state"""
        return self.status in [RequestStatus.PENDING, RequestStatus.PROCESSING, RequestStatus.EXECUTING]
    
    def is_completed(self) -> bool:
        """Check if request is completed (success or failure)"""
        return self.status in [RequestStatus.COMPLETED, RequestStatus.FAILED, RequestStatus.CANCELLED]
    
    def get_priority_score(self) -> int:
        """Get numeric priority score for sorting"""
        priority_scores = {
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1
        }
        return priority_scores.get(self.priority, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return self.dict(by_alias=True, exclude_none=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketIntelligenceRequest":
        """Create instance from dictionary"""
        return cls(**data)


class RequestFilter(BaseModel):
    """Filter criteria for querying requests"""
    status: Optional[RequestStatus] = Field(default=None, description="Filter by status")
    request_type: Optional[RequestType] = Field(default=None, description="Filter by request type")
    priority: Optional[Priority] = Field(default=None, description="Filter by priority")
    user_id: Optional[str] = Field(default=None, description="Filter by user")
    project_id: Optional[str] = Field(default=None, description="Filter by project")
    created_after: Optional[datetime] = Field(default=None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(default=None, description="Filter by creation date")
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class RequestSummary(BaseModel):
    """Summary information for a request (lightweight)"""
    request_id: str
    project_id: str
    user_id: str
    request_type: RequestType
    status: RequestStatus
    priority: Priority
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    progress_percentage: float
    current_stage: str
    
    @classmethod
    def from_request(cls, request: MarketIntelligenceRequest) -> "RequestSummary":
        """Create summary from full request"""
        return cls(
            request_id=request.request_id,
            project_id=request.project_id,
            user_id=request.user_id,
            request_type=request.request_type,
            status=request.status,
            priority=request.priority,
            created_at=request.created_at,
            started_at=request.started_at,
            completed_at=request.completed_at,
            progress_percentage=request.progress.percentage,
            current_stage=request.progress.current_stage
        ) 