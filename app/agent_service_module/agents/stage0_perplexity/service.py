from ...config.service_factory import ServiceFactory
from .models import Stage0PerplexityRequest, Stage0PerplexityResponse

class Stage0PerplexityService:
    """Main service for stage0_perplexity."""
    
    def __init__(self):
        # Factory automatically provides correct implementation based on environment
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process(self, request: Stage0PerplexityRequest) -> Stage0PerplexityResponse:
        """Process the stage0_perplexity request."""
        # Implementation will be added based on specific agent requirements
        result = {"message": "Processing stage0_perplexity request", "request_id": request.request_id}
        
        return Stage0PerplexityResponse(
            request_id=request.request_id,
            result=result,
            status="completed"
        )
