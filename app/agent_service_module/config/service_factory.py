from typing import Union, Any
from .settings import settings

class ServiceFactory:
    @staticmethod
    def get_openai_client():
        from ..agents.agent1_deduplication.openai_api import OpenAIAPI
        return OpenAIAPI()
    
    @staticmethod
    def get_bedrock_client():
        from ..agents.agent1_deduplication.bedrock_api import BedrockAPI
        return BedrockAPI()
    
    @staticmethod
    def get_perplexity_client():
        from ..agents.stage0_perplexity.perplexity_api import PerplexityAPI
        return PerplexityAPI()
    
    @staticmethod
    def get_serp_client():
        from ..agents.stage0_serp.serp_api import SerpAPI
        return SerpAPI()
    
    @staticmethod
    def get_storage_client():
        if settings.STORAGE_TYPE == "minio":
            from ..shared.storage.minio_client import MinioClient
            return MinioClient()
        else:
            from ..shared.storage.s3_client import S3Client
            return S3Client()
    
    @staticmethod
    def get_database_client():
        from ..shared.database.dynamodb_client import DynamoDBClient
        return DynamoDBClient()
    
    @staticmethod
    def get_embedding_client():
        from ..agents.agent1_deduplication.embedding_api import EmbeddingAPI
        return EmbeddingAPI() 