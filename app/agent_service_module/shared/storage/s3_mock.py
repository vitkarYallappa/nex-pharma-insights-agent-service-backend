from typing import Optional, Dict, Any
import os
import tempfile
from datetime import datetime

class S3Mock:
    """Mock S3 client for testing."""
    
    def __init__(self):
        self.objects = {}  # object_key -> content
        self.metadata = {}  # object_key -> metadata
    
    async def upload_file(self, file_path: str, object_key: str, 
                         metadata: Optional[Dict[str, str]] = None) -> bool:
        """Mock upload file operation."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            self.objects[object_key] = content
            if metadata:
                self.metadata[object_key] = metadata
            
            print(f"Mock S3: File uploaded: {object_key}")
            return True
        except Exception as e:
            print(f"Mock S3: Error uploading file: {e}")
            return False
    
    async def upload_content(self, content: bytes, object_key: str,
                           content_type: str = 'application/octet-stream',
                           metadata: Optional[Dict[str, str]] = None) -> bool:
        """Mock upload content operation."""
        self.objects[object_key] = content
        if metadata:
            self.metadata[object_key] = metadata
        
        print(f"Mock S3: Content uploaded: {object_key} ({len(content)} bytes)")
        return True
    
    async def download_file(self, object_key: str, file_path: str) -> bool:
        """Mock download file operation."""
        if object_key not in self.objects:
            print(f"Mock S3: Object not found: {object_key}")
            return False
        
        try:
            with open(file_path, 'wb') as f:
                f.write(self.objects[object_key])
            
            print(f"Mock S3: File downloaded: {object_key}")
            return True
        except Exception as e:
            print(f"Mock S3: Error downloading file: {e}")
            return False
    
    async def get_content(self, object_key: str) -> Optional[bytes]:
        """Mock get content operation."""
        if object_key in self.objects:
            print(f"Mock S3: Content retrieved: {object_key}")
            return self.objects[object_key]
        
        print(f"Mock S3: Object not found: {object_key}")
        return None
    
    async def delete_object(self, object_key: str) -> bool:
        """Mock delete object operation."""
        if object_key in self.objects:
            del self.objects[object_key]
            if object_key in self.metadata:
                del self.metadata[object_key]
            print(f"Mock S3: Object deleted: {object_key}")
            return True
        
        print(f"Mock S3: Object not found for deletion: {object_key}")
        return False
    
    async def list_objects(self, prefix: str = "") -> list:
        """Mock list objects operation."""
        matching_keys = [key for key in self.objects.keys() if key.startswith(prefix)]
        print(f"Mock S3: Listed {len(matching_keys)} objects with prefix '{prefix}'")
        return matching_keys
    
    async def object_exists(self, object_key: str) -> bool:
        """Mock object exists check."""
        return object_key in self.objects
    
    def clear_all(self):
        """Clear all mock objects (testing utility)."""
        self.objects.clear()
        self.metadata.clear()
        print("Mock S3: All objects cleared")
    
    def get_object_count(self) -> int:
        """Get number of stored objects (testing utility)."""
        return len(self.objects) 