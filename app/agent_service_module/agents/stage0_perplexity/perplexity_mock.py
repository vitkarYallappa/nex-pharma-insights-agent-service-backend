import asyncio
from typing import List, Optional, Dict
from datetime import datetime
from .models import ContentExtractionRequest, PerplexityResponse, ExtractedContent
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityMock:
    """Mock Perplexity API for testing"""
    
    def __init__(self):
        self.mock_content = self._generate_mock_content()
    
    async def extract_content(self, request: ContentExtractionRequest) -> PerplexityResponse:
        """Mock content extraction"""
        await asyncio.sleep(0.2)  # Simulate processing time
        
        logger.info(f"Mock Perplexity extraction for {len(request.urls)} URLs")
        
        extracted_content = []
        successful = 0
        
        for i, url in enumerate(request.urls):
            # Simulate some failures
            if i % 5 == 4:  # Fail every 5th URL
                continue
            
            content = self._generate_mock_extraction(url, i)
            extracted_content.append(content)
            successful += 1
        
        failed = len(request.urls) - successful
        
        return PerplexityResponse(
            request_id=request.request_id,
            total_urls=len(request.urls),
            successful_extractions=successful,
            failed_extractions=failed,
            extracted_content=extracted_content,
            processing_metadata={"source": "mock", "mode": request.extraction_mode}
        )
    
    def _generate_mock_content(self) -> Dict[str, str]:
        """Generate realistic mock content templates"""
        return {
            "pharmaceutical": "This article discusses the latest developments in pharmaceutical AI regulation. The FDA has announced new guidelines for AI-powered drug discovery tools, emphasizing the need for transparency and validation in machine learning models used for therapeutic development.",
            "regulation": "New regulatory frameworks are being established to govern the use of artificial intelligence in healthcare and pharmaceutical industries. These regulations aim to ensure patient safety while promoting innovation in AI-driven medical technologies.",
            "ai_drug_discovery": "Artificial intelligence is revolutionizing drug discovery processes, enabling researchers to identify potential therapeutic compounds faster than traditional methods. Machine learning algorithms can predict molecular behavior and optimize drug candidates for clinical trials.",
            "compliance": "Pharmaceutical companies must now comply with updated AI governance requirements that mandate documentation of algorithmic decision-making processes, data validation procedures, and bias mitigation strategies in AI-powered research tools."
        }
    
    def _generate_mock_extraction(self, url: str, index: int) -> ExtractedContent:
        """Generate mock extraction for single URL"""
        # Select content based on URL domain or index
        url_str = str(url).lower()
        
        if "fda.gov" in url_str:
            content_key = "regulation"
            title = "FDA AI Regulation Guidelines"
            confidence = 0.9
        elif "pharma" in url_str:
            content_key = "pharmaceutical"
            title = "Pharmaceutical AI Development Standards"
            confidence = 0.85
        elif "ai" in url_str or "drug" in url_str:
            content_key = "ai_drug_discovery"
            title = "AI in Drug Discovery: Latest Advances"
            confidence = 0.8
        else:
            content_key = "compliance"
            title = "AI Compliance Requirements for Healthcare"
            confidence = 0.75
        
        content = self.mock_content.get(content_key, self.mock_content["pharmaceutical"])
        
        return ExtractedContent(
            url=url,
            title=f"{title} - Analysis {index + 1}",
            content=content,
            metadata={
                "extraction_method": "mock",
                "mock_category": content_key,
                "generated_at": datetime.utcnow().isoformat()
            },
            author="Mock Author",
            published_date=datetime.utcnow(),
            word_count=len(content.split()),
            language="en",
            content_type="article",
            extraction_confidence=confidence
        )
