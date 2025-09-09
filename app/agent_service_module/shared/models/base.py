from pydantic import BaseModel as PydanticBaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class BaseModel(PydanticBaseModel):
    """Base model for all agent service models."""
    
    id: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True
        validate_assignment = True
    
    def update_timestamp(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return self.json() 