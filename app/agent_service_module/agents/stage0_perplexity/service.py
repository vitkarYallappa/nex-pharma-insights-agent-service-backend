from typing import List, Optional
from ...config.service_factory import ServiceFactory
from .models import ContentExtractionRequest, PerplexityResponse, Stage0PerplexityRequest, Stage0PerplexityResponse
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


class Stage0PerplexityService:
    """Legacy service for backward compatibility"""
    
    def __init__(self):
        self.perplexity_service = PerplexityService()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process(self, request: Stage0PerplexityRequest) -> Stage0PerplexityResponse:
        """Process the stage0_perplexity request - legacy compatibility method"""
        try:
            # For backward compatibility, we'll use the new service internally
            # but maintain the old interface
            result = {
                "message": "Processing stage0_perplexity request", 
                "request_id": request.request_id,
                "content_processed": len(request.content),
                "timestamp": request.timestamp.isoformat()
            }
            
            logger.info(f"Legacy perplexity processing for request: {request.request_id}")
            
            return Stage0PerplexityResponse(
                request_id=request.request_id,
                result=result,
                status="completed"
            )
            
        except Exception as e:
            logger.error(f"Legacy perplexity processing error: {str(e)}")
            return Stage0PerplexityResponse(
                request_id=request.request_id,
                result={"error": str(e)},
                status="failed"
            )
