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