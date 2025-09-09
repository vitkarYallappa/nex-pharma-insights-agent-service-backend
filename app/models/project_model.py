import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.config.settings import settings


class ProjectModel(BaseModel):
    """Project model matching existing DynamoDB schema"""
    
    # DynamoDB: pk (String) - Project ID as UUID string
    pk: str = Field(..., description="Project ID (UUID as string)")
    
    # DynamoDB: name (String)
    name: str = Field(..., description="Project name")
    
    # DynamoDB: description (String)
    description: Optional[str] = Field(None, description="Project description")
    
    # DynamoDB: created_by (String) - Creator user ID as UUID string
    created_by: str = Field(..., description="Creator user ID (UUID as string)")
    
    # DynamoDB: status (String)
    status: Optional[str] = Field(None, description="Project status")
    
    # DynamoDB: project_metadata (Map)
    project_metadata: Optional[Dict[str, Any]] = Field(None, description="Project metadata JSON")
    
    # DynamoDB: module_config (Map)
    module_config: Optional[Dict[str, Any]] = Field(None, description="Module configuration JSON")
    
    # DynamoDB: created_at (String) - ISO timestamp
    created_at: str = Field(..., description="Creation timestamp (ISO string)")
    
    # DynamoDB: updated_at (String) - ISO timestamp
    updated_at: Optional[str] = Field(None, description="Last update timestamp (ISO string)")
    
    @classmethod
    def table_name(cls) -> str:
        """Return DynamoDB table name for current environment"""
        return settings.projects_table
    
    @classmethod
    def create_new(cls, name: str, created_by: str, description: Optional[str] = None,
                   status: Optional[str] = None, project_metadata: Optional[Dict[str, Any]] = None,
                   module_config: Optional[Dict[str, Any]] = None) -> 'ProjectModel':
        """Create a new project model instance"""
        now = datetime.utcnow().isoformat()
        
        return cls(
            pk=str(uuid.uuid4()),
            name=name,
            description=description,
            created_by=created_by,
            status=status or "active",
            project_metadata=project_metadata or {},
            module_config=module_config or {},
            created_at=now,
            updated_at=now
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for DynamoDB storage"""
        data = self.model_dump()
        
        # Remove None values to keep DynamoDB items clean
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectModel':
        """Create model instance from DynamoDB data"""
        return cls(**data)
    
    def to_response(self) -> Dict[str, Any]:
        """Convert model to API response format"""
        return {
            "id": self.pk,  # Return as 'id' for API consistency
            "name": self.name,
            "description": self.description,
            "created_by": self.created_by,
            "status": self.status,
            "project_metadata": self.project_metadata,
            "module_config": self.module_config,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields and set updated_at timestamp"""
        for field, value in kwargs.items():
            if hasattr(self, field) and value is not None:
                setattr(self, field, value)
        
        # Always update the timestamp
        self.updated_at = datetime.utcnow().isoformat()
    
    class Config:
        json_schema_extra = {
            "example": {
                "pk": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Sample Project",
                "description": "A sample project for demonstration",
                "created_by": "456e7890-e89b-12d3-a456-426614174001",
                "status": "active",
                "project_metadata": {"priority": "high"},
                "module_config": {"enabled_modules": ["analysis"]},
                "created_at": "2023-01-01T00:00:00.000000",
                "updated_at": "2023-01-01T00:00:00.000000"
            }
        } 