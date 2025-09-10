import os
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables

# Global settings instance
settings = Settings() 