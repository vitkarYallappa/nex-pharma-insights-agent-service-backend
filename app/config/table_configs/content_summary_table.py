"""
Content Summary Table Configuration
Dedicated configuration for the content_summary table schema and settings
Matches SQLAlchemy schema structure with DynamoDB NoSQL approach
"""

from typing import Dict, Any

class ContentSummaryTableConfig:
    """Configuration for the content_summary table"""
    
    # Table name (without environment suffix)
    TABLE_NAME = "content_summary"
    
    # Field mapping from SQLAlchemy to DynamoDB
    # SQLAlchemy -> DynamoDB mapping:
    # summary_id (UUID) -> pk (String) - Primary key
    # url_id (UUID) -> url_id (String) - URL ID reference
    # content_id (UUID) -> content_id (String) - Content ID reference
    # summary_text (String) -> summary_text (String) - Summary text
    # summary_content_file_path (String) -> summary_content_file_path (String) - File path
    # confidence_score (Numeric) -> confidence_score (Number) - Confidence score
    # version (Integer) -> version (Number) - Version number
    # is_canonical (Boolean) -> is_canonical (Boolean) - Canonical flag
    # preferred_choice (Boolean) -> preferred_choice (Boolean) - Preferred choice flag
    # created_at (DateTime) -> created_at (String) - ISO timestamp
    # created_by (String) -> created_by (String) - Creator identifier
    
    # Complete DynamoDB schema for content_summary table
    SCHEMA = {
        "table_name": TABLE_NAME,
        "key_schema": [
            {
                "AttributeName": "pk",  # Maps to SQLAlchemy 'summary_id' field
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
        "url_id": "987fcdeb-51a2-43d7-8f9e-123456789abc",  # URL ID reference
        "content_id": "456e7890-f12a-34b5-c678-901234567def",  # Content ID reference
        "summary_text": "This article discusses the latest pharmaceutical market trends and insights for 2024, highlighting key developments in drug discovery and regulatory changes.",  # Summary text
        "summary_content_file_path": "/content/summaries/2024/pharma-insights-summary.txt",  # File path
        "confidence_score": 0.92,  # Confidence score (0.00-1.00)
        "version": 1,  # Version number
        "is_canonical": True,  # Canonical flag
        "preferred_choice": True,  # Preferred choice flag
        "created_at": "2024-12-01T10:00:00Z",  # ISO timestamp
        "created_by": "ai-summarizer-v2"  # Creator identifier
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
        return "Content summary table with primary key only - simple and fast" 