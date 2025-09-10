import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from .config import get_config, RootOrchestratorConfig
from .models import (
    MarketIntelligenceRequest,
    RequestStatus,
    RequestFilter,
    RequestSummary,
    ProcessingStrategy
)
from .strategies.base_strategy import (
    BaseProcessingStrategy,
    StrategyError,
    StrategyInitializationError,
    RequestNotFoundError
)
from .strategies.table_strategy import TableProcessingStrategy
from .status_tracker import get_status_tracker
from .workers.table_processor import TableProcessor
from .temp_logger import get_logger

logger = get_logger(__name__)


class RootOrchestratorService:
    """
    Root Orchestrator Service
    
    This is the main service that coordinates market intelligence request processing
    using different strategies (table-based, SQS-based). It provides a unified
    interface for submitting, tracking, and managing requests.
    """
    
    def __init__(self, config: Optional[RootOrchestratorConfig] = None):
        """
        Initialize the Root Orchestrator Service.
        
        Args:
            config: Optional configuration. If None, loads from environment.
        """
        self.config = config or get_config()
        self.status_tracker = get_status_tracker()
        
        # Processing strategies
        self._strategies: Dict[str, BaseProcessingStrategy] = {}
        self._current_strategy: Optional[BaseProcessingStrategy] = None
        
        # Background workers
        self._workers: Dict[str, Any] = {}
        
        # Service state
        self._is_initialized = False
        self._is_running = False
        self._startup_time = datetime.utcnow()
        
        logger.info(f"Root Orchestrator Service created with strategy: {self.config.default_strategy}")
    
    async def initialize(self) -> bool:
        """
        Initialize the Root Orchestrator Service.
        
        Returns:
            bool: True if initialization was successful
        """
        if self._is_initialized:
            logger.warning("Root Orchestrator Service is already initialized")
            return True
        
        try:
            logger.info("Initializing Root Orchestrator Service")
            
            # Initialize strategies
            await self._initialize_strategies()
            
            # Set current strategy
            await self._set_current_strategy(self.config.default_strategy)
            
            # Start background workers if needed
            await self._start_workers()
            
            self._is_initialized = True
            self._is_running = True
            
            logger.info("Root Orchestrator Service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Root Orchestrator Service: {e}")
            raise StrategyInitializationError(f"Service initialization failed: {str(e)}", "root_orchestrator")
    
    async def shutdown(self) -> bool:
        """
        Shutdown the Root Orchestrator Service.
        
        Returns:
            bool: True if shutdown was successful
        """
        if not self._is_initialized:
            logger.warning("Root Orchestrator Service is not initialized")
            return True
        
        try:
            logger.info("Shutting down Root Orchestrator Service")
            
            # Stop background workers
            await self._stop_workers()
            
            # Shutdown strategies
            await self._shutdown_strategies()
            
            self._is_initialized = False
            self._is_running = False
            
            logger.info("Root Orchestrator Service shutdown completed")
            return True
            
        except Exception as e:
            logger.error(f"Error during Root Orchestrator Service shutdown: {e}")
            return False
    
    async def submit_request(self, request: MarketIntelligenceRequest) -> bool:
        """
        Submit a market intelligence request for processing.
        
        Args:
            request: The market intelligence request to process
            
        Returns:
            bool: True if submission was successful
            
        Raises:
            StrategyError: If there's an error with the processing strategy
        """
        try:
            logger.info(f"RootOrchestrator: Starting submit_request for {request.request_id}")
            
            if not self._is_initialized:
                logger.info(f"RootOrchestrator: Initializing service for {request.request_id}")
                await self.initialize()
            
            logger.info(f"RootOrchestrator: Service initialized, submitting request: {request.request_id}")
            
            # Get the appropriate strategy
            logger.info(f"RootOrchestrator: Getting strategy for request: {request.request_id}")
            strategy = await self._get_strategy_for_request(request)
            logger.info(f"RootOrchestrator: Got strategy {type(strategy).__name__} for request: {request.request_id}")
            
            # Submit to strategy
            logger.info(f"RootOrchestrator: Calling strategy.submit_request for: {request.request_id}")
            success = await strategy.submit_request(request)
            logger.info(f"RootOrchestrator: Strategy submit_request returned {success} for: {request.request_id}")
            
            if success:
                logger.info(f"Request submitted successfully: {request.request_id}")
            else:
                logger.error(f"Failed to submit request: {request.request_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error submitting request {request.request_id}: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise StrategyError(f"Failed to submit request: {str(e)}", "root_orchestrator", request.request_id)
    
    async def get_request_status(self, request_id: str) -> Optional[MarketIntelligenceRequest]:
        """
        Get the status of a specific request.
        
        Args:
            request_id: The unique identifier of the request
            
        Returns:
            Optional[MarketIntelligenceRequest]: The request with current status, or None if not found
        """
        try:
            if not self._is_initialized:
                await self.initialize()
            
            logger.debug(f"Getting status for request: {request_id}")
            
            # Try current strategy first
            if self._current_strategy:
                request = await self._current_strategy.get_request_status(request_id)
                if request:
                    return request
            
            # Try all other strategies if not found in current strategy
            for strategy_name, strategy in self._strategies.items():
                if strategy != self._current_strategy:
                    request = await strategy.get_request_status(request_id)
                    if request:
                        return request
            
            logger.debug(f"Request not found: {request_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting request status {request_id}: {e}")
            return None
    
    async def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a pending or processing request.
        
        Args:
            request_id: The unique identifier of the request to cancel
            
        Returns:
            bool: True if cancellation was successful
            
        Raises:
            RequestNotFoundError: If the request is not found
        """
        try:
            if not self._is_initialized:
                await self.initialize()
            
            logger.info(f"Cancelling request: {request_id}")
            
            # Find the request in any strategy
            request = await self.get_request_status(request_id)
            if not request:
                raise RequestNotFoundError(f"Request not found: {request_id}", "root_orchestrator", request_id)
            
            # Get the strategy that has this request
            strategy = await self._get_strategy_by_name(request.processing_strategy.value)
            
            # Cancel the request
            success = await strategy.cancel_request(request_id)
            
            if success:
                logger.info(f"Request cancelled successfully: {request_id}")
            
            return success
            
        except RequestNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error cancelling request {request_id}: {e}")
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
            if not self._is_initialized:
                await self.initialize()
            
            logger.debug("Listing requests with filters")
            
            all_summaries = []
            
            # Get requests from all strategies
            for strategy_name, strategy in self._strategies.items():
                try:
                    summaries = await strategy.list_requests(filter_criteria)
                    all_summaries.extend(summaries)
                except Exception as e:
                    logger.warning(f"Error getting requests from strategy {strategy_name}: {e}")
                    continue
            
            # Remove duplicates (shouldn't happen, but just in case)
            seen_ids = set()
            unique_summaries = []
            for summary in all_summaries:
                if summary.request_id not in seen_ids:
                    unique_summaries.append(summary)
                    seen_ids.add(summary.request_id)
            
            logger.debug(f"Retrieved {len(unique_summaries)} unique requests")
            return unique_summaries
            
        except Exception as e:
            logger.error(f"Error listing requests: {e}")
            return []
    
    async def get_processing_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get processing statistics for the specified time period.
        
        Args:
            hours: Number of hours to look back for statistics
            
        Returns:
            Dict[str, Any]: Aggregated statistics from all strategies
        """
        try:
            if not self._is_initialized:
                await self.initialize()
            
            logger.debug(f"Getting processing statistics for {hours} hours")
            
            # Get statistics from current strategy
            if self._current_strategy:
                stats = await self._current_strategy.get_processing_statistics(hours)
                
                # Add root orchestrator specific metrics
                stats.update({
                    "orchestrator_uptime": (datetime.utcnow() - self._startup_time).total_seconds(),
                    "available_strategies": list(self._strategies.keys()),
                    "current_strategy": self._current_strategy.get_strategy_name(),
                    "workers_running": len([w for w in self._workers.values() if getattr(w, '_is_running', False)])
                })
                
                return stats
            else:
                return {
                    "error": "No active strategy",
                    "available_strategies": list(self._strategies.keys())
                }
                
        except Exception as e:
            logger.error(f"Error getting processing statistics: {e}")
            return {"error": str(e)}
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of the Root Orchestrator and its components.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        try:
            health_info = {
                "orchestrator": "healthy" if self._is_running else "unhealthy",
                "initialized": self._is_initialized,
                "uptime": (datetime.utcnow() - self._startup_time).total_seconds(),
                "strategies": {},
                "workers": {},
                "current_strategy": self._current_strategy.get_strategy_name() if self._current_strategy else None
            }
            
            # Check strategy health
            for strategy_name, strategy in self._strategies.items():
                try:
                    strategy_health = strategy.get_health_status()
                    health_info["strategies"][strategy_name] = strategy_health
                except Exception as e:
                    health_info["strategies"][strategy_name] = {"status": "unhealthy", "error": str(e)}
            
            # Check worker health
            for worker_name, worker in self._workers.items():
                try:
                    if hasattr(worker, 'get_status'):
                        worker_status = worker.get_status()
                        health_info["workers"][worker_name] = worker_status
                    else:
                        health_info["workers"][worker_name] = {"status": "unknown"}
                except Exception as e:
                    health_info["workers"][worker_name] = {"status": "unhealthy", "error": str(e)}
            
            # Determine overall health
            if self._is_running and self._current_strategy:
                current_strategy_health = health_info["strategies"].get(
                    self._current_strategy.get_strategy_name(), {}
                ).get("status", "unknown")
                
                if current_strategy_health == "healthy":
                    health_info["status"] = "healthy"
                elif current_strategy_health == "degraded":
                    health_info["status"] = "degraded"
                else:
                    health_info["status"] = "unhealthy"
            else:
                health_info["status"] = "unhealthy"
            
            return health_info
            
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_configuration(self) -> Dict[str, Any]:
        """
        Get system configuration information.
        
        Returns:
            Dict[str, Any]: Configuration information
        """
        try:
            config_info = {
                "available_strategies": list(self._strategies.keys()),
                "default_strategy": self.config.default_strategy.value,
                "current_strategy": self._current_strategy.get_strategy_name() if self._current_strategy else None,
                "environment": self.config.environment.value,
                "debug": self.config.debug
            }
            
            # Add strategy-specific configurations
            if self.config.table_config:
                config_info["table_config"] = {
                    "polling_interval": self.config.table_config.polling_interval,
                    "max_concurrent_requests": self.config.table_config.max_concurrent_requests,
                    "table_name": self.config.table_config.table_name
                }
            
            if self.config.sqs_config and self.config.is_sqs_enabled():
                config_info["sqs_config"] = {
                    "max_workers": self.config.sqs_config.max_workers,
                    "visibility_timeout": self.config.sqs_config.visibility_timeout,
                    "aws_region": self.config.sqs_config.aws_region
                }
            
            return config_info
            
        except Exception as e:
            logger.error(f"Error getting configuration: {e}")
            return {"error": str(e)}
    
    async def switch_strategy(self, strategy_name: str) -> bool:
        """
        Switch to a different processing strategy.
        
        Args:
            strategy_name: Name of the strategy to switch to
            
        Returns:
            bool: True if switch was successful
        """
        try:
            logger.info(f"Switching to strategy: {strategy_name}")
            
            # Validate strategy exists
            if strategy_name not in self._strategies:
                logger.error(f"Strategy not found: {strategy_name}")
                return False
            
            # Stop current workers
            await self._stop_workers()
            
            # Switch strategy
            await self._set_current_strategy(strategy_name)
            
            # Start new workers
            await self._start_workers()
            
            logger.info(f"Successfully switched to strategy: {strategy_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error switching strategy to {strategy_name}: {e}")
            return False
    
    # Private helper methods
    
    async def _initialize_strategies(self):
        """Initialize all available processing strategies"""
        
        # Initialize table strategy
        table_config = self.config.get_strategy_config("table")
        table_strategy = TableProcessingStrategy(table_config)
        await table_strategy.initialize()
        self._strategies["table"] = table_strategy
        
        # TODO: Initialize SQS strategy when implemented
        # if self.config.is_sqs_enabled():
        #     sqs_config = self.config.get_strategy_config("sqs")
        #     sqs_strategy = SQSProcessingStrategy(sqs_config)
        #     await sqs_strategy.initialize()
        #     self._strategies["sqs"] = sqs_strategy
        
        logger.info(f"Initialized {len(self._strategies)} strategies: {list(self._strategies.keys())}")
    
    async def _shutdown_strategies(self):
        """Shutdown all processing strategies"""
        for strategy_name, strategy in self._strategies.items():
            try:
                await strategy.shutdown()
                logger.info(f"Strategy {strategy_name} shutdown successfully")
            except Exception as e:
                logger.error(f"Error shutting down strategy {strategy_name}: {e}")
        
        self._strategies.clear()
        self._current_strategy = None
    
    async def _set_current_strategy(self, strategy_name: str):
        """Set the current active strategy"""
        if strategy_name not in self._strategies:
            raise StrategyError(f"Strategy not found: {strategy_name}", "root_orchestrator")
        
        self._current_strategy = self._strategies[strategy_name]
        logger.info(f"Current strategy set to: {strategy_name}")
    
    async def _get_strategy_for_request(self, request: MarketIntelligenceRequest) -> BaseProcessingStrategy:
        """Get the appropriate strategy for a request"""
        strategy_name = request.processing_strategy.value
        
        if strategy_name not in self._strategies:
            # Fall back to current strategy
            logger.warning(f"Requested strategy {strategy_name} not available, using current strategy")
            return self._current_strategy
        
        return self._strategies[strategy_name]
    
    async def _get_strategy_by_name(self, strategy_name: str) -> BaseProcessingStrategy:
        """Get strategy by name"""
        if strategy_name not in self._strategies:
            raise StrategyError(f"Strategy not found: {strategy_name}", "root_orchestrator")
        
        return self._strategies[strategy_name]
    
    async def _start_workers(self):
        """Start background workers for current strategy"""
        if not self._current_strategy:
            return
        
        strategy_name = self._current_strategy.get_strategy_name()
        
        if strategy_name == "table":
            # Start table processor
            processor_config = self.config.get_strategy_config("table")
            table_processor = TableProcessor(self._current_strategy, processor_config)
            
            # Start processor in background
            processor_task = asyncio.create_task(table_processor.start())
            self._workers["table_processor"] = {
                "processor": table_processor,
                "task": processor_task
            }
            
            logger.info("Table processor started")
        
        # TODO: Start SQS workers when implemented
    
    async def _stop_workers(self):
        """Stop all background workers"""
        for worker_name, worker_info in self._workers.items():
            try:
                if "processor" in worker_info:
                    await worker_info["processor"].stop()
                
                if "task" in worker_info and not worker_info["task"].done():
                    worker_info["task"].cancel()
                    try:
                        await worker_info["task"]
                    except asyncio.CancelledError:
                        pass
                
                logger.info(f"Worker {worker_name} stopped")
                
            except Exception as e:
                logger.error(f"Error stopping worker {worker_name}: {e}")
        
        self._workers.clear()
    
    # Context manager support
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.shutdown()


# Global service instance
_orchestrator_service: Optional[RootOrchestratorService] = None


def get_orchestrator_service() -> RootOrchestratorService:
    """
    Get the global Root Orchestrator Service instance.
    
    Returns:
        RootOrchestratorService: The global service instance
    """
    global _orchestrator_service
    
    if _orchestrator_service is None:
        _orchestrator_service = RootOrchestratorService()
    
    return _orchestrator_service


def set_orchestrator_service(service: RootOrchestratorService):
    """
    Set the global Root Orchestrator Service instance.
    
    Args:
        service: The service instance to set as global
    """
    global _orchestrator_service
    _orchestrator_service = service


async def initialize_orchestrator_service(config: Optional[RootOrchestratorConfig] = None) -> RootOrchestratorService:
    """
    Initialize and return the global Root Orchestrator Service.
    
    Args:
        config: Optional configuration
        
    Returns:
        RootOrchestratorService: The initialized service instance
    """
    service = RootOrchestratorService(config)
    await service.initialize()
    set_orchestrator_service(service)
    return service 