#!/usr/bin/env python3
"""
Test script to demonstrate SERP URL generation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agent_service_module.agents.stage0_serp.serp_api import SerpAPI
from app.agent_service_module.agents.stage0_serp.serp_query_builder import build_query

def test_serp_url_generation():
    """Test SERP URL generation with the exact format requested"""
    
    # Initialize SERP API (you'll need to set SERP_API_KEY in settings)
    serp_api = SerpAPI()
    
    # Test data matching your requirements
    keywords = ["semaglutide", "tirzepatide", "wegovy", "ozempic", "mounjaro"]
    source = {"name": "fda.gov", "type": "domain", "url": "https://fda.gov"}
    
    print("🧪 Testing SERP URL Generation")
    print("=" * 50)
    
    # Test 1: Single keyword (like your example)
    print("\n1️⃣ Single keyword test:")
    single_keyword_url = serp_api.build_serp_url(
        keywords=["semaglutide"],
        source=source,
        date_filter="cdr:1"
    )
    print(f"URL: {single_keyword_url}")
    
    # Test 2: Multiple keywords
    print("\n2️⃣ Multiple keywords test:")
    multi_keyword_url = serp_api.build_serp_url(
        keywords=keywords,
        source=source,
        date_filter="cdr:1"
    )
    print(f"URL: {multi_keyword_url}")
    
    # Test 3: Query builder output
    print("\n3️⃣ Query builder output:")
    query_data = build_query(
        keywords=["semaglutide"],
        sources=[source],
        date_filter="cdr:1"
    )
    print(f"Generated query: {query_data['query']}")
    print(f"Parameters: {query_data['params']}")
    
    # Test 4: Expected format comparison
    print("\n4️⃣ Format comparison:")
    expected_format = 'https://serpapi.com/search.json?engine=google&q=("semaglutide") (site:fda.gov)&tbs=cdr:1&api_key=YOUR_API_KEY'
    print(f"Expected format: {expected_format}")
    print(f"Generated format: {single_keyword_url}")
    
    print("\n✅ URL generation test completed!")

if __name__ == "__main__":
    test_serp_url_generation() 