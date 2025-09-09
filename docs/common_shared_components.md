# Common Shared Components Implementation

## 10-Line Prompt:
Create shared infrastructure components including configuration management with environment-based settings (local/dev/prod/mock), service factory pattern for dependency injection that automatically switches between real and mock implementations, database connection manager for DynamoDB with local and AWS endpoints, storage abstraction layer supporting both Minio (local) and S3 (production), base model classes with Pydantic validation, logging utilities with structured logging, text processing utilities for content manipulation, input validators for API requests, custom exception classes for error handling, and file management utilities for object storage operations across all agents.

## What it covers: 
Configuration, database, storage, models, utilities, logging, validation
## Methods: 
Factory pattern, dependency injection, connection management, file operations
## Why: 
Shared infrastructure, consistent patterns, environment abstraction, code reuse

---

## config/settings.py
```python
import os
from enum import Enum
from typing import Optional
from pydantic import BaseSettings, Field

class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    STAGING = "staging" 
    PROD = "prod"
    MOCK = "mock"

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: Environment = Field(default=Environment.LOCAL)
    
    # Mock flags
    USE_MOCK_APIS: bool = Field(default=False)
    USE_MOCK_STORAGE: bool = Field(default=False)
    USE_MOCK_DATABASE: bool = Field(default=False)
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4")
    PERPLEXITY_API_KEY: Optional[str] = Field(default=None)
    SERP_API_KEY: Optional[str] = Field(default=None)
    
    # AWS Configuration
    AWS_REGION: str = Field(default="us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None)
    BEDROCK_MODEL_ID: str = Field(default="anthropic.claude-3-sonnet-20240229-v1:0")
    
    # Storage
    STORAGE_TYPE: str = Field(default="minio")
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    S3_BUCKET_NAME: str = Field(default="agent-content-bucket")
    
    # Database
    DYNAMODB_ENDPOINT: Optional[str] = Field(default="http://localhost:8000")
    DYNAMODB_REGION: str = Field(default="us-east-1")
    
    def is_local(self) -> bool:
        return self.ENVIRONMENT == Environment.LOCAL
        
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PROD
        
    def should_use_mocks(self) -> bool:
        return self.ENVIRONMENT == Environment.MOCK
    
    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'local')}"
        case_sensitive = True

settings = Settings()
```

## config/service_factory.py
```python
from typing import Any
from .settings import settings

class ServiceFactory:
    """Factory for creating service instances based on environment"""
    
    @staticmethod
    def get_openai_client():
        if settings.USE_MOCK_APIS:
            from ..agents.agent1_deduplication.openai_mock import OpenAIMock
            return OpenAIMock()
        else:
            from ..agents.agent1_deduplication.openai_api import OpenAIAPI
            return OpenAIAPI()
    
    @staticmethod
    def get_bedrock_client():
        if settings.USE_MOCK_APIS:
            from ..agents.agent1_deduplication.bedrock_mock import BedrockMock
            return BedrockMock()
        else:
            from ..agents.agent1_deduplication.bedrock_api import BedrockAPI
            return BedrockAPI()
    
    @staticmethod
    def get_storage_client():
        if settings.USE_MOCK_STORAGE:
            from ..shared.storage.storage_mock import StorageMock
            return StorageMock()
        elif settings.STORAGE_TYPE == "minio":
            from ..shared.storage.minio_client import MinioClient
            return MinioClient()
        else:
            from ..shared.storage.s3_client import S3Client
            return S3Client()
    
    @staticmethod
    def get_database_client():
        if settings.USE_MOCK_DATABASE:
            from ..shared.database.database_mock import DatabaseMock
            return DatabaseMock()
        else:
            from ..shared.database.dynamodb_client import DynamoDBClient
            return DynamoDBClient()
```

## shared/models/base.py
```python
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class BaseAgentModel(BaseModel):
    """Base model for all agent data structures"""
    id: Optional[str] = Field(default=None)
    request_id: str = Field(..., description="Request identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        validate_assignment = True
        use_enum_values = True

class AgentRequest(BaseAgentModel):
    """Base request model for agent operations"""
    agent_type: str = Field(..., description="Agent type identifier")
    input_data: Dict[str, Any] = Field(..., description="Input data")
    config: Dict[str, Any] = Field(default_factory=dict)

class AgentResponse(BaseAgentModel):
    """Base response model for agent operations"""
    agent_type: str = Field(..., description="Agent type identifier")
    output_data: Dict[str, Any] = Field(..., description="Output data")
    success: bool = Field(default=True)
    error_message: Optional[str] = Field(default=None)
    processing_time: Optional[float] = Field(default=None)
```

## shared/database/dynamodb_client.py
```python
import boto3
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

class DynamoDBClient:
    """DynamoDB client for real database operations"""
    
    def __init__(self):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.DYNAMODB_REGION
        )
        
        if settings.DYNAMODB_ENDPOINT:
            # Local DynamoDB
            self.dynamodb = session.resource(
                'dynamodb',
                endpoint_url=settings.DYNAMODB_ENDPOINT
            )
        else:
            # AWS DynamoDB
            self.dynamodb = session.resource('dynamodb')
    
    async def save_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """Save item to DynamoDB table"""
        try:
            table = self.dynamodb.Table(table_name)
            table.put_item(Item=item)
            logger.info(f"Saved item to {table_name}")
            return True
        except ClientError as e:
            logger.error(f"DynamoDB save error: {e}")
            return False
    
    async def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get item from DynamoDB table"""
        try:
            table = self.dynamodb.Table(table_name)
            response = table.get_item(Key=key)
            return response.get('Item')
        except ClientError as e:
            logger.error(f"DynamoDB get error: {e}")
            return None
    
    async def query_items(self, table_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Query items from DynamoDB table"""
        try:
            table = self.dynamodb.Table(table_name)
            response = table.query(**kwargs)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"DynamoDB query error: {e}")
            return []
```

## shared/storage/s3_client.py
```python
import boto3
import json
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError
from ..config.settings import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)

class S3Client:
    """S3 client for production storage operations"""
    
    def __init__(self):
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.s3 = session.client('s3')
        self.bucket_name = settings.S3_BUCKET_NAME
    
    async def save_json(self, key: str, data: Dict[str, Any]) -> bool:
        """Save JSON data to S3"""
        try:
            json_data = json.dumps(data, default=str)
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_data,
                ContentType='application/json'
            )
            logger.info(f"Saved to S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"S3 save error: {e}")
            return False
    
    async def load_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Load JSON data from S3"""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            data = json.loads(response['Body'].read())
            return data
        except ClientError as e:
            logger.error(f"S3 load error: {e}")
            return None
    
    async def save_text(self, key: str, content: str) -> bool:
        """Save text content to S3"""
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType='text/plain'
            )
            return True
        except ClientError as e:
            logger.error(f"S3 text save error: {e}")
            return False
```

## shared/utils/logger.py
```python
import logging
import sys
from typing import Optional
from ..config.settings import settings

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        # Configure handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Set format
        if settings.ENVIRONMENT == "prod":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set level
        if settings.ENVIRONMENT == "prod":
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.INFO)
    
    return logger
```

## shared/utils/validators.py
```python
from typing import Any, Dict, List
from pydantic import ValidationError, BaseModel

class RequestValidator:
    """Validate API requests and data structures"""
    
    @staticmethod
    def validate_model(model_class: BaseModel, data: Dict[str, Any]) -> tuple[bool, Any]:
        """Validate data against Pydantic model"""
        try:
            validated = model_class(**data)
            return True, validated
        except ValidationError as e:
            return False, str(e)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        import re
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return pattern.match(url) is not None
    
    @staticmethod
    def validate_request_id(request_id: str) -> bool:
        """Validate request ID format"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', request_id))
```

## shared/utils/exceptions.py
```python
class AgentServiceException(Exception):
    """Base exception for agent service errors"""
    pass

class ConfigurationError(AgentServiceException):
    """Configuration related errors"""
    pass

class APIConnectionError(AgentServiceException):
    """API connection errors"""
    pass

class DataValidationError(AgentServiceException):
    """Data validation errors"""
    pass

class StorageError(AgentServiceException):
    """Storage operation errors"""
    pass

class DatabaseError(AgentServiceException):
    """Database operation errors"""
    pass

class ProcessingError(AgentServiceException):
    """Content processing errors"""
    pass
```