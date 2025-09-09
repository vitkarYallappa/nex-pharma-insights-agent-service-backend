from ...config.service_factory import ServiceFactory

class Agent1DeduplicationStorage:
    """Storage operations for agent1_deduplication."""
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def save_result(self, request_id: str, data: dict) -> bool:
        """Save processing result."""
        object_key = f"agent1_deduplication/results/{request_id}.json"
        content = json.dumps(data).encode('utf-8')
        
        return await self.storage_client.upload_content(
            content=content,
            object_key=object_key,
            content_type='application/json'
        )
    
    async def load_result(self, request_id: str) -> dict:
        """Load processing result."""
        object_key = f"agent1_deduplication/results/{request_id}.json"
        content = await self.storage_client.get_content(object_key)
        
        if content:
            return json.loads(content.decode('utf-8'))
        return {}
