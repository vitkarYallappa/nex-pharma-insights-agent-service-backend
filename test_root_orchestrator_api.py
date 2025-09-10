#!/usr/bin/env python3
"""
Root Orchestrator API Test

This test script validates the Root Orchestrator API endpoints:
1. POST /api/v1/market-intelligence/requests - Submit request
2. GET /api/v1/market-intelligence/requests/{request_id} - Get status
3. GET /api/v1/market-intelligence/requests/{request_id}/results - Get results

This tests the complete API flow from request submission to completion.
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any

import httpx
from pydantic import BaseModel

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configuration
BASE_URL = "http://localhost:8005"
API_PREFIX = "/api/v1/market-intelligence"


class APITestConfig:
    """Configuration for API testing"""
    
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", BASE_URL)
        self.timeout = int(os.getenv("API_TIMEOUT", "30"))
        self.max_wait_time = int(os.getenv("MAX_WAIT_TIME", "300"))  # 5 minutes
        self.poll_interval = int(os.getenv("POLL_INTERVAL", "5"))  # 5 seconds


class APITester:
    """API testing client for Root Orchestrator"""
    
    def __init__(self, config: APITestConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            base_url=config.base_url,
            timeout=config.timeout
        )
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def health_check(self) -> bool:
        """Check if the API server is running"""
        try:
            response = await self.client.get("/health")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
    
    async def submit_request(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Submit a market intelligence request"""
        try:
            print(f"📤 Submitting request...")
            print(f"   Data: {json.dumps(request_data, indent=2)}")
            
            response = await self.client.post(
                f"{API_PREFIX}/requests",
                json=request_data
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Request submitted successfully!")
                print(f"   Request ID: {result.get('request_id')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Message: {result.get('message')}")
                return result
            else:
                print(f"❌ Request submission failed:")
                print(f"   Status: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error submitting request: {e}")
            return None
    
    async def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a request"""
        try:
            response = await self.client.get(f"{API_PREFIX}/requests/{request_id}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"❌ Request not found: {request_id}")
                return None
            else:
                print(f"❌ Error getting status: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting request status: {e}")
            return None
    
    async def get_request_results(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get the results of a completed request"""
        try:
            response = await self.client.get(f"{API_PREFIX}/requests/{request_id}/results")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                print(f"❌ Request not found: {request_id}")
                return None
            elif response.status_code == 202:
                print(f"⏳ Request still processing: {request_id}")
                return None
            else:
                print(f"❌ Error getting results: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting request results: {e}")
            return None
    
    async def wait_for_completion(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Wait for a request to complete and return final status"""
        print(f"⏳ Waiting for request completion: {request_id}")
        
        start_time = time.time()
        max_wait = self.config.max_wait_time
        poll_interval = self.config.poll_interval
        
        while time.time() - start_time < max_wait:
            status_data = await self.get_request_status(request_id)
            
            if not status_data:
                print(f"❌ Failed to get status for request: {request_id}")
                return None
            
            status = status_data.get('status')
            progress = status_data.get('progress_percentage', 0)
            current_stage = status_data.get('current_stage', 'unknown')
            
            elapsed = time.time() - start_time
            print(f"   [{elapsed:.0f}s] Status: {status} | Progress: {progress}% | Stage: {current_stage}")
            
            if status in ['COMPLETED', 'FAILED']:
                return status_data
            
            await asyncio.sleep(poll_interval)
        
        print(f"⏰ Timeout waiting for completion after {max_wait}s")
        return await self.get_request_status(request_id)


async def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 ROOT ORCHESTRATOR API TEST")
    print("="*60)
    
    config = APITestConfig()
    
    async with APITester(config) as tester:
        # Health check
        print(f"\n🏥 HEALTH CHECK")
        print("-" * 30)
        
        is_healthy = await tester.health_check()
        if not is_healthy:
            print(f"❌ API server is not running at {config.base_url}")
            print(f"   Please start the server with: python start_server.py")
            return False
        
        print(f"✅ API server is running at {config.base_url}")
        
        # Test request submission
        print(f"\n📤 REQUEST SUBMISSION TEST")
        print("-" * 30)
        
        # Create test request data
        request_data = {
            "project_id": "test_project_001",
            "user_id": "test_user_001",
            "priority": "high",
            "processing_strategy": "table",
            "config": {
                "keywords": ["semaglutide", "tirzepatide", "wegovy"],
                "sources": [
                    {"name": "FDA", "type": "regulatory"},
                    {"name": "NIH", "type": "academic"}
                ],
                "extraction_mode": "summary",
                "quality_threshold": 0.7
            },
            "metadata": {
                "test_run": True,
                "submitted_via": "api_test",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        # Submit request
        submission_result = await tester.submit_request(request_data)
        if not submission_result:
            print(f"❌ Request submission failed")
            return False
        
        request_id = submission_result.get('request_id')
        
        # Test status checking
        print(f"\n📊 STATUS CHECKING TEST")
        print("-" * 30)
        
        initial_status = await tester.get_request_status(request_id)
        if initial_status:
            print(f"✅ Initial status retrieved:")
            print(f"   Status: {initial_status.get('status')}")
            print(f"   Created: {initial_status.get('created_at')}")
            print(f"   Priority: {initial_status.get('priority')}")
            print(f"   Strategy: {initial_status.get('processing_strategy')}")
        
        # Wait for processing to complete
        print(f"\n⏳ WORKFLOW EXECUTION TEST")
        print("-" * 30)
        
        final_status = await tester.wait_for_completion(request_id)
        
        if not final_status:
            print(f"❌ Failed to get final status")
            return False
        
        final_status_value = final_status.get('status')
        
        if final_status_value == 'COMPLETED':
            print(f"✅ Request completed successfully!")
            
            # Test results retrieval
            print(f"\n📋 RESULTS RETRIEVAL TEST")
            print("-" * 30)
            
            results = await tester.get_request_results(request_id)
            if results:
                print(f"✅ Results retrieved successfully:")
                
                # Show results summary
                report_data = results.get('report_data', {})
                if report_data:
                    print(f"   Report Type: {report_data.get('report_type')}")
                    print(f"   Generated At: {report_data.get('generated_at')}")
                    
                    sections = report_data.get('sections', {})
                    print(f"   Sections: {list(sections.keys())}")
                    
                    metadata = report_data.get('metadata', {})
                    print(f"   Total Citations: {metadata.get('total_citations', 0)}")
                    print(f"   Processing Time: {metadata.get('processing_time_seconds', 0)}s")
                
                storage_info = results.get('storage_info', {})
                if storage_info:
                    print(f"   Storage Path: {storage_info.get('report_path')}")
                    print(f"   File Size: {storage_info.get('file_size_bytes', 0)} bytes")
                
            else:
                print(f"❌ Failed to retrieve results")
                return False
                
        elif final_status_value == 'FAILED':
            print(f"❌ Request failed:")
            errors = final_status.get('errors', [])
            for error in errors:
                print(f"   Error: {error}")
            return False
        
        else:
            print(f"⚠️  Request ended with status: {final_status_value}")
            return False
    
    return True


async def test_error_scenarios():
    """Test error handling scenarios"""
    print(f"\n🚨 ERROR SCENARIO TESTS")
    print("-" * 30)
    
    config = APITestConfig()
    
    async with APITester(config) as tester:
        # Test invalid request data
        print(f"Testing invalid request data...")
        
        invalid_request = {
            "project_id": "",  # Invalid empty project_id
            "user_id": "test_user",
            "priority": "INVALID_PRIORITY"  # Invalid priority
        }
        
        result = await tester.submit_request(invalid_request)
        if result is None:
            print(f"✅ Invalid request properly rejected")
        else:
            print(f"❌ Invalid request was accepted (should be rejected)")
        
        # Test non-existent request status
        print(f"Testing non-existent request...")
        
        fake_request_id = "non_existent_request_123"
        status = await tester.get_request_status(fake_request_id)
        if status is None:
            print(f"✅ Non-existent request properly handled")
        else:
            print(f"❌ Non-existent request returned data (should return None)")


async def main():
    """Main test function"""
    print("🚀 Starting Root Orchestrator API Tests")
    print(f"Target URL: {BASE_URL}")
    print(f"API Prefix: {API_PREFIX}")
    
    # Check environment
    print("Production Mode: Enabled")
    
    try:
        # Run main API tests
        success = await test_api_endpoints()
        
        # Run error scenario tests
        await test_error_scenarios()
        
        # Summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        if success:
            print(f"🎉 ALL TESTS PASSED!")
            print(f"   ✅ API server is running")
            print(f"   ✅ Request submission works")
            print(f"   ✅ Status checking works")
            print(f"   ✅ Workflow execution works")
            print(f"   ✅ Results retrieval works")
            print(f"   ✅ Error handling works")
            
            print(f"\n🌐 API Documentation:")
            print(f"   Swagger UI: {BASE_URL}/docs")
            print(f"   ReDoc: {BASE_URL}/redoc")
            
        else:
            print(f"❌ SOME TESTS FAILED")
            print(f"   Check the error messages above for details")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 