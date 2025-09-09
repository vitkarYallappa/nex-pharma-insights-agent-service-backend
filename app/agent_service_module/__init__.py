"""
Agent Service Module

A modular agent service system with environment-based configuration
and factory pattern for seamless switching between real and mock implementations.
"""

from .config.settings import settings
from .config.service_factory import ServiceFactory

__version__ = "1.0.0"
__all__ = ["settings", "ServiceFactory"] 