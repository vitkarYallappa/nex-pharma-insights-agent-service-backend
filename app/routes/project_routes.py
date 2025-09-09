from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.controllers.project_controller import ProjectController
from app.schemas.project_schema import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ProjectListResponse,
    ProjectDataResponse
)
from app.schemas.base_schema import PaginationParams

router = APIRouter(prefix="/projects", tags=["projects"])
controller = ProjectController()


@router.get("/", response_model=ProjectListResponse)
async def get_all_projects(
    pagination: PaginationParams = Depends()
):
    """
    Get all projects with pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 10, max: 100)
    """
    return await controller.get_all_projects(pagination)


@router.get("/{project_id}", response_model=ProjectDataResponse)
async def get_project_by_id(project_id: str):
    """
    Get a specific project by ID.
    
    - **project_id**: The unique identifier of the project
    """
    return await controller.get_project_by_id(project_id)


@router.post("/", response_model=ProjectDataResponse, status_code=201)
async def create_project(request: ProjectCreateRequest):
    """
    Create a new project.
    
    - **name**: Project name (required)
    - **description**: Project description (optional)
    - **owner_id**: Project owner user ID (required)
    - **tags**: List of project tags (optional)
    - **metadata**: Additional metadata (optional)
    """
    return await controller.create_project(request)


@router.put("/{project_id}", response_model=ProjectDataResponse)
async def update_project(project_id: str, request: ProjectUpdateRequest):
    """
    Update an existing project.
    
    - **project_id**: The unique identifier of the project
    - **name**: Project name (optional)
    - **description**: Project description (optional)
    - **status**: Project status (optional)
    - **tags**: List of project tags (optional)
    - **metadata**: Additional metadata (optional)
    """
    return await controller.update_project(project_id, request)


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """
    Delete a project.
    
    - **project_id**: The unique identifier of the project
    """
    return await controller.delete_project(project_id)


@router.get("/owner/{owner_id}", response_model=ProjectListResponse)
async def get_projects_by_owner(owner_id: str):
    """
    Get all projects by owner ID.
    
    - **owner_id**: The unique identifier of the project owner
    """
    return await controller.get_projects_by_owner(owner_id)


@router.get("/search/", response_model=ProjectListResponse)
async def search_projects(
    q: str = Query(..., description="Search query for project names")
):
    """
    Search projects by name.
    
    - **q**: Search query string
    """
    return await controller.search_projects(q) 