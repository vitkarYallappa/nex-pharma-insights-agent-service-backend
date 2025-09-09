from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.config.settings import settings
from app.models.request_model import RequestModel
from app.core.exceptions import DatabaseException


class RequestRepository(BaseRepository):
    """Request repository for DynamoDB operations."""
    
    def __init__(self):
        super().__init__(settings.requests_table)
    
    async def get_requests_by_project(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all requests by project ID."""
        return await self.query_by_attribute('project_id', project_id)
    
    async def get_requests_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all requests by status."""
        return await self.query_by_attribute('status', status)
    
    async def get_requests_by_type(self, request_type: str) -> List[Dict[str, Any]]:
        """Get all requests by type."""
        return await self.query_by_attribute('request_type', request_type)
    
    async def get_requests_by_priority(self, priority: str) -> List[Dict[str, Any]]:
        """Get all requests by priority."""
        return await self.query_by_attribute('priority', priority) 