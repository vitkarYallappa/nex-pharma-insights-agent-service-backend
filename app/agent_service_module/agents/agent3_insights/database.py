from ...shared.database.base_repository import BaseRepository

class Agent3InsightsRepository(BaseRepository):
    """Database operations for agent3_insights."""
    
    def __init__(self):
        super().__init__(table_name="agent3_insights_data")
    
    def get_table_name(self) -> str:
        return "agent3_insights_data"
    
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
