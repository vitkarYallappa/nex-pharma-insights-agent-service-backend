from fastapi import HTTPException
from typing import Any, Dict, Optional, List


class BaseCustomException(HTTPException):
    """Base custom exception class."""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ItemNotFoundException(BaseCustomException):
    """Exception raised when an item is not found."""
    
    def __init__(self, item_type: str, item_id: str):
        super().__init__(
            status_code=404,
            detail=f"{item_type} with ID '{item_id}' not found"
        )


class ValidationException(BaseCustomException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=422,
            detail=f"Validation error: {message}"
        )


class DatabaseException(BaseCustomException):
    """Exception raised for database errors."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=500,
            detail=f"Database error: {message}"
        )


class BusinessLogicException(BaseCustomException):
    """Exception raised for business logic errors."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=400,
            detail=f"Business logic error: {message}"
        )


# Root Orchestrator Exception Classes
# These are the exceptions used by the Root Orchestrator system

class ValidationError(Exception):
    """Exception raised for validation errors in Root Orchestrator."""
    
    def __init__(self, message: str, details: Optional[List[str]] = None):
        self.message = message
        self.details = details or []
        super().__init__(self.message)


class NotFoundError(Exception):
    """Exception raised when a resource is not found in Root Orchestrator."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        self.message = message
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(self.message)


class BusinessLogicError(Exception):
    """Exception raised for business logic errors in Root Orchestrator."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ServiceUnavailableError(Exception):
    """Exception raised when a service is unavailable in Root Orchestrator."""
    
    def __init__(self, message: str, service_name: Optional[str] = None, retry_after: Optional[int] = None):
        self.message = message
        self.service_name = service_name
        self.retry_after = retry_after
        super().__init__(self.message)


class StrategyError(Exception):
    """Exception raised for processing strategy errors."""
    
    def __init__(self, message: str, strategy_name: str, request_id: Optional[str] = None):
        self.message = message
        self.strategy_name = strategy_name
        self.request_id = request_id
        super().__init__(self.message)


class StrategyInitializationError(StrategyError):
    """Exception raised when a processing strategy fails to initialize."""
    
    def __init__(self, message: str, strategy_name: str):
        super().__init__(f"Strategy initialization failed: {message}", strategy_name)


class StrategyOperationError(StrategyError):
    """Exception raised when a processing strategy operation fails."""
    
    def __init__(self, message: str, strategy_name: str, request_id: Optional[str] = None):
        super().__init__(f"Strategy operation failed: {message}", strategy_name, request_id)


class RequestNotFoundError(StrategyError):
    """Exception raised when a request is not found in a processing strategy."""
    
    def __init__(self, message: str, strategy_name: str, request_id: str):
        super().__init__(f"Request not found: {message}", strategy_name, request_id)


class RequestValidationError(StrategyError):
    """Exception raised when request validation fails in a processing strategy."""
    
    def __init__(self, message: str, strategy_name: str, validation_errors: List[str], request_id: Optional[str] = None):
        self.validation_errors = validation_errors
        super().__init__(f"Request validation failed: {message}", strategy_name, request_id)


# Configuration and Service Errors

class ConfigurationError(Exception):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        self.message = message
        self.config_key = config_key
        super().__init__(self.message)


class ServiceInitializationError(Exception):
    """Exception raised when a service fails to initialize."""
    
    def __init__(self, message: str, service_name: str):
        self.message = message
        self.service_name = service_name
        super().__init__(self.message)


class WorkflowError(Exception):
    """Exception raised for workflow execution errors."""
    
    def __init__(self, message: str, workflow_stage: Optional[str] = None, request_id: Optional[str] = None):
        self.message = message
        self.workflow_stage = workflow_stage
        self.request_id = request_id
        super().__init__(self.message) 