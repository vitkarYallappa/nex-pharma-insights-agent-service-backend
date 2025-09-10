# Stage 0 SERP Agent Implementation

## 10-Line Prompt:
Create SERP search agent that handles web search operations through multiple search engines (Google, Bing, SerpAPI) with query optimization and result ranking, includes real API integration with rate limiting and error handling, response processing that validates URLs and extracts metadata like domain and position, service orchestration that coordinates API calls and result aggregation, storage operations to save search results in S3/Minio for downstream processing, database operations to track search metadata and request status in DynamoDB, comprehensive error handling for API failures and invalid responses, support for multi-engine search with deduplication, and environment-based configuration for production deployment.

## What it covers: 
Web search operations, result extraction, multi-engine support, URL validation
## Methods: 
SERP API integration, response parsing, result aggregation, storage coordination
## Why: 
Foundation for content pipeline, search result quality, scalable search operations

---

## models.py
```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class SerpRequest(BaseModel):
    """Request model for SERP API calls"""
    query: str = Field(..., description="Search query")
    num_results: int = Field(default=10, ge=1, le=100)
    language: str = Field(default="en")
    country: str = Field(default="us")
    engine: str = Field(default="google")

class SerpResult(BaseModel):
    """Individual search result"""
    title: str = Field(..., description="Page title")
    url: HttpUrl = Field(..., description="Page URL")
    snippet: str = Field(..., description="Search snippet")
    position: int = Field(..., description="Result position")
    domain: str = Field(..., description="Website domain")
    published_date: Optional[datetime] = Field(default=None)

class SerpResponse(BaseModel):
    """Complete SERP API response"""
    request_id: str = Field(..., description="Request identifier")
    query: str = Field(..., description="Original query")
    total_results: int = Field(..., description="Total results")
    results: List[SerpResult] = Field(..., description="Search results")
    search_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_urls(self) -> List[str]:
        """Extract URLs from results"""
        return [str(result.url) for result in self.results]
```

## serp_api.py
```python
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
```

## Production Implementation

The SERP service uses real API implementations for production deployment. All mock implementations have been removed to ensure production readiness.

## serp_response.py
```python
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from urllib.parse import urlparse
from .models import SerpResponse, SerpResult
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SerpResponseHandler:
    """Process and validate SERP API responses"""
    
    @staticmethod
    def process_response(data: Dict[str, Any], query: str, engine: str = "google") -> SerpResponse:
        """Process SERP response based on engine type"""
        if engine == "google":
            return SerpResponseHandler._process_google(data, query)
        elif engine == "bing":
            return SerpResponseHandler._process_bing(data, query)
        else:
            return SerpResponseHandler._process_generic(data, query)
    
    @staticmethod
    def _process_google(data: Dict[str, Any], query: str) -> SerpResponse:
        """Process Google SERP response"""
        try:
            organic_results = data.get("organic_results", [])
            results = []
            
            for i, result in enumerate(organic_results):
                processed = SerpResponseHandler._process_single_result(result, i + 1)
                if processed:
                    results.append(processed)
            
            return SerpResponse(
                request_id=SerpResponseHandler._generate_request_id("google"),
                query=query,
                total_results=data.get("search_information", {}).get("total_results", 0),
                results=results,
                search_metadata=SerpResponseHandler._extract_metadata(data)
            )
            
        except Exception as e:
            logger.error(f"Error processing Google response: {str(e)}")
            raise ValueError(f"Invalid Google response: {str(e)}")
    
    @staticmethod
    def _process_single_result(result: Dict[str, Any], position: int) -> Optional[SerpResult]:
        """Process individual search result"""
        try:
            url = result.get("link", "")
            if not SerpResponseHandler._is_valid_url(url):
                return None
            
            return SerpResult(
                title=SerpResponseHandler._clean_text(result.get("title", "")),
                url=url,
                snippet=SerpResponseHandler._clean_text(result.get("snippet", "")),
                position=position,
                domain=SerpResponseHandler._extract_domain(url)
            )
            
        except Exception as e:
            logger.warning(f"Error processing result {position}: {str(e)}")
            return None
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        cleaned = re.sub(r'<[^>]+>', '', text)  # Remove HTML
        return re.sub(r'\s+', ' ', cleaned).strip()  # Normalize whitespace
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc.lower()
        except:
            return ""
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    @staticmethod
    def _generate_request_id(source: str) -> str:
        """Generate unique request ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        return f"{source}_serp_{timestamp}"
    
    @staticmethod
    def _extract_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract search metadata"""
        return {
            "search_time": data.get("search_metadata", {}).get("total_time_taken"),
            "processed_at": datetime.utcnow().isoformat()
        }
```

## service.py
```python
from typing import List, Optional
from ...config.service_factory import ServiceFactory
from .models import SerpRequest, SerpResponse
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
```

## storage.py
```python
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
```

## database.py
```python
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
```