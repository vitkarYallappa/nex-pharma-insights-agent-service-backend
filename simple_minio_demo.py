#!/usr/bin/env python3
"""
Simple MinIO Demo - Store Report in Real MinIO

This demo connects to your MinIO server and stores a market intelligence report
so you can see it in the MinIO console at http://localhost:9090
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.root_orchestrator.temp_service_factory import ServiceFactory

# MinIO client using boto3
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


class SimpleMinIOClient:
    """Simple MinIO client for storing reports"""
    
    def __init__(self):
        # MinIO configuration based on your Docker setup
        self.endpoint = "localhost:9001"  # Your MinIO S3 API port
        self.access_key = "minioadmin"
        self.secret_key = "minioadmin123"
        self.bucket_name = "nex-pharma"
        
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required. Install with: pip install boto3")
        
        # Create S3 client for MinIO
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f"http://{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name='us-east-1'
        )
        
        print(f"🔗 Connected to MinIO: {self.endpoint}")
    
    async def ensure_bucket_exists(self):
        """Ensure the bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f"✅ Bucket '{self.bucket_name}' exists")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    print(f"✅ Created bucket '{self.bucket_name}'")
                    return True
                except Exception as create_error:
                    print(f"❌ Failed to create bucket: {create_error}")
                    return False
            else:
                print(f"❌ Bucket error: {e}")
                return False
    
    async def save_json_report(self, key: str, data: dict) -> bool:
        """Save JSON report to MinIO"""
        try:
            json_data = json.dumps(data, default=str, indent=2)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            
            print(f"✅ Saved report to MinIO: {key} ({len(json_data)} bytes)")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save report: {e}")
            return False
    
    async def list_reports(self) -> list:
        """List all reports in MinIO"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix='reports/'
            )
            
            objects = response.get('Contents', [])
            report_keys = [obj['Key'] for obj in objects]
            
            print(f"📋 Found {len(report_keys)} reports in MinIO")
            return report_keys
            
        except Exception as e:
            print(f"❌ Failed to list reports: {e}")
            return []


async def create_sample_report(request_id: str) -> dict:
    """Create a sample market intelligence report"""
    
    print("🔍 Step 1: SERP API - Finding 2 quality URLs...")
    
    # Get SERP client
    serp_client = ServiceFactory.get_serp_client()
    
    serp_response = await serp_client.call_api({
        "query": "semaglutide tirzepatide obesity market 2024",
        "num_results": 10
    })
    
    # Extract top 2 URLs
    discovered_urls = []
    if serp_response.get("status") == "success" and serp_response.get("data"):
        results = serp_response["data"].get("results", [])
        for result in results[:2]:
            if result.get("url"):
                discovered_urls.append(result["url"])
                print(f"   📎 {result.get('title', 'No title')}")
                print(f"      {result['url']}")
    
    print(f"✅ Found {len(discovered_urls)} URLs")
    
    print("\n🧠 Step 2: Perplexity API - Generating comprehensive analysis...")
    
    # Get Perplexity client
    perplexity_client = ServiceFactory.get_perplexity_client()
    
    query = f"""
    Provide a comprehensive market intelligence report on semaglutide and GLP-1 receptor agonists for obesity treatment.
    
    Include these sections:
    1. Market Summary - Current size, growth, key players
    2. Competitive Analysis - Semaglutide vs Tirzepatide
    3. Regulatory Insights - FDA approvals, safety
    4. Market Implications - Future outlook
    
    {f"Consider these sources: {', '.join(discovered_urls)}" if discovered_urls else ""}
    """
    
    perplexity_response = await perplexity_client.search_with_metadata(query)
    content = perplexity_response.get("content", "")
    
    print(f"✅ Generated {len(content)} characters of analysis")
    
    # Create structured report
    report = {
        "request_id": request_id,
        "report_type": "simple_minio_semaglutide_intelligence",
        "generated_at": datetime.utcnow().isoformat(),
        "api_calls_made": {
            "serp_call": {
                "purpose": "Find 2 recent, quality URLs about semaglutide market",
                "result": f"Found {len(discovered_urls)} URLs"
            },
            "perplexity_call": {
                "purpose": "Generate comprehensive market intelligence report", 
                "result": f"Generated {len(content)} characters of analysis"
            }
        },
        "sections": {
            "url_discovery": {
                "total_urls_discovered": len(discovered_urls),
                "discovered_urls": discovered_urls,
                "search_query": "semaglutide tirzepatide obesity market 2024"
            },
            "comprehensive_analysis": {
                "content": content,
                "citations": perplexity_response.get("citations", []),
                "usage": perplexity_response.get("usage", {}),
                "generated_at": datetime.utcnow().isoformat()
            }
        },
        "metadata": {
            "content_source": "serp_api + perplexity_api",
            "total_api_calls": 2,
            "total_citations": len(perplexity_response.get("citations", [])),
            "total_cost": perplexity_response.get("usage", {}).get("cost", 0),
            "storage_location": "real_minio"
        }
    }
    
    return report


async def main():
    """Main demo function"""
    
    print("📦 SIMPLE MINIO DEMO - SERP → Perplexity → MinIO")
    print("="*60)
    print("This demo shows the minimal workflow:")
    print("1. 🔍 SERP API: Find 2 quality URLs")
    print("2. 🧠 Perplexity API: Generate comprehensive analysis")  
    print("3. 📦 MinIO: Store report for viewing in console")
    print("="*60)
    
    # Check configuration
    serp_key = os.getenv("SERPAPI_KEY")
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    
    print(f"\n🔧 CONFIGURATION:")
    print(f"   API Mode: Production APIs")
    print(f"   SERP API: {'✅' if serp_key else '❌'}")
    print(f"   Perplexity API: {'✅' if perplexity_key else '❌'}")
    print(f"   MinIO Endpoint: localhost:9001")
    print(f"   MinIO Console: http://localhost:9090")
    
    if not BOTO3_AVAILABLE:
        print(f"\n❌ ERROR: boto3 not available")
        print(f"   Install with: pip install boto3")
        return 1
    
    try:
        # Initialize MinIO client
        print(f"\n🔌 CONNECTING TO MINIO...")
        minio_client = SimpleMinIOClient()
        
        # Ensure bucket exists
        bucket_ready = await minio_client.ensure_bucket_exists()
        if not bucket_ready:
            print(f"❌ MinIO bucket not ready")
            return 1
        
        # Generate report
        request_id = f"simple_minio_{int(datetime.utcnow().timestamp())}"
        
        print(f"\n🚀 GENERATING REPORT (ID: {request_id})")
        print("-" * 50)
        
        start_time = datetime.now()
        report = await create_sample_report(request_id)
        end_time = datetime.now()
        
        duration = (end_time - start_time).total_seconds()
        
        print(f"\n📦 Step 3: Storing report in MinIO...")
        
        # Store in MinIO
        storage_key = f"reports/semaglutide/{request_id}.json"
        success = await minio_client.save_json_report(storage_key, report)
        
        if success:
            print(f"\n✅ WORKFLOW COMPLETED IN {duration:.1f} SECONDS")
            print("="*60)
            
            # Show results
            print(f"\n📊 RESULTS:")
            print(f"   Report ID: {request_id}")
            print(f"   Processing Time: {duration:.1f}s")
            print(f"   API Calls Made: 2 (SERP + Perplexity)")
            print(f"   Report Size: {len(json.dumps(report))} bytes")
            print(f"   Storage Key: {storage_key}")
            
            # Show MinIO access
            print(f"\n🌐 VIEW REPORT IN MINIO:")
            print(f"   Console URL: http://localhost:9090")
            print(f"   Username: minioadmin")
            print(f"   Password: minioadmin123")
            print(f"   Bucket: nex-pharma")
            print(f"   Report Path: {storage_key}")
            
            # List all reports
            all_reports = await minio_client.list_reports()
            print(f"\n📋 ALL REPORTS IN MINIO:")
            for report_key in all_reports:
                print(f"   📄 {report_key}")
            
            print(f"\n🎉 SUCCESS! Report is now visible in MinIO console.")
            print(f"💡 Go to http://localhost:9090 to view your report!")
            
            return 0
        else:
            print(f"❌ Failed to store report in MinIO")
            return 1
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 