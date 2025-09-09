from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Agent1DeduplicationRequest(BaseModel):
    """Request model for agent1_deduplication."""
    request_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class Agent1DeduplicationResponse(BaseModel):
    """Response model for agent1_deduplication."""
    request_id: str
    result: Dict[str, Any]
    status: str
    timestamp: datetime = datetime.utcnow()
