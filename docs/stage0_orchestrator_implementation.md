# Stage 0 Orchestrator Agent Implementation

## 10-Line Prompt:
Create Stage 0 orchestrator agent that coordinates the complete content ingestion pipeline by managing SERP search operations and Perplexity content extraction in sequence, includes workflow management with state tracking for pipeline progress and error recovery, request coordination that generates unique request IDs and manages data flow between SERP and Perplexity agents, comprehensive error handling for partial failures where some URLs succeed while others fail, result aggregation that combines search results with extracted content into unified datasets, storage coordination that organizes all Stage 0 outputs in structured S3/Minio folders, database coordination that tracks overall pipeline status and metadata across both search and extraction phases, retry logic for failed operations with exponential backoff, pipeline status reporting with detailed progress tracking, and environment-based configuration that works seamlessly with both real and mock implementations.

## What it covers: 
Pipeline orchestration, workflow management, error recovery, result aggregation
## Methods: 
Workflow coordination, state management, error handling, data aggregation
## Why: 
Reliable pipeline execution, comprehensive error handling, structured data flow

---

## models.py
```python
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class PipelineStatus(str, Enum):
    PENDING = "pending"
    SEARCHING = "searching"
    EXTRACTING = "extracting"
    AGGREGATING = "aggregating"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"

class IngestionRequest(BaseModel):
    """Complete ingestion pipeline request"""
    query: str = Field(..., description="Search query")
    num_results: int = Field(default=10, ge=1, le=100, description="Number of search results")
    extraction_mode: str = Field(default="summary", description="Content extraction mode")
    request_id: Optional[str] = Field(default=None, description="Optional request ID")
    search_engines: List[str] = Field(default=["google"], description="Search engines to use")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Search filters")
    
    def generate_request_id(self) -> str:
        """Generate unique request ID if not provided"""
        if not self.request_id:
            timestamp = int(datetime.utcnow().timestamp() * 1000)
            query_hash = abs(hash(self.query)) % 10000
            self.request_id = f"ing_{timestamp}_{query_hash}"
        return self.request_id

class PipelineState(BaseModel):
    """Pipeline execution state tracking"""
    request_id: str = Field(..., description="Request identifier")
    status: PipelineStatus = Field(default=PipelineStatus.PENDING)
    current_stage: str = Field(default="initialization")
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    
    # Stage-specific tracking
    search_completed: bool = Field(default=False)
    extraction_completed: bool = Field(default=False)
    aggregation_completed: bool = Field(default=False)
    
    # Result counts
    urls_found: int = Field(default=0)
    content_extracted: int = Field(default=0)
    content_failed: int = Field(default=0)
    
    # Timing information
    started_at: datetime = Field(default_factory=datetime.utcnow)
    search_started_at: Optional[datetime] = Field(default=None)
    extraction_started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Error tracking
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    def add_error(self, error: str):
        """Add error to tracking"""
        self.errors.append(f"{datetime.utcnow().isoformat()}: {error}")
    
    def add_warning(self, warning: str):
        """Add warning to tracking"""
        self.warnings.append(f"{datetime.utcnow().isoformat()}: {warning}")
    
    def update_progress(self):
        """Update progress percentage based on completed stages"""
        completed_stages = 0
        total_stages = 3  # search, extraction, aggregation
        
        if self.search_completed:
            completed_stages += 1
        if self.extraction_completed:
            completed_stages += 1
        if self.aggregation_completed:
            completed_stages += 1
        
        self.progress_percentage = (completed_stages / total_stages) * 100

class IngestionResponse(BaseModel):
    """Complete ingestion pipeline response"""
    request_id: str = Field(..., description="Request identifier")
    status: PipelineStatus = Field(..., description="Final pipeline status")
    
    # Input data
    original_query: str = Field(..., description="Original search query")
    
    # Search results
    search_results: Dict[str, Any] = Field(default_factory=dict, description="SERP results")
    urls_found: int = Field(default=0)
    
    # Extraction results
    extraction_results: Dict[str, Any] = Field(default_factory=dict, description="Content extraction results")
    content_extracted: int = Field(default=0)
    content_failed: int = Field(default=0)
    
    # Aggregated data
    aggregated_content: List[Dict[str, Any]] = Field(default_factory=list, description="Combined results")
    high_quality_content: List[Dict[str, Any]] = Field(default_factory=list, description="High quality content")
    
    # Processing metadata
    processing_time: float = Field(default=0.0, description="Total processing time")
    stages_completed: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Storage information
    storage_paths: Dict[str, str] = Field(default_factory=dict, description="Storage locations")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def is_successful(self) -> bool:
        """Check if pipeline was successful"""
        return self.status in [PipelineStatus.COMPLETED, PipelineStatus.PARTIAL_SUCCESS]
    
    def get_success_rate(self) -> float:
        """Calculate content extraction success rate"""
        total = self.content_extracted + self.content_failed
        return (self.content_extracted / total * 100) if total > 0 else 0.0

class RetryConfig(BaseModel):
    """Retry configuration for pipeline operations"""
    max_retries: int = Field(default=3, ge=0, le=10)
    initial_delay: float = Field(default=1.0, ge=0.1, le=10.0)
    max_delay: float = Field(default=60.0, ge=1.0, le=300.0)
    exponential_base: float = Field(default=2.0, ge=1.1, le=5.0)
    retry_on_statuses: List[str] = Field(default=["failed", "timeout", "rate_limited"])
```

## ingestion_service.py
```python
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from ..stage0_serp.service import SerpService
from ..stage0_perplexity.service import PerplexityService
from .models import IngestionRequest, IngestionResponse, PipelineState, PipelineStatus, RetryConfig
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class IngestionService:
    """Main ingestion service orchestrating SERP + Perplexity pipeline"""
    
    def __init__(self):
        self.serp_service = SerpService()
        self.perplexity_service = PerplexityService()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
        self.retry_config = RetryConfig()
    
    async def process_ingestion(self, request: IngestionRequest) -> IngestionResponse:
        """Execute complete ingestion pipeline"""
        # Generate request ID
        request_id = request.generate_request_id()
        
        # Initialize pipeline state
        state = PipelineState(request_id=request_id)
        
        try:
            logger.info(f"Starting ingestion pipeline: {request_id}")
            
            # Save initial state
            await self._save_pipeline_state(state)
            
            # Stage 1: SERP Search
            search_results = await self._execute_search_stage(request, state)
            
            # Stage 2: Content Extraction
            extraction_results = await self._execute_extraction_stage(search_results, request, state)
            
            # Stage 3: Aggregation
            aggregated_results = await self._execute_aggregation_stage(search_results, extraction_results, state)
            
            # Create final response
            response = self._create_success_response(request, search_results, extraction_results, aggregated_results, state)
            
            # Mark as completed
            state.status = PipelineStatus.COMPLETED
            state.completed_at = datetime.utcnow()
            await self._save_pipeline_state(state)
            
            logger.info(f"Ingestion pipeline completed: {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Ingestion pipeline failed: {request_id} - {str(e)}")
            
            # Handle failure
            state.status = PipelineStatus.FAILED
            state.add_error(f"Pipeline failure: {str(e)}")
            state.completed_at = datetime.utcnow()
            await self._save_pipeline_state(state)
            
            return self._create_failure_response(request, state, str(e))
    
    async def _execute_search_stage(self, request: IngestionRequest, state: PipelineState) -> Dict[str, Any]:
        """Execute SERP search stage with retry logic"""
        try:
            state.current_stage = "search"
            state.search_started_at = datetime.utcnow()
            await self._save_pipeline_state(state)
            
            logger.info(f"Starting search stage: {request.request_id}")
            
            # Execute search with retry
            search_response = await self._retry_operation(
                self.serp_service.search,
                request.query,
                request.num_results
            )
            
            # Update state
            state.search_completed = True
            state.urls_found = len(search_response.results)
            state.update_progress()
            
            if state.urls_found == 0:
                state.add_warning("No search results found")
            
            await self._save_pipeline_state(state)
            
            logger.info(f"Search stage completed: {state.urls_found} URLs found")
            return search_response.dict()
            
        except Exception as e:
            state.add_error(f"Search stage failed: {str(e)}")
            await self._save_pipeline_state(state)
            raise Exception(f"Search stage failed: {str(e)}")
    
    async def _execute_extraction_stage(self, search_results: Dict[str, Any], request: IngestionRequest, state: PipelineState) -> Dict[str, Any]:
        """Execute content extraction stage"""
        try:
            state.current_stage = "extraction"
            state.extraction_started_at = datetime.utcnow()
            await self._save_pipeline_state(state)
            
            logger.info(f"Starting extraction stage: {request.request_id}")
            
            # Extract URLs from search results
            urls = [result["url"] for result in search_results.get("results", [])]
            
            if not urls:
                state.add_warning("No URLs to extract content from")
                state.extraction_completed = True
                state.update_progress()
                return {"extracted_content": [], "successful_extractions": 0, "failed_extractions": 0}
            
            # Execute extraction with retry
            extraction_response = await self._retry_operation(
                self.perplexity_service.extract_content,
                urls,
                request.request_id
            )
            
            # Update state
            state.extraction_completed = True
            state.content_extracted = extraction_response.successful_extractions
            state.content_failed = extraction_response.failed_extractions
            state.update_progress()
            
            if state.content_extracted == 0:
                state.add_warning("No content successfully extracted")
            elif state.content_failed > 0:
                state.add_warning(f"{state.content_failed} content extractions failed")
            
            await self._save_pipeline_state(state)
            
            logger.info(f"Extraction stage completed: {state.content_extracted} successful, {state.content_failed} failed")
            return extraction_response.dict()
            
        except Exception as e:
            state.add_error(f"Extraction stage failed: {str(e)}")
            await self._save_pipeline_state(state)
            raise Exception(f"Extraction stage failed: {str(e)}")
    
    async def _execute_aggregation_stage(self, search_results: Dict[str, Any], extraction_results: Dict[str, Any], state: PipelineState) -> Dict[str, Any]:
        """Execute result aggregation stage"""
        try:
            state.current_stage = "aggregation"
            await self._save_pipeline_state(state)
            
            logger.info(f"Starting aggregation stage: {state.request_id}")
            
            # Combine search and extraction results
            aggregated = self._aggregate_results(search_results, extraction_results)
            
            # Filter high-quality content
            high_quality = self._filter_high_quality_content(aggregated["combined_content"])
            
            # Store aggregated results
            await self._store_aggregated_results(state.request_id, aggregated, high_quality)
            
            # Update state
            state.aggregation_completed = True
            state.update_progress()
            await self._save_pipeline_state(state)
            
            logger.info(f"Aggregation stage completed: {len(aggregated['combined_content'])} total, {len(high_quality)} high-quality")
            
            return {
                "aggregated_content": aggregated["combined_content"],
                "high_quality_content": high_quality,
                "aggregation_metadata": aggregated["metadata"]
            }
            
        except Exception as e:
            state.add_error(f"Aggregation stage failed: {str(e)}")
            await self._save_pipeline_state(state)
            raise Exception(f"Aggregation stage failed: {str(e)}")
    
    def _aggregate_results(self, search_results: Dict[str, Any], extraction_results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine search and extraction results"""
        search_items = search_results.get("results", [])
        extracted_items = extraction_results.get("extracted_content", [])
        
        # Create URL mapping for extracted content
        extracted_by_url = {item["url"]: item for item in extracted_items}
        
        combined_content = []
        
        for search_item in search_items:
            url = search_item["url"]
            
            # Base item from search
            combined_item = {
                "url": url,
                "title": search_item.get("title", ""),
                "snippet": search_item.get("snippet", ""),
                "domain": search_item.get("domain", ""),
                "position": search_item.get("position", 0),
                "search_metadata": {
                    "search_title": search_item.get("title"),
                    "search_snippet": search_item.get("snippet"),
                    "search_position": search_item.get("position")
                }
            }
            
            # Add extracted content if available
            if url in extracted_by_url:
                extracted = extracted_by_url[url]
                combined_item.update({
                    "content": extracted.get("content", ""),
                    "extracted_title": extracted.get("title", ""),
                    "author": extracted.get("author"),
                    "published_date": extracted.get("published_date"),
                    "word_count": extracted.get("word_count", 0),
                    "extraction_confidence": extracted.get("extraction_confidence", 0.0),
                    "content_metadata": extracted.get("metadata", {}),
                    "has_extracted_content": True
                })
            else:
                combined_item.update({
                    "content": "",
                    "has_extracted_content": False,
                    "extraction_confidence": 0.0
                })
            
            combined_content.append(combined_item)
        
        return {
            "combined_content": combined_content,
            "metadata": {
                "total_search_results": len(search_items),
                "total_extracted": len(extracted_items),
                "combined_items": len(combined_content),
                "extraction_success_rate": len(extracted_items) / len(search_items) * 100 if search_items else 0
            }
        }
    
    def _filter_high_quality_content(self, combined_content: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter for high-quality content"""
        high_quality = []
        
        for item in combined_content:
            if self._is_high_quality_item(item):
                high_quality.append(item)
        
        return high_quality
    
    def _is_high_quality_item(self, item: Dict[str, Any]) -> bool:
        """Check if item meets high-quality criteria"""
        # Must have extracted content
        if not item.get("has_extracted_content", False):
            return False
        
        # Minimum confidence threshold
        if item.get("extraction_confidence", 0.0) < 0.7:
            return False
        
        # Minimum content length
        if item.get("word_count", 0) < 100:
            return False
        
        # Must have meaningful title
        title = item.get("extracted_title") or item.get("title", "")
        if not title or len(title.strip()) < 10:
            return False
        
        return True
    
    async def _retry_operation(self, operation, *args, **kwargs):
        """Execute operation with retry logic"""
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                return await operation(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                if attempt == self.retry_config.max_retries:
                    break
                
                # Calculate delay
                delay = min(
                    self.retry_config.initial_delay * (self.retry_config.exponential_base ** attempt),
                    self.retry_config.max_delay
                )
                
                logger.warning(f"Operation failed (attempt {attempt + 1}), retrying in {delay}s: {str(e)}")
                await asyncio.sleep(delay)
        
        raise last_exception
    
    async def _save_pipeline_state(self, state: PipelineState):
        """Save pipeline state to database"""
        try:
            await self.database_client.save_item("pipeline_states", state.dict())
        except Exception as e:
            logger.error(f"Failed to save pipeline state: {str(e)}")
    
    async def _store_aggregated_results(self, request_id: str, aggregated: Dict[str, Any], high_quality: List[Dict[str, Any]]):
        """Store aggregated results"""
        try:
            # Store combined results
            await self.storage_client.save_json(f"aggregated_results/{request_id}/combined.json", aggregated)
            
            # Store high-quality content separately
            await self.storage_client.save_json(f"aggregated_results/{request_id}/high_quality.json", high_quality)
            
        except Exception as e:
            logger.error(f"Failed to store aggregated results: {str(e)}")
    
    def _create_success_response(self, request: IngestionRequest, search_results: Dict[str, Any], extraction_results: Dict[str, Any], aggregated_results: Dict[str, Any], state: PipelineState) -> IngestionResponse:
        """Create successful response"""
        processing_time = (datetime.utcnow() - state.started_at).total_seconds()
        
        # Determine final status
        final_status = PipelineStatus.COMPLETED
        if state.content_failed > 0 and state.content_extracted > 0:
            final_status = PipelineStatus.PARTIAL_SUCCESS
        
        return IngestionResponse(
            request_id=state.request_id,
            status=final_status,
            original_query=request.query,
            search_results=search_results,
            urls_found=state.urls_found,
            extraction_results=extraction_results,
            content_extracted=state.content_extracted,
            content_failed=state.content_failed,
            aggregated_content=aggregated_results.get("aggregated_content", []),
            high_quality_content=aggregated_results.get("high_quality_content", []),
            processing_time=processing_time,
            stages_completed=["search", "extraction", "aggregation"],
            errors=state.errors,
            warnings=state.warnings,
            storage_paths={
                "combined_results": f"aggregated_results/{state.request_id}/combined.json",
                "high_quality_results": f"aggregated_results/{state.request_id}/high_quality.json"
            }
        )
    
    def _create_failure_response(self, request: IngestionRequest, state: PipelineState, error_message: str) -> IngestionResponse:
        """Create failure response"""
        processing_time = (datetime.utcnow() - state.started_at).total_seconds()
        
        return IngestionResponse(
            request_id=state.request_id,
            status=PipelineStatus.FAILED,
            original_query=request.query,
            processing_time=processing_time,
            errors=state.errors + [error_message],
            warnings=state.warnings
        )
```

## workflow_manager.py
```python
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ...config.service_factory import ServiceFactory
from .models import PipelineState, PipelineStatus
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class WorkflowManager:
    """Manage pipeline workflows and state transitions"""
    
    def __init__(self):
        self.database_client = ServiceFactory.get_database_client()
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def get_pipeline_status(self, request_id: str) -> Optional[PipelineState]:
        """Get current pipeline status"""
        try:
            state_data = await self.database_client.get_item("pipeline_states", {"request_id": request_id})
            
            if state_data:
                return PipelineState(**state_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {str(e)}")
            return None
    
    async def list_active_pipelines(self) -> List[PipelineState]:
        """List all active (non-completed) pipelines"""
        try:
            # Query for active pipelines
            active_statuses = [PipelineStatus.PENDING, PipelineStatus.SEARCHING, PipelineStatus.EXTRACTING, PipelineStatus.AGGREGATING]
            
            all_states = []
            for status in active_statuses:
                states = await self.database_client.query_items(
                    "pipeline_states",
                    IndexName="status-index",  # Assuming GSI exists
                    KeyConditionExpression="status = :status",
                    ExpressionAttributeValues={":status": status.value}
                )
                all_states.extend(states)
            
            return [PipelineState(**state) for state in all_states]
            
        except Exception as e:
            logger.error(f"Failed to list active pipelines: {str(e)}")
            return []
    
    async def cleanup_stale_pipelines(self, max_age_hours: int = 24) -> int:
        """Clean up stale/stuck pipelines"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            active_pipelines = await self.list_active_pipelines()
            
            cleaned_count = 0
            
            for pipeline in active_pipelines:
                if pipeline.started_at < cutoff_time:
                    logger.warning(f"Marking stale pipeline as failed: {pipeline.request_id}")
                    
                    # Update to failed status
                    pipeline.status = PipelineStatus.FAILED
                    pipeline.add_error(f"Pipeline marked as stale after {max_age_hours} hours")
                    pipeline.completed_at = datetime.utcnow()
                    
                    await self.database_client.save_item("pipeline_states", pipeline.dict())
                    cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} stale pipelines")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup stale pipelines: {str(e)}")
            return 0
    
    async def get_pipeline_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get pipeline execution statistics"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Get all recent pipelines
            recent_pipelines = await self.database_client.query_items(
                "pipeline_states",
                IndexName="created_at-index",  # Assuming GSI exists
                KeyConditionExpression="created_at > :cutoff",
                ExpressionAttributeValues={":cutoff": cutoff_time.isoformat()}
            )
            
            stats = {
                "total_pipelines": len(recent_pipelines),
                "completed": 0,
                "failed": 0,
                "partial_success": 0,
                "active": 0,
                "average_processing_time": 0.0,
                "success_rate": 0.0,
                "total_urls_processed": 0,
                "total_content_extracted": 0
            }
            
            processing_times = []
            
            for pipeline_data in recent_pipelines:
                pipeline = PipelineState(**pipeline_data)
                
                if pipeline.status == PipelineStatus.COMPLETED:
                    stats["completed"] += 1
                elif pipeline.status == PipelineStatus.FAILED:
                    stats["failed"] += 1
                elif pipeline.status == PipelineStatus.PARTIAL_SUCCESS:
                    stats["partial_success"] += 1
                else:
                    stats["active"] += 1
                
                stats["total_urls_processed"] += pipeline.urls_found
                stats["total_content_extracted"] += pipeline.content_extracted
                
                # Calculate processing time for completed pipelines
                if pipeline.completed_at and pipeline.started_at:
                    processing_time = (pipeline.completed_at - pipeline.started_at).total_seconds()
                    processing_times.append(processing_time)
            
            # Calculate averages
            if processing_times:
                stats["average_processing_time"] = sum(processing_times) / len(processing_times)
            
            completed_count = stats["completed"] + stats["partial_success"]
            if stats["total_pipelines"] > 0:
                stats["success_rate"] = (completed_count / stats["total_pipelines"]) * 100
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get pipeline statistics: {str(e)}")
            return {}
    
    async def retry_failed_pipeline(self, request_id: str) -> bool:
        """Retry a failed pipeline"""
        try:
            pipeline = await self.get_pipeline_status(request_id)
            
            if not pipeline:
                logger.error(f"Pipeline not found: {request_id}")
                return False
            
            if pipeline.status != PipelineStatus.FAILED:
                logger.error(f"Pipeline is not in failed state: {request_id}")
                return False
            
            # Reset pipeline state for retry
            pipeline.status = PipelineStatus.PENDING
            pipeline.current_stage = "initialization"
            pipeline.progress_percentage = 0.0
            pipeline.search_completed = False
            pipeline.extraction_completed = False
            pipeline.aggregation_completed = False
            pipeline.completed_at = None
            
            # Clear previous errors but keep them in history
            pipeline.errors = [f"RETRY - Previous errors: {'; '.join(pipeline.errors)}"]
            pipeline.warnings = []
            
            # Save updated state
            await self.database_client.save_item("pipeline_states", pipeline.dict())
            
            logger.info(f"Pipeline marked for retry: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to retry pipeline: {str(e)}")
            return False
    
    async def cancel_pipeline(self, request_id: str) -> bool:
        """Cancel an active pipeline"""
        try:
            pipeline = await self.get_pipeline_status(request_id)
            
            if not pipeline:
                logger.error(f"Pipeline not found: {request_id}")
                return False
            
            if pipeline.status in [PipelineStatus.COMPLETED, PipelineStatus.FAILED]:
                logger.error(f"Cannot cancel completed/failed pipeline: {request_id}")
                return False
            
            # Update to failed status with cancellation reason
            pipeline.status = PipelineStatus.FAILED
            pipeline.add_error("Pipeline cancelled by user")
            pipeline.completed_at = datetime.utcnow()
            
            await self.database_client.save_item("pipeline_states", pipeline.dict())
            
            logger.info(f"Pipeline cancelled: {request_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel pipeline: {str(e)}")
            return False
```

## service.py
```python
from typing import List, Dict, Any, Optional
from .ingestion_service import IngestionService
from .workflow_manager import WorkflowManager
from .models import IngestionRequest, IngestionResponse, PipelineState
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OrchestratorService:
    """Main orchestrator service providing unified interface"""
    
    def __init__(self):
        self.ingestion_service = IngestionService()
        self.workflow_manager = WorkflowManager()
    
    async def process_request(self, query: str, num_results: int = 10, **kwargs) -> IngestionResponse:
        """Process complete ingestion request"""
        try:
            request = IngestionRequest(
                query=query,
                num_results=num_results,
                **kwargs
            )
            
            logger.info(f"Processing orchestrator request: {query}")
            
            return await self.ingestion_service.process_ingestion(request)
            
        except Exception as e:
            logger.error(f"Orchestrator request failed: {str(e)}")
            raise
    
    async def get_status(self, request_id: str) -> Optional[PipelineState]:
        """Get pipeline status"""
        return await self.workflow_manager.get_pipeline_status(request_id)
    
    async def list_active_requests(self) -> List[PipelineState]:
        """List active pipeline requests"""
        return await self.workflow_manager.list_active_pipelines()
    
    async def retry_request(self, request_id: str) -> bool:
        """Retry failed request"""
        return await self.workflow_manager.retry_failed_pipeline(request_id)
    
    async def cancel_request(self, request_id: str) -> bool:
        """Cancel active request"""
        return await self.workflow_manager.cancel_pipeline(request_id)
    
    async def get_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get processing statistics"""
        return await self.workflow_manager.get_pipeline_statistics(days)
    
    async def cleanup_stale_requests(self, max_age_hours: int = 24) -> int:
        """Clean up stale requests"""
        return await self.workflow_manager.cleanup_stale_pipelines(max_age_hours)
```

## storage.py
```python
from typing import Dict, Any, List, Optional
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OrchestratorStorage:
    """Handle orchestrator-specific storage operations"""
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def save_pipeline_results(self, request_id: str, results: Dict[str, Any]) -> bool:
        """Save complete pipeline results"""
        try:
            key = f"pipeline_results/{request_id}/complete.json"
            success = await self.storage_client.save_json(key, results)
            
            if success:
                logger.info(f"Saved pipeline results: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Pipeline results save error: {str(e)}")
            return False
    
    async def save_stage_results(self, request_id: str, stage: str, results: Dict[str, Any]) -> bool:
        """Save individual stage results"""
        try:
            key = f"pipeline_results/{request_id}/{stage}.json"
            success = await self.storage_client.save_json(key, results)
            
            if success:
                logger.debug(f"Saved stage results: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Stage results save error: {str(e)}")
            return False
    
    async def load_pipeline_results(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Load complete pipeline results"""
        try:
            key = f"pipeline_results/{request_id}/complete.json"
            results = await self.storage_client.load_json(key)
            
            if results:
                logger.info(f"Loaded pipeline results: {key}")
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline results load error: {str(e)}")
            return None
```

## database.py
```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OrchestratorDatabase:
    """Handle orchestrator database operations"""
    
    def __init__(self):
        self.db_client = ServiceFactory.get_database_client()
    
    async def save_pipeline_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save pipeline execution metadata"""
        try:
            table_name = "pipeline_executions"
            
            if 'created_at' not in metadata:
                metadata['created_at'] = datetime.utcnow().isoformat()
            
            success = await self.db_client.save_item(table_name, metadata)
            
            if success:
                logger.info(f"Saved pipeline metadata: {metadata.get('request_id')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Pipeline metadata save error: {str(e)}")
            return False
    
    async def get_pipeline_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent pipeline execution history"""
        try:
            table_name = "pipeline_executions"
            
            history = await self.db_client.query_items(
                table_name,
                IndexName="created_at-index",
                ScanIndexForward=False,
                Limit=limit
            )
            
            logger.info(f"Retrieved {len(history)} pipeline history records")
            return history
            
        except Exception as e:
            logger.error(f"Pipeline history query error: {str(e)}")
            return []
```