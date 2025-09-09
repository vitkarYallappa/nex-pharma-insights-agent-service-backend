import asyncio
from typing import Dict, Any
from datetime import datetime
from .models import IngestionResponse, PipelineStatus, PipelineState
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OrchestratorMock:
    """Mock Orchestrator implementation for testing"""
    
    def __init__(self):
        self.mock_pipelines = {}  # Store mock pipeline states
    
    async def process_ingestion(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock ingestion processing"""
        await asyncio.sleep(0.5)  # Simulate processing time
        
        query = data.get('query', 'mock query')
        num_results = data.get('num_results', 10)
        request_id = f"mock_{int(datetime.utcnow().timestamp() * 1000)}"
        
        logger.info(f"Mock orchestrator processing: {query}")
        
        # Simulate successful pipeline execution
        mock_response = IngestionResponse(
            request_id=request_id,
            status=PipelineStatus.COMPLETED,
            original_query=query,
            search_results={
                "query": query,
                "results": [
                    {
                        "title": f"Mock Result {i+1} for {query}",
                        "url": f"https://example.com/mock-result-{i+1}",
                        "snippet": f"Mock snippet for result {i+1} related to {query}",
                        "domain": "example.com",
                        "position": i+1
                    }
                    for i in range(min(num_results, 5))  # Limit mock results
                ]
            },
            urls_found=min(num_results, 5),
            extraction_results={
                "extracted_content": [
                    {
                        "url": f"https://example.com/mock-result-{i+1}",
                        "title": f"Mock Content Title {i+1}",
                        "content": f"This is mock extracted content for result {i+1}. It contains relevant information about {query} and demonstrates the content extraction capabilities of the system.",
                        "word_count": 25,
                        "extraction_confidence": 0.85,
                        "author": "Mock Author",
                        "language": "en",
                        "content_type": "article"
                    }
                    for i in range(min(num_results, 3))  # Some extractions fail in mock
                ]
            },
            content_extracted=min(num_results, 3),
            content_failed=max(0, min(num_results, 5) - 3),
            aggregated_content=[
                {
                    "url": f"https://example.com/mock-result-{i+1}",
                    "title": f"Mock Result {i+1} for {query}",
                    "content": f"Mock extracted content for result {i+1}",
                    "has_extracted_content": i < 3,
                    "extraction_confidence": 0.85 if i < 3 else 0.0,
                    "search_metadata": {"position": i+1}
                }
                for i in range(min(num_results, 5))
            ],
            high_quality_content=[
                {
                    "url": f"https://example.com/mock-result-{i+1}",
                    "title": f"High Quality Mock Result {i+1}",
                    "content": f"High quality mock content for {query}",
                    "extraction_confidence": 0.9,
                    "word_count": 150
                }
                for i in range(min(2, num_results))  # Only first 2 are high quality
            ],
            processing_time=0.5,
            stages_completed=["search", "extraction", "aggregation"],
            storage_paths={
                "combined_results": f"mock/aggregated_results/{request_id}/combined.json",
                "high_quality_results": f"mock/aggregated_results/{request_id}/high_quality.json"
            }
        )
        
        # Store mock pipeline state
        self.mock_pipelines[request_id] = PipelineState(
            request_id=request_id,
            status=PipelineStatus.COMPLETED,
            current_stage="completed",
            progress_percentage=100.0,
            search_completed=True,
            extraction_completed=True,
            aggregation_completed=True,
            urls_found=min(num_results, 5),
            content_extracted=min(num_results, 3),
            content_failed=max(0, min(num_results, 5) - 3),
            completed_at=datetime.utcnow()
        )
        
        return {
            "status": "success",
            "data": mock_response.dict()
        }
    
    async def get_pipeline_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock pipeline status retrieval"""
        request_id = data.get('request_id')
        
        if request_id in self.mock_pipelines:
            return {
                "status": "success",
                "data": self.mock_pipelines[request_id].dict()
            }
        else:
            return {
                "status": "error",
                "error": "Pipeline not found",
                "error_code": "NOT_FOUND"
            }
    
    async def list_active_pipelines(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock active pipelines listing"""
        # Return some mock active pipelines
        active_pipelines = [
            pipeline.dict() for pipeline in self.mock_pipelines.values()
            if pipeline.status in [PipelineStatus.PENDING, PipelineStatus.SEARCHING, PipelineStatus.EXTRACTING]
        ]
        
        return {
            "status": "success",
            "data": {
                "active_pipelines": active_pipelines,
                "count": len(active_pipelines)
            }
        }
    
    async def get_statistics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock statistics"""
        return {
            "status": "success",
            "data": {
                "total_pipelines": len(self.mock_pipelines),
                "completed": len([p for p in self.mock_pipelines.values() if p.status == PipelineStatus.COMPLETED]),
                "failed": 0,
                "partial_success": 0,
                "active": 0,
                "average_processing_time": 0.5,
                "success_rate": 100.0,
                "total_urls_processed": sum(p.urls_found for p in self.mock_pipelines.values()),
                "total_content_extracted": sum(p.content_extracted for p in self.mock_pipelines.values())
            }
        }
    
    async def retry_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock pipeline retry"""
        request_id = data.get('request_id')
        
        return {
            "status": "success",
            "data": {
                "retry_initiated": True,
                "request_id": request_id
            }
        }
    
    async def cancel_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock pipeline cancellation"""
        request_id = data.get('request_id')
        
        if request_id in self.mock_pipelines:
            self.mock_pipelines[request_id].status = PipelineStatus.FAILED
            self.mock_pipelines[request_id].add_error("Pipeline cancelled by user (mock)")
        
        return {
            "status": "success",
            "data": {
                "cancellation_initiated": True,
                "request_id": request_id
            }
        }
    
    async def call_api(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock API call handler"""
        logger.info(f"Mock Orchestrator API call: {operation}")
        
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
            logger.error(f"Mock API error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "error_code": "MOCK_ERROR"
            }
