from ...config.service_factory import ServiceFactory
from .models import Stage0SerpRequest, Stage0SerpResponse

class Stage0SerpService:
    """Main service for stage0_serp."""
    
    def __init__(self):
        # Factory automatically provides correct implementation based on environment
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process(self, request: Stage0SerpRequest) -> Stage0SerpResponse:
        """Process the stage0_serp request."""
        # Implementation will be added based on specific agent requirements
        result = {"message": "Processing stage0_serp request", "request_id": request.request_id}
        
        return Stage0SerpResponse(
            request_id=request.request_id,
            result=result,
            status="completed"
        )
