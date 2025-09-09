from fastapi import HTTPException
from typing import Any, Dict, Optional


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