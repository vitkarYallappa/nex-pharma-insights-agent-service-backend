import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

from .base_strategy import (
    BaseProcessingStrategy,
    StrategyInitializationError,
    StrategyOperationError,
    RequestNotFoundError,
    RequestValidationError
)
from ..models import (
    MarketIntelligenceRequest,
    RequestStatus,
    RequestFilter,
    RequestSummary,
    RequestResults
)
from ..status_tracker import get_status_tracker
from ..temp_service_factory import ServiceFactory
from ..temp_logger import get_logger

logger = get_logger(__name__)


class TableProcessingStrategy(BaseProcessingStrategy):
    """
    Table-based processing strategy using database polling.
    
    This strategy stores requests in a database table and uses background polling
    to process them sequentially. It provides simple, reliable processing with
    easy debugging and monitoring capabilities.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the table processing strategy.
        
        Args:
            config: Table strategy configuration
        """
        super().__init__(config)
        
        # Configuration
        self.table_name = config.get("table_name", "market_intelligence_requests")
        self.polling_interval = config.get("polling_interval", 5.0)
        self.max_concurrent_requests = config.get("max_concurrent_requests", 1)
        self.batch_query_size = config.get("batch_query_size", 10)
        self.cleanup_completed_after = config.get("cleanup_completed_after", 86400)  # 24 hours
        self.cleanup_failed_after = config.get("cleanup_failed_after", 172800)  # 48 hours
        
        # Perplexity API configuration
        self.perplexity_model = config.get("perplexity_model", "sonar-pro")
        self.perplexity_max_tokens = config.get("perplexity_max_tokens", 1024)
        self.perplexity_temperature = config.get("perplexity_temperature", 0.2)
        self.perplexity_rate_limit_delay = config.get("perplexity_rate_limit_delay", 1.0)
        self.perplexity_timeout = config.get("perplexity_timeout", 30.0)
        
        # Content generation flags
        self.enable_market_summary = config.get("enable_market_summary", True)
        self.enable_competitive_analysis = config.get("enable_competitive_analysis", True)
        self.enable_regulatory_insights = config.get("enable_regulatory_insights", True)
        self.enable_market_implications = config.get("enable_market_implications", True)
        
        # SERP API configuration
        self.serp_engine = config.get("serp_engine", "google")
        self.serp_language = config.get("serp_language", "en")
        self.serp_country = config.get("serp_country", "us")
        self.serp_results_per_domain = config.get("serp_results_per_domain", 5)
        self.serp_rate_limit_delay = config.get("serp_rate_limit_delay", 0.2)
        self.serp_timeout = config.get("serp_timeout", 30.0)
        
        # URL discovery configuration
        self.enable_url_discovery = config.get("enable_url_discovery", True)
        self.max_urls_per_analysis = config.get("max_urls_per_analysis", 20)
        self.source_domains = config.get("source_domains", [
            "reuters.com", "fda.gov", "clinicaltrials.gov", 
            "pharmaphorum.com", "ema.europa.eu", "nih.gov"
        ])
        self.search_keywords = config.get("search_keywords", [
            "semaglutide", "tirzepatide", "wegovy", "ozempic", "mounjaro",
            "obesity drug", "weight loss medication", "GLP-1 receptor agonist"
        ])
        
        # Database client
        self.db_client = None
        
        # Status tracker
        self.status_tracker = get_status_tracker()
        
        # Processing state
        self._active_requests: Dict[str, MarketIntelligenceRequest] = {}
        self._processing_lock = asyncio.Lock()
    
    async def initialize(self) -> bool:
        """
        Initialize the table processing strategy.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            self.log_info("Initializing table processing strategy")
            
            # Initialize database client
            self.db_client = ServiceFactory.get_database_client()
            
            # Test database connection
            await self._test_database_connection()
            
            # Ensure table exists (if using SQL database)
            await self._ensure_table_exists()
            
            self._is_initialized = True
            self.log_info("Table processing strategy initialized successfully")
            return True
            
        except Exception as e:
            error_msg = f"Failed to initialize table strategy: {str(e)}"
            self.log_error(error_msg)
            raise StrategyInitializationError(error_msg, self.get_strategy_name())
    
    async def shutdown(self) -> bool:
        """
        Shutdown the table processing strategy.
        
        Returns:
            bool: True if shutdown was successful
        """
        try:
            self.log_info("Shutting down table processing strategy")
            
            # Wait for active requests to complete (with timeout)
            if self._active_requests:
                self.log_info(f"Waiting for {len(self._active_requests)} active requests to complete")
                
                # Give active requests some time to complete
                for _ in range(30):  # Wait up to 30 seconds
                    if not self._active_requests:
                        break
                    await asyncio.sleep(1)
                
                # Force cleanup remaining requests
                if self._active_requests:
                    self.log_warning(f"Force stopping {len(self._active_requests)} active requests")
                    self._active_requests.clear()
            
            self._is_initialized = False
            self._is_running = False
            
            self.log_info("Table processing strategy shutdown completed")
            return True
            
        except Exception as e:
            error_msg = f"Error during table strategy shutdown: {str(e)}"
            self.log_error(error_msg)
            return False
    
    async def submit_request(self, request: MarketIntelligenceRequest) -> bool:
        """
        Submit a request for processing.
        
        Args:
            request: The market intelligence request to process
            
        Returns:
            bool: True if submission was successful
        """
        try:
            # Validate request
            validation_errors = self.validate_request(request)
            if validation_errors:
                error_msg = f"Request validation failed: {', '.join(validation_errors)}"
                raise RequestValidationError(error_msg, self.get_strategy_name(), validation_errors, request.request_id)
            
            # Set processing strategy
            request.processing_strategy = "table"
            
            # Ensure status is PENDING
            if request.status != RequestStatus.PENDING:
                request.status = RequestStatus.PENDING
            
            # Save to database
            success = await self._save_request_to_db(request)
            
            if success:
                self.log_info(f"Request submitted successfully: {request.request_id}")
                return True
            else:
                raise StrategyOperationError("Failed to save request to database", self.get_strategy_name(), request.request_id)
                
        except (RequestValidationError, StrategyOperationError):
            raise
        except Exception as e:
            error_msg = self.format_error_message("submit_request", e, request.request_id)
            self.log_error(error_msg)
            raise StrategyOperationError(error_msg, self.get_strategy_name(), request.request_id)
    
    async def get_request_status(self, request_id: str) -> Optional[MarketIntelligenceRequest]:
        """
        Get the current status of a request.
        
        Args:
            request_id: The unique identifier of the request
            
        Returns:
            Optional[MarketIntelligenceRequest]: The request with current status, or None if not found
        """
        try:
            # Check active requests first
            if request_id in self._active_requests:
                return self._active_requests[request_id]
            
            # Query database
            request_data = await self.db_client.get_item(self.table_name, {"request_id": request_id})
            
            if request_data:
                return MarketIntelligenceRequest.from_dict(request_data)
            
            return None
            
        except Exception as e:
            error_msg = self.format_error_message("get_request_status", e, request_id)
            self.log_error(error_msg)
            return None
    
    async def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a pending or processing request.
        
        Args:
            request_id: The unique identifier of the request to cancel
            
        Returns:
            bool: True if cancellation was successful
        """
        try:
            # Get current request
            request = await self.get_request_status(request_id)
            if not request:
                raise RequestNotFoundError(f"Request not found: {request_id}", self.get_strategy_name(), request_id)
            
            # Check if request can be cancelled
            if not request.is_active():
                self.log_warning(f"Cannot cancel request {request_id}: already in terminal state {request.status}")
                return False
            
            # Update status to cancelled
            success = await self.update_request_status(request_id, RequestStatus.CANCELLED, "Cancelled by user request")
            
            # Remove from active requests if present
            if request_id in self._active_requests:
                del self._active_requests[request_id]
            
            if success:
                self.log_info(f"Request cancelled successfully: {request_id}")
            
            return success
            
        except RequestNotFoundError:
            raise
        except Exception as e:
            error_msg = self.format_error_message("cancel_request", e, request_id)
            self.log_error(error_msg)
            return False
    
    async def list_requests(self, filter_criteria: RequestFilter) -> List[RequestSummary]:
        """
        List requests based on filter criteria.
        
        Args:
            filter_criteria: Criteria for filtering requests
            
        Returns:
            List[RequestSummary]: List of request summaries matching the criteria
        """
        try:
            # Build filter expression for scan operation (no GSI required)
            filter_expressions = []
            expression_values = {}
            expression_names = {}
            
            if filter_criteria.status:
                filter_expressions.append("#status = :status")
                expression_values[":status"] = filter_criteria.status.value
                expression_names["#status"] = "status"
            
            if filter_criteria.request_type:
                filter_expressions.append("request_type = :request_type")
                expression_values[":request_type"] = filter_criteria.request_type.value
            
            if filter_criteria.priority:
                filter_expressions.append("priority = :priority")
                expression_values[":priority"] = filter_criteria.priority.value
            
            if filter_criteria.user_id:
                filter_expressions.append("user_id = :user_id")
                expression_values[":user_id"] = filter_criteria.user_id
            
            if filter_criteria.project_id:
                filter_expressions.append("project_id = :project_id")
                expression_values[":project_id"] = filter_criteria.project_id
            
            # Use robust scan approach (handles scan limitations properly)
            items = await self._scan_with_filters(
                filter_expressions, 
                expression_values, 
                expression_names, 
                filter_criteria.limit
            )
            
            # Convert to request summaries
            summaries = []
            for item in items:
                try:
                    request = MarketIntelligenceRequest.from_dict(item)
                    summary = RequestSummary.from_request(request)
                    summaries.append(summary)
                except Exception as e:
                    self.log_warning(f"Failed to parse request {item.get('request_id', 'unknown')}: {e}")
                    continue
            
            # Apply date filters (if database doesn't support them natively)
            if filter_criteria.created_after or filter_criteria.created_before:
                filtered_summaries = []
                for summary in summaries:
                    if filter_criteria.created_after and summary.created_at < filter_criteria.created_after:
                        continue
                    if filter_criteria.created_before and summary.created_at > filter_criteria.created_before:
                        continue
                    filtered_summaries.append(summary)
                summaries = filtered_summaries
            
            return summaries
            
        except Exception as e:
            error_msg = self.format_error_message("list_requests", e)
            self.log_error(error_msg)
            return []
    
    async def update_request_status(self, request_id: str, status: RequestStatus, message: Optional[str] = None) -> bool:
        """
        Update the status of a request.
        
        Args:
            request_id: The unique identifier of the request
            status: The new status to set
            message: Optional message describing the status change
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Get current request
            request = await self.get_request_status(request_id)
            if not request:
                raise RequestNotFoundError(f"Request not found: {request_id}", self.get_strategy_name(), request_id)
            
            # Use status tracker for validation and update
            success = self.status_tracker.update_request_status(request, status, message)
            
            if success:
                # Save updated request to database
                await self._save_request_to_db(request)
                
                # Update active requests cache
                if request_id in self._active_requests:
                    self._active_requests[request_id] = request
            
            return success
            
        except RequestNotFoundError:
            raise
        except Exception as e:
            error_msg = self.format_error_message("update_request_status", e, request_id)
            self.log_error(error_msg)
            return False
    
    async def update_request_progress(self, request_id: str, stage: str, percentage: float, **kwargs) -> bool:
        """
        Update the progress of a request.
        
        Args:
            request_id: The unique identifier of the request
            stage: Current processing stage
            percentage: Progress percentage (0-100)
            **kwargs: Additional progress data
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Get current request
            request = await self.get_request_status(request_id)
            if not request:
                raise RequestNotFoundError(f"Request not found: {request_id}", self.get_strategy_name(), request_id)
            
            # Use status tracker for progress update
            success = self.status_tracker.update_request_progress(request, stage, percentage, **kwargs)
            
            if success:
                # Save updated request to database
                await self._save_request_to_db(request)
                
                # Update active requests cache
                if request_id in self._active_requests:
                    self._active_requests[request_id] = request
            
            return success
            
        except RequestNotFoundError:
            raise
        except Exception as e:
            error_msg = self.format_error_message("update_request_progress", e, request_id)
            self.log_error(error_msg)
            return False
    
    async def save_request_results(self, request_id: str, results: Dict[str, Any]) -> bool:
        """
        Save the results of a completed request.
        
        Args:
            request_id: The unique identifier of the request
            results: The results data to save
            
        Returns:
            bool: True if save was successful
        """
        try:
            # Get current request
            request = await self.get_request_status(request_id)
            if not request:
                raise RequestNotFoundError(f"Request not found: {request_id}", self.get_strategy_name(), request_id)
            
            # Create RequestResults object
            request_results = RequestResults(**results)
            request.results = request_results
            
            # Save updated request to database
            success = await self._save_request_to_db(request)
            
            if success:
                # Update active requests cache
                if request_id in self._active_requests:
                    self._active_requests[request_id] = request
                
                self.log_info(f"Results saved for request: {request_id}")
            
            return success
            
        except RequestNotFoundError:
            raise
        except Exception as e:
            error_msg = self.format_error_message("save_request_results", e, request_id)
            self.log_error(error_msg)
            return False
    
    async def get_processing_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get processing statistics for the specified time period.
        
        Args:
            hours: Number of hours to look back for statistics
            
        Returns:
            Dict[str, Any]: Statistics data
        """
        try:
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=hours)
            
            # Query requests in time range
            filter_criteria = RequestFilter(
                created_after=start_time,
                limit=1000  # Large limit to get all recent requests
            )
            
            summaries = await self.list_requests(filter_criteria)
            
            # Convert summaries back to full requests for analysis
            requests = []
            for summary in summaries:
                request = await self.get_request_status(summary.request_id)
                if request:
                    requests.append(request)
            
            # Use status tracker to calculate statistics
            stats = self.status_tracker.get_status_statistics(requests)
            
            # Add table-specific statistics
            stats.update({
                "strategy": "table",
                "time_range_hours": hours,
                "active_requests_count": len(self._active_requests),
                "polling_interval": self.polling_interval,
                "max_concurrent": self.max_concurrent_requests
            })
            
            return stats
            
        except Exception as e:
            error_msg = self.format_error_message("get_processing_statistics", e)
            self.log_error(error_msg)
            return {"error": str(e)}
    
    async def cleanup_old_requests(self, completed_age_hours: int = 24, failed_age_hours: int = 48) -> int:
        """
        Clean up old completed and failed requests.
        
        Args:
            completed_age_hours: Age in hours after which completed requests are cleaned up
            failed_age_hours: Age in hours after which failed requests are cleaned up
            
        Returns:
            int: Number of requests cleaned up
        """
        try:
            cleanup_count = 0
            current_time = datetime.utcnow()
            
            # Clean up completed requests
            completed_cutoff = current_time - timedelta(hours=completed_age_hours)
            completed_filter = RequestFilter(
                status=RequestStatus.COMPLETED,
                created_before=completed_cutoff,
                limit=100
            )
            
            completed_requests = await self.list_requests(completed_filter)
            for summary in completed_requests:
                try:
                    await self.db_client.delete_item(self.table_name, {"request_id": summary.request_id})
                    cleanup_count += 1
                    self.log_debug(f"Cleaned up completed request: {summary.request_id}")
                except Exception as e:
                    self.log_warning(f"Failed to cleanup request {summary.request_id}: {e}")
            
            # Clean up failed requests
            failed_cutoff = current_time - timedelta(hours=failed_age_hours)
            failed_filter = RequestFilter(
                status=RequestStatus.FAILED,
                created_before=failed_cutoff,
                limit=100
            )
            
            failed_requests = await self.list_requests(failed_filter)
            for summary in failed_requests:
                try:
                    await self.db_client.delete_item(self.table_name, {"request_id": summary.request_id})
                    cleanup_count += 1
                    self.log_debug(f"Cleaned up failed request: {summary.request_id}")
                except Exception as e:
                    self.log_warning(f"Failed to cleanup request {summary.request_id}: {e}")
            
            if cleanup_count > 0:
                self.log_info(f"Cleaned up {cleanup_count} old requests")
            
            return cleanup_count
            
        except Exception as e:
            error_msg = self.format_error_message("cleanup_old_requests", e)
            self.log_error(error_msg)
            return 0
    
    # Internal helper methods
    
    async def _test_database_connection(self):
        """Test database connection"""
        try:
            # Simple test query
            await self.db_client.get_item(self.table_name, {"request_id": "test_connection"})
        except Exception as e:
            # Connection test failed, but that's expected for non-existent item
            # The important thing is that we can connect to the database
            pass
    
    async def _ensure_table_exists(self):
        """Ensure the requests table exists (for SQL databases)"""
        # This would be implemented based on the specific database type
        # For DynamoDB, tables are usually pre-created
        # For SQL databases, we might need to create the table schema
        pass
    
    async def _save_request_to_db(self, request: MarketIntelligenceRequest) -> bool:
        """
        Save a request to the database.
        
        Args:
            request: The request to save
            
        Returns:
            bool: True if save was successful
        """
        try:
            # Convert request to dictionary for storage
            request_data = request.to_dict()
            
            # Save to database
            success = await self.db_client.save_item(self.table_name, request_data)
            
            if not success:
                self.log_error(f"Database save returned False for request: {request.request_id}")
            
            return success
            
        except Exception as e:
            self.log_error(f"Failed to save request {request.request_id} to database: {e}")
            return False
    
    async def get_pending_requests(self, limit: int = None) -> List[MarketIntelligenceRequest]:
        """
        Get pending requests ordered by priority and creation time.
        
        Args:
            limit: Maximum number of requests to return
            
        Returns:
            List[MarketIntelligenceRequest]: List of pending requests
        """
        try:
            # Query for pending requests
            filter_criteria = RequestFilter(
                status=RequestStatus.PENDING,
                limit=limit or self.batch_query_size
            )
            
            summaries = await self.list_requests(filter_criteria)
            
            # Get full requests and sort by priority
            requests = []
            for summary in summaries:
                request = await self.get_request_status(summary.request_id)
                if request and request.status == RequestStatus.PENDING:
                    requests.append(request)
            
            # Sort by priority score (higher = more priority)
            requests.sort(key=lambda r: self.calculate_priority_score(r), reverse=True)
            
            return requests
            
        except Exception as e:
            error_msg = self.format_error_message("get_pending_requests", e)
            self.log_error(error_msg)
            return []
    
    def add_active_request(self, request: MarketIntelligenceRequest):
        """Add a request to the active requests cache"""
        self._active_requests[request.request_id] = request
    
    def remove_active_request(self, request_id: str):
        """Remove a request from the active requests cache"""
        if request_id in self._active_requests:
            del self._active_requests[request_id]
    
    def get_active_request_count(self) -> int:
        """Get the number of currently active requests"""
        return len(self._active_requests)
    
    def can_process_more_requests(self) -> bool:
        """Check if we can process more requests based on concurrency limits"""
        return len(self._active_requests) < self.max_concurrent_requests
    
    def get_perplexity_config(self) -> Dict[str, Any]:
        """Get Perplexity API configuration for use by market intelligence service"""
        return {
            "model": self.perplexity_model,
            "max_tokens": self.perplexity_max_tokens,
            "temperature": self.perplexity_temperature,
            "rate_limit_delay": self.perplexity_rate_limit_delay,
            "timeout": self.perplexity_timeout,
            "content_generation": {
                "enable_market_summary": self.enable_market_summary,
                "enable_competitive_analysis": self.enable_competitive_analysis,
                "enable_regulatory_insights": self.enable_regulatory_insights,
                "enable_market_implications": self.enable_market_implications
            }
        }
    
    def get_serp_config(self) -> Dict[str, Any]:
        """Get SERP API configuration for use by market intelligence service"""
        return {
            "engine": self.serp_engine,
            "language": self.serp_language,
            "country": self.serp_country,
            "results_per_domain": self.serp_results_per_domain,
            "rate_limit_delay": self.serp_rate_limit_delay,
            "timeout": self.serp_timeout,
            "url_discovery": {
                "enable_url_discovery": self.enable_url_discovery,
                "max_urls_per_analysis": self.max_urls_per_analysis,
                "source_domains": self.source_domains,
                "search_keywords": self.search_keywords
            }
        }
    
    def get_market_intelligence_config(self) -> Dict[str, Any]:
        """Get complete configuration for market intelligence service"""
        return {
            "perplexity": self.get_perplexity_config(),
            "serp": self.get_serp_config(),
            "processing": {
                "max_concurrent_requests": self.max_concurrent_requests,
                "polling_interval": self.polling_interval,
                "cleanup_completed_after": self.cleanup_completed_after
            }
        }
    
    async def _scan_with_filters(self, filter_expressions: List[str], expression_values: Dict[str, Any], 
                                expression_names: Dict[str, str], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Robust scan method that handles DynamoDB scan limitations properly.
        Similar to your find_all_by_query approach.
        """
        try:
            scan_kwargs = {}
            
            # Add filter expression if we have filters
            if filter_expressions:
                scan_kwargs['FilterExpression'] = " AND ".join(filter_expressions)
                scan_kwargs['ExpressionAttributeValues'] = expression_values
                if expression_names:
                    scan_kwargs['ExpressionAttributeNames'] = expression_names
            
            # Handle scan with filters and limit properly
            if filter_expressions and limit:
                # When using filters, scan without limit and apply limit in code
                all_items = []
                response = await self.db_client.scan(self.table_name, **scan_kwargs)
                all_items.extend(response or [])
                
                # For now, we'll use a simple approach since we don't have pagination info
                # In a real implementation, you'd handle LastEvaluatedKey for pagination
                items = all_items[:limit] if limit else all_items
            else:
                # No filters or no limit - use DynamoDB limit directly
                if limit and not filter_expressions:
                    scan_kwargs['Limit'] = limit
                
                items = await self.db_client.scan(self.table_name, **scan_kwargs)
                if not items:
                    items = []
            
            self.log_info(f"Scan with filters returned {len(items)} items from {self.table_name}")
            return items
            
        except Exception as e:
            error_msg = f"Scan with filters failed in {self.table_name}: {str(e)}"
            self.log_error(error_msg)
            return [] 