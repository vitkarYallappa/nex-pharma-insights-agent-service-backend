import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


def generate_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix."""
    unique_id = uuid.uuid4().hex[:12]
    return f"{prefix}_{unique_id}" if prefix else unique_id


def current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat() if dt else None


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary."""
    return {k: v for k, v in data.items() if v is not None}


def paginate_list(
    items: List[Any], 
    page: int = 1, 
    page_size: int = 10
) -> Dict[str, Any]:
    """Paginate a list of items."""
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    paginated_items = items[start_index:end_index]
    
    return {
        "items": paginated_items,
        "total": len(items),
        "page": page,
        "page_size": page_size,
        "total_pages": (len(items) + page_size - 1) // page_size
    }


def validate_uuid(uuid_string: str) -> bool:
    """Validate if string is a valid UUID."""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False 