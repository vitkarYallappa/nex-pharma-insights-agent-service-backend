from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Stage0PerplexityRequest(BaseModel):
    """Request model for stage0_perplexity."""
    request_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class Stage0PerplexityResponse(BaseModel):
    """Response model for stage0_perplexity."""
    request_id: str
    result: Dict[str, Any]
    status: str
    timestamp: datetime = datetime.utcnow()
