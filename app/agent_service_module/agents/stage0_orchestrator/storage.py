from typing import Dict, Any, List, Optional
import json
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
