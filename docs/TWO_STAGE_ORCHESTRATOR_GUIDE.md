# Two-Stage Orchestrator Complete Guide

## 🎯 Architecture Overview

```
Root Orchestrator
├── Stage0 Orchestrator (SERP + Perplexity) → S3 Summary
└── Stage1 Orchestrator (4 Agents Sequential) → Individual Tables
    ├── Agent1: Deduplication → agent1_deduplication_results
    ├── Agent2: Relevance → agent2_relevance_results  
    ├── Agent3: Insights → agent3_insights_results
    └── Agent4: Implications → agent4_implications_results
```

## 🔄 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TWO-STAGE ORCHESTRATOR WORKFLOW                     │
└─────────────────────────────────────────────────────────────────────────────┘

1. API REQUEST
   ┌─────────────────┐
   │   POST Request  │
   │   /api/v1/      │──────┐
   │   market-       │      │
   │   intelligence/ │      │
   │   requests      │      │
   └─────────────────┘      │
                            │
2. ROOT ORCHESTRATOR        │
   ┌─────────────────┐      │
   │ Root            │◀─────┘
   │ Orchestrator    │
   │                 │
   │ Detects: SERP-  │──────┐
   │ Perplexity      │      │
   │ Workflow        │      │
   └─────────────────┘      │
                            │
3. STAGE0 ORCHESTRATOR      │
   ┌─────────────────┐      │
   │ Stage0          │◀─────┘
   │ Orchestrator    │
   │                 │
   │ SERP API        │──────┐
   │ ↓               │      │
   │ Perplexity API  │      │
   │ ↓               │      │
   │ S3 Summary      │      │
   └─────────────────┘      │
                            │
4. STAGE0 COMPLETION        │
   ┌─────────────────┐      │
   │ S3 Summary      │◀─────┘
   │ Created:        │
   │                 │──────┐
   │ s3://bucket/    │      │
   │ summaries/      │      │
   │ {request_id}/   │      │
   │ summary.json    │      │
   └─────────────────┘      │
                            │
5. STAGE1 ORCHESTRATOR      │
   ┌─────────────────┐      │
   │ Stage1          │◀─────┘
   │ Orchestrator    │
   │                 │
   │ Sequential      │──────┐
   │ Agent           │      │
   │ Processing      │      │
   └─────────────────┘      │
                            │
6. AGENT1 PROCESSING        │
   ┌─────────────────┐      │
   │ Agent1          │◀─────┘
   │ Deduplication   │
   │                 │
   │ Input: S3       │──────┐
   │ Output: Table   │      │
   │ agent1_         │      │
   │ deduplication_  │      │
   │ results         │      │
   └─────────────────┘      │
                            │
7. AGENT2 PROCESSING        │
   ┌─────────────────┐      │
   │ Agent2          │◀─────┘
   │ Relevance       │
   │                 │
   │ Input: S3       │──────┐
   │ Output: Table   │      │
   │ agent2_         │      │
   │ relevance_      │      │
   │ results         │      │
   └─────────────────┘      │
                            │
8. AGENT3 PROCESSING        │
   ┌─────────────────┐      │
   │ Agent3          │◀─────┘
   │ Insights        │
   │                 │
   │ Input: S3       │──────┐
   │ Output: Table   │      │
   │ agent3_         │      │
   │ insights_       │      │
   │ results         │      │
   └─────────────────┘      │
                            │
9. AGENT4 PROCESSING        │
   ┌─────────────────┐      │
   │ Agent4          │◀─────┘
   │ Implications    │
   │                 │
   │ Input: S3       │──────┐
   │ Output: Table   │      │
   │ agent4_         │      │
   │ implications_   │      │
   │ results         │      │
   └─────────────────┘      │
                            │
10. FINAL COMPLETION        │
    ┌─────────────────┐     │
    │ All Agents      │◀────┘
    │ Completed       │
    │                 │
    │ Status:         │
    │ COMPLETED       │
    │                 │
    │ Results in 4    │
    │ separate tables │
    └─────────────────┘
```

## 📋 Request Format

Your request format remains the same:

```json
{
    "project_id": "clinical_trials_test",
    "user_id": "test_user_003",
    "priority": "high",
    "processing_strategy": "table",
    "config": {
        "keywords": [
            "Obesity",
            "Weight loss",
            "Overweight",
            "Obese"
        ],
        "sources": [
            {
                "name": "ClinicalTrials",
                "type": "clinical",
                "url": "https://clinicaltrials.gov/"
            },
            {
                "name": "PubMed",
                "type": "clinical",
                "url": "https://pubmed.ncbi.nlm.nih.gov/"
            }
        ],
        "extraction_mode": "summary",
        "quality_threshold": 0.5,
        "date_range": {
            "start_date": "2025-08-01",
            "end_date": "2025-08-03"
        }
    }
}
```

## 🗃️ Database Tables Structure

### **Stage0 Results**
- **Table**: `market_intelligence_requests`
- **Purpose**: Root orchestrator request tracking
- **Schema**: 
  ```json
  {
    "request_id": "req_123456",
    "status": "completed",
    "stage0_results": { ... },
    "stage1_results": { ... }
  }
  ```

### **Stage1 Pipeline Tracking**
- **Table**: `stage1_pipeline_states`
- **Purpose**: Track Stage1 agent processing
- **Schema**:
  ```json
  {
    "request_id": "req_123456",
    "stage1_id": "stage1_req_123456_1704067200000",
    "status": "completed",
    "current_agent": "agent4_implications",
    "agent_states": { ... }
  }
  ```

### **Agent1 Results**
- **Table**: `agent1_deduplication_results`
- **Purpose**: Store deduplication results
- **Schema**:
  ```json
  {
    "request_id": "req_123456",
    "content_hash": "hash_abc123",
    "original_content": "...",
    "is_duplicate": false,
    "duplicate_group_id": "group_1",
    "similarity_score": 0.85
  }
  ```

### **Agent2 Results**
- **Table**: `agent2_relevance_results`
- **Purpose**: Store relevance scoring results
- **Schema**:
  ```json
  {
    "request_id": "req_123456",
    "content_id": "content_1",
    "content": "...",
    "relevance_score": 0.92,
    "relevance_category": "high",
    "keywords_matched": ["Obesity", "Weight loss"]
  }
  ```

### **Agent3 Results**
- **Table**: `agent3_insights_results`
- **Purpose**: Store generated insights
- **Schema**:
  ```json
  {
    "request_id": "req_123456",
    "insight_id": "insight_1",
    "insight_text": "Key finding about obesity treatment...",
    "insight_type": "trend",
    "confidence_score": 0.88,
    "source_content_ids": ["content_1", "content_3"]
  }
  ```

### **Agent4 Results**
- **Table**: `agent4_implications_results`
- **Purpose**: Store business implications
- **Schema**:
  ```json
  {
    "request_id": "req_123456",
    "implication_id": "impl_1",
    "implication_text": "Market opportunity in obesity drugs...",
    "impact_level": "high",
    "stakeholder_groups": ["pharma", "healthcare"],
    "related_insights": ["insight_1", "insight_2"]
  }
  ```

## 📊 Processing Timeline

```
Timeline for Complete 2-Stage Processing:

STAGE 0 (SERP + Perplexity)
T+0s    │ API Request Received
        │ ├─ Root Orchestrator detects SERP-Perplexity workflow
        │ └─ Stage0 Orchestrator starts
        │
T+2s    │ SERP API Processing
        │ ├─ Source 1: ClinicalTrials (5 URLs found)
        │ └─ Source 2: PubMed (3 URLs found)
        │
T+15s   │ Perplexity API Processing
        │ ├─ Extract content from 8 URLs
        │ └─ Quality filtering applied
        │
T+25s   │ Stage0 Completion
        │ ├─ S3 Summary created: s3://bucket/summaries/{request_id}/summary.json
        │ └─ Stage1 Orchestrator triggered
        │

STAGE 1 (4 Agents Sequential)
T+26s   │ Stage1 Orchestrator starts
        │ ├─ Reads S3 summary
        │ └─ Initializes agent processing queue
        │
T+27s   │ Agent1 (Deduplication) Processing
        │ ├─ Reads S3 summary data
        │ ├─ Identifies duplicate content
        │ ├─ Groups similar content
        │ └─ Stores results in agent1_deduplication_results
        │
T+35s   │ Agent2 (Relevance) Processing
        │ ├─ Reads S3 summary data
        │ ├─ Scores content relevance
        │ ├─ Categorizes by relevance level
        │ └─ Stores results in agent2_relevance_results
        │
T+45s   │ Agent3 (Insights) Processing
        │ ├─ Reads S3 summary data
        │ ├─ Generates insights from content
        │ ├─ Calculates confidence scores
        │ └─ Stores results in agent3_insights_results
        │
T+55s   │ Agent4 (Implications) Processing
        │ ├─ Reads S3 summary data
        │ ├─ Identifies business implications
        │ ├─ Maps to stakeholder groups
        │ └─ Stores results in agent4_implications_results
        │
T+65s   │ Complete Processing
        │ ├─ All 4 agents completed
        │ ├─ Final status: COMPLETED
        │ └─ Results available in 4 separate tables
```

## 🔍 File Structure

### **Stage1 Orchestrator Files**
```
app/agent_service_module/agents/stage1_orchestrator/
├── __init__.py                 # Package initialization
├── models.py                   # Stage1 models and enums
├── service.py                  # Main Stage1 orchestrator service
├── agent_processor.py          # Sequential agent processing logic
└── workflow_manager.py         # Pipeline state management
```

### **Key Models**
```python
# Stage1 Status Enum
class Stage1Status(str, Enum):
    PENDING = "pending"
    AGENT1_PROCESSING = "agent1_processing"  # Deduplication
    AGENT2_PROCESSING = "agent2_processing"  # Relevance
    AGENT3_PROCESSING = "agent3_processing"  # Insights
    AGENT4_PROCESSING = "agent4_processing"  # Implications
    COMPLETED = "completed"
    FAILED = "failed"

# Agent Types
class AgentType(str, Enum):
    DEDUPLICATION = "agent1_deduplication"
    RELEVANCE = "agent2_relevance"
    INSIGHTS = "agent3_insights"
    IMPLICATIONS = "agent4_implications"
```

## 🔄 Agent Processing Flow

### **Sequential Processing Pattern**
Each agent follows the same pattern:

1. **Input**: Reads S3 summary from Stage0
2. **Processing**: Applies agent-specific logic
3. **Output**: Stores results in agent-specific table
4. **Status**: Updates pipeline state

### **Agent Service Interface**
All agents implement the same interface:

```python
async def process_from_s3(
    request_id: str,
    s3_path: str,
    output_table: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process S3 data and store results in agent table
    
    Returns:
    {
        "success": True/False,
        "items_processed": 10,
        "items_successful": 8,
        "items_failed": 2,
        "errors": [...],
        "processing_time": 5.2
    }
    """
```

## 🚀 API Usage

### **Submit Request**
```bash
curl -X POST http://localhost:8005/api/v1/market-intelligence/requests \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "clinical_trials_test",
    "user_id": "test_user_003",
    "priority": "high",
    "processing_strategy": "table",
    "config": {
      "keywords": ["Obesity", "Weight loss"],
      "sources": [
        {
          "name": "ClinicalTrials",
          "type": "clinical",
          "url": "https://clinicaltrials.gov/"
        }
      ],
      "date_range": {
        "start_date": "2025-08-01",
        "end_date": "2025-08-03"
      }
    }
  }'
```

### **Check Status**
```bash
curl http://localhost:8005/api/v1/market-intelligence/requests/{request_id}/status
```

### **Get Results**
```bash
curl http://localhost:8005/api/v1/market-intelligence/requests/{request_id}/results
```

## 📋 Expected Response Format

```json
{
  "request_id": "req_20250101_123456",
  "status": "completed",
  "processing_stages": ["stage0_serp_perplexity", "stage1_agents"],
  "stage0_results": {
    "sources_processed": 2,
    "urls_found": 8,
    "content_extracted": 6,
    "s3_summary_path": "s3://bucket/summaries/req_20250101_123456/summary.json"
  },
  "stage1_results": {
    "stage1_id": "stage1_req_20250101_123456_1704067200000",
    "status": "completed",
    "agents_completed": 4,
    "overall_success_rate": 95.0,
    "total_processing_time": 40.5,
    "agent_results": {
      "agent1_deduplication": {
        "status": "completed",
        "items_processed": 6,
        "items_successful": 6,
        "processing_time": 8.2
      },
      "agent2_relevance": {
        "status": "completed", 
        "items_processed": 6,
        "items_successful": 5,
        "processing_time": 10.1
      },
      "agent3_insights": {
        "status": "completed",
        "items_processed": 5,
        "items_successful": 4,
        "processing_time": 12.3
      },
      "agent4_implications": {
        "status": "completed",
        "items_processed": 4,
        "items_successful": 4,
        "processing_time": 9.9
      }
    },
    "result_tables": {
      "agent1_deduplication": "agent1_deduplication_results",
      "agent2_relevance": "agent2_relevance_results",
      "agent3_insights": "agent3_insights_results",
      "agent4_implications": "agent4_implications_results"
    }
  }
}
```

## 🔍 Querying Agent Results

### **Get Deduplication Results**
```sql
SELECT * FROM agent1_deduplication_results 
WHERE request_id = 'req_20250101_123456'
```

### **Get Relevance Results**
```sql
SELECT * FROM agent2_relevance_results 
WHERE request_id = 'req_20250101_123456'
ORDER BY relevance_score DESC
```

### **Get Insights Results**
```sql
SELECT * FROM agent3_insights_results 
WHERE request_id = 'req_20250101_123456'
ORDER BY confidence_score DESC
```

### **Get Implications Results**
```sql
SELECT * FROM agent4_implications_results 
WHERE request_id = 'req_20250101_123456'
ORDER BY impact_level DESC
```

## 🎯 Key Benefits

✅ **Sequential Processing** - Agents process one by one as requested  
✅ **Individual Tables** - Each agent stores results in its own table  
✅ **S3 Summary Input** - All agents read from the same S3 summary  
✅ **No Aggregation** - No complex aggregation phase needed  
✅ **Simple Architecture** - Following stage0 orchestrator pattern  
✅ **Easy Monitoring** - Track each agent's progress individually  
✅ **Fault Tolerance** - Failed agents don't block others  
✅ **Scalable** - Each agent can be optimized independently  

## 🔧 Configuration

### **Agent Table Names**
```python
AGENT_TABLES = {
    "agent1_deduplication": "agent1_deduplication_results",
    "agent2_relevance": "agent2_relevance_results", 
    "agent3_insights": "agent3_insights_results",
    "agent4_implications": "agent4_implications_results"
}
```

### **Processing Timeouts**
```python
AGENT_TIMEOUTS = {
    "agent1_deduplication": 300,  # 5 minutes
    "agent2_relevance": 600,      # 10 minutes
    "agent3_insights": 900,       # 15 minutes
    "agent4_implications": 600    # 10 minutes
}
```

## 🎉 Summary

The Two-Stage Orchestrator successfully implements:

1. **Root Orchestrator** - Manages overall workflow
2. **Stage0 Orchestrator** - SERP + Perplexity → S3 Summary
3. **Stage1 Orchestrator** - 4 Agents → Individual Tables

Your request flows through both stages automatically, with each agent processing the S3 summary and storing results in its dedicated table. No complex aggregation needed! 🚀 