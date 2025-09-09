from typing import Dict, Any
import json

class EmbeddingMock:
    """Mock Embedding implementation for testing."""
    
    def __init__(self):
        pass
    
    async def call_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock API call to Embedding."""
        print(f"Mock Embedding: Processing request: {json.dumps(data, default=str)}")
        
        # Return mock response
        return {
            "status": "success",
            "data": data,
            "mock": True,
            "message": f"Mock response from Embedding"
        }
