from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from app.services.base_service import BaseService
from app.repositories.request_repository import RequestRepository
from app.models.request_model import RequestModel
from app.core.exceptions import ValidationException, BusinessLogicException
import logging

logger = logging.getLogger(__name__)


class RequestService(BaseService):
    """Request service with business logic."""
    
    def __init__(self):
        self.repository = RequestRepository()
        super().__init__(self.repository)
    
    async def get_all_requests(self, limit: Optional[int] = None) -> List[RequestModel]:
        """Get all requests."""
        try:
            items = await self.repository.scan_all(limit)
            return [RequestModel.from_dynamodb_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting all requests: {e}")
            raise
    
    async def get_request_by_id(self, request_id: str) -> RequestModel:
        """Get request by ID."""
        try:
            item = await self.get_by_id_or_raise(request_id, "Request")
            return RequestModel.from_dynamodb_item(item)
        except Exception as e:
            logger.error(f"Error getting request {request_id}: {e}")
            raise
    
    async def create_request(self, request_data: Dict[str, Any]) -> RequestModel:
        """Create new request."""
        try:
            # Validate required fields
            self.validate_required_fields(request_data, ['project_id', 'request_type'])
            
            # Generate ID and timestamps
            request_data['id'] = f"req_{uuid.uuid4().hex[:12]}"
            request_data['created_at'] = datetime.utcnow()
            request_data['updated_at'] = datetime.utcnow()
            
            # Set default status and priority
            if 'status' not in request_data:
                request_data['status'] = 'pending'
            if 'priority' not in request_data:
                request_data['priority'] = 'medium'
            
            # Create request model for validation
            request = RequestModel(**request_data)
            
            # Save to database
            item = await self.repository.create(request.to_dynamodb_item())
            
            return RequestModel.from_dynamodb_item(item)
        except Exception as e:
            logger.error(f"Error creating request: {e}")
            raise
    
    async def update_request(self, request_id: str, updates: Dict[str, Any]) -> RequestModel:
        """Update existing request."""
        try:
            # Check if request exists
            await self.get_by_id_or_raise(request_id, "Request")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow()
            
            # Sanitize updates
            updates = self.sanitize_data(updates)
            
            # Update in database
            item = await self.repository.update(request_id, updates)
            
            return RequestModel.from_dynamodb_item(item)
        except Exception as e:
            logger.error(f"Error updating request {request_id}: {e}")
            raise
    
    async def delete_request(self, request_id: str) -> bool:
        """Delete request."""
        try:
            # Check if request exists
            await self.get_by_id_or_raise(request_id, "Request")
            
            # Delete from database
            return await self.repository.delete(request_id)
        except Exception as e:
            logger.error(f"Error deleting request {request_id}: {e}")
            raise
    
    async def get_requests_by_project(self, project_id: str) -> List[RequestModel]:
        """Get requests by project."""
        try:
            items = await self.repository.get_requests_by_project(project_id)
            return [RequestModel.from_dynamodb_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting requests for project {project_id}: {e}")
            raise 