"""
Database module with real and mock implementations.
"""

from .connection import DatabaseConnection
from .base_repository import BaseRepository

__all__ = ["DatabaseConnection", "BaseRepository"] 