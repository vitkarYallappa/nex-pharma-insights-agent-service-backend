from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.config.settings import settings
from app.models.content_repository_model import ContentRepositoryModel
from app.core.exceptions import DatabaseException


class ContentRepositoryRepository(BaseRepository):
    """Content repository for DynamoDB operations."""
    
    def __init__(self):
        super().__init__(settings.content_repository_table)
    
    async def get_content_by_type(self, content_type: str) -> List[Dict[str, Any]]:
        """Get all content by type."""
        return await self.query_by_attribute('content_type', content_type)
    
    async def get_content_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all content by category."""
        return await self.query_by_attribute('category', category)
    
    async def get_content_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all content by status."""
        return await self.query_by_attribute('status', status)
    
    async def search_content_by_title(self, title_pattern: str) -> List[Dict[str, Any]]:
        """Search content by title pattern."""
        try:
            response = self.table.scan(
                FilterExpression="contains(#title, :title_pattern)",
                ExpressionAttributeNames={'#title': 'title'},
                ExpressionAttributeValues={':title_pattern': title_pattern}
            )
            return response.get('Items', [])
        except Exception as e:
            raise DatabaseException(f"Failed to search content: {e}")
    
    async def get_content_by_tags(self, tags: List[str]) -> List[Dict[str, Any]]:
        """Get content that contains any of the specified tags."""
        try:
            # Build filter expression for tags
            filter_expressions = []
            expression_attribute_values = {}
            
            for i, tag in enumerate(tags):
                filter_expressions.append(f"contains(tags, :tag{i})")
                expression_attribute_values[f":tag{i}"] = tag
            
            filter_expression = " OR ".join(filter_expressions)
            
            response = self.table.scan(
                FilterExpression=filter_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return response.get('Items', [])
        except Exception as e:
            raise DatabaseException(f"Failed to search content by tags: {e}") 