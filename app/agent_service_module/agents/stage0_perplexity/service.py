from typing import Optional
from ...config.service_factory import ServiceFactory
from .models import ExtractedContent
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityService:
    """Perplexity service for single URL content extraction"""
    
    def __init__(self, prompt_type: str = "default"):
        self.perplexity_client = ServiceFactory.get_perplexity_client()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
        self.prompt_type = prompt_type
        
        # Set prompt type on client if it supports it
        if hasattr(self.perplexity_client, 'set_prompt_type'):
            self.perplexity_client.set_prompt_type(prompt_type)
    
    def set_prompt_type(self, prompt_type: str):
        """Change prompt type for demos - default, demo, detailed, quick"""
        self.prompt_type = prompt_type
        if hasattr(self.perplexity_client, 'set_prompt_type'):
            self.perplexity_client.set_prompt_type(prompt_type)
        logger.info(f"Service prompt type changed to: {prompt_type}")
    
    async def extract_single_url(self, url: str, request_id: str, prompt_type: Optional[str] = None) -> Optional[ExtractedContent]:
        """Extract content from single URL with optional prompt type override"""
        try:
            # Use override prompt type if provided
            if prompt_type and hasattr(self.perplexity_client, 'set_prompt_type'):
                original_type = self.prompt_type
                self.perplexity_client.set_prompt_type(prompt_type)
                logger.info(f"Using prompt type '{prompt_type}' for URL: {url}")
            
            logger.info(f"Starting extraction for URL: {url}")
            
            # Extract content from single URL
            extracted_content = await self.perplexity_client.extract_single_url(url)
            
            # Restore original prompt type if it was overridden
            if prompt_type and hasattr(self.perplexity_client, 'set_prompt_type'):
                self.perplexity_client.set_prompt_type(original_type)
            
            if extracted_content:
                # Store result
                await self._store_extraction(extracted_content, request_id)
                logger.info(f"Successfully extracted and stored content from {url}")
                return extracted_content
            else:
                logger.warning(f"Failed to extract content from {url}")
                return None
                
        except Exception as e:
            logger.error(f"Single URL extraction error: {str(e)}")
            return None

    async def _store_extraction(self, content: ExtractedContent, request_id: str):
        """Store extraction result"""
        try:
            # Store in database
            await self.database_client.store_extraction_result(content, request_id)
            
            # Store in S3 if needed
            await self.storage_client.store_content(content, request_id)
            
        except Exception as e:
            logger.warning(f"Failed to store extraction result: {str(e)}")
            # Don't fail the extraction if storage fails
