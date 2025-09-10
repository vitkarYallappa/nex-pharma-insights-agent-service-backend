# Visual Workflow Diagram

## 🎯 Complete SERP-Perplexity Workflow

```mermaid
graph TD
    A[API Request<br/>POST /api/v1/market-intelligence/requests] --> B[Route Handler<br/>market_intelligence_routes.py]
    B --> C[Controller<br/>market_intelligence_controller.py]
    C --> D[Root Orchestrator<br/>root_orchestrator_service.py]
    D --> E[Table Strategy<br/>table_strategy.py]
    E --> F[Database Storage<br/>DynamoDB<br/>Status: PENDING]
    
    F --> G[Background Processor<br/>table_processor.py<br/>Polling Loop]
    G --> H{Workflow Detection<br/>sources & keywords?}
    
    H -->|Yes| I[Stage0 Orchestrator<br/>stage0_orchestrator/service.py]
    H -->|No| J[Original Workflow<br/>market_intelligence_service.py]
    
    I --> K[Ingestion Service<br/>ingestion_service.py]
    K --> L[Source Processing Loop<br/>Process Each Source]
    
    L --> M[Source 1: ClinicalTrials<br/>SERP API Call]
    M --> N[SERP Response<br/>URLs Found: 5]
    N --> O[Perplexity Processing<br/>Extract Content from Each URL]
    O --> P[Source 1 Results<br/>3 Content Items Extracted]
    
    P --> Q[Source 2: PubMed<br/>SERP API Call]
    Q --> R[SERP Response<br/>URLs Found: 3]
    R --> S[Perplexity Processing<br/>Extract Content from Each URL]
    S --> T[Source 2 Results<br/>3 Content Items Extracted]
    
    T --> U[Results Aggregation<br/>Combine All Sources]
    U --> V[Final Storage<br/>DynamoDB<br/>Status: COMPLETED]
    
    V --> W[API Response<br/>Results Available]

    style A fill:#e1f5fe
    style F fill:#fff3e0
    style V fill:#e8f5e8
    style W fill:#e8f5e8
```

## 🔄 Data Transformation Flow

```mermaid
graph LR
    A[Your Request<br/>{keywords, sources, date_range}] --> B[Schema Validation<br/>SubmitRequestSchema]
    B --> C[MarketIntelligenceRequest<br/>Object Creation]
    C --> D[Database Storage<br/>JSON Format]
    D --> E[Background Processing<br/>Object Reconstruction]
    E --> F[Stage0 Conversion<br/>Format Mapping]
    F --> G[SERP Query Building<br/>Google Search Format]
    G --> H[Perplexity Processing<br/>Content Extraction]
    H --> I[Results Aggregation<br/>Final Response]
```

## 📊 Processing Timeline

```mermaid
gantt
    title SERP-Perplexity Processing Timeline
    dateFormat X
    axisFormat %Ss
    
    section API Layer
    Request Received    :done, api, 0, 1s
    Schema Validation   :done, schema, 0, 1s
    Database Storage    :done, db, 1s, 2s
    
    section Background Processing
    Request Detection   :done, detect, 2s, 3s
    Workflow Selection  :done, workflow, 3s, 4s
    
    section Source 1 (ClinicalTrials)
    SERP API Call      :done, serp1, 4s, 6s
    URLs Found (5)     :done, urls1, 6s, 7s
    Perplexity Calls   :done, perp1, 7s, 12s
    Content Extracted  :done, content1, 12s, 13s
    
    section Source 2 (PubMed)
    SERP API Call      :done, serp2, 13s, 15s
    URLs Found (3)     :done, urls2, 15s, 16s
    Perplexity Calls   :done, perp2, 16s, 20s
    Content Extracted  :done, content2, 20s, 21s
    
    section Finalization
    Results Aggregation :done, agg, 21s, 22s
    Final Storage      :done, final, 22s, 23s
```

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph "API Layer"
        A1[FastAPI Routes]
        A2[Pydantic Schemas]
        A3[Controllers]
    end
    
    subgraph "Root Orchestrator"
        B1[Service]
        B2[Strategies]
        B3[Workers]
        B4[Models]
    end
    
    subgraph "Stage0 Orchestrator"
        C1[Service]
        C2[Ingestion Service]
        C3[Workflow Manager]
    end
    
    subgraph "Agent Services"
        D1[SERP API<br/>stage0_serp]
        D2[Perplexity API<br/>stage0_perplexity]
    end
    
    subgraph "External APIs"
        E1[SerpAPI<br/>Google Search]
        E2[Perplexity AI<br/>Content Extraction]
    end
    
    subgraph "Storage"
        F1[DynamoDB<br/>Requests & Results]
        F2[S3<br/>File Storage]
    end
    
    A1 --> A3
    A3 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> C1
    C1 --> C2
    C2 --> D1
    C2 --> D2
    D1 --> E1
    D2 --> E2
    B2 --> F1
    C2 --> F2
```

## 🔍 Component Interaction Details

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Controller
    participant RootOrch
    participant TableProc
    participant Stage0
    participant SERP
    participant Perplexity
    participant DB
    
    User->>API: POST /requests {keywords, sources, date_range}
    API->>Controller: submit_request()
    Controller->>RootOrch: submit_request()
    RootOrch->>DB: Store request (PENDING)
    RootOrch->>User: Return request_id
    
    loop Background Processing
        TableProc->>DB: Poll for PENDING requests
        DB->>TableProc: Return request
        TableProc->>Stage0: process_request()
        
        loop For Each Source
            Stage0->>SERP: search_with_date_range()
            SERP->>Stage0: Return URLs
            
            loop For Each URL
                Stage0->>Perplexity: extract_single_url()
                Perplexity->>Stage0: Return content
            end
        end
        
        Stage0->>TableProc: Return aggregated results
        TableProc->>DB: Update status (COMPLETED)
    end
    
    User->>API: GET /requests/{id}/results
    API->>DB: Fetch results
    DB->>User: Return final results
``` 