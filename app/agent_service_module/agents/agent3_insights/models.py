"""
Clean models for Agent 3 - Insights Generation

Focused data models for insight generation and storage.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class InsightCategory(str, Enum):
    """Categories for market insights"""
    MARKET_TREND = "market_trend"
    COMPETITIVE = "competitive"
    REGULATORY = "regulatory"
    CLINICAL = "clinical"
    INVESTMENT = "investment"
    RISK = "risk"
    GENERAL = "general"

class ImpactLevel(str, Enum):
    """Impact levels for insights"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TimeHorizon(str, Enum):
    """Time horizons for insights"""
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"

class Priority(str, Enum):
    """Priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class MarketInsight(BaseModel):
    """Individual market insight"""
    insight: str = Field(..., description="The insight text")
    category: InsightCategory = Field(..., description="Insight category")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    impact_level: ImpactLevel = Field(..., description="Impact level")
    time_horizon: TimeHorizon = Field(..., description="Time horizon")
    supporting_evidence: List[str] = Field(default_factory=list, description="Supporting evidence")

class StrategicRecommendation(BaseModel):
    """Strategic recommendation"""
    recommendation: str = Field(..., description="The recommendation")
    priority: Priority = Field(..., description="Priority level")
    rationale: str = Field(..., description="Rationale for the recommendation")

class RiskFactor(BaseModel):
    """Risk factor identification"""
    risk: str = Field(..., description="The identified risk")
    severity: Priority = Field(..., description="Risk severity")
    mitigation: str = Field(..., description="Suggested mitigation strategy")

class Agent3InsightsRequest(BaseModel):
    """Request model for Agent 3 insights generation"""
    request_id: str = Field(..., description="Unique request identifier")
    s3_summary_path: Optional[str] = Field(None, description="S3 path to summary content")
    content: Optional[str] = Field(None, description="Direct content for processing")
    url_id: Optional[str] = Field(None, description="URL ID from Perplexity processing")
    content_id: Optional[str] = Field(None, description="Content ID from Perplexity processing")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    api_provider: str = Field(default="anthropic_direct", description="API provider to use")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class InsightsData(BaseModel):
    """MVP insights data - simple HTML content"""
    html_content: str = Field(..., description="HTML formatted insights for MVP")

class Agent3InsightsResponse(BaseModel):
    """Response model for Agent 3 insights generation"""
    request_id: str = Field(..., description="Request identifier")
    insights: InsightsData = Field(..., description="Generated insights")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    status: str = Field(default="completed", description="Processing status")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Database storage fields
    content_length: Optional[int] = Field(None, description="Length of processed content")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    api_provider: Optional[str] = Field(None, description="API provider used")
    model_used: Optional[str] = Field(None, description="Model used for generation")

# Database table schema for DynamoDB
AGENT3_TABLE_SCHEMA = {
    "table_name": "agent3_insights_results",
    "partition_key": "request_id",
    "sort_key": "insight_id",
    "attributes": {
        "request_id": "S",
        "insight_id": "S",
        "insights_data": "S",  # JSON string of InsightsData
        "metadata": "S",       # JSON string of metadata
        "status": "S",
        "timestamp": "S",
        "content_length": "N",
        "processing_time_ms": "N",
        "api_provider": "S",
        "model_used": "S"
    },
    "global_secondary_indexes": [
        {
            "index_name": "status-timestamp-index",
            "partition_key": "status",
            "sort_key": "timestamp"
        }
    ]
}
