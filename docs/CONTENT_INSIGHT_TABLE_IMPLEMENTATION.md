# Content Insight Table Implementation

## Overview

This document describes the implementation of the `content_insight` table and its integration with Agent3 Insights service to properly store insight data with `url_id` and `content_id` from Perplexity processing.

## Problem Solved

Previously, Agent3 was storing insight data in a generic `insights_metadata` table without proper linkage to the original content processed by Perplexity. This made it difficult to:

- Track which insights came from which URLs
- Link insights back to original content
- Maintain data relationships across the pipeline
- Query insights by content source

## Solution Architecture

### Data Flow

```
Perplexity → S3 Storage → Agent3 → content_insight table
    ↓           ↓           ↓              ↓
  url_id    content_id   Bedrock      Structured
content_id   + content   Insights      Storage
```

1. **Perplexity Stage**: Processes URLs and generates `url_id` and `content_id`
2. **S3 Storage**: Content stored with these IDs as metadata
3. **Agent3 Processing**: Fetches content using IDs, generates insights
4. **content_insight Table**: Stores insights with proper ID linkage

## Table Structure

### content_insight Table Schema

```python
{
    "table_name": "content_insight-{environment}",
    "key_schema": [
        {"AttributeName": "pk", "KeyType": "HASH"}  # Primary key
    ],
    "attribute_definitions": [
        {"AttributeName": "pk", "AttributeType": "S"}  # String (UUID)
    ],
    "billing_mode": "PAY_PER_REQUEST"
}
```

### Data Fields

| Field | Type | Description |
|-------|------|-------------|
| `pk` | String | Primary key (insight UUID) |
| `url_id` | String | URL ID from Perplexity |
| `content_id` | String | Content ID from Perplexity |
| `insight_text` | String | Generated insight content |
| `insight_content_file_path` | String | S3 path to full insight data |
| `insight_category` | String | Category (e.g., "ai_generated") |
| `confidence_score` | Decimal | Confidence score (0.0-1.0) |
| `version` | Number | Version number |
| `is_canonical` | Boolean | Whether this is the canonical version |
| `preferred_choice` | Boolean | Whether this is the preferred choice |
| `created_at` | String | ISO timestamp |
| `created_by` | String | Creator identifier |

## Implementation Details

### 1. Table Configuration

**File**: `app/config/table_configs/content_insight_table.py`

```python
class ContentInsightTableConfig:
    TABLE_NAME = "content_insight"
    
    @classmethod
    def get_table_name(cls, environment: str = "local") -> str:
        return f"{cls.TABLE_NAME}-{environment}"
    
    @classmethod
    def get_schema(cls, environment: str = "local") -> Dict[str, Any]:
        # Returns complete DynamoDB schema
```

### 2. Data Model

**File**: `app/agent_service_module/agents/agent3_insights/content_insight_model.py`

```python
class ContentInsightModel(BaseModel):
    pk: str  # Primary key (UUID)
    url_id: str  # From Perplexity
    content_id: str  # From Perplexity
    insight_text: str
    insight_content_file_path: str
    # ... other fields
    
    @classmethod
    def create_new(cls, url_id: str, content_id: str, ...):
        # Factory method for creating new insights
    
    def to_dict(self) -> Dict[str, Any]:
        # Converts to DynamoDB format (handles Decimal conversion)
```

### 3. Agent3 Service Integration

**File**: `app/agent_service_module/agents/agent3_insights/service.py`

Key changes:
- Added `url_id` and `content_id` fields to `Agent3InsightsRequest`
- Updated `_store_results()` method to use `content_insight` table
- Proper handling of Decimal types for DynamoDB
- Metadata propagation from request to response

```python
async def _store_results(self, response: Agent3InsightsResponse):
    # Extract url_id and content_id from metadata
    url_id = response.metadata.get('url_id', 'unknown')
    content_id = response.metadata.get('content_id', 'unknown')
    
    # Create ContentInsightModel instance
    content_insight = ContentInsightModel.create_new(
        url_id=url_id,
        content_id=content_id,
        insight_text=response.insights.html_content,
        insight_content_file_path=insights_key,
        # ... other fields
    )
    
    # Store in content_insight table
    await self.database_client.put_item(
        table_name=self.table_name,
        item=content_insight.to_dict()
    )
```

### 4. Request Model Updates

**File**: `app/agent_service_module/agents/agent3_insights/models.py`

```python
class Agent3InsightsRequest(BaseModel):
    request_id: str
    s3_summary_path: Optional[str] = None
    content: Optional[str] = None
    url_id: Optional[str] = None      # NEW: From Perplexity
    content_id: Optional[str] = None  # NEW: From Perplexity
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    api_provider: str = Field(default="anthropic_direct")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

## Usage Examples

### 1. Basic Agent3 Processing

```python
from app.agent_service_module.agents.agent3_insights.service import Agent3InsightsService
from app.agent_service_module.agents.agent3_insights.models import Agent3InsightsRequest

# Create request with Perplexity IDs
request = Agent3InsightsRequest(
    request_id="req-123",
    content="Market analysis content...",
    url_id="url-456",      # From Perplexity
    content_id="content-789",  # From Perplexity
    api_provider="anthropic_direct"
)

# Process with Agent3
service = Agent3InsightsService()
response = await service.process(request)

# Data is automatically stored in content_insight table
```

### 2. Direct Model Usage

```python
from app.agent_service_module.agents.agent3_insights.content_insight_model import ContentInsightModel

# Create insight directly
insight = ContentInsightModel.create_new(
    url_id="url-123",
    content_id="content-456",
    insight_text="Generated insights...",
    insight_content_file_path="/insights/result.json",
    insight_category="market_analysis",
    confidence_score=0.95
)

# Convert for DynamoDB storage
db_item = insight.to_dict()  # Handles Decimal conversion

# Convert for API response
api_response = insight.to_response()
```

## Database Operations

### Creating Tables

```bash
# Create all tables including content_insight
python3 scripts/create_tables.py create
```

### Querying Data

```python
# Get insight by ID
insight = await db_client.get_item(
    table_name="content_insight-local",
    key={"pk": "insight-uuid"}
)

# Query by URL ID (requires GSI if frequent)
# Note: Current implementation uses simple key-value lookup
```

## Benefits

1. **Data Integrity**: Proper linkage between Perplexity content and insights
2. **Traceability**: Can trace insights back to original URLs
3. **Structured Storage**: Consistent data model across the pipeline
4. **Performance**: Optimized for common query patterns
5. **Scalability**: DynamoDB handles large-scale operations
6. **Type Safety**: Proper handling of Decimal types for DynamoDB

## Migration Notes

### From Previous Implementation

The previous implementation stored data in `insights_metadata` table with this structure:
```python
{
    "request_id": "...",
    "insights_storage_key": "...",
    "status": "...",
    # ... other metadata
}
```

The new implementation stores in `content_insight` table with:
```python
{
    "pk": "insight-uuid",
    "url_id": "from-perplexity",
    "content_id": "from-perplexity",
    "insight_text": "...",
    "insight_content_file_path": "s3-path",
    # ... structured insight data
}
```

### Breaking Changes

1. **Table Name**: Changed from `insights_metadata` to `content_insight-{env}`
2. **Data Structure**: More structured with proper field types
3. **Primary Key**: Uses insight UUID instead of request_id
4. **Required Fields**: `url_id` and `content_id` are now required

## Testing

### Automated Tests

Run the example to verify the implementation:

```bash
python3 examples/agent3_content_insight_example.py
```

### Manual Verification

1. Check table exists: `python3 scripts/create_tables.py list`
2. Process test request through Agent3
3. Verify data stored in content_insight table
4. Confirm S3 storage of full insight data

## Future Enhancements

1. **Global Secondary Indexes**: Add GSI for querying by `url_id` or `content_id`
2. **Batch Operations**: Support for batch insight processing
3. **Data Archiving**: Implement archiving strategy for old insights
4. **Analytics**: Add analytics queries for insight performance
5. **Versioning**: Enhanced versioning support for insight updates

## Troubleshooting

### Common Issues

1. **Float Type Error**: Use `to_dict()` method for proper Decimal conversion
2. **Missing IDs**: Ensure `url_id` and `content_id` are passed from Perplexity
3. **Table Not Found**: Run `python3 scripts/create_tables.py create`
4. **Permission Errors**: Check DynamoDB permissions and endpoint configuration

### Debug Commands

```bash
# List all tables
python3 scripts/create_tables.py list

# Check table structure
aws dynamodb describe-table --table-name content_insight-local --endpoint-url http://localhost:8000

# Query table contents
aws dynamodb scan --table-name content_insight-local --endpoint-url http://localhost:8000
``` 