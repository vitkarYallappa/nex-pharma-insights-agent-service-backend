import aiohttp
from typing import Dict, Any, Optional
from .models import ExtractedContent
from .prompt_config import PromptManager
from ...config.settings import settings
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityAPI:
    """Perplexity API client for single URL content extraction"""
    
    def __init__(self, prompt_type: str = "default"):
        self.api_key = settings.PERPLEXITY_API_KEY
        self.base_url = "https://api.perplexity.ai"
        self.session = None
        self.prompt_type = prompt_type
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for content extraction - easy to update for demos"""
        return PromptManager.get_system_prompt(self.prompt_type)
    
    def _get_user_prompt(self, url: str) -> str:
        """Get user prompt for specific URL - easy to customize for different needs"""
        return PromptManager.format_user_prompt(url, self.prompt_type)
    
    def set_prompt_type(self, prompt_type: str):
        """Change prompt type for demos - default, demo, detailed, quick"""
        self.prompt_type = prompt_type
        logger.info(f"Prompt type changed to: {prompt_type}")
    
    async def extract_single_url(self, url: str) -> Optional[ExtractedContent]:
        """Extract content from single URL"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            logger.info(f"Extracting content from URL: {url} (prompt_type: {self.prompt_type})")
            
            # Correct headers for Perplexity API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Correct payload structure for Perplexity API
            payload = {
                "model": "sonar-pro",  # Using sonar-pro for better content extraction
                "messages": [
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": self._get_user_prompt(url)
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.2,
                "return_citations": True,
                "return_images": False,
                "search_domain_filter": [url],  # Focus search on the specific URL
                "search_recency_filter": "month"
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)  # Increased timeout for Perplexity
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                return self._parse_response(data, url)
                
        except aiohttp.ClientTimeout:
            logger.error(f"Timeout error for URL {url}")
            return None
        except aiohttp.ClientResponseError as e:
            logger.error(f"HTTP error for URL {url}: {e.status} - {e.message}")
            return None
        except Exception as e:
            logger.error(f"URL extraction failed for {url}: {str(e)}")
            return None
    
    def _parse_response(self, data: Dict[str, Any], url: str) -> Optional[ExtractedContent]:
        """Parse Perplexity API response"""
        try:
            # Check for choices in response
            choices = data.get("choices", [])
            if not choices:
                logger.warning(f"No choices in response for URL: {url}")
                return None
            
            # Extract message content
            choice = choices[0]
            message = choice.get("message", {})
            content = message.get("content", "")
            
            if not content:
                logger.warning(f"No content in response for URL: {url}")
                return None
            
            # Extract metadata from response
            citations = data.get("citations", [])
            usage = data.get("usage", {})
            finish_reason = choice.get("finish_reason", "")
            
            # Parse content for title and summary
            lines = content.split('\n')
            title = lines[0] if lines else "Untitled"
            summary = '\n'.join(lines[1:]) if len(lines) > 1 else content
            
            # Calculate confidence based on response quality
            confidence = self._calculate_confidence(summary, citations, finish_reason)
            
            return ExtractedContent(
                url=url,
                title=self._clean_title(title),
                content=summary,
                metadata={
                    "citations": citations,
                    "usage": usage,
                    "finish_reason": finish_reason,
                    "extraction_method": "perplexity_api",
                    "prompt_type": self.prompt_type,
                    "model": "sonar-pro"
                },
                word_count=len(summary.split()),
                extraction_confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Response parsing error for URL {url}: {str(e)}")
            return None
    
    def _clean_title(self, title: str) -> str:
        """Clean extracted title"""
        # Remove common prefixes
        prefixes = ["Title:", "# ", "## ", "### ", "**", "*"]
        for prefix in prefixes:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
        
        # Remove markdown formatting
        title = title.replace("**", "").replace("*", "")
        
        # Limit length and clean
        return title[:200].strip()
    
    def _calculate_confidence(self, content: str, citations: list, finish_reason: str) -> float:
        """Calculate extraction confidence score"""
        base_score = 0.3
        
        # Content length factor
        content_length = len(content)
        if content_length > 1000:
            base_score += 0.3
        elif content_length > 500:
            base_score += 0.2
        elif content_length > 200:
            base_score += 0.1
        
        # Citations factor (Perplexity provides citations)
        if citations:
            citation_score = min(len(citations) * 0.1, 0.3)
            base_score += citation_score
        
        # Finish reason factor
        if finish_reason == "stop":
            base_score += 0.1
        elif finish_reason == "length":
            base_score += 0.05  # Partial content due to length limit
        
        # Content quality indicators
        if any(indicator in content.lower() for indicator in ["summary", "abstract", "overview", "introduction"]):
            base_score += 0.1
        
        return min(base_score, 1.0)
