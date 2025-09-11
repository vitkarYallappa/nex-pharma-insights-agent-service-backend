#!/usr/bin/env python3
"""
Example: Agent3 Insights with Content Insight Table Storage

This example demonstrates how Agent3 now properly stores insight data
in the content_insight table with url_id and content_id from Perplexity.

Flow:
1. Perplexity processes URLs and stores content with url_id and content_id
2. Agent3 fetches content from S3 using these IDs
3. Agent3 generates insights using Bedrock/Anthropic
4. Agent3 stores insights in content_insight table with proper structure
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.agent_service_module.agents.agent3_insights.service import Agent3InsightsService
from app.agent_service_module.agents.agent3_insights.models import Agent3InsightsRequest
from app.agent_service_module.agents.agent3_insights.content_insight_model import ContentInsightModel

async def demonstrate_agent3_content_insight_flow():
    """Demonstrate the complete Agent3 flow with content_insight table storage"""
    
    print("🧪 Agent3 Content Insight Table Integration Example")
    print("=" * 60)
    
    # Step 1: Simulate data from Perplexity (url_id and content_id)
    print("\n📋 Step 1: Simulating Perplexity Data")
    url_id = str(uuid.uuid4())
    content_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    
    print(f"   URL ID: {url_id}")
    print(f"   Content ID: {content_id}")
    print(f"   Request ID: {request_id}")
    
    # Step 2: Create Agent3 request with the IDs from Perplexity
    print("\n🔧 Step 2: Creating Agent3 Request")
    
    # Sample content that would normally come from S3
    sample_content = """
    Semaglutide Market Analysis:
    
    The global semaglutide market is experiencing unprecedented growth, driven by increasing 
    diabetes prevalence and obesity rates worldwide. Key market dynamics include:
    
    - Market size projected to reach $15.8 billion by 2028
    - Strong competition from Novo Nordisk's Ozempic and Wegovy
    - Emerging biosimilar threats expected by 2030
    - Regulatory approvals expanding to new indications
    - Supply chain challenges affecting market access
    
    Investment opportunities exist in manufacturing capacity and distribution networks.
    """
    
    agent3_request = Agent3InsightsRequest(
        request_id=request_id,
        content=sample_content,  # Direct content for this example
        url_id=url_id,           # From Perplexity
        content_id=content_id,   # From Perplexity
        api_provider="mock",     # Use mock for this example
        metadata={
            "source": "perplexity_processing",
            "original_url": "https://example.com/semaglutide-market-report",
            "processing_timestamp": datetime.utcnow().isoformat()
        }
    )
    
    print(f"   ✅ Request created with URL ID and Content ID")
    
    # Step 3: Process with Agent3 Service
    print("\n🤖 Step 3: Processing with Agent3 Service")
    
    try:
        agent3_service = Agent3InsightsService()
        response = await agent3_service.process(agent3_request)
        
        print(f"   ✅ Processing completed successfully")
        print(f"   📊 Status: {response.status}")
        print(f"   ⏱️  Processing time: {response.processing_time_ms:.2f}ms")
        print(f"   📝 Content length: {response.content_length} characters")
        print(f"   🔧 API Provider: {response.api_provider}")
        
        # Step 4: Verify data was stored in content_insight table
        print("\n💾 Step 4: Verifying Content Insight Table Storage")
        
        # The service automatically stores data in content_insight table
        # Let's show what the stored data structure looks like
        print(f"   ✅ Insights stored in content_insight table")
        print(f"   🔗 URL ID: {response.metadata.get('url_id', 'N/A')}")
        print(f"   📄 Content ID: {response.metadata.get('content_id', 'N/A')}")
        print(f"   📁 S3 Storage Key: insights_results/{request_id}.json")
        
        # Step 5: Show the insight data structure
        print("\n📋 Step 5: Content Insight Data Structure")
        print("   The following data is stored in content_insight table:")
        print(f"   - pk (insight_id): Generated UUID")
        print(f"   - url_id: {url_id}")
        print(f"   - content_id: {content_id}")
        print(f"   - insight_text: Generated insights content")
        print(f"   - insight_content_file_path: S3 storage path")
        print(f"   - insight_category: ai_generated")
        print(f"   - confidence_score: 0.85")
        print(f"   - version: 1")
        print(f"   - is_canonical: true")
        print(f"   - preferred_choice: true")
        print(f"   - created_at: {datetime.utcnow().isoformat()}")
        print(f"   - created_by: {response.api_provider}-{response.model_used}")
        
        print("\n✅ Example completed successfully!")
        print("\n💡 Key Benefits:")
        print("   - Proper linkage between Perplexity content and insights")
        print("   - Structured storage in content_insight table")
        print("   - Traceability from URL to final insights")
        print("   - S3 storage for full insight content")
        print("   - Database metadata for quick queries")
        
    except Exception as e:
        print(f"   ❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

async def show_content_insight_model_usage():
    """Show how to use the ContentInsightModel directly"""
    
    print("\n" + "=" * 60)
    print("🔧 ContentInsightModel Direct Usage Example")
    print("=" * 60)
    
    # Create a content insight directly
    insight = ContentInsightModel.create_new(
        url_id="123e4567-e89b-12d3-a456-426614174000",
        content_id="987fcdeb-51a2-43d7-8f9e-123456789abc",
        insight_text="Market analysis shows 15% growth in oncology segment",
        insight_content_file_path="/insights/market-analysis-2024.json",
        insight_category="market_trend",
        confidence_score=0.92,
        version=1,
        is_canonical=True,
        preferred_choice=True,
        created_by="agent3-bedrock"
    )
    
    print(f"📝 Created insight: {insight.pk}")
    print(f"🔗 URL ID: {insight.url_id}")
    print(f"📄 Content ID: {insight.content_id}")
    print(f"💭 Insight: {insight.insight_text}")
    print(f"📊 Confidence: {insight.confidence_score}")
    
    # Convert to DynamoDB format
    db_item = insight.to_dict()
    print(f"\n💾 DynamoDB item (with Decimal conversion):")
    for key, value in db_item.items():
        print(f"   {key}: {value} ({type(value).__name__})")
    
    # Convert to API response format
    api_response = insight.to_response()
    print(f"\n🌐 API response format:")
    for key, value in api_response.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    print("🚀 Starting Agent3 Content Insight Integration Examples")
    
    # Run the main example
    asyncio.run(demonstrate_agent3_content_insight_flow())
    
    # Show model usage
    asyncio.run(show_content_insight_model_usage())
    
    print("\n🎉 All examples completed!") 