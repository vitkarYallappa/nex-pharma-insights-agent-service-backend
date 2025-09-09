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
