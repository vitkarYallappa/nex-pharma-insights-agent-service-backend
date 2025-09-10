# Root Orchestrator Developer Guide

## Overview

The **Root Orchestrator** is the top-level request management system that sits above the existing `stage0_orchestrator` to handle user-submitted market intelligence requests. It provides two processing strategies: **Table-based** and **SQS-based** processing.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ROOT ORCHESTRATOR SYSTEM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────────────────────────────────────┐ │
│  │   User Request  │───▶│            Root Orchestrator                    │ │
│  │   (API/UI)      │    │                                                 │ │
│  └─────────────────┘    │  ┌─────────────────────────────────────────────┐│ │
│                         │  │         Strategy Pattern                    ││ │
│                         │  │                                             ││ │
│                         │  │  ┌─────────────┐    ┌─────────────────────┐││ │
│                         │  │  │Table Strategy│    │   SQS Strategy      │││ │
│                         │  │  │             │    │                     │││ │
│                         │  │  │- Poll Table │    │- Queue Messages     │││ │
│                         │  │  │- Process    │    │- Consumer Workers   │││ │
│                         │  │  │- Update     │    │- Dead Letter Queue  │││ │
│                         │  │  └─────────────┘    └─────────────────────┘││ │
│                         │  └─────────────────────────────────────────────┘│ │
│                         └─────────────────────────────────────────────────┘ │
│                                                │                             │
│                                                ▼                             │
│                         ┌─────────────────────────────────────────────────┐ │
│                         │        Market Intelligence Workflow             │ │
│                         │                                                 │ │
│                         │  ┌─────────────────────────────────────────────┐│ │
│                         │  │           stage0_orchestrator               ││ │
│                         │  │                                             ││ │
│                         │  │  SERP → Perplexity → Aggregation → Report  ││ │
│                         │  └─────────────────────────────────────────────┘│ │
│                         └─────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 Core Concepts

### 1. **Request Lifecycle**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   PENDING   │───▶│ PROCESSING  │───▶│  EXECUTING  │───▶│ COMPLETED/  │───▶│   STORED    │
│             │    │             │    │             │    │   FAILED    │    │             │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### 2. **Processing Strategies**

The system uses the **Strategy Pattern** to support different processing approaches:

- **Table Strategy**: Database polling-based processing
- **SQS Strategy**: Message queue-based processing

### 3. **Request Types**

Currently supports:
- **Semaglutide Market Intelligence**: Hardcoded workflow for Semaglutide/Tirzepatide monitoring
- **Future**: Extensible for other pharmaceutical intelligence workflows

## 📊 Table-Based Processing Approach

### **How It Works**

1. **Request Submission**: User submits request via API
2. **Database Storage**: Request stored in `market_intelligence_requests` table
3. **Background Polling**: Processor polls table for `PENDING` requests
4. **Sequential Processing**: Processes one request at a time
5. **Status Updates**: Updates request status in real-time
6. **Result Storage**: Stores results and updates final status

### **Database Schema**

```sql
-- market_intelligence_requests table
{
  "request_id": "string (PK)",
  "project_id": "string",
  "user_id": "string", 
  "request_type": "semaglutide_intelligence",
  "status": "PENDING|PROCESSING|EXECUTING|COMPLETED|FAILED",
  "priority": "HIGH|MEDIUM|LOW",
  "configuration": {
    "keywords": [...],
    "sources": [...],
    "custom_params": {...}
  },
  "created_at": "timestamp",
  "started_at": "timestamp",
  "completed_at": "timestamp",
  "progress": {
    "current_stage": "string",
    "percentage": "number",
    "urls_found": "number",
    "content_extracted": "number"
  },
  "results": {
    "report_path": "string",
    "summary": {...}
  },
  "errors": [...],
  "processing_metadata": {...}
}
```

### **Table Processing Flow**

```python
# Pseudo-code for table processing
while True:
    # 1. Poll for pending requests
    pending_requests = db.query(
        table="market_intelligence_requests",
        filter="status = PENDING",
        order_by="priority DESC, created_at ASC",
        limit=1
    )
    
    if pending_requests:
        request = pending_requests[0]
        
        # 2. Update status to PROCESSING
        db.update(request.id, {"status": "PROCESSING", "started_at": now()})
        
        try:
            # 3. Execute market intelligence workflow
            result = await market_intelligence_service.execute(request.configuration)
            
            # 4. Update with results
            db.update(request.id, {
                "status": "COMPLETED",
                "completed_at": now(),
                "results": result
            })
            
        except Exception as e:
            # 5. Handle errors
            db.update(request.id, {
                "status": "FAILED", 
                "completed_at": now(),
                "errors": [str(e)]
            })
    
    # 6. Wait before next poll
    await asyncio.sleep(polling_interval)
```

### **Advantages of Table Approach**

✅ **Simple Implementation**: Direct database operations  
✅ **Easy Debugging**: All state visible in database  
✅ **Immediate Consistency**: Real-time status updates  
✅ **No Additional Infrastructure**: Uses existing database  
✅ **Transaction Support**: ACID compliance for status updates  

### **Disadvantages of Table Approach**

❌ **Polling Overhead**: Continuous database queries  
❌ **Single Point Processing**: One request at a time  
❌ **Scaling Limitations**: Database becomes bottleneck  
❌ **Resource Usage**: Constant polling consumes resources  

## 🚀 SQS-Based Processing Approach

### **How It Works**

1. **Request Submission**: User submits request via API
2. **Queue Message**: Request sent to SQS queue
3. **Consumer Workers**: Multiple workers consume messages
4. **Parallel Processing**: Multiple requests processed simultaneously
5. **Status Updates**: Workers update database with progress
6. **Dead Letter Queue**: Failed messages moved to DLQ for retry

### **SQS Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────────────────┐
│   User Request  │───▶│  Main SQS Queue │───▶│     Consumer Workers        │
└─────────────────┘    └─────────────────┘    │                             │
                                              │  ┌─────────┐ ┌─────────┐    │
                                              │  │Worker 1 │ │Worker 2 │    │
                                              │  └─────────┘ └─────────┘    │
                                              │  ┌─────────┐ ┌─────────┐    │
                                              │  │Worker 3 │ │Worker N │    │
                                              │  └─────────┘ └─────────┘    │
                                              └─────────────────────────────┘
                                                              │
                                                              ▼
                              ┌─────────────────┐    ┌─────────────────┐
                              │ Dead Letter     │◀───│   Failed        │
                              │ Queue (DLQ)     │    │   Messages      │
                              └─────────────────┘    └─────────────────┘
```

### **SQS Message Structure**

```json
{
  "request_id": "req_20241201_123456",
  "project_id": "proj_semaglutide_001",
  "user_id": "user_analyst_001",
  "request_type": "semaglutide_intelligence",
  "priority": "HIGH",
  "configuration": {
    "keywords": ["semaglutide", "tirzepatide", "wegovy"],
    "sources": [
      {"name": "FDA", "type": "regulatory"},
      {"name": "NIH", "type": "academic"},
      {"name": "ClinicalTrials.gov", "type": "clinical"}
    ],
    "extraction_mode": "summary",
    "quality_threshold": 0.7
  },
  "metadata": {
    "submitted_at": "2024-12-01T12:34:56Z",
    "retry_count": 0,
    "max_retries": 3
  }
}
```

### **SQS Processing Flow**

```python
# Pseudo-code for SQS processing
async def sqs_consumer_worker():
    while True:
        # 1. Receive messages from SQS
        messages = sqs.receive_messages(
            queue_url=MAIN_QUEUE_URL,
            max_messages=1,
            wait_time=20  # Long polling
        )
        
        for message in messages:
            try:
                # 2. Parse message
                request_data = json.loads(message.body)
                
                # 3. Update status to PROCESSING
                await db.update(request_data['request_id'], {
                    "status": "PROCESSING",
                    "started_at": now()
                })
                
                # 4. Execute workflow
                result = await market_intelligence_service.execute(
                    request_data['configuration']
                )
                
                # 5. Update with results
                await db.update(request_data['request_id'], {
                    "status": "COMPLETED",
                    "completed_at": now(),
                    "results": result
                })
                
                # 6. Delete message from queue
                message.delete()
                
            except Exception as e:
                # 7. Handle retry logic
                retry_count = request_data.get('metadata', {}).get('retry_count', 0)
                max_retries = request_data.get('metadata', {}).get('max_retries', 3)
                
                if retry_count < max_retries:
                    # Retry: Send back to queue with increased retry count
                    request_data['metadata']['retry_count'] = retry_count + 1
                    sqs.send_message(
                        queue_url=MAIN_QUEUE_URL,
                        message_body=json.dumps(request_data),
                        delay_seconds=exponential_backoff(retry_count)
                    )
                else:
                    # Send to Dead Letter Queue
                    sqs.send_message(
                        queue_url=DLQ_URL,
                        message_body=json.dumps(request_data)
                    )
                    
                    # Update status to FAILED
                    await db.update(request_data['request_id'], {
                        "status": "FAILED",
                        "completed_at": now(),
                        "errors": [str(e)]
                    })
                
                # Delete original message
                message.delete()
```

### **Advantages of SQS Approach**

✅ **High Scalability**: Multiple concurrent workers  
✅ **Built-in Retry**: Automatic retry with exponential backoff  
✅ **Fault Tolerance**: Dead Letter Queue for failed messages  
✅ **Decoupling**: Loose coupling between components  
✅ **Auto-scaling**: Workers can scale based on queue depth  
✅ **Durability**: Messages persisted until processed  

### **Disadvantages of SQS Approach**

❌ **Additional Infrastructure**: Requires SQS setup and management  
❌ **Complexity**: More moving parts to monitor  
❌ **Cost**: SQS usage costs (though minimal)  
❌ **Eventual Consistency**: Status updates may have slight delays  

## 📁 Required Files and Implementation Guide

### **File Structure Overview**

```
app/
├── root_orchestrator/
│   ├── __init__.py
│   ├── models.py                           # Request models and enums
│   ├── root_orchestrator_service.py        # Main orchestrator service
│   ├── config.py                          # Configuration settings
│   ├── status_tracker.py                  # Status management
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── base_strategy.py               # Abstract base strategy
│   │   ├── table_strategy.py              # Table-based processing
│   │   └── sqs_strategy.py                # SQS-based processing
│   └── workers/
│       ├── __init__.py
│       ├── table_processor.py             # Table polling worker
│       └── sqs_consumer.py                # SQS consumer worker
├── controllers/
│   └── market_intelligence_controller.py   # API endpoints
├── routes/
│   └── market_intelligence_routes.py       # FastAPI routes
└── schemas/
    └── market_intelligence_schema.py       # Request/response schemas
```

### **Implementation Order and Details**

#### **Phase 1: Core Models and Base Classes (Files 1-4)**

**File 1: `app/root_orchestrator/models.py`**
```python
# Implementation Guide:
# 1. Define RequestStatus enum (PENDING, PROCESSING, EXECUTING, COMPLETED, FAILED)
# 2. Define RequestType enum (SEMAGLUTIDE_INTELLIGENCE, future types)
# 3. Define Priority enum (HIGH, MEDIUM, LOW)
# 4. Create MarketIntelligenceRequest model with all fields from schema
# 5. Create RequestProgress model for tracking
# 6. Create RequestResults model for storing outcomes
# 7. Add validation methods and helper functions

# Key Components:
- RequestStatus, RequestType, Priority enums
- MarketIntelligenceRequest (main request model)
- RequestProgress (progress tracking)
- RequestResults (results storage)
- Validation methods
```

**File 2: `app/root_orchestrator/config.py`**
```python
# Implementation Guide:
# 1. Define TableStrategyConfig with polling settings
# 2. Define SQSStrategyConfig with queue URLs and worker settings
# 3. Create RootOrchestratorConfig that combines both
# 4. Add environment variable loading
# 5. Add validation for configuration values
# 6. Create factory methods for different environments

# Key Components:
- TableStrategyConfig class
- SQSStrategyConfig class  
- RootOrchestratorConfig class
- Environment variable handling
- Configuration validation
```

**File 3: `app/root_orchestrator/strategies/base_strategy.py`**
```python
# Implementation Guide:
# 1. Create abstract BaseProcessingStrategy class
# 2. Define abstract methods: submit_request, get_status, cancel_request
# 3. Define common interface for both table and SQS strategies
# 4. Add logging and error handling patterns
# 5. Define strategy lifecycle methods

# Key Components:
- BaseProcessingStrategy (abstract class)
- Abstract methods for all operations
- Common error handling patterns
- Logging interface
```

**File 4: `app/root_orchestrator/status_tracker.py`**
```python
# Implementation Guide:
# 1. Create StatusTracker class for unified status management
# 2. Implement status update methods
# 3. Add progress calculation logic
# 4. Create status history tracking
# 5. Add status validation and transitions

# Key Components:
- StatusTracker class
- Status update methods
- Progress calculation
- Status history
- Validation logic
```

#### **Phase 2: Table Strategy Implementation (Files 5-6)**

**File 5: `app/root_orchestrator/strategies/table_strategy.py`**
```python
# Implementation Guide:
# 1. Inherit from BaseProcessingStrategy
# 2. Implement submit_request: Store request in database
# 3. Implement get_status: Query database for status
# 4. Implement cancel_request: Update status to cancelled
# 5. Add database connection management
# 6. Add error handling and retry logic

# Key Components:
- TableProcessingStrategy class
- Database operations (CRUD)
- Request submission logic
- Status querying
- Error handling
```

**File 6: `app/root_orchestrator/workers/table_processor.py`**
```python
# Implementation Guide:
# 1. Create TableProcessor class for background polling
# 2. Implement polling loop with configurable interval
# 3. Add request processing logic
# 4. Integrate with MarketIntelligenceService
# 5. Add comprehensive error handling and logging
# 6. Implement graceful shutdown

# Key Components:
- TableProcessor class
- Polling loop logic
- Request processing
- Market intelligence integration
- Error handling and recovery
```

#### **Phase 3: API Layer (Files 7-9)**

**File 7: `app/schemas/market_intelligence_schema.py`**
```python
# Implementation Guide:
# 1. Create Pydantic schemas for API requests/responses
# 2. Define SubmitRequestSchema with validation
# 3. Define RequestStatusSchema for status responses
# 4. Define RequestResultsSchema for results
# 5. Add custom validators for business logic

# Key Components:
- SubmitRequestSchema
- RequestStatusSchema  
- RequestResultsSchema
- Custom validators
- Error response schemas
```

**File 8: `app/controllers/market_intelligence_controller.py`**
```python
# Implementation Guide:
# 1. Create MarketIntelligenceController class
# 2. Implement submit_request method
# 3. Implement get_request_status method
# 4. Implement get_request_results method
# 5. Add request validation and error handling
# 6. Integrate with RootOrchestratorService

# Key Components:
- MarketIntelligenceController class
- Request submission logic
- Status checking logic
- Results retrieval logic
- Validation and error handling
```

**File 9: `app/routes/market_intelligence_routes.py`**
```python
# Implementation Guide:
# 1. Define FastAPI router for market intelligence endpoints
# 2. Create POST /market-intelligence/requests endpoint
# 3. Create GET /market-intelligence/requests/{request_id}/status endpoint
# 4. Create GET /market-intelligence/requests/{request_id}/results endpoint
# 5. Add proper HTTP status codes and error responses
# 6. Add API documentation with examples

# Key Components:
- FastAPI router setup
- POST /requests endpoint
- GET /status endpoint
- GET /results endpoint
- Error handling middleware
```

#### **Phase 4: Main Orchestrator Service (File 10)**

**File 10: `app/root_orchestrator/root_orchestrator_service.py`**
```python
# Implementation Guide:
# 1. Create RootOrchestratorService class
# 2. Implement strategy pattern for table/SQS selection
# 3. Add request validation and preprocessing
# 4. Integrate with MarketIntelligenceService
# 5. Add comprehensive logging and monitoring
# 6. Implement request lifecycle management

# Key Components:
- RootOrchestratorService class
- Strategy pattern implementation
- Request validation
- Lifecycle management
- Integration layer
```

#### **Phase 5: SQS Strategy Implementation (Files 11-12)**

**File 11: `app/root_orchestrator/strategies/sqs_strategy.py`**
```python
# Implementation Guide:
# 1. Inherit from BaseProcessingStrategy
# 2. Implement submit_request: Send message to SQS
# 3. Implement get_status: Query database for status
# 4. Add SQS client configuration and management
# 5. Implement message formatting and validation
# 6. Add error handling for SQS operations

# Key Components:
- SQSProcessingStrategy class
- SQS client management
- Message operations
- Queue management
- Error handling
```

**File 12: `app/root_orchestrator/workers/sqs_consumer.py`**
```python
# Implementation Guide:
# 1. Create SQSConsumer class for message processing
# 2. Implement long polling message consumption
# 3. Add message processing with retry logic
# 4. Integrate with MarketIntelligenceService
# 5. Implement Dead Letter Queue handling
# 6. Add worker scaling and management

# Key Components:
- SQSConsumer class
- Message consumption loop
- Retry and DLQ logic
- Worker management
- Scaling capabilities
```

## 🔧 Implementation Strategy

### **Phase 1: Table-Based Implementation**

**Step 1: Core Foundation (Files 1-4)**
1. Create `models.py` with all request models and enums
2. Create `config.py` with configuration classes
3. Create `base_strategy.py` with abstract interface
4. Create `status_tracker.py` for status management

**Step 2: Table Strategy (Files 5-6)**
1. Implement `table_strategy.py` with database operations
2. Create `table_processor.py` for background polling
3. Test table strategy in isolation

**Step 3: API Layer (Files 7-9)**
1. Create API schemas in `market_intelligence_schema.py`
2. Implement controller in `market_intelligence_controller.py`
3. Add routes in `market_intelligence_routes.py`
4. Test API endpoints

**Step 4: Integration (File 10)**
1. Create main `root_orchestrator_service.py`
2. Integrate all components
3. End-to-end testing

### **Phase 2: SQS-Based Implementation**

**Step 1: SQS Strategy (File 11)**
1. Implement `sqs_strategy.py` with SQS operations
2. Add SQS client configuration and management
3. Test SQS message operations

**Step 2: SQS Consumer (File 12)**
1. Create `sqs_consumer.py` for message processing
2. Implement worker scaling and management
3. Test consumer with mock messages

**Step 3: Integration Testing**
1. Test both strategies with same API
2. Performance comparison testing
3. Load testing for scalability

### **Phase 3: Unified Interface**

1. **Strategy Selection** - Configuration-based strategy selection
2. **Monitoring** - Unified monitoring for both approaches
3. **Testing** - Comprehensive test suite
4. **Documentation** - API documentation and usage guides

## ✅ Implementation Checklist

### **Phase 1: Table Strategy (Files 1-10)**

**Core Foundation:**
- [ ] `models.py` - Request models, enums, validation
- [ ] `config.py` - Configuration classes and environment loading
- [ ] `base_strategy.py` - Abstract strategy interface
- [ ] `status_tracker.py` - Status management and tracking

**Table Strategy:**
- [ ] `table_strategy.py` - Database operations and request handling
- [ ] `table_processor.py` - Background polling worker

**API Layer:**
- [ ] `market_intelligence_schema.py` - Pydantic schemas
- [ ] `market_intelligence_controller.py` - Business logic
- [ ] `market_intelligence_routes.py` - FastAPI endpoints

**Integration:**
- [ ] `root_orchestrator_service.py` - Main orchestrator service

### **Phase 2: SQS Strategy (Files 11-12)**

**SQS Implementation:**
- [ ] `sqs_strategy.py` - SQS operations and message handling
- [ ] `sqs_consumer.py` - Message consumer workers

### **Testing and Deployment:**
- [ ] Unit tests for all components
- [ ] Integration tests for end-to-end flows
- [ ] Load testing for performance validation
- [ ] Documentation and API examples

## 🔗 File Dependencies

### **Dependency Graph:**

```
models.py (1)
    ↓
config.py (2)
    ↓
base_strategy.py (3) ← status_tracker.py (4)
    ↓                      ↓
table_strategy.py (5) ←────┘
    ↓
table_processor.py (6)
    ↓
market_intelligence_schema.py (7)
    ↓
market_intelligence_controller.py (8)
    ↓
market_intelligence_routes.py (9)
    ↓
root_orchestrator_service.py (10)
    ↓
sqs_strategy.py (11)
    ↓
sqs_consumer.py (12)
```

### **Implementation Order:**
1. **Foundation Layer**: Files 1-4 (can be done in parallel after models.py)
2. **Table Strategy**: Files 5-6 (depends on 1-4)
3. **API Layer**: Files 7-9 (depends on 1-4, can be parallel with 5-6)
4. **Integration**: File 10 (depends on all previous)
5. **SQS Strategy**: Files 11-12 (depends on 1-4, 10)

## 📋 Development Guidelines

### **Code Standards:**
- Follow existing project structure and naming conventions
- Use type hints for all function parameters and returns
- Add comprehensive docstrings for all classes and methods
- Include error handling and logging in all operations
- Write unit tests for each component

### **Testing Requirements:**
- Unit tests with >80% coverage
- Integration tests for API endpoints
- Mock external dependencies (SQS, Database)
- Performance tests for polling and message processing
- Error scenario testing

### **Documentation Requirements:**
- API documentation with OpenAPI/Swagger
- Code comments for complex business logic
- Configuration examples for both strategies
- Deployment guides for different environments

## 📋 Configuration Options

### **Table Strategy Configuration**

```python
TABLE_CONFIG = {
    "polling_interval": 5,  # seconds
    "max_concurrent_requests": 1,
    "table_name": "market_intelligence_requests",
    "status_update_interval": 10,  # seconds
    "cleanup_completed_after": 86400,  # 24 hours in seconds
}
```

### **SQS Strategy Configuration**

```python
SQS_CONFIG = {
    "main_queue_url": "https://sqs.region.amazonaws.com/account/main-queue",
    "dlq_url": "https://sqs.region.amazonaws.com/account/dlq",
    "max_workers": 5,
    "visibility_timeout": 300,  # 5 minutes
    "max_retries": 3,
    "retry_delay_base": 2,  # exponential backoff base
    "long_polling_wait_time": 20,  # seconds
}
```

## 🚦 Status Management

### **Status Flow**

```
PENDING → PROCESSING → EXECUTING → COMPLETED
                    ↘              ↗
                      → FAILED ←
```

### **Status Definitions**

- **PENDING**: Request submitted, waiting to be processed
- **PROCESSING**: Request picked up by processor, initializing
- **EXECUTING**: Market intelligence workflow is running
- **COMPLETED**: Workflow completed successfully, results available
- **FAILED**: Workflow failed, error details available

### **Progress Tracking**

```python
progress = {
    "current_stage": "serp_discovery|content_extraction|aggregation|completed",
    "percentage": 0-100,
    "urls_found": 0,
    "content_extracted": 0,
    "estimated_completion": "timestamp"
}
```

## 🔍 Monitoring and Observability

### **Key Metrics**

1. **Request Metrics**
   - Requests per hour/day
   - Average processing time
   - Success/failure rates
   - Queue depth (SQS only)

2. **Performance Metrics**
   - API response times
   - Workflow execution times
   - Resource utilization

3. **Error Metrics**
   - Error rates by type
   - Retry counts
   - Dead letter queue size

### **Logging Strategy**

```python
# Request lifecycle logging
logger.info("Request submitted", extra={
    "request_id": request_id,
    "user_id": user_id,
    "project_id": project_id,
    "strategy": "table|sqs"
})

logger.info("Processing started", extra={
    "request_id": request_id,
    "worker_id": worker_id,
    "estimated_duration": duration
})

logger.info("Processing completed", extra={
    "request_id": request_id,
    "duration": actual_duration,
    "urls_processed": count,
    "success_rate": percentage
})
```

## 🧪 Testing Strategy

### **Unit Tests**
- Strategy implementations
- Model validation
- Configuration parsing

### **Integration Tests**
- End-to-end request processing
- Database operations
- SQS message handling

### **Load Tests**
- Concurrent request handling
- Performance under load
- Resource utilization

## 🚀 Deployment Considerations

### **Table Strategy Deployment**
- Single processor instance
- Database connection pooling
- Monitoring for polling efficiency

### **SQS Strategy Deployment**
- Multiple worker instances
- Auto-scaling based on queue depth
- Dead Letter Queue monitoring
- SQS permissions and IAM roles

## 📚 Developer Workflow

### **Adding New Request Types**

1. **Extend Models** - Add new request type enum
2. **Create Workflow** - Implement specific workflow logic
3. **Update Processor** - Add routing logic for new type
4. **Add Tests** - Unit and integration tests
5. **Update Documentation** - API docs and examples

### **Debugging Issues**

1. **Check Request Status** - Database or SQS console
2. **Review Logs** - Structured logging for traceability
3. **Monitor Metrics** - Performance and error metrics
4. **Test Locally** - Isolated testing with mock data

## 🔄 Future Enhancements

### **Planned Features**
- **Priority Queues**: Different queues for different priorities
- **Batch Processing**: Process multiple similar requests together
- **Caching**: Cache results for similar requests
- **Webhooks**: Notify external systems on completion
- **Scheduling**: Cron-like scheduling for recurring requests

### **Scalability Improvements**
- **Horizontal Scaling**: Multiple processor instances
- **Load Balancing**: Distribute load across workers
- **Regional Deployment**: Multi-region processing
- **Cost Optimization**: Spot instances for workers

---

## 📋 Summary

The Root Orchestrator provides a flexible, scalable solution for managing market intelligence requests with two distinct processing strategies:

**Table Strategy**: Simple, reliable, easy to debug  
**SQS Strategy**: Scalable, fault-tolerant, high-throughput  

Both strategies provide the same API interface, allowing users to choose based on their specific requirements for scale, complexity, and infrastructure preferences.

The implementation follows established patterns and integrates seamlessly with the existing agent service architecture while providing room for future enhancements and additional workflow types. 