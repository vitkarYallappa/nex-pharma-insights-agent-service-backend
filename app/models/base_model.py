from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class BaseDataModel(BaseModel):
    """Base data model with common fields."""
    
    id: str = Field(..., description="Unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
    
    def to_dynamodb_item(self) -> Dict[str, Any]:
        """Convert model to DynamoDB item format."""
        item = {}
        for field_name, field_value in self.dict().items():
            if field_value is not None:
                if isinstance(field_value, datetime):
                    item[field_name] = field_value.isoformat()
                else:
                    item[field_name] = field_value
        return item
    
    @classmethod
    def from_dynamodb_item(cls, item: Dict[str, Any]):
        """Create model instance from DynamoDB item."""
        # Convert datetime strings back to datetime objects
        for field_name, field_info in cls.model_fields.items():
            if field_name in item:
                # Check if the field is a datetime type
                if hasattr(field_info, 'annotation') and field_info.annotation == datetime:
                    if isinstance(item[field_name], str):
                        item[field_name] = datetime.fromisoformat(item[field_name])
                elif str(field_info).find('datetime') != -1:  # Fallback check
                    if isinstance(item[field_name], str):
                        try:
                            item[field_name] = datetime.fromisoformat(item[field_name])
                        except ValueError:
                            pass  # Not a datetime string
        
        return cls(**item) 