from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class OpenaiResponse(BaseModel):
    """Response model for Openai API."""
    status: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
