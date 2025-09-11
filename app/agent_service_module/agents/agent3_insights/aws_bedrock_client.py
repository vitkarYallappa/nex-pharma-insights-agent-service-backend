"""
AWS Bedrock Anthropic Claude Client for Agent 3 - Insights Generation

Enhanced implementation for AWS Bedrock with Anthropic Claude integration.
Includes robust error handling, credential management, and response parsing.
"""

import os
import json
import asyncio
import boto3
from typing import Dict, Any, Optional, Union
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError

try:
    from .prompt_config import InsightPromptConfig, MODEL_CONFIG
    from ...shared.utils.logger import get_logger
    from ....config.unified_settings import settings
except ImportError:
    # For standalone testing
    from prompt_config import InsightPromptConfig, MODEL_CONFIG
    import logging


    def get_logger(name):
        return logging.getLogger(name)


    # Mock settings for standalone testing
    class MockSettings:
        AWS_REGION = "us-east-1"
        AWS_ACCESS_KEY_ID = None
        AWS_SECRET_ACCESS_KEY = None


    settings = MockSettings()

logger = get_logger(__name__)


class AWSBedrockClient:
    """Enhanced AWS Bedrock Anthropic Claude client for insight generation"""

    def __init__(self):
        """Initialize AWS Bedrock client with enhanced credential handling"""
        try:
            # Get AWS configuration
            self.aws_region = getattr(settings, 'AWS_REGION', None) or os.getenv("AWS_REGION", "us-east-1")

            # Initialize Bedrock client with proper credential handling
            self._initialize_bedrock_client()

            # Get model configuration
            self.model_config = MODEL_CONFIG["aws_bedrock"]

            # Validate model availability
            self._validate_model_access()

            logger.info(f"AWS Bedrock client initialized successfully in region: {self.aws_region}")

        except Exception as e:
            logger.error(f"Failed to initialize AWS Bedrock client: {str(e)}")
            raise

    def _initialize_bedrock_client(self):
        """Initialize Bedrock client with direct credentials like working test.py"""
        try:
            # Use direct credentials like working test.py
            aws_access_key = os.getenv("BEDROCK_AGENT_AWS_ACCESS_KEY_ID", "****************************")
            aws_secret_key = os.getenv("BEDROCK_AGENT_AWS_SECRET_ACCESS_KEY", "*************************")
            aws_session_token = os.getenv("BEDROCK_AGENT_AWS_SESSION_TOKEN",
                                          "***********************")

            logger.info("Using explicit AWS credentials")

            # Create client directly with credentials like working test.py
            self.bedrock_client = boto3.client(
                "bedrock-agent-runtime",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                aws_session_token=aws_session_token if aws_session_token else None,
                region_name=self.aws_region
            )

        except NoCredentialsError:
            logger.error("No AWS credentials found. Please configure AWS credentials.")
            raise
        except Exception as e:
            logger.error(f"Failed to create Bedrock client: {str(e)}")
            raise

    def _validate_model_access(self):
        """Validate that we can access the specified model"""
        try:
            model_id = self.model_config["model_id"]
            logger.info(f"Validating access to model: {model_id}")

            # Note: We could add a simple test call here if needed
            # For now, we'll validate during the actual API call

        except Exception as e:
            logger.warning(f"Could not validate model access: {str(e)}")

    async def generate_insights(self, content: str, request_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[
        str, Any]:
        """Generate insights from content using AWS Bedrock Anthropic Claude"""
        try:
            logger.info(f"Generating insights via AWS Bedrock for request_id: {request_id}")

            # Validate input
            if not content or not content.strip():
                raise ValueError("Content cannot be empty")

            if len(content) > 100000:  # 100KB limit
                logger.warning(f"Content length ({len(content)}) exceeds recommended limit")
                content = content[:100000] + "... [truncated]"

            # Prepare messages for Claude
            messages = [
                {
                    "role": "user",
                    "content": InsightPromptConfig.get_insight_prompt(content, metadata)
                }
            ]

            # Make Bedrock API call with retry logic
            response_data = await self._call_bedrock_api_with_retry(messages)

            # Parse and validate response
            insights = self._parse_insights_response(response_data)

            # Add comprehensive metadata
            result = {
                "request_id": request_id,
                "insights": insights,
                "metadata": {
                    "model": self.model_config["model_id"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "content_length": len(content),
                    "api_provider": "aws_bedrock",
                    "aws_region": self.aws_region,
                    "processing_time_ms": None,  # Could be calculated if needed
                    "model_config": {
                        "max_tokens": self.model_config["max_tokens"],
                        "temperature": self.model_config["temperature"]
                    }
                }
            }

            logger.info(f"Successfully generated insights via AWS Bedrock for request_id: {request_id}")
            return result

        except Exception as e:
            logger.error(f"Error generating insights via AWS Bedrock for request_id {request_id}: {str(e)}")
            raise

    async def _call_bedrock_api_with_retry(self, messages: list, max_retries: int = 3) -> Dict[str, Any]:
        """Make API call to AWS Bedrock with retry logic"""
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await self._call_bedrock_api(messages)
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', 'Unknown')

                if error_code in ['ThrottlingException', 'ServiceUnavailableException']:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 1.0  # Exponential backoff
                        logger.warning(
                            f"Bedrock API throttled, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                        continue

                logger.error(f"Bedrock API error: {error_code} - {str(e)}")
                last_exception = e
                break
            except Exception as e:
                logger.error(f"Unexpected error in Bedrock API call: {str(e)}")
                last_exception = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(1.0)
                    continue
                break

        if last_exception:
            raise last_exception
        else:
            raise RuntimeError("All retry attempts failed")

    async def _call_bedrock_api(self, messages: list) -> Dict[str, Any]:
        """Make API call to AWS Bedrock Agent (like working test.py)"""
        try:
            # Get the user message content
            user_content = messages[0]["content"] if messages else ""

            # Generate unique session ID
            import uuid
            session_id = f"session-{uuid.uuid4()}"

            # Get agent configuration from settings or environment
            agent_id = getattr(settings, 'AWS_BEDROCK_AGENT_ID', None) or os.getenv("AWS_BEDROCK_AGENT_ID",
                                                                                    "B7TOHQ5N03")
            agent_alias_id = getattr(settings, 'AWS_BEDROCK_AGENT_ALIAS_ID', None) or os.getenv(
                "AWS_BEDROCK_AGENT_ALIAS_ID", "KOINO4TU2J")

            logger.debug(f"Invoking Bedrock agent {agent_id} with session {session_id}")

            # Make the Bedrock Agent API call (synchronous, but we'll run in executor for async)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.bedrock_client.invoke_agent(
                    agentId=agent_id,
                    agentAliasId=agent_alias_id,
                    sessionId=session_id,
                    inputText=user_content
                )
            )

            # Process streaming response like working test.py
            completion = ""
            if 'completion' in response:
                for event in response['completion']:
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'bytes' in chunk:
                            completion += chunk['bytes'].decode('utf-8')

            # Log successful API call
            logger.debug(f"Bedrock Agent API call successful, response size: {len(completion)} characters")

            # Return in expected format
            return {
                "content": [{"type": "text", "text": completion}]
            }

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"AWS Bedrock API call failed: {error_code} - {error_message}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Bedrock response JSON: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Bedrock API call: {str(e)}")
            raise

    def _parse_insights_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate AWS Bedrock Anthropic response with enhanced error handling"""
        try:
            # Extract content from Bedrock response
            content = response_data.get("content", [])
            if not content or not isinstance(content, list):
                raise ValueError("Invalid Bedrock response format: missing or invalid content")

            # Get text content
            text_content = ""
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_content += item.get("text", "")

            if not text_content:
                raise ValueError("No text content found in Bedrock response")

            logger.debug(f"Extracted text content length: {len(text_content)}")

            # Try to parse JSON from the response with multiple strategies
            insights = self._extract_json_from_text(text_content)

            # Validate and enhance the insights structure
            insights = self._validate_and_enhance_insights(insights)

            return insights

        except Exception as e:
            logger.error(f"Error parsing Bedrock insights response: {str(e)}")
            # Return fallback insights instead of raising
            return self._create_fallback_insights(
                text_content if 'text_content' in locals() else "No content available")

    def _extract_json_from_text(self, text_content: str) -> Dict[str, Any]:
        """Extract JSON from text content with multiple parsing strategies"""

        # Strategy 1: Look for JSON block markers
        json_markers = ["```json", "```", "{"]
        for marker in json_markers:
            if marker in text_content:
                if marker == "```json":
                    start = text_content.find("```json") + 7
                    end = text_content.find("```", start)
                    if end != -1:
                        json_str = text_content[start:end].strip()
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            continue
                elif marker == "```":
                    start = text_content.find("```") + 3
                    end = text_content.find("```", start)
                    if end != -1:
                        json_str = text_content[start:end].strip()
                        try:
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            continue

        # Strategy 2: Look for JSON object boundaries
        json_start = text_content.find("{")
        json_end = text_content.rfind("}") + 1

        if json_start != -1 and json_end > json_start:
            json_str = text_content[json_start:json_end]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from boundaries: {str(e)}")

        # Strategy 3: Try to parse the entire content
        try:
            return json.loads(text_content.strip())
        except json.JSONDecodeError:
            pass

        # If all strategies fail, create structured response from text
        logger.warning("Could not extract valid JSON, creating structured response from text")
        raise ValueError("No valid JSON found in response")

    def _validate_and_enhance_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance the insights structure"""
        from .prompt_config import EXPECTED_RESPONSE_KEYS

        # Ensure all expected keys are present
        for key in EXPECTED_RESPONSE_KEYS:
            if key not in insights:
                logger.warning(f"Missing expected key in insights: {key}")
                insights[key] = []

        # Validate structure of each section
        if isinstance(insights.get("market_insights"), list):
            for insight in insights["market_insights"]:
                if isinstance(insight, dict):
                    # Ensure required fields
                    insight.setdefault("confidence_score", 0.7)
                    insight.setdefault("impact_level", "medium")

        if isinstance(insights.get("strategic_recommendations"), list):
            for rec in insights["strategic_recommendations"]:
                if isinstance(rec, dict):
                    rec.setdefault("priority", "medium")

        if isinstance(insights.get("risk_factors"), list):
            for risk in insights["risk_factors"]:
                if isinstance(risk, dict):
                    risk.setdefault("severity", "medium")

        return insights

    def _create_fallback_insights(self, text_content: str) -> Dict[str, Any]:
        """Create enhanced fallback insights structure when JSON parsing fails"""
        # Extract key information from text content
        content_preview = text_content[:500] + "..." if len(text_content) > 500 else text_content

        return {
            "market_insights": [
                {
                    "insight": f"Analysis based on content: {content_preview}",
                    "category": "general_analysis",
                    "confidence_score": 0.6,
                    "impact_level": "medium",
                    "time_horizon": "medium_term",
                    "supporting_evidence": ["Bedrock response content"]
                }
            ],
            "key_themes": self._extract_themes_from_text(text_content),
            "strategic_recommendations": [
                {
                    "recommendation": "Conduct detailed analysis of the generated insights",
                    "priority": "medium",
                    "rationale": "Bedrock response requires structured interpretation",
                    "timeline": "short_term"
                }
            ],
            "risk_factors": [
                {
                    "risk": "Response format parsing limitation",
                    "severity": "low",
                    "mitigation": "Manual review and structured analysis recommended",
                    "probability": "low"
                }
            ]
        }

    def _extract_themes_from_text(self, text_content: str) -> list:
        """Extract key themes from text content"""
        # Simple keyword-based theme extraction
        pharma_keywords = [
            "market", "clinical", "regulatory", "competition", "approval",
            "trial", "drug", "therapy", "patient", "revenue", "growth"
        ]

        themes = []
        text_lower = text_content.lower()

        for keyword in pharma_keywords:
            if keyword in text_lower:
                themes.append(keyword.title())

        return themes[:5] if themes else ["Market Analysis", "Content Review"]


# Enhanced test function
async def test_bedrock_client():
    """Enhanced test function for AWS Bedrock client"""
    try:
        print("🚀 Testing AWS Bedrock Client...")

        client = AWSBedrockClient()

        test_content = """
        Recent FDA approval of new obesity medication shows promising market potential.
        Clinical trials demonstrate 15% weight loss efficacy compared to 5% for existing treatments.
        Market size estimated at $2.4B by 2025, with potential to reach $5B by 2030.
        Key competitors include Novo Nordisk (Wegovy), Eli Lilly (Mounjaro), and emerging biosimilars.
        Regulatory pathway appears favorable with expedited review status.
        Patient access concerns due to high pricing ($1,200/month) and insurance coverage limitations.
        """

        print(f"📄 Test content length: {len(test_content)} characters")

        result = await client.generate_insights(test_content, "test_bedrock_001")

        print("✅ AWS Bedrock API Test Successful!")
        print("\n📊 Generated Insights:")
        print(f"   - Market Insights: {len(result['insights']['market_insights'])} items")
        print(f"   - Key Themes: {len(result['insights']['key_themes'])} items")
        print(f"   - Recommendations: {len(result['insights']['strategic_recommendations'])} items")
        print(f"   - Risk Factors: {len(result['insights']['risk_factors'])} items")

        print(f"\n🔧 Model Used: {result['metadata']['model']}")
        print(f"🌍 AWS Region: {result['metadata']['aws_region']}")

        return True

    except Exception as e:
        print(f"❌ AWS Bedrock API Test Failed: {str(e)}")
        import traceback
        print(f"📋 Error Details:\n{traceback.format_exc()}")
        return False


if __name__ == "__main__":
    asyncio.run(test_bedrock_client())
