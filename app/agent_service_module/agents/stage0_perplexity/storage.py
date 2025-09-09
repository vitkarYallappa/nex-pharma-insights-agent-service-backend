from typing import Dict, Any, List, Optional
import json
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityStorage:
    """Handle Perplexity-specific storage operations"""
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def save_extraction_results(self, request_id: str, results: Dict[str, Any]) -> bool:
        """Save extraction results to storage"""
        try:
            key = f"perplexity_results/{request_id}.json"
            success = await self.storage_client.save_json(key, results)
            
            if success:
                logger.info(f"Saved Perplexity results: {key}")
            else:
                logger.error(f"Failed to save results: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Perplexity storage error: {str(e)}")
            return False
    
    async def save_individual_content(self, request_id: str, content_list: List[Dict[str, Any]]) -> bool:
        """Save individual content items"""
        try:
            success_count = 0
            
            for i, content in enumerate(content_list):
                key = f"perplexity_content/{request_id}/{i}.json"
                if await self.storage_client.save_json(key, content):
                    success_count += 1
            
            logger.info(f"Saved {success_count}/{len(content_list)} content items")
            return success_count == len(content_list)
            
        except Exception as e:
            logger.error(f"Content storage error: {str(e)}")
            return False
    
    async def load_extraction_results(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Load extraction results from storage"""
        try:
            key = f"perplexity_results/{request_id}.json"
            results = await self.storage_client.load_json(key)
            
            if results:
                logger.info(f"Loaded Perplexity results: {key}")
            else:
                logger.warning(f"No results found: {key}")
            
            return results
            
        except Exception as e:
            logger.error(f"Perplexity load error: {str(e)}")
            return None
    
    async def save_raw_content(self, request_id: str, url: str, raw_content: str) -> bool:
        """Save raw extracted content for debugging"""
        try:
            # Create safe filename from URL
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()
            key = f"perplexity_raw/{request_id}/{url_hash}.txt"
            
            success = await self.storage_client.save_text(key, raw_content)
            
            if success:
                logger.debug(f"Saved raw content: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Raw content save error: {str(e)}")
            return False
