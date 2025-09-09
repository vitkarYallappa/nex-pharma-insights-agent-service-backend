import os
from enum import Enum
from typing import Dict, Any
from pydantic import BaseSettings

class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"
    MOCK = "mock"

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: Environment = Environment.LOCAL
    
    # Service Modes
    USE_MOCK_APIS: bool = False
    USE_MOCK_STORAGE: bool = False
    USE_MOCK_DATABASE: bool = False
    
    # API Configurations
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4"
    PERPLEXITY_API_KEY: str = ""
    SERP_API_KEY: str = ""
    
    # AWS/Bedrock Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Storage Configuration
    STORAGE_TYPE: str = "minio"  # "minio" or "s3"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "agent-content-bucket"
    
    # Database Configuration
    DYNAMODB_ENDPOINT: str = "http://localhost:8000"  # Local DynamoDB
    DYNAMODB_REGION: str = "us-east-1"
    
    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'local')}"
        case_sensitive = True

# Global settings instance
settings = Settings() 