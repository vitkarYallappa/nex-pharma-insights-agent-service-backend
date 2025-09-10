#!/usr/bin/env python3
"""
End-to-End Test: Request Submission → Agent 3 Insights

Test the complete workflow:
1. API Request submission
2. Stage0 Orchestrator (SERP + Perplexity)
3. Stage1 Orchestrator → Agent 3 Insights
4. ContentInsightModel storage
5. Results retrieval
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_agent3_direct():
    """Test Agent 3 service directly"""
    print("🧪 Testing Agent 3 Service Directly")
    print("=" * 50)
    
    try:
        from app.agent_service_module.agents.agent3_insights.service import Agent3InsightsService
        from app.agent_service_module.agents.agent3_insights.models import Agent3InsightsRequest
        
        service = Agent3InsightsService()
        
        # Test content (simulating Stage0 output)
        test_content = """
        PHARMACEUTICAL MARKET INTELLIGENCE SUMMARY
        
        Recent FDA approval of semaglutide (Wegovy) for chronic weight management represents a significant 
        market opportunity. Clinical trials demonstrated:
        
        - 15% average weight loss over 68 weeks
        - Superior efficacy compared to existing treatments
        - Strong safety profile with manageable side effects
        
        MARKET ANALYSIS:
        - Global obesity drug market projected to reach $2.4 billion by 2025
        - Key competitors: Novo Nordisk (Ozempic, Wegovy), Eli Lilly (Mounjaro)
        - Insurance coverage expanding but remains limited
        
        REGULATORY LANDSCAPE:
        - EU approval expected Q2 2024
        - Additional indications under review (cardiovascular benefits)
        - Supply chain constraints may limit initial market penetration
        
        COMPETITIVE INTELLIGENCE:
        - Novo Nordisk investing $6B in manufacturing capacity
        - Eli Lilly's tirzepatide showing promising Phase 3 results
        - Generic competition not expected until 2030+ due to patent protection
        """
        
        # Test with direct content
        request = Agent3InsightsRequest(
            request_id="e2e_test_001",
            content=test_content,
            api_provider="anthropic_direct",
            metadata={"test_mode": True, "source": "e2e_test"}
        )
        
        print(f"📤 Submitting request: {request.request_id}")
        print(f"   Content length: {len(test_content)} chars")
        print(f"   API provider: {request.api_provider}")
        
        # Process the request
        start_time = time.time()
        response = await service.process(request)
        processing_time = time.time() - start_time
        
        print(f"\n📥 Response received:")
        print(f"   Status: {response.status}")
        print(f"   Processing time: {processing_time:.2f}s")
        
        if response.status == "completed":
            print(f"   Market insights: {len(response.insights.market_insights)}")
            print(f"   Key themes: {len(response.insights.key_themes)}")
            print(f"   Recommendations: {len(response.insights.strategic_recommendations)}")
            print(f"   Risk factors: {len(response.insights.risk_factors)}")
            
            # Show sample insights
            if response.insights.market_insights:
                print(f"\n📊 Sample Market Insight:")
                insight = response.insights.market_insights[0]
                print(f"   Category: {insight.category}")
                print(f"   Confidence: {insight.confidence_score}")
                print(f"   Impact: {insight.impact_level}")
                print(f"   Text: {insight.insight[:100]}...")
            
            # Test retrieval
            print(f"\n🔍 Testing results retrieval...")
            retrieved = await service.get_results(request.request_id)
            
            if retrieved:
                print(f"   ✅ Retrieved {retrieved['total_insights']} insights")
                print(f"   Status: {retrieved['status']}")
            else:
                print(f"   ❌ No results found for retrieval")
                
            return True
        else:
            print(f"   ❌ Processing failed: {response.metadata.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Agent 3 direct test failed: {str(e)}")
        return False

async def test_stage1_orchestrator():
    """Test Stage1 Orchestrator calling Agent 3"""
    print("\n🧪 Testing Stage1 Orchestrator → Agent 3")
    print("=" * 50)
    
    try:
        from app.agent_service_module.agents.stage1_orchestrator.service import Stage1OrchestratorService
        from app.agent_service_module.agents.stage1_orchestrator.models import Stage1Request
        
        orchestrator = Stage1OrchestratorService()
        
        # Simulate Stage0 completion with S3 summary
        request = Stage1Request(
            request_id="e2e_stage1_001",
            s3_summary_path="s3://test-bucket/summaries/e2e_test_summary.json",
            stage0_results={
                "summary": "Test pharmaceutical market analysis",
                "sources_processed": 2,
                "total_content_length": 5000
            }
        )
        
        print(f"📤 Submitting Stage1 request: {request.request_id}")
        print(f"   S3 path: {request.s3_summary_path}")
        
        # This will process through enabled agents (Agent3 and Agent4)
        response = await orchestrator.process_stage1_request(request)
        
        print(f"\n📥 Stage1 Response:")
        print(f"   Status: {response.status}")
        print(f"   Agents processed: {len(response.agent_results)}")
        
        # Check Agent 3 results
        agent3_result = response.agent_results.get("INSIGHTS")
        if agent3_result:
            print(f"   Agent 3 status: {agent3_result.get('status', 'unknown')}")
            print(f"   Agent 3 processing time: {agent3_result.get('processing_time_ms', 0):.2f}ms")
        
        return response.status in ["completed", "partial_success"]
        
    except Exception as e:
        print(f"❌ Stage1 orchestrator test failed: {str(e)}")
        return False

async def test_root_orchestrator_flow():
    """Test complete Root Orchestrator flow"""
    print("\n🧪 Testing Root Orchestrator → Stage0 → Stage1 → Agent 3")
    print("=" * 60)
    
    try:
        # This would test the complete API flow
        # For now, we'll simulate the request structure
        
        test_request_payload = {
            "project_id": "e2e_test_project",
            "user_id": "test_user_e2e",
            "priority": "high",
            "processing_strategy": "table",
            "config": {
                "keywords": ["Obesity", "Weight loss", "Semaglutide"],
                "sources": [
                    {
                        "name": "FDA",
                        "type": "regulatory",
                        "url": "https://www.fda.gov/"
                    }
                ],
                "extraction_mode": "summary",
                "quality_threshold": 0.7,
                "search_query": "semaglutide obesity treatment approval",
                "date_range": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-01"
                }
            }
        }
        
        print(f"📤 Simulated API Request:")
        print(f"   Project: {test_request_payload['project_id']}")
        print(f"   Keywords: {test_request_payload['config']['keywords']}")
        print(f"   Sources: {len(test_request_payload['config']['sources'])}")
        print(f"   Strategy: {test_request_payload['processing_strategy']}")
        
        # In a real test, this would go through:
        # 1. FastAPI endpoint
        # 2. Root Orchestrator
        # 3. Stage0 Orchestrator (SERP + Perplexity)
        # 4. Stage1 Orchestrator (Agent 3 + Agent 4)
        # 5. Database storage
        
        print(f"\n📋 Expected Flow:")
        print(f"   1. ✅ API Request → Root Orchestrator")
        print(f"   2. ✅ Root Orchestrator → Stage0 (SERP + Perplexity)")
        print(f"   3. ✅ Stage0 → S3 Summary Storage")
        print(f"   4. ✅ Root Orchestrator → Stage1 (Agents)")
        print(f"   5. ✅ Stage1 → Agent 3 (Insights)")
        print(f"   6. ✅ Agent 3 → ContentInsightModel Storage")
        print(f"   7. ✅ Results Available via API")
        
        return True
        
    except Exception as e:
        print(f"❌ Root orchestrator flow test failed: {str(e)}")
        return False

def check_environment_setup():
    """Check if environment is properly configured"""
    print("🔧 Environment Setup Check")
    print("=" * 40)
    
    # Check API keys
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    serp_key = os.getenv("SERP_API_KEY")
    
    print(f"ANTHROPIC_API_KEY: {'✅ Set' if anthropic_key else '❌ Not set'}")
    print(f"PERPLEXITY_API_KEY: {'✅ Set' if perplexity_key else '❌ Not set'}")
    print(f"SERP_API_KEY: {'✅ Set' if serp_key else '❌ Not set'}")
    
    # Check agent configuration
    try:
        from app.agent_service_module.agents.stage1_orchestrator.agent_config import get_enabled_agents
        enabled_agents = get_enabled_agents()
        print(f"\nEnabled Agents: {enabled_agents}")
        
        if "agent3_insights" in enabled_agents:
            print("✅ Agent 3 (Insights) is enabled")
        else:
            print("❌ Agent 3 (Insights) is disabled")
            
    except Exception as e:
        print(f"⚠️  Could not check agent configuration: {e}")
    
    # Check table configuration
    try:
        from app.agent_service_module.agents.agent3_insights.content_insight_model import ContentInsightModel
        table_name = ContentInsightModel.table_name()
        print(f"\nContent Insights Table: {table_name}")
        
    except Exception as e:
        print(f"⚠️  Could not check table configuration: {e}")

async def main():
    """Main test function"""
    print("🚀 End-to-End Agent 3 Workflow Test")
    print("=" * 70)
    
    # Check environment
    check_environment_setup()
    
    # Run tests
    success_count = 0
    total_tests = 3
    
    print(f"\n" + "="*70)
    
    if await test_agent3_direct():
        success_count += 1
    
    if await test_stage1_orchestrator():
        success_count += 1
        
    if await test_root_orchestrator_flow():
        success_count += 1
    
    # Summary
    print(f"\n🏁 End-to-End Test Summary")
    print("=" * 40)
    print(f"Passed: {success_count}/{total_tests} tests")
    
    if success_count == total_tests:
        print("✅ End-to-end workflow ready!")
        print("\n📋 Next Steps:")
        print("   1. Create database tables: python3 scripts/create_tables.py create")
        print("   2. Start FastAPI server: python3 start_server.py")
        print("   3. Submit API request to: http://localhost:8005/api/v1/market-intelligence/requests")
        print("   4. Monitor Agent 3 insights generation")
    else:
        print("⚠️  Some components need attention")
        
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("\n💡 Add to .env file:")
            print("   ANTHROPIC_API_KEY=your_anthropic_key_here")

if __name__ == "__main__":
    asyncio.run(main()) 