import boto3
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError
from ....config.unified_settings import settings

class S3Client:
    """S3-compatible client implementation supporting both AWS S3 and MinIO."""
    
    def __init__(self):
        # Configure based on storage type
        if settings.STORAGE_TYPE == "minio":
            # MinIO configuration
            self.s3 = boto3.client(
                's3',
                endpoint_url=f'http://{settings.MINIO_ENDPOINT}',
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                region_name=settings.AWS_REGION
            )
            print(f"Initialized MinIO client: {settings.MINIO_ENDPOINT}")
        else:
            # AWS S3 configuration
            self.session = boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.s3 = self.session.client('s3')
            print(f"Initialized AWS S3 client: {settings.AWS_REGION}")
        
        self.bucket_name = settings.S3_BUCKET_NAME
        self.storage_type = settings.STORAGE_TYPE
    
    async def upload_file(self, file_path: str, object_key: str, 
                         metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload a file to S3."""
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3.upload_file(file_path, self.bucket_name, object_key, ExtraArgs=extra_args)
            print(f"File uploaded to {self.storage_type}: {object_key}")
            return True
        except ClientError as e:
            print(f"Error uploading file to {self.storage_type}: {e}")
            return False
    
    async def upload_content(self, content: bytes, object_key: str,
                           content_type: str = 'application/octet-stream',
                           metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload content directly to S3."""
        try:
            extra_args = {'ContentType': content_type}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=content,
                **extra_args
            )
            print(f"Content uploaded to {self.storage_type}: {object_key}")
            return True
        except ClientError as e:
            print(f"Error uploading content to {self.storage_type}: {e}")
            return False
    
    async def download_file(self, object_key: str, file_path: str) -> bool:
        """Download a file from S3."""
        try:
            self.s3.download_file(self.bucket_name, object_key, file_path)
            print(f"File downloaded from S3: {object_key}")
            return True
        except ClientError as e:
            print(f"Error downloading file from S3: {e}")
            return False
    
    async def get_content(self, object_key: str) -> Optional[bytes]:
        """Get content from S3."""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=object_key)
            content = response['Body'].read()
            print(f"Content retrieved from S3: {object_key}")
            return content
        except ClientError as e:
            print(f"Error getting content from S3: {e}")
            return None
    
    async def delete_object(self, object_key: str) -> bool:
        """Delete an object from S3."""
        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_key)
            print(f"Object deleted from S3: {object_key}")
            return True
        except ClientError as e:
            print(f"Error deleting object from S3: {e}")
            return False
    
    async def list_objects(self, prefix: str = "") -> list:
        """List objects in S3 bucket."""
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            objects = response.get('Contents', [])
            print(f"Listed {len(objects)} objects from S3")
            return [obj['Key'] for obj in objects]
        except ClientError as e:
            print(f"Error listing objects from S3: {e}")
            return []
    
    async def object_exists(self, object_key: str) -> bool:
        """Check if an object exists in S3."""
        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False 