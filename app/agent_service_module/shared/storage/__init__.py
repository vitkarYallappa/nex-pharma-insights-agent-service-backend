"""
Storage module with real implementations for S3 and Minio.
"""

from .base_storage import BaseStorage
from .s3_client import S3Client

__all__ = ["BaseStorage", "S3Client"] 