from datetime import datetime
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response schema."""
    
    success: bool = Field(True, description="Request success status")
    message: str = Field("Operation completed successfully", description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DataResponse(BaseResponse, Generic[T]):
    """Generic data response schema."""
    
    data: Optional[T] = Field(None, description="Response data")


class ListResponse(BaseResponse, Generic[T]):
    """Generic list response schema."""
    
    data: List[T] = Field(default_factory=list, description="List of items")
    total: int = Field(0, description="Total number of items")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Items per page")


class BatchResponse(BaseResponse, Generic[T]):
    """Batch processing response schema for content extraction operations."""
    
    data: List[T] = Field(default_factory=list, description="Processed items")
    total_processed: int = Field(0, description="Total items processed")
    successful: int = Field(0, description="Successfully processed items")
    failed: int = Field(0, description="Failed processing items")
    batch_metadata: dict = Field(default_factory=dict, description="Batch processing metadata")


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginationParams(BaseModel):
    """Pagination parameters schema."""
    
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for pagination."""
        return (self.page - 1) * self.page_size 