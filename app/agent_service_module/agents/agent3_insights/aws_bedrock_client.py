"""
AWS Bedrock Anthropic Claude Client for Agent 3 - Insights Generation

Clean, minimal implementation for AWS Bedrock with Anthropic Claude integration.
"""

import os
import json
import asyncio
import boto3
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from .prompt_config import InsightPromptConfig, MODEL_CONFIG
    from ...shared.utils.logger import get_logger
except ImportError:
    # For standalone testing
    from prompt_config import InsightPromptConfig, MODEL_CONFIG
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger(__name__)

class AWSBedrockClient:
    """AWS Bedrock Anthropic Claude client for insight generation"""
    
    def __init__(self):
        # AWS credentials from environment or IAM role
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        
        # Initialize Bedrock client
        self.bedrock_client = boto3.client(
            "bedrock-runtime",
            region_name=self.aws_region
        )
        
        self.model_config = MODEL_CONFIG["aws_bedrock"]
        
    async def generate_insights(self, content: str, request_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate insights from content using AWS Bedrock Anthropic Claude"""
        try:
            logger.info(f"Generating insights via AWS Bedrock for request_id: {request_id}")
            
            # Prepare messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": InsightPromptConfig.get_insight_prompt(content, metadata)
                }
            ]
            
            # Make Bedrock API call
            response_data = await self._call_bedrock_api(messages)
            
            # Parse and validate response
            insights = self._parse_insights_response(response_data)
            
            # Add metadata
            result = {
                "request_id": request_id,
                "insights": insights,
                "metadata": {
                    "model": self.model_config["model_id"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_length": len(content),
                    "api_provider": "aws_bedrock",
                    "aws_region": self.aws_region
                }
            }
            
            logger.info(f"Successfully generated insights via AWS Bedrock for request_id: {request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating insights via AWS Bedrock for request_id {request_id}: {str(e)}")
            raise
    
    async def _call_bedrock_api(self, messages: list) -> Dict[str, Any]:
        """Make API call to AWS Bedrock Anthropic Claude"""
        try:
            # Prepare the request body for Anthropic Claude on Bedrock
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.model_config["max_tokens"],
                "temperature": self.model_config["temperature"],
                "system": InsightPromptConfig.get_system_prompt(),
                "messages": messages
            }
            
            # Convert to JSON string
            body_json = json.dumps(body)
            
            # Make the Bedrock API call (synchronous, but we'll run in executor for async)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.bedrock_client.invoke_model(
                    modelId=self.model_config["model_id"],
                    contentType="application/json",
                    accept="application/json",
                    body=body_json
                )
            )
            
            # Parse response
            response_body = response["body"].read()
            response_data = json.loads(response_body)
            
            return response_data
            
        except Exception as e:
            logger.error(f"AWS Bedrock API call failed: {str(e)}")
            raise
    
    def _parse_insights_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate AWS Bedrock Anthropic response"""
        try:
            # Extract content from Bedrock response
            content = response_data.get("content", [])
            if not content or not isinstance(content, list):
                raise ValueError("Invalid Bedrock response format: missing content")
            
            # Get text content
            text_content = ""
            for item in content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")
            
            if not text_content:
                raise ValueError("No text content found in Bedrock response")
            
            # Try to parse JSON from the response
            json_start = text_content.find("{")
            json_end = text_content.rfind("}") + 1
            
            if json_start == -1 or json_end == 0:
                # If no JSON found, create structured response from text
                return self._create_fallback_insights(text_content)
            
            json_str = text_content[json_start:json_end]
            insights = json.loads(json_str)
            
            # Validate required keys
            from .prompt_config import EXPECTED_RESPONSE_KEYS
            for key in EXPECTED_RESPONSE_KEYS:
                if key not in insights:
                    logger.warning(f"Missing expected key in insights: {key}")
                    insights[key] = []
            
            return insights
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response from Bedrock: {e}")
            return self._create_fallback_insights(text_content)
        except Exception as e:
            logger.error(f"Error parsing Bedrock insights response: {e}")
            raise
    
    def _create_fallback_insights(self, text_content: str) -> Dict[str, Any]:
        """Create fallback insights structure when JSON parsing fails"""
        return {
            "market_insights": [
                {
                    "insight": text_content[:500] + "..." if len(text_content) > 500 else text_content,
                    "category": "general",
                    "confidence_score": 0.7,
                    "impact_level": "medium",
                    "time_horizon": "medium_term",
                    "supporting_evidence": ["Raw Bedrock response"]
                }
            ],
            "key_themes": ["Market Analysis", "Content Review"],
            "strategic_recommendations": [
                {
                    "recommendation": "Review and analyze the generated content for actionable insights",
                    "priority": "medium",
                    "rationale": "Bedrock response requires manual review"
                }
            ],
            "risk_factors": [
                {
                    "risk": "Response format parsing issue",
                    "severity": "low",
                    "mitigation": "Manual review of content recommended"
                }
            ]
        }

# Test function for development
async def test_bedrock_client():
    """Test function for development"""
    try:
        client = AWSBedrockClient()
        
        test_content = """
        Recent FDA approval of new obesity medication shows promising market potential.
        Clinical trials demonstrate 15% weight loss efficacy. Market size estimated at $2.4B by 2025.
        Key competitors include Novo Nordisk and Eli Lilly.
        """
        
        result = await client.generate_insights(test_content, "test_request_002")
        print("✅ AWS Bedrock API Test Successful")
        print(json.dumps(result, indent=2))
        return True
        
    except Exception as e:
        print(f"❌ AWS Bedrock API Test Failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bedrock_client()) 