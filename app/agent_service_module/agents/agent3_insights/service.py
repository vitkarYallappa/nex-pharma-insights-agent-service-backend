"""
Agent 3 Insights Service - Clean and Production-Ready Implementation

Integrates Anthropic Claude (direct and AWS Bedrock) for insight generation.
Fetches content from S3 and stores results in database.
"""

import json
import time
import uuid
from typing import Dict, Any, Optional, List

from ...config.service_factory import ServiceFactory
from .models import Agent3InsightsRequest, Agent3InsightsResponse, InsightsData
from .content_insight_model import ContentInsightModel
from .anthropic_direct_client import AnthropicDirectClient
from .aws_bedrock_client import AWSBedrockClient
from ...shared.utils.logger import get_logger
from ...shared.utils.text_processing import parse_s3_uri

logger = get_logger(__name__)

class Agent3InsightsService:
    """Main service for Agent 3 insights generation"""
    
    def __init__(self):
        # Get clients from factory
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
        
        # Table name from ContentInsightModel
        self.table_name = ContentInsightModel.table_name()
        
        # Initialize API clients
        self.anthropic_client = None
        self.bedrock_client = None
        
    async def process(self, request: Agent3InsightsRequest) -> Agent3InsightsResponse:
        """Process insights generation request"""
        start_time = time.time()
        
        try:
            logger.info(f"Starting insights processing for request_id: {request.request_id}")
            
            # Get content (from S3 or direct)
            content = await self._get_content(request)
            if not content:
                raise ValueError("No content available for processing")
            
            # Generate insights using specified API provider
            insights_result = await self._generate_insights(content, request)
            
            # Parse insights data
            insights_data = self._parse_insights_data(insights_result["insights"])
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Create response
            response = Agent3InsightsResponse(
                request_id=request.request_id,
                insights=insights_data,
                metadata=insights_result.get("metadata", {}),
                status="completed",
                content_length=len(content),
                processing_time_ms=processing_time_ms,
                api_provider=request.api_provider,
                model_used=insights_result.get("metadata", {}).get("model", "unknown")
            )
            
            # Store in database
            await self._store_results(response)
            
            logger.info(f"Successfully completed insights processing for request_id: {request.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing insights for request_id {request.request_id}: {str(e)}")
            
            # Return error response
            processing_time_ms = (time.time() - start_time) * 1000
            return Agent3InsightsResponse(
                request_id=request.request_id,
                insights=InsightsData(),
                metadata={"error": str(e)},
                status="failed",
                processing_time_ms=processing_time_ms,
                api_provider=request.api_provider
            )
    
    async def process_from_s3(self, request_id: str, s3_path: str, output_table: str, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process insights from S3 content path - expected by Stage1 orchestrator
        
        Args:
            request_id: The request identifier
            s3_path: S3 path containing content to process
            output_table: DynamoDB table name for storing results
            config: Optional processing configuration
            
        Returns:
            Dict containing processing results
        """
        try:
            logger.info(f"Processing insights from S3 for request_id: {request_id}")
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
                    "request_id": request_id,
                    "status": "failed",
                    "error": "No content available for processing",
                    "insights": {}
                }
            
            # Create request object for processing
            insights_request = Agent3InsightsRequest(
                request_id=request_id,
                content=combined_content,
                metadata=config or {},
                api_provider="anthropic_direct"  # Default provider
            )
            
            # Process insights
            response = await self.process(insights_request)
            
            # Return results in expected format
            return {
                "success": True,
                "request_id": request_id,
                "status": response.status,
                "insights": response.insights.dict() if response.insights else {},
                "metadata": response.metadata,
                "processing_time_ms": response.processing_time_ms,
                "api_provider": response.api_provider,
                "content_length": len(combined_content),
                "output_table": output_table
            }
            
        except Exception as e:
            logger.error(f"Error processing insights from S3 for request_id {request_id}: {str(e)}")
            return {
                "success": False,
                "request_id": request_id,
                "status": "failed",
                "error": str(e),
                "insights": {},
                "output_table": output_table
            }
    
    async def _get_content(self, request: Agent3InsightsRequest) -> str:
        """Get content from S3 or direct input"""
        try:
            if request.s3_summary_path:
                logger.info(f"Fetching content from S3: {request.s3_summary_path}")
                content = await self.storage_client.download_file_content(request.s3_summary_path)
                return content
            elif request.content:
                logger.info("Using direct content input")
                return request.content
            else:
                raise ValueError("No content source specified (s3_summary_path or content)")
                
        except Exception as e:
            logger.error(f"Error fetching content: {str(e)}")
            raise
    
    async def _generate_insights(self, content: str, request: Agent3InsightsRequest) -> Dict[str, Any]:
        """Generate insights using specified API provider"""
        try:
            if request.api_provider == "anthropic_direct":
                if not self.anthropic_client:
                    self.anthropic_client = AnthropicDirectClient()
                return await self.anthropic_client.generate_insights(
                    content, request.request_id, request.metadata
                )
            
            elif request.api_provider == "aws_bedrock":
                if not self.bedrock_client:
                    self.bedrock_client = AWSBedrockClient()
                return await self.bedrock_client.generate_insights(
                    content, request.request_id, request.metadata
                )
            
            else:
                raise ValueError(f"Unsupported API provider: {request.api_provider}")
                
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            raise
    
    def _parse_insights_data(self, insights_dict: Dict[str, Any]) -> InsightsData:
        """Parse insights dictionary into structured data model"""
        try:
            # Convert dictionary to InsightsData model
            # This will validate the structure and provide defaults
            return InsightsData(**insights_dict)
            
        except Exception as e:
            logger.warning(f"Error parsing insights data: {str(e)}")
            # Return empty insights data if parsing fails
            return InsightsData()
    
    async def _store_results(self, response: Agent3InsightsResponse):
        """Store results in database using ContentInsightModel"""
        try:
            # Convert insights to individual content insight records
            for i, market_insight in enumerate(response.insights.market_insights):
                # Create ContentInsightModel instance
                content_insight = ContentInsightModel.create_new(
                    url_id=response.request_id,  # Using request_id as url_id reference
                    content_id=f"{response.request_id}_content_{i}",
                    insight_text=market_insight.insight,
                    insight_content_file_path=f"insights/{response.request_id}/insight_{i}.json",
                    insight_category=market_insight.category.value if hasattr(market_insight.category, 'value') else str(market_insight.category),
                    confidence_score=market_insight.confidence_score,
                    version=1,
                    is_canonical=True,
                    preferred_choice=market_insight.impact_level.value == "high" if hasattr(market_insight.impact_level, 'value') else market_insight.impact_level == "high",
                    created_by=response.api_provider or "agent3_insights"
                )
                
                # Store in database
                await self.database_client.put_item(
                    table_name=self.table_name,
                    item=content_insight.to_dict()
                )
            
            # Store summary metadata as a separate record
            summary_insight = ContentInsightModel.create_new(
                url_id=response.request_id,
                content_id=f"{response.request_id}_summary",
                insight_text=f"Generated {len(response.insights.market_insights)} insights with {len(response.insights.key_themes)} key themes",
                insight_content_file_path=f"insights/{response.request_id}/summary.json",
                insight_category="summary",
                confidence_score=0.9,
                version=1,
                is_canonical=True,
                preferred_choice=True,
                created_by=response.api_provider or "agent3_insights"
            )
            
            await self.database_client.put_item(
                table_name=self.table_name,
                item=summary_insight.to_dict()
            )
            
            logger.info(f"Stored {len(response.insights.market_insights) + 1} insight records for request_id: {response.request_id}")
            
        except Exception as e:
            logger.error(f"Error storing results: {str(e)}")
            # Don't raise - storage failure shouldn't fail the entire process
    
    async def get_results(self, request_id: str) -> Optional[List[Dict[str, Any]]]:
        """Retrieve results for a request ID using ContentInsightModel"""
        try:
            # Since we don't have GSI, we'll use scan with filter (for simple cases)
            # In production, you might want to store a mapping or use a different approach
            response = await self.database_client.scan(
                table_name=self.table_name,
                FilterExpression="url_id = :url_id",
                ExpressionAttributeValues={":url_id": request_id}
            )
            
            # Return the raw items from DynamoDB scan
            return response if response else []
            
        except Exception as e:
            logger.error(f"Error retrieving results for request_id {request_id}: {str(e)}")
            return None
