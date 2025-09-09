from typing import Dict, Any, List, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SerpDatabase:
    """Handle SERP database operations"""
    
    def __init__(self):
        self.db_client = ServiceFactory.get_database_client()
        self.table_name = "serp_requests"
    
    async def save_search_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save search metadata"""
        try:
            if 'created_at' not in metadata:
                metadata['created_at'] = datetime.utcnow().isoformat()
            
            success = await self.db_client.save_item(self.table_name, metadata)
            
            if success:
                logger.info(f"Saved search metadata: {metadata.get('request_id')}")
            else:
                logger.error(f"Failed to save metadata: {metadata.get('request_id')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Search metadata save error: {str(e)}")
            return False
    
    async def get_search_metadata(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get search metadata by request ID"""
        try:
            key = {"request_id": request_id}
            metadata = await self.db_client.get_item(self.table_name, key)
            
            if metadata:
                logger.info(f"Retrieved search metadata: {request_id}")
            else:
                logger.warning(f"No metadata found: {request_id}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Search metadata get error: {str(e)}")
            return None
    
    async def get_search_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get search statistics"""
        try:
            from datetime import timedelta
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Get recent searches
            recent_searches = await self.db_client.query_items(
                self.table_name,
                IndexName="created_at-index",
                KeyConditionExpression="created_at > :cutoff",
                ExpressionAttributeValues={":cutoff": cutoff_time.isoformat()}
            )
            
            stats = {
                "total_searches": len(recent_searches),
                "total_results_found": sum(search.get("total_results", 0) for search in recent_searches),
                "average_results_per_search": 0.0,
                "successful_searches": len([s for s in recent_searches if s.get("successful_results", 0) > 0]),
                "failed_searches": len([s for s in recent_searches if s.get("successful_results", 0) == 0])
            }
            
            if stats["total_searches"] > 0:
                stats["average_results_per_search"] = stats["total_results_found"] / stats["total_searches"]
                stats["success_rate"] = (stats["successful_searches"] / stats["total_searches"]) * 100
            else:
                stats["success_rate"] = 0.0
            
            return stats
            
        except Exception as e:
            logger.error(f"Search statistics error: {str(e)}")
            return {}
    
    async def update_search_status(self, request_id: str, status: str) -> bool:
        """Update search status"""
        try:
            update_data = {
                "request_id": request_id,
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            success = await self.db_client.save_item(self.table_name, update_data)
            
            if success:
                logger.info(f"Updated search status: {request_id} -> {status}")
            
            return success
            
        except Exception as e:
            logger.error(f"Status update error: {str(e)}")
            return False
