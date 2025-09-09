from typing import List, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from .models import SerpRequest, SerpResponse, Stage0SerpRequest, Stage0SerpResponse
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SerpService:
    """Main SERP service orchestrating search operations"""
    
    def __init__(self):
        self.serp_client = ServiceFactory.get_serp_client()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def search(self, query: str, num_results: int = 10) -> SerpResponse:
        """Execute search and store results"""
        try:
            logger.info(f"Starting SERP search for: {query}")
            
            request = SerpRequest(
                query=query,
                num_results=num_results
            )
            
            # Execute search
            response = await self.serp_client.search(request)
            
            # Validate response
            validated_response = self._validate_response(response)
            
            # Store results
            await self._store_results(validated_response)
            
            logger.info(f"SERP search completed. Found {len(validated_response.results)} results")
            return validated_response
            
        except Exception as e:
            logger.error(f"SERP search error: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
    
    async def multi_engine_search(self, query: str, engines: List[str], num_results: int = 10) -> SerpResponse:
        """Search across multiple engines"""
        try:
            all_results = []
            
            for engine in engines:
                try:
                    request = SerpRequest(
                        query=query,
                        num_results=num_results,
                        engine=engine
                    )
                    
                    response = await self.serp_client.search(request)
                    all_results.extend(response.results)
                    
                except Exception as e:
                    logger.warning(f"Engine {engine} failed: {str(e)}")
                    continue
            
            # Aggregate and deduplicate
            aggregated = self._aggregate_results(query, all_results)
            await self._store_results(aggregated)
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Multi-engine search failed: {str(e)}")
            raise
    
    def _validate_response(self, response: SerpResponse) -> SerpResponse:
        """Validate and clean response"""
        if not response.results:
            logger.warning(f"No results for query: {response.query}")
        
        # Filter valid URLs
        valid_results = [r for r in response.results if r.url and r.title]
        response.results = valid_results
        
        return response
    
    def _aggregate_results(self, query: str, all_results: List) -> SerpResponse:
        """Aggregate and deduplicate results"""
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            url_str = str(result.url)
            if url_str not in seen_urls:
                seen_urls.add(url_str)
                unique_results.append(result)
        
        # Re-rank by position
        sorted_results = sorted(unique_results, key=lambda x: x.position)
        
        return SerpResponse(
            request_id=f"multi_{int(datetime.utcnow().timestamp())}",
            query=query,
            total_results=len(sorted_results),
            results=sorted_results[:50],
            search_metadata={"source": "multi_engine"}
        )
    
    async def _store_results(self, response: SerpResponse):
        """Store search results"""
        try:
            # Store in object storage
            storage_key = f"serp_results/{response.request_id}.json"
            await self.storage_client.save_json(storage_key, response.dict())
            
            # Store metadata in database
            await self.database_client.save_item("serp_metadata", {
                "request_id": response.request_id,
                "query": response.query,
                "total_results": response.total_results,
                "storage_key": storage_key,
                "created_at": response.created_at.isoformat()
            })
            
            logger.info(f"Stored SERP results: {storage_key}")
            
        except Exception as e:
            logger.error(f"Failed to store results: {str(e)}")

class Stage0SerpService:
    """Main service for stage0_serp with legacy compatibility"""
    
    def __init__(self):
        # Factory automatically provides correct implementation based on environment
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
        self.serp_service = SerpService()
    
    async def process(self, request: Stage0SerpRequest) -> Stage0SerpResponse:
        """Process the stage0_serp request with enhanced functionality"""
        try:
            logger.info(f"Processing stage0_serp request: {request.request_id}")
            
            # Extract query from content or use content as query
            query = request.content
            
            # Perform SERP search
            serp_response = await self.serp_service.search(query, num_results=10)
            
            # Convert to legacy format
            result = {
                "message": "Processing stage0_serp request completed",
                "request_id": request.request_id,
                "search_results": {
                    "query": serp_response.query,
                    "total_results": serp_response.total_results,
                    "results": [
                        {
                            "title": result.title,
                            "url": str(result.url),
                            "snippet": result.snippet,
                            "domain": result.domain,
                            "position": result.position
                        }
                        for result in serp_response.results
                    ]
                }
            }
            
            return Stage0SerpResponse(
                request_id=request.request_id,
                result=result,
                status="completed"
            )
            
        except Exception as e:
            logger.error(f"Stage0 SERP processing error: {str(e)}")
            return Stage0SerpResponse(
                request_id=request.request_id,
                result={"error": str(e), "message": "Processing failed"},
                status="failed"
            )
