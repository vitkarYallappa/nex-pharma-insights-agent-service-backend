import json
from typing import Dict, Any, List, Optional
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SerpStorage:
    """Handle SERP-specific storage operations"""
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def save_search_results(self, request_id: str, results: Dict[str, Any]) -> bool:
        """Save search results to storage"""
        try:
            key = f"serp_results/{request_id}.json"
            success = await self.storage_client.save_json(key, results)
            
            if success:
                logger.info(f"Saved SERP results: {key}")
            else:
                logger.error(f"Failed to save results: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"SERP storage error: {str(e)}")
            return False
    
    async def save_individual_results(self, request_id: str, results_list: List[Dict[str, Any]]) -> bool:
        """Save individual search results"""
        try:
            success_count = 0
            
            for i, result in enumerate(results_list):
                key = f"serp_individual/{request_id}/{i}.json"
                if await self.storage_client.save_json(key, result):
                    success_count += 1
            
            logger.info(f"Saved {success_count}/{len(results_list)} individual results")
            return success_count == len(results_list)
            
        except Exception as e:
            logger.error(f"Individual results storage error: {str(e)}")
            return False
    
    async def load_search_results(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Load search results from storage"""
        try:
            key = f"serp_results/{request_id}.json"
            results = await self.storage_client.load_json(key)
            
            if results:
                logger.info(f"Loaded SERP results: {key}")
            else:
                logger.warning(f"No results found: {key}")
            
            return results
            
        except Exception as e:
            logger.error(f"SERP load error: {str(e)}")
            return None
    
    async def save_raw_response(self, request_id: str, raw_response: str) -> bool:
        """Save raw API response for debugging"""
        try:
            key = f"serp_raw/{request_id}.json"
            success = await self.storage_client.save_text(key, raw_response)
            
            if success:
                logger.debug(f"Saved raw response: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Raw response save error: {str(e)}")
            return False
