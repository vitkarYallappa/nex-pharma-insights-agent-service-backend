from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from .connection import DatabaseConnection

class BaseRepository(ABC):
    """Base repository class for database operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = DatabaseConnection()
    
    async def create(self, item: Dict[str, Any]) -> bool:
        """Create a new item."""
        return await self.db.put_item(self.table_name, item)
    
    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item by ID."""
        return await self.db.get_item(self.table_name, {"id": item_id})
    
    async def update(self, item: Dict[str, Any]) -> bool:
        """Update an existing item."""
        return await self.db.put_item(self.table_name, item)
    
    async def delete(self, item_id: str) -> bool:
        """Delete an item by ID."""
        return await self.db.delete_item(self.table_name, {"id": item_id})
    
    async def list_all(self) -> List[Dict[str, Any]]:
        """List all items."""
        return await self.db.scan(self.table_name)
    
    @abstractmethod
    def get_table_name(self) -> str:
        """Get the table name for this repository."""
        pass 