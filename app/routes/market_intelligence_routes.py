from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Depends, status
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from ..controllers.market_intelligence_controller import MarketIntelligenceController
from ..schemas.market_intelligence_schema import (
    SubmitRequestSchema,
    RequestResponseSchema,
    RequestStatusSchema,
    RequestResultsSchema,
    RequestListFilterSchema,
    RequestListResponseSchema,
    CancelRequestSchema,
    CancelResponseSchema,
    ProcessingStatisticsSchema,
    HealthCheckSchema,
    ConfigurationSchema,
    ErrorResponseSchema
)
from ..core.exceptions import (
    ValidationError,
    NotFoundError,
    BusinessLogicError,
    ServiceUnavailableError
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/market-intelligence",
    tags=["Market Intelligence"],
    responses={
        500: {"model": ErrorResponseSchema, "description": "Internal Server Error"},
        503: {"model": ErrorResponseSchema, "description": "Service Unavailable"}
    }
)

# Dependency to get controller instance
def get_controller() -> MarketIntelligenceController:
    """Dependency to get market intelligence controller instance"""
    return MarketIntelligenceController()


@router.post(
    "/requests",
    response_model=RequestResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Market Intelligence Request",
    description="Submit a new market intelligence request for processing",
    responses={
        201: {"model": RequestResponseSchema, "description": "Request submitted successfully"},
        400: {"model": ErrorResponseSchema, "description": "Invalid request data"},
        503: {"model": ErrorResponseSchema, "description": "Service unavailable or at capacity"}
    }
)
async def submit_request(
    request_data: SubmitRequestSchema,
    controller: MarketIntelligenceController = Depends(get_controller)
) -> RequestResponseSchema:
    """
    Submit a new market intelligence request.
    
    This endpoint allows users to submit requests for Semaglutide and Tirzepatide
    market intelligence analysis. The request will be processed asynchronously
    using the specified processing strategy.
    
    **Request Parameters:**
    - **project_id**: Identifier for the project this request belongs to
    - **user_id**: Identifier for the user submitting the request
    - **priority**: Request priority (HIGH, MEDIUM, LOW)
    - **processing_strategy**: Strategy to use (TABLE, SQS)
    - **config**: Optional custom configuration for the analysis
    - **metadata**: Optional additional metadata
    
    **Response:**
    Returns the request ID, current status, and estimated completion time.
    """
    try:
        logger.info(f"API: Submitting request for user {request_data.user_id}")
        
        result = await controller.submit_request(request_data)
        
        logger.info(f"API: Request submitted successfully: {result.request_id}")
        return result
        
    except ValidationError as e:
        logger.warning(f"API: Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ValidationError",
                "message": str(e),
                "details": getattr(e, 'details', None)
            }
        )
    except ServiceUnavailableError as e:
        logger.warning(f"API: Service unavailable: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error": "ServiceUnavailable",
                "message": str(e),
                "retry_after": 60  # Suggest retry after 60 seconds
            }
        )
    except BusinessLogicError as e:
        logger.error(f"API: Business logic error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "BusinessLogicError",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"API: Unexpected error submitting request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "An unexpected error occurred"
            }
        )


@router.get(
    "/requests/{request_id}",
    response_model=RequestStatusSchema,
    summary="Get Request Status",
    description="Get the current status and progress of a market intelligence request",
    responses={
        200: {"model": RequestStatusSchema, "description": "Request status retrieved successfully"},
        404: {"model": ErrorResponseSchema, "description": "Request not found"}
    }
)
async def get_request_status(
    request_id: str,
    controller: MarketIntelligenceController = Depends(get_controller)
) -> RequestStatusSchema:
    """
    Get the current status of a market intelligence request.
    
    This endpoint provides detailed information about a request including:
    - Current processing status
    - Progress percentage and current stage
    - Processing timestamps
    - Error messages and warnings
    - Detailed progress metrics (URLs found, content extracted, etc.)
    
    **Path Parameters:**
    - **request_id**: The unique identifier of the request
    
    **Response:**
    Returns comprehensive status information including progress details.
    """
    try:
        logger.debug(f"API: Getting status for request {request_id}")
        
        result = await controller.get_request_status(request_id)
        
        logger.debug(f"API: Status retrieved for request {request_id}: {result.status}")
        return result
        
    except NotFoundError as e:
        logger.warning(f"API: Request not found: {request_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NotFound",
                "message": str(e),
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"API: Error getting request status {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Failed to retrieve request status"
            }
        )


@router.get(
    "/requests/{request_id}/results",
    response_model=RequestResultsSchema,
    summary="Get Request Results",
    description="Get the results of a completed market intelligence request",
    responses={
        200: {"model": RequestResultsSchema, "description": "Request results retrieved successfully"},
        404: {"model": ErrorResponseSchema, "description": "Request not found"},
        400: {"model": ErrorResponseSchema, "description": "Request not completed or results unavailable"}
    }
)
async def get_request_results(
    request_id: str,
    controller: MarketIntelligenceController = Depends(get_controller)
) -> RequestResultsSchema:
    """
    Get the results of a completed market intelligence request.
    
    This endpoint returns the analysis results including:
    - Report and data file paths
    - Executive summary
    - Processing statistics and metrics
    - Content breakdown by source and type
    - Quality metrics and confidence scores
    
    **Path Parameters:**
    - **request_id**: The unique identifier of the completed request
    
    **Response:**
    Returns comprehensive results and analysis data.
    
    **Note:** This endpoint only works for requests with status 'COMPLETED'.
    """
    try:
        logger.debug(f"API: Getting results for request {request_id}")
        
        result = await controller.get_request_results(request_id)
        
        logger.debug(f"API: Results retrieved for request {request_id}")
        return result
        
    except NotFoundError as e:
        logger.warning(f"API: Request not found: {request_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NotFound",
                "message": str(e),
                "request_id": request_id
            }
        )
    except BusinessLogicError as e:
        logger.warning(f"API: Business logic error for results {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "BusinessLogicError",
                "message": str(e),
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"API: Error getting request results {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Failed to retrieve request results"
            }
        )


@router.get(
    "/requests",
    response_model=RequestListResponseSchema,
    summary="List Requests",
    description="List market intelligence requests with filtering and pagination",
    responses={
        200: {"model": RequestListResponseSchema, "description": "Requests retrieved successfully"}
    }
)
async def list_requests(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    processing_strategy: Optional[str] = Query(None, description="Filter by processing strategy"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    sort_by: Optional[str] = Query("created_at", description="Field to sort by"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)"),
    controller: MarketIntelligenceController = Depends(get_controller)
) -> RequestListResponseSchema:
    """
    List market intelligence requests with filtering and pagination.
    
    This endpoint allows you to retrieve a paginated list of requests with
    various filtering options:
    
    **Query Parameters:**
    - **status**: Filter by request status (PENDING, PROCESSING, COMPLETED, FAILED, CANCELLED)
    - **priority**: Filter by priority (HIGH, MEDIUM, LOW)
    - **processing_strategy**: Filter by strategy (TABLE, SQS)
    - **user_id**: Filter by user who submitted the request
    - **project_id**: Filter by project
    - **limit**: Maximum number of results (1-1000, default: 50)
    - **offset**: Number of results to skip (default: 0)
    - **sort_by**: Field to sort by (created_at, updated_at, priority, status)
    - **sort_order**: Sort order (asc, desc, default: desc)
    
    **Response:**
    Returns a paginated list of request summaries with metadata.
    """
    try:
        logger.debug(f"API: Listing requests with filters")
        
        # Create filter schema
        filter_params = RequestListFilterSchema(
            status=status,
            priority=priority,
            processing_strategy=processing_strategy,
            user_id=user_id,
            project_id=project_id,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = await controller.list_requests(filter_params)
        
        logger.debug(f"API: Retrieved {len(result.requests)} requests")
        return result
        
    except ValidationError as e:
        logger.warning(f"API: Validation error in list requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ValidationError",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"API: Error listing requests: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Failed to retrieve requests"
            }
        )


@router.delete(
    "/requests/{request_id}",
    response_model=CancelResponseSchema,
    summary="Cancel Request",
    description="Cancel a pending or processing market intelligence request",
    responses={
        200: {"model": CancelResponseSchema, "description": "Request cancelled successfully"},
        404: {"model": ErrorResponseSchema, "description": "Request not found"},
        400: {"model": ErrorResponseSchema, "description": "Request cannot be cancelled"}
    }
)
async def cancel_request(
    request_id: str,
    cancel_data: CancelRequestSchema = CancelRequestSchema(),
    controller: MarketIntelligenceController = Depends(get_controller)
) -> CancelResponseSchema:
    """
    Cancel a pending or processing market intelligence request.
    
    This endpoint allows you to cancel requests that are in PENDING or PROCESSING
    status. Completed, failed, or already cancelled requests cannot be cancelled.
    
    **Path Parameters:**
    - **request_id**: The unique identifier of the request to cancel
    
    **Request Body:**
    - **reason**: Optional reason for cancellation
    
    **Response:**
    Returns confirmation of cancellation with details.
    
    **Note:** Only active requests (PENDING, PROCESSING) can be cancelled.
    """
    try:
        logger.info(f"API: Cancelling request {request_id}")
        
        result = await controller.cancel_request(request_id, cancel_data)
        
        logger.info(f"API: Request {request_id} cancelled successfully")
        return result
        
    except NotFoundError as e:
        logger.warning(f"API: Request not found for cancellation: {request_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NotFound",
                "message": str(e),
                "request_id": request_id
            }
        )
    except BusinessLogicError as e:
        logger.warning(f"API: Cannot cancel request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "BusinessLogicError",
                "message": str(e),
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"API: Error cancelling request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Failed to cancel request"
            }
        )


@router.get(
    "/statistics",
    response_model=ProcessingStatisticsSchema,
    summary="Get Processing Statistics",
    description="Get processing statistics for the specified time period",
    responses={
        200: {"model": ProcessingStatisticsSchema, "description": "Statistics retrieved successfully"}
    }
)
async def get_processing_statistics(
    hours: int = Query(24, ge=1, le=8760, description="Number of hours to look back (1-8760)"),
    controller: MarketIntelligenceController = Depends(get_controller)
) -> ProcessingStatisticsSchema:
    """
    Get processing statistics for the specified time period.
    
    This endpoint provides comprehensive statistics about request processing
    including success rates, performance metrics, and current system state.
    
    **Query Parameters:**
    - **hours**: Number of hours to look back (1-8760, default: 24)
    
    **Response:**
    Returns detailed processing statistics including:
    - Request counts by status
    - Success rates and performance metrics
    - Current system capacity and load
    - Strategy-specific metrics
    """
    try:
        logger.debug(f"API: Getting processing statistics for {hours} hours")
        
        result = await controller.get_processing_statistics(hours)
        
        logger.debug(f"API: Statistics retrieved for {hours} hours")
        return result
        
    except ValidationError as e:
        logger.warning(f"API: Invalid hours parameter: {hours}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "ValidationError",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"API: Error getting statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Failed to retrieve statistics"
            }
        )


@router.get(
    "/health",
    response_model=HealthCheckSchema,
    summary="Health Check",
    description="Get the health status of the market intelligence system",
    responses={
        200: {"model": HealthCheckSchema, "description": "Health status retrieved successfully"}
    }
)
async def get_health_status(
    controller: MarketIntelligenceController = Depends(get_controller)
) -> HealthCheckSchema:
    """
    Get the health status of the market intelligence system.
    
    This endpoint provides information about the health of various system
    components including database, storage, and processing strategies.
    
    **Response:**
    Returns health status information:
    - Overall system health (healthy, degraded, unhealthy)
    - Individual component health status
    - System uptime and current load
    - Detailed diagnostic information
    
    **Health Status Values:**
    - **healthy**: All components are functioning normally
    - **degraded**: Some components have issues but system is operational
    - **unhealthy**: Critical components are failing
    """
    try:
        logger.debug("API: Performing health check")
        
        result = await controller.get_health_status()
        
        logger.debug(f"API: Health check completed: {result.status}")
        return result
        
    except Exception as e:
        logger.error(f"API: Error during health check: {e}")
        # Return unhealthy status instead of raising error
        return HealthCheckSchema(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            database="unknown",
            storage="unknown",
            processing_strategy="unknown",
            active_requests=0,
            details={"error": str(e)}
        )


@router.get(
    "/config",
    response_model=ConfigurationSchema,
    summary="Get Configuration",
    description="Get system configuration information",
    responses={
        200: {"model": ConfigurationSchema, "description": "Configuration retrieved successfully"}
    }
)
async def get_configuration(
    controller: MarketIntelligenceController = Depends(get_controller)
) -> ConfigurationSchema:
    """
    Get system configuration information.
    
    This endpoint provides information about system configuration including
    available processing strategies, limits, and supported features.
    
    **Response:**
    Returns configuration information:
    - Available processing strategies
    - System limits and timeouts
    - Supported request types
    - API version and documentation links
    """
    try:
        logger.debug("API: Getting system configuration")
        
        result = await controller.get_configuration()
        
        logger.debug("API: Configuration retrieved successfully")
        return result
        
    except Exception as e:
        logger.error(f"API: Error getting configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "Failed to retrieve configuration"
            }
        )


# Note: Exception handlers should be added to the main FastAPI app, not the router
# These can be added in the main application file when including this router


# Add router to main application
def include_routes(app):
    """Include market intelligence routes in the main FastAPI application"""
    app.include_router(router) 