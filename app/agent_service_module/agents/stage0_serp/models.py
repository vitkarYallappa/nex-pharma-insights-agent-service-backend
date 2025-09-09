from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Stage0SerpRequest(BaseModel):
    """Request model for stage0_serp."""
    request_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class Stage0SerpResponse(BaseModel):
    """Response model for stage0_serp."""
    request_id: str
    result: Dict[str, Any]
    status: str
    timestamp: datetime = datetime.utcnow()
