from typing import List, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from .models import SerpRequest, SerpResponse
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SerpService:
    """Main SERP service for search operations"""
    
    def __init__(self):
        self.serp_client = ServiceFactory.get_serp_client()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def search(self, query: str, num_results: int = 10) -> SerpResponse:
        """Execute search query"""
        try:
            logger.info(f"Starting SERP search: {query}")
            
            request = SerpRequest(
                query=query,
                num_results=num_results
            )
            
            # Execute search
            response = await self.serp_client.search(request)
            
            # Store results
            await self._store_search_results(response)
            
            logger.info(f"SERP search completed: {len(response.results)} results found")
            return response
            
        except Exception as e:
            logger.error(f"SERP search error: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
    
    async def search_batch(self, queries: List[str], num_results: int = 10) -> List[SerpResponse]:
        """Execute multiple search queries"""
        try:
            responses = []
            
            for query in queries:
                try:
                    response = await self.search(query, num_results)
                    responses.append(response)
                except Exception as e:
                    logger.error(f"Batch search failed for query '{query}': {str(e)}")
                    continue
            
            logger.info(f"Batch search completed: {len(responses)}/{len(queries)} successful")
            return responses
            
        except Exception as e:
            logger.error(f"Batch search error: {str(e)}")
            raise
    
    async def _store_search_results(self, response: SerpResponse):
        """Store search results"""
        try:
            # Store in object storage
            storage_key = f"serp_results/{response.request_id}.json"
            await self.storage_client.save_json(storage_key, response.dict())
            
            # Store metadata in database
            await self.database_client.save_item("serp_requests", {
                "request_id": response.request_id,
                "query": response.query,
                "total_results": response.total_results,
                "successful_results": len(response.results),
                "storage_key": storage_key,
                "created_at": response.created_at.isoformat()
            })
            
            logger.info(f"Stored search results: {storage_key}")
            
        except Exception as e:
            logger.error(f"Failed to store search results: {str(e)}")
