import asyncio
from typing import Dict, Any, List
from datetime import datetime

from .models import (
    Stage1Request, Stage1Response, Stage1PipelineState, 
    AgentProcessingState, AgentType, Stage1Status, AgentTableConfig
)
from ...shared.utils.logger import get_logger

# Import agent services
from ..agent1_deduplication.service import Agent1DeduplicationService
from ..agent2_relevance.service import Agent2RelevanceService  
from ..agent3_insights.service import Agent3InsightsService
from ..agent4_implications.service import Agent4ImplicationsService

logger = get_logger(__name__)

class AgentProcessor:
    """Processes Stage1 request through all 4 agents sequentially"""
    
    def __init__(self):
        # Initialize agent services
        self.agent1_service = Agent1DeduplicationService()
        self.agent2_service = Agent2RelevanceService()
        self.agent3_service = Agent3InsightsService()
        self.agent4_service = Agent4ImplicationsService()
        
        # Agent table configurations (all configs)
        self.all_table_configs = {
            config.agent_type: config 
            for config in AgentTableConfig.get_default_configs()
        }
        
        # Only enabled agent configurations
        self.enabled_table_configs = {
            config.agent_type: config 
            for config in AgentTableConfig.get_enabled_configs()
        }
    
    async def process_all_agents(self, request: Stage1Request, 
                               pipeline_state: Stage1PipelineState) -> Stage1Response:
        """Process request through all 4 agents sequentially"""
        
        start_time = datetime.utcnow()
        
        try:
            # Full agent processing sequence
            all_agent_sequence = [
                (AgentType.DEDUPLICATION, self.agent1_service, Stage1Status.AGENT1_PROCESSING),
                (AgentType.RELEVANCE, self.agent2_service, Stage1Status.AGENT2_PROCESSING),
                (AgentType.INSIGHTS, self.agent3_service, Stage1Status.AGENT3_PROCESSING),
                (AgentType.IMPLICATIONS, self.agent4_service, Stage1Status.AGENT4_PROCESSING)
            ]
            
            # Filter to only enabled agents
            enabled_agent_sequence = [
                (agent_type, agent_service, processing_status)
                for agent_type, agent_service, processing_status in all_agent_sequence
                if agent_type in self.enabled_table_configs
            ]
            
            logger.info(f"Processing {len(enabled_agent_sequence)} enabled agents for request: {request.request_id}")
            enabled_agent_names = [agent_type.value for agent_type, _, _ in enabled_agent_sequence]
            logger.info(f"Enabled agents: {enabled_agent_names}")
            
            # Process each enabled agent sequentially
            for agent_type, agent_service, processing_status in enabled_agent_sequence:
                logger.info(f"Starting {agent_type.value} processing for request: {request.request_id}")
                
                # Update pipeline status
                pipeline_state.status = processing_status
                pipeline_state.current_agent = agent_type
                
                # Process agent
                agent_result = await self._process_single_agent(
                    request, agent_type, agent_service, pipeline_state
                )
                
                # Check if agent processing failed
                if not agent_result.get('success', False):
                    logger.error(f"Agent {agent_type.value} failed for request: {request.request_id}")
                    pipeline_state.status = Stage1Status.FAILED
                    break
                
                logger.info(f"Completed {agent_type.value} processing for request: {request.request_id}")
            
            # Determine final status
            if pipeline_state.is_pipeline_complete():
                pipeline_state.status = Stage1Status.COMPLETED
            elif pipeline_state.status != Stage1Status.FAILED:
                pipeline_state.status = Stage1Status.PARTIAL_SUCCESS
            
            # Calculate total processing time
            end_time = datetime.utcnow()
            pipeline_state.completed_at = end_time
            pipeline_state.total_processing_time = (end_time - start_time).total_seconds()
            
            # Create response
            return self._create_stage1_response(request, pipeline_state)
            
        except Exception as e:
            logger.error(f"Agent processing failed for request {request.request_id}: {str(e)}")
            pipeline_state.status = Stage1Status.FAILED
            pipeline_state.completed_at = datetime.utcnow()
            
            # Return failed response
            return Stage1Response(
                request_id=request.request_id,
                stage1_id=pipeline_state.stage1_id,
                status=Stage1Status.FAILED,
                total_processing_time=(datetime.utcnow() - start_time).total_seconds(),
                agents_completed=0,
                overall_success_rate=0.0,
                errors=[str(e)]
            )
    
    async def _process_single_agent(self, request: Stage1Request, agent_type: AgentType,
                                  agent_service: Any, pipeline_state: Stage1PipelineState) -> Dict[str, Any]:
        """Process a single agent"""
        
        agent_start_time = datetime.utcnow()
        
        # Get table configuration
        table_config = self.enabled_table_configs[agent_type]
        
        # Create agent processing state
        agent_state = AgentProcessingState(
            request_id=request.request_id,
            agent_type=agent_type,
            status=Stage1Status.PENDING,
            input_s3_path=request.s3_summary_path,
            output_table_name=table_config.table_name,
            started_at=agent_start_time
        )
        
        try:
            # Update agent status to processing
            agent_state.status = self._get_processing_status_for_agent(agent_type)
            
            # Call the specific agent service
            agent_result = await self._call_agent_service(
                agent_service, request, agent_state
            )
            
            # Update agent state with results
            agent_state.completed_at = datetime.utcnow()
            agent_state.processing_time_seconds = (
                agent_state.completed_at - agent_start_time
            ).total_seconds()
            
            if agent_result.get('success', False):
                agent_state.status = Stage1Status.COMPLETED
                agent_state.items_processed = agent_result.get('items_processed', 0)
                agent_state.items_successful = agent_result.get('items_successful', 0)
                agent_state.items_failed = agent_result.get('items_failed', 0)
            else:
                agent_state.status = Stage1Status.FAILED
                agent_state.errors = agent_result.get('errors', [])
            
            # Store agent state in pipeline
            pipeline_state.agent_states[agent_type.value] = agent_state
            
            return agent_result
            
        except Exception as e:
            logger.error(f"Agent {agent_type.value} processing failed: {str(e)}")
            
            agent_state.status = Stage1Status.FAILED
            agent_state.completed_at = datetime.utcnow()
            agent_state.processing_time_seconds = (
                agent_state.completed_at - agent_start_time
            ).total_seconds()
            agent_state.errors = [str(e)]
            
            # Store failed state
            pipeline_state.agent_states[agent_type.value] = agent_state
            
            return {'success': False, 'error': str(e)}
    
    async def _call_agent_service(self, agent_service: Any, request: Stage1Request,
                                agent_state: AgentProcessingState) -> Dict[str, Any]:
        """Call the specific agent service with S3 data"""
        
        try:
            # All agents follow the same pattern:
            # 1. Read S3 summary data
            # 2. Process the data
            # 3. Store results in their respective table
            
            result = await agent_service.process_from_s3(
                request_id=request.request_id,
                s3_path=request.s3_summary_path,
                output_table=agent_state.output_table_name,
                config=request.processing_config
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Agent service call failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _get_processing_status_for_agent(self, agent_type: AgentType) -> Stage1Status:
        """Get the processing status for specific agent"""
        status_map = {
            AgentType.DEDUPLICATION: Stage1Status.AGENT1_PROCESSING,
            AgentType.RELEVANCE: Stage1Status.AGENT2_PROCESSING,
            AgentType.INSIGHTS: Stage1Status.AGENT3_PROCESSING,
            AgentType.IMPLICATIONS: Stage1Status.AGENT4_PROCESSING
        }
        return status_map.get(agent_type, Stage1Status.PENDING)
    
    def _create_stage1_response(self, request: Stage1Request, 
                              pipeline_state: Stage1PipelineState) -> Stage1Response:
        """Create final Stage1 response"""
        
        # Calculate statistics for enabled agents only
        enabled_configs = AgentTableConfig.get_enabled_configs()
        enabled_agents = [config.agent_type for config in enabled_configs]
        total_enabled_agents = len(enabled_agents)
        
        completed_agents = sum(
            1 for state in pipeline_state.agent_states.values()
            if state.status == Stage1Status.COMPLETED
        )
        
        success_rate = (completed_agents / total_enabled_agents) * 100 if total_enabled_agents > 0 else 0
        
        # Collect agent results summary (only for enabled agents)
        agent_results = {}
        result_tables = {}
        
        for agent_type in enabled_agents:
            agent_key = agent_type.value
            if agent_key in pipeline_state.agent_states:
                agent_state = pipeline_state.agent_states[agent_key]
                agent_results[agent_key] = {
                    'status': agent_state.status,
                    'items_processed': agent_state.items_processed,
                    'items_successful': agent_state.items_successful,
                    'processing_time': agent_state.processing_time_seconds
                }
                result_tables[agent_key] = agent_state.output_table_name
        
        # Collect errors and warnings
        all_errors = []
        all_warnings = []
        
        for agent_state in pipeline_state.agent_states.values():
            all_errors.extend(agent_state.errors)
            all_warnings.extend(agent_state.warnings)
        
        return Stage1Response(
            request_id=request.request_id,
            stage1_id=pipeline_state.stage1_id,
            status=pipeline_state.status,
            total_processing_time=pipeline_state.total_processing_time or 0,
            agents_completed=completed_agents,
            overall_success_rate=success_rate,
            agent_results=agent_results,
            result_tables=result_tables,
            completed_at=pipeline_state.completed_at or datetime.utcnow(),
            errors=all_errors,
            warnings=all_warnings
        ) 