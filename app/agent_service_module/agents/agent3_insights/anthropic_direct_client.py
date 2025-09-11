"""
Direct Anthropic Claude API Client for Agent 3 - Insights Generation

Clean, minimal implementation for direct Anthropic API integration.
"""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from .prompt_config import InsightPromptConfig, MODEL_CONFIG
    from ...shared.utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    # For standalone testing
    from prompt_config import InsightPromptConfig, MODEL_CONFIG
    import logging
    def get_logger(name):
        return logging.getLogger(name)
    logger = logging.getLogger(__name__)

class AnthropicDirectClient:
    """Direct Anthropic Claude API client for insight generation"""
    
    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.base_url = "https://api.anthropic.com/v1"
        self.model_config = MODEL_CONFIG["anthropic_direct"]
        
    async def generate_insights(self, content: str, request_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate insights from content using direct Anthropic API"""
        try:
            logger.info(f"Generating insights for request_id: {request_id}")
            
            # Prepare messages
            messages = [
                {
                    "role": "user",
                    "content": InsightPromptConfig.get_insight_prompt(content, metadata)
                }
            ]
            
            # Make API call
            response_data = await self._call_anthropic_api(messages)
            
            # Parse and validate response
            insights = self._parse_insights_response(response_data)
            
            # Add metadata
            result = {
                "request_id": request_id,
                "insights": insights,
                "metadata": {
                    "model": self.model_config["model"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_length": len(content),
                    "api_provider": "anthropic_direct"
                }
            }
            
            logger.info(f"Successfully generated insights for request_id: {request_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating insights for request_id {request_id}: {str(e)}")
            raise
    
    async def _call_anthropic_api(self, messages: list) -> Dict[str, Any]:
        """Make API call to Anthropic Claude"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model_config["model"],
            "max_tokens": self.model_config["max_tokens"],
            "temperature": self.model_config["temperature"],
            "system": InsightPromptConfig.get_system_prompt(),
            "messages": messages
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error {response.status}: {error_text}")
                
                return await response.json()
    
    def _parse_insights_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate Anthropic API response"""
        try:
            # Extract content from response
            content = response_data.get("content", [])
            if not content or not isinstance(content, list):
                raise ValueError("Invalid response format: missing content")
            
            # Get text content
            text_content = ""
            for item in content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")
            
            if not text_content:
                raise ValueError("No text content found in response")
            
            # Try to parse JSON from the response
            # Look for JSON block in the response
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
            logger.warning(f"Failed to parse JSON response: {e}")
            return self._create_fallback_insights(text_content)
        except Exception as e:
            logger.error(f"Error parsing insights response: {e}")
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
                    "supporting_evidence": ["Raw API response"]
                }
            ],
            "key_themes": ["Market Analysis", "Content Review"],
            "strategic_recommendations": [
                {
                    "recommendation": "Review and analyze the generated content for actionable insights",
                    "priority": "medium",
                    "rationale": "API response requires manual review"
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
async def test_anthropic_client():
    """Test function for development"""
    try:
        client = AnthropicDirectClient()
        
        test_content = """
        Recent FDA approval of new obesity medication shows promising market potential.
        Clinical trials demonstrate 15% weight loss efficacy. Market size estimated at $2.4B by 2025.
        Key competitors include Novo Nordisk and Eli Lilly.
        """
        
        result = await client.generate_insights(test_content, "test_request_001")
        print("✅ Anthropic Direct API Test Successful")
        print(json.dumps(result, indent=2))
        return True
        
    except Exception as e:
        print(f"❌ Anthropic Direct API Test Failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_anthropic_client()) 