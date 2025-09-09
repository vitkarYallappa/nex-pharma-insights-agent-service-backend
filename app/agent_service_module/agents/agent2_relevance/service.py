from ...config.service_factory import ServiceFactory
from .models import Agent2RelevanceRequest, Agent2RelevanceResponse

class Agent2RelevanceService:
    """Main service for agent2_relevance."""
    
    def __init__(self):
        # Factory automatically provides correct implementation based on environment
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process(self, request: Agent2RelevanceRequest) -> Agent2RelevanceResponse:
        """Process the agent2_relevance request."""
        # Implementation will be added based on specific agent requirements
        result = {"message": "Processing agent2_relevance request", "request_id": request.request_id}
        
        return Agent2RelevanceResponse(
            request_id=request.request_id,
            result=result,
            status="completed"
        )
