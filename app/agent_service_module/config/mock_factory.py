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