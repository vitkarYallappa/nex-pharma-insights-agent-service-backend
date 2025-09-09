from typing import List, Dict, Any, Optional
from .ingestion_service import IngestionService
from .workflow_manager import WorkflowManager
from .models import IngestionRequest, IngestionResponse, PipelineState, Stage0OrchestratorRequest, Stage0OrchestratorResponse
from ...config.service_factory import ServiceFactory
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


class Stage0OrchestratorService:
    """Legacy service for backward compatibility"""
    
    def __init__(self):
        self.orchestrator_service = OrchestratorService()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process(self, request: Stage0OrchestratorRequest) -> Stage0OrchestratorResponse:
        """Process the stage0_orchestrator request - legacy compatibility method"""
        try:
            # For backward compatibility, we'll use the new orchestrator service internally
            # but maintain the old interface
            logger.info(f"Legacy orchestrator processing for request: {request.request_id}")
            
            # Extract query from content or use a default
            query = request.content if request.content else "pharmaceutical AI regulation"
            
            # Process through new orchestrator
            try:
                response = await self.orchestrator_service.process_request(
                    query=query,
                    num_results=5  # Conservative for legacy requests
                )
                
                # Convert to legacy format
                result = {
                    "message": "Processing stage0_orchestrator request completed",
                    "request_id": request.request_id,
                    "pipeline_request_id": response.request_id,
                    "query_processed": query,
                    "urls_found": response.urls_found,
                    "content_extracted": response.content_extracted,
                    "processing_time": response.processing_time,
                    "status": response.status.value,
                    "timestamp": request.timestamp.isoformat()
                }
                
                return Stage0OrchestratorResponse(
                    request_id=request.request_id,
                    result=result,
                    status="completed"
                )
                
            except Exception as e:
                # Fallback for legacy compatibility
                logger.warning(f"New orchestrator failed for legacy request, using fallback: {str(e)}")
                
                result = {
                    "message": "Processing stage0_orchestrator request (fallback mode)",
                    "request_id": request.request_id,
                    "content_processed": len(request.content),
                    "timestamp": request.timestamp.isoformat(),
                    "fallback_reason": str(e)
                }
                
                return Stage0OrchestratorResponse(
                    request_id=request.request_id,
                    result=result,
                    status="completed"
                )
            
        except Exception as e:
            logger.error(f"Legacy orchestrator processing error: {str(e)}")
            return Stage0OrchestratorResponse(
                request_id=request.request_id,
                result={"error": str(e)},
                status="failed"
            )
