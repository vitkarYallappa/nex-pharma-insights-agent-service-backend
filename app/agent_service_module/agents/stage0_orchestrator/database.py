from ...shared.database.base_repository import BaseRepository

class Stage0OrchestratorRepository(BaseRepository):
    """Database operations for stage0_orchestrator."""
    
    def __init__(self):
        super().__init__(table_name="stage0_orchestrator_data")
    
    def get_table_name(self) -> str:
        return "stage0_orchestrator_data"
    
    async def save_request(self, request_data: dict) -> bool:
        """Save request data."""
        return await self.create(request_data)
    
    async def get_request(self, request_id: str) -> dict:
        """Get request data."""
        return await self.get_by_id(request_id)
    
    async def update_status(self, request_id: str, status: str) -> bool:
        """Update request status."""
        request_data = await self.get_by_id(request_id)
        if request_data:
            request_data['status'] = status
            return await self.update(request_data)
        return False
