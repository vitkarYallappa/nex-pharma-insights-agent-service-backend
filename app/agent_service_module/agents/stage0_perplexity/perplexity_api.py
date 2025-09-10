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
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "sonar-pro",
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
                "return_citations": True
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                return self._parse_response(data, url)
                
        except Exception as e:
            logger.error(f"URL extraction failed for {url}: {str(e)}")
            return None
    
    def _parse_response(self, data: Dict[str, Any], url: str) -> Optional[ExtractedContent]:
        """Parse Perplexity API response"""
        try:
            choices = data.get("choices", [])
            if not choices:
                return None
            
            message = choices[0].get("message", {})
            content = message.get("content", "")
            
            if not content:
                return None
            
            # Extract metadata
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
                    "extraction_method": "perplexity_api",
                    "prompt_type": self.prompt_type
                },
                word_count=len(summary.split()),
                extraction_confidence=self._calculate_confidence(summary, citations)
            )
            
        except Exception as e:
            logger.error(f"Response parsing error: {str(e)}")
            return None
    
    def _clean_title(self, title: str) -> str:
        """Clean extracted title"""
        prefixes = ["Title:", "# ", "## "]
        for prefix in prefixes:
            if title.startswith(prefix):
                title = title[len(prefix):].strip()
        
        return title[:200]
    
    def _calculate_confidence(self, content: str, citations: list) -> float:
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
