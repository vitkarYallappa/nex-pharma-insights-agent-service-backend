from typing import List, Dict, Any, Optional
from .agent_processor import AgentProcessor
from .workflow_manager import Stage1WorkflowManager
from .models import Stage1Request, Stage1Response, Stage1PipelineState, AgentType, Stage1Status
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class Stage1OrchestratorService:
    """Stage1 orchestrator service for sequential agent processing"""
    
    def __init__(self):
        self.agent_processor = AgentProcessor()
        self.workflow_manager = Stage1WorkflowManager()
    
    async def process_stage1_request(self, request: Stage1Request) -> Stage1Response:
        """Process Stage1 request through all 4 agents sequentially"""
        try:
            logger.info(f"Starting Stage1 processing for request: {request.request_id}")
            
            # Initialize pipeline state
            pipeline_state = Stage1PipelineState(
                request_id=request.request_id,
                stage1_id=request.generate_stage1_id(),
                status=Stage1Status.PENDING
            )
            
            # Store initial state
            await self.workflow_manager.save_pipeline_state(pipeline_state)
            
            # Process agents sequentially
            return await self.agent_processor.process_all_agents(request, pipeline_state)
            
        except Exception as e:
            logger.error(f"Stage1 processing failed for request {request.request_id}: {str(e)}")
            raise
    
    async def process_from_stage0_completion(self, request_id: str, s3_summary_path: str, 
                                           stage0_results: Dict[str, Any]) -> Stage1Response:
        """Start Stage1 processing when Stage0 completes"""
        try:
            logger.info(f"Starting Stage1 from Stage0 completion: {request_id}")
            
            # Create Stage1 request
            stage1_request = Stage1Request(
                request_id=request_id,
                s3_summary_path=s3_summary_path,
                stage0_results=stage0_results
            )
            
            # Process through all agents
            return await self.process_stage1_request(stage1_request)
            
        except Exception as e:
            logger.error(f"Stage1 processing from Stage0 failed: {str(e)}")
            raise
    
    async def get_status(self, request_id: str) -> Optional[Stage1PipelineState]:
        """Get Stage1 pipeline status"""
        return await self.workflow_manager.get_pipeline_status(request_id)
    
    async def get_agent_status(self, request_id: str, agent_type: AgentType) -> Optional[Dict[str, Any]]:
        """Get specific agent processing status"""
        pipeline_state = await self.get_status(request_id)
        if pipeline_state and agent_type.value in pipeline_state.agent_states:
            return pipeline_state.agent_states[agent_type.value].dict()
        return None
    
    async def retry_failed_agent(self, request_id: str, agent_type: AgentType) -> bool:
        """Retry a specific failed agent"""
        try:
            logger.info(f"Retrying agent {agent_type.value} for request: {request_id}")
            return await self.workflow_manager.retry_agent(request_id, agent_type)
        except Exception as e:
            logger.error(f"Agent retry failed: {str(e)}")
            return False
    
    async def list_active_pipelines(self) -> List[Stage1PipelineState]:
        """List active Stage1 pipelines"""
        return await self.workflow_manager.list_active_pipelines()
    
    async def get_agent_results(self, request_id: str, agent_type: AgentType) -> Dict[str, Any]:
        """Get results from specific agent's table"""
        return await self.workflow_manager.get_agent_results(request_id, agent_type)
    
    async def get_all_results(self, request_id: str) -> Dict[str, Any]:
        """Get results from all agent tables"""
        results = {}
        for agent_type in AgentType:
            try:
                agent_results = await self.get_agent_results(request_id, agent_type)
                results[agent_type.value] = agent_results
            except Exception as e:
                logger.warning(f"Failed to get results for {agent_type.value}: {str(e)}")
                results[agent_type.value] = {"error": str(e)}
        
        return results
    
    async def cleanup_completed_requests(self, max_age_hours: int = 24) -> int:
        """Clean up old completed requests"""
        return await self.workflow_manager.cleanup_completed_pipelines(max_age_hours) 