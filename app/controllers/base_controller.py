from typing import Any, Dict
from fastapi import HTTPException
from app.core.exceptions import (
    ItemNotFoundException, 
    ValidationException, 
    DatabaseException, 
    BusinessLogicException
)
from app.schemas.base_schema import ErrorResponse
import logging

logger = logging.getLogger(__name__)


class BaseController:
    """Base controller with common request/response handling."""
    
    def handle_exceptions(self, func):
        """Decorator to handle common exceptions."""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ItemNotFoundException as e:
                logger.warning(f"Item not found: {e.detail}")
                raise HTTPException(status_code=404, detail=e.detail)
            except ValidationException as e:
                logger.warning(f"Validation error: {e.detail}")
                raise HTTPException(status_code=422, detail=e.detail)
            except BusinessLogicException as e:
                logger.warning(f"Business logic error: {e.detail}")
                raise HTTPException(status_code=400, detail=e.detail)
            except DatabaseException as e:
                logger.error(f"Database error: {e.detail}")
                raise HTTPException(status_code=500, detail="Internal server error")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        return wrapper
    
    def create_error_response(self, error_message: str, error_code: str = None) -> ErrorResponse:
        """Create standardized error response."""
        return ErrorResponse(
            error=error_message,
            error_code=error_code
        ) 