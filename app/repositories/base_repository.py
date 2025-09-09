from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type
from botocore.exceptions import ClientError
from app.core.database import db_connection
from app.core.exceptions import DatabaseException, ItemNotFoundException
import logging

logger = logging.getLogger(__name__)


class BaseRepository(ABC):
    """Base repository class for DynamoDB operations."""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
        self.table = db_connection.resource.Table(table_name)
    
    async def get_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get item by ID."""
        try:
            response = self.table.get_item(
                Key={'pk': item_id}
            )
            return response.get('Item')
        except ClientError as e:
            logger.error(f"Error getting item {item_id} from {self.table_name}: {e}")
            raise DatabaseException(f"Failed to get item: {e}")
    
    async def scan_all(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scan all items in table."""
        try:
            scan_kwargs = {}
            if limit:
                scan_kwargs['Limit'] = limit
            
            response = self.table.scan(**scan_kwargs)
            items = response.get('Items', [])
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response and (not limit or len(items) < limit):
                scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                if limit:
                    scan_kwargs['Limit'] = limit - len(items)
                
                response = self.table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))
            
            return items
        except ClientError as e:
            logger.error(f"Error scanning {self.table_name}: {e}")
            raise DatabaseException(f"Failed to scan items: {e}")
    
    async def create(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create new item."""
        try:
            self.table.put_item(Item=item)
            return item
        except ClientError as e:
            logger.error(f"Error creating item in {self.table_name}: {e}")
            raise DatabaseException(f"Failed to create item: {e}")
    
    async def update(self, item_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing item."""
        try:
            # Build update expression
            update_expression = "SET "
            expression_attribute_values = {}
            expression_attribute_names = {}
            
            for key, value in updates.items():
                if key != 'pk':  # Don't update the primary key
                    attr_name = f"#{key}"
                    attr_value = f":{key}"
                    update_expression += f"{attr_name} = {attr_value}, "
                    expression_attribute_names[attr_name] = key
                    expression_attribute_values[attr_value] = value
            
            update_expression = update_expression.rstrip(', ')
            
            response = self.table.update_item(
                Key={'pk': item_id},
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
            
            return response.get('Attributes')
        except ClientError as e:
            logger.error(f"Error updating item {item_id} in {self.table_name}: {e}")
            raise DatabaseException(f"Failed to update item: {e}")
    
    async def delete(self, item_id: str) -> bool:
        """Delete item by ID."""
        try:
            self.table.delete_item(
                Key={'pk': item_id}
            )
            return True
        except ClientError as e:
            logger.error(f"Error deleting item {item_id} from {self.table_name}: {e}")
            raise DatabaseException(f"Failed to delete item: {e}")
    
    async def query_by_attribute(
        self, 
        attribute_name: str, 
        attribute_value: Any,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query items by attribute (requires GSI)."""
        try:
            scan_kwargs = {
                'FilterExpression': f"#{attribute_name} = :{attribute_name}",
                'ExpressionAttributeNames': {f"#{attribute_name}": attribute_name},
                'ExpressionAttributeValues': {f":{attribute_name}": attribute_value}
            }
            
            if limit:
                scan_kwargs['Limit'] = limit
            
            response = self.table.scan(**scan_kwargs)
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"Error querying {self.table_name} by {attribute_name}: {e}")
            raise DatabaseException(f"Failed to query items: {e}") 