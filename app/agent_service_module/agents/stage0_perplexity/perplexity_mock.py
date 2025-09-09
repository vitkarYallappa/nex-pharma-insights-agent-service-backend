from typing import Dict, Any
import json

class PerplexityMock:
    """Mock Perplexity implementation for testing."""
    
    def __init__(self):
        pass
    
    async def call_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock API call to Perplexity."""
        print(f"Mock Perplexity: Processing request: {json.dumps(data, default=str)}")
        
        # Return mock response
        return {
            "status": "success",
            "data": data,
            "mock": True,
            "message": f"Mock response from Perplexity"
        }
