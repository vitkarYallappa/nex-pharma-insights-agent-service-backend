# DynamoDB Table Specifications for Root Orchestrator

This document provides complete DynamoDB table specifications for the Root Orchestrator system, including primary tables, indexes, and configuration details.

## Table Overview

The Root Orchestrator system requires **2 primary tables**:

1. **`market_intelligence_requests`** - Main requests table
2. **`request_processing_logs`** - Processing logs and audit trail (optional)

---

## 1. Market Intelligence Requests Table

### Table Configuration

```json
{
  "TableName": "market_intelligence_requests",
  "BillingMode": "PAY_PER_REQUEST",
  "AttributeDefinitions": [
    {
      "AttributeName": "request_id",
      "AttributeType": "S"
    },
    {
      "AttributeName": "user_id",
      "AttributeType": "S"
    },
    {
      "AttributeName": "project_id", 
      "AttributeType": "S"
    },
    {
      "AttributeName": "status",
      "AttributeType": "S"
    },
    {
      "AttributeName": "created_at",
      "AttributeType": "S"
    },
    {
      "AttributeName": "priority",
      "AttributeType": "S"
    },
    {
      "AttributeName": "processing_strategy",
      "AttributeType": "S"
    }
  ],
  "KeySchema": [
    {
      "AttributeName": "request_id",
      "KeyType": "HASH"
    }
  ]
}
```

### Global Secondary Indexes (GSIs)

#### GSI 1: User Index
```json
{
  "IndexName": "user-index",
  "KeySchema": [
    {
      "AttributeName": "user_id",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "created_at",
      "KeyType": "RANGE"
    }
  ],
  "Projection": {
    "ProjectionType": "ALL"
  }
}
```

#### GSI 2: Project Index
```json
{
  "IndexName": "project-index",
  "KeySchema": [
    {
      "AttributeName": "project_id",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "created_at",
      "KeyType": "RANGE"
    }
  ],
  "Projection": {
    "ProjectionType": "ALL"
  }
}
```

#### GSI 3: Status Index
```json
{
  "IndexName": "status-index",
  "KeySchema": [
    {
      "AttributeName": "status",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "created_at",
      "KeyType": "RANGE"
    }
  ],
  "Projection": {
    "ProjectionType": "ALL"
  }
}
```

#### GSI 4: Processing Strategy Index
```json
{
  "IndexName": "strategy-index",
  "KeySchema": [
    {
      "AttributeName": "processing_strategy",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "priority",
      "KeyType": "RANGE"
    }
  ],
  "Projection": {
    "ProjectionType": "ALL"
  }
}
```

### Item Structure

```json
{
  "request_id": "req_1757412789250_a08ac7ad",
  "project_id": "test-project-001",
  "user_id": "test-user-123",
  "request_type": "semaglutide_intelligence",
  "status": "pending",
  "status_message": null,
  "priority": "high",
  "processing_strategy": "table",
  
  "config": {
    "keywords": [
      "semaglutide",
      "tirzepatide", 
      "wegovy",
      "obesity drug",
      "weight loss medication",
      "GLP-1 receptor agonist",
      "diabetes treatment",
      "clinical trials obesity"
    ],
    "sources": [
      {
        "name": "FDA",
        "base_url": "https://www.fda.gov",
        "source_type": "government"
      },
      {
        "name": "NIH", 
        "base_url": "https://www.nih.gov",
        "source_type": "academic"
      },
      {
        "name": "ClinicalTrials.gov",
        "base_url": "https://clinicaltrials.gov", 
        "source_type": "clinical"
      }
    ],
    "extraction_mode": "summary",
    "quality_threshold": 0.7,
    "batch_size": 5,
    "max_retries": 2,
    "custom_params": {}
  },
  
  "created_at": "2024-01-09T15:43:09.250000",
  "updated_at": "2024-01-09T15:43:19.261000", 
  "started_at": "2024-01-09T15:43:09.251000",
  "completed_at": null,
  
  "progress": {
    "current_stage": "content_extraction",
    "percentage": 65.0,
    "urls_found": 15,
    "content_extracted": 12,
    "processing_errors": 1,
    "estimated_completion": "2024-01-09T15:45:00.000000",
    "last_updated": "2024-01-09T15:43:15.000000"
  },
  
  "results": {
    "report_path": "reports/semaglutide_intelligence_req_1757412789250_a08ac7ad.json",
    "summary": {
      "executive_summary": "Mock analysis completed successfully",
      "key_findings": ["Finding 1", "Finding 2"],
      "total_sources": 3,
      "total_content_items": 35
    },
    "execution_summary": {
      "total_urls_discovered": 15,
      "total_content_extracted": 12,
      "processing_duration": 10.0,
      "api_calls_made": 18,
      "success_rate": 94.6
    },
    "intelligence_data": {
      "regulatory_content": {
        "count": 12,
        "items": []
      },
      "clinical_content": {
        "count": 15, 
        "items": []
      },
      "academic_content": {
        "count": 8,
        "items": []
      }
    },
    "structured_outputs": [],
    "quality_metrics": {
      "average_confidence": 0.85,
      "high_quality_items": 28
    },
    "processing_metadata": {}
  },
  
  "errors": [
    "2024-01-09T15:43:12.000000: Failed to extract content from URL xyz"
  ],
  "warnings": [
    "2024-01-09T15:43:10.000000: Low confidence score for source ABC"
  ],
  
  "processing_metadata": {
    "test_run": true,
    "timestamp": "2024-01-09T15:43:09.250000",
    "status_history": [
      {
        "timestamp": "2024-01-09T15:43:09.250000",
        "old_status": "pending",
        "new_status": "processing",
        "message": "Started processing"
      }
    ]
  }
}
```

### Field Descriptions

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `request_id` | String | Unique request identifier (PK) | Yes |
| `project_id` | String | Project identifier | Yes |
| `user_id` | String | User who submitted request | Yes |
| `request_type` | String | Type of intelligence request | Yes |
| `status` | String | Current status (pending/processing/executing/completed/failed/cancelled) | Yes |
| `status_message` | String | Current status message | No |
| `priority` | String | Priority level (high/medium/low) | Yes |
| `processing_strategy` | String | Processing strategy (table/sqs) | Yes |
| `config` | Map | Request configuration object | Yes |
| `created_at` | String | ISO timestamp of creation | Yes |
| `updated_at` | String | ISO timestamp of last update | Yes |
| `started_at` | String | ISO timestamp when processing started | No |
| `completed_at` | String | ISO timestamp when processing completed | No |
| `progress` | Map | Progress tracking object | Yes |
| `results` | Map | Processing results object | No |
| `errors` | List | List of error messages | Yes |
| `warnings` | List | List of warning messages | Yes |
| `processing_metadata` | Map | Additional processing metadata | Yes |

---

## 2. Request Processing Logs Table (Optional)

### Table Configuration

```json
{
  "TableName": "request_processing_logs",
  "BillingMode": "PAY_PER_REQUEST",
  "AttributeDefinitions": [
    {
      "AttributeName": "log_id",
      "AttributeType": "S"
    },
    {
      "AttributeName": "request_id",
      "AttributeType": "S"
    },
    {
      "AttributeName": "timestamp",
      "AttributeType": "S"
    }
  ],
  "KeySchema": [
    {
      "AttributeName": "log_id",
      "KeyType": "HASH"
    }
  ]
}
```

### Global Secondary Index

```json
{
  "IndexName": "request-logs-index",
  "KeySchema": [
    {
      "AttributeName": "request_id",
      "KeyType": "HASH"
    },
    {
      "AttributeName": "timestamp", 
      "KeyType": "RANGE"
    }
  ],
  "Projection": {
    "ProjectionType": "ALL"
  }
}
```

### Item Structure

```json
{
  "log_id": "log_1757412789250_001",
  "request_id": "req_1757412789250_a08ac7ad",
  "timestamp": "2024-01-09T15:43:09.250000",
  "log_level": "INFO",
  "message": "Request processing started",
  "stage": "initialization",
  "metadata": {
    "worker_id": "table_processor_001",
    "processing_node": "node-1"
  }
}
```

---

## DynamoDB Creation Scripts

### AWS CLI Commands

```bash
# Create main requests table
aws dynamodb create-table \
  --table-name market_intelligence_requests \
  --attribute-definitions \
    AttributeName=request_id,AttributeType=S \
    AttributeName=user_id,AttributeType=S \
    AttributeName=project_id,AttributeType=S \
    AttributeName=status,AttributeType=S \
    AttributeName=created_at,AttributeType=S \
    AttributeName=priority,AttributeType=S \
    AttributeName=processing_strategy,AttributeType=S \
  --key-schema \
    AttributeName=request_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    'IndexName=user-index,KeySchema=[{AttributeName=user_id,KeyType=HASH},{AttributeName=created_at,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
    'IndexName=project-index,KeySchema=[{AttributeName=project_id,KeyType=HASH},{AttributeName=created_at,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
    'IndexName=status-index,KeySchema=[{AttributeName=status,KeyType=HASH},{AttributeName=created_at,KeyType=RANGE}],Projection={ProjectionType=ALL}' \
    'IndexName=strategy-index,KeySchema=[{AttributeName=processing_strategy,KeyType=HASH},{AttributeName=priority,KeyType=RANGE}],Projection={ProjectionType=ALL}'

# Create logs table (optional)
aws dynamodb create-table \
  --table-name request_processing_logs \
  --attribute-definitions \
    AttributeName=log_id,AttributeType=S \
    AttributeName=request_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=log_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --global-secondary-indexes \
    'IndexName=request-logs-index,KeySchema=[{AttributeName=request_id,KeyType=HASH},{AttributeName=timestamp,KeyType=RANGE}],Projection={ProjectionType=ALL}'
```

### Python Boto3 Script

```python
import boto3

def create_market_intelligence_tables():
    dynamodb = boto3.client('dynamodb')
    
    # Main requests table
    requests_table = {
        'TableName': 'market_intelligence_requests',
        'AttributeDefinitions': [
            {'AttributeName': 'request_id', 'AttributeType': 'S'},
            {'AttributeName': 'user_id', 'AttributeType': 'S'},
            {'AttributeName': 'project_id', 'AttributeType': 'S'},
            {'AttributeName': 'status', 'AttributeType': 'S'},
            {'AttributeName': 'created_at', 'AttributeType': 'S'},
            {'AttributeName': 'priority', 'AttributeType': 'S'},
            {'AttributeName': 'processing_strategy', 'AttributeType': 'S'}
        ],
        'KeySchema': [
            {'AttributeName': 'request_id', 'KeyType': 'HASH'}
        ],
        'BillingMode': 'PAY_PER_REQUEST',
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'user-index',
                'KeySchema': [
                    {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            },
            {
                'IndexName': 'project-index',
                'KeySchema': [
                    {'AttributeName': 'project_id', 'KeyType': 'HASH'},
                    {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            },
            {
                'IndexName': 'status-index',
                'KeySchema': [
                    {'AttributeName': 'status', 'KeyType': 'HASH'},
                    {'AttributeName': 'created_at', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            },
            {
                'IndexName': 'strategy-index',
                'KeySchema': [
                    {'AttributeName': 'processing_strategy', 'KeyType': 'HASH'},
                    {'AttributeName': 'priority', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            }
        ]
    }
    
    try:
        response = dynamodb.create_table(**requests_table)
        print(f"Created table: {response['TableDescription']['TableName']}")
    except Exception as e:
        print(f"Error creating requests table: {e}")

if __name__ == "__main__":
    create_market_intelligence_tables()
```

---

## Query Patterns

### Common Query Operations

1. **Get Request by ID**
   ```python
   response = dynamodb.get_item(
       TableName='market_intelligence_requests',
       Key={'request_id': {'S': 'req_1757412789250_a08ac7ad'}}
   )
   ```

2. **Get Requests by User**
   ```python
   response = dynamodb.query(
       TableName='market_intelligence_requests',
       IndexName='user-index',
       KeyConditionExpression='user_id = :user_id',
       ExpressionAttributeValues={':user_id': {'S': 'test-user-123'}}
   )
   ```

3. **Get Pending Requests**
   ```python
   response = dynamodb.query(
       TableName='market_intelligence_requests',
       IndexName='status-index',
       KeyConditionExpression='#status = :status',
       ExpressionAttributeNames={'#status': 'status'},
       ExpressionAttributeValues={':status': {'S': 'pending'}}
   )
   ```

4. **Get Requests by Priority for Table Strategy**
   ```python
   response = dynamodb.query(
       TableName='market_intelligence_requests',
       IndexName='strategy-index',
       KeyConditionExpression='processing_strategy = :strategy',
       ExpressionAttributeValues={':strategy': {'S': 'table'}},
       ScanIndexForward=False  # Descending order by priority
   )
   ```

---

## Performance Considerations

### Capacity Planning
- **Read Capacity**: Estimate based on API request volume
- **Write Capacity**: Consider request submission rate + status updates
- **GSI Capacity**: Factor in query patterns for each index

### Best Practices
1. Use **PAY_PER_REQUEST** billing for variable workloads
2. Enable **Point-in-Time Recovery** for production
3. Set up **CloudWatch alarms** for throttling
4. Consider **DynamoDB Accelerator (DAX)** for read-heavy workloads
5. Implement **TTL** for automatic cleanup of old completed requests

### TTL Configuration
```python
# Enable TTL on completed requests (optional)
dynamodb.update_time_to_live(
    TableName='market_intelligence_requests',
    TimeToLiveSpecification={
        'AttributeName': 'ttl',
        'Enabled': True
    }
)
```

---

## Environment-Specific Table Names

### Development
- `dev-market-intelligence-requests`
- `dev-request-processing-logs`

### Staging  
- `staging-market-intelligence-requests`
- `staging-request-processing-logs`

### Production
- `prod-market-intelligence-requests`
- `prod-request-processing-logs`

---

This specification provides everything needed to create and manage the DynamoDB tables for your Root Orchestrator system. The tables are designed for optimal performance with the query patterns used by the application. 