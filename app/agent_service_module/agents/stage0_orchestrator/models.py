from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class Stage0OrchestratorRequest(BaseModel):
    """Request model for stage0_orchestrator."""
    request_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.utcnow()

class Stage0OrchestratorResponse(BaseModel):
    """Response model for stage0_orchestrator."""
    request_id: str
    result: Dict[str, Any]
    status: str
    timestamp: datetime = datetime.utcnow()
