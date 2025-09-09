from typing import List
from fastapi import HTTPException, Depends
from app.controllers.base_controller import BaseController
from app.services.project_service import ProjectService
from app.schemas.project_schema import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectResponse,
    ProjectListResponse,
    ProjectDataResponse
)
from app.schemas.base_schema import PaginationParams
import logging

logger = logging.getLogger(__name__)


class ProjectController(BaseController):
    """Project controller for handling HTTP requests."""
    
    def __init__(self):
        self.service = ProjectService()
    
    async def get_all_projects(
        self, 
        pagination: PaginationParams = Depends()
    ) -> ProjectListResponse:
        """Get all projects with pagination."""
        @self.handle_exceptions
        async def _get_all_projects():
            projects = await self.service.get_all_projects(
                limit=pagination.page_size
            )
            
            # Convert ProjectModel to ProjectResponse
            project_responses = [ProjectResponse.model_validate(project.to_response()) for project in projects]
            
            return ProjectListResponse(
                data=project_responses,
                total=len(project_responses),
                page=pagination.page,
                page_size=pagination.page_size,
                message="Projects retrieved successfully"
            )
        
        return await _get_all_projects()
    
    async def get_project_by_id(self, project_id: str) -> ProjectDataResponse:
        """Get project by ID."""
        @self.handle_exceptions
        async def _get_project_by_id():
            project = await self.service.get_project_by_id(project_id)
            
            # Convert ProjectModel to ProjectResponse
            project_response = ProjectResponse.model_validate(project.to_response())
            
            return ProjectDataResponse(
                data=project_response,
                message="Project retrieved successfully"
            )
        
        return await _get_project_by_id()
    
    async def create_project(self, request: ProjectCreateRequest) -> ProjectDataResponse:
        """Create new project."""
        @self.handle_exceptions
        async def _create_project():
            project = await self.service.create_project(request.dict())
            
            # Convert ProjectModel to ProjectResponse
            project_response = ProjectResponse.model_validate(project.to_response())
            
            return ProjectDataResponse(
                data=project_response,
                message="Project created successfully"
            )
        
        return await _create_project()
    
    async def update_project(
        self, 
        project_id: str, 
        request: ProjectUpdateRequest
    ) -> ProjectDataResponse:
        """Update existing project."""
        @self.handle_exceptions
        async def _update_project():
            # Only include non-None values in update
            updates = {k: v for k, v in request.dict().items() if v is not None}
            
            project = await self.service.update_project(project_id, updates)
            
            # Convert ProjectModel to ProjectResponse
            project_response = ProjectResponse.model_validate(project.to_response())
            
            return ProjectDataResponse(
                data=project_response,
                message="Project updated successfully"
            )
        
        return await _update_project()
    
    async def delete_project(self, project_id: str) -> dict:
        """Delete project."""
        @self.handle_exceptions
        async def _delete_project():
            await self.service.delete_project(project_id)
            
            return {
                "success": True,
                "message": "Project deleted successfully"
            }
        
        return await _delete_project()
    
    async def get_projects_by_owner(self, owner_id: str) -> ProjectListResponse:
        """Get projects by owner."""
        @self.handle_exceptions
        async def _get_projects_by_owner():
            projects = await self.service.get_projects_by_owner(owner_id)
            
            # Convert ProjectModel to ProjectResponse
            project_responses = [ProjectResponse.model_validate(project.to_response()) for project in projects]
            
            return ProjectListResponse(
                data=project_responses,
                total=len(project_responses),
                message="Projects retrieved successfully"
            )
        
        return await _get_projects_by_owner()
    
    async def search_projects(self, query: str) -> ProjectListResponse:
        """Search projects."""
        @self.handle_exceptions
        async def _search_projects():
            projects = await self.service.search_projects(query)
            
            # Convert ProjectModel to ProjectResponse
            project_responses = [ProjectResponse.model_validate(project.to_response()) for project in projects]
            
            return ProjectListResponse(
                data=project_responses,
                total=len(project_responses),
                message="Projects search completed"
            )
        
        return await _search_projects() 