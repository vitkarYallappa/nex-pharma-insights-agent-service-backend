import boto3
from typing import List, Dict, Any
from ...config.settings import settings

class DatabaseMigrations:
    """Database migrations for DynamoDB tables."""
    
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.DYNAMODB_REGION
        )
        
        if settings.DYNAMODB_ENDPOINT:
            self.dynamodb = self.session.resource(
                'dynamodb',
                endpoint_url=settings.DYNAMODB_ENDPOINT
            )
        else:
            self.dynamodb = self.session.resource('dynamodb')
    
    def create_table(self, table_name: str, key_schema: List[Dict], 
                    attribute_definitions: List[Dict], 
                    billing_mode: str = 'PAY_PER_REQUEST') -> bool:
        """Create a DynamoDB table."""
        try:
            table = self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=key_schema,
                AttributeDefinitions=attribute_definitions,
                BillingMode=billing_mode
            )
            
            # Wait for table to be created
            table.wait_until_exists()
            print(f"Table {table_name} created successfully")
            return True
        except Exception as e:
            print(f"Error creating table {table_name}: {e}")
            return False
    
    def delete_table(self, table_name: str) -> bool:
        """Delete a DynamoDB table."""
        try:
            table = self.dynamodb.Table(table_name)
            table.delete()
            print(f"Table {table_name} deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting table {table_name}: {e}")
            return False
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        try:
            table = self.dynamodb.Table(table_name)
            table.load()
            return True
        except Exception:
            return False
    
    def create_agent_tables(self) -> bool:
        """Create all agent-related tables."""
        tables = [
            {
                'name': 'agent_requests',
                'key_schema': [
                    {'AttributeName': 'request_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'request_id', 'AttributeType': 'S'}
                ]
            },
            {
                'name': 'agent_content',
                'key_schema': [
                    {'AttributeName': 'content_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'content_id', 'AttributeType': 'S'}
                ]
            },
            {
                'name': 'agent_results',
                'key_schema': [
                    {'AttributeName': 'result_id', 'KeyType': 'HASH'}
                ],
                'attribute_definitions': [
                    {'AttributeName': 'result_id', 'AttributeType': 'S'}
                ]
            }
        ]
        
        success = True
        for table_config in tables:
            if not self.table_exists(table_config['name']):
                if not self.create_table(
                    table_config['name'],
                    table_config['key_schema'],
                    table_config['attribute_definitions']
                ):
                    success = False
            else:
                print(f"Table {table_config['name']} already exists")
        
        return success 