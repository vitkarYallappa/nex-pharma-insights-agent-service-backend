import json
from typing import Dict, Any, Optional
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
                logger.error(f"Failed to save SERP results: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"SERP storage error: {str(e)}")
            return False
    
    async def load_search_results(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Load search results from storage"""
        try:
            key = f"serp_results/{request_id}.json"
            results = await self.storage_client.load_json(key)
            
            if results:
                logger.info(f"Loaded SERP results: {key}")
            else:
                logger.warning(f"No SERP results found: {key}")
            
            return results
            
        except Exception as e:
            logger.error(f"SERP load error: {str(e)}")
            return None
    
    async def save_raw_response(self, request_id: str, raw_data: str) -> bool:
        """Save raw API response for debugging"""
        try:
            key = f"serp_raw/{request_id}.txt"
            success = await self.storage_client.save_text(key, raw_data)
            
            if success:
                logger.debug(f"Saved raw SERP response: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Raw SERP save error: {str(e)}")
            return False

class Stage0SerpStorage:
    """Storage operations for stage0_serp with enhanced functionality"""
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
        self.serp_storage = SerpStorage()
    
    async def save_result(self, request_id: str, data: dict) -> bool:
        """Save processing result with enhanced storage"""
        try:
            # Save to legacy location for backward compatibility
            object_key = f"stage0_serp/results/{request_id}.json"
            content = json.dumps(data).encode('utf-8')
            
            legacy_success = await self.storage_client.upload_content(
                content=content,
                object_key=object_key,
                content_type='application/json'
            )
            
            # Also save using new SERP storage format if data contains search results
            if 'search_results' in data:
                serp_success = await self.serp_storage.save_search_results(
                    request_id, 
                    data['search_results']
                )
                return legacy_success and serp_success
            
            return legacy_success
            
        except Exception as e:
            logger.error(f"Stage0 SERP storage error: {str(e)}")
            return False
    
    async def load_result(self, request_id: str) -> dict:
        """Load processing result with fallback to enhanced storage"""
        try:
            # Try legacy location first
            object_key = f"stage0_serp/results/{request_id}.json"
            content = await self.storage_client.get_content(object_key)
            
            if content:
                return json.loads(content.decode('utf-8'))
            
            # Fallback to new SERP storage format
            serp_results = await self.serp_storage.load_search_results(request_id)
            if serp_results:
                return {
                    "request_id": request_id,
                    "search_results": serp_results,
                    "message": "Loaded from enhanced SERP storage"
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Stage0 SERP load error: {str(e)}")
            return {}
    
    async def save_search_metadata(self, request_id: str, metadata: Dict[str, Any]) -> bool:
        """Save search metadata"""
        try:
            key = f"stage0_serp/metadata/{request_id}.json"
            content = json.dumps(metadata).encode('utf-8')
            
            success = await self.storage_client.upload_content(
                content=content,
                object_key=key,
                content_type='application/json'
            )
            
            if success:
                logger.info(f"Saved SERP metadata: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"SERP metadata storage error: {str(e)}")
            return False
    
    async def load_search_metadata(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Load search metadata"""
        try:
            key = f"stage0_serp/metadata/{request_id}.json"
            content = await self.storage_client.get_content(key)
            
            if content:
                metadata = json.loads(content.decode('utf-8'))
                logger.info(f"Loaded SERP metadata: {key}")
                return metadata
            
            return None
            
        except Exception as e:
            logger.error(f"SERP metadata load error: {str(e)}")
            return None
