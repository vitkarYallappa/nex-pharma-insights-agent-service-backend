#!/usr/bin/env python3
"""
Example: Using Agent 3 Insights with Mock Bedrock

This example demonstrates how to use Agent 3 insights generation
with mock Bedrock data instead of making actual API calls.
"""

import os
import sys
import asyncio

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def example_mock_bedrock_usage():
    """Example of using Agent 3 with mock Bedrock"""
    print("🎭 Agent 3 Mock Bedrock Example")
    print("=" * 50)
    
    # Method 1: Using environment variable
    print("\n📋 Method 1: Environment Variable")
    os.environ["BEDROCK_MOCK_MODE"] = "true"
    
    from app.agent_service_module.agents.agent3_insights.service import Agent3InsightsService
    from app.agent_service_module.agents.agent3_insights.models import Agent3InsightsRequest
    
    service = Agent3InsightsService()
    
    # Sample pharmaceutical content
    content = """
    Semaglutide market analysis for Q3 2024:
    - Market size: $15.2B globally
    - Growth rate: 18% YoY
    - Key players: Novo Nordisk (Ozempic/Wegovy), Eli Lilly (Mounjaro)
    - FDA approvals expanding to new indications
    - Patient access challenges due to pricing
    - Insurance coverage improving but still limited
    - Competition from biosimilars expected by 2026
    """
    
    request = Agent3InsightsRequest(
        request_id="example_001",
        content=content,
        api_provider="aws_bedrock"  # Will use mock due to env var
    )
    
    response = await service.process(request)
    
    print(f"✅ Generated insights using: {response.api_provider}")
    print(f"📊 Market insights: {len(response.insights.market_insights)}")
    print(f"🎯 Key themes: {', '.join(response.insights.key_themes[:3])}...")
    
    # Method 2: Using explicit mock provider
    print("\n📋 Method 2: Explicit Mock Provider")
    
    request2 = Agent3InsightsRequest(
        request_id="example_002", 
        content=content,
        api_provider="aws_bedrock_mock"  # Explicit mock
    )
    
    response2 = await service.process(request2)
    
    print(f"✅ Generated insights using: {response2.api_provider}")
    print(f"📊 Market insights: {len(response2.insights.market_insights)}")
    
    # Method 3: Using S3 processing with mock config
    print("\n📋 Method 3: S3 Processing with Mock Config")
    
    config = {
        "use_mock_bedrock": True,
        "analysis_type": "market_intelligence"
    }
    
    # This would normally process from S3, but we can show the config
    print(f"🔧 Mock config: {config}")
    print("✅ Mock configuration ready for S3 processing")
    
    print("\n🎉 All mock methods demonstrated successfully!")

if __name__ == "__main__":
    asyncio.run(example_mock_bedrock_usage()) 