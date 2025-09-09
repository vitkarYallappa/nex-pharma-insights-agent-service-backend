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