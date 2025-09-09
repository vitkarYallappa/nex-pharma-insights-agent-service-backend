from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from urllib.parse import urlparse
from pydantic import BaseModel
from .models import SerpResponse, SerpResult
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SerpResponseHandler:
    """Process and validate SERP API responses"""
    
    @staticmethod
    def process_response(data: Dict[str, Any], query: str, engine: str = "google") -> SerpResponse:
        """Process SERP response based on engine type"""
        if engine == "google":
            return SerpResponseHandler._process_google(data, query)
        elif engine == "bing":
            return SerpResponseHandler._process_bing(data, query)
        else:
            return SerpResponseHandler._process_generic(data, query)
    
    @staticmethod
    def _process_google(data: Dict[str, Any], query: str) -> SerpResponse:
        """Process Google SERP response"""
        try:
            organic_results = data.get("organic_results", [])
            results = []
            
            for i, result in enumerate(organic_results):
                processed = SerpResponseHandler._process_single_result(result, i + 1)
                if processed:
                    results.append(processed)
            
            return SerpResponse(
                request_id=SerpResponseHandler._generate_request_id("google"),
                query=query,
                total_results=data.get("search_information", {}).get("total_results", 0),
                results=results,
                search_metadata=SerpResponseHandler._extract_metadata(data)
            )
            
        except Exception as e:
            logger.error(f"Error processing Google response: {str(e)}")
            raise ValueError(f"Invalid Google response: {str(e)}")
    
    @staticmethod
    def _process_bing(data: Dict[str, Any], query: str) -> SerpResponse:
        """Process Bing SERP response"""
        try:
            organic_results = data.get("organic_results", [])
            results = []
            
            for i, result in enumerate(organic_results):
                processed = SerpResponseHandler._process_single_result(result, i + 1)
                if processed:
                    results.append(processed)
            
            return SerpResponse(
                request_id=SerpResponseHandler._generate_request_id("bing"),
                query=query,
                total_results=data.get("search_information", {}).get("total_results", 0),
                results=results,
                search_metadata=SerpResponseHandler._extract_metadata(data)
            )
            
        except Exception as e:
            logger.error(f"Error processing Bing response: {str(e)}")
            raise ValueError(f"Invalid Bing response: {str(e)}")
    
    @staticmethod
    def _process_generic(data: Dict[str, Any], query: str) -> SerpResponse:
        """Process generic SERP response"""
        try:
            organic_results = data.get("organic_results", [])
            results = []
            
            for i, result in enumerate(organic_results):
                processed = SerpResponseHandler._process_single_result(result, i + 1)
                if processed:
                    results.append(processed)
            
            return SerpResponse(
                request_id=SerpResponseHandler._generate_request_id("generic"),
                query=query,
                total_results=len(results),
                results=results,
                search_metadata=SerpResponseHandler._extract_metadata(data)
            )
            
        except Exception as e:
            logger.error(f"Error processing generic response: {str(e)}")
            raise ValueError(f"Invalid generic response: {str(e)}")
    
    @staticmethod
    def _process_single_result(result: Dict[str, Any], position: int) -> Optional[SerpResult]:
        """Process individual search result"""
        try:
            url = result.get("link", "")
            if not SerpResponseHandler._is_valid_url(url):
                return None
            
            return SerpResult(
                title=SerpResponseHandler._clean_text(result.get("title", "")),
                url=url,
                snippet=SerpResponseHandler._clean_text(result.get("snippet", "")),
                position=position,
                domain=SerpResponseHandler._extract_domain(url)
            )
            
        except Exception as e:
            logger.warning(f"Error processing result {position}: {str(e)}")
            return None
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        cleaned = re.sub(r'<[^>]+>', '', text)  # Remove HTML
        return re.sub(r'\s+', ' ', cleaned).strip()  # Normalize whitespace
    
    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc.lower()
        except:
            return ""
    
    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """Validate URL format"""
        try:
            parsed = urlparse(url)
            return bool(parsed.scheme and parsed.netloc)
        except:
            return False
    
    @staticmethod
    def _generate_request_id(source: str) -> str:
        """Generate unique request ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        return f"{source}_serp_{timestamp}"
    
    @staticmethod
    def _extract_metadata(data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract search metadata"""
        return {
            "search_time": data.get("search_metadata", {}).get("total_time_taken"),
            "processed_at": datetime.utcnow().isoformat()
        }

# Legacy response model for backward compatibility
class LegacySerpResponse(BaseModel):
    """Legacy response model for Serp API."""
    status: str
    data: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    error: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
