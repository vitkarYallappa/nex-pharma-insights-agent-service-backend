from ...config.service_factory import ServiceFactory
from .models import Stage0OrchestratorRequest, Stage0OrchestratorResponse

class Stage0OrchestratorService:
    """Main service for stage0_orchestrator."""
    
    def __init__(self):
        # Factory automatically provides correct implementation based on environment
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process(self, request: Stage0OrchestratorRequest) -> Stage0OrchestratorResponse:
        """Process the stage0_orchestrator request."""
        # Implementation will be added based on specific agent requirements
        result = {"message": "Processing stage0_orchestrator request", "request_id": request.request_id}
        
        return Stage0OrchestratorResponse(
            request_id=request.request_id,
            result=result,
            status="completed"
        )
