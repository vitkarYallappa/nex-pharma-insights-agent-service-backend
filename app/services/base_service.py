from abc import ABC
from typing import Any, Dict, List, Optional, Type, TypeVar
from app.core.exceptions import ItemNotFoundException, ValidationException
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseService(ABC):
    """Base service class with common business logic."""
    
    def __init__(self, repository):
        self.repository = repository
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]):
        """Validate that required fields are present."""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValidationException(f"Missing required fields: {', '.join(missing_fields)}")
    
    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data."""
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    async def get_by_id_or_raise(self, item_id: str, item_type: str = "Item") -> Dict[str, Any]:
        """Get item by ID or raise exception if not found."""
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundException(item_type, item_id)
        return item 