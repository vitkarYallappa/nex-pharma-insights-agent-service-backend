from typing import Union
from ...config.service_factory import ServiceFactory
from .dynamodb_client import DynamoDBClient
from .dynamodb_mock import DynamoDBMock

class DatabaseConnection:
    """Database connection manager using factory pattern."""
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self) -> Union[DynamoDBClient, DynamoDBMock]:
        """Get database client (real or mock based on configuration)."""
        if self._client is None:
            self._client = ServiceFactory.get_database_client()
        return self._client
    
    async def put_item(self, table_name: str, item: dict) -> bool:
        """Put an item into database."""
        return await self.client.put_item(table_name, item)
    
    async def get_item(self, table_name: str, key: dict) -> dict:
        """Get an item from database."""
        return await self.client.get_item(table_name, key)
    
    async def query(self, table_name: str, key_condition: str, **kwargs) -> list:
        """Query items from database."""
        return await self.client.query(table_name, key_condition, **kwargs)
    
    async def scan(self, table_name: str, **kwargs) -> list:
        """Scan items from database."""
        return await self.client.scan(table_name, **kwargs)
    
    async def delete_item(self, table_name: str, key: dict) -> bool:
        """Delete an item from database."""
        return await self.client.delete_item(table_name, key) 