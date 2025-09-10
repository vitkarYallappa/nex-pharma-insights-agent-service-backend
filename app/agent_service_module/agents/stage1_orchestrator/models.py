from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class Stage1Status(str, Enum):
    """Status of Stage1 processing pipeline"""
    PENDING = "pending"
    AGENT1_PROCESSING = "agent1_processing"  # Deduplication
    AGENT2_PROCESSING = "agent2_processing"  # Relevance
    AGENT3_PROCESSING = "agent3_processing"  # Insights
    AGENT4_PROCESSING = "agent4_processing"  # Implications
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"

class AgentType(str, Enum):
    """Types of agents in Stage1"""
    DEDUPLICATION = "agent1_deduplication"
    RELEVANCE = "agent2_relevance"
    INSIGHTS = "agent3_insights"
    IMPLICATIONS = "agent4_implications"

class Stage1Request(BaseModel):
    """Stage1 processing request"""
    request_id: str = Field(..., description="Request ID from Stage0")
    s3_summary_path: str = Field(..., description="S3 path to Stage0 summary results")
    stage0_results: Dict[str, Any] = Field(default_factory=dict, description="Stage0 results metadata")
    processing_config: Dict[str, Any] = Field(default_factory=dict, description="Processing configuration")
    
    def generate_stage1_id(self) -> str:
        """Generate Stage1 specific ID"""
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        return f"stage1_{self.request_id}_{timestamp}"

class AgentProcessingState(BaseModel):
    """State tracking for individual agent processing"""
    request_id: str = Field(..., description="Request identifier")
    agent_type: AgentType = Field(..., description="Type of agent")
    status: Stage1Status = Field(default=Stage1Status.PENDING)
    
    # Input/Output paths
    input_s3_path: str = Field(..., description="S3 path to input data")
    output_table_name: str = Field(..., description="DynamoDB table for results")
    
    # Processing metadata
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    processing_time_seconds: Optional[float] = Field(default=None)
    
    # Results tracking
    items_processed: int = Field(default=0)
    items_successful: int = Field(default=0)
    items_failed: int = Field(default=0)
    
    # Error handling
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

class Stage1PipelineState(BaseModel):
    """Overall Stage1 pipeline state tracking"""
    request_id: str = Field(..., description="Request identifier")
    stage1_id: str = Field(..., description="Stage1 specific identifier")
    status: Stage1Status = Field(default=Stage1Status.PENDING)
    current_agent: Optional[AgentType] = Field(default=None)
    
    # Pipeline timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    total_processing_time: Optional[float] = Field(default=None)
    
    # Agent states
    agent_states: Dict[str, AgentProcessingState] = Field(default_factory=dict)
    
    # Overall results
    total_items_processed: int = Field(default=0)
    pipeline_success_rate: float = Field(default=0.0)
    
    def get_next_agent(self) -> Optional[AgentType]:
        """Get the next agent to process"""
        agent_sequence = [
            AgentType.DEDUPLICATION,
            AgentType.RELEVANCE, 
            AgentType.INSIGHTS,
            AgentType.IMPLICATIONS
        ]
        
        if not self.current_agent:
            return agent_sequence[0]
        
        try:
            current_index = agent_sequence.index(self.current_agent)
            if current_index < len(agent_sequence) - 1:
                return agent_sequence[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def is_pipeline_complete(self) -> bool:
        """Check if all enabled agents have completed processing"""
        # Get only enabled agents
        enabled_configs = AgentTableConfig.get_enabled_configs()
        enabled_agents = [config.agent_type for config in enabled_configs]
        
        for agent in enabled_agents:
            agent_key = agent.value
            if agent_key not in self.agent_states:
                return False
            
            agent_state = self.agent_states[agent_key]
            if agent_state.status not in [Stage1Status.COMPLETED, Stage1Status.PARTIAL_SUCCESS]:
                return False
        
        return True

class AgentTableConfig(BaseModel):
    """Configuration for agent-specific tables"""
    agent_type: AgentType = Field(..., description="Agent type")
    table_name: str = Field(..., description="DynamoDB table name")
    table_schema: Dict[str, Any] = Field(default_factory=dict, description="Table schema definition")
    enabled: bool = Field(default=True, description="Whether this agent is enabled")
    
    @classmethod
    def get_default_configs(cls) -> List["AgentTableConfig"]:
        """Get default table configurations for all agents"""
        from .agent_config import AGENT_CONFIG
        
        return [
            cls(
                agent_type=AgentType.DEDUPLICATION,
                table_name="agent1_deduplication_results",
                table_schema={
                    "partition_key": "request_id",
                    "sort_key": "content_hash",
                    "attributes": ["original_content", "is_duplicate", "duplicate_group_id", "similarity_score"]
                },
                enabled=AGENT_CONFIG["agent1_deduplication"]["enabled"]
            ),
            cls(
                agent_type=AgentType.RELEVANCE,
                table_name="agent2_relevance_results", 
                table_schema={
                    "partition_key": "request_id",
                    "sort_key": "content_id",
                    "attributes": ["content", "relevance_score", "relevance_category", "keywords_matched"]
                },
                enabled=AGENT_CONFIG["agent2_relevance"]["enabled"]
            ),
            cls(
                agent_type=AgentType.INSIGHTS,
                table_name="agent3_insights_results",
                table_schema={
                    "partition_key": "request_id", 
                    "sort_key": "insight_id",
                    "attributes": ["insight_text", "insight_type", "confidence_score", "source_content_ids"]
                },
                enabled=AGENT_CONFIG["agent3_insights"]["enabled"]
            ),
            cls(
                agent_type=AgentType.IMPLICATIONS,
                table_name="agent4_implications_results",
                table_schema={
                    "partition_key": "request_id",
                    "sort_key": "implication_id", 
                    "attributes": ["implication_text", "impact_level", "stakeholder_groups", "related_insights"]
                },
                enabled=AGENT_CONFIG["agent4_implications"]["enabled"]
            )
        ]
    
    @classmethod
    def get_enabled_configs(cls) -> List["AgentTableConfig"]:
        """Get only enabled agent configurations"""
        return [config for config in cls.get_default_configs() if config.enabled]

class Stage1Response(BaseModel):
    """Response from Stage1 processing"""
    request_id: str = Field(..., description="Original request ID")
    stage1_id: str = Field(..., description="Stage1 processing ID")
    status: Stage1Status = Field(..., description="Final processing status")
    
    # Processing summary
    total_processing_time: float = Field(..., description="Total time in seconds")
    agents_completed: int = Field(..., description="Number of agents completed")
    overall_success_rate: float = Field(..., description="Overall success rate")
    
    # Agent results summary
    agent_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Results from each agent")
    
    # Table locations
    result_tables: Dict[str, str] = Field(default_factory=dict, description="Table names for each agent's results")
    
    # Metadata
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list) 