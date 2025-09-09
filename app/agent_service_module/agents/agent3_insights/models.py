from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Agent3InsightsRequest(BaseModel):
    """Request model for agent3_insights."""
    request_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class Agent3InsightsResponse(BaseModel):
    """Response model for agent3_insights."""
    request_id: str
    result: Dict[str, Any]
    status: str
    timestamp: datetime = datetime.utcnow()
