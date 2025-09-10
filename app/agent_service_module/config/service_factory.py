from typing import Union, Any
from ...config.unified_settings import settings

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
        try:
            from ..agents.stage0_serp.serp_api import SerpAPI
            return SerpAPI()
        except Exception as e:
            # Enhanced error reporting for SERP client creation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to create SERP client: {e}")
            logger.error(f"Settings SERP_API_KEY available: {bool(getattr(settings, 'SERP_API_KEY', None))}")
            
            # Re-raise with more context
            raise Exception(f"Service initialization failed: {str(e)}")
    
    @staticmethod
    def get_storage_client():
        # Use S3Client for both S3 and MinIO (MinIO is S3-compatible)
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