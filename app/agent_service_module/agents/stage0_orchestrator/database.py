from typing import Dict, Any, List, Optional
from datetime import datetime
from ...shared.database.base_repository import BaseRepository
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


class Stage0OrchestratorRepository(BaseRepository):
    """Legacy database operations for stage0_orchestrator - maintained for backward compatibility"""
    
    def __init__(self):
        super().__init__(table_name="stage0_orchestrator_data")
    
    def get_table_name(self) -> str:
        return "stage0_orchestrator_data"
    
    async def save_request(self, request_data: dict) -> bool:
        """Save request data."""
        try:
            return await self.create(request_data)
        except Exception as e:
            logger.error(f"Legacy save request error: {str(e)}")
            return False
    
    async def get_request(self, request_id: str) -> dict:
        """Get request data."""
        try:
            return await self.get_by_id(request_id)
        except Exception as e:
            logger.error(f"Legacy get request error: {str(e)}")
            return {}
    
    async def update_status(self, request_id: str, status: str) -> bool:
        """Update request status."""
        try:
            request_data = await self.get_by_id(request_id)
            if request_data:
                request_data['status'] = status
                request_data['updated_at'] = datetime.utcnow().isoformat()
                return await self.update(request_data)
            return False
        except Exception as e:
            logger.error(f"Legacy update status error: {str(e)}")
            return False
