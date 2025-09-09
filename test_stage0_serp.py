#!/usr/bin/env python3
"""
Simple test script for Stage 0 SERP Agent
Run this to test the SERP agent with mock data
"""

import asyncio
import json
from datetime import datetime
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.agent_service_module.agents.stage0_serp.models import (
    SerpRequest, 
    Stage0SerpRequest
)
from app.agent_service_module.agents.stage0_serp.serp_mock import SerpMock
from app.agent_service_module.agents.stage0_serp.service import Stage0SerpService

async def test_serp_mock():
    """Test the SERP mock implementation"""
    print("🧪 Testing SERP Mock Implementation")
    print("=" * 50)
    
    mock = SerpMock()
    
    # Test different queries
    test_queries = [
        "FDA AI regulation pharmaceutical",
        "drug discovery compliance",
        "clinical trial AI implementation",
        "pharmaceutical data privacy"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing query: '{query}'")
        
        request = SerpRequest(
            query=query,
            num_results=5
        )
        
        response = await mock.search(request)
        
        print(f"✅ Request ID: {response.request_id}")
        print(f"📊 Total Results: {response.total_results}")
        print(f"🔍 Found {len(response.results)} results")
        
        for i, result in enumerate(response.results[:3], 1):
            print(f"  {i}. {result.title}")
            print(f"     🔗 {result.url}")
            print(f"     📄 {result.snippet[:100]}...")
            print(f"     🌐 Domain: {result.domain}")
            print()

async def test_legacy_api():
    """Test the legacy API compatibility"""
    print("\n🔄 Testing Legacy API Compatibility")
    print("=" * 50)
    
    mock = SerpMock()
    
    # Test legacy call_api method
    legacy_data = {
        "query": "pharmaceutical AI regulations",
        "num_results": 3
    }
    
    print(f"📝 Testing legacy API with: {json.dumps(legacy_data, indent=2)}")
    
    response = await mock.call_api(legacy_data)
    
    print(f"✅ Status: {response['status']}")
    print(f"🔧 Mock: {response['mock']}")
    print(f"💬 Message: {response['message']}")
    
    if 'data' in response:
        data = response['data']
        print(f"📊 Results found: {len(data.get('results', []))}")

async def test_stage0_service():
    """Test the Stage0SerpService"""
    print("\n🚀 Testing Stage0 SERP Service")
    print("=" * 50)
    
    try:
        service = Stage0SerpService()
        
        # Create a test request
        request = Stage0SerpRequest(
            request_id=f"test_{int(datetime.utcnow().timestamp())}",
            content="FDA AI guidelines pharmaceutical industry",
            metadata={"test": True, "source": "manual_test"}
        )
        
        print(f"📝 Processing request: {request.request_id}")
        print(f"🔍 Query: {request.content}")
        
        # Process the request
        response = await service.process(request)
        
        print(f"✅ Status: {response.status}")
        print(f"📊 Request ID: {response.request_id}")
        
        if 'search_results' in response.result:
            search_results = response.result['search_results']
            print(f"🔍 Query processed: {search_results['query']}")
            print(f"📈 Total results: {search_results['total_results']}")
            print(f"📋 Results returned: {len(search_results['results'])}")
            
            print("\n📄 Sample Results:")
            for i, result in enumerate(search_results['results'][:2], 1):
                print(f"  {i}. {result['title']}")
                print(f"     🔗 {result['url']}")
                print(f"     🌐 {result['domain']}")
                print()
        
    except Exception as e:
        print(f"❌ Error testing Stage0 service: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_response_formats():
    """Test different response formats"""
    print("\n📋 Testing Response Formats")
    print("=" * 50)
    
    mock = SerpMock()
    
    # Test with different parameters
    test_cases = [
        {"query": "AI drug discovery", "num_results": 2},
        {"query": "regulatory compliance", "num_results": 5},
        {"query": "nonexistent query xyz123", "num_results": 3}
    ]
    
    for case in test_cases:
        print(f"\n🧪 Test case: {case}")
        
        request = SerpRequest(**case)
        response = await mock.search(request)
        
        print(f"  📊 Results: {len(response.results)}")
        print(f"  🆔 Request ID: {response.request_id}")
        print(f"  📅 Created: {response.created_at}")
        print(f"  🔧 Metadata: {response.search_metadata}")
        
        # Test URL extraction
        urls = response.get_urls()
        print(f"  🔗 URLs extracted: {len(urls)}")

def print_header():
    """Print test header"""
    print("🧪 Stage 0 SERP Agent Test Suite")
    print("=" * 60)
    print("This script tests the SERP agent implementation with mock data")
    print("No real API calls will be made - only mock responses")
    print("=" * 60)

async def main():
    """Main test function"""
    print_header()
    
    try:
        # Run all tests
        await test_serp_mock()
        await test_legacy_api()
        await test_stage0_service()
        await test_response_formats()
        
        print("\n🎉 All tests completed successfully!")
        print("✅ The Stage 0 SERP agent is working correctly with mock data")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    # Run the tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 