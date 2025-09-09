# Stage 0 Perplexity Agent Implementation

## 10-Line Prompt:
Create Perplexity content extraction agent that processes URLs from SERP results to extract structured content summaries and metadata, includes real Perplexity API integration with batch processing capabilities and rate limiting, mock implementation that generates realistic content extractions for testing without API calls, response processing that validates extracted content quality and confidence scores, content models for structured summaries with metadata like author and publish date, service orchestration that manages batch URL processing and error handling for failed extractions, storage operations to save extracted content and summaries for agent processing pipeline, database operations to track extraction status and content metadata in DynamoDB, comprehensive error handling for API failures and content extraction errors, and environment-based configuration for switching between real and mock implementations seamlessly.

## What it covers: 
Content extraction, URL processing, batch operations, content validation
## Methods: 
Perplexity API integration, content parsing, batch processing, quality scoring
## Why: 
Content foundation for agents, structured data extraction, scalable processing

---

## models.py
```python
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime

class ContentExtractionRequest(BaseModel):
    """Request for extracting content from URLs"""
    urls: List[HttpUrl] = Field(..., description="URLs to extract")
    request_id: str = Field(..., description="SERP request ID")
    extraction_mode: str = Field(default="summary", description="full|summary|metadata")
    max_content_length: int = Field(default=5000, description="Max content length")

class ExtractedContent(BaseModel):
    """Individual extracted content item"""
    url: HttpUrl = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Extracted content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    author: Optional[str] = Field(default=None)
    published_date: Optional[datetime] = Field(default=None)
    word_count: int = Field(default=0)
    language: str = Field(default="en")
    content_type: str = Field(default="article")
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    
    def is_high_quality(self) -> bool:
        """Check if content meets quality threshold"""
        return (self.extraction_confidence >= 0.7 and 
                self.word_count >= 100 and 
                len(self.title) >= 10)

class PerplexityResponse(BaseModel):
    """Complete content extraction response"""
    request_id: str = Field(..., description="Request ID")
    total_urls: int = Field(..., description="Total URLs processed")
    successful_extractions: int = Field(..., description="Successful extractions")
    failed_extractions: int = Field(..., description="Failed extractions")
    extracted_content: List[ExtractedContent] = Field(..., description="Content items")
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_successful_content(self) -> List[ExtractedContent]:
        """Get successfully extracted content"""
        return [content for content in self.extracted_content if content.content]
    
    def get_high_quality_content(self) -> List[ExtractedContent]:
        """Get high quality content only"""
        return [content for content in self.extracted_content if content.is_high_quality()]

class BatchExtractionStatus(BaseModel):
    """Batch processing status tracking"""
    batch_id: str = Field(..., description="Batch ID")
    total_urls: int = Field(..., description="Total URLs")
    completed: int = Field(default=0)
    failed: int = Field(default=0)
    in_progress: int = Field(default=0)
    status: str = Field(default="pending")
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage"""
        if self.total_urls == 0:
            return 0.0
        return (self.completed + self.failed) / self.total_urls * 100
```

## perplexity_api.py
```python
import asyncio
import aiohttp
from typing import List, Dict, Any
from .models import ContentExtractionRequest, PerplexityResponse, ExtractedContent
from ...config.settings import settings
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityAPI:
    """Real Perplexity API client for content extraction"""
    
    def __init__(self):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
        self.session = None
        self.rate_limit_delay = 1.0  # seconds between requests
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def extract_content(self, request: ContentExtractionRequest) -> PerplexityResponse:
        """Extract content from multiple URLs"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            logger.info(f"Starting Perplexity extraction for {len(request.urls)} URLs")
            
            extracted_content = []
            successful = 0
            failed = 0
            
            for url in request.urls:
                try:
                    content = await self._extract_single_url(url, request.extraction_mode)
                    if content:
                        extracted_content.append(content)
                        successful += 1
                    else:
                        failed += 1
                    
                    # Rate limiting
                    await asyncio.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    logger.warning(f"Failed to extract {url}: {str(e)}")
                    failed += 1
                    continue
            
            return PerplexityResponse(
                request_id=request.request_id,
                total_urls=len(request.urls),
                successful_extractions=successful,
                failed_extractions=failed,
                extracted_content=extracted_content,
                processing_metadata={"extraction_mode": request.extraction_mode}
            )
            
        except Exception as e:
            logger.error(f"Perplexity API error: {str(e)}")
            raise Exception(f"Content extraction failed: {str(e)}")
    
    async def _extract_single_url(self, url: str, mode: str) -> Optional[ExtractedContent]:
        """Extract content from single URL"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {
                        "role": "system",
                        "content": f"Extract and summarize content from the provided URL. Mode: {mode}"
                    },
                    {
                        "role": "user", 
                        "content": f"Extract content from: {url}"
                    }
                ],
                "max_tokens": 2000,
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
                
                return self._parse_extraction_response(data, url)
                
        except Exception as e:
            logger.error(f"Single URL extraction error for {url}: {str(e)}")
            return None
    
    def _parse_extraction_response(self, data: Dict[str, Any], url: str) -> Optional[ExtractedContent]:
        """Parse Perplexity API response"""
        try:
            choices = data.get("choices", [])
            if not choices:
                return None
            
            message = choices[0].get("message", {})
            content = message.get("content", "")
            
            if not content:
                return None
            
            # Extract metadata from response
            citations = data.get("citations", [])
            usage = data.get("usage", {})
            
            # Parse content for title and summary
            lines = content.split('\n')
            title = lines[0] if lines else "Untitled"
            summary = '\n'.join(lines[1:]) if len(lines) > 1 else content
            
            return ExtractedContent(
                url=url,
                title=self._clean_title(title),
                content=summary,
                metadata={
                    "citations": citations,
                    "usage": usage,
                    "extraction_method": "perplexity_api"
                },
                word_count=len(summary.split()),
                extraction_confidence=self._calculate_confidence(summary, citations)
            )
            
        except Exception as e:
            logger.error(f"Response parsing error: {str(e)}")
            return None
    
    def _clean_title(self, title: str) -> str:
        """Clean extracted title"""
        # Remove common prefixes/suffixes
        prefixes = ["Title:", "# ", "## "]
        for prefix in prefixes:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
        
        return title[:200]  # Limit length
    
    def _calculate_confidence(self, content: str, citations: List) -> float:
        """Calculate extraction confidence score"""
        base_score = 0.5
        
        # Length factor
        if len(content) > 500:
            base_score += 0.2
        elif len(content) > 200:
            base_score += 0.1
        
        # Citations factor
        if citations:
            base_score += min(len(citations) * 0.1, 0.3)
        
        return min(base_score, 1.0)
```

## perplexity_mock.py
```python
import asyncio
from typing import List, Optional
from datetime import datetime
from .models import ContentExtractionRequest, PerplexityResponse, ExtractedContent
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityMock:
    """Mock Perplexity API for testing"""
    
    def __init__(self):
        self.mock_content = self._generate_mock_content()
    
    async def extract_content(self, request: ContentExtractionRequest) -> PerplexityResponse:
        """Mock content extraction"""
        await asyncio.sleep(0.2)  # Simulate processing time
        
        logger.info(f"Mock Perplexity extraction for {len(request.urls)} URLs")
        
        extracted_content = []
        successful = 0
        
        for i, url in enumerate(request.urls):
            # Simulate some failures
            if i % 5 == 4:  # Fail every 5th URL
                continue
            
            content = self._generate_mock_extraction(url, i)
            extracted_content.append(content)
            successful += 1
        
        failed = len(request.urls) - successful
        
        return PerplexityResponse(
            request_id=request.request_id,
            total_urls=len(request.urls),
            successful_extractions=successful,
            failed_extractions=failed,
            extracted_content=extracted_content,
            processing_metadata={"source": "mock", "mode": request.extraction_mode}
        )
    
    def _generate_mock_content(self) -> Dict[str, str]:
        """Generate realistic mock content templates"""
        return {
            "pharmaceutical": "This article discusses the latest developments in pharmaceutical AI regulation. The FDA has announced new guidelines for AI-powered drug discovery tools, emphasizing the need for transparency and validation in machine learning models used for therapeutic development.",
            "regulation": "New regulatory frameworks are being established to govern the use of artificial intelligence in healthcare and pharmaceutical industries. These regulations aim to ensure patient safety while promoting innovation in AI-driven medical technologies.",
            "ai_drug_discovery": "Artificial intelligence is revolutionizing drug discovery processes, enabling researchers to identify potential therapeutic compounds faster than traditional methods. Machine learning algorithms can predict molecular behavior and optimize drug candidates for clinical trials.",
            "compliance": "Pharmaceutical companies must now comply with updated AI governance requirements that mandate documentation of algorithmic decision-making processes, data validation procedures, and bias mitigation strategies in AI-powered research tools."
        }
    
    def _generate_mock_extraction(self, url: str, index: int) -> ExtractedContent:
        """Generate mock extraction for single URL"""
        # Select content based on URL domain or index
        url_str = str(url).lower()
        
        if "fda.gov" in url_str:
            content_key = "regulation"
            title = "FDA AI Regulation Guidelines"
            confidence = 0.9
        elif "pharma" in url_str:
            content_key = "pharmaceutical"
            title = "Pharmaceutical AI Development Standards"
            confidence = 0.85
        elif "ai" in url_str or "drug" in url_str:
            content_key = "ai_drug_discovery"
            title = "AI in Drug Discovery: Latest Advances"
            confidence = 0.8
        else:
            content_key = "compliance"
            title = "AI Compliance Requirements for Healthcare"
            confidence = 0.75
        
        content = self.mock_content.get(content_key, self.mock_content["pharmaceutical"])
        
        return ExtractedContent(
            url=url,
            title=f"{title} - Analysis {index + 1}",
            content=content,
            metadata={
                "extraction_method": "mock",
                "mock_category": content_key,
                "generated_at": datetime.utcnow().isoformat()
            },
            author="Mock Author",
            published_date=datetime.utcnow(),
            word_count=len(content.split()),
            language="en",
            content_type="article",
            extraction_confidence=confidence
        )
```

## perplexity_response.py
```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from .models import PerplexityResponse, ExtractedContent
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityResponseHandler:
    """Process and validate Perplexity API responses"""
    
    @staticmethod
    def process_batch_response(responses: List[Dict[str, Any]], request_id: str) -> PerplexityResponse:
        """Process batch extraction responses"""
        try:
            extracted_content = []
            successful = 0
            failed = 0
            
            for response_data in responses:
                processed = PerplexityResponseHandler._process_single_response(response_data)
                if processed:
                    extracted_content.append(processed)
                    successful += 1
                else:
                    failed += 1
            
            return PerplexityResponse(
                request_id=request_id,
                total_urls=len(responses),
                successful_extractions=successful,
                failed_extractions=failed,
                extracted_content=extracted_content,
                processing_metadata=PerplexityResponseHandler._extract_batch_metadata(responses)
            )
            
        except Exception as e:
            logger.error(f"Batch response processing error: {str(e)}")
            raise ValueError(f"Invalid batch response: {str(e)}")
    
    @staticmethod
    def _process_single_response(response: Dict[str, Any]) -> Optional[ExtractedContent]:
        """Process single extraction response"""
        try:
            choices = response.get("choices", [])
            if not choices:
                return None
            
            message = choices[0].get("message", {})
            content = message.get("content", "")
            
            if not content or len(content.strip()) < 50:
                return None
            
            # Extract URL from metadata or response
            url = response.get("url", "")
            if not url:
                return None
            
            # Parse structured content
            parsed = PerplexityResponseHandler._parse_content_structure(content)
            
            return ExtractedContent(
                url=url,
                title=parsed["title"],
                content=parsed["summary"],
                metadata=PerplexityResponseHandler._extract_content_metadata(response),
                author=parsed.get("author"),
                published_date=parsed.get("published_date"),
                word_count=len(parsed["summary"].split()),
                language=parsed.get("language", "en"),
                content_type=parsed.get("content_type", "article"),
                extraction_confidence=PerplexityResponseHandler._calculate_quality_score(parsed, response)
            )
            
        except Exception as e:
            logger.warning(f"Single response processing error: {str(e)}")
            return None
    
    @staticmethod
    def _parse_content_structure(content: str) -> Dict[str, Any]:
        """Parse structured content from extraction"""
        lines = content.strip().split('\n')
        
        # Extract title (usually first line)
        title = lines[0].strip() if lines else "Untitled"
        title = PerplexityResponseHandler._clean_title(title)
        
        # Extract summary (remaining content)
        summary_lines = lines[1:] if len(lines) > 1 else [content]
        summary = '\n'.join(summary_lines).strip()
        
        # Try to extract metadata from structured content
        metadata = PerplexityResponseHandler._extract_inline_metadata(content)
        
        return {
            "title": title,
            "summary": summary,
            "author": metadata.get("author"),
            "published_date": metadata.get("published_date"),
            "language": metadata.get("language", "en"),
            "content_type": metadata.get("content_type", "article")
        }
    
    @staticmethod
    def _clean_title(title: str) -> str:
        """Clean and normalize title"""
        # Remove common markdown/formatting
        prefixes = ["# ", "## ", "### ", "Title:", "TITLE:"]
        for prefix in prefixes:
            if title.upper().startswith(prefix.upper()):
                title = title[len(prefix):].strip()
        
        # Remove quotes
        if title.startswith('"') and title.endswith('"'):
            title = title[1:-1]
        
        return title[:200]  # Limit length
    
    @staticmethod
    def _extract_inline_metadata(content: str) -> Dict[str, Any]:
        """Extract metadata from content text"""
        metadata = {}
        
        # Look for author patterns
        import re
        author_patterns = [
            r"Author:\s*(.+)",
            r"By\s+(.+)",
            r"Written by\s+(.+)"
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata["author"] = match.group(1).strip()
                break
        
        # Look for date patterns
        date_patterns = [
            r"Published:\s*(.+)",
            r"Date:\s*(.+)",
            r"(\d{4}-\d{2}-\d{2})"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    date_str = match.group(1).strip()
                    # Try to parse date (simplified)
                    if len(date_str) == 10 and date_str.count('-') == 2:
                        metadata["published_date"] = datetime.fromisoformat(date_str)
                except:
                    pass
        
        return metadata
    
    @staticmethod
    def _calculate_quality_score(parsed: Dict[str, Any], response: Dict[str, Any]) -> float:
        """Calculate content quality score"""
        score = 0.0
        
        # Title quality
        title = parsed.get("title", "")
        if title and title != "Untitled":
            score += 0.2
            if len(title) > 20:
                score += 0.1
        
        # Content length
        summary = parsed.get("summary", "")
        word_count = len(summary.split())
        if word_count >= 100:
            score += 0.3
        elif word_count >= 50:
            score += 0.2
        elif word_count >= 20:
            score += 0.1
        
        # Metadata presence
        if parsed.get("author"):
            score += 0.1
        if parsed.get("published_date"):
            score += 0.1
        
        # Response quality indicators
        usage = response.get("usage", {})
        if usage.get("total_tokens", 0) > 500:
            score += 0.1
        
        citations = response.get("citations", [])
        if citations:
            score += min(len(citations) * 0.05, 0.2)
        
        return min(score, 1.0)
    
    @staticmethod
    def _extract_content_metadata(response: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from API response"""
        return {
            "usage": response.get("usage", {}),
            "citations": response.get("citations", []),
            "model": response.get("model", ""),
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "response_id": response.get("id", "")
        }
    
    @staticmethod
    def _extract_batch_metadata(responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract metadata from batch responses"""
        total_tokens = sum(
            resp.get("usage", {}).get("total_tokens", 0) 
            for resp in responses
        )
        
        total_citations = sum(
            len(resp.get("citations", [])) 
            for resp in responses
        )
        
        return {
            "batch_size": len(responses),
            "total_tokens_used": total_tokens,
            "total_citations": total_citations,
            "processed_at": datetime.utcnow().isoformat()
        }
```

## service.py
```python
from typing import List, Optional
from ...config.service_factory import ServiceFactory
from .models import ContentExtractionRequest, PerplexityResponse
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityService:
    """Main Perplexity service for content extraction"""
    
    def __init__(self):
        self.perplexity_client = ServiceFactory.get_perplexity_client()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def extract_content(self, urls: List[str], request_id: str) -> PerplexityResponse:
        """Extract content from URLs"""
        try:
            logger.info(f"Starting content extraction for {len(urls)} URLs")
            
            request = ContentExtractionRequest(
                urls=urls,
                request_id=request_id,
                extraction_mode="summary"
            )
            
            # Execute extraction
            response = await self.perplexity_client.extract_content(request)
            
            # Validate and filter results
            validated_response = self._validate_response(response)
            
            # Store results
            await self._store_extraction_results(validated_response)
            
            logger.info(f"Content extraction completed. Success: {validated_response.successful_extractions}, Failed: {validated_response.failed_extractions}")
            return validated_response
            
        except Exception as e:
            logger.error(f"Content extraction error: {str(e)}")
            raise Exception(f"Extraction failed: {str(e)}")
    
    async def extract_content_batch(self, urls: List[str], request_id: str, batch_size: int = 10) -> PerplexityResponse:
        """Extract content in batches"""
        try:
            all_content = []
            total_successful = 0
            total_failed = 0
            
            # Process in batches
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i + batch_size]
                batch_id = f"{request_id}_batch_{i // batch_size}"
                
                logger.info(f"Processing batch {i // batch_size + 1}: {len(batch_urls)} URLs")
                
                try:
                    batch_request = ContentExtractionRequest(
                        urls=batch_urls,
                        request_id=batch_id,
                        extraction_mode="summary"
                    )
                    
                    batch_response = await self.perplexity_client.extract_content(batch_request)
                    
                    all_content.extend(batch_response.extracted_content)
                    total_successful += batch_response.successful_extractions
                    total_failed += batch_response.failed_extractions
                    
                except Exception as e:
                    logger.error(f"Batch {batch_id} failed: {str(e)}")
                    total_failed += len(batch_urls)
                    continue
            
            # Create combined response
            combined_response = PerplexityResponse(
                request_id=request_id,
                total_urls=len(urls),
                successful_extractions=total_successful,
                failed_extractions=total_failed,
                extracted_content=all_content,
                processing_metadata={"processing_mode": "batch", "batch_size": batch_size}
            )
            
            # Store combined results
            await self._store_extraction_results(combined_response)
            
            return combined_response
            
        except Exception as e:
            logger.error(f"Batch extraction error: {str(e)}")
            raise
    
    def _validate_response(self, response: PerplexityResponse) -> PerplexityResponse:
        """Validate and filter extraction response"""
        # Filter out low-quality content
        high_quality_content = []
        
        for content in response.extracted_content:
            if self._is_content_valid(content):
                high_quality_content.append(content)
        
        response.extracted_content = high_quality_content
        response.successful_extractions = len(high_quality_content)
        response.failed_extractions = response.total_urls - len(high_quality_content)
        
        logger.info(f"Filtered to {len(high_quality_content)} high-quality extractions")
        return response
    
    def _is_content_valid(self, content) -> bool:
        """Check if extracted content meets quality standards"""
        # Minimum content length
        if not content.content or len(content.content.strip()) < 100:
            return False
        
        # Must have title
        if not content.title or content.title == "Untitled":
            return False
        
        # Minimum confidence score
        if content.extraction_confidence < 0.5:
            return False
        
        # Check for common extraction errors
        error_indicators = ["error", "404", "not found", "access denied"]
        content_lower = content.content.lower()
        if any(indicator in content_lower for indicator in error_indicators):
            return False
        
        return True
    
    async def _store_extraction_results(self, response: PerplexityResponse):
        """Store extraction results"""
        try:
            # Store in object storage
            storage_key = f"perplexity_results/{response.request_id}.json"
            await self.storage_client.save_json(storage_key, response.dict())
            
            # Store individual content items
            for i, content in enumerate(response.extracted_content):
                content_key = f"perplexity_content/{response.request_id}/{i}.json"
                await self.storage_client.save_json(content_key, content.dict())
            
            # Store metadata in database
            await self.database_client.save_item("perplexity_extractions", {
                "request_id": response.request_id,
                "total_urls": response.total_urls,
                "successful_extractions": response.successful_extractions,
                "failed_extractions": response.failed_extractions,
                "storage_key": storage_key,
                "created_at": response.created_at.isoformat()
            })
            
            logger.info(f"Stored extraction results: {storage_key}")
            
        except Exception as e:
            logger.error(f"Failed to store extraction results: {str(e)}")
```

## storage.py
```python
from typing import Dict, Any, List, Optional
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityStorage:
    """Handle Perplexity-specific storage operations"""
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def save_extraction_results(self, request_id: str, results: Dict[str, Any]) -> bool:
        """Save extraction results to storage"""
        try:
            key = f"perplexity_results/{request_id}.json"
            success = await self.storage_client.save_json(key, results)
            
            if success:
                logger.info(f"Saved Perplexity results: {key}")
            else:
                logger.error(f"Failed to save results: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Perplexity storage error: {str(e)}")
            return False
    
    async def save_individual_content(self, request_id: str, content_list: List[Dict[str, Any]]) -> bool:
        """Save individual content items"""
        try:
            success_count = 0
            
            for i, content in enumerate(content_list):
                key = f"perplexity_content/{request_id}/{i}.json"
                if await self.storage_client.save_json(key, content):
                    success_count += 1
            
            logger.info(f"Saved {success_count}/{len(content_list)} content items")
            return success_count == len(content_list)
            
        except Exception as e:
            logger.error(f"Content storage error: {str(e)}")
            return False
    
    async def load_extraction_results(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Load extraction results from storage"""
        try:
            key = f"perplexity_results/{request_id}.json"
            results = await self.storage_client.load_json(key)
            
            if results:
                logger.info(f"Loaded Perplexity results: {key}")
            else:
                logger.warning(f"No results found: {key}")
            
            return results
            
        except Exception as e:
            logger.error(f"Perplexity load error: {str(e)}")
            return None
    
    async def save_raw_content(self, request_id: str, url: str, raw_content: str) -> bool:
        """Save raw extracted content for debugging"""
        try:
            # Create safe filename from URL
            import hashlib
            url_hash = hashlib.md5(url.encode()).hexdigest()
            key = f"perplexity_raw/{request_id}/{url_hash}.txt"
            
            success = await self.storage_client.save_text(key, raw_content)
            
            if success:
                logger.debug(f"Saved raw content: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Raw content save error: {str(e)}")
            return False
```

## database.py
```python
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
```