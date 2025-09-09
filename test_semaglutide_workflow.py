#!/usr/bin/env python3
"""
Test script for Semaglutide Market Intelligence Workflow

This script validates the configuration and demonstrates the workflow structure
without making actual API calls.
"""

import sys
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append('.')

from app.agent_service_module.config.market_intelligence_config import (
    MarketIntelligenceConfig,
    MarketIntelligenceSource, 
    MarketIntelligenceWorkflow,
    DEFAULT_SEMAGLUTIDE_CONFIG
)


def test_configuration():
    """Test the market intelligence configuration"""
    print("🧪 TESTING MARKET INTELLIGENCE CONFIGURATION")
    print("=" * 60)
    
    # Test default configuration
    config = DEFAULT_SEMAGLUTIDE_CONFIG
    
    print(f"✅ Configuration loaded successfully")
    print(f"Title: {config.title}")
    print(f"Objective: {config.objective}")
    print(f"Priority: {config.priority}")
    print(f"Keywords: {len(config.primary_keywords)} items")
    print(f"Sources: {len(config.sources)} sources")
    
    # Test search query generation
    search_query = config.get_search_query()
    print(f"\n🔍 Generated search query:")
    print(f"Query: {search_query}")
    
    # Test site-specific queries
    print(f"\n🌐 Site-specific queries:")
    for source in config.sources:
        site_query = config.get_site_specific_query(source)
        print(f"{source.name}: {site_query[:100]}...")
    
    # Test URL calculations
    total_urls = config.get_total_expected_urls()
    print(f"\n📊 Expected URLs: {total_urls}")
    
    # Test source filtering
    regulatory_sources = config.get_sources_by_type("regulatory")
    clinical_sources = config.get_sources_by_type("clinical")
    academic_sources = config.get_sources_by_type("academic")
    
    print(f"\n📋 Sources by type:")
    print(f"Regulatory: {len(regulatory_sources)} sources")
    print(f"Clinical: {len(clinical_sources)} sources")
    print(f"Academic: {len(academic_sources)} sources")
    
    return config


def test_workflow():
    """Test the workflow orchestrator"""
    print(f"\n🔄 TESTING WORKFLOW ORCHESTRATOR")
    print("=" * 60)
    
    # Initialize workflow
    workflow = MarketIntelligenceWorkflow()
    
    # Test search request generation
    search_requests = workflow.generate_search_requests()
    print(f"✅ Generated {len(search_requests)} search requests")
    
    for i, request in enumerate(search_requests, 1):
        print(f"\n{i}. {request['source_name']} ({request['source_type']})")
        print(f"   Query: {request['query'][:80]}...")
        print(f"   Max Results: {request['num_results']}")
        print(f"   Priority: {request['priority']}")
    
    # Test API call calculations
    api_calls = workflow.calculate_api_calls()
    print(f"\n🔧 API Call Estimates:")
    print(f"SERP calls: {api_calls['serp_calls']}")
    print(f"Perplexity calls: {api_calls['perplexity_calls']}")
    print(f"Total calls: {api_calls['total_calls']}")
    print(f"Expected URLs: {api_calls['expected_urls']}")
    
    # Test workflow summary
    summary = workflow.get_workflow_summary()
    print(f"\n📋 Workflow Summary Generated:")
    print(f"Configuration keys: {list(summary.keys())}")
    
    return workflow, summary


def test_custom_configuration():
    """Test custom configuration creation"""
    print(f"\n⚙️  TESTING CUSTOM CONFIGURATION")
    print("=" * 60)
    
    # Create custom configuration
    custom_config = MarketIntelligenceConfig(
        title="Custom Semaglutide Intelligence",
        objective="Extended monitoring with additional sources",
        created_by="test-user",
        
        primary_keywords=[
            "semaglutide", "tirzepatide", "wegovy", "ozempic",
            "GLP-1", "diabetes", "obesity", "weight loss"
        ],
        
        sources=[
            MarketIntelligenceSource(
                name="FDA",
                base_url="https://www.fda.gov",
                source_type="regulatory",
                priority=1,
                max_results_per_query=8
            ),
            MarketIntelligenceSource(
                name="NIH",
                base_url="https://www.nih.gov", 
                source_type="academic",
                priority=2,
                max_results_per_query=6
            ),
            MarketIntelligenceSource(
                name="ClinicalTrials.gov",
                base_url="https://clinicaltrials.gov",
                source_type="clinical",
                priority=1,
                max_results_per_query=10
            ),
            MarketIntelligenceSource(
                name="EMA",
                base_url="https://www.ema.europa.eu",
                source_type="regulatory",
                priority=3,
                max_results_per_query=4
            )
        ],
        
        extraction_mode="full",
        batch_size=3,
        quality_threshold=0.8
    )
    
    print(f"✅ Custom configuration created")
    print(f"Title: {custom_config.title}")
    print(f"Sources: {len(custom_config.sources)}")
    print(f"Keywords: {len(custom_config.primary_keywords)}")
    print(f"Expected URLs: {custom_config.get_total_expected_urls()}")
    
    # Test custom workflow
    custom_workflow = MarketIntelligenceWorkflow(custom_config)
    custom_api_calls = custom_workflow.calculate_api_calls()
    
    print(f"\n🔧 Custom API Estimates:")
    print(f"SERP calls: {custom_api_calls['serp_calls']}")
    print(f"Perplexity calls: {custom_api_calls['perplexity_calls']}")
    print(f"Total calls: {custom_api_calls['total_calls']}")
    
    return custom_config, custom_workflow


def generate_sample_output():
    """Generate sample output structure"""
    print(f"\n📄 SAMPLE OUTPUT STRUCTURE")
    print("=" * 60)
    
    sample_output = {
        "report_metadata": {
            "request_id": "sema_demo_20241201_123456",
            "title": "Semaglutide and Tirzepatide Market Intelligence",
            "objective": "Monitor regulatory, clinical, and academic market developments",
            "priority": "High",
            "created_by": "user-uuid-here",
            "generated_at": datetime.utcnow().isoformat(),
            "time_range": {
                "start": "2024-01-01T00:00:00",
                "end": "2025-12-31T23:59:59"
            }
        },
        
        "execution_summary": {
            "sources_processed": 3,
            "successful_sources": 3,
            "failed_sources": 0,
            "total_urls_discovered": 15,
            "total_content_extracted": 12,
            "overall_success_rate": 80.0,
            "unique_content_items": 11
        },
        
        "intelligence_data": {
            "regulatory_content": {
                "source": "FDA",
                "count": 4,
                "items": ["Sample FDA content items..."]
            },
            "clinical_content": {
                "source": "ClinicalTrials.gov",
                "count": 3,
                "items": ["Sample clinical trial data..."]
            },
            "academic_content": {
                "source": "NIH", 
                "count": 4,
                "items": ["Sample academic research..."]
            }
        },
        
        "structured_outputs": [
            {
                "source": "FDA",
                "url": "https://www.fda.gov/drug/wegovy/announcement",
                "summary": "FDA announces new guidance for semaglutide...",
                "category": "regulatory",
                "title": "FDA Semaglutide Guidance Update",
                "extraction_confidence": 0.85,
                "word_count": 1250
            },
            {
                "source": "ClinicalTrials.gov",
                "url": "https://clinicaltrials.gov/ct2/show/NCT12345678",
                "summary": "Phase III clinical trial of tirzepatide...",
                "category": "clinical", 
                "title": "Tirzepatide Efficacy Study",
                "extraction_confidence": 0.92,
                "word_count": 890
            }
        ],
        
        "keywords_used": [
            "semaglutide", "tirzepatide", "wegovy", "obesity drug",
            "weight loss medication", "GLP-1 receptor agonist",
            "diabetes treatment", "clinical trials obesity"
        ],
        
        "storage_info": {
            "report_path": "market_intelligence/sema_demo_20241201_123456/final_report.json",
            "raw_data_path": "market_intelligence/sema_demo_20241201_123456/raw_data.json"
        }
    }
    
    print("✅ Sample output structure generated")
    print(f"Report sections: {len(sample_output)} main sections")
    print(f"Structured outputs: {len(sample_output['structured_outputs'])} examples")
    
    # Save sample output
    with open("sample_semaglutide_report.json", "w") as f:
        json.dump(sample_output, f, indent=2)
    
    print(f"💾 Sample report saved to: sample_semaglutide_report.json")
    
    return sample_output


def display_workflow_summary():
    """Display comprehensive workflow summary"""
    print(f"\n📊 COMPREHENSIVE WORKFLOW SUMMARY")
    print("=" * 60)
    
    print("""
🎯 WORKFLOW OBJECTIVES:
• Monitor Semaglutide (Wegovy) regulatory developments
• Track Tirzepatide clinical trial progress  
• Gather academic research insights
• Provide structured intelligence reports

🔄 PROCESSING FLOW:
1. SERP Discovery → 3 API calls (FDA, NIH, ClinicalTrials.gov)
2. URL Extraction → 15 URLs total (5 per source)
3. Content Extraction → 15 Perplexity API calls
4. Aggregation → Combine, deduplicate, categorize
5. Intelligence Report → Structured JSON output

📈 EXPECTED RESULTS:
• Regulatory intelligence from FDA
• Clinical trial data from ClinicalTrials.gov
• Academic research from NIH
• Quality-filtered content (>70% confidence)
• Deduplication by URL
• Categorization by source type

⚙️  CONFIGURATION OPTIONS:
• Customizable keywords and sources
• Adjustable quality thresholds
• Configurable batch processing
• Flexible retry mechanisms
• Extensible source types

🔧 API REQUIREMENTS:
• SERP API key for web search
• Perplexity API key for content extraction
• AWS credentials for storage (optional)
• Database access for state tracking

📊 OUTPUT FORMATS:
• JSON intelligence reports
• Structured content summaries
• Processing statistics
• Quality metrics
• Storage references
""")


def main():
    """Main test execution"""
    print("🧬 SEMAGLUTIDE MARKET INTELLIGENCE WORKFLOW TEST")
    print("Testing configuration and workflow structure\n")
    
    try:
        # Test configuration
        config = test_configuration()
        
        # Test workflow
        workflow, summary = test_workflow()
        
        # Test custom configuration
        custom_config, custom_workflow = test_custom_configuration()
        
        # Generate sample output
        sample_output = generate_sample_output()
        
        # Display summary
        display_workflow_summary()
        
        print(f"\n✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
        print(f"\n📚 NEXT STEPS:")
        print("1. Set up API keys in environment variables")
        print("2. Run the full example: python examples/semaglutide_market_intelligence_example.py")
        print("3. Customize configuration for your specific needs")
        print("4. Integrate with your existing workflows")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 