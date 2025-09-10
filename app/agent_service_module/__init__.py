"""
Agent Service Module

This module provides a comprehensive agent service system for pharmaceutical
market intelligence processing. It includes multiple specialized agents
and factory pattern for seamless service integration.

Key Components:
- Agent1: Deduplication Service
- Agent2: Relevance Scoring Service  
- Agent3: Insights Generation Service
- Agent4: Implications Analysis Service
- Stage0: Orchestration and Data Collection Services

Features:
- Modular agent architecture
- Configurable service factory
- Comprehensive logging and monitoring
- Storage and database abstraction
- Environment-based configuration
"""

__version__ = "1.0.0"
__author__ = "Pharma Intelligence Team"

# Import key components for easy access
from .config.settings import settings
from .config.service_factory import ServiceFactory

__all__ = [
    'settings',
    'ServiceFactory'
] 