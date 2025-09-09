from typing import Union, Optional, Dict
from ...config.service_factory import ServiceFactory
from .s3_client import S3Client
from .s3_mock import S3Mock

class BaseStorage:
    """Base storage manager using factory pattern."""
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self) -> Union[S3Client, S3Mock]:
        """Get storage client (real or mock based on configuration)."""
        if self._client is None:
            self._client = ServiceFactory.get_storage_client()
        return self._client
    
    async def upload_file(self, file_path: str, object_key: str, 
                         metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload a file to storage."""
        return await self.client.upload_file(file_path, object_key, metadata)
    
    async def upload_content(self, content: bytes, object_key: str,
                           content_type: str = 'application/octet-stream',
                           metadata: Optional[Dict[str, str]] = None) -> bool:
        """Upload content directly to storage."""
        return await self.client.upload_content(content, object_key, content_type, metadata)
    
    async def download_file(self, object_key: str, file_path: str) -> bool:
        """Download a file from storage."""
        return await self.client.download_file(object_key, file_path)
    
    async def get_content(self, object_key: str) -> Optional[bytes]:
        """Get content from storage."""
        return await self.client.get_content(object_key)
    
    async def delete_object(self, object_key: str) -> bool:
        """Delete an object from storage."""
        return await self.client.delete_object(object_key)
    
    async def list_objects(self, prefix: str = "") -> list:
        """List objects in storage."""
        return await self.client.list_objects(prefix)
    
    async def object_exists(self, object_key: str) -> bool:
        """Check if an object exists in storage."""
        return await self.client.object_exists(object_key) 