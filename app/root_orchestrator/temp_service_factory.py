"""
Temporary Service Factory for Root Orchestrator

This is a minimal service factory that provides the basic services needed
by the Root Orchestrator without depending on the existing configuration
system that has Pydantic compatibility issues.
"""

from typing import Any, Dict, Optional
import os


class MockDatabaseClient:
    """Mock database client for development/testing"""
    
    def __init__(self):
        self._data: Dict[str, Dict[str, Any]] = {}
    
    async def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get an item from the mock database"""
        table = self._data.get(table_name, {})
        item_key = str(key.get("request_id", ""))
        return table.get(item_key)
    
    async def save_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """Save an item to the mock database"""
        try:
            if table_name not in self._data:
                self._data[table_name] = {}
            
            item_key = str(item.get("request_id", ""))
            self._data[table_name][item_key] = item.copy()
            return True
        except Exception:
            return False
    
    async def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        """Delete an item from the mock database"""
        try:
            table = self._data.get(table_name, {})
            item_key = str(key.get("request_id", ""))
            if item_key in table:
                del table[item_key]
                return True
            return False
        except Exception:
            return False
    
    async def query_items(self, table_name: str, query_params: Dict[str, Any], 
                         limit: Optional[int] = None, offset: Optional[int] = None) -> list:
        """Query items from the mock database"""
        try:
            table = self._data.get(table_name, {})
            items = list(table.values())
            
            # Apply basic filtering
            if query_params:
                filtered_items = []
                for item in items:
                    match = True
                    for key, value in query_params.items():
                        if key in item and item[key] != value:
                            match = False
                            break
                    if match:
                        filtered_items.append(item)
                items = filtered_items
            
            # Apply pagination
            if offset:
                items = items[offset:]
            if limit:
                items = items[:limit]
            
            return items
        except Exception:
            return []


class MockStorageClient:
    """Mock storage client for development/testing"""
    
    def __init__(self):
        self._storage: Dict[str, Any] = {}
    
    async def save_json(self, key: str, data: Any) -> bool:
        """Save JSON data to mock storage"""
        try:
            self._storage[key] = data
            return True
        except Exception:
            return False
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON data from mock storage"""
        return self._storage.get(key)
    
    async def delete(self, key: str) -> bool:
        """Delete data from mock storage"""
        try:
            if key in self._storage:
                del self._storage[key]
                return True
            return False
        except Exception:
            return False


class TempServiceFactory:
    """
    Temporary service factory for Root Orchestrator.
    
    This provides basic mock services for development and testing
    without depending on the existing configuration system.
    """
    
    _database_client: Optional[MockDatabaseClient] = None
    _storage_client: Optional[MockStorageClient] = None
    
    @classmethod
    def get_database_client(cls) -> MockDatabaseClient:
        """Get database client instance"""
        if cls._database_client is None:
            cls._database_client = MockDatabaseClient()
        return cls._database_client
    
    @classmethod
    def get_storage_client(cls) -> MockStorageClient:
        """Get storage client instance"""
        if cls._storage_client is None:
            cls._storage_client = MockStorageClient()
        return cls._storage_client
    
    @classmethod
    def reset(cls):
        """Reset all service instances (for testing)"""
        cls._database_client = None
        cls._storage_client = None


# For compatibility with existing imports
ServiceFactory = TempServiceFactory 