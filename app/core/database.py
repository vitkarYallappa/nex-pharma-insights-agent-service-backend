import boto3
from botocore.exceptions import ClientError
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class DynamoDBConnection:
    """DynamoDB connection manager."""
    
    def __init__(self):
        self._client = None
        self._resource = None
    
    @property
    def client(self):
        """Get DynamoDB client."""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    @property
    def resource(self):
        """Get DynamoDB resource."""
        if self._resource is None:
            self._resource = self._create_resource()
        return self._resource
    
    def _create_client(self):
        """Create DynamoDB client."""
        try:
            client_config = {
                'region_name': settings.AWS_REGION
            }
            
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                client_config.update({
                    'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                    'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY
                })
            
            if settings.DYNAMODB_ENDPOINT:
                client_config['endpoint_url'] = settings.DYNAMODB_ENDPOINT
            
            return boto3.client('dynamodb', **client_config)
        except Exception as e:
            logger.error(f"Failed to create DynamoDB client: {e}")
            raise
    
    def _create_resource(self):
        """Create DynamoDB resource."""
        try:
            resource_config = {
                'region_name': settings.AWS_REGION
            }
            
            if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
                resource_config.update({
                    'aws_access_key_id': settings.AWS_ACCESS_KEY_ID,
                    'aws_secret_access_key': settings.AWS_SECRET_ACCESS_KEY
                })
            
            if settings.DYNAMODB_ENDPOINT:
                resource_config['endpoint_url'] = settings.DYNAMODB_ENDPOINT
            
            return boto3.resource('dynamodb', **resource_config)
        except Exception as e:
            logger.error(f"Failed to create DynamoDB resource: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check DynamoDB connection health."""
        try:
            self.client.list_tables()
            return True
        except ClientError as e:
            logger.error(f"DynamoDB health check failed: {e}")
            return False


# Global database connection instance
db_connection = DynamoDBConnection() 