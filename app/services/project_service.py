from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from app.services.base_service import BaseService
from app.repositories.project_repository import ProjectRepository
from app.models.project_model import ProjectModel
from app.core.exceptions import ValidationException, BusinessLogicException
import logging

logger = logging.getLogger(__name__)


class ProjectService(BaseService):
    """Project service with business logic."""
    
    def __init__(self):
        self.repository = ProjectRepository()
        super().__init__(self.repository)
    
    async def get_all_projects(self, limit: Optional[int] = None) -> List[ProjectModel]:
        """Get all projects."""
        try:
            items = await self.repository.scan_all(limit)
            return [ProjectModel.from_dict(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting all projects: {e}")
            raise
    
    async def get_project_by_id(self, project_id: str) -> ProjectModel:
        """Get project by ID."""
        try:
            item = await self.get_by_id_or_raise(project_id, "Project")
            return ProjectModel.from_dict(item)
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}")
            raise
    
    async def create_project(self, project_data: Dict[str, Any]) -> ProjectModel:
        """Create new project."""
        try:
            # Validate required fields
            self.validate_required_fields(project_data, ['name', 'created_by'])
            
            # Create new project using the model's create_new method
            project = ProjectModel.create_new(
                name=project_data['name'],
                created_by=project_data['created_by'],
                description=project_data.get('description'),
                status=project_data.get('status'),
                project_metadata=project_data.get('project_metadata'),
                module_config=project_data.get('module_config')
            )
            
            # Save to database
            item = await self.repository.create(project.to_dict())
            
            return ProjectModel.from_dict(item)
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> ProjectModel:
        """Update existing project."""
        try:
            # Check if project exists
            await self.get_by_id_or_raise(project_id, "Project")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            # Sanitize updates
            updates = self.sanitize_data(updates)
            
            # Update in database
            item = await self.repository.update(project_id, updates)
            
            return ProjectModel.from_dict(item)
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            raise
    
    async def delete_project(self, project_id: str) -> bool:
        """Delete project."""
        try:
            # Check if project exists
            await self.get_by_id_or_raise(project_id, "Project")
            
            # Perform business logic checks
            await self._validate_project_deletion(project_id)
            
            # Delete from database
            return await self.repository.delete(project_id)
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            raise
    
    async def get_projects_by_owner(self, owner_id: str) -> List[ProjectModel]:
        """Get projects by owner."""
        try:
            items = await self.repository.get_projects_by_owner(owner_id)
            return [ProjectModel.from_dict(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting projects for owner {owner_id}: {e}")
            raise
    
    async def search_projects(self, query: str) -> List[ProjectModel]:
        """Search projects by name."""
        try:
            items = await self.repository.search_projects_by_name(query)
            return [ProjectModel.from_dict(item) for item in items]
        except Exception as e:
            logger.error(f"Error searching projects with query '{query}': {e}")
            raise
    
    async def _validate_project_deletion(self, project_id: str):
        """Validate if project can be deleted."""
        # Add business logic validation here
        # For example, check if project has active requests
        pass 