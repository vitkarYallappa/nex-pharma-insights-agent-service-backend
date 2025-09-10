"""
Root Orchestrator Package

This package provides the top-level request management system for market intelligence workflows.
It supports both table-based and SQS-based processing strategies.
"""

from .models import (
    RequestStatus,
    RequestType, 
    Priority,
    MarketIntelligenceRequest,
    RequestProgress,
    RequestResults,
    DateRangeConfig,
    SourceConfig,
    MarketIntelligenceRequestConfig
)

try:
    from .root_orchestrator_service import RootOrchestratorService
    __all__ = [
        "RequestStatus",
        "RequestType",
        "Priority", 
        "MarketIntelligenceRequest",
        "RequestProgress",
        "RequestResults",
        "DateRangeConfig",
        "SourceConfig", 
        "MarketIntelligenceRequestConfig",
        "RootOrchestratorService"
    ]
except ImportError as e:
    # Handle import errors gracefully during development
    __all__ = [
        "RequestStatus",
        "RequestType",
        "Priority", 
        "MarketIntelligenceRequest",
        "RequestProgress",
        "RequestResults",
        "DateRangeConfig",
        "SourceConfig", 
        "MarketIntelligenceRequestConfig"
    ] 