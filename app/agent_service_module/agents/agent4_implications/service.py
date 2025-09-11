import json
from typing import Dict, Any, Optional
from ...config.service_factory import ServiceFactory
from .models import Agent4ImplicationsRequest, Agent4ImplicationsResponse
from ...shared.utils.logger import get_logger
from ...shared.utils.text_processing import parse_s3_uri

logger = get_logger(__name__)

class Agent4ImplicationsService:
    """Main service for agent4_implications."""
    
    def __init__(self):
        # Factory automatically provides correct implementation based on environment
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process(self, request: Agent4ImplicationsRequest) -> Agent4ImplicationsResponse:
        """Process the agent4_implications request."""
        # Implementation will be added based on specific agent requirements
        result = {"message": "Processing agent4_implications request", "request_id": request.request_id}
        
        return Agent4ImplicationsResponse(
            request_id=request.request_id,
            result=result,
            status="completed"
        )
    
    async def process_from_s3(self, request_id: str, s3_path: str, output_table: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process implications from S3 content path - expected by Stage1 orchestrator
        
        Args:
            request_id: The request identifier
            s3_path: S3 path containing content to process
            output_table: DynamoDB table name for storing results
            config: Optional processing configuration
            
        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"Processing implications from S3 for request_id: {request_id}")
            logger.info(f"S3 path to process: {s3_path}")
            logger.info(f"Output table: {output_table}")
            
            # Get content from S3 path
            combined_content = ""
            try:
                # Parse S3 URI to extract object key
                object_key = parse_s3_uri(s3_path)
                logger.info(f"Parsed S3 object key: {object_key}")
                content_bytes = await self.storage_client.get_content(object_key)
                if content_bytes:
                    content_str = content_bytes.decode('utf-8')
                    # Try to parse as JSON first
                    try:
                        content_data = json.loads(content_str)
                        # Extract summary or content field
                        if isinstance(content_data, dict):
                            combined_content = content_data.get('summary', content_data.get('content', str(content_data)))
                        else:
                            combined_content = str(content_data)
                    except json.JSONDecodeError:
                        # Use as plain text
                        combined_content = content_str
                    
                    logger.info(f"Loaded content from {s3_path}: {len(combined_content)} chars")
                else:
                    logger.warning(f"No content found at {s3_path}")
            except Exception as e:
                logger.error(f"Failed to read content from {s3_path}: {e}")
            
            if not combined_content.strip():
                logger.warning(f"No content available for processing request_id: {request_id}")
                return {
                    "success": False,
                    "request_id": request_id,
                    "status": "failed",
                    "error": "No content available for processing",
                    "implications": {},
                    "output_table": output_table
                }
            
            # Create request object for processing
            implications_request = Agent4ImplicationsRequest(
                request_id=request_id,
                content=combined_content,
                metadata=config or {}
            )
            
            # Process implications
            response = await self.process(implications_request)
            
            # Return results in expected format
            return {
                "success": True,
                "request_id": request_id,
                "status": response.status,
                "implications": response.result,
                "content_length": len(combined_content),
                "output_table": output_table
            }
            
        except Exception as e:
            logger.error(f"Error processing implications from S3 for request_id {request_id}: {str(e)}")
            return {
                "success": False,
                "request_id": request_id,
                "status": "failed",
                "error": str(e),
                "implications": {},
                "output_table": output_table
            }
