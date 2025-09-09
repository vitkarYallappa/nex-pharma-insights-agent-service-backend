from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

from ..models import (
    MarketIntelligenceRequest,
    RequestStatus,
    RequestFilter,
    RequestSummary
)


class BaseProcessingStrategy(ABC):
    """
    Abstract base class for processing strategies.
    
    This class defines the interface that all processing strategies must implement.
    It provides common functionality and enforces the contract for request handling.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the processing strategy.
        
        Args:
            config: Strategy-specific configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._is_initialized = False
        self._is_running = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the processing strategy.
        
        This method should set up any required resources, connections, or workers.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def shutdown(self) -> bool:
        """
        Shutdown the processing strategy.
        
        This method should clean up resources, close connections, and stop workers.
        
        Returns:
            bool: True if shutdown was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def submit_request(self, request: MarketIntelligenceRequest) -> bool:
        """
        Submit a request for processing.
        
        Args:
            request: The market intelligence request to process
            
        Returns:
            bool: True if submission was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_request_status(self, request_id: str) -> Optional[MarketIntelligenceRequest]:
        """
        Get the current status of a request.
        
        Args:
            request_id: The unique identifier of the request
            
        Returns:
            Optional[MarketIntelligenceRequest]: The request with current status, or None if not found
        """
        pass
    
    @abstractmethod
    async def cancel_request(self, request_id: str) -> bool:
        """
        Cancel a pending or processing request.
        
        Args:
            request_id: The unique identifier of the request to cancel
            
        Returns:
            bool: True if cancellation was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_requests(self, filter_criteria: RequestFilter) -> List[RequestSummary]:
        """
        List requests based on filter criteria.
        
        Args:
            filter_criteria: Criteria for filtering requests
            
        Returns:
            List[RequestSummary]: List of request summaries matching the criteria
        """
        pass
    
    @abstractmethod
    async def update_request_status(self, request_id: str, status: RequestStatus, message: Optional[str] = None) -> bool:
        """
        Update the status of a request.
        
        Args:
            request_id: The unique identifier of the request
            status: The new status to set
            message: Optional message describing the status change
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def update_request_progress(self, request_id: str, stage: str, percentage: float, **kwargs) -> bool:
        """
        Update the progress of a request.
        
        Args:
            request_id: The unique identifier of the request
            stage: Current processing stage
            percentage: Progress percentage (0-100)
            **kwargs: Additional progress data (urls_found, content_extracted, etc.)
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def save_request_results(self, request_id: str, results: Dict[str, Any]) -> bool:
        """
        Save the results of a completed request.
        
        Args:
            request_id: The unique identifier of the request
            results: The results data to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_processing_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get processing statistics for the specified time period.
        
        Args:
            hours: Number of hours to look back for statistics
            
        Returns:
            Dict[str, Any]: Statistics data including counts, rates, and performance metrics
        """
        pass
    
    @abstractmethod
    async def cleanup_old_requests(self, completed_age_hours: int = 24, failed_age_hours: int = 48) -> int:
        """
        Clean up old completed and failed requests.
        
        Args:
            completed_age_hours: Age in hours after which completed requests are cleaned up
            failed_age_hours: Age in hours after which failed requests are cleaned up
            
        Returns:
            int: Number of requests cleaned up
        """
        pass
    
    # Common utility methods (implemented in base class)
    
    def is_initialized(self) -> bool:
        """Check if the strategy is initialized."""
        return self._is_initialized
    
    def is_running(self) -> bool:
        """Check if the strategy is currently running."""
        return self._is_running
    
    def get_strategy_name(self) -> str:
        """Get the name of this strategy."""
        return self.__class__.__name__.replace("ProcessingStrategy", "").lower()
    
    def log_info(self, message: str, **kwargs):
        """Log an info message with strategy context."""
        self.logger.info(f"[{self.get_strategy_name()}] {message}", extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log a warning message with strategy context."""
        self.logger.warning(f"[{self.get_strategy_name()}] {message}", extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log an error message with strategy context."""
        self.logger.error(f"[{self.get_strategy_name()}] {message}", extra=kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log a debug message with strategy context."""
        self.logger.debug(f"[{self.get_strategy_name()}] {message}", extra=kwargs)
    
    def validate_request(self, request: MarketIntelligenceRequest) -> List[str]:
        """
        Validate a request before processing.
        
        Args:
            request: The request to validate
            
        Returns:
            List[str]: List of validation errors (empty if valid)
        """
        errors = []
        
        # Basic validation
        if not request.request_id:
            errors.append("Request ID is required")
        
        if not request.project_id:
            errors.append("Project ID is required")
        
        if not request.user_id:
            errors.append("User ID is required")
        
        if not request.config:
            errors.append("Configuration is required")
        else:
            # Validate configuration
            if not request.config.keywords:
                errors.append("Keywords are required in configuration")
            
            if not request.config.sources:
                errors.append("Sources are required in configuration")
        
        return errors
    
    def calculate_priority_score(self, request: MarketIntelligenceRequest) -> int:
        """
        Calculate a numeric priority score for request ordering.
        
        Args:
            request: The request to score
            
        Returns:
            int: Priority score (higher = more priority)
        """
        base_score = request.get_priority_score()
        
        # Add urgency based on creation time (older requests get higher priority)
        age_hours = (datetime.utcnow() - request.created_at).total_seconds() / 3600
        age_bonus = min(int(age_hours), 10)  # Max 10 point bonus for age
        
        return base_score * 10 + age_bonus
    
    def format_error_message(self, operation: str, error: Exception, request_id: Optional[str] = None) -> str:
        """
        Format a consistent error message.
        
        Args:
            operation: The operation that failed
            error: The exception that occurred
            request_id: Optional request ID for context
            
        Returns:
            str: Formatted error message
        """
        strategy_name = self.get_strategy_name()
        timestamp = datetime.utcnow().isoformat()
        
        if request_id:
            return f"[{strategy_name}] {operation} failed for request {request_id} at {timestamp}: {str(error)}"
        else:
            return f"[{strategy_name}] {operation} failed at {timestamp}: {str(error)}"
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get the health status of this strategy.
        
        Returns:
            Dict[str, Any]: Health status information
        """
        return {
            "strategy": self.get_strategy_name(),
            "initialized": self._is_initialized,
            "running": self._is_running,
            "timestamp": datetime.utcnow().isoformat(),
            "config_keys": list(self.config.keys()) if self.config else []
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.shutdown()


class StrategyError(Exception):
    """Base exception for strategy-related errors."""
    
    def __init__(self, message: str, strategy_name: str, request_id: Optional[str] = None):
        self.strategy_name = strategy_name
        self.request_id = request_id
        super().__init__(message)


class StrategyInitializationError(StrategyError):
    """Exception raised when strategy initialization fails."""
    pass


class StrategyOperationError(StrategyError):
    """Exception raised when a strategy operation fails."""
    pass


class RequestNotFoundError(StrategyError):
    """Exception raised when a requested item is not found."""
    pass


class RequestValidationError(StrategyError):
    """Exception raised when request validation fails."""
    
    def __init__(self, message: str, strategy_name: str, validation_errors: List[str], request_id: Optional[str] = None):
        self.validation_errors = validation_errors
        super().__init__(message, strategy_name, request_id) 