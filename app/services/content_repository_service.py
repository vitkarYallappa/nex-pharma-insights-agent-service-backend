from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from app.services.base_service import BaseService
from app.repositories.content_repository_repository import ContentRepositoryRepository
from app.models.content_repository_model import ContentRepositoryModel
from app.core.exceptions import ValidationException, BusinessLogicException
import logging

logger = logging.getLogger(__name__)


class ContentRepositoryService(BaseService):
    """Content repository service with business logic."""
    
    def __init__(self):
        self.repository = ContentRepositoryRepository()
        super().__init__(self.repository)
    
    async def get_all_content(self, limit: Optional[int] = None) -> List[ContentRepositoryModel]:
        """Get all content."""
        try:
            items = await self.repository.scan_all(limit)
            return [ContentRepositoryModel.from_dynamodb_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting all content: {e}")
            raise
    
    async def get_content_by_id(self, content_id: str) -> ContentRepositoryModel:
        """Get content by ID."""
        try:
            item = await self.get_by_id_or_raise(content_id, "Content")
            return ContentRepositoryModel.from_dynamodb_item(item)
        except Exception as e:
            logger.error(f"Error getting content {content_id}: {e}")
            raise
    
    async def create_content(self, content_data: Dict[str, Any]) -> ContentRepositoryModel:
        """Create new content."""
        try:
            # Validate required fields
            self.validate_required_fields(content_data, ['title', 'content_type'])
            
            # Generate ID and timestamps
            content_data['id'] = f"content_{uuid.uuid4().hex[:12]}"
            content_data['created_at'] = datetime.utcnow()
            content_data['updated_at'] = datetime.utcnow()
            
            # Set default status
            if 'status' not in content_data:
                content_data['status'] = 'active'
            
            # Create content model for validation
            content = ContentRepositoryModel(**content_data)
            
            # Save to database
            item = await self.repository.create(content.to_dynamodb_item())
            
            return ContentRepositoryModel.from_dynamodb_item(item)
        except Exception as e:
            logger.error(f"Error creating content: {e}")
            raise
    
    async def update_content(self, content_id: str, updates: Dict[str, Any]) -> ContentRepositoryModel:
        """Update existing content."""
        try:
            # Check if content exists
            await self.get_by_id_or_raise(content_id, "Content")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow()
            
            # Sanitize updates
            updates = self.sanitize_data(updates)
            
            # Update in database
            item = await self.repository.update(content_id, updates)
            
            return ContentRepositoryModel.from_dynamodb_item(item)
        except Exception as e:
            logger.error(f"Error updating content {content_id}: {e}")
            raise
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete content."""
        try:
            # Check if content exists
            await self.get_by_id_or_raise(content_id, "Content")
            
            # Delete from database
            return await self.repository.delete(content_id)
        except Exception as e:
            logger.error(f"Error deleting content {content_id}: {e}")
            raise
    
    async def search_content(self, query: str) -> List[ContentRepositoryModel]:
        """Search content by title."""
        try:
            items = await self.repository.search_content_by_title(query)
            return [ContentRepositoryModel.from_dynamodb_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error searching content with query '{query}': {e}")
            raise 