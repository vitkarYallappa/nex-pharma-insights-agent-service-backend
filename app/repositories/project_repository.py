from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.config.settings import settings
from app.models.project_model import ProjectModel
from app.core.exceptions import DatabaseException


class ProjectRepository(BaseRepository):
    """Project repository for DynamoDB operations."""
    
    def __init__(self):
        super().__init__(settings.projects_table)
    
    async def get_projects_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        """Get all projects by owner ID."""
        return await self.query_by_attribute('created_by', owner_id)
    
    async def get_projects_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get all projects by status."""
        return await self.query_by_attribute('status', status)
    
    async def search_projects_by_name(self, name_pattern: str) -> List[Dict[str, Any]]:
        """Search projects by name pattern."""
        try:
            response = self.table.scan(
                FilterExpression="contains(#name, :name_pattern)",
                ExpressionAttributeNames={'#name': 'name'},
                ExpressionAttributeValues={':name_pattern': name_pattern}
            )
            return response.get('Items', [])
        except Exception as e:
            raise DatabaseException(f"Failed to search projects: {e}") 