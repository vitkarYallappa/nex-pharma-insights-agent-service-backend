from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from ...config.service_factory import ServiceFactory
from .models import Stage1PipelineState, AgentType, Stage1Status
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class Stage1WorkflowManager:
    """Manage Stage1 pipeline workflows and state transitions"""
    
    def __init__(self):
        self.database_client = ServiceFactory.get_database_client()
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def save_pipeline_state(self, pipeline_state: Stage1PipelineState) -> bool:
        """Save pipeline state to database"""
        try:
            # Convert to dict and handle datetime serialization
            state_dict = self._serialize_pipeline_state(pipeline_state)
            
            await self.database_client.put_item(
                table_name="stage1_pipeline_states",
                item=state_dict
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save pipeline state: {str(e)}")
            return False
    
    def _serialize_pipeline_state(self, pipeline_state: Stage1PipelineState) -> Dict[str, Any]:
        """Serialize pipeline state with proper datetime handling"""
        state_dict = pipeline_state.dict()
        
        # Convert datetime objects to ISO format strings
        if state_dict.get('started_at'):
            state_dict['started_at'] = state_dict['started_at'].isoformat()
        
        if state_dict.get('completed_at'):
            state_dict['completed_at'] = state_dict['completed_at'].isoformat()
        
        # Handle agent states datetime fields
        if 'agent_states' in state_dict:
            for agent_key, agent_state in state_dict['agent_states'].items():
                if agent_state.get('started_at'):
                    agent_state['started_at'] = agent_state['started_at'].isoformat()
                if agent_state.get('completed_at'):
                    agent_state['completed_at'] = agent_state['completed_at'].isoformat()
        
        return state_dict
    
    async def get_pipeline_status(self, request_id: str) -> Optional[Stage1PipelineState]:
        """Get current pipeline status"""
        try:
            state_data = await self.database_client.get_item(
                table_name="stage1_pipeline_states", 
                key={"request_id": request_id}
            )
            
            if state_data:
                # Deserialize datetime fields
                deserialized_data = self._deserialize_pipeline_state(state_data)
                return Stage1PipelineState(**deserialized_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get pipeline status: {str(e)}")
            return None
    
    def _deserialize_pipeline_state(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize pipeline state with proper datetime handling"""
        # Convert ISO format strings back to datetime objects
        if state_data.get('started_at') and isinstance(state_data['started_at'], str):
            try:
                state_data['started_at'] = datetime.fromisoformat(state_data['started_at'])
            except ValueError:
                state_data['started_at'] = None
        
        if state_data.get('completed_at') and isinstance(state_data['completed_at'], str):
            try:
                state_data['completed_at'] = datetime.fromisoformat(state_data['completed_at'])
            except ValueError:
                state_data['completed_at'] = None
        
        # Handle agent states datetime fields
        if 'agent_states' in state_data:
            for agent_key, agent_state in state_data['agent_states'].items():
                if agent_state.get('started_at') and isinstance(agent_state['started_at'], str):
                    try:
                        agent_state['started_at'] = datetime.fromisoformat(agent_state['started_at'])
                    except ValueError:
                        agent_state['started_at'] = None
                        
                if agent_state.get('completed_at') and isinstance(agent_state['completed_at'], str):
                    try:
                        agent_state['completed_at'] = datetime.fromisoformat(agent_state['completed_at'])
                    except ValueError:
                        agent_state['completed_at'] = None
        
        return state_data
    
    async def update_pipeline_status(self, request_id: str, status: Stage1Status, 
                                   current_agent: Optional[AgentType] = None) -> bool:
        """Update pipeline status"""
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if current_agent:
                update_data["current_agent"] = current_agent.value
            
            await self.database_client.update_item(
                table_name="stage1_pipeline_states",
                key={"request_id": request_id},
                update_data=update_data
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to update pipeline status: {str(e)}")
            return False
    
    async def list_active_pipelines(self) -> List[Stage1PipelineState]:
        """List all active (non-completed) pipelines"""
        try:
            # Query for active pipelines
            active_statuses = [
                Stage1Status.PENDING, 
                Stage1Status.AGENT1_PROCESSING,
                Stage1Status.AGENT2_PROCESSING, 
                Stage1Status.AGENT3_PROCESSING,
                Stage1Status.AGENT4_PROCESSING
            ]
            
            all_states = []
            for status in active_statuses:
                states = await self.database_client.query_items(
                    table_name="stage1_pipeline_states",
                    index_name="status-index",  # Assuming GSI exists
                    key_condition_expression="status = :status",
                    expression_attribute_values={":status": status.value}
                )
                all_states.extend(states)
            
            return [Stage1PipelineState(**state) for state in all_states]
            
        except Exception as e:
            logger.error(f"Failed to list active pipelines: {str(e)}")
            return []
    
    async def get_agent_results(self, request_id: str, agent_type: AgentType) -> Dict[str, Any]:
        """Get results from specific agent's table"""
        try:
            # Get table name for agent
            table_name = self._get_agent_table_name(agent_type)
            
            # Query agent results
            results = await self.database_client.query_items(
                table_name=table_name,
                key_condition_expression="request_id = :request_id",
                expression_attribute_values={":request_id": request_id}
            )
            
            return {
                "agent_type": agent_type.value,
                "table_name": table_name,
                "results_count": len(results),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Failed to get agent results: {str(e)}")
            return {"error": str(e)}
    
    async def retry_agent(self, request_id: str, agent_type: AgentType) -> bool:
        """Retry a specific failed agent"""
        try:
            # Get current pipeline state
            pipeline_state = await self.get_pipeline_status(request_id)
            if not pipeline_state:
                return False
            
            # Reset agent state
            agent_key = agent_type.value
            if agent_key in pipeline_state.agent_states:
                pipeline_state.agent_states[agent_key].status = Stage1Status.PENDING
                pipeline_state.agent_states[agent_key].errors = []
                pipeline_state.agent_states[agent_key].started_at = None
                pipeline_state.agent_states[agent_key].completed_at = None
            
            # Update pipeline status
            pipeline_state.status = Stage1Status.PENDING
            pipeline_state.current_agent = agent_type
            
            # Save updated state
            return await self.save_pipeline_state(pipeline_state)
            
        except Exception as e:
            logger.error(f"Failed to retry agent: {str(e)}")
            return False
    
    async def cleanup_completed_pipelines(self, max_age_hours: int = 24) -> int:
        """Clean up old completed pipelines"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            
            # Query completed pipelines older than cutoff
            completed_states = await self.database_client.query_items(
                table_name="stage1_pipeline_states",
                index_name="status-index",
                key_condition_expression="status = :status",
                filter_expression="completed_at < :cutoff_time",
                expression_attribute_values={
                    ":status": Stage1Status.COMPLETED.value,
                    ":cutoff_time": cutoff_time.isoformat()
                }
            )
            
            # Delete old states
            deleted_count = 0
            for state in completed_states:
                try:
                    await self.database_client.delete_item(
                        table_name="stage1_pipeline_states",
                        key={"request_id": state["request_id"]}
                    )
                    deleted_count += 1
                except Exception as e:
                    logger.warning(f"Failed to delete pipeline state {state['request_id']}: {str(e)}")
            
            logger.info(f"Cleaned up {deleted_count} completed pipeline states")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup completed pipelines: {str(e)}")
            return 0
    
    def _get_agent_table_name(self, agent_type: AgentType) -> str:
        """Get table name for specific agent"""
        table_map = {
            AgentType.DEDUPLICATION: "agent1_deduplication_results",
            AgentType.RELEVANCE: "agent2_relevance_results",
            AgentType.INSIGHTS: "agent3_insights_results",
            AgentType.IMPLICATIONS: "agent4_implications_results"
        }
        return table_map.get(agent_type, "unknown_agent_table") 