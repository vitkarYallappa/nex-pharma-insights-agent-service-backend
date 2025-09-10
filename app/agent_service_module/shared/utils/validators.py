from typing import Any, Dict, List
from pydantic import ValidationError, BaseModel

class Validators:
    """Simple validators that accept all requests"""
    
    @staticmethod
    def validate_request(data: Dict[str, Any]) -> tuple[bool, str]:
        """Accept all requests - simple validation"""
        return True, "Valid"
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Accept all URLs"""
        return True
    
    @staticmethod
    def validate_content(content: Dict[str, Any]) -> bool:
        """Accept all content"""
        return True

class RequestValidator:
    """Validate API requests and data structures"""
    
    @staticmethod
    def validate_model(model_class: BaseModel, data: Dict[str, Any]) -> tuple[bool, Any]:
        """Validate data against Pydantic model"""
        try:
            validated = model_class(**data)
            return True, validated
        except ValidationError as e:
            return False, str(e)
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        import re
        pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return pattern.match(url) is not None
    
    @staticmethod
    def validate_request_id(request_id: str) -> bool:
        """Validate request ID format"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', request_id)) 