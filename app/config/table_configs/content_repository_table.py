"""
Content Repository Table Configuration
Dedicated configuration for the content_repository table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ContentRepositoryTableConfig:
    """Configuration for the content_repository table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "content_repository"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # content_id (UUID) -> pk (String) - Primary key
    # request_id (UUID) -> request_id (String) - Request ID reference
    # project_id (UUID) -> project_id (String) - Project ID reference
    # canonical_url (String) -> canonical_url (String) - Canonical URL
    # title (String) -> title (String) - Content title
    # content_hash (String) -> content_hash (String) - Content hash
    # source_type (String) -> source_type (String) - Source type
    # version (Integer) -> version (Number) - Version number
    # is_canonical (Boolean) -> is_canonical (Boolean) - Canonical status
    # relevance_type (String) -> relevance_type (String) - Relevance type
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # updated_at (DateTime) -> updated_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for content_repository table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to SQLAlchemy 'content_id' field
                "KeyType": "HASH"  # Partition key
            }
        ],
        "attribute_definitions": [
            {
                "AttributeName": "pk",
                "AttributeType": "S"  # String (UUID as string)
            }
        ],
        "billing_mode": "PAY_PER_REQUEST"
    }
    
    # Sample item structure (for reference - not used in table creation)
    SAMPLE_ITEM = {
        "pk": "123e4567-e89b-12d3-a456-426614174000",  # Primary key (UUID as string)
        "request_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Request ID reference
        "project_id": "456e7890-f12a-34b5-c678-901234567def",  # Project ID reference
        "canonical_url": "https://example.com/article/123",  # Canonical URL
        "title": "Advanced Machine Learning Techniques in Healthcare",  # Content title
        "content_hash": "sha256:a1b2c3d4e5f6...",  # Content hash
        "source_type": "web_article",  # Source type
        "version": 1,  # Version number
        "is_canonical": True,  # Canonical status
        "relevance_type": "high",  # Relevance type
        "created_at": "2024-12-01T10:00:00Z",  # ISO timestamp
        "updated_at": "2024-12-01T12:00:00Z"   # ISO timestamp
    }
    
    @classmethod
    def get_table_name(cls, environment: str = "local") -> str:
        """Get full table name with environment suffix"""
        return f"{cls.TABLE_NAME}-{environment}"
    
    @classmethod
    def get_schema(cls, environment: str = "local") -> Dict[str, Any]:
        """Get complete schema with environment-specific table name"""
        schema = cls.SCHEMA.copy()
        schema["table_name"] = cls.get_table_name(environment)
        return schema
    
    @classmethod
    def get_description(cls) -> str:
        """Get table description"""
        return "Content repository table with primary key only - simple and fast" 