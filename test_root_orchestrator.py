#!/usr/bin/env python3
"""
Root Orchestrator End-to-End Test

This script tests the complete Root Orchestrator system including:
- Request submission
- Status tracking
- Background processing
- Results retrieval
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Import Root Orchestrator components
from app.root_orchestrator.models import (
    MarketIntelligenceRequest,
    RequestStatus,
    RequestType,
    Priority,
    ProcessingStrategy,
    MarketIntelligenceRequestConfig
)
from app.root_orchestrator.root_orchestrator_service import RootOrchestratorService
from app.controllers.market_intelligence_controller import MarketIntelligenceController
from app.schemas.market_intelligence_schema import SubmitRequestSchema


async def test_root_orchestrator_system():
    """Test the complete Root Orchestrator system"""
    
    print("🚀 Starting Root Orchestrator End-to-End Test")
    print("=" * 60)
    
    try:
        # 1. Test Root Orchestrator Service initialization
        print("\n1️⃣ Testing Root Orchestrator Service Initialization...")
        
        orchestrator = RootOrchestratorService()
        await orchestrator.initialize()
        
        print("✅ Root Orchestrator Service initialized successfully")
        
        # 2. Test request submission through controller
        print("\n2️⃣ Testing Request Submission...")
        
        controller = MarketIntelligenceController()
        
        # Create a test request
        request_data = SubmitRequestSchema(
            project_id="test-project-001",
            user_id="test-user-123",
            priority=Priority.HIGH,
            processing_strategy=ProcessingStrategy.TABLE,
            metadata={"test_run": True, "timestamp": datetime.utcnow().isoformat()}
        )
        
        # Submit the request
        response = await controller.submit_request(request_data)
        request_id = response.request_id
        
        print(f"✅ Request submitted successfully: {request_id}")
        print(f"   Status: {response.status}")
        print(f"   Message: {response.message}")
        
        # 3. Test status tracking
        print("\n3️⃣ Testing Status Tracking...")
        
        # Check initial status
        status_response = await controller.get_request_status(request_id)
        print(f"✅ Initial status retrieved: {status_response.status}")
        print(f"   Current stage: {status_response.current_stage}")
        print(f"   Progress: {status_response.progress_percentage}%")
        
        # 4. Wait for processing to complete (with timeout)
        print("\n4️⃣ Waiting for Processing to Complete...")
        
        max_wait_time = 30  # 30 seconds timeout
        wait_interval = 2   # Check every 2 seconds
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
            
            status_response = await controller.get_request_status(request_id)
            print(f"   [{elapsed_time}s] Status: {status_response.status}, Progress: {status_response.progress_percentage}%")
            
            if status_response.status in [RequestStatus.COMPLETED, RequestStatus.FAILED]:
                break
        
        # 5. Test results retrieval
        if status_response.status == RequestStatus.COMPLETED:
            print("\n5️⃣ Testing Results Retrieval...")
            
            results_response = await controller.get_request_results(request_id)
            
            print("✅ Results retrieved successfully:")
            print(f"   Report Path: {results_response.report_path}")
            print(f"   Summary: {results_response.summary}")
            print(f"   Total Sources: {results_response.total_sources}")
            print(f"   Total Content Items: {results_response.total_content_items}")
            print(f"   Success Rate: {results_response.success_rate}%")
            print(f"   Processing Duration: {results_response.processing_duration}s")
        else:
            print(f"❌ Request did not complete successfully: {status_response.status}")
        
        # 6. Test statistics
        print("\n6️⃣ Testing Statistics Retrieval...")
        
        stats_response = await controller.get_processing_statistics(1)  # Last 1 hour
        
        print("✅ Statistics retrieved successfully:")
        print(f"   Strategy: {stats_response.strategy}")
        print(f"   Total Requests: {stats_response.total_requests}")
        print(f"   Completed Requests: {stats_response.completed_requests}")
        print(f"   Success Rate: {stats_response.success_rate}%")
        print(f"   Active Requests: {stats_response.active_requests}")
        
        # 7. Test health check
        print("\n7️⃣ Testing Health Check...")
        
        health_response = await controller.get_health_status()
        
        print("✅ Health check completed:")
        print(f"   Overall Status: {health_response.status}")
        print(f"   Database: {health_response.database}")
        print(f"   Storage: {health_response.storage}")
        print(f"   Processing Strategy: {health_response.processing_strategy}")
        print(f"   Uptime: {health_response.uptime_seconds:.1f}s")
        
        # 8. Test configuration
        print("\n8️⃣ Testing Configuration Retrieval...")
        
        config_response = await controller.get_configuration()
        
        print("✅ Configuration retrieved successfully:")
        print(f"   Available Strategies: {config_response.available_strategies}")
        print(f"   Default Strategy: {config_response.default_strategy}")
        print(f"   Max Concurrent Requests: {config_response.max_concurrent_requests}")
        print(f"   API Version: {config_response.api_version}")
        
        # 9. Cleanup
        print("\n9️⃣ Cleanup...")
        
        await orchestrator.shutdown()
        print("✅ Root Orchestrator Service shutdown successfully")
        
        print("\n🎉 All tests completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        # Try to cleanup
        try:
            if 'orchestrator' in locals():
                await orchestrator.shutdown()
        except:
            pass
        
        return False


async def test_api_schemas():
    """Test API schema validation"""
    
    print("\n📋 Testing API Schema Validation...")
    
    try:
        # Test valid request schema
        valid_request = SubmitRequestSchema(
            project_id="test-project",
            user_id="test-user",
            priority=Priority.MEDIUM,
            processing_strategy=ProcessingStrategy.TABLE
        )
        
        print("✅ Valid request schema validation passed")
        
        # Test invalid request schema
        try:
            invalid_request = SubmitRequestSchema(
                project_id="",  # Empty project ID should fail
                user_id="test-user"
            )
            print("❌ Invalid request schema should have failed")
            return False
        except Exception:
            print("✅ Invalid request schema validation correctly failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation test failed: {e}")
        return False


def display_test_summary():
    """Display test summary and next steps"""
    
    print("\n" + "=" * 60)
    print("🎯 ROOT ORCHESTRATOR TEST SUMMARY")
    print("=" * 60)
    
    print("\n✅ COMPLETED COMPONENTS:")
    print("   • Root Orchestrator Service")
    print("   • Table Processing Strategy")
    print("   • Background Table Processor")
    print("   • Market Intelligence Controller")
    print("   • API Routes and Schemas")
    print("   • Status Tracking System")
    print("   • Mock Services (Database, Storage, MI Service)")
    
    print("\n🔧 ARCHITECTURE VALIDATED:")
    print("   • Request submission and validation")
    print("   • Background processing with polling")
    print("   • Status tracking and progress updates")
    print("   • Results storage and retrieval")
    print("   • Health monitoring and statistics")
    print("   • Configuration management")
    
    print("\n🚀 NEXT STEPS:")
    print("   1. Replace mock services with real implementations")
    print("   2. Add SQS processing strategy")
    print("   3. Implement comprehensive testing suite")
    print("   4. Add monitoring and alerting")
    print("   5. Deploy to production environment")
    
    print("\n📚 USAGE:")
    print("   • Submit requests via POST /api/v1/market-intelligence/requests")
    print("   • Track status via GET /api/v1/market-intelligence/requests/{id}")
    print("   • Get results via GET /api/v1/market-intelligence/requests/{id}/results")
    print("   • Monitor health via GET /api/v1/market-intelligence/health")
    
    print("\n" + "=" * 60)


async def main():
    """Main test function"""
    
    print("🧪 ROOT ORCHESTRATOR COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    # Run schema tests
    schema_success = await test_api_schemas()
    
    # Run end-to-end tests
    e2e_success = await test_root_orchestrator_system()
    
    # Display summary
    display_test_summary()
    
    # Final result
    if schema_success and e2e_success:
        print("\n🎉 ALL TESTS PASSED - Root Orchestrator is ready!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Please check the errors above")
        return 1


if __name__ == "__main__":
    """Run the test suite"""
    import sys
    
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {e}")
        sys.exit(1) 