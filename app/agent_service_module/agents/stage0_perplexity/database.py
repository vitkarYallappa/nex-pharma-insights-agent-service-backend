from typing import Dict, Any, List, Optional
from datetime import datetime
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
    
    async def save_summary(self, summary_data: Dict[str, Any]) -> bool:
        """Save Perplexity extraction summary to summary table"""
        try:
            from ....config.table_configs.perplexity_summary_table import PerplexitySummaryTableConfig
            from ....config.unified_settings import settings
            
            # Get table name with environment suffix
            table_name = PerplexitySummaryTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            success = await self.db_client.save_item(table_name, summary_data)
            
            if success:
                logger.info(f"Saved Perplexity summary: {summary_data.get('request_id')}")
            else:
                logger.error(f"Failed to save summary: {summary_data.get('request_id')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Summary save error: {str(e)}")
            return False
    
    async def get_summary(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get Perplexity extraction summary by request ID"""
        try:
            from ....config.table_configs.perplexity_summary_table import PerplexitySummaryTableConfig
            from ....config.unified_settings import settings
            
            # Get table name with environment suffix
            table_name = PerplexitySummaryTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            key = {"request_id": request_id}
            summary = await self.db_client.get_item(table_name, key)
            
            if summary:
                logger.info(f"Retrieved Perplexity summary: {request_id}")
            else:
                logger.warning(f"No summary found: {request_id}")
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary get error: {str(e)}")
            return None
    
    async def list_summaries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent Perplexity summaries"""
        try:
            from ....config.table_configs.perplexity_summary_table import PerplexitySummaryTableConfig
            from ....config.unified_settings import settings
            
            # Get table name with environment suffix
            table_name = PerplexitySummaryTableConfig.get_table_name(settings.TABLE_ENVIRONMENT)
            
            # Query using GSI to get recent summaries
            summaries = await self.db_client.query_items(
                table_name,
                index_name="created_at-index",
                limit=limit
            )
            
            logger.info(f"Retrieved {len(summaries)} Perplexity summaries")
            return summaries
            
        except Exception as e:
            logger.error(f"Summary list error: {str(e)}")
            return []
