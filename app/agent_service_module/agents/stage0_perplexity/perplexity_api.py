import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
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
