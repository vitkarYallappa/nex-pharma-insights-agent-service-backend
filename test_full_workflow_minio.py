#!/usr/bin/env python3
"""
Full Workflow MinIO Test

This test runs the complete market intelligence workflow including:
1. SERP URL discovery
2. Perplexity content generation 
3. Report assembly
4. MinIO storage

This will show the complete Perplexity summary in MinIO.
"""

import os
import sys
import asyncio
import json
from datetime import datetime

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.root_orchestrator.temp_service_factory import ServiceFactory
from app.root_orchestrator.temp_market_intelligence_service import MarketIntelligenceService


async def test_minio_storage():
    """Test MinIO storage functionality"""
    print("📦 TESTING MINIO STORAGE")
    print("="*50)
    
    storage_client = ServiceFactory.get_storage_client()
    minio_client = ServiceFactory.get_minio_client()
    
    print(f"Storage Client: {type(storage_client).__name__}")
    print(f"MinIO Client: {type(minio_client).__name__}")
    print(f"MinIO Endpoint: {minio_client.endpoint}")
    print(f"MinIO Bucket: {minio_client.bucket_name}")
    
    # Test basic storage
    test_data = {"test": "data", "timestamp": datetime.utcnow().isoformat()}
    test_key = "test/workflow_test.json"
    
    success = await storage_client.save_json(test_key, test_data)
    print(f"Test storage: {'✅ Success' if success else '❌ Failed'}")
    
    # List current objects
    objects = await minio_client.list_objects()
    print(f"Current objects in MinIO: {len(objects)}")
    for obj in objects[:5]:  # Show first 5
        print(f"  - {obj}")
    
    return success


async def test_full_market_intelligence_workflow():
    """Test the complete market intelligence workflow with MinIO storage"""
    print("\n🔄 FULL MARKET INTELLIGENCE WORKFLOW TEST")
    print("="*60)
    
    # Initialize the market intelligence service
    service = MarketIntelligenceService()
    
    # Generate a unique request ID
    request_id = f"test_workflow_{int(datetime.utcnow().timestamp())}"
    print(f"Request ID: {request_id}")
    
    try:
        # Execute the complete workflow
        print(f"\n📡 Executing complete semaglutide intelligence workflow...")
        start_time = datetime.now()
        
        result = await service.execute_semaglutide_intelligence(request_id)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Workflow completed in {duration:.2f}s")
        
        # Show result summary
        if result:
            print(f"\n📊 WORKFLOW RESULTS:")
            print(f"   Report Type: {result.get('report_type', 'N/A')}")
            print(f"   Generated At: {result.get('generated_at', 'N/A')}")
            
            sections = result.get('sections', {})
            print(f"   Sections: {list(sections.keys())}")
            
            metadata = result.get('metadata', {})
            print(f"   Total Citations: {metadata.get('total_citations', 0)}")
            print(f"   Processing Stages: {metadata.get('processing_stages', 0)}")
            print(f"   Content Source: {metadata.get('content_source', 'N/A')}")
            
            # Show URL discovery results
            url_discovery = sections.get('url_discovery', {})
            if url_discovery:
                print(f"\n🔍 URL DISCOVERY RESULTS:")
                print(f"   Total URLs: {url_discovery.get('total_urls_discovered', 0)}")
                print(f"   Domains: {url_discovery.get('domains_searched', [])}")
                
                urls_by_domain = url_discovery.get('urls_by_domain', {})
                for domain, urls in urls_by_domain.items():
                    # Handle case where urls might be an int instead of list
                    if isinstance(urls, list):
                        print(f"   {domain}: {len(urls)} URLs")
                        for url in urls[:2]:  # Show first 2 URLs per domain
                            print(f"     - {url}")
                    else:
                        print(f"   {domain}: {urls} URLs")
            
            # Show Perplexity content summaries
            print(f"\n🧠 PERPLEXITY CONTENT SUMMARIES:")
            
            market_summary = sections.get('market_summary', {})
            if market_summary:
                content = market_summary.get('content', '')
                print(f"   Market Summary: {len(content)} characters")
                print(f"     Preview: {content[:100]}...")
            
            competitive_analysis = sections.get('competitive_analysis', {})
            if competitive_analysis:
                content = competitive_analysis.get('content', '')
                print(f"   Competitive Analysis: {len(content)} characters")
                print(f"     Preview: {content[:100]}...")
            
            regulatory_insights = sections.get('regulatory_insights', {})
            if regulatory_insights:
                content = regulatory_insights.get('content', '')
                print(f"   Regulatory Insights: {len(content)} characters")
                print(f"     Preview: {content[:100]}...")
            
            market_implications = sections.get('market_implications', {})
            if market_implications:
                content = market_implications.get('content', '')
                print(f"   Market Implications: {len(content)} characters")
                print(f"     Preview: {content[:100]}...")
        
        return result
        
    except Exception as e:
        print(f"❌ Workflow Error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def check_minio_report_storage():
    """Check what reports are stored in MinIO"""
    print(f"\n📦 CHECKING MINIO REPORT STORAGE")
    print("="*50)
    
    minio_client = ServiceFactory.get_minio_client()
    storage_client = ServiceFactory.get_storage_client()
    
    # List all objects in MinIO
    objects = await minio_client.list_objects()
    print(f"Total objects in MinIO: {len(objects)}")
    
    # Filter for report files
    report_objects = [obj for obj in objects if obj.startswith('reports/')]
    print(f"Report objects: {len(report_objects)}")
    
    for report_obj in report_objects:
        print(f"  📄 {report_obj}")
        
        # Try to load and show summary of each report
        try:
            report_data = await storage_client.load_json(report_obj)
            if report_data:
                print(f"     Type: {report_data.get('report_type', 'N/A')}")
                print(f"     Generated: {report_data.get('generated_at', 'N/A')}")
                
                sections = report_data.get('sections', {})
                if 'market_summary' in sections:
                    summary_content = sections['market_summary'].get('content', '')
                    print(f"     Market Summary: {len(summary_content)} chars")
                    if summary_content:
                        print(f"     Preview: {summary_content[:80]}...")
        except Exception as e:
            print(f"     ❌ Error loading report: {e}")
    
    return report_objects


async def main():
    """Main test function"""
    print("🧪 FULL WORKFLOW MINIO TEST")
    print("Testing complete market intelligence workflow with MinIO storage")
    print("="*70)
    
    # Check current configuration
    serp_key = os.getenv("SERPAPI_KEY")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    
    print(f"Current Mode: Production APIs")
    print(f"SERP Key: {'✅ Set' if serp_key else '❌ Missing'}")
    print(f"Perplexity Key: {'✅ Set' if perplexity_key else '❌ Missing'}")
    
    # Test MinIO storage
    storage_success = await test_minio_storage()
    
    # Check existing reports
    existing_reports = await check_minio_report_storage()
    
    # Run full workflow
    workflow_result = await test_full_market_intelligence_workflow()
    
    # Check MinIO again after workflow
    print(f"\n📦 MINIO AFTER WORKFLOW")
    print("="*50)
    new_reports = await check_minio_report_storage()
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print(f"{'='*70}")
    
    print(f"MinIO Storage: {'✅ Working' if storage_success else '❌ Failed'}")
    print(f"Workflow Execution: {'✅ Success' if workflow_result else '❌ Failed'}")
    print(f"Reports Before: {len(existing_reports)}")
    print(f"Reports After: {len(new_reports)}")
    print(f"New Reports Created: {len(new_reports) - len(existing_reports)}")
    
    if workflow_result:
        print(f"\n🎉 SUCCESS! Complete workflow executed and stored in MinIO")
        print(f"   You should now be able to see the Perplexity summary in MinIO")
        print(f"   Check the 'reports/semaglutide/' folder in your MinIO console")
        
        # Show MinIO console access
        print(f"\n🌐 MinIO Console Access:")
        print(f"   URL: http://localhost:9091")
        print(f"   Username: minioadmin")
        print(f"   Password: minioadmin123")
        print(f"   Bucket: nex-pharma")
        print(f"   Reports Path: reports/semaglutide/")
    else:
        print(f"\n❌ Workflow failed - check error messages above")
    
    return 0 if (storage_success and workflow_result) else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 