# Environment Configuration Structure

```
agent_service_module/
├── __init__.py
│
├── config/
│   ├── __init__.py
│   ├── settings.py              # Main configuration manager
│   ├── environments.py          # Environment-specific configs
│   ├── service_factory.py       # Service factory for dependency injection
│   └── mock_factory.py          # Mock service factory
│
├── agents/
│   ├── __init__.py
│   │
│   ├── stage0_serp/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serp_api.py          # Real SERP API
│   │   ├── serp_mock.py         # Mock SERP API
│   │   ├── serp_response.py
│   │   ├── service.py           # Uses factory to get API client
│   │   ├── storage.py
│   │   └── database.py
│   │
│   ├── stage0_perplexity/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── perplexity_api.py    # Real Perplexity API
│   │   ├── perplexity_mock.py   # Mock Perplexity API
│   │   ├── perplexity_response.py
│   │   ├── service.py
│   │   ├── storage.py
│   │   └── database.py
│   │
│   ├── agent1_deduplication/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── openai_api.py        # Real OpenAI API
│   │   ├── openai_mock.py       # Mock OpenAI API
│   │   ├── openai_response.py
│   │   ├── bedrock_api.py       # Real Bedrock API
│   │   ├── bedrock_mock.py      # Mock Bedrock API
│   │   ├── bedrock_response.py
│   │   ├── embedding_api.py     # Real Embedding API
│   │   ├── embedding_mock.py    # Mock Embedding API
│   │   ├── embedding_response.py
│   │   ├── similarity_engine.py
│   │   ├── clustering_service.py
│   │   ├── service.py           # Uses factory to get API clients
│   │   ├── storage.py
│   │   └── database.py
│   │
│   ├── agent2_relevance/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── openai_api.py        # Real OpenAI API
│   │   ├── openai_mock.py       # Mock OpenAI API
│   │   ├── openai_response.py
│   │   ├── bedrock_api.py       # Real Bedrock API
│   │   ├── bedrock_mock.py      # Mock Bedrock API
│   │   ├── bedrock_response.py
│   │   ├── kiq_engine.py
│   │   ├── kit_classifier.py
│   │   ├── scoring_engine.py
│   │   ├── service.py           # Uses factory to get API clients
│   │   ├── storage.py
│   │   └── database.py
│   │
│   ├── agent3_insights/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── openai_api.py        # Real OpenAI API
│   │   ├── openai_mock.py       # Mock OpenAI API
│   │   ├── openai_response.py
│   │   ├── bedrock_api.py       # Real Bedrock API
│   │   ├── bedrock_mock.py      # Mock Bedrock API
│   │   ├── bedrock_response.py
│   │   ├── rag_retrieval.py
│   │   ├── insight_generator.py
│   │   ├── gap_analyzer.py
│   │   ├── service.py           # Uses factory to get API clients
│   │   ├── storage.py
│   │   └── database.py
│   │
│   └── agent4_implications/
│       ├── __init__.py
│       ├── models.py
│       ├── openai_api.py        # Real OpenAI API
│       ├── openai_mock.py       # Mock OpenAI API
│       ├── openai_response.py
│       ├── bedrock_api.py       # Real Bedrock API
│       ├── bedrock_mock.py      # Mock Bedrock API
│       ├── bedrock_response.py
│       ├── stakeholder_mapper.py
│       ├── impact_assessor.py
│       ├── scenario_planner.py
│       ├── service.py           # Uses factory to get API clients
│       ├── storage.py
│       └── database.py
│
├── shared/
│   ├── __init__.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── dynamodb_client.py   # Real DynamoDB client
│   │   ├── dynamodb_mock.py     # Mock DynamoDB client
│   │   ├── connection.py        # Uses factory to get client
│   │   ├── base_repository.py
│   │   └── migrations.py
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── s3_client.py         # Real S3 client
│   │   ├── s3_mock.py           # Mock S3 client
│   │   ├── minio_client.py      # Real Minio client
│   │   ├── minio_mock.py        # Mock Minio client
│   │   ├── base_storage.py      # Uses factory to get client
│   │   └── file_manager.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── request.py
│   │   └── common.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── text_processing.py
│       ├── validators.py
│       ├── logger.py
│       └── exceptions.py
│
└── environments/
    ├── __init__.py
    ├── .env.local           # Local environment variables
    ├── .env.dev             # Development environment variables
    ├── .env.staging         # Staging environment variables
    ├── .env.prod            # Production environment variables
    └── .env.mock            # Mock/testing environment variables
```

## Configuration Files:

### **1. config/settings.py - Main Configuration Manager**
```python
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
```

### **2. config/environments.py - Environment-Specific Configs**
```python
from .settings import Environment, Settings

class EnvironmentConfig:
    @staticmethod
    def get_config(env: Environment) -> dict:
        configs = {
            Environment.LOCAL: {
                "USE_MOCK_APIS": False,
                "USE_MOCK_STORAGE": False,
                "USE_MOCK_DATABASE": False,
                "STORAGE_TYPE": "minio",
                "DYNAMODB_ENDPOINT": "http://localhost:8000"
            },
            Environment.DEV: {
                "USE_MOCK_APIS": False,
                "USE_MOCK_STORAGE": False,
                "USE_MOCK_DATABASE": False,
                "STORAGE_TYPE": "s3",
                "DYNAMODB_ENDPOINT": None  # Use AWS DynamoDB
            },
            Environment.STAGING: {
                "USE_MOCK_APIS": False,
                "USE_MOCK_STORAGE": False,
                "USE_MOCK_DATABASE": False,
                "STORAGE_TYPE": "s3",
                "DYNAMODB_ENDPOINT": None
            },
            Environment.PROD: {
                "USE_MOCK_APIS": False,
                "USE_MOCK_STORAGE": False,
                "USE_MOCK_DATABASE": False,
                "STORAGE_TYPE": "s3",
                "DYNAMODB_ENDPOINT": None
            },
            Environment.MOCK: {
                "USE_MOCK_APIS": True,
                "USE_MOCK_STORAGE": True,
                "USE_MOCK_DATABASE": True,
                "STORAGE_TYPE": "mock",
                "DYNAMODB_ENDPOINT": "mock"
            }
        }
        return configs.get(env, configs[Environment.LOCAL])
```

### **3. config/service_factory.py - Service Factory**
```python
from typing import Union, Any
from .settings import settings
from .mock_factory import MockFactory

class ServiceFactory:
    @staticmethod
    def get_openai_client():
        if settings.USE_MOCK_APIS:
            return MockFactory.get_openai_mock()
        else:
            from ..agents.agent1_deduplication.openai_api import OpenAIAPI
            return OpenAIAPI()
    
    @staticmethod
    def get_bedrock_client():
        if settings.USE_MOCK_APIS:
            return MockFactory.get_bedrock_mock()
        else:
            from ..agents.agent1_deduplication.bedrock_api import BedrockAPI
            return BedrockAPI()
    
    @staticmethod
    def get_perplexity_client():
        if settings.USE_MOCK_APIS:
            return MockFactory.get_perplexity_mock()
        else:
            from ..agents.stage0_perplexity.perplexity_api import PerplexityAPI
            return PerplexityAPI()
    
    @staticmethod
    def get_serp_client():
        if settings.USE_MOCK_APIS:
            return MockFactory.get_serp_mock()
        else:
            from ..agents.stage0_serp.serp_api import SerpAPI
            return SerpAPI()
    
    @staticmethod
    def get_storage_client():
        if settings.USE_MOCK_STORAGE:
            return MockFactory.get_storage_mock()
        elif settings.STORAGE_TYPE == "minio":
            from ..shared.storage.minio_client import MinioClient
            return MinioClient()
        else:
            from ..shared.storage.s3_client import S3Client
            return S3Client()
    
    @staticmethod
    def get_database_client():
        if settings.USE_MOCK_DATABASE:
            return MockFactory.get_database_mock()
        else:
            from ..shared.database.dynamodb_client import DynamoDBClient
            return DynamoDBClient()
    
    @staticmethod
    def get_embedding_client():
        if settings.USE_MOCK_APIS:
            return MockFactory.get_embedding_mock()
        else:
            from ..agents.agent1_deduplication.embedding_api import EmbeddingAPI
            return EmbeddingAPI()
```

### **4. config/mock_factory.py - Mock Factory**
```python
class MockFactory:
    @staticmethod
    def get_openai_mock():
        from ..agents.agent1_deduplication.openai_mock import OpenAIMock
        return OpenAIMock()
    
    @staticmethod
    def get_bedrock_mock():
        from ..agents.agent1_deduplication.bedrock_mock import BedrockMock
        return BedrockMock()
    
    @staticmethod
    def get_perplexity_mock():
        from ..agents.stage0_perplexity.perplexity_mock import PerplexityMock
        return PerplexityMock()
    
    @staticmethod
    def get_serp_mock():
        from ..agents.stage0_serp.serp_mock import SerpMock
        return SerpMock()
    
    @staticmethod
    def get_storage_mock():
        from ..shared.storage.s3_mock import S3Mock
        return S3Mock()
    
    @staticmethod
    def get_database_mock():
        from ..shared.database.dynamodb_mock import DynamoDBMock
        return DynamoDBMock()
    
    @staticmethod
    def get_embedding_mock():
        from ..agents.agent1_deduplication.embedding_mock import EmbeddingMock
        return EmbeddingMock()
```

## Environment Files:

### **environments/.env.local**
```env
ENVIRONMENT=local
USE_MOCK_APIS=false
USE_MOCK_STORAGE=false
USE_MOCK_DATABASE=false

# API Keys (for local testing with real APIs)
OPENAI_API_KEY=your_openai_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
SERP_API_KEY=your_serp_key_here

# Local Services
STORAGE_TYPE=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
DYNAMODB_ENDPOINT=http://localhost:8000
```

### **environments/.env.mock**
```env
ENVIRONMENT=mock
USE_MOCK_APIS=true
USE_MOCK_STORAGE=true
USE_MOCK_DATABASE=true

# Mock values (not used but required for validation)
OPENAI_API_KEY=mock_key
PERPLEXITY_API_KEY=mock_key
SERP_API_KEY=mock_key
STORAGE_TYPE=mock
DYNAMODB_ENDPOINT=mock
```

### **environments/.env.prod**
```env
ENVIRONMENT=prod
USE_MOCK_APIS=false
USE_MOCK_STORAGE=false
USE_MOCK_DATABASE=false

# Production API Keys (from environment variables)
OPENAI_API_KEY=${OPENAI_API_KEY}
PERPLEXITY_API_KEY=${PERPLEXITY_API_KEY}
SERP_API_KEY=${SERP_API_KEY}

# AWS Configuration
AWS_REGION=us-east-1
STORAGE_TYPE=s3
S3_BUCKET_NAME=agent-content-prod
# DYNAMODB_ENDPOINT not set = use AWS DynamoDB
```

## Usage in Agent Services:

### **Example: Agent Service Using Factory**
```python
# agents/agent1_deduplication/service.py
from ...config.service_factory import ServiceFactory
from .models import DeduplicationRequest, DeduplicationResponse

class DeduplicationService:
    def __init__(self):
        # Factory automatically provides correct implementation based on environment
        self.openai_client = ServiceFactory.get_openai_client()
        self.bedrock_client = ServiceFactory.get_bedrock_client()
        self.embedding_client = ServiceFactory.get_embedding_client()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process(self, request: DeduplicationRequest) -> DeduplicationResponse:
        # Use clients without knowing if they're real or mock
        embeddings = await self.embedding_client.generate_embeddings(request.content)
        clusters = await self.openai_client.cluster_content(embeddings)
        
        # Store results
        await self.storage_client.save(clusters)
        await self.database_client.store_metadata(clusters)
        
        return DeduplicationResponse(clusters=clusters)
```

## Environment Switching:

### **1. Local Development:**
```bash
export ENVIRONMENT=local
python main.py  # Uses minio + local DynamoDB + real APIs
```

### **2. Mock Testing:**
```bash
export ENVIRONMENT=mock
python main.py  # Uses all mocks
```

### **3. Production:**
```bash
export ENVIRONMENT=prod
python main.py  # Uses S3 + AWS DynamoDB + real APIs
```

## Benefits:

1. **Single Point of Change**: Change environment with one variable
2. **No Code Changes**: Same service code works in all environments
3. **Easy Testing**: Mock everything with one setting
4. **Gradual Migration**: Can mock specific services while keeping others real
5. **Environment Isolation**: Clear separation between environments
6. **Secret Management**: Environment-specific secrets
7. **Dependency Injection**: Clean separation of concerns

This approach gives you maximum flexibility with minimal code changes when switching between environments!