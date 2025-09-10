import boto3
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError
from ...config.settings import settings

class DynamoDBClient:
    """Real DynamoDB client implementation."""
    
    def __init__(self):
        # For local DynamoDB, use proper dummy credentials that boto3 accepts
        if settings.DYNAMODB_ENDPOINT:
            # Local DynamoDB - use dummy credentials that boto3 accepts
            aws_access_key = settings.AWS_ACCESS_KEY_ID or "test"
            aws_secret_key = settings.AWS_SECRET_ACCESS_KEY or "test"
            
            # Ensure credentials are valid format for boto3
            if aws_access_key == "dummy":
                aws_access_key = "test"
            if aws_secret_key == "dummy":
                aws_secret_key = "test"
                
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=settings.DYNAMODB_ENDPOINT,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=settings.DYNAMODB_REGION
            )
        else:
            # AWS DynamoDB - use real credentials
            self.session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.DYNAMODB_REGION
            )
            self.dynamodb = self.session.resource('dynamodb')
    
    async def put_item(self, table_name: str, item: Dict[str, Any]) -> bool:
        """Put an item into DynamoDB table."""
        try:
            table = self.dynamodb.Table(table_name)
            table.put_item(Item=item)
            return True
        except ClientError as e:
            print(f"Error putting item: {e}")
            return False
    
    async def get_item(self, table_name: str, key: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get an item from DynamoDB table."""
        try:
            table = self.dynamodb.Table(table_name)
            response = table.get_item(Key=key)
            return response.get('Item')
        except ClientError as e:
            print(f"Error getting item: {e}")
            return None
    
    async def query(self, table_name: str, key_condition: str, **kwargs) -> List[Dict[str, Any]]:
        """Query items from DynamoDB table."""
        try:
            table = self.dynamodb.Table(table_name)
            response = table.query(
                KeyConditionExpression=key_condition,
                **kwargs
            )
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error querying items: {e}")
            return []
    
    async def scan(self, table_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Scan items from DynamoDB table."""
        try:
            table = self.dynamodb.Table(table_name)
            response = table.scan(**kwargs)
            return response.get('Items', [])
        except ClientError as e:
            print(f"Error scanning items: {e}")
            return []
    
    async def delete_item(self, table_name: str, key: Dict[str, Any]) -> bool:
        """Delete an item from DynamoDB table."""
        try:
            table = self.dynamodb.Table(table_name)
            table.delete_item(Key=key)
            return True
        except ClientError as e:
            print(f"Error deleting item: {e}")
            return False 