#!/usr/bin/env python3
"""
Semaglutide and Tirzepatide Market Intelligence Example

This example demonstrates the complete workflow for monitoring regulatory, clinical, 
and academic developments for Wegovy (Semaglutide) and Tirzepatide therapies.

Workflow Overview:
1. Stage 1: SerpAPI Discovery (3 calls - one per source)
2. Stage 2: URL Extraction (15 URLs total - 5 per source)  
3. Stage 3: Perplexity Summarization (15 calls - one per URL)
4. Stage 4: Aggregation and Intelligence Report Generation

Total API Calls: 18 (3 SERP + 15 Perplexity)
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Import the market intelligence components
from app.agent_service_module.services.market_intelligence_service import MarketIntelligenceService
from app.agent_service_module.config.market_intelligence_config import (
    MarketIntelligenceConfig, 
    MarketIntelligenceSource,
    DEFAULT_SEMAGLUTIDE_CONFIG
)


async def run_semaglutide_intelligence_workflow():
    """Execute the complete Semaglutide/Tirzepatide market intelligence workflow"""
    
    print("=" * 80)
    print("SEMAGLUTIDE AND TIRZEPATIDE MARKET INTELLIGENCE WORKFLOW")
    print("=" * 80)
    
    # Initialize the market intelligence service
    service = MarketIntelligenceService()
    
    # Display configuration summary
    config_summary = service.get_configuration_summary()
    print("\n📋 WORKFLOW CONFIGURATION:")
    print(f"Title: {config_summary['workflow_config']['title']}")
    print(f"Objective: {config_summary['workflow_config']['objective']}")
    print(f"Priority: {config_summary['workflow_config']['priority']}")
    print(f"Time Range: {config_summary['workflow_config']['time_range']['start']} → {config_summary['workflow_config']['time_range']['end']}")
    print(f"Sources: {config_summary['workflow_config']['sources_count']}")
    print(f"Keywords: {config_summary['workflow_config']['keywords_count']}")
    print(f"Expected URLs: {config_summary['workflow_config']['expected_urls']}")
    
    # Display API call estimates
    api_estimates = config_summary['api_call_estimates']
    print(f"\n🔧 API CALL ESTIMATES:")
    print(f"SERP API calls: {api_estimates['serp_calls']}")
    print(f"Perplexity API calls: {api_estimates['perplexity_calls']}")
    print(f"Total API calls: {api_estimates['total_calls']}")
    
    # Display search requests that will be executed
    print(f"\n🔍 SEARCH REQUESTS TO BE EXECUTED:")
    for i, request in enumerate(config_summary['search_requests'], 1):
        print(f"{i}. {request['source_name']} ({request['source_type']})")
        print(f"   Query: {request['query'][:100]}...")
        print(f"   Max Results: {request['num_results']}")
        print(f"   Priority: {request['priority']}")
    
    # Execute the workflow
    print(f"\n🚀 EXECUTING WORKFLOW...")
    print("This will perform the following stages:")
    print("1. SERP Discovery: Search each source for relevant content")
    print("2. URL Extraction: Extract URLs from search results")
    print("3. Content Extraction: Use Perplexity to summarize each URL")
    print("4. Aggregation: Combine and analyze all results")
    
    try:
        # Execute the complete workflow
        start_time = datetime.utcnow()
        result = await service.execute_semaglutide_intelligence(request_id="sema_demo_2024")
        end_time = datetime.utcnow()
        
        processing_time = (end_time - start_time).total_seconds()
        
        print(f"\n✅ WORKFLOW COMPLETED in {processing_time:.2f} seconds")
        
        # Display execution summary
        execution_summary = result['execution_summary']
        print(f"\n📊 EXECUTION SUMMARY:")
        print(f"Sources Processed: {execution_summary['sources_processed']}")
        print(f"Successful Sources: {execution_summary['successful_sources']}")
        print(f"Failed Sources: {execution_summary['failed_sources']}")
        print(f"URLs Discovered: {execution_summary['total_urls_discovered']}")
        print(f"Content Extracted: {execution_summary['total_content_extracted']}")
        print(f"Success Rate: {execution_summary['overall_success_rate']:.1f}%")
        print(f"Unique Content Items: {execution_summary['unique_content_items']}")
        
        # Display intelligence data breakdown
        intelligence_data = result['intelligence_data']
        print(f"\n🧠 INTELLIGENCE DATA BREAKDOWN:")
        print(f"Regulatory Content (FDA): {intelligence_data['regulatory_content']['count']} items")
        print(f"Clinical Content (ClinicalTrials.gov): {intelligence_data['clinical_content']['count']} items")
        print(f"Academic Content (NIH): {intelligence_data['academic_content']['count']} items")
        
        # Display quality metrics
        quality_metrics = result['content_analysis']['quality_metrics']
        print(f"\n📈 CONTENT QUALITY METRICS:")
        print(f"Total Items: {quality_metrics['total_items']}")
        print(f"High Quality Items: {quality_metrics['high_quality_items']}")
        print(f"Unique Items: {quality_metrics['unique_items']}")
        print(f"Quality Rate: {quality_metrics['quality_rate']:.1f}%")
        
        # Display structured output examples
        if result['structured_outputs']:
            print(f"\n📄 STRUCTURED OUTPUT EXAMPLES:")
            for i, item in enumerate(result['structured_outputs'][:3], 1):
                print(f"\n{i}. {item['title']}")
                print(f"   Source: {item['source']}")
                print(f"   Category: {item['category']}")
                print(f"   URL: {item['url']}")
                print(f"   Confidence: {item['extraction_confidence']:.2f}")
                print(f"   Word Count: {item['word_count']}")
                print(f"   Summary: {item['summary'][:200]}...")
        
        # Display processing details per source
        print(f"\n🔍 PROCESSING DETAILS BY SOURCE:")
        for source_name, details in result['processing_details'].items():
            if details['status'] == 'completed':
                print(f"\n✅ {source_name}:")
                print(f"   URLs Found: {details['urls_found']}")
                print(f"   Content Extracted: {details['content_extracted']}")
                print(f"   Processing Time: {details['processing_time']:.2f}s")
                print(f"   Success Rate: {details['success_rate']:.1f}%")
            else:
                print(f"\n❌ {source_name}: {details['error']}")
        
        # Save results to file
        output_file = f"semaglutide_intelligence_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        
        print(f"\n💾 Full report saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ WORKFLOW FAILED: {str(e)}")
        raise


async def demonstrate_custom_configuration():
    """Demonstrate how to create a custom configuration for different use cases"""
    
    print("\n" + "=" * 80)
    print("CUSTOM CONFIGURATION EXAMPLE")
    print("=" * 80)
    
    # Create custom configuration for expanded monitoring
    custom_config = MarketIntelligenceConfig(
        title="Extended Semaglutide Market Intelligence",
        objective="Comprehensive monitoring including European regulatory bodies",
        created_by="analyst-team-lead",
        
        # Add additional keywords
        primary_keywords=[
            "semaglutide", "tirzepatide", "wegovy", "ozempic", "mounjaro",
            "obesity drug", "weight loss medication", "GLP-1 receptor agonist",
            "diabetes treatment", "clinical trials obesity", "bariatric medicine",
            "metabolic syndrome", "insulin resistance"
        ],
        
        # Add additional sources
        sources=[
            MarketIntelligenceSource(
                name="FDA",
                base_url="https://www.fda.gov",
                source_type="regulatory",
                priority=1,
                max_results_per_query=7
            ),
            MarketIntelligenceSource(
                name="NIH", 
                base_url="https://www.nih.gov",
                source_type="academic",
                priority=2,
                max_results_per_query=7
            ),
            MarketIntelligenceSource(
                name="ClinicalTrials.gov",
                base_url="https://clinicaltrials.gov",
                source_type="clinical", 
                priority=1,
                max_results_per_query=7
            ),
            MarketIntelligenceSource(
                name="EMA",
                base_url="https://www.ema.europa.eu",
                source_type="regulatory",
                priority=2,
                max_results_per_query=5
            ),
            MarketIntelligenceSource(
                name="PubMed",
                base_url="https://pubmed.ncbi.nlm.nih.gov",
                source_type="academic",
                priority=1,
                max_results_per_query=8
            )
        ],
        
        # Enhanced processing parameters
        extraction_mode="full",
        batch_size=3,
        quality_threshold=0.8,
        max_retries=3
    )
    
    # Initialize service with custom config
    custom_service = MarketIntelligenceService(custom_config)
    
    # Display custom configuration
    custom_summary = custom_service.get_configuration_summary()
    print(f"\n📋 CUSTOM CONFIGURATION:")
    print(f"Title: {custom_summary['workflow_config']['title']}")
    print(f"Sources: {custom_summary['workflow_config']['sources_count']}")
    print(f"Keywords: {custom_summary['workflow_config']['keywords_count']}")
    print(f"Expected URLs: {custom_summary['workflow_config']['expected_urls']}")
    print(f"Total API Calls: {custom_summary['api_call_estimates']['total_calls']}")
    
    print(f"\n🔍 CUSTOM SEARCH REQUESTS:")
    for i, request in enumerate(custom_summary['search_requests'], 1):
        print(f"{i}. {request['source_name']} - {request['num_results']} results")
    
    print(f"\n⚙️  PROCESSING PARAMETERS:")
    params = custom_summary['processing_parameters']
    print(f"Extraction Mode: {params['extraction_mode']}")
    print(f"Batch Size: {params['batch_size']}")
    print(f"Quality Threshold: {params['quality_threshold']}")
    print(f"Max Retries: {params['max_retries']}")


async def monitor_workflow_status():
    """Demonstrate how to monitor workflow status during execution"""
    
    print("\n" + "=" * 80)
    print("WORKFLOW STATUS MONITORING EXAMPLE")
    print("=" * 80)
    
    service = MarketIntelligenceService()
    
    # Start workflow in background
    request_id = "sema_status_demo_2024"
    
    print(f"🚀 Starting workflow with ID: {request_id}")
    
    # In a real scenario, you would start the workflow and then monitor it
    # For this example, we'll show how the status monitoring would work
    
    print(f"\n📊 STATUS MONITORING:")
    print("In a real implementation, you would:")
    print("1. Start the workflow asynchronously")
    print("2. Poll the status periodically")
    print("3. Display progress updates")
    print("4. Handle completion or failure")
    
    # Example status structure
    example_status = {
        "request_id": request_id,
        "status": "extracting",
        "current_stage": "content_extraction",
        "progress_percentage": 65.0,
        "urls_found": 15,
        "content_extracted": 10,
        "errors": [],
        "warnings": ["Some URLs returned low-quality content"]
    }
    
    print(f"\n📈 EXAMPLE STATUS RESPONSE:")
    for key, value in example_status.items():
        print(f"{key}: {value}")


def display_workflow_architecture():
    """Display the complete workflow architecture and data flow"""
    
    print("\n" + "=" * 80)
    print("WORKFLOW ARCHITECTURE AND DATA FLOW")
    print("=" * 80)
    
    print("""
🏗️  ARCHITECTURE OVERVIEW:

┌─────────────────────────────────────────────────────────────────────────────┐
│                    SEMAGLUTIDE MARKET INTELLIGENCE WORKFLOW                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  📋 Configuration Layer                                                     │
│  ├── MarketIntelligenceConfig (keywords, sources, parameters)              │
│  ├── MarketIntelligenceWorkflow (request generation, API estimation)       │
│  └── MarketIntelligenceService (orchestration, aggregation)                │
│                                                                             │
│  🔄 Processing Stages                                                       │
│  ├── Stage 1: SERP Discovery                                               │
│  │   ├── FDA: site:fda.gov + keywords → 5 URLs                            │
│  │   ├── NIH: site:nih.gov + keywords → 5 URLs                            │
│  │   └── ClinicalTrials: site:clinicaltrials.gov + keywords → 5 URLs      │
│  │                                                                         │
│  ├── Stage 2: Content Extraction                                           │
│  │   ├── Perplexity API: URL 1 → Summary                                  │
│  │   ├── Perplexity API: URL 2 → Summary                                  │
│  │   └── ... (15 total extractions)                                       │
│  │                                                                         │
│  ├── Stage 3: Aggregation                                                  │
│  │   ├── Combine results by source type                                   │
│  │   ├── Filter high-quality content                                      │
│  │   ├── Deduplicate by URL                                               │
│  │   └── Generate quality metrics                                         │
│  │                                                                         │
│  └── Stage 4: Intelligence Report                                          │
│      ├── Structured outputs by category                                    │
│      ├── Processing statistics                                             │
│      ├── Quality analysis                                                  │
│      └── Storage paths                                                     │
│                                                                             │
│  💾 Storage Layer                                                           │
│  ├── Raw search results                                                    │
│  ├── Extracted content                                                     │
│  ├── Aggregated intelligence                                               │
│  └── Final reports                                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

📊 DATA FLOW:

Keywords → SERP Queries → URLs → Content Extraction → Aggregation → Intelligence Report

🔢 API CALL BREAKDOWN:
• SERP API: 3 calls (1 per source)
• Perplexity API: 15 calls (1 per URL)
• Total: 18 API calls

📈 EXPECTED OUTPUTS:
• Regulatory intelligence from FDA
• Clinical trial data from ClinicalTrials.gov  
• Academic research from NIH
• Structured JSON reports
• Quality-filtered content
• Deduplication and categorization
""")


async def main():
    """Main execution function"""
    
    print("🧬 SEMAGLUTIDE AND TIRZEPATIDE MARKET INTELLIGENCE")
    print("Comprehensive workflow demonstration\n")
    
    try:
        # 1. Display architecture
        display_workflow_architecture()
        
        # 2. Run the main workflow
        await run_semaglutide_intelligence_workflow()
        
        # 3. Demonstrate custom configuration
        await demonstrate_custom_configuration()
        
        # 4. Show status monitoring
        await monitor_workflow_status()
        
        print("\n" + "=" * 80)
        print("✅ ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("=" * 80)
        
        print(f"\n📚 NEXT STEPS:")
        print("1. Configure your API keys (SERP_API_KEY, PERPLEXITY_API_KEY)")
        print("2. Customize the configuration for your specific needs")
        print("3. Set up scheduled runs for continuous monitoring")
        print("4. Integrate with your existing analysis workflows")
        print("5. Extend with additional sources or processing agents")
        
    except Exception as e:
        print(f"\n❌ DEMONSTRATION FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    # Run the complete demonstration
    asyncio.run(main()) 