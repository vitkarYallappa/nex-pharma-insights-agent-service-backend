from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from ..root_orchestrator.models import (
    RequestStatus, RequestType, Priority, ProcessingStrategy,
    MarketIntelligenceRequestConfig
)


class SubmitRequestSchema(BaseModel):
    """Schema for submitting a new market intelligence request"""
    
    project_id: str = Field(..., description="Project identifier")
    project_request_id: str = Field(..., description="Project identifier")
    user_id: str = Field(..., description="User identifier")
    priority: Priority = Field(default=Priority.MEDIUM, description="Request priority")
    processing_strategy: ProcessingStrategy = Field(
        default=ProcessingStrategy.TABLE, 
        description="Processing strategy to use"
    )
    
    # Configuration options
    config: Optional[MarketIntelligenceRequestConfig] = Field(
        default=None,
        description="Custom configuration for the request"
    )
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata for the request"
    )
    
    @validator('project_id', 'user_id')
    def validate_ids(cls, v):
        if not v or not v.strip():
            raise ValueError("ID cannot be empty")
        return v.strip()
    
    @validator('metadata')
    def validate_metadata(cls, v):
        if v is None:
            return {}
        # Ensure metadata is serializable
        try:
            import json
            json.dumps(v)
        except (TypeError, ValueError):
            raise ValueError("Metadata must be JSON serializable")
        return v


class RequestResponseSchema(BaseModel):
    """Schema for request submission response"""
    
    request_id: str = Field(..., description="Unique request identifier")
    status: RequestStatus = Field(..., description="Current request status")
    message: str = Field(..., description="Response message")
    created_at: datetime = Field(..., description="Request creation timestamp")
    estimated_completion: Optional[datetime] = Field(
        default=None,
        description="Estimated completion time"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RequestStatusSchema(BaseModel):
    """Schema for request status response"""
    
    request_id: str = Field(..., description="Request identifier")
    status: RequestStatus = Field(..., description="Current status")
    request_type: RequestType = Field(..., description="Type of request")
    priority: Priority = Field(..., description="Request priority")
    processing_strategy: ProcessingStrategy = Field(..., description="Processing strategy used")
    
    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    started_at: Optional[datetime] = Field(default=None, description="Processing start time")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    
    # Progress information
    current_stage: Optional[str] = Field(default=None, description="Current processing stage")
    progress_percentage: Optional[float] = Field(default=None, description="Progress percentage (0-100)")
    
    # Additional progress details
    urls_found: Optional[int] = Field(default=None, description="Number of URLs found")
    content_extracted: Optional[int] = Field(default=None, description="Number of content items extracted")
    processing_errors: Optional[int] = Field(default=None, description="Number of processing errors")
    
    # Messages
    status_message: Optional[str] = Field(default=None, description="Current status message")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class RequestResultsSchema(BaseModel):
    """Schema for request results"""
    
    request_id: str = Field(..., description="Request identifier")
    
    # Result files
    report_path: Optional[str] = Field(default=None, description="Path to the main report file")
    raw_data_path: Optional[str] = Field(default=None, description="Path to raw data file")
    
    # Summary information
    summary: Optional[str] = Field(default=None, description="Executive summary")
    total_sources: Optional[int] = Field(default=None, description="Total number of sources processed")
    total_content_items: Optional[int] = Field(default=None, description="Total content items extracted")
    
    # Processing statistics
    processing_duration: Optional[float] = Field(default=None, description="Processing duration in seconds")
    api_calls_made: Optional[int] = Field(default=None, description="Total API calls made")
    success_rate: Optional[float] = Field(default=None, description="Success rate percentage")
    
    # Content breakdown
    content_by_source: Optional[Dict[str, int]] = Field(
        default=None,
        description="Content count by source"
    )
    content_by_type: Optional[Dict[str, int]] = Field(
        default=None,
        description="Content count by type (regulatory, clinical, academic)"
    )
    
    # Quality metrics
    average_confidence: Optional[float] = Field(default=None, description="Average content confidence score")
    high_quality_items: Optional[int] = Field(default=None, description="Number of high-quality items")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class RequestListFilterSchema(BaseModel):
    """Schema for filtering request lists"""
    
    status: Optional[RequestStatus] = Field(default=None, description="Filter by status")
    request_type: Optional[RequestType] = Field(default=None, description="Filter by request type")
    priority: Optional[Priority] = Field(default=None, description="Filter by priority")
    processing_strategy: Optional[ProcessingStrategy] = Field(
        default=None,
        description="Filter by processing strategy"
    )
    
    user_id: Optional[str] = Field(default=None, description="Filter by user ID")
    project_id: Optional[str] = Field(default=None, description="Filter by project ID")
    
    # Date range filters
    created_after: Optional[datetime] = Field(default=None, description="Filter requests created after this date")
    created_before: Optional[datetime] = Field(default=None, description="Filter requests created before this date")
    
    # Pagination
    limit: int = Field(default=50, ge=1, le=1000, description="Maximum number of results")
    offset: int = Field(default=0, ge=0, description="Number of results to skip")
    
    # Sorting
    sort_by: Optional[str] = Field(
        default="created_at",
        description="Field to sort by (created_at, updated_at, priority)"
    )
    sort_order: Optional[str] = Field(
        default="desc",
        description="Sort order (asc, desc)"
    )
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        allowed_fields = ['created_at', 'updated_at', 'priority', 'status']
        if v and v not in allowed_fields:
            raise ValueError(f"sort_by must be one of: {allowed_fields}")
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        if v and v.lower() not in ['asc', 'desc']:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v.lower() if v else v


class RequestSummarySchema(BaseModel):
    """Schema for request summary in list responses"""
    
    request_id: str = Field(..., description="Request identifier")
    status: RequestStatus = Field(..., description="Current status")
    request_type: RequestType = Field(..., description="Request type")
    priority: Priority = Field(..., description="Priority")
    processing_strategy: ProcessingStrategy = Field(..., description="Processing strategy")
    
    user_id: str = Field(..., description="User who submitted the request")
    project_id: str = Field(..., description="Associated project")
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Progress summary
    progress_percentage: Optional[float] = Field(default=None, description="Progress percentage")
    current_stage: Optional[str] = Field(default=None, description="Current stage")
    
    # Quick stats
    processing_duration: Optional[float] = Field(default=None, description="Processing duration in seconds")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RequestListResponseSchema(BaseModel):
    """Schema for paginated request list response"""
    
    requests: List[RequestSummarySchema] = Field(..., description="List of request summaries")
    total_count: int = Field(..., description="Total number of requests matching filter")
    limit: int = Field(..., description="Limit used for this query")
    offset: int = Field(..., description="Offset used for this query")
    has_more: bool = Field(..., description="Whether there are more results available")


class CancelRequestSchema(BaseModel):
    """Schema for request cancellation"""
    
    reason: Optional[str] = Field(default=None, description="Reason for cancellation")


class CancelResponseSchema(BaseModel):
    """Schema for cancellation response"""
    
    request_id: str = Field(..., description="Request identifier")
    cancelled: bool = Field(..., description="Whether cancellation was successful")
    message: str = Field(..., description="Cancellation message")


class ProcessingStatisticsSchema(BaseModel):
    """Schema for processing statistics"""
    
    strategy: str = Field(..., description="Processing strategy name")
    time_range_hours: int = Field(..., description="Time range for statistics")
    
    # Request counts
    total_requests: int = Field(..., description="Total number of requests")
    pending_requests: int = Field(..., description="Number of pending requests")
    processing_requests: int = Field(..., description="Number of processing requests")
    completed_requests: int = Field(..., description="Number of completed requests")
    failed_requests: int = Field(..., description="Number of failed requests")
    cancelled_requests: int = Field(..., description="Number of cancelled requests")
    
    # Performance metrics
    success_rate: float = Field(..., description="Success rate percentage")
    average_processing_time: float = Field(..., description="Average processing time in seconds")
    
    # Current state
    active_requests: int = Field(..., description="Currently active requests")
    max_concurrent: int = Field(..., description="Maximum concurrent requests allowed")
    
    # Additional strategy-specific metrics
    additional_metrics: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional strategy-specific metrics"
    )


class HealthCheckSchema(BaseModel):
    """Schema for health check response"""
    
    status: str = Field(..., description="Overall health status (healthy, degraded, unhealthy)")
    timestamp: datetime = Field(..., description="Health check timestamp")
    
    # Component health
    database: str = Field(..., description="Database health status")
    storage: str = Field(..., description="Storage health status")
    processing_strategy: str = Field(..., description="Processing strategy health")
    
    # System metrics
    uptime_seconds: Optional[float] = Field(default=None, description="System uptime in seconds")
    active_requests: int = Field(..., description="Number of active requests")
    
    # Detailed information
    details: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Detailed health information"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ErrorResponseSchema(BaseModel):
    """Schema for error responses"""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    request_id: Optional[str] = Field(default=None, description="Request ID if applicable")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConfigurationSchema(BaseModel):
    """Schema for system configuration response"""
    
    available_strategies: List[str] = Field(..., description="Available processing strategies")
    default_strategy: str = Field(..., description="Default processing strategy")
    
    # Strategy configurations
    table_config: Optional[Dict[str, Any]] = Field(default=None, description="Table strategy configuration")
    sqs_config: Optional[Dict[str, Any]] = Field(default=None, description="SQS strategy configuration")
    
    # System limits
    max_concurrent_requests: int = Field(..., description="Maximum concurrent requests")
    request_timeout_seconds: int = Field(..., description="Request timeout in seconds")
    
    # Supported request types
    supported_request_types: List[str] = Field(..., description="Supported request types")
    
    # API information
    api_version: str = Field(..., description="API version")
    documentation_url: Optional[str] = Field(default=None, description="API documentation URL")


# Request/Response type unions for OpenAPI documentation
RequestSubmissionResponse = Union[RequestResponseSchema, ErrorResponseSchema]
RequestStatusResponse = Union[RequestStatusSchema, ErrorResponseSchema]
RequestResultsResponse = Union[RequestResultsSchema, ErrorResponseSchema]
RequestListResponse = Union[RequestListResponseSchema, ErrorResponseSchema]
CancellationResponse = Union[CancelResponseSchema, ErrorResponseSchema]
StatisticsResponse = Union[ProcessingStatisticsSchema, ErrorResponseSchema]
HealthResponse = Union[HealthCheckSchema, ErrorResponseSchema]
ConfigurationResponse = Union[ConfigurationSchema, ErrorResponseSchema] 