"""
Content URL Mapping Table Configuration
Dedicated configuration for the content_url_mapping table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ContentUrlMappingTableConfig:
    """Configuration for the content_url_mapping table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "content_url_mapping"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # url_id (UUID) -> pk (String) - Primary key
    # discovered_url (String) -> discovered_url (String) - Discovered URL
    # title (String) -> title (String) - Content title
    # content_id (UUID) -> content_id (String) - Content ID reference
    # source_domain (String) -> source_domain (String) - Source domain
    # is_canonical (Boolean) -> is_canonical (Boolean) - Canonical flag
    # dedup_confidence (Numeric) -> dedup_confidence (Number) - Deduplication confidence score
    # dedup_method (String) -> dedup_method (String) - Deduplication method
    # discovered_at (DateTime) -> discovered_at (String) - ISO timestamp
    
    # Complete DynamoDB schema for content_url_mapping table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to SQLAlchemy 'url_id' field
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
        "discovered_url": "https://example.com/article/pharma-insights-2024",  # Discovered URL
        "title": "Pharmaceutical Market Insights 2024",  # Content title
        "content_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # Content ID reference
        "source_domain": "example.com",  # Source domain
        "is_canonical": True,  # Canonical flag
        "dedup_confidence": 0.95,  # Deduplication confidence score (0.00-1.00)
        "dedup_method": "content_hash",  # Deduplication method
        "discovered_at": "2024-12-01T10:00:00Z"  # ISO timestamp
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
        return "Content URL mapping table with primary key only - simple and fast" 