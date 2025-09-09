"""
Custom exceptions for the agent service system.
"""

class AgentServiceException(Exception):
    """Base exception for agent service errors."""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ConfigurationError(AgentServiceException):
    """Raised when there's a configuration error."""
    pass

class APIError(AgentServiceException):
    """Raised when there's an API error."""
    pass

class StorageError(AgentServiceException):
    """Raised when there's a storage error."""
    pass

class DatabaseError(AgentServiceException):
    """Raised when there's a database error."""
    pass

class ValidationError(AgentServiceException):
    """Raised when there's a validation error."""
    pass

class ProcessingError(AgentServiceException):
    """Raised when there's a processing error."""
    pass 