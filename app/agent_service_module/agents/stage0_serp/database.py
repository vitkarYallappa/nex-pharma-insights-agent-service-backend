from typing import Dict, Any, List, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from ...shared.database.base_repository import BaseRepository
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SerpDatabase:
    """Handle SERP database operations"""
    
    def __init__(self):
        self.db_client = ServiceFactory.get_database_client()
        self.table_name = "serp_requests"
    
    async def save_search_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save search request metadata"""
        try:
            # Add timestamp if not present
            if 'created_at' not in metadata:
                metadata['created_at'] = datetime.utcnow().isoformat()
            
            success = await self.db_client.save_item(self.table_name, metadata)
            
            if success:
                logger.info(f"Saved SERP metadata: {metadata.get('request_id')}")
            else:
                logger.error(f"Failed to save SERP metadata: {metadata.get('request_id')}")
            
            return success
            
        except Exception as e:
            logger.error(f"SERP database save error: {str(e)}")
            return False
    
    async def get_search_metadata(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get search metadata by request ID"""
        try:
            key = {"request_id": request_id}
            metadata = await self.db_client.get_item(self.table_name, key)
            
            if metadata:
                logger.info(f"Retrieved SERP metadata: {request_id}")
            else:
                logger.warning(f"No SERP metadata found: {request_id}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"SERP database get error: {str(e)}")
            return None
    
    async def get_recent_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search requests"""
        try:
            # Query recent searches (implementation depends on table structure)
            searches = await self.db_client.query_items(
                self.table_name,
                IndexName="created_at-index",  # Assuming GSI exists
                ScanIndexForward=False,
                Limit=limit
            )
            
            logger.info(f"Retrieved {len(searches)} recent searches")
            return searches
            
        except Exception as e:
            logger.error(f"Recent searches query error: {str(e)}")
            return []
    
    async def update_search_status(self, request_id: str, status: str) -> bool:
        """Update search request status"""
        try:
            update_data = {
                "request_id": request_id,
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            success = await self.db_client.save_item(self.table_name, update_data)
            
            if success:
                logger.info(f"Updated SERP status: {request_id} -> {status}")
            
            return success
            
        except Exception as e:
            logger.error(f"SERP status update error: {str(e)}")
            return False
    
    async def get_search_history(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get search history for a specific query"""
        try:
            # Query searches by query (implementation depends on table structure)
            searches = await self.db_client.query_items(
                self.table_name,
                KeyConditionExpression="query = :query",
                ExpressionAttributeValues={":query": query},
                ScanIndexForward=False,
                Limit=limit
            )
            
            logger.info(f"Retrieved {len(searches)} searches for query: {query}")
            return searches
            
        except Exception as e:
            logger.error(f"Search history query error: {str(e)}")
            return []

class Stage0SerpRepository(BaseRepository):
    """Database operations for stage0_serp with enhanced functionality"""
    
    def __init__(self):
        super().__init__(table_name="stage0_serp_data")
        self.serp_database = SerpDatabase()
    
    def get_table_name(self) -> str:
        return "stage0_serp_data"
    
    async def save_request(self, request_data: dict) -> bool:
        """Save request data with enhanced metadata tracking"""
        try:
            # Save to legacy table for backward compatibility
            legacy_success = await self.create(request_data)
            
            # Also save to SERP metadata table if it contains search info
            if 'query' in request_data or 'search_results' in request_data:
                serp_metadata = {
                    "request_id": request_data.get("request_id"),
                    "query": request_data.get("query", request_data.get("content", "")),
                    "status": request_data.get("status", "pending"),
                    "total_results": request_data.get("total_results", 0),
                    "created_at": datetime.utcnow().isoformat()
                }
                
                serp_success = await self.serp_database.save_search_metadata(serp_metadata)
                return legacy_success and serp_success
            
            return legacy_success
            
        except Exception as e:
            logger.error(f"Stage0 SERP save request error: {str(e)}")
            return False
    
    async def get_request(self, request_id: str) -> dict:
        """Get request data with fallback to enhanced metadata"""
        try:
            # Try legacy table first
            legacy_data = await self.get_by_id(request_id)
            if legacy_data:
                return legacy_data
            
            # Fallback to SERP metadata
            serp_metadata = await self.serp_database.get_search_metadata(request_id)
            if serp_metadata:
                return {
                    "request_id": request_id,
                    "content": serp_metadata.get("query", ""),
                    "status": serp_metadata.get("status", "unknown"),
                    "metadata": serp_metadata,
                    "timestamp": serp_metadata.get("created_at")
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Stage0 SERP get request error: {str(e)}")
            return {}
    
    async def update_status(self, request_id: str, status: str) -> bool:
        """Update request status in both legacy and enhanced tables"""
        try:
            # Update legacy table
            request_data = await self.get_by_id(request_id)
            legacy_success = True
            
            if request_data:
                request_data['status'] = status
                request_data['updated_at'] = datetime.utcnow().isoformat()
                legacy_success = await self.update(request_data)
            
            # Update SERP metadata table
            serp_success = await self.serp_database.update_search_status(request_id, status)
            
            return legacy_success and serp_success
            
        except Exception as e:
            logger.error(f"Stage0 SERP update status error: {str(e)}")
            return False
    
    async def get_recent_requests(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent requests from both legacy and enhanced tables"""
        try:
            # Get from both sources and merge
            legacy_requests = await self.get_all()  # Implement pagination if needed
            serp_requests = await self.serp_database.get_recent_searches(limit)
            
            # Merge and deduplicate by request_id
            all_requests = {}
            
            for req in legacy_requests:
                if 'request_id' in req:
                    all_requests[req['request_id']] = req
            
            for req in serp_requests:
                if 'request_id' in req:
                    if req['request_id'] not in all_requests:
                        all_requests[req['request_id']] = req
                    else:
                        # Merge metadata
                        all_requests[req['request_id']].update(req)
            
            # Sort by timestamp and limit
            sorted_requests = sorted(
                all_requests.values(),
                key=lambda x: x.get('created_at', x.get('timestamp', '')),
                reverse=True
            )
            
            return sorted_requests[:limit]
            
        except Exception as e:
            logger.error(f"Stage0 SERP get recent requests error: {str(e)}")
            return []
