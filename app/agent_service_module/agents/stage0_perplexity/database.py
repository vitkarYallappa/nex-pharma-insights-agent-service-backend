from typing import Dict, Any, List, Optional
from datetime import datetime
from ...shared.database.base_repository import BaseRepository
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityDatabase:
    """Handle Perplexity database operations"""
    
    def __init__(self):
        self.db_client = ServiceFactory.get_database_client()
        self.table_name = "perplexity_extractions"
    
    async def save_extraction_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save extraction metadata"""
        try:
            if 'created_at' not in metadata:
                metadata['created_at'] = datetime.utcnow().isoformat()
            
            success = await self.db_client.save_item(self.table_name, metadata)
            
            if success:
                logger.info(f"Saved extraction metadata: {metadata.get('request_id')}")
            else:
                logger.error(f"Failed to save metadata: {metadata.get('request_id')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Extraction metadata save error: {str(e)}")
            return False
    
    async def get_extraction_metadata(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get extraction metadata by request ID"""
        try:
            key = {"request_id": request_id}
            metadata = await self.db_client.get_item(self.table_name, key)
            
            if metadata:
                logger.info(f"Retrieved extraction metadata: {request_id}")
            else:
                logger.warning(f"No metadata found: {request_id}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Extraction metadata get error: {str(e)}")
            return None
    
    async def save_content_metadata(self, content_items: List[Dict[str, Any]]) -> bool:
        """Save individual content metadata"""
        try:
            table_name = "perplexity_content"
            success_count = 0
            
            for content in content_items:
                content_meta = {
                    "content_id": f"{content.get('request_id')}_{content.get('url_hash', '')}",
                    "request_id": content.get("request_id"),
                    "url": content.get("url"),
                    "title": content.get("title"),
                    "word_count": content.get("word_count", 0),
                    "extraction_confidence": content.get("extraction_confidence", 0.0),
                    "content_type": content.get("content_type", "article"),
                    "language": content.get("language", "en"),
                    "created_at": datetime.utcnow().isoformat()
                }
                
                if await self.db_client.save_item(table_name, content_meta):
                    success_count += 1
            
            logger.info(f"Saved {success_count}/{len(content_items)} content metadata items")
            return success_count == len(content_items)
            
        except Exception as e:
            logger.error(f"Content metadata save error: {str(e)}")
            return False
    
    async def get_extraction_stats(self, request_id: str) -> Dict[str, Any]:
        """Get extraction statistics"""
        try:
            # Get main extraction record
            metadata = await self.get_extraction_metadata(request_id)
            
            if not metadata:
                return {}
            
            # Get content items count
            content_table = "perplexity_content"
            content_items = await self.db_client.query_items(
                content_table,
                KeyConditionExpression="request_id = :request_id",
                ExpressionAttributeValues={":request_id": request_id}
            )
            
            stats = {
                "request_id": request_id,
                "total_urls": metadata.get("total_urls", 0),
                "successful_extractions": metadata.get("successful_extractions", 0),
                "failed_extractions": metadata.get("failed_extractions", 0),
                "content_items_stored": len(content_items),
                "created_at": metadata.get("created_at"),
                "average_confidence": 0.0
            }
            
            # Calculate average confidence
            if content_items:
                confidences = [item.get("extraction_confidence", 0.0) for item in content_items]
                stats["average_confidence"] = sum(confidences) / len(confidences)
            
            return stats
            
        except Exception as e:
            logger.error(f"Extraction stats error: {str(e)}")
            return {}
    
    async def update_extraction_status(self, request_id: str, status: str) -> bool:
        """Update extraction status"""
        try:
            update_data = {
                "request_id": request_id,
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            success = await self.db_client.save_item(self.table_name, update_data)
            
            if success:
                logger.info(f"Updated extraction status: {request_id} -> {status}")
            
            return success
            
        except Exception as e:
            logger.error(f"Status update error: {str(e)}")
            return False


class Stage0PerplexityRepository(BaseRepository):
    """Legacy database operations for stage0_perplexity - maintained for backward compatibility"""
    
    def __init__(self):
        super().__init__(table_name="stage0_perplexity_data")
    
    def get_table_name(self) -> str:
        return "stage0_perplexity_data"
    
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
