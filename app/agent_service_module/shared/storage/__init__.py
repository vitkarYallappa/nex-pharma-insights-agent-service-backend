"""
Storage module with real and mock implementations for S3 and Minio.
"""

from .base_storage import BaseStorage
from .file_manager import FileManager

__all__ = ["BaseStorage", "FileManager"] 