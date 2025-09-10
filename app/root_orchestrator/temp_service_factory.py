"""
Temporary Service Factory for Root Orchestrator

This is a minimal service factory that provides the basic services needed
by the Root Orchestrator without depending on the existing configuration
system that has Pydantic compatibility issues.
"""

from typing import Any, Dict, Optional, List
import os
import asyncio
import json
import random
from datetime import datetime

# Conditional import for aiohttp (only needed for real API clients)
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None

# Simple PerplexityClient implementation based on your reference
import requests

class SimplePerplexityClient:
    """Simple Perplexity client based on your reference implementation"""
    
    def __init__(self, api_key: str, use_mock_data: bool = False):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai"
        self.use_mock_data = use_mock_data
    
    def search(self, query: str) -> str:
        """Perform a search and return results as text"""
        if self.use_mock_data:
            return "Mock response for testing purposes."
        
        data = {
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": query}],
            "max_tokens": 1024
        }
        
        try:
            response = self._make_request("POST", "/chat/completions", json=data)
            choices = response.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""
        except Exception as e:
            print(f"Perplexity API error: {e}")
            return f"Error: {e}"
    
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request to Perplexity API"""
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()


class MockDatabaseClient:
    """Mock database client for development/testing"""
    
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
    
    async def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get an item from the mock database"""
        table = self._data.get(table_name, {})
        item_key = str(key.get("request_id", ""))
        return table.get(item_key)
    
    async def save_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """Save an item to the mock database"""
        try:
            if table_name not in self._data:
                self._data[table_name] = {}
            
            item_key = str(item.get("request_id", ""))
            self._data[table_name][item_key] = item.copy()
            return True
        except Exception:
            return False
    
    async def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        """Delete an item from the mock database"""
        try:
            table = self._data.get(table_name, {})
            item_key = str(key.get("request_id", ""))
            if item_key in table:
                del table[item_key]
                return True
            return False
        except Exception:
            return False
    
    async def query_items(self, table_name: str, query_params: Dict[str, Any], 
                         limit: Optional[int] = None, offset: Optional[int] = None) -> list:
        """Query items from the mock database"""
        try:
            table = self._data.get(table_name, {})
            items = list(table.values())
            
            # Apply basic filtering
            if query_params:
                filtered_items = []
                for item in items:
                    match = True
                    for key, value in query_params.items():
                        if key in item and item[key] != value:
                            match = False
                            break
                    if match:
                        filtered_items.append(item)
                items = filtered_items
            
            # Apply pagination
            if offset:
                items = items[offset:]
            if limit:
                items = items[:limit]
            
            return items
        except Exception:
            return []
    
    async def scan(self, table_name: str, **kwargs) -> list:
        """Scan items from the mock database (similar to DynamoDB scan)"""
        try:
            table = self._data.get(table_name, {})
            items = list(table.values())
            
            # Handle FilterExpression (simplified for mock)
            if 'FilterExpression' in kwargs and 'ExpressionAttributeValues' in kwargs:
                filter_expr = kwargs['FilterExpression']
                attr_values = kwargs['ExpressionAttributeValues']
                attr_names = kwargs.get('ExpressionAttributeNames', {})
                
                filtered_items = []
                for item in items:
                    # Simple mock filtering - check if item matches filter conditions
                    if self._matches_filter_expression(item, filter_expr, attr_values, attr_names):
                        filtered_items.append(item)
                items = filtered_items
            
            # Apply limit
            if 'Limit' in kwargs:
                items = items[:kwargs['Limit']]
            
            return items
        except Exception as e:
            print(f"Mock scan error: {e}")
            return []
    
    def _matches_filter_expression(self, item: Dict[str, Any], filter_expr: str, 
                                 attr_values: Dict[str, Any], attr_names: Dict[str, str]) -> bool:
        """Simple mock filter expression matching"""
        try:
            # This is a very simplified implementation for testing
            # In reality, you'd parse the filter expression properly
            
            # Handle simple equality checks
            for placeholder, value in attr_values.items():
                placeholder_clean = placeholder.replace(':', '')
                
                # Check if this attribute exists in the item and matches
                attr_name = placeholder_clean
                
                # Handle attribute name mapping
                for name_placeholder, actual_name in attr_names.items():
                    if name_placeholder.replace('#', '') == placeholder_clean:
                        attr_name = actual_name
                        break
                
                if attr_name in item and item[attr_name] == value:
                    continue
                elif f"#{placeholder_clean}" in filter_expr or f":{placeholder_clean}" in filter_expr:
                    # If this attribute is in the filter but doesn't match, item doesn't match
                    return False
            
            return True
        except Exception:
            # If we can't parse the filter, include the item (safer for testing)
            return True


class MockStorageClient:
    """Mock storage client for development/testing"""
    
    def __init__(self):
        self._storage: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
    
    # JSON convenience methods
    async def save_json(self, key: str, data: Any) -> bool:
        """Save JSON data to mock storage"""
        try:
            import json
            json_data = json.dumps(data, default=str).encode('utf-8')
            return await self.upload_content(json_data, key, 'application/json')
        except Exception as e:
            print(f"Mock Storage: Error saving JSON {key}: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON data from mock storage"""
        try:
            import json
            content = await self.get_content(key)
            if content:
                return json.loads(content.decode('utf-8'))
            return None
        except Exception as e:
            print(f"Mock Storage: Error getting JSON {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete data from mock storage"""
        return await self.delete_object(key)
    
    # Full S3/MinIO-compatible interface
    async def upload_file(self, file_path: str, object_key: str, 
                         metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload a file to mock storage"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return await self.upload_content(content, object_key, metadata=metadata)
        except Exception as e:
            print(f"Mock Storage: Error uploading file {file_path}: {e}")
            return False
    
    async def upload_content(self, content: bytes, object_key: str,
                           content_type: str = 'application/octet-stream',
                           metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload content directly to mock storage"""
        try:
            self._storage[object_key] = content
            if metadata:
                self._metadata[object_key] = metadata
            print(f"Mock Storage: Content uploaded: {object_key} ({len(content)} bytes)")
            return True
        except Exception as e:
            print(f"Mock Storage: Error uploading content {object_key}: {e}")
            return False
    
    async def download_file(self, object_key: str, file_path: str) -> bool:
        """Download a file from mock storage"""
        try:
            content = await self.get_content(object_key)
            if content is None:
                return False
            
            with open(file_path, 'wb') as f:
                f.write(content)
            print(f"Mock Storage: File downloaded: {object_key}")
            return True
        except Exception as e:
            print(f"Mock Storage: Error downloading file {object_key}: {e}")
            return False
    
    async def get_content(self, object_key: str) -> Optional[bytes]:
        """Get content from mock storage"""
        content = self._storage.get(object_key)
        if content:
            print(f"Mock Storage: Content retrieved: {object_key}")
        return content
    
    async def delete_object(self, object_key: str) -> bool:
        """Delete an object from mock storage"""
        try:
            if object_key in self._storage:
                del self._storage[object_key]
                if object_key in self._metadata:
                    del self._metadata[object_key]
                print(f"Mock Storage: Object deleted: {object_key}")
                return True
            return False
        except Exception as e:
            print(f"Mock Storage: Error deleting object {object_key}: {e}")
            return False
    
    async def list_objects(self, prefix: str = "") -> List[str]:
        """List objects in mock storage"""
        try:
            objects = [key for key in self._storage.keys() if key.startswith(prefix)]
            print(f"Mock Storage: Listed {len(objects)} objects with prefix '{prefix}'")
            return objects
        except Exception as e:
            print(f"Mock Storage: Error listing objects: {e}")
            return []
    
    async def object_exists(self, object_key: str) -> bool:
        """Check if an object exists in mock storage"""
        exists = object_key in self._storage
        print(f"Mock Storage: Object {object_key} exists: {exists}")
        return exists


class MockMinioClient:
    """
    Mock MinIO client that provides the same interface as the real MinIO client.
    
    This allows for development and testing without requiring a real MinIO server.
    """
    
    def __init__(self, endpoint: str = "localhost:9001", access_key: str = "minioadmin", 
                 secret_key: str = "minioadmin123", secure: bool = False):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "nex-pharma")
        
        # Mock storage
        self._storage: Dict[str, bytes] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        
        print(f"Mock MinIO: Initialized with endpoint {endpoint}, bucket '{self.bucket_name}'")
    
    async def upload_file(self, file_path: str, object_key: str, 
                         metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload a file to mock MinIO"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return await self.upload_content(content, object_key, metadata=metadata)
        except Exception as e:
            print(f"Mock MinIO: Error uploading file {file_path}: {e}")
            return False
    
    async def upload_content(self, content: bytes, object_key: str,
                           content_type: str = 'application/octet-stream',
                           metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload content directly to mock MinIO"""
        try:
            self._storage[object_key] = content
            if metadata:
                self._metadata[object_key] = metadata
            print(f"Mock MinIO: Content uploaded to bucket '{self.bucket_name}': {object_key} ({len(content)} bytes)")
            return True
        except Exception as e:
            print(f"Mock MinIO: Error uploading content {object_key}: {e}")
            return False
    
    async def download_file(self, object_key: str, file_path: str) -> bool:
        """Download a file from mock MinIO"""
        try:
            content = await self.get_content(object_key)
            if content is None:
                return False
            
            with open(file_path, 'wb') as f:
                f.write(content)
            print(f"Mock MinIO: File downloaded from bucket '{self.bucket_name}': {object_key}")
            return True
        except Exception as e:
            print(f"Mock MinIO: Error downloading file {object_key}: {e}")
            return False
    
    async def get_content(self, object_key: str) -> Optional[bytes]:
        """Get content from mock MinIO"""
        content = self._storage.get(object_key)
        if content:
            print(f"Mock MinIO: Content retrieved from bucket '{self.bucket_name}': {object_key}")
        else:
            print(f"Mock MinIO: Object not found in bucket '{self.bucket_name}': {object_key}")
        return content
    
    async def delete_object(self, object_key: str) -> bool:
        """Delete an object from mock MinIO"""
        try:
            if object_key in self._storage:
                del self._storage[object_key]
                if object_key in self._metadata:
                    del self._metadata[object_key]
                print(f"Mock MinIO: Object deleted from bucket '{self.bucket_name}': {object_key}")
                return True
            print(f"Mock MinIO: Object not found for deletion: {object_key}")
            return False
        except Exception as e:
            print(f"Mock MinIO: Error deleting object {object_key}: {e}")
            return False
    
    async def list_objects(self, prefix: str = "") -> List[str]:
        """List objects in mock MinIO"""
        try:
            objects = [key for key in self._storage.keys() if key.startswith(prefix)]
            print(f"Mock MinIO: Listed {len(objects)} objects from bucket '{self.bucket_name}' with prefix '{prefix}'")
            return objects
        except Exception as e:
            print(f"Mock MinIO: Error listing objects: {e}")
            return []
    
    async def object_exists(self, object_key: str) -> bool:
        """Check if an object exists in mock MinIO"""
        exists = object_key in self._storage
        print(f"Mock MinIO: Object {object_key} exists in bucket '{self.bucket_name}': {exists}")
        return exists
    
    async def create_bucket_if_not_exists(self) -> bool:
        """Mock bucket creation (always succeeds)"""
        print(f"Mock MinIO: Bucket '{self.bucket_name}' ready (mock)")
        return True
    
    # JSON convenience methods
    async def save_json(self, key: str, data: Any) -> bool:
        """Save JSON data to mock MinIO"""
        try:
            import json
            json_data = json.dumps(data, default=str).encode('utf-8')
            return await self.upload_content(json_data, key, 'application/json')
        except Exception as e:
            print(f"Mock MinIO: Error saving JSON {key}: {e}")
            return False
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON data from mock MinIO"""
        try:
            import json
            content = await self.get_content(key)
            if content:
                return json.loads(content.decode('utf-8'))
            return None
        except Exception as e:
            print(f"Mock MinIO: Error getting JSON {key}: {e}")
            return None


class PerplexityClientWrapper:
    """
    Wrapper for the existing PerplexityClient that provides async interface.
    
    This provides both the original URL-based content extraction interface
    and the new simple search interface for market intelligence queries.
    """
    
    def __init__(self, api_key: Optional[str] = None, use_mock_data: bool = True):
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY", "mock_key")
        self.use_mock_data = use_mock_data
        self.base_url = "https://api.perplexity.ai"
        self.session = None
        self.rate_limit_delay = 1.0
        
        # Initialize the simple PerplexityClient
        if not use_mock_data:
            self.perplexity_client = SimplePerplexityClient(
                api_key=self.api_key,
                use_mock_data=use_mock_data
            )
        else:
            self.perplexity_client = None
        
        # Mock responses for different query types (for search interface)
        self.search_mock_responses = {
            "summary": {
                "id": "mock-summary-response",
                "model": "llama-3.1-sonar-small-128k-online",
                "created": 1756392439,
                "usage": {"prompt_tokens": 125, "completion_tokens": 531, "total_tokens": 656, "cost": {"total_cost": 0.014}},
                "citations": [
                    "https://pharmaphorum.com/news/lilly-pauses-mounjaro-shipments-uk-ahead-price-hike",
                    "https://news.sky.com/story/mounjaro-manufacturer-pauses-uk-shipments"
                ],
                "search_results": [
                    {"title": "Lilly pauses Mounjaro shipments to UK ahead of price hike", "url": "https://pharmaphorum.com/news/lilly-pauses-mounjaro-shipments-uk-ahead-price-hike", "date": "2025-08-28"}
                ],
                "choices": [{
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": "Based on recent developments, Eli Lilly has temporarily halted UK shipments of Mounjaro (tirzepatide), a popular weight-loss drug, ahead of a significant price increase. This strategic move reflects the growing demand and market dynamics in the obesity treatment sector..."
                    }
                }]
            },
            "insights": {
                "id": "mock-insights-response",
                "model": "llama-3.1-sonar-small-128k-online",
                "created": 1756392440,
                "usage": {"prompt_tokens": 200, "completion_tokens": 750, "total_tokens": 950, "cost": {"total_cost": 0.021}},
                "citations": [
                    "https://reuters.com/business/healthcare-pharmaceuticals/obesity-drug-market-analysis",
                    "https://bloomberg.com/news/articles/pharmaceutical-market-trends"
                ],
                "search_results": [
                    {"title": "Obesity Drug Market Analysis", "url": "https://reuters.com/business/healthcare-pharmaceuticals/obesity-drug-market-analysis", "date": "2025-08-29"}
                ],
                "choices": [{
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": "The obesity drug market is experiencing unprecedented growth, driven by increasing prevalence of obesity and breakthrough medications like semaglutide and tirzepatide. Key insights include market expansion, regulatory approvals, and competitive landscape shifts..."
                    }
                }]
            },
            "implications": {
                "id": "mock-implications-response",
                "model": "llama-3.1-sonar-small-128k-online",
                "created": 1756392441,
                "usage": {"prompt_tokens": 180, "completion_tokens": 620, "total_tokens": 800, "cost": {"total_cost": 0.018}},
                "citations": [
                    "https://nejm.org/doi/full/clinical-implications-obesity-drugs",
                    "https://fda.gov/news-events/press-announcements/obesity-treatment-guidelines"
                ],
                "search_results": [
                    {"title": "Clinical Implications of Obesity Drugs", "url": "https://nejm.org/doi/full/clinical-implications-obesity-drugs", "date": "2025-08-30"}
                ],
                "choices": [{
                    "index": 0,
                    "finish_reason": "stop",
                    "message": {
                        "role": "assistant",
                        "content": "The strategic implications of obesity drug developments include healthcare cost reduction, improved patient outcomes, and significant market opportunities. Stakeholders should consider regulatory changes, access barriers, and long-term sustainability..."
                    }
                }]
                         }
         }
        
        # Mock content templates for URL extraction (matching original pattern)
        self.url_mock_content = {
            "pharmaceutical": "This article discusses the latest developments in pharmaceutical AI regulation. The FDA has announced new guidelines for AI-powered drug discovery tools, emphasizing the need for transparency and validation in machine learning models used for therapeutic development.",
            "regulation": "New regulatory frameworks are being established to govern the use of artificial intelligence in healthcare and pharmaceutical industries. These regulations aim to ensure patient safety while promoting innovation in AI-driven medical technologies.",
            "ai_drug_discovery": "Artificial intelligence is revolutionizing drug discovery processes, enabling researchers to identify potential therapeutic compounds faster than traditional methods. Machine learning algorithms can predict molecular behavior and optimize drug candidates for clinical trials.",
            "compliance": "Pharmaceutical companies must now comply with updated AI governance requirements that mandate documentation of algorithmic decision-making processes, data validation procedures, and bias mitigation strategies in AI-powered research tools.",
            "semaglutide": "Semaglutide represents a breakthrough in obesity treatment, showing significant weight loss results in clinical trials. The GLP-1 receptor agonist has transformed the pharmaceutical landscape for metabolic disorders and diabetes management.",
            "market_analysis": "The obesity drug market is experiencing unprecedented growth, driven by increasing prevalence of obesity worldwide and the success of new GLP-1 medications like semaglutide and tirzepatide."
        }
    
    async def __aenter__(self):
        if not self.use_mock_data and AIOHTTP_AVAILABLE:
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    # Original interface methods (for compatibility with existing agent service)
    async def extract_content(self, request) -> Dict[str, Any]:
        """
        Extract content from URLs (original interface).
        
        Args:
            request: ContentExtractionRequest with urls, request_id, extraction_mode
            
        Returns:
            Dict representing PerplexityResponse
        """
        try:
            if self.use_mock_data:
                return await self._mock_extract_content(request)
            else:
                return await self._real_extract_content(request)
        except Exception as e:
            print(f"Perplexity extract_content error: {e}")
            return await self._mock_extract_content(request)
    
    async def _mock_extract_content(self, request) -> Dict[str, Any]:
        """Mock content extraction matching original PerplexityResponse structure"""
        await asyncio.sleep(0.2)  # Simulate processing time
        
        extracted_content = []
        successful = 0
        
        urls = getattr(request, 'urls', [])
        request_id = getattr(request, 'request_id', 'mock_request')
        extraction_mode = getattr(request, 'extraction_mode', 'summary')
        
        for i, url in enumerate(urls):
            # Simulate some failures (every 5th URL fails)
            if i % 5 == 4:
                continue
            
            content_item = self._generate_mock_url_extraction(str(url), i)
            extracted_content.append(content_item)
            successful += 1
        
        failed = len(urls) - successful
        
        return {
            "request_id": request_id,
            "total_urls": len(urls),
            "successful_extractions": successful,
            "failed_extractions": failed,
            "extracted_content": extracted_content,
            "processing_metadata": {"source": "mock", "mode": extraction_mode},
            "created_at": "2025-01-27T12:00:00Z"
        }
    
    def _generate_mock_url_extraction(self, url: str, index: int) -> Dict[str, Any]:
        """Generate mock extraction for single URL matching ExtractedContent structure"""
        from datetime import datetime
        
        # Select content based on URL domain or index
        url_lower = url.lower()
        
        if "fda.gov" in url_lower:
            content_key = "regulation"
            title = "FDA AI Regulation Guidelines"
            confidence = 0.9
        elif "pharma" in url_lower:
            content_key = "pharmaceutical"
            title = "Pharmaceutical AI Development Standards"
            confidence = 0.85
        elif "semaglutide" in url_lower or "obesity" in url_lower:
            content_key = "semaglutide"
            title = "Semaglutide Market Analysis"
            confidence = 0.88
        elif "ai" in url_lower or "drug" in url_lower:
            content_key = "ai_drug_discovery"
            title = "AI in Drug Discovery: Latest Advances"
            confidence = 0.8
        else:
            content_key = "market_analysis"
            title = "Market Analysis Report"
            confidence = 0.75
        
        content = self.url_mock_content.get(content_key, self.url_mock_content["pharmaceutical"])
        
        return {
            "url": url,
            "title": f"{title} - Analysis {index + 1}",
            "content": content,
            "metadata": {
                "extraction_method": "mock",
                "mock_category": content_key,
                "generated_at": datetime.utcnow().isoformat(),
                "citations": [url],
                "usage": {"total_tokens": len(content.split()) * 1.3, "total_cost": 0.01}
            },
            "author": "Mock Author",
            "published_date": datetime.utcnow().isoformat(),
            "word_count": len(content.split()),
            "language": "en",
            "content_type": "article",
            "extraction_confidence": confidence
        }
    
    async def _real_extract_content(self, request) -> Dict[str, Any]:
        """Real content extraction using Perplexity API"""
        # This would implement the real API calls similar to the original PerplexityAPI
        # For now, fall back to mock
        return await self._mock_extract_content(request)
    
    # New search interface methods (for market intelligence queries)
    async def search(self, query: str, model: str = "sonar-pro", max_tokens: int = 1024) -> str:
        """
        Execute a Perplexity search query and return the response text.
        
        Args:
            query: The search query
            model: The Perplexity model to use
            max_tokens: Maximum tokens in response
            
        Returns:
            str: The response text content
        """
        try:
            if self.use_mock_data or not self.perplexity_client:
                return await self._get_mock_response(query)
            else:
                # Use the existing PerplexityClient
                return self.perplexity_client.search(query)
        except Exception as e:
            print(f"Perplexity search error: {e}")
            return f"Mock response for testing purposes. Query: {query[:100]}..."
    
    async def search_with_metadata(self, query: str, model: str = "sonar-pro", max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Execute a Perplexity search query and return full response with metadata.
        
        Args:
            query: The search query
            model: The Perplexity model to use
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict[str, Any]: Full response including content, citations, usage, etc.
        """
        try:
            if self.use_mock_data or not self.perplexity_client:
                return await self._get_mock_response_with_metadata(query)
            else:
                # Use the existing PerplexityClient
                content = self.perplexity_client.search(query)
                return {
                    "content": content,
                    "citations": [],  # Your client doesn't return citations in this format
                    "search_results": [],
                    "usage": {"total_tokens": len(content.split()) * 1.3, "total_cost": 0.015},
                    "model": model
                }
        except Exception as e:
            print(f"Perplexity search with metadata error: {e}")
            return {
                "content": f"Mock response for testing purposes. Query: {query[:100]}...",
                "citations": [],
                "search_results": [],
                "usage": {"total_tokens": 0, "total_cost": 0.0},
                "error": str(e)
            }
    
    async def _get_mock_response(self, query: str) -> str:
        """Get mock response text based on query content"""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        query_lower = query.lower()
        if "summary" in query_lower or "summarize" in query_lower:
            response_type = "summary"
        elif "insight" in query_lower or "analyze" in query_lower:
            response_type = "insights"
        elif "implication" in query_lower or "impact" in query_lower:
            response_type = "implications"
        else:
            response_type = random.choice(["summary", "insights", "implications"])
        
        mock_response = self.search_mock_responses[response_type]
        return mock_response["choices"][0]["message"]["content"]
    
    async def _get_mock_response_with_metadata(self, query: str) -> Dict[str, Any]:
        """Get mock response with full metadata based on query content"""
        await asyncio.sleep(0.5)  # Simulate API delay
        
        query_lower = query.lower()
        if "summary" in query_lower or "summarize" in query_lower:
            response_type = "summary"
        elif "insight" in query_lower or "analyze" in query_lower:
            response_type = "insights"
        elif "implication" in query_lower or "impact" in query_lower:
            response_type = "implications"
        else:
            response_type = random.choice(["summary", "insights", "implications"])
        
        mock_response = self.search_mock_responses[response_type]
        
        return {
            "content": mock_response["choices"][0]["message"]["content"],
            "citations": mock_response["citations"],
            "search_results": mock_response["search_results"],
            "usage": mock_response["usage"],
            "model": mock_response["model"],
            "id": mock_response["id"]
        }
    
    async def _execute_real_api_call(self, query: str, model: str, max_tokens: int) -> str:
        """Execute real Perplexity API call"""
        response_data = await self._execute_real_api_call_with_metadata(query, model, max_tokens)
        return response_data.get("content", "")
    
    async def _execute_real_api_call_with_metadata(self, query: str, model: str, max_tokens: int) -> Dict[str, Any]:
        """Execute real Perplexity API call with full metadata"""
        if not AIOHTTP_AVAILABLE:
            print("Perplexity search with metadata error: aiohttp not available, falling back to mock")
            return await self._get_mock_response_with_metadata(query)
            
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": query}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
            "return_citations": True
        }
        
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            return {
                "content": data["choices"][0]["message"]["content"],
                "citations": data.get("citations", []),
                "search_results": data.get("search_results", []),
                "usage": data.get("usage", {}),
                "model": data.get("model", model),
                "id": data.get("id", "")
                         }


class MockSerpClient:
    """
    Mock SERP API client that matches the original interface.
    
    This provides URL discovery functionality for market intelligence
    by searching for relevant content based on keywords and domains.
    """
    
    def __init__(self, api_key: Optional[str] = None, use_mock_data: bool = True):
        self.api_key = api_key or os.getenv("SERPAPI_KEY", "mock_key")
        self.use_mock_data = use_mock_data
        self.base_url = "https://serpapi.com/search"
        self.session = None
        
        # Mock search results for different domains and topics
        self.mock_results = {
            "semaglutide": [
                {
                    "title": "Lilly pill cuts body weight by 10.5% in patients with obesity",
                    "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/lilly-pill-cuts-body-weight-105-patients-obesity-2025-08-26/",
                    "snippet": "Topline data from orforglipron's earlier-stage study showed the experimental pill helped patients lose an average of 10.5% of their body weight...",
                    "source": "Reuters",
                    "domain": "reuters.com",
                    "date": "6 days ago"
                },
                {
                    "title": "Mounjaro manufacturer pauses UK shipments ahead of price hike",
                    "url": "https://news.sky.com/story/mounjaro-manufacturer-pauses-uk-shipments-ahead-of-price-hike-13234567",
                    "snippet": "Eli Lilly has temporarily halted UK shipments of Mounjaro (tirzepatide), a popular weight-loss drug, ahead of a significant price increase...",
                    "source": "Sky News",
                    "domain": "news.sky.com",
                    "date": "3 days ago"
                },
                {
                    "title": "Semaglutide Market Analysis and Growth Projections 2025",
                    "url": "https://pharmaphorum.com/news/semaglutide-market-analysis-growth-projections-2025/",
                    "snippet": "The global semaglutide market is experiencing unprecedented growth, driven by increasing obesity rates and successful clinical outcomes...",
                    "source": "PharmaPhorum",
                    "domain": "pharmaphorum.com",
                    "date": "1 week ago"
                }
            ],
            "obesity_drugs": [
                {
                    "title": "FDA Approves New Obesity Treatment Guidelines",
                    "url": "https://www.fda.gov/news-events/press-announcements/fda-approves-new-obesity-treatment-guidelines-2025",
                    "snippet": "The FDA has announced updated guidelines for obesity treatment medications, including new safety protocols and prescribing recommendations...",
                    "source": "FDA",
                    "domain": "fda.gov",
                    "date": "2 weeks ago"
                },
                {
                    "title": "Clinical Trial Results: Next-Generation Obesity Drugs",
                    "url": "https://clinicaltrials.gov/study/NCT05123456",
                    "snippet": "Phase III clinical trial results demonstrate significant efficacy of next-generation GLP-1 receptor agonists in obesity treatment...",
                    "source": "ClinicalTrials.gov",
                    "domain": "clinicaltrials.gov",
                    "date": "5 days ago"
                }
            ],
            "pharmaceutical_regulation": [
                {
                    "title": "EMA Issues New Pharmaceutical Regulation Framework",
                    "url": "https://www.ema.europa.eu/en/news/ema-issues-new-pharmaceutical-regulation-framework",
                    "snippet": "The European Medicines Agency has published new regulatory framework for pharmaceutical development and approval processes...",
                    "source": "EMA",
                    "domain": "ema.europa.eu",
                    "date": "1 week ago"
                }
            ]
        }
    
    async def __aenter__(self):
        if not self.use_mock_data and AIOHTTP_AVAILABLE:
            self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    # Original interface methods (for compatibility with existing agent service)
    async def search(self, request) -> Dict[str, Any]:
        """
        Execute search query (original interface).
        
        Args:
            request: SerpRequest with query, num_results, etc.
            
        Returns:
            Dict representing SerpResponse
        """
        try:
            if self.use_mock_data:
                return await self._mock_search(request)
            else:
                return await self._real_search(request)
        except Exception as e:
            print(f"SERP search error: {e}")
            return await self._mock_search(request)
    
    async def _mock_search(self, request) -> Dict[str, Any]:
        """Mock search execution matching original SerpResponse structure"""
        await asyncio.sleep(0.1)  # Simulate API delay
        
        query = getattr(request, 'query', '')
        num_results = getattr(request, 'num_results', 10)
        
        # Select relevant mock results based on query
        results = self._select_mock_results_by_query(query, num_results)
        
        return {
            "request_id": f"mock_serp_{int(asyncio.get_event_loop().time())}",
            "query": query,
            "total_results": len(results) * 10,  # Simulate larger result set
            "results": results,
            "search_metadata": {"source": "mock", "engine": "mock_google"},
            "created_at": datetime.utcnow().isoformat()
        }
    
    def _select_mock_results_by_query(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Select mock results based on query content"""
        query_lower = query.lower()
        selected_results = []
        
        # Determine query category and select appropriate results
        if "semaglutide" in query_lower or "tirzepatide" in query_lower:
            category_results = self.mock_results["semaglutide"]
        elif "obesity" in query_lower or "weight loss" in query_lower:
            category_results = self.mock_results["obesity_drugs"]
        elif "regulation" in query_lower or "fda" in query_lower or "ema" in query_lower:
            category_results = self.mock_results["pharmaceutical_regulation"]
        else:
            # Mix results from all categories
            category_results = []
            for category in self.mock_results.values():
                category_results.extend(category[:2])  # Take 2 from each category
        
        # Convert to proper format and add position
        for i, result in enumerate(category_results[:num_results]):
            formatted_result = {
                "title": result["title"],
                "url": result["url"],
                "snippet": result["snippet"],
                "position": i + 1,
                "domain": result["domain"],
                "published_date": None  # Could add mock dates if needed
            }
            selected_results.append(formatted_result)
        
        return selected_results
    
    async def _real_search(self, request) -> Dict[str, Any]:
        """Real SERP API search"""
        if not AIOHTTP_AVAILABLE:
            print("SERP search error: aiohttp not available, falling back to mock")
            return await self._mock_search(request)
            
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        params = {
            "q": getattr(request, 'query', ''),
            "api_key": self.api_key,
            "engine": getattr(request, 'engine', 'google'),
            "num": getattr(request, 'num_results', 10),
            "hl": getattr(request, 'language', 'en'),
            "gl": getattr(request, 'country', 'us'),
            "format": "json"
        }
        
        async with self.session.get(self.base_url, params=params) as response:
            response.raise_for_status()
            data = await response.json()
            
            # Parse response to match our format
            organic_results = data.get("organic_results", [])
            results = []
            
            for i, result in enumerate(organic_results):
                formatted_result = {
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": i + 1,
                    "domain": self._extract_domain(result.get("link", "")),
                    "published_date": result.get("date")
                }
                results.append(formatted_result)
            
            return {
                "request_id": f"serp_{int(asyncio.get_event_loop().time())}",
                "query": params["q"],
                "total_results": data.get("search_information", {}).get("total_results", 0),
                "results": results,
                "search_metadata": data.get("search_metadata", {}),
                "created_at": datetime.utcnow().isoformat()
            }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return ""
    
    # New search interface methods (for market intelligence queries)
    async def search_by_keywords_and_domain(self, keywords: List[str], domain: str, num_results: int = 10) -> Dict[str, Any]:
        """
        Search for URLs by keywords within a specific domain.
        
        Args:
            keywords: List of search keywords
            domain: Target domain to search within
            num_results: Maximum number of results
            
        Returns:
            Dict with exact_urls, url_details, search_query, total_found
        """
        try:
            # Build search query
            search_query = f"{' '.join(keywords)} site:{domain}"
            
            # Create mock request object
            class MockRequest:
                def __init__(self, query, num_results):
                    self.query = query
                    self.num_results = num_results
                    self.engine = "google"
                    self.language = "en"
                    self.country = "us"
            
            request = MockRequest(search_query, num_results)
            
            # Execute search
            search_response = await self.search(request)
            
            # Extract URLs and details
            results = search_response.get("results", [])
            exact_urls = [result["url"] for result in results]
            url_details = [
                {
                    "url": result["url"],
                    "title": result["title"],
                    "date": result.get("published_date") or "Recent",
                    "snippet": result["snippet"],
                    "source": result["domain"],
                    "position": result["position"]
                }
                for result in results
            ]
            
            return {
                "exact_urls": exact_urls,
                "url_details": url_details,
                "search_query": search_query,
                "total_found": len(exact_urls)
            }
            
        except Exception as e:
            print(f"SERP search by keywords and domain error: {e}")
            return {
                "exact_urls": [],
                "url_details": [],
                "search_query": f"{' '.join(keywords)} site:{domain}",
                "total_found": 0,
                "error": str(e)
            }
    
    # Legacy method for backward compatibility
    async def call_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy API call method"""
        try:
            class MockRequest:
                def __init__(self, query, num_results):
                    self.query = query
                    self.num_results = num_results
                    self.engine = "google"
                    self.language = "en"
                    self.country = "us"
            
            request = MockRequest(
                data.get("query", ""),
                data.get("num_results", 10)
            )
            response = await self.search(request)
            return {
                "status": "success", 
                "data": response
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


class TempServiceFactory:
    """
    Temporary service factory for Root Orchestrator.
    
    This provides basic mock services for development and testing
    without depending on the existing configuration system.
    """
    
    _database_client: Optional[MockDatabaseClient] = None
    _storage_client: Optional[MockStorageClient] = None
    _minio_client: Optional[MockMinioClient] = None
    _perplexity_client: Optional[PerplexityClientWrapper] = None
    _serp_client: Optional[MockSerpClient] = None
    
    @classmethod
    def get_database_client(cls) -> MockDatabaseClient:
        """Get database client instance"""
        if cls._database_client is None:
            cls._database_client = MockDatabaseClient()
        return cls._database_client
    
    @classmethod
    def get_storage_client(cls) -> MockStorageClient:
        """Get storage client instance"""
        if cls._storage_client is None:
            cls._storage_client = MockStorageClient()
        return cls._storage_client
    
    @classmethod
    def get_minio_client(cls) -> MockMinioClient:
        """Get MinIO client instance"""
        if cls._minio_client is None:
            endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9001")
            access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
            secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin123")
            cls._minio_client = MockMinioClient(endpoint, access_key, secret_key)
        return cls._minio_client
    
    @classmethod
    def get_perplexity_client(cls) -> PerplexityClientWrapper:
        """Get Perplexity client instance"""
        if cls._perplexity_client is None:
            use_mock = os.getenv("AGENT_SERVICE_USE_MOCK_DATA", "true").lower() == "true"
            cls._perplexity_client = PerplexityClientWrapper(use_mock_data=use_mock)
        return cls._perplexity_client
    
    @classmethod
    def get_serp_client(cls) -> MockSerpClient:
        """Get SERP client instance"""
        if cls._serp_client is None:
            use_mock = os.getenv("AGENT_SERVICE_USE_MOCK_DATA", "true").lower() == "true"
            cls._serp_client = MockSerpClient(use_mock_data=use_mock)
        return cls._serp_client
    
    @classmethod
    def reset(cls):
        """Reset all service instances (for testing)"""
        cls._database_client = None
        cls._storage_client = None
        cls._minio_client = None
        cls._perplexity_client = None
        cls._serp_client = None


# For compatibility with existing imports
ServiceFactory = TempServiceFactory 