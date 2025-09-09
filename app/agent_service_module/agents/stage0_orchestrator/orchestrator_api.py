from typing import Dict, Any, Optional, List
from .service import OrchestratorService
from .models import IngestionRequest, IngestionResponse, PipelineState
from ...config.settings import settings
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OrchestratorAPI:
    """External API interface for Orchestrator operations"""
    
    def __init__(self):
        self.orchestrator_service = OrchestratorService()
        self.api_key = getattr(settings, 'ORCHESTRATOR_API_KEY', None)
    
    async def process_ingestion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ingestion request via API"""
        try:
            # Validate API key if configured
            if self.api_key and data.get('api_key') != self.api_key:
                return {
                    "status": "error",
                    "error": "Invalid API key",
                    "error_code": "UNAUTHORIZED"
                }
            
            # Extract request parameters
            query = data.get('query')
            if not query:
                return {
                    "status": "error",
                    "error": "Query parameter is required",
                    "error_code": "MISSING_QUERY"
                }
            
            num_results = data.get('num_results', 10)
            extraction_mode = data.get('extraction_mode', 'summary')
            request_id = data.get('request_id')
            
            logger.info(f"API ingestion request: {query}")
            
            # Process through orchestrator service
            response = await self.orchestrator_service.process_request(
                query=query,
                num_results=num_results,
                extraction_mode=extraction_mode,
                request_id=request_id
            )
            
            return {
                "status": "success",
                "data": response.dict()
            }
            
        except Exception as e:
            logger.error(f"API ingestion error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "PROCESSING_ERROR"
            }
    
    async def get_pipeline_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get pipeline status via API"""
        try:
            # Validate API key if configured
            if self.api_key and data.get('api_key') != self.api_key:
                return {
                    "status": "error",
                    "error": "Invalid API key",
                    "error_code": "UNAUTHORIZED"
                }
            
            request_id = data.get('request_id')
            if not request_id:
                return {
                    "status": "error",
                    "error": "Request ID parameter is required",
                    "error_code": "MISSING_REQUEST_ID"
                }
            
            pipeline_state = await self.orchestrator_service.get_status(request_id)
            
            if pipeline_state:
                return {
                    "status": "success",
                    "data": pipeline_state.dict()
                }
            else:
                return {
                    "status": "error",
                    "error": "Pipeline not found",
                    "error_code": "NOT_FOUND"
                }
                
        except Exception as e:
            logger.error(f"API status check error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "STATUS_ERROR"
            }
    
    async def list_active_pipelines(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """List active pipelines via API"""
        try:
            # Validate API key if configured
            if self.api_key and data.get('api_key') != self.api_key:
                return {
                    "status": "error",
                    "error": "Invalid API key",
                    "error_code": "UNAUTHORIZED"
                }
            
            active_pipelines = await self.orchestrator_service.list_active_requests()
            
            return {
                "status": "success",
                "data": {
                    "active_pipelines": [pipeline.dict() for pipeline in active_pipelines],
                    "count": len(active_pipelines)
                }
            }
            
        except Exception as e:
            logger.error(f"API list active error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "LIST_ERROR"
            }
    
    async def get_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get pipeline statistics via API"""
        try:
            # Validate API key if configured
            if self.api_key and data.get('api_key') != self.api_key:
                return {
                    "status": "error",
                    "error": "Invalid API key",
                    "error_code": "UNAUTHORIZED"
                }
            
            days = data.get('days', 7)
            stats = await self.orchestrator_service.get_statistics(days)
            
            return {
                "status": "success",
                "data": stats
            }
            
        except Exception as e:
            logger.error(f"API statistics error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "STATS_ERROR"
            }
    
    async def retry_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Retry failed pipeline via API"""
        try:
            # Validate API key if configured
            if self.api_key and data.get('api_key') != self.api_key:
                return {
                    "status": "error",
                    "error": "Invalid API key",
                    "error_code": "UNAUTHORIZED"
                }
            
            request_id = data.get('request_id')
            if not request_id:
                return {
                    "status": "error",
                    "error": "Request ID parameter is required",
                    "error_code": "MISSING_REQUEST_ID"
                }
            
            success = await self.orchestrator_service.retry_request(request_id)
            
            return {
                "status": "success",
                "data": {
                    "retry_initiated": success,
                    "request_id": request_id
                }
            }
            
        except Exception as e:
            logger.error(f"API retry error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "RETRY_ERROR"
            }
    
    async def cancel_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel active pipeline via API"""
        try:
            # Validate API key if configured
            if self.api_key and data.get('api_key') != self.api_key:
                return {
                    "status": "error",
                    "error": "Invalid API key",
                    "error_code": "UNAUTHORIZED"
                }
            
            request_id = data.get('request_id')
            if not request_id:
                return {
                    "status": "error",
                    "error": "Request ID parameter is required",
                    "error_code": "MISSING_REQUEST_ID"
                }
            
            success = await self.orchestrator_service.cancel_request(request_id)
            
            return {
                "status": "success",
                "data": {
                    "cancellation_initiated": success,
                    "request_id": request_id
                }
            }
            
        except Exception as e:
            logger.error(f"API cancel error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "CANCEL_ERROR"
            }
    
    async def call_api(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic API call handler"""
        try:
            if operation == "process_ingestion":
                return await self.process_ingestion(data)
            elif operation == "get_status":
                return await self.get_pipeline_status(data)
            elif operation == "list_active":
                return await self.list_active_pipelines(data)
            elif operation == "get_statistics":
                return await self.get_statistics(data)
            elif operation == "retry_pipeline":
                return await self.retry_pipeline(data)
            elif operation == "cancel_pipeline":
                return await self.cancel_pipeline(data)
            else:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}",
                    "error_code": "UNKNOWN_OPERATION"
                }
                
        except Exception as e:
            logger.error(f"API call error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "API_ERROR"
            }
