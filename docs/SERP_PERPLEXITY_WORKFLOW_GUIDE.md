# SERP-Perplexity Workflow Complete Guide

## 🎯 Overview

This document provides a complete breakdown of the SERP-Perplexity workflow, from API submission to final results. It shows every file, method, and data flow involved in processing your request format.

## 📋 Request Format

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

## 🔄 Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SERP-PERPLEXITY WORKFLOW                         │
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
2. ROUTE HANDLER            │
   ┌─────────────────┐      │
   │ market_         │◀─────┘
   │ intelligence_   │
   │ routes.py       │
   │                 │
   │ submit_request()│──────┐
   └─────────────────┘      │
                            │
3. CONTROLLER               │
   ┌─────────────────┐      │
   │ market_         │◀─────┘
   │ intelligence_   │
   │ controller.py   │
   │                 │
   │ submit_request()│──────┐
   └─────────────────┘      │
                            │
4. ROOT ORCHESTRATOR        │
   ┌─────────────────┐      │
   │ root_           │◀─────┘
   │ orchestrator_   │
   │ service.py      │
   │                 │
   │ submit_request()│──────┐
   └─────────────────┘      │
                            │
5. TABLE STRATEGY           │
   ┌─────────────────┐      │
   │ table_          │◀─────┘
   │ strategy.py     │
   │                 │
   │ submit_request()│──────┐
   └─────────────────┘      │
                            │
6. DATABASE STORAGE         │
   ┌─────────────────┐      │
   │ DynamoDB        │◀─────┘
   │ market_         │
   │ intelligence_   │
   │ requests        │
   │                 │
   │ Status: PENDING │
   └─────────────────┘
                            
7. BACKGROUND PROCESSOR
   ┌─────────────────┐
   │ table_          │
   │ processor.py    │
   │                 │──────┐
   │ _processing_    │      │
   │ loop()          │      │
   └─────────────────┘      │
                            │
8. WORKFLOW DETECTION       │
   ┌─────────────────┐      │
   │ _process_       │◀─────┘
   │ request()       │
   │                 │
   │ Check: sources? │──────┐
   │ keywords?       │      │
   └─────────────────┘      │
                            │
9. STAGE0 ORCHESTRATOR      │
   ┌─────────────────┐      │
   │ stage0_         │◀─────┘
   │ orchestrator/   │
   │ service.py      │
   │                 │
   │ process_        │──────┐
   │ request()       │      │
   └─────────────────┘      │
                            │
10. INGESTION SERVICE       │
    ┌─────────────────┐     │
    │ ingestion_      │◀────┘
    │ service.py      │
    │                 │
    │ process_        │─────┐
    │ ingestion()     │     │
    └─────────────────┘     │
                            │
11. SOURCE PROCESSING       │
    ┌─────────────────┐     │
    │ FOR EACH SOURCE │◀────┘
    │                 │
    │ Source 1:       │─────┐
    │ ClinicalTrials  │     │
    │                 │     │
    │ Source 2:       │     │
    │ PubMed          │     │
    └─────────────────┘     │
                            │
12. SERP API CALL           │
    ┌─────────────────┐     │
    │ stage0_serp/    │◀────┘
    │ serp_api.py     │
    │                 │
    │ search_with_    │─────┐
    │ date_range()    │     │
    └─────────────────┘     │
                            │
13. SERP RESPONSE           │
    ┌─────────────────┐     │
    │ URLs Found:     │◀────┘
    │                 │
    │ • URL 1         │─────┐
    │ • URL 2         │     │
    │ • URL 3         │     │
    │ • ...           │     │
    └─────────────────┘     │
                            │
14. PERPLEXITY PROCESSING   │
    ┌─────────────────┐     │
    │ FOR EACH URL    │◀────┘
    │                 │
    │ stage0_         │─────┐
    │ perplexity/     │     │
    │ perplexity_     │     │
    │ api.py          │     │
    │                 │     │
    │ extract_single_ │     │
    │ url()           │     │
    └─────────────────┘     │
                            │
15. CONTENT EXTRACTION      │
    ┌─────────────────┐     │
    │ Content Results:│◀────┘
    │                 │
    │ • Title         │─────┐
    │ • Content       │     │
    │ • Confidence    │     │
    │ • Quality Score │     │
    └─────────────────┘     │
                            │
16. AGGREGATION             │
    ┌─────────────────┐     │
    │ Combine Results │◀────┘
    │                 │
    │ • All URLs      │─────┐
    │ • All Content   │     │
    │ • Statistics    │     │
    │ • Metadata      │     │
    └─────────────────┘     │
                            │
17. FINAL STORAGE           │
    ┌─────────────────┐     │
    │ DynamoDB        │◀────┘
    │                 │
    │ Status:         │
    │ COMPLETED       │
    │                 │
    │ Results: {...}  │
    └─────────────────┘
```

## 📁 File-by-File Method Details

### 1. **API Entry Point**

#### `app/routes/market_intelligence_routes.py`
```python
@router.post("/requests")
async def submit_request(
    request_data: SubmitRequestSchema,
    controller: MarketIntelligenceController = Depends(get_controller)
) -> RequestResponseSchema:
    """
    🎯 Entry point for all market intelligence requests
    
    Flow:
    1. Validates request schema
    2. Calls controller.submit_request()
    3. Returns request_id and status
    """
```

#### `app/schemas/market_intelligence_schema.py`
```python
class SubmitRequestSchema(BaseModel):
    """
    🔍 Request validation schema
    
    Validates:
    - project_id, user_id (required)
    - priority (high/medium/low)
    - processing_strategy (table/sqs)
    - config (MarketIntelligenceRequestConfig)
    """
    
    config: Optional[MarketIntelligenceRequestConfig] = Field(...)
    # ↑ This includes keywords, sources, date_range
```

### 2. **Business Logic Layer**

#### `app/controllers/market_intelligence_controller.py`
```python
class MarketIntelligenceController:
    
    async def submit_request(self, request_data: SubmitRequestSchema) -> RequestResponseSchema:
        """
        🎯 Main business logic handler
        
        Flow:
        1. Validates business rules
        2. Creates MarketIntelligenceRequest object
        3. Calls orchestrator_service.submit_request()
        4. Returns response with request_id
        """
        
        # Key method calls:
        await self._validate_submission_rules(request_data)
        mi_request = MarketIntelligenceRequest(...)
        success = await self.orchestrator_service.submit_request(mi_request)
```

### 3. **Root Orchestrator Layer**

#### `app/root_orchestrator/root_orchestrator_service.py`
```python
class RootOrchestratorService:
    
    async def submit_request(self, request: MarketIntelligenceRequest) -> bool:
        """
        🎯 Strategy pattern implementation
        
        Flow:
        1. Gets appropriate strategy (table/sqs)
        2. Calls strategy.submit_request()
        3. Returns success status
        """
        
        strategy = await self._get_strategy_for_request(request)
        success = await strategy.submit_request(request)
```

#### `app/root_orchestrator/models.py`
```python
class MarketIntelligenceRequestConfig(BaseModel):
    """
    🔍 Enhanced configuration model
    
    New fields added:
    - keywords: List[str]
    - sources: List[SourceConfig] 
    - date_range: Optional[DateRangeConfig]
    - search_query: Optional[str]
    - quality_threshold: float
    """
    
class SourceConfig(BaseModel):
    """Source configuration"""
    name: str
    type: str  # clinical, academic, government
    url: str

class DateRangeConfig(BaseModel):
    """Date range for searches"""
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
```

### 4. **Strategy Implementation**

#### `app/root_orchestrator/strategies/table_strategy.py`
```python
class TableProcessingStrategy:
    
    async def submit_request(self, request: MarketIntelligenceRequest) -> bool:
        """
        🎯 Database storage strategy
        
        Flow:
        1. Stores request in DynamoDB
        2. Sets status to PENDING
        3. Background processor will pick it up
        """
        
        await self.database_client.put_item(
            table_name="market_intelligence_requests",
            item=request.dict()
        )
```

### 5. **Background Processing**

#### `app/root_orchestrator/workers/table_processor.py`
```python
class TableProcessor:
    
    async def _processing_loop(self):
        """
        🔄 Main polling loop
        
        Flow:
        1. Polls database for PENDING requests
        2. Calls _process_request() for each
        3. Sleeps and repeats
        """
        
    async def _process_request(self, request: MarketIntelligenceRequest):
        """
        🎯 Individual request processing
        
        Flow:
        1. Updates status to PROCESSING
        2. Detects workflow type (SERP-Perplexity vs original)
        3. Calls appropriate workflow
        4. Updates status to COMPLETED/FAILED
        """
        
        # Key detection logic:
        if hasattr(request.config, 'sources') and request.config.sources:
            # Use SERP-Perplexity workflow
            stage0_request = await self._convert_to_stage0_request(request)
            result = await orchestrator_service.process_request(...)
        else:
            # Use original workflow
            result = await self.market_intelligence_service.execute_semaglutide_intelligence(...)
    
    async def _convert_to_stage0_request(self, request: MarketIntelligenceRequest) -> dict:
        """
        🔄 Request format conversion
        
        Converts:
        - Root orchestrator format → stage0_orchestrator format
        - Handles keywords, sources, date_range mapping
        """
```

### 6. **Stage0 Orchestrator Integration**

#### `app/agent_service_module/agents/stage0_orchestrator/service.py`
```python
class OrchestratorService:
    
    async def process_request(self, query: str, num_results: int = 10, **kwargs) -> IngestionResponse:
        """
        🎯 Stage0 orchestrator entry point
        
        Flow:
        1. Creates IngestionRequest
        2. Calls ingestion_service.process_ingestion()
        3. Returns IngestionResponse
        """
        
        request = IngestionRequest(
            query=query,
            num_results=num_results,
            keywords=kwargs.get('keywords'),
            sources=kwargs.get('sources'),
            date_range=kwargs.get('date_range'),
            **kwargs
        )
```

#### `app/agent_service_module/agents/stage0_orchestrator/models.py`
```python
class IngestionRequest(BaseModel):
    """
    🔍 Enhanced ingestion request
    
    New fields added:
    - keywords: Optional[List[str]]
    - sources: Optional[List[SourceConfig]]
    - date_range: Optional[DateRangeConfig]
    - quality_threshold: float
    """
    
    def is_serp_perplexity_workflow(self) -> bool:
        """Detects if this should use SERP-Perplexity workflow"""
        return bool(self.keywords and self.sources)
```

### 7. **Ingestion Processing**

#### `app/agent_service_module/agents/stage0_orchestrator/ingestion_service.py`
```python
class IngestionService:
    
    async def process_ingestion(self, request: IngestionRequest) -> IngestionResponse:
        """
        🎯 Main ingestion orchestrator
        
        Flow:
        1. Detects workflow type
        2. For SERP-Perplexity: processes sources one by one
        3. For each source: SERP → URLs → Perplexity → Content
        4. Aggregates all results
        """
        
        if request.is_serp_perplexity_workflow():
            return await self._process_serp_perplexity_workflow(request)
        else:
            return await self._process_standard_workflow(request)
    
    async def _process_serp_perplexity_workflow(self, request: IngestionRequest):
        """
        🔄 SERP-Perplexity workflow implementation
        
        Flow:
        1. For each source in request.sources:
           a. Call SERP API to find URLs
           b. For each URL found:
              - Call Perplexity API to extract content
              - Apply quality filtering
           c. Aggregate source results
        2. Combine all source results
        3. Return final response
        """
```

### 8. **SERP API Integration**

#### `app/agent_service_module/agents/stage0_serp/serp_api.py`
```python
class SerpAPI:
    
    async def search_with_date_range(
        self, 
        keywords: List[str], 
        source: Dict[str, Any] = None,
        start_date: str = None, 
        end_date: str = None
    ) -> SerpResponse:
        """
        🔍 SERP API call with date filtering
        
        Flow:
        1. Converts source to dict format
        2. Builds query with keywords (OR logic)
        3. Adds site restriction (site:domain.com)
        4. Adds date range filter
        5. Calls Google via SerpAPI
        6. Returns structured results
        """
        
        # Key transformations:
        query = '("Obesity" OR "Weight loss" OR "Overweight" OR "Obese") (site:clinicaltrials.gov)'
        params = {
            'tbs': 'cdr:1,cd_min:8/01/2025,cd_max:8/03/2025'
        }
```

#### `app/agent_service_module/agents/stage0_serp/serp_query_builder.py`
```python
def build_date_range_query(
    keywords: List[str], 
    sources: List[Dict[str, Any]] = None,
    start_date: str = None, 
    end_date: str = None
) -> Dict[str, Any]:
    """
    🔧 Query builder for Google search
    
    Builds:
    - Keywords with OR logic: ("Obesity" OR "Weight loss")
    - Site restrictions: (site:clinicaltrials.gov)
    - Date filters: tbs=cdr:1,cd_min:8/01/2025,cd_max:8/03/2025
    """
```

### 9. **Perplexity API Integration**

#### `app/agent_service_module/agents/stage0_perplexity/perplexity_api.py`
```python
class PerplexityAPI:
    
    async def extract_single_url(self, url: str) -> PerplexityResponse:
        """
        🔍 Perplexity API call for content extraction
        
        Flow:
        1. Creates focused query for the URL
        2. Calls Perplexity chat completions API
        3. Extracts content, title, confidence
        4. Applies quality scoring
        5. Returns structured response
        """
        
        # Key API call:
        payload = {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": "Extract key information..."},
                {"role": "user", "content": f"Analyze this URL: {url}"}
            ],
            "return_citations": True,
            "search_domain_filter": [url]
        }
```

## 📊 Data Flow Diagram

```
REQUEST DATA TRANSFORMATION FLOW:

1. API Request Format:
   {
     "config": {
       "keywords": ["Obesity", "Weight loss"],
       "sources": [{"name": "ClinicalTrials", "url": "..."}],
       "date_range": {"start_date": "2025-08-01", "end_date": "2025-08-03"}
     }
   }
   ↓

2. MarketIntelligenceRequest Object:
   MarketIntelligenceRequest(
     config=MarketIntelligenceRequestConfig(
       keywords=["Obesity", "Weight loss"],
       sources=[SourceConfig(name="ClinicalTrials", ...)],
       date_range=DateRangeConfig(start_date="2025-08-01", ...)
     )
   )
   ↓

3. Database Storage (DynamoDB):
   {
     "request_id": "req_123456",
     "status": "PENDING",
     "config": { ... },
     "created_at": "2025-01-01T10:00:00Z"
   }
   ↓

4. Background Processor Detection:
   if request.config.sources and request.config.keywords:
       use_serp_perplexity_workflow = True
   ↓

5. Stage0 Request Conversion:
   {
     "query": '("Obesity" OR "Weight loss")',
     "keywords": ["Obesity", "Weight loss"],
     "sources": [{"name": "ClinicalTrials", "type": "clinical", "url": "..."}],
     "date_range": {"start_date": "2025-08-01", "end_date": "2025-08-03"}
   }
   ↓

6. SERP API Query:
   {
     "q": '("Obesity" OR "Weight loss") (site:clinicaltrials.gov)',
     "tbs": "cdr:1,cd_min:8/01/2025,cd_max:8/03/2025",
     "engine": "google"
   }
   ↓

7. SERP Response:
   {
     "organic_results": [
       {"title": "Study 1", "link": "https://clinicaltrials.gov/study1"},
       {"title": "Study 2", "link": "https://clinicaltrials.gov/study2"}
     ]
   }
   ↓

8. Perplexity API Calls (for each URL):
   {
     "model": "sonar-pro",
     "messages": [{"role": "user", "content": "Analyze: https://clinicaltrials.gov/study1"}],
     "search_domain_filter": ["https://clinicaltrials.gov/study1"]
   }
   ↓

9. Perplexity Responses:
   {
     "choices": [{
       "message": {
         "content": "This clinical trial studies obesity treatment..."
       }
     }]
   }
   ↓

10. Final Aggregated Results:
    {
      "request_id": "req_123456",
      "status": "completed",
      "sources_processed": [
        {
          "source_name": "ClinicalTrials",
          "urls_found": 5,
          "content_extracted": 3,
          "content": [
            {"url": "...", "title": "...", "content": "...", "confidence": 0.85},
            {"url": "...", "title": "...", "content": "...", "confidence": 0.92}
          ]
        }
      ],
      "total_urls_found": 5,
      "total_content_extracted": 3
    }
```

## ⏱️ Processing Timeline

```
Timeline for Processing Your Request:

T+0s    │ API Request Received
        │ ├─ Schema Validation
        │ ├─ Controller Processing  
        │ ├─ Root Orchestrator
        │ └─ Database Storage (Status: PENDING)
        │
T+1s    │ Background Processor Picks Up Request
        │ ├─ Status Update: PROCESSING
        │ ├─ Workflow Detection: SERP-Perplexity
        │ └─ Stage0 Orchestrator Called
        │
T+2s    │ Source 1 Processing: ClinicalTrials
        │ ├─ SERP API Call (keywords + site + date range)
        │ ├─ Response: 5 URLs found
        │ └─ Start Perplexity processing
        │
T+5s    │ Perplexity Processing URLs 1-5
        │ ├─ URL 1: Content extracted (confidence: 0.85)
        │ ├─ URL 2: Content extracted (confidence: 0.92)
        │ ├─ URL 3: Content too short (skipped)
        │ ├─ URL 4: Content extracted (confidence: 0.78)
        │ └─ URL 5: API error (skipped)
        │
T+15s   │ Source 2 Processing: PubMed
        │ ├─ SERP API Call (keywords + site + date range)
        │ ├─ Response: 3 URLs found
        │ └─ Start Perplexity processing
        │
T+20s   │ Perplexity Processing URLs 1-3
        │ ├─ URL 1: Content extracted (confidence: 0.88)
        │ ├─ URL 2: Content extracted (confidence: 0.91)
        │ └─ URL 3: Content extracted (confidence: 0.76)
        │
T+25s   │ Results Aggregation
        │ ├─ Combine all source results
        │ ├─ Calculate statistics
        │ ├─ Apply quality filtering
        │ └─ Generate final report
        │
T+26s   │ Final Storage
        │ ├─ Status Update: COMPLETED
        │ ├─ Results stored in database
        │ └─ Processing complete
```

## 🔍 Key Configuration Points

### 1. **SERP API Configuration**
```python
# In stage0_serp/serp_api.py
SERP_CONFIG = {
    "api_key": "sadsad",
    "timeout": 60,
    "max_results": 20,
    "headers": {
        "User-Agent": "Mozilla/5.0...",
        "Accept": "application/json"
    }
}
```

### 2. **Perplexity API Configuration**
```python
# In stage0_perplexity/perplexity_api.py
PERPLEXITY_CONFIG = {
    "api_key": "dumypasdsadplx-asdsadsadsa",
    "model": "sonar-pro",
    "timeout": 60,
    "return_citations": True,
    "return_images": False
}
```

### 3. **Quality Thresholds**
```python
# Content quality filtering
QUALITY_THRESHOLDS = {
    "min_content_length": 100,      # characters
    "min_confidence": 0.5,          # 0.0 - 1.0
    "quality_threshold": 0.5        # from your request
}
```

## 🚀 Testing Your Request

### 1. **Start the Server**
```bash
python3 start_server.py
```

### 2. **Submit Your Request**
```bash
curl -X POST http://localhost:8005/api/v1/market-intelligence/requests \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "clinical_trials_test",
    "user_id": "test_user_003",
    "priority": "high",
    "processing_strategy": "table",
    "config": {
      "keywords": ["Obesity", "Weight loss", "Overweight", "Obese"],
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
  }'
```

### 3. **Check Status**
```bash
curl http://localhost:8005/api/v1/market-intelligence/requests/{request_id}/status
```

### 4. **Get Results**
```bash
curl http://localhost:8005/api/v1/market-intelligence/requests/{request_id}/results
```

## 📋 Expected Response Format

```json
{
  "request_id": "req_20250101_123456",
  "status": "completed",
  "started_at": "2025-01-01T10:00:00Z",
  "completed_at": "2025-01-01T10:00:26Z",
  "sources_processed": [
    {
      "source_name": "ClinicalTrials",
      "source_url": "https://clinicaltrials.gov/",
      "source_type": "clinical",
      "urls_found": 5,
      "content_extracted": 3,
      "urls": [
        "https://clinicaltrials.gov/study/NCT123456",
        "https://clinicaltrials.gov/study/NCT789012"
      ],
      "content": [
        {
          "url": "https://clinicaltrials.gov/study/NCT123456",
          "title": "Obesity Treatment Study",
          "content": "This randomized controlled trial...",
          "confidence": 0.85,
          "quality_score": 0.78,
          "keywords_found": ["Obesity", "Weight loss"]
        }
      ]
    },
    {
      "source_name": "PubMed",
      "source_url": "https://pubmed.ncbi.nlm.nih.gov/",
      "source_type": "clinical",
      "urls_found": 3,
      "content_extracted": 3,
      "content": [...]
    }
  ],
  "total_urls_found": 8,
  "total_content_extracted": 6,
  "processing_time_seconds": 26,
  "errors": [],
  "warnings": ["Content too short from 2 URLs"]
}
```

## 🎯 Summary

This workflow successfully integrates:

✅ **Your Request Format** - Keywords, sources, date ranges  
✅ **SERP API** - Finds URLs from each source  
✅ **Perplexity API** - Extracts content from each URL  
✅ **Source-by-Source Processing** - Handles sources one by one  
✅ **Quality Filtering** - Applies your quality threshold  
✅ **Existing Infrastructure** - Uses current API endpoint  

The system processes your sources sequentially (ClinicalTrials first, then PubMed), calls SERP to find URLs, then calls Perplexity for each URL to extract content, exactly as requested! 🚀 