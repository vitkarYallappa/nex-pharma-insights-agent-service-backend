from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Agent2RelevanceRequest(BaseModel):
    """Request model for agent2_relevance."""
    request_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class Agent2RelevanceResponse(BaseModel):
    """Response model for agent2_relevance."""
    request_id: str
    result: Dict[str, Any]
    status: str
    timestamp: datetime = datetime.utcnow()
