from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from .base_controller import BaseController
from ..root_orchestrator.root_orchestrator_service import RootOrchestratorService
from ..root_orchestrator.models import (
    MarketIntelligenceRequest,
    RequestStatus,
    RequestType,
    Priority,
    ProcessingStrategy,
    RequestFilter,
    MarketIntelligenceRequestConfig
)
from ..schemas.market_intelligence_schema import (
    SubmitRequestSchema,
    RequestResponseSchema,
    RequestStatusSchema,
    RequestResultsSchema,
    RequestListFilterSchema,
    RequestListResponseSchema,
    RequestSummarySchema,
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
from datetime import timedelta

logger = logging.getLogger(__name__)


class MarketIntelligenceController(BaseController):
    """
    Controller for market intelligence request management.
    
    This controller handles the business logic for submitting, tracking,
    and managing market intelligence requests through the Root Orchestrator.
    """
    
    def __init__(self):
        """Initialize the controller"""
        super().__init__()
        self.orchestrator_service = RootOrchestratorService()
        self._startup_time = datetime.utcnow()
    
    async def submit_request(self, request_data: SubmitRequestSchema) -> RequestResponseSchema:
        """
        Submit a new market intelligence request.
        
        Args:
            request_data: The request submission data
            
        Returns:
            RequestResponseSchema: Response with request ID and status
            
        Raises:
            ValidationError: If request data is invalid
            ServiceUnavailableError: If the service is not available
            BusinessLogicError: If business rules are violated
        """
        try:
            logger.info(f"Submitting new market intelligence request for user: {request_data.user_id}")
            
            # Validate business rules
            await self._validate_submission_rules(request_data)
            
            # Create the market intelligence request
            mi_request = MarketIntelligenceRequest(
                project_id=request_data.project_id,
                user_id=request_data.user_id,
                priority=request_data.priority,
                processing_strategy=request_data.processing_strategy,
                config=request_data.config or MarketIntelligenceRequestConfig(),
                processing_metadata=request_data.metadata or {}
            )
            
            # Submit to orchestrator
            success = await self.orchestrator_service.submit_request(mi_request)
            
            if not success:
                raise ServiceUnavailableError("Failed to submit request to orchestrator")
            
            # Estimate completion time
            estimated_completion = await self._estimate_completion_time(mi_request)
            
            logger.info(f"Request submitted successfully: {mi_request.request_id}")
            
            return RequestResponseSchema(
                request_id=mi_request.request_id,
                status=mi_request.status,
                message="Request submitted successfully",
                created_at=mi_request.created_at,
                estimated_completion=estimated_completion
            )
            
        except (ValidationError, ServiceUnavailableError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error submitting request: {e}")
            raise BusinessLogicError(f"Failed to submit request: {str(e)}")
    
    async def get_request_status(self, request_id: str) -> RequestStatusSchema:
        """
        Get the status of a specific request.
        
        Args:
            request_id: The unique identifier of the request
            
        Returns:
            RequestStatusSchema: Current request status and details
            
        Raises:
            NotFoundError: If the request is not found
            BusinessLogicError: If there's an error retrieving status
        """
        try:
            logger.debug(f"Getting status for request: {request_id}")
            
            # Get request from orchestrator
            request = await self.orchestrator_service.get_request_status(request_id)
            
            if not request:
                raise NotFoundError(f"Request not found: {request_id}")
            
            # Convert to response schema
            return self._convert_to_status_schema(request)
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting request status {request_id}: {e}")
            raise BusinessLogicError(f"Failed to get request status: {str(e)}")
    
    async def get_request_results(self, request_id: str) -> RequestResultsSchema:
        """
        Get the results of a completed request.
        
        Args:
            request_id: The unique identifier of the request
            
        Returns:
            RequestResultsSchema: Request results and metadata
            
        Raises:
            NotFoundError: If the request is not found
            BusinessLogicError: If the request is not completed or results unavailable
        """
        try:
            logger.debug(f"Getting results for request: {request_id}")
            
            # Get request from orchestrator
            request = await self.orchestrator_service.get_request_status(request_id)
            
            if not request:
                raise NotFoundError(f"Request not found: {request_id}")
            
            if request.status != RequestStatus.COMPLETED:
                raise BusinessLogicError(f"Request {request_id} is not completed (status: {request.status})")
            
            if not request.results:
                raise BusinessLogicError(f"Results not available for request {request_id}")
            
            # Convert to results schema
            return self._convert_to_results_schema(request)
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Error getting request results {request_id}: {e}")
            raise BusinessLogicError(f"Failed to get request results: {str(e)}")
    
    async def list_requests(self, filter_params: RequestListFilterSchema) -> RequestListResponseSchema:
        """
        List requests with filtering and pagination.
        
        Args:
            filter_params: Filter and pagination parameters
            
        Returns:
            RequestListResponseSchema: Paginated list of requests
            
        Raises:
            ValidationError: If filter parameters are invalid
            BusinessLogicError: If there's an error retrieving requests
        """
        try:
            logger.debug(f"Listing requests with filters: {filter_params.dict()}")
            
            # Convert to internal filter format
            request_filter = RequestFilter(
                status=filter_params.status,
                request_type=filter_params.request_type,
                priority=filter_params.priority,
                user_id=filter_params.user_id,
                project_id=filter_params.project_id,
                created_after=filter_params.created_after,
                created_before=filter_params.created_before,
                limit=filter_params.limit,
                offset=filter_params.offset
            )
            
            # Get requests from orchestrator
            request_summaries = await self.orchestrator_service.list_requests(request_filter)
            
            # Convert to response format
            response_summaries = [
                self._convert_to_summary_schema(summary)
                for summary in request_summaries
            ]
            
            # Apply sorting if specified
            if filter_params.sort_by:
                response_summaries = self._sort_requests(
                    response_summaries,
                    filter_params.sort_by,
                    filter_params.sort_order
                )
            
            # Calculate pagination info
            total_count = len(response_summaries)  # This is simplified - in production, you'd get total from DB
            has_more = (filter_params.offset + len(response_summaries)) < total_count
            
            return RequestListResponseSchema(
                requests=response_summaries,
                total_count=total_count,
                limit=filter_params.limit,
                offset=filter_params.offset,
                has_more=has_more
            )
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error listing requests: {e}")
            raise BusinessLogicError(f"Failed to list requests: {str(e)}")
    
    async def cancel_request(self, request_id: str, cancel_data: CancelRequestSchema) -> CancelResponseSchema:
        """
        Cancel a pending or processing request.
        
        Args:
            request_id: The unique identifier of the request to cancel
            cancel_data: Cancellation details
            
        Returns:
            CancelResponseSchema: Cancellation result
            
        Raises:
            NotFoundError: If the request is not found
            BusinessLogicError: If the request cannot be cancelled
        """
        try:
            logger.info(f"Cancelling request: {request_id}")
            
            # Check if request exists and can be cancelled
            request = await self.orchestrator_service.get_request_status(request_id)
            
            if not request:
                raise NotFoundError(f"Request not found: {request_id}")
            
            if not request.is_active():
                raise BusinessLogicError(f"Request {request_id} cannot be cancelled (status: {request.status})")
            
            # Cancel the request
            success = await self.orchestrator_service.cancel_request(request_id)
            
            if success:
                message = f"Request cancelled successfully"
                if cancel_data.reason:
                    message += f": {cancel_data.reason}"
                
                logger.info(f"Request {request_id} cancelled successfully")
                
                return CancelResponseSchema(
                    request_id=request_id,
                    cancelled=True,
                    message=message
                )
            else:
                raise BusinessLogicError(f"Failed to cancel request {request_id}")
            
        except (NotFoundError, BusinessLogicError):
            raise
        except Exception as e:
            logger.error(f"Error cancelling request {request_id}: {e}")
            raise BusinessLogicError(f"Failed to cancel request: {str(e)}")
    
    async def get_processing_statistics(self, hours: int = 24) -> ProcessingStatisticsSchema:
        """
        Get processing statistics for the specified time period.
        
        Args:
            hours: Number of hours to look back for statistics
            
        Returns:
            ProcessingStatisticsSchema: Processing statistics
            
        Raises:
            ValidationError: If hours parameter is invalid
            BusinessLogicError: If there's an error retrieving statistics
        """
        try:
            if hours <= 0 or hours > 8760:  # Max 1 year
                raise ValidationError("Hours must be between 1 and 8760")
            
            logger.debug(f"Getting processing statistics for last {hours} hours")
            
            # Get statistics from orchestrator
            stats = await self.orchestrator_service.get_processing_statistics(hours)
            
            # Convert to response schema
            return ProcessingStatisticsSchema(
                strategy=stats.get("strategy", "unknown"),
                time_range_hours=hours,
                total_requests=stats.get("total_requests", 0),
                pending_requests=stats.get("pending_requests", 0),
                processing_requests=stats.get("processing_requests", 0),
                completed_requests=stats.get("completed_requests", 0),
                failed_requests=stats.get("failed_requests", 0),
                cancelled_requests=stats.get("cancelled_requests", 0),
                success_rate=stats.get("success_rate", 0.0),
                average_processing_time=stats.get("average_processing_time", 0.0),
                active_requests=stats.get("active_requests_count", 0),
                max_concurrent=stats.get("max_concurrent", 1),
                additional_metrics=stats.get("additional_metrics", {})
            )
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Error getting processing statistics: {e}")
            raise BusinessLogicError(f"Failed to get processing statistics: {str(e)}")
    
    async def get_health_status(self) -> HealthCheckSchema:
        """
        Get the health status of the market intelligence system.
        
        Returns:
            HealthCheckSchema: System health information
            
        Raises:
            BusinessLogicError: If there's an error checking health
        """
        try:
            logger.debug("Performing health check")
            
            # Check orchestrator health
            orchestrator_health = await self.orchestrator_service.get_health_status()
            
            # Determine overall health status
            overall_status = self._determine_overall_health(orchestrator_health)
            
            # Calculate uptime
            uptime = (datetime.utcnow() - self._startup_time).total_seconds()
            
            return HealthCheckSchema(
                status=overall_status,
                timestamp=datetime.utcnow(),
                database=orchestrator_health.get("database", "unknown"),
                storage=orchestrator_health.get("storage", "unknown"),
                processing_strategy=orchestrator_health.get("strategy", "unknown"),
                uptime_seconds=uptime,
                active_requests=orchestrator_health.get("active_requests", 0),
                details=orchestrator_health
            )
            
        except Exception as e:
            logger.error(f"Error performing health check: {e}")
            # Return degraded status instead of raising error
            return HealthCheckSchema(
                status="unhealthy",
                timestamp=datetime.utcnow(),
                database="unknown",
                storage="unknown",
                processing_strategy="unknown",
                uptime_seconds=(datetime.utcnow() - self._startup_time).total_seconds(),
                active_requests=0,
                details={"error": str(e)}
            )
    
    async def get_configuration(self) -> ConfigurationSchema:
        """
        Get system configuration information.
        
        Returns:
            ConfigurationSchema: System configuration
            
        Raises:
            BusinessLogicError: If there's an error retrieving configuration
        """
        try:
            logger.debug("Getting system configuration")
            
            # Get configuration from orchestrator
            config = await self.orchestrator_service.get_configuration()
            
            return ConfigurationSchema(
                available_strategies=config.get("available_strategies", ["table"]),
                default_strategy=config.get("default_strategy", "table"),
                table_config=config.get("table_config"),
                sqs_config=config.get("sqs_config"),
                max_concurrent_requests=config.get("max_concurrent_requests", 1),
                request_timeout_seconds=config.get("request_timeout_seconds", 1800),
                supported_request_types=["semaglutide_intelligence"],
                api_version="1.0.0",
                documentation_url="/docs"
            )
            
        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            raise BusinessLogicError(f"Failed to get configuration: {str(e)}")
    
    # Private helper methods
    
    async def _validate_submission_rules(self, request_data: SubmitRequestSchema):
        """Validate business rules for request submission"""
        
        # Check if user has permission (simplified - in production, check auth)
        if not request_data.user_id:
            raise ValidationError("User ID is required")
        
        # Check if project exists (simplified - in production, validate against project service)
        if not request_data.project_id:
            raise ValidationError("Project ID is required")
        
        # Validate processing strategy availability
        config = await self.orchestrator_service.get_configuration()
        available_strategies = config.get("available_strategies", ["table"])
        
        if request_data.processing_strategy.value not in available_strategies:
            raise ValidationError(f"Processing strategy '{request_data.processing_strategy}' is not available")
        
        # Check system capacity (simplified)
        stats = await self.orchestrator_service.get_processing_statistics(1)
        active_requests = stats.get("active_requests_count", 0)
        max_concurrent = stats.get("max_concurrent", 1)
        
        if active_requests >= max_concurrent:
            raise ServiceUnavailableError("System is at maximum capacity, please try again later")
    
    async def _estimate_completion_time(self, request: MarketIntelligenceRequest) -> Optional[datetime]:
        """Estimate completion time for a request"""
        try:
            # Get average processing time from statistics
            stats = await self.orchestrator_service.get_processing_statistics(24)
            avg_time = stats.get("average_processing_time", 1800)  # Default 30 minutes
            
            # Add some buffer and queue time
            estimated_seconds = avg_time * 1.2 + 300  # 20% buffer + 5 min queue time
            
            return datetime.utcnow().replace(microsecond=0) + timedelta(seconds=estimated_seconds)
            
        except Exception:
            # If estimation fails, return None
            return None
    
    def _convert_to_status_schema(self, request: MarketIntelligenceRequest) -> RequestStatusSchema:
        """Convert MarketIntelligenceRequest to RequestStatusSchema"""
        
        progress = request.progress
        
        return RequestStatusSchema(
            request_id=request.request_id,
            status=request.status,
            request_type=request.request_type,
            priority=request.priority,
            processing_strategy=request.processing_strategy,
            created_at=request.created_at,
            updated_at=request.updated_at,
            started_at=request.started_at,
            completed_at=request.completed_at,
            current_stage=progress.current_stage if progress else None,
            progress_percentage=progress.percentage if progress else None,
            urls_found=progress.urls_found if progress else None,
            content_extracted=progress.content_extracted if progress else None,
            processing_errors=progress.processing_errors if progress else None,
            status_message=request.status_message,
            errors=request.errors,
            warnings=request.warnings
        )
    
    def _convert_to_results_schema(self, request: MarketIntelligenceRequest) -> RequestResultsSchema:
        """Convert MarketIntelligenceRequest to RequestResultsSchema"""
        
        results = request.results
        
        return RequestResultsSchema(
            request_id=request.request_id,
            report_path=results.report_path if results else None,
            raw_data_path=results.raw_data_path if results else None,
            summary=results.summary if results else None,
            total_sources=results.total_sources if results else None,
            total_content_items=results.total_content_items if results else None,
            processing_duration=request.get_processing_duration(),
            api_calls_made=results.api_calls_made if results else None,
            success_rate=results.get_success_rate() if results else None,
            content_by_source=results.content_by_source if results else None,
            content_by_type=results.get_content_count_by_type() if results else None,
            average_confidence=results.average_confidence if results else None,
            high_quality_items=results.high_quality_items if results else None
        )
    
    def _convert_to_summary_schema(self, summary) -> RequestSummarySchema:
        """Convert RequestSummary to RequestSummarySchema"""
        
        return RequestSummarySchema(
            request_id=summary.request_id,
            status=summary.status,
            request_type=summary.request_type,
            priority=summary.priority,
            processing_strategy=summary.processing_strategy,
            user_id=summary.user_id,
            project_id=summary.project_id,
            created_at=summary.created_at,
            updated_at=summary.updated_at,
            progress_percentage=summary.progress_percentage,
            current_stage=summary.current_stage,
            processing_duration=summary.processing_duration
        )
    
    def _sort_requests(self, requests: List[RequestSummarySchema], sort_by: str, sort_order: str) -> List[RequestSummarySchema]:
        """Sort requests by specified field and order"""
        
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "created_at":
            return sorted(requests, key=lambda r: r.created_at, reverse=reverse)
        elif sort_by == "updated_at":
            return sorted(requests, key=lambda r: r.updated_at, reverse=reverse)
        elif sort_by == "priority":
            # Priority sorting: HIGH > MEDIUM > LOW
            priority_order = {"high": 3, "medium": 2, "low": 1}
            return sorted(requests, key=lambda r: priority_order.get(r.priority.value.lower(), 0), reverse=reverse)
        elif sort_by == "status":
            return sorted(requests, key=lambda r: r.status.value, reverse=reverse)
        else:
            return requests
    
    def _determine_overall_health(self, orchestrator_health: Dict[str, Any]) -> str:
        """Determine overall health status from component health"""
        
        component_statuses = [
            orchestrator_health.get("database", "unknown"),
            orchestrator_health.get("storage", "unknown"),
            orchestrator_health.get("strategy", "unknown")
        ]
        
        if all(status == "healthy" for status in component_statuses):
            return "healthy"
        elif any(status == "unhealthy" for status in component_statuses):
            return "unhealthy"
        else:
            return "degraded" 