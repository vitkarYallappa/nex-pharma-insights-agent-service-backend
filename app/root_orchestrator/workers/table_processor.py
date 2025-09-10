import asyncio
import signal
import sys
from datetime import datetime
from typing import Optional, Dict, Any

from ..strategies.table_strategy import TableProcessingStrategy
from ..models import MarketIntelligenceRequest, RequestStatus
from ..status_tracker import get_status_tracker
from ..temp_market_intelligence_service import MarketIntelligenceService
from ..temp_logger import get_logger

logger = get_logger(__name__)


class TableProcessor:
    """
    Background processor for table-based market intelligence requests.
    
    This worker polls the database for pending requests and processes them
    using the MarketIntelligenceService. It handles one request at a time
    with configurable polling intervals and error handling.
    """
    
    def __init__(self, strategy, config: Dict[str, Any]):
        """
        Initialize the table processor.
        
        Args:
            strategy: The table processing strategy to use
            config: Processor configuration
        """
        self.strategy = strategy
        self.config = config
        
        # Configuration
        self.polling_interval = config.get("polling_interval", 5.0)
        self.max_processing_time = config.get("max_processing_time", 1800)  # 30 minutes
        self.cleanup_interval = config.get("cleanup_interval", 3600)  # 1 hour
        self.health_check_interval = config.get("health_check_interval", 300)  # 5 minutes
        
        # Services
        self.market_intelligence_service = MarketIntelligenceService()
        self.status_tracker = get_status_tracker()
        
        # State
        self._is_running = False
        self._should_stop = False
        self._current_request: Optional[MarketIntelligenceRequest] = None
        self._last_cleanup = datetime.utcnow()
        self._last_health_check = datetime.utcnow()
        self._processing_task: Optional[asyncio.Task] = None
        
        # Statistics
        self._stats = {
            "requests_processed": 0,
            "requests_completed": 0,
            "requests_failed": 0,
            "total_processing_time": 0.0,
            "started_at": None,
            "last_request_at": None
        }
    
    async def start(self):
        """Start the table processor"""
        if self._is_running:
            logger.warning("Table processor is already running")
            return
        
        logger.info("Starting table processor")
        
        try:
            # Initialize strategy if not already done
            if not self.strategy.is_initialized():
                await self.strategy.initialize()
            
            # Set up signal handlers for graceful shutdown
            self._setup_signal_handlers()
            
            # Start processing
            self._is_running = True
            self._should_stop = False
            self._stats["started_at"] = datetime.utcnow()
            
            logger.info(f"Table processor started with polling interval: {self.polling_interval}s")
            
            # Main processing loop
            await self._processing_loop()
            
        except Exception as e:
            logger.error(f"Table processor startup failed: {e}")
            raise
    
    async def stop(self):
        """Stop the table processor gracefully"""
        if not self._is_running:
            logger.warning("Table processor is not running")
            return
        
        logger.info("Stopping table processor")
        
        # Signal stop
        self._should_stop = True
        
        # Wait for current request to complete (with timeout)
        if self._processing_task and not self._processing_task.done():
            try:
                await asyncio.wait_for(self._processing_task, timeout=30.0)
            except asyncio.TimeoutError:
                logger.warning("Processing task did not complete within timeout, cancelling")
                self._processing_task.cancel()
                try:
                    await self._processing_task
                except asyncio.CancelledError:
                    pass
        
        self._is_running = False
        logger.info("Table processor stopped")
    
    async def _processing_loop(self):
        """Main processing loop"""
        while not self._should_stop:
            try:
                # Check if we can process more requests
                if not self.strategy.can_process_more_requests():
                    logger.debug("Maximum concurrent requests reached, waiting")
                    await asyncio.sleep(self.polling_interval)
                    continue
                
                # Get pending requests
                pending_requests = await self.strategy.get_pending_requests(limit=1)
                
                if pending_requests:
                    request = pending_requests[0]
                    logger.info(f"Processing request: {request.request_id}")
                    
                    # Process the request
                    self._processing_task = asyncio.create_task(
                        self._process_request(request)
                    )
                    
                    try:
                        await self._processing_task
                    except asyncio.CancelledError:
                        logger.warning(f"Processing cancelled for request: {request.request_id}")
                        break
                    except Exception as e:
                        logger.error(f"Processing failed for request {request.request_id}: {e}")
                        await self._handle_processing_error(request, e)
                    
                    self._processing_task = None
                else:
                    # No pending requests, wait before next poll
                    logger.debug("No pending requests found")
                    await asyncio.sleep(self.polling_interval)
                
                # Periodic maintenance tasks
                await self._run_maintenance_tasks()
                
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                await asyncio.sleep(self.polling_interval)
    
    async def _process_request(self, request: MarketIntelligenceRequest):
        """
        Process a single market intelligence request.
        
        Args:
            request: The request to process
        """
        start_time = datetime.utcnow()
        self._current_request = request
        
        try:
            # Add to active requests
            self.strategy.add_active_request(request)
            
            # Update status to PROCESSING
            await self.strategy.update_request_status(
                request.request_id, 
                RequestStatus.PROCESSING, 
                "Started processing"
            )
            
            # Update progress
            await self.strategy.update_request_progress(
                request.request_id,
                "initialization",
                5.0
            )
            
            # Execute the market intelligence workflow
            logger.info(f"Executing market intelligence workflow for: {request.request_id}")
            
            result = await self._execute_with_timeout(
                self.market_intelligence_service.execute_semaglutide_intelligence(request.request_id),
                self.max_processing_time
            )
            
            # Save results
            await self.strategy.save_request_results(request.request_id, result)
            
            # Update status to COMPLETED
            await self.strategy.update_request_status(
                request.request_id,
                RequestStatus.COMPLETED,
                "Processing completed successfully"
            )
            
            # Update final progress
            await self.strategy.update_request_progress(
                request.request_id,
                "completed",
                100.0
            )
            
            # Update statistics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._stats["requests_processed"] += 1
            self._stats["requests_completed"] += 1
            self._stats["total_processing_time"] += processing_time
            self._stats["last_request_at"] = datetime.utcnow()
            
            logger.info(f"Request completed successfully: {request.request_id} (took {processing_time:.1f}s)")
            
        except asyncio.TimeoutError:
            error_msg = f"Processing timeout after {self.max_processing_time}s"
            logger.error(f"Request {request.request_id}: {error_msg}")
            
            await self.strategy.update_request_status(
                request.request_id,
                RequestStatus.FAILED,
                error_msg
            )
            
            self._stats["requests_failed"] += 1
            
        except Exception as e:
            error_msg = f"Processing failed: {str(e)}"
            logger.error(f"Request {request.request_id}: {error_msg}")
            
            await self.strategy.update_request_status(
                request.request_id,
                RequestStatus.FAILED,
                error_msg
            )
            
            self._stats["requests_failed"] += 1
            
        finally:
            # Remove from active requests
            self.strategy.remove_active_request(request.request_id)
            self._current_request = None
    
    async def _execute_with_timeout(self, coro, timeout_seconds: float):
        """
        Execute a coroutine with timeout.
        
        Args:
            coro: The coroutine to execute
            timeout_seconds: Timeout in seconds
            
        Returns:
            The result of the coroutine
            
        Raises:
            asyncio.TimeoutError: If timeout is exceeded
        """
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    
    async def _handle_processing_error(self, request: MarketIntelligenceRequest, error: Exception):
        """
        Handle processing errors.
        
        Args:
            request: The request that failed
            error: The error that occurred
        """
        try:
            # Update request status
            await self.strategy.update_request_status(
                request.request_id,
                RequestStatus.FAILED,
                f"Processing error: {str(error)}"
            )
            
            # Remove from active requests
            self.strategy.remove_active_request(request.request_id)
            
            # Update statistics
            self._stats["requests_failed"] += 1
            
        except Exception as e:
            logger.error(f"Error handling processing error for {request.request_id}: {e}")
    
    async def _run_maintenance_tasks(self):
        """Run periodic maintenance tasks"""
        current_time = datetime.utcnow()
        
        # Cleanup old requests
        if (current_time - self._last_cleanup).total_seconds() >= self.cleanup_interval:
            try:
                cleanup_count = await self.strategy.cleanup_old_requests()
                if cleanup_count > 0:
                    logger.info(f"Cleaned up {cleanup_count} old requests")
                self._last_cleanup = current_time
            except Exception as e:
                logger.error(f"Cleanup task failed: {e}")
        
        # Health check
        if (current_time - self._last_health_check).total_seconds() >= self.health_check_interval:
            try:
                await self._perform_health_check()
                self._last_health_check = current_time
            except Exception as e:
                logger.error(f"Health check failed: {e}")
    
    async def _perform_health_check(self):
        """Perform health check"""
        try:
            # Check strategy health
            strategy_health = self.strategy.get_health_status()
            
            # Check database connectivity
            test_request = await self.strategy.get_request_status("health_check_test")
            
            # Log health status
            logger.debug(f"Health check passed - Strategy: {strategy_health['strategy']}, "
                        f"Active requests: {self.strategy.get_active_request_count()}")
            
        except Exception as e:
            logger.warning(f"Health check detected issues: {e}")
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self.stop())
        
        # Handle SIGINT (Ctrl+C) and SIGTERM
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def get_status(self) -> Dict[str, Any]:
        """Get processor status"""
        current_time = datetime.utcnow()
        uptime = (current_time - self._stats["started_at"]).total_seconds() if self._stats["started_at"] else 0
        
        return {
            "processor": "table",
            "is_running": self._is_running,
            "should_stop": self._should_stop,
            "uptime_seconds": uptime,
            "current_request": self._current_request.request_id if self._current_request else None,
            "active_requests": self.strategy.get_active_request_count(),
            "max_concurrent": self.strategy.max_concurrent_requests,
            "polling_interval": self.polling_interval,
            "statistics": self._stats.copy(),
            "last_cleanup": self._last_cleanup.isoformat(),
            "last_health_check": self._last_health_check.isoformat()
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self._stats.copy()
        
        # Calculate derived statistics
        if stats["requests_processed"] > 0:
            stats["average_processing_time"] = stats["total_processing_time"] / stats["requests_processed"]
            stats["success_rate"] = (stats["requests_completed"] / stats["requests_processed"]) * 100
        else:
            stats["average_processing_time"] = 0.0
            stats["success_rate"] = 0.0
        
        return stats


async def run_table_processor(config: Dict[str, Any]):
    """
    Run the table processor as a standalone process.
    
    Args:
        config: Processor configuration
    """
    logger.info("Starting table processor service")
    
    try:
        # Create strategy
        strategy = TableProcessingStrategy(config.get("table_config", {}))
        
        # Create processor
        processor = TableProcessor(strategy, config.get("processor_config", {}))
        
        # Start processor
        await processor.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down")
    except Exception as e:
        logger.error(f"Table processor service failed: {e}")
        raise
    finally:
        logger.info("Table processor service stopped")


if __name__ == "__main__":
    """Run table processor as standalone script"""
    import json
    
    # Load configuration
    config_file = os.getenv("TABLE_PROCESSOR_CONFIG", "table_processor_config.json")
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        # Default configuration
        config = {
            "table_config": {
                "table_name": "market_intelligence_requests",
                "polling_interval": 5.0,
                "max_concurrent_requests": 1,
                "cleanup_completed_after": 86400,
                "cleanup_failed_after": 172800
            },
            "processor_config": {
                "polling_interval": 5.0,
                "max_processing_time": 1800,
                "cleanup_interval": 3600,
                "health_check_interval": 300
            }
        }
    
    # Run processor
    asyncio.run(run_table_processor(config)) 