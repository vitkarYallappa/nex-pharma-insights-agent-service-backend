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