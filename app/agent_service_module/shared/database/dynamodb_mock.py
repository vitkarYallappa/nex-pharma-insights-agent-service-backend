from typing import Dict, Any, List, Optional
import json
from datetime import datetime

class DynamoDBMock:
    """Mock DynamoDB client for testing."""
    
    def __init__(self):
        self.tables = {}
    
    async def put_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """Mock put item operation."""
        if table_name not in self.tables:
            self.tables[table_name] = []
        
        # Add timestamp for mock data
        item['_mock_timestamp'] = datetime.utcnow().isoformat()
        self.tables[table_name].append(item.copy())
        
        print(f"Mock DynamoDB: Put item in {table_name}: {json.dumps(item, default=str)}")
        return True
    
    async def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mock get item operation."""
        if table_name not in self.tables:
            return None
        
        # Simple key matching (in real implementation, this would be more sophisticated)
        for item in self.tables[table_name]:
            match = True
            for k, v in key.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                print(f"Mock DynamoDB: Found item in {table_name}")
                return item.copy()
        
        print(f"Mock DynamoDB: Item not found in {table_name}")
        return None
    
    async def query(self, table_name: str, key_condition: str, **kwargs) -> List[Dict[str, Any]]:
        """Mock query operation."""
        if table_name not in self.tables:
            return []
        
        # Simple mock - return all items (in real implementation, would parse key_condition)
        items = self.tables[table_name].copy()
        print(f"Mock DynamoDB: Query returned {len(items)} items from {table_name}")
        return items
    
    async def scan(self, table_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Mock scan operation."""
        if table_name not in self.tables:
            return []
        
        items = self.tables[table_name].copy()
        print(f"Mock DynamoDB: Scan returned {len(items)} items from {table_name}")
        return items
    
    async def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        """Mock delete item operation."""
        if table_name not in self.tables:
            return False
        
        # Find and remove item
        for i, item in enumerate(self.tables[table_name]):
            match = True
            for k, v in key.items():
                if item.get(k) != v:
                    match = False
                    break
            if match:
                del self.tables[table_name][i]
                print(f"Mock DynamoDB: Deleted item from {table_name}")
                return True
        
        print(f"Mock DynamoDB: Item not found for deletion in {table_name}")
        return False
    
    def clear_table(self, table_name: str):
        """Clear all items from a mock table (testing utility)."""
        if table_name in self.tables:
            self.tables[table_name] = []
            print(f"Mock DynamoDB: Cleared table {table_name}")
    
    def get_table_items(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all items from a mock table (testing utility)."""
        return self.tables.get(table_name, []).copy() 