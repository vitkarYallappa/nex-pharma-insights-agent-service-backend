"""
Production Service Factory for Root Orchestrator

This service factory provides real implementations for production use.
"""

from typing import Any, Dict, Optional
import os

class TempServiceFactory:
    """
    Production service factory for Root Orchestrator.
    
    This provides real service implementations for production use.
    """
    
    _database_client = None
    _storage_client = None
    _minio_client = None
    _perplexity_client = None
    _serp_client = None
    
    @classmethod
    def get_database_client(cls):
        """Get real database client instance"""
        if cls._database_client is None:
            from ..agent_service_module.config.service_factory import ServiceFactory as RealServiceFactory
            cls._database_client = RealServiceFactory.get_database_client()
        return cls._database_client
    
    @classmethod
    def get_storage_client(cls):
        """Get real storage client instance"""
        if cls._storage_client is None:
            from ..agent_service_module.config.service_factory import ServiceFactory as RealServiceFactory
            cls._storage_client = RealServiceFactory.get_storage_client()
        return cls._storage_client
    
    @classmethod
    def get_minio_client(cls):
        """Get real MinIO client instance"""
        if cls._minio_client is None:
            from ..agent_service_module.config.service_factory import ServiceFactory as RealServiceFactory
            cls._minio_client = RealServiceFactory.get_storage_client()
        return cls._minio_client
    
    @classmethod
    def get_perplexity_client(cls):
        """Get real Perplexity client instance"""
        if cls._perplexity_client is None:
            from ..agent_service_module.config.service_factory import ServiceFactory as RealServiceFactory
            cls._perplexity_client = RealServiceFactory.get_perplexity_client()
        return cls._perplexity_client
    
    @classmethod
    def get_serp_client(cls):
        """Get real SERP client instance"""
        if cls._serp_client is None:
            from ..agent_service_module.config.service_factory import ServiceFactory as RealServiceFactory
            cls._serp_client = RealServiceFactory.get_serp_client()
        return cls._serp_client
    
    @classmethod
    def reset(cls):
        """Reset all service instances (for testing)"""
        cls._database_client = None
        cls._storage_client = None
        cls._minio_client = None
        cls._perplexity_client = None
        cls._serp_client = None


# For compatibility with existing imports
ServiceFactory = TempServiceFactory 