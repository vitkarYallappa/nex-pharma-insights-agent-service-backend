import asyncio
import aiohttp
from typing import Dict, Any
from .models import SerpRequest, SerpResponse, SerpResult
from ...config.settings import settings
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SerpAPI:
    """Real SERP API client for web search"""
    
    def __init__(self):
        self.api_key = settings.SERP_API_KEY
        self.base_url = "https://serpapi.com/search"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search(self, request: SerpRequest) -> SerpResponse:
        """Execute search query using SERP API"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            params = self._build_params(request)
            
            async with self.session.get(self.base_url, params=params) as response:
                response.raise_for_status()
                data = await response.json()
                return self._parse_response(data, request)
                
        except Exception as e:
            logger.error(f"SERP API error: {str(e)}")
            raise Exception(f"Search failed: {str(e)}")
    
    def _build_params(self, request: SerpRequest) -> Dict[str, Any]:
        """Build search parameters"""
        return {
            "q": request.query,
            "api_key": self.api_key,
            "engine": request.engine,
            "num": request.num_results,
            "hl": request.language,
            "gl": request.country,
            "format": "json"
        }
    
    def _parse_response(self, data: Dict[str, Any], request: SerpRequest) -> SerpResponse:
        """Parse SERP API response"""
        organic_results = data.get("organic_results", [])
        results = []
        
        for i, result in enumerate(organic_results):
            serp_result = SerpResult(
                title=result.get("title", ""),
                url=result.get("link", ""),
                snippet=result.get("snippet", ""),
                position=i + 1,
                domain=self._extract_domain(result.get("link", ""))
            )
            results.append(serp_result)
        
        return SerpResponse(
            request_id=f"serp_{int(asyncio.get_event_loop().time())}",
            query=request.query,
            total_results=data.get("search_information", {}).get("total_results", 0),
            results=results,
            search_metadata=data.get("search_metadata", {})
        )
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ""

    # Legacy method for backward compatibility
    async def call_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy API call method"""
        try:
            # Convert legacy format to new format
            request = SerpRequest(
                query=data.get("query", ""),
                num_results=data.get("num_results", 10)
            )
            response = await self.search(request)
            return {
                "status": "success", 
                "data": response.dict()
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
