from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class OrchestratorResponse(BaseModel):
    """Response model for Orchestrator API."""
    status: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
