# FastAPI Agent Service - Complete Architecture Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Design](#architecture-design)
3. [Folder Structure](#folder-structure)
4. [Core Components](#core-components)
5. [Configuration Setup](#configuration-setup)
6. [Database Layer](#database-layer)
7. [Models and Schemas](#models-and-schemas)
8. [Repository Layer](#repository-layer)
9. [Service Layer](#service-layer)
10. [Controller Layer](#controller-layer)
11. [Routes Layer](#routes-layer)
12. [Middleware and Utils](#middleware-and-utils)
13. [Main Application](#main-application)
14. [Dependencies](#dependencies)
15. [Implementation Examples](#implementation-examples)
16. [Best Practices](#best-practices)
17. [Testing Strategy](#testing-strategy)
18. [Deployment Guide](#deployment-guide)

## Project Overview

The Agent Service is a FastAPI-based microservice designed with a layered architecture pattern. It uses DynamoDB as the primary database and follows clean architecture principles with clear separation of concerns.

### Key Features
- **FastAPI Framework**: Modern, fast web framework for building APIs
- **DynamoDB Integration**: NoSQL database with boto3 client
- **Layered Architecture**: Clear separation between routes, controllers, services, and repositories
- **Pydantic Validation**: Request/response validation and serialization
- **Modular Design**: Three core modules (project, request, content_repository)
- **Async Support**: Full asynchronous request handling

### Technology Stack
- **Framework**: FastAPI 0.104.1
- **Database**: AWS DynamoDB
- **ORM/Client**: boto3
- **Validation**: Pydantic
- **Authentication**: JWT (optional)
- **Documentation**: Auto-generated OpenAPI/Swagger

## Architecture Design

The service follows a clean architecture pattern with the following layers:

```
┌─────────────────┐
│     Routes      │ ← HTTP endpoints and routing
├─────────────────┤
│   Controllers   │ ← Request/Response handling
├─────────────────┤
│    Services     │ ← Business logic
├─────────────────┤
│  Repositories   │ ← Data access layer
├─────────────────┤
│    Database     │ ← DynamoDB connection
└─────────────────┘
```

### Design Principles
1. **Single Responsibility**: Each layer has a specific purpose
2. **Dependency Inversion**: Higher layers depend on abstractions
3. **Open/Closed**: Open for extension, closed for modification
4. **Interface Segregation**: Small, focused interfaces
5. **DRY**: Don't repeat yourself

## Folder Structure

```
agent_service/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application entry point
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py             # Configuration settings
│   ├── core/
│   │   ├── __init__.py
│   │   ├── database.py             # Database connection
│   │   ├── exceptions.py           # Custom exceptions
│   │   └── logging.py              # Logging configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py           # Base model class
│   │   ├── project_model.py        # Project data model
│   │   ├── request_model.py        # Request data model
│   │   └── content_repository_model.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base_schema.py          # Base Pydantic schemas
│   │   ├── project_schema.py       # Project request/response schemas
│   │   ├── request_schema.py       # Request schemas
│   │   └── content_repository_schema.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base_repository.py      # Base repository class
│   │   ├── project_repository.py   # Project data access
│   │   ├── request_repository.py   # Request data access
│   │   └── content_repository_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_service.py         # Base service class
│   │   ├── project_service.py      # Project business logic
│   │   ├── request_service.py      # Request business logic
│   │   └── content_repository_service.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── base_controller.py      # Base controller class
│   │   ├── project_controller.py   # Project API handlers
│   │   ├── request_controller.py   # Request API handlers
│   │   └── content_repository_controller.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── project_routes.py       # Project endpoints
│   │   ├── request_routes.py       # Request endpoints
│   │   └── content_repository_routes.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── cors_middleware.py      # CORS configuration
│   │   ├── auth_middleware.py      # Authentication middleware
│   │   └── logging_middleware.py   # Request logging
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py              # Utility functions
│       ├── validators.py           # Custom validators
│       └── formatters.py           # Data formatters
├── requirements.txt                # Python dependencies
├── .env.example                   # Environment variables template
└── README.md                      # Project documentation
```

## Core Components

### 1. Configuration Management

**File: `app/config/settings.py`**

```python
import os
from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings configuration."""
    
    # Application settings
    app_name: str = "Agent Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API settings
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    
    # DynamoDB settings
    aws_region: str = "us-east-1"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    dynamodb_endpoint_url: Optional[str] = None
    
    # Table names
    projects_table: str = "projects"
    requests_table: str = "requests"
    content_repository_table: str = "content_repository"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
```

### 2. Database Connection

**File: `app/core/database.py`**

```python
import boto3
from botocore.exceptions import ClientError
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class DynamoDBConnection:
    """DynamoDB connection manager."""
    
    def __init__(self):
        self._client = None
        self._resource = None
    
    @property
    def client(self):
        """Get DynamoDB client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    @property
    def resource(self):
        """Get DynamoDB resource."""
        if self._resource is None:
            self._resource = self._create_resource()
        return self._resource
    
    def _create_client(self):
        """Create DynamoDB client."""
        try:
            client_config = {
                'region_name': settings.aws_region
            }
            
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                client_config.update({
                    'aws_access_key_id': settings.aws_access_key_id,
                    'aws_secret_access_key': settings.aws_secret_access_key
                })
            
            if settings.dynamodb_endpoint_url:
                client_config['endpoint_url'] = settings.dynamodb_endpoint_url
            
            return boto3.client('dynamodb', **client_config)
        except Exception as e:
            logger.error(f"Failed to create DynamoDB client: {e}")
            raise
    
    def _create_resource(self):
        """Create DynamoDB resource."""
        try:
            resource_config = {
                'region_name': settings.aws_region
            }
            
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                resource_config.update({
                    'aws_access_key_id': settings.aws_access_key_id,
                    'aws_secret_access_key': settings.aws_secret_access_key
                })
            
            if settings.dynamodb_endpoint_url:
                resource_config['endpoint_url'] = settings.dynamodb_endpoint_url
            
            return boto3.resource('dynamodb', **resource_config)
        except Exception as e:
            logger.error(f"Failed to create DynamoDB resource: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check DynamoDB connection health."""
        try:
            self.client.list_tables()
            return True
        except ClientError as e:
            logger.error(f"DynamoDB health check failed: {e}")
            return False


# Global database connection instance
db_connection = DynamoDBConnection()
```

### 3. Custom Exceptions

**File: `app/core/exceptions.py`**

```python
from fastapi import HTTPException
from typing import Any, Dict, Optional


class BaseCustomException(HTTPException):
    """Base custom exception class."""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ItemNotFoundException(BaseCustomException):
    """Exception raised when an item is not found."""
    
    def __init__(self, item_type: str, item_id: str):
        super().__init__(
            status_code=404,
            detail=f"{item_type} with ID '{item_id}' not found"
        )


class ValidationException(BaseCustomException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=422,
            detail=f"Validation error: {message}"
        )


class DatabaseException(BaseCustomException):
    """Exception raised for database errors."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=500,
            detail=f"Database error: {message}"
        )


class BusinessLogicException(BaseCustomException):
    """Exception raised for business logic errors."""
    
    def __init__(self, message: str):
        super().__init__(
            status_code=400,
            detail=f"Business logic error: {message}"
        )
```

### 4. Logging Configuration

**File: `app/core/logging.py`**

```python
import logging
import sys
from app.config.settings import settings


def setup_logging():
    """Setup application logging configuration."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level.upper()))
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    loggers = [
        'app',
        'uvicorn',
        'fastapi'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, settings.log_level.upper()))
```

## Models and Schemas

### Base Model

**File: `app/models/base_model.py`**

```python
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
        for field_name, field_info in cls.__fields__.items():
            if field_name in item and field_info.type_ == datetime:
                if isinstance(item[field_name], str):
                    item[field_name] = datetime.fromisoformat(item[field_name])
        
        return cls(**item)
```

### Project Model

**File: `app/models/project_model.py`**

```python
from typing import Optional, List
from pydantic import Field
from app.models.base_model import BaseDataModel


class ProjectModel(BaseDataModel):
    """Project data model."""
    
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: str = Field(default="active", description="Project status")
    owner_id: str = Field(..., description="Project owner user ID")
    tags: Optional[List[str]] = Field(default_factory=list, description="Project tags")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "proj_123456789",
                "name": "Sample Project",
                "description": "A sample project for demonstration",
                "status": "active",
                "owner_id": "user_123",
                "tags": ["sample", "demo"],
                "metadata": {"priority": "high"}
            }
        }
```

### Request Model

**File: `app/models/request_model.py`**

```python
from typing import Optional, Dict, Any
from pydantic import Field
from app.models.base_model import BaseDataModel


class RequestModel(BaseDataModel):
    """Request data model."""
    
    project_id: str = Field(..., description="Associated project ID")
    request_type: str = Field(..., description="Type of request")
    status: str = Field(default="pending", description="Request status")
    priority: str = Field(default="medium", description="Request priority")
    payload: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Request payload")
    response_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Response data")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "req_123456789",
                "project_id": "proj_123456789",
                "request_type": "data_analysis",
                "status": "pending",
                "priority": "high",
                "payload": {"data_source": "api", "filters": {}},
                "response_data": {},
                "error_message": None
            }
        }
```

### Content Repository Model

**File: `app/models/content_repository_model.py`**

```python
from typing import Optional, List, Dict, Any
from pydantic import Field
from app.models.base_model import BaseDataModel


class ContentRepositoryModel(BaseDataModel):
    """Content repository data model."""
    
    title: str = Field(..., description="Content title")
    content_type: str = Field(..., description="Type of content")
    content_url: Optional[str] = Field(None, description="URL to content")
    content_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Content data")
    tags: Optional[List[str]] = Field(default_factory=list, description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    status: str = Field(default="active", description="Content status")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "content_123456789",
                "title": "Sample Content",
                "content_type": "article",
                "content_url": "https://example.com/content",
                "content_data": {"summary": "This is a sample content"},
                "tags": ["sample", "article"],
                "category": "documentation",
                "status": "active",
                "metadata": {"author": "John Doe"}
            }
        }
```

### Base Schema

**File: `app/schemas/base_schema.py`**

```python
from datetime import datetime
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response schema."""
    
    success: bool = Field(True, description="Request success status")
    message: str = Field("Operation completed successfully", description="Response message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DataResponse(BaseResponse, GenericModel, Generic[T]):
    """Generic data response schema."""
    
    data: Optional[T] = Field(None, description="Response data")


class ListResponse(BaseResponse, GenericModel, Generic[T]):
    """Generic list response schema."""
    
    data: List[T] = Field(default_factory=list, description="List of items")
    total: int = Field(0, description="Total number of items")
    page: int = Field(1, description="Current page number")
    page_size: int = Field(10, description="Items per page")


class ErrorResponse(BaseModel):
    """Error response schema."""
    
    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaginationParams(BaseModel):
    """Pagination parameters schema."""
    
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(10, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for pagination."""
        return (self.page - 1) * self.page_size
```

### Project Schema

**File: `app/schemas/project_schema.py`**

```python
from typing import Optional, List
from pydantic import BaseModel, Field
from app.schemas.base_schema import DataResponse, ListResponse
from app.models.project_model import ProjectModel


class ProjectCreateRequest(BaseModel):
    """Project creation request schema."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    owner_id: str = Field(..., description="Project owner user ID")
    tags: Optional[List[str]] = Field(default_factory=list, description="Project tags")
    metadata: Optional[dict] = Field(default_factory=dict, description="Additional metadata")


class ProjectUpdateRequest(BaseModel):
    """Project update request schema."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    status: Optional[str] = Field(None, description="Project status")
    tags: Optional[List[str]] = Field(None, description="Project tags")
    metadata: Optional[dict] = Field(None, description="Additional metadata")


class ProjectResponse(ProjectModel):
    """Project response schema."""
    pass


class ProjectListResponse(ListResponse[ProjectResponse]):
    """Project list response schema."""
    pass


class ProjectDataResponse(DataResponse[ProjectResponse]):
    """Single project response schema."""
    pass
```

## Repository Layer

### Base Repository

**File: `app/repositories/base_repository.py`**

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type
from botocore.exceptions import ClientError
from app.core.database import db_connection
from app.core.exceptions import DatabaseException, ItemNotFoundException
import logging

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """Base repository class for DynamoDB operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.table = db_connection.resource.Table(table_name)
    
    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item by ID."""
        try:
            response = self.table.get_item(
                Key={'id': item_id}
            )
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Error getting item {item_id} from {self.table_name}: {e}")
            raise DatabaseException(f"Failed to get item: {e}")
    
    async def scan_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scan all items in table."""
        try:
            scan_kwargs = {}
            if limit:
                scan_kwargs['Limit'] = limit
            
            response = self.table.scan(**scan_kwargs)
            items = response.get('Items', [])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response and (not limit or len(items) < limit):
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                if limit:
                    scan_kwargs['Limit'] = limit - len(items)
                
                response = self.table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))
            
            return items
        except ClientError as e:
            logger.error(f"Error scanning {self.table_name}: {e}")
            raise DatabaseException(f"Failed to scan items: {e}")
    
    async def create(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create new item."""
        try:
            self.table.put_item(Item=item)
            return item
        except ClientError as e:
            logger.error(f"Error creating item in {self.table_name}: {e}")
            raise DatabaseException(f"Failed to create item: {e}")
    
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing item."""
        try:
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for key, value in updates.items():
                if key != 'id':  # Don't update the primary key
                    attr_name = f"#{key}"
                    attr_value = f":{key}"
                    update_expression += f"{attr_name} = {attr_value}, "
                    expression_attribute_names[attr_name] = key
                    expression_attribute_values[attr_value] = value
            
            update_expression = update_expression.rstrip(', ')
            
            response = self.table.update_item(
                Key={'id': item_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            return response.get('Attributes')
        except ClientError as e:
            logger.error(f"Error updating item {item_id} in {self.table_name}: {e}")
            raise DatabaseException(f"Failed to update item: {e}")
    
    async def delete(self, item_id: str) -> bool:
        """Delete item by ID."""
        try:
            self.table.delete_item(
                Key={'id': item_id}
            )
            return True
        except ClientError as e:
            logger.error(f"Error deleting item {item_id} from {self.table_name}: {e}")
            raise DatabaseException(f"Failed to delete item: {e}")
    
    async def query_by_attribute(
        self, 
        attribute_name: str, 
        attribute_value: Any,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query items by attribute (requires GSI)."""
        try:
            scan_kwargs = {
                'FilterExpression': f"#{attribute_name} = :{attribute_name}",
                'ExpressionAttributeNames': {f"#{attribute_name}": attribute_name},
                'ExpressionAttributeValues': {f":{attribute_name}": attribute_value}
            }
            
            if limit:
                scan_kwargs['Limit'] = limit
            
            response = self.table.scan(**scan_kwargs)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"Error querying {self.table_name} by {attribute_name}: {e}")
            raise DatabaseException(f"Failed to query items: {e}")
```

### Project Repository

**File: `app/repositories/project_repository.py`**

```python
from typing import List, Optional, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.config.settings import settings
from app.models.project_model import ProjectModel


class ProjectRepository(BaseRepository):
    """Project repository for DynamoDB operations."""
    
    def __init__(self):
        super().__init__(settings.projects_table)
    
    async def get_projects_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        """Get all projects by owner ID."""
        return await self.query_by_attribute('owner_id', owner_id)
    
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
```

## Service Layer

### Base Service

**File: `app/services/base_service.py`**

```python
from abc import ABC
from typing import Any, Dict, List, Optional, Type, TypeVar
from app.core.exceptions import ItemNotFoundException, ValidationException
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class BaseService(ABC):
    """Base service class with common business logic."""
    
    def __init__(self, repository):
        self.repository = repository
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]):
        """Validate that required fields are present."""
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            raise ValidationException(f"Missing required fields: {', '.join(missing_fields)}")
    
    def sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data."""
        # Remove None values
        return {k: v for k, v in data.items() if v is not None}
    
    async def get_by_id_or_raise(self, item_id: str, item_type: str = "Item") -> Dict[str, Any]:
        """Get item by ID or raise exception if not found."""
        item = await self.repository.get_by_id(item_id)
        if not item:
            raise ItemNotFoundException(item_type, item_id)
        return item
```

### Project Service

**File: `app/services/project_service.py`**

```python
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
            return [ProjectModel.from_dynamodb_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting all projects: {e}")
            raise
    
    async def get_project_by_id(self, project_id: str) -> ProjectModel:
        """Get project by ID."""
        try:
            item = await self.get_by_id_or_raise(project_id, "Project")
            return ProjectModel.from_dynamodb_item(item)
        except Exception as e:
            logger.error(f"Error getting project {project_id}: {e}")
            raise
    
    async def create_project(self, project_data: Dict[str, Any]) -> ProjectModel:
        """Create new project."""
        try:
            # Validate required fields
            self.validate_required_fields(project_data, ['name', 'owner_id'])
            
            # Generate ID and timestamps
            project_data['id'] = f"proj_{uuid.uuid4().hex[:12]}"
            project_data['created_at'] = datetime.utcnow()
            project_data['updated_at'] = datetime.utcnow()
            
            # Set default status
            if 'status' not in project_data:
                project_data['status'] = 'active'
            
            # Create project model for validation
            project = ProjectModel(**project_data)
            
            # Save to database
            item = await self.repository.create(project.to_dynamodb_item())
            
            return ProjectModel.from_dynamodb_item(item)
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> ProjectModel:
        """Update existing project."""
        try:
            # Check if project exists
            await self.get_by_id_or_raise(project_id, "Project")
            
            # Add update timestamp
            updates['updated_at'] = datetime.utcnow()
            
            # Sanitize updates
            updates = self.sanitize_data(updates)
            
            # Update in database
            item = await self.repository.update(project_id, updates)
            
            return ProjectModel.from_dynamodb_item(item)
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
            return [ProjectModel.from_dynamodb_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error getting projects for owner {owner_id}: {e}")
            raise
    
    async def search_projects(self, query: str) -> List[ProjectModel]:
        """Search projects by name."""
        try:
            items = await self.repository.search_projects_by_name(query)
            return [ProjectModel.from_dynamodb_item(item) for item in items]
        except Exception as e:
            logger.error(f"Error searching projects with query '{query}': {e}")
            raise
    
    async def _validate_project_deletion(self, project_id: str):
        """Validate if project can be deleted."""
        # Add business logic validation here
        # For example, check if project has active requests
        pass
```

## Controller Layer

### Base Controller

**File: `app/controllers/base_controller.py`**

```python
from typing import Any, Dict
from fastapi import HTTPException
from app.core.exceptions import (
    ItemNotFoundException, 
    ValidationException, 
    DatabaseException, 
    BusinessLogicException
)
from app.schemas.base_schema import ErrorResponse
import logging

logger = logging.getLogger(__name__)


class BaseController:
    """Base controller with common request/response handling."""
    
    def handle_exceptions(self, func):
        """Decorator to handle common exceptions."""
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except ItemNotFoundException as e:
                logger.warning(f"Item not found: {e.detail}")
                raise HTTPException(status_code=404, detail=e.detail)
            except ValidationException as e:
                logger.warning(f"Validation error: {e.detail}")
                raise HTTPException(status_code=422, detail=e.detail)
            except BusinessLogicException as e:
                logger.warning(f"Business logic error: {e.detail}")
                raise HTTPException(status_code=400, detail=e.detail)
            except DatabaseException as e:
                logger.error(f"Database error: {e.detail}")
                raise HTTPException(status_code=500, detail="Internal server error")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise HTTPException(status_code=500, detail="Internal server error")
        
        return wrapper
    
    def create_error_response(self, error_message: str, error_code: str = None) -> ErrorResponse:
        """Create standardized error response."""
        return ErrorResponse(
            error=error_message,
            error_code=error_code
        )
```

### Project Controller

**File: `app/controllers/project_controller.py`**

```python
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
    
    @BaseController.handle_exceptions
    async def get_all_projects(
        self, 
        pagination: PaginationParams = Depends()
    ) -> ProjectListResponse:
        """Get all projects with pagination."""
        projects = await self.service.get_all_projects(
            limit=pagination.page_size
        )
        
        return ProjectListResponse(
            data=projects,
            total=len(projects),
            page=pagination.page,
            page_size=pagination.page_size,
            message="Projects retrieved successfully"
        )
    
    @BaseController.handle_exceptions
    async def get_project_by_id(self, project_id: str) -> ProjectDataResponse:
        """Get project by ID."""
        project = await self.service.get_project_by_id(project_id)
        
        return ProjectDataResponse(
            data=project,
            message="Project retrieved successfully"
        )
    
    @BaseController.handle_exceptions
    async def create_project(self, request: ProjectCreateRequest) -> ProjectDataResponse:
        """Create new project."""
        project = await self.service.create_project(request.dict())
        
        return ProjectDataResponse(
            data=project,
            message="Project created successfully"
        )
    
    @BaseController.handle_exceptions
    async def update_project(
        self, 
        project_id: str, 
        request: ProjectUpdateRequest
    ) -> ProjectDataResponse:
        """Update existing project."""
        # Only include non-None values in update
        updates = {k: v for k, v in request.dict().items() if v is not None}
        
        project = await self.service.update_project(project_id, updates)
        
        return ProjectDataResponse(
            data=project,
            message="Project updated successfully"
        )
    
    @BaseController.handle_exceptions
    async def delete_project(self, project_id: str) -> dict:
        """Delete project."""
        await self.service.delete_project(project_id)
        
        return {
            "success": True,
            "message": "Project deleted successfully"
        }
    
    @BaseController.handle_exceptions
    async def get_projects_by_owner(self, owner_id: str) -> ProjectListResponse:
        """Get projects by owner."""
        projects = await self.service.get_projects_by_owner(owner_id)
        
        return ProjectListResponse(
            data=projects,
            total=len(projects),
            message="Projects retrieved successfully"
        )
    
    @BaseController.handle_exceptions
    async def search_projects(self, query: str) -> ProjectListResponse:
        """Search projects."""
        projects = await self.service.search_projects(query)
        
        return ProjectListResponse(
            data=projects,
            total=len(projects),
            message="Projects search completed"
        )
```

## Routes Layer

### Project Routes

**File: `app/routes/project_routes.py`**

```python
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
```

## Middleware and Utils

### CORS Middleware

**File: `app/middleware/cors_middleware.py`**

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI


def setup_cors(app: FastAPI):
    """Setup CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure based on your needs
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
```

### Logging Middleware

**File: `app/middleware/logging_middleware.py`**

```python
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} - "
            f"Processing time: {process_time:.4f}s"
        )
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
```

### Utility Functions

**File: `app/utils/helpers.py`**

```python
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


def generate_id(prefix: str = "") -> str:
    """Generate unique ID with optional prefix."""
    unique_id = uuid.uuid4().hex[:12]
    return f"{prefix}_{unique_id}" if prefix else unique_id


def current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string."""
    return dt.isoformat() if dt else None


def clean_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values from dictionary."""
    return {k: v for k, v in data.items() if v is not None}


def paginate_list(
    items: List[Any], 
    page: int = 1, 
    page_size: int = 10
) -> Dict[str, Any]:
    """Paginate a list of items."""
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    paginated_items = items[start_index:end_index]
    
    return {
        "items": paginated_items,
        "total": len(items),
        "page": page,
        "page_size": page_size,
        "total_pages": (len(items) + page_size - 1) // page_size
    }


def validate_uuid(uuid_string: str) -> bool:
    """Validate if string is a valid UUID."""
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False
```

## Main Application

**File: `app/main.py`**

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config.settings import settings
from app.core.logging import setup_logging
from app.core.database import db_connection
from app.middleware.cors_middleware import setup_cors
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes.project_routes import router as project_router
# Import other route modules here
# from app.routes.request_routes import router as request_router
# from app.routes.content_repository_routes import router as content_repository_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Agent Service...")
    
    # Setup logging
    setup_logging()
    
    # Check database connection
    if not db_connection.health_check():
        logger.error("Failed to connect to DynamoDB")
        raise Exception("Database connection failed")
    
    logger.info("Agent Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agent Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A FastAPI microservice with DynamoDB integration",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup middleware
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(project_router, prefix=settings.api_prefix)
# app.include_router(request_router, prefix=settings.api_prefix)
# app.include_router(content_repository_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = db_connection.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": settings.app_version
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
```

## Dependencies

**File: `requirements.txt`**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
boto3==1.34.0
botocore==1.34.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
```

## Environment Configuration

**File: `.env.example`**

```env
# Application Settings
APP_NAME=Agent Service
APP_VERSION=1.0.0
DEBUG=false

# API Settings
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# AWS DynamoDB Settings
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
DYNAMODB_ENDPOINT_URL=http://localhost:8000  # For local DynamoDB

# Table Names
PROJECTS_TABLE=projects
REQUESTS_TABLE=requests
CONTENT_REPOSITORY_TABLE=content_repository

# Logging
LOG_LEVEL=INFO
```

## Implementation Examples

### Example 1: Complete Request Flow

```python
# 1. Route receives HTTP request
@router.get("/{project_id}")
async def get_project_by_id(project_id: str):
    return await controller.get_project_by_id(project_id)

# 2. Controller handles request/response
async def get_project_by_id(self, project_id: str):
    project = await self.service.get_project_by_id(project_id)
    return ProjectDataResponse(data=project)

# 3. Service implements business logic
async def get_project_by_id(self, project_id: str):
    item = await self.get_by_id_or_raise(project_id, "Project")
    return ProjectModel.from_dynamodb_item(item)

# 4. Repository performs database operation
async def get_by_id(self, item_id: str):
    response = self.table.get_item(Key={'id': item_id})
    return response.get('Item')
```

### Example 2: Error Handling

```python
# Custom exception in service
if not project_data.get('name'):
    raise ValidationException("Project name is required")

# Exception handling in controller
@BaseController.handle_exceptions
async def create_project(self, request: ProjectCreateRequest):
    # This decorator handles all exceptions automatically
    return await self.service.create_project(request.dict())

# Global exception handler in main.py
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Internal server error"})
```

## Best Practices

### 1. Code Organization
- Keep each layer focused on its specific responsibility
- Use dependency injection for better testability
- Follow consistent naming conventions
- Implement proper error handling at each layer

### 2. Database Operations
- Always use parameterized queries
- Implement proper connection pooling
- Handle DynamoDB-specific exceptions
- Use batch operations for multiple items

### 3. API Design
- Use appropriate HTTP status codes
- Implement consistent response formats
- Provide comprehensive API documentation
- Use proper request/response validation

### 4. Security
- Validate all input data
- Implement proper authentication/authorization
- Use environment variables for sensitive data
- Log security-related events

### 5. Performance
- Implement proper pagination
- Use async/await for I/O operations
- Cache frequently accessed data
- Monitor and optimize database queries

## Testing Strategy

### Unit Tests Structure
```
tests/
├── unit/
│   ├── test_services/
│   ├── test_repositories/
│   ├── test_controllers/
│   └── test_utils/
├── integration/
│   ├── test_api_endpoints/
│   └── test_database/
└── fixtures/
    └── sample_data.py
```

### Example Unit Test
```python
import pytest
from unittest.mock import AsyncMock, patch
from app.services.project_service import ProjectService
from app.models.project_model import ProjectModel

@pytest.mark.asyncio
async def test_get_project_by_id():
    # Arrange
    service = ProjectService()
    project_data = {"id": "proj_123", "name": "Test Project"}
    
    with patch.object(service.repository, 'get_by_id', return_value=project_data):
        # Act
        result = await service.get_project_by_id("proj_123")
        
        # Assert
        assert isinstance(result, ProjectModel)
        assert result.id == "proj_123"
        assert result.name == "Test Project"
```

## Deployment Guide

### Docker Configuration

**File: `Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ../app ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**File: `docker-compose.yml`**

```yaml
version: '3.8'

services:
  agent-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AWS_REGION=us-east-1
      - DYNAMODB_ENDPOINT_URL=http://dynamodb-local:8000
    depends_on:
      - dynamodb-local
    volumes:
      - .env:/app/.env

  dynamodb-local:
    command: "-jar DynamoDBLocal.jar -sharedDb -dbPath ./data"
    image: "amazon/dynamodb-local:latest"
    container_name: dynamodb-local
    ports:
      - "8000:8000"
    volumes:
      - "./docker/dynamodb:/home/dynamodblocal/data"
    working_dir: /home/dynamodblocal
```

### Kubernetes Deployment

**File: `k8s/deployment.yaml`**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: agent-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: agent-service
  template:
    metadata:
      labels:
        app: agent-service
    spec:
      containers:
      - name: agent-service
        image: agent-service:latest
        ports:
        - containerPort: 8000
        env:
        - name: AWS_REGION
          value: "us-east-1"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### AWS Lambda Deployment

**File: `lambda_handler.py`**

```python
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

## Monitoring and Observability

### Health Checks
- Database connectivity
- Service dependencies
- Resource utilization
- Response time metrics

### Logging Strategy
- Structured logging with JSON format
- Request/response logging
- Error tracking and alerting
- Performance metrics

### Metrics Collection
- API endpoint performance
- Database query performance
- Error rates and types
- Business metrics

## Conclusion

This comprehensive guide provides a complete FastAPI microservice architecture with:

- **Layered Architecture**: Clear separation of concerns
- **DynamoDB Integration**: Robust database operations
- **Error Handling**: Comprehensive exception management
- **Validation**: Request/response validation with Pydantic
- **Documentation**: Auto-generated API documentation
- **Testing**: Unit and integration testing strategies
- **Deployment**: Multiple deployment options
- **Monitoring**: Observability and health checking

The architecture is designed to be scalable, maintainable, and production-ready. Each component is modular and can be extended or modified independently while maintaining the overall system integrity.

Remember to:
1. Customize the configuration for your specific environment
2. Implement proper authentication and authorization
3. Add comprehensive tests for all components
4. Monitor and optimize performance regularly
5. Keep dependencies updated and secure

This foundation provides everything needed to build a robust microservice that can handle production workloads while maintaining code quality and developer productivity. 