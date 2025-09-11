"""
Agent 3 Insights Service - Clean and Production-Ready Implementation

Integrates Anthropic Claude (direct and AWS Bedrock) for insight generation.
Fetches content from S3 and stores results in database.
"""

import json
import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from ...config.service_factory import ServiceFactory
from .models import Agent3InsightsRequest, Agent3InsightsResponse, InsightsData
from .content_insight_model import ContentInsightModel
from .anthropic_direct_client import AnthropicDirectClient
from .aws_bedrock_client import AWSBedrockClient
from ...shared.utils.logger import get_logger
from ...shared.utils.text_processing import parse_s3_uri

logger = get_logger(__name__)

class Agent3InsightsService:
    """
    Agent 3 Insights Service - SIMPLIFIED
    
    Only focuses on:
    1. Reading content from S3/MinIO (extracted by Perplexity)
    2. Generating insights using AI (Claude/Bedrock)
    3. Storing insights in S3/MinIO and simple metadata in database
    """
    
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
            
            # Parse insights data - handle both MVP and legacy formats
            insights_data = self._parse_insights_data(insights_result["insights"])
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Create response with url_id and content_id in metadata
            response_metadata = insights_result.get("metadata", {})
            if request.url_id:
                response_metadata['url_id'] = request.url_id
            if request.content_id:
                response_metadata['content_id'] = request.content_id
            
            response = Agent3InsightsResponse(
                request_id=request.request_id,
                insights=insights_data,
                metadata=response_metadata,
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
            raise
    
    async def _get_content(self, request: Agent3InsightsRequest) -> str:
        """Get content from S3 or direct input"""
        try:
            # If direct content provided, use it
            if request.content:
                logger.info("Using direct content input")
                return request.content
            
            # Otherwise, get from S3 using request_id
            if request.request_id:
                logger.info(f"Fetching content from S3 for request_id: {request.request_id}")
                
                # Try to get Perplexity results first
                content_key = f"perplexity_results/{request.request_id}.json"
                content_bytes = await self.storage_client.get_content(content_key)
                
                if content_bytes:
                    # Parse Perplexity results and extract content
                    perplexity_data = json.loads(content_bytes.decode('utf-8'))
                    
                    if 'items_summary' in perplexity_data:
                        # New format from centralized DB operations
                        combined_content = ""
                        for item in perplexity_data['items_summary']:
                            # Get individual content files
                            for s3_file in item.get('s3_files', []):
                                try:
                                    item_bytes = await self.storage_client.get_content(s3_file)
                                    if item_bytes:
                                        item_data = json.loads(item_bytes.decode('utf-8'))
                                        combined_content += f"\n\n--- {item_data.get('title', 'Content')} ---\n"
                                        combined_content += item_data.get('content', '')
                                except Exception as e:
                                    logger.warning(f"Could not load content from {s3_file}: {e}")
                        
                        if combined_content.strip():
                            return combined_content
                    
                    # Fallback to old format
                    if 'extracted_content' in perplexity_data:
                        combined_content = ""
                        for item in perplexity_data['extracted_content']:
                            if 'content' in item:
                                combined_content += f"\n\n--- {item.get('title', 'Content')} ---\n"
                                combined_content += item['content']
                        return combined_content
                
                # Fallback: try direct content files
                content_pattern = f"perplexity_content/{request.request_id}/"
                logger.warning(f"No summary found, would need to scan {content_pattern}")
                
                raise ValueError(f"No content found for request_id: {request.request_id}")
            
            raise ValueError("No content source provided (neither direct content nor request_id)")
            
        except Exception as e:
            logger.error(f"Error getting content: {str(e)}")
            raise
    
    async def _generate_insights(self, content: str, request: Agent3InsightsRequest) -> Dict[str, Any]:
        """Generate insights using specified API provider"""
        try:
            if request.api_provider == "anthropic_direct":
                if not self.anthropic_client:
                    self.anthropic_client = AnthropicDirectClient()
                return await self.anthropic_client.generate_insights(content, request.request_id)
            
            elif request.api_provider == "aws_bedrock":
                if not self.bedrock_client:
                    self.bedrock_client = AWSBedrockClient()
                return await self.bedrock_client.generate_insights(content, request.request_id)
            
            else:
                raise ValueError(f"Unsupported API provider: {request.api_provider}")
                
        except Exception as e:
            logger.error(f"Error generating insights: {str(e)}")
            raise
    
    def _parse_insights_data(self, insights_raw: Any) -> InsightsData:
        """Parse insights data from AI response"""
        try:
            if isinstance(insights_raw, str):
                # Try to parse as JSON first
                try:
                    insights_dict = json.loads(insights_raw)
                except json.JSONDecodeError:
                    # If not JSON, treat as HTML/text content
                    insights_dict = {"html_content": insights_raw}
            else:
                insights_dict = insights_raw
            
            # Create InsightsData object
            return InsightsData(
                html_content=insights_dict.get("html_content", str(insights_dict)),
                structured_data=insights_dict if isinstance(insights_dict, dict) else {}
            )
            
        except Exception as e:
            logger.error(f"Error parsing insights data: {str(e)}")
            # Fallback to basic structure
            return InsightsData(
                html_content=str(insights_raw),
                structured_data={}
            )
    
    async def _store_results(self, response: Agent3InsightsResponse):
        """Store insights results in content_insight table with url_id and content_id"""
        try:
            # Step 1: Store insights in S3/MinIO
            insights_key = f"insights_results/{response.request_id}.json"
            insights_data = {
                "request_id": response.request_id,
                "insights": response.insights.model_dump(),
                "metadata": response.metadata,
                "status": response.status,
                "content_length": response.content_length,
                "processing_time_ms": response.processing_time_ms,
                "api_provider": response.api_provider,
                "model_used": response.model_used,
                "created_at": datetime.utcnow().isoformat()
            }
            
            insights_json = json.dumps(insights_data, indent=2)
            success = await self.storage_client.upload_content(
                insights_json.encode('utf-8'),
                insights_key,
                'application/json'
            )
            
            if not success:
                raise Exception(f"Failed to store insights at {insights_key}")
            
            # Step 2: Store in content_insight table with proper structure
            # Extract url_id and content_id from metadata or response
            url_id = response.metadata.get('url_id', 'unknown')
            content_id = response.metadata.get('content_id', 'unknown')
            
            # Create ContentInsightModel instance
            content_insight = ContentInsightModel.create_new(
                url_id=url_id,
                content_id=content_id,
                insight_text=response.insights.html_content if response.insights.html_content else "Generated insights",
                insight_content_file_path=insights_key,
                insight_category="ai_generated",
                confidence_score=0.85,  # Default confidence score
                version=1,
                is_canonical=True,
                preferred_choice=True,
                created_by=f"{response.api_provider}-{response.model_used}"
            )
            
            # Convert to DynamoDB item format (handles Decimal conversion)
            item = content_insight.to_dict()
            
            # Store in content_insight table
            await self.database_client.put_item(
                table_name=self.table_name,
                item=item
            )
            
            logger.info(f"💾 Stored insights in content_insight table: {content_insight.pk}")
            logger.info(f"💾 S3 storage key: {insights_key}")
            logger.info(f"💾 URL ID: {url_id}, Content ID: {content_id}")
            
        except Exception as e:
            logger.error(f"Error storing insights: {str(e)}")
            # Don't raise - storage failure shouldn't fail the entire process
