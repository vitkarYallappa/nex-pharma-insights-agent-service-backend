import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from .models import SerpRequest, SerpResponse, SerpResult
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SerpMock:
    """Mock SERP API for testing"""
    
    def __init__(self):
        self.mock_results = self._generate_mock_results()
    
    async def search(self, request: SerpRequest) -> SerpResponse:
        """Mock search with predefined results"""
        await asyncio.sleep(0.1)  # Simulate latency
        
        logger.info(f"Mock SERP search for: {request.query}")
        
        filtered_results = self._filter_by_query(request.query, request.num_results)
        
        return SerpResponse(
            request_id=f"mock_serp_{int(datetime.utcnow().timestamp())}",
            query=request.query,
            total_results=len(filtered_results) * 10,
            results=filtered_results,
            search_metadata={"source": "mock", "engine": "mock_google"}
        )
    
    def _generate_mock_results(self) -> List[SerpResult]:
        """Generate realistic mock results"""
        return [
            SerpResult(
                title="FDA AI Regulation Guidelines 2025",
                url="https://fda.gov/ai-regulation-guidelines-2025",
                snippet="New FDA guidelines for AI in pharmaceutical industry...",
                position=1,
                domain="fda.gov"
            ),
            SerpResult(
                title="Pharmaceutical AI Compliance Requirements",
                url="https://pharmareview.com/ai-compliance-2025",
                snippet="Updated compliance requirements for AI in drug development...",
                position=2,
                domain="pharmareview.com"
            ),
            SerpResult(
                title="AI Drug Discovery Regulatory Landscape",
                url="https://biotech.news/ai-drug-discovery-regulation",
                snippet="Analysis of regulatory changes affecting AI drug discovery...",
                position=3,
                domain="biotech.news"
            ),
            SerpResult(
                title="Clinical Trial AI Implementation Guide",
                url="https://clinicaltrials.gov/ai-implementation-guide",
                snippet="Comprehensive guide for implementing AI in clinical trials...",
                position=4,
                domain="clinicaltrials.gov"
            ),
            SerpResult(
                title="Pharmaceutical Data Privacy Regulations",
                url="https://pharmalaw.com/data-privacy-regulations",
                snippet="Latest updates on data privacy in pharmaceutical research...",
                position=5,
                domain="pharmalaw.com"
            ),
            SerpResult(
                title="AI in Drug Manufacturing Standards",
                url="https://manufacturing.pharma/ai-standards",
                snippet="Industry standards for AI implementation in drug manufacturing...",
                position=6,
                domain="manufacturing.pharma"
            )
        ]
    
    def _filter_by_query(self, query: str, num_results: int) -> List[SerpResult]:
        """Filter mock results by query relevance"""
        query_words = query.lower().split()
        relevant_results = []
        
        for result in self.mock_results:
            title_lower = result.title.lower()
            snippet_lower = result.snippet.lower()
            
            if any(word in title_lower or word in snippet_lower for word in query_words):
                relevant_results.append(result)
        
        # If no relevant results, return first few results
        if not relevant_results:
            relevant_results = self.mock_results[:num_results]
        
        return relevant_results[:num_results]

    # Legacy method for backward compatibility
    async def call_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock API call to Serp."""
        print(f"Mock Serp: Processing request: {json.dumps(data, default=str)}")
        
        try:
            # Convert legacy format to new format
            request = SerpRequest(
                query=data.get("query", "pharmaceutical AI"),
                num_results=data.get("num_results", 10)
            )
            response = await self.search(request)
            
            return {
                "status": "success",
                "data": response.dict(),
                "mock": True,
                "message": f"Mock response from Serp"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "mock": True
            }
