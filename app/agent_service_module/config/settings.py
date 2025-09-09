import os
from enum import Enum
from typing import Dict, Any, Optional
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
    
    # Service Modes
    USE_MOCK_APIS: bool = Field(default=False)
    USE_MOCK_STORAGE: bool = Field(default=False)
    USE_MOCK_DATABASE: bool = Field(default=False)
    
    # API Configurations
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4")
    PERPLEXITY_API_KEY: Optional[str] = Field(default=None)
    SERP_API_KEY: Optional[str] = Field(default=None)
    
    # AWS/Bedrock Configuration
    AWS_REGION: str = Field(default="us-east-1")
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None)
    BEDROCK_MODEL_ID: str = Field(default="anthropic.claude-3-sonnet-20240229-v1:0")
    
    # Storage Configuration
    STORAGE_TYPE: str = Field(default="minio")  # "minio" or "s3"
    MINIO_ENDPOINT: str = Field(default="localhost:9000")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin")
    MINIO_SECRET_KEY: str = Field(default="minioadmin")
    S3_BUCKET_NAME: str = Field(default="agent-content-bucket")
    
    # Database Configuration
    DYNAMODB_ENDPOINT: Optional[str] = Field(default="http://localhost:8000")  # Local DynamoDB
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

# Global settings instance
settings = Settings() 