from typing import Dict, Any
import json

class OpenaiMock:
    """Mock Openai implementation for testing."""
    
    def __init__(self):
        pass
    
    async def call_api(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock API call to Openai."""
        print(f"Mock Openai: Processing request: {json.dumps(data, default=str)}")
        
        # Return mock response
        return {
            "status": "success",
            "data": data,
            "mock": True,
            "message": f"Mock response from Openai"
        }
