from typing import Optional, List, Dict, Any
from ...config.service_factory import ServiceFactory
from .models import ExtractedContent
from .db_operations_service import PerplexityDbOperationsService
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityService:
    """Perplexity service for single URL content extraction with centralized storage"""
    
    def __init__(self, prompt_type: str = "default"):
        self.perplexity_client = ServiceFactory.get_perplexity_client()
        self.db_operations = PerplexityDbOperationsService()  # Centralized DB operations
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
        """Store extraction result using centralized DB operations"""
        try:
            # Convert ExtractedContent to dict format
            content_item = {
                "url": str(getattr(content, 'url', 'unknown')),  # Convert URL to string
                "title": getattr(content, 'title', 'Untitled'),
                "content": getattr(content, 'content', ''),
                "word_count": getattr(content, 'word_count', 0),
                "confidence": getattr(content, 'extraction_confidence', 0.8),
                "metadata": getattr(content, 'metadata', {})
            }
            
            # Store using centralized DB operations service
            storage_result = await self.db_operations.store_perplexity_extraction_complete(
                request_id=request_id,
                extracted_content=[content_item],  # Single item in list
                request_details=None  # Will use defaults
            )
            
            logger.info(f"✅ Stored extraction via centralized service: {storage_result.get('database_records', 0)} DB records")
            
        except Exception as e:
            logger.warning(f"Failed to store extraction result: {str(e)}")
            # Don't fail the extraction if storage fails
