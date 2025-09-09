import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from ..agents.stage0_orchestrator.service import OrchestratorService
from ..agents.stage0_orchestrator.models import IngestionRequest, IngestionResponse
from ..config.market_intelligence_config import MarketIntelligenceConfig, MarketIntelligenceWorkflow, DEFAULT_SEMAGLUTIDE_CONFIG
from ..shared.utils.logger import get_logger

logger = get_logger(__name__)


class MarketIntelligenceService:
    """Specialized service for pharmaceutical market intelligence workflows"""
    
    def __init__(self, config: MarketIntelligenceConfig = None):
        self.config = config or DEFAULT_SEMAGLUTIDE_CONFIG
        self.workflow = MarketIntelligenceWorkflow(self.config)
        self.orchestrator = OrchestratorService()
    
    async def execute_semaglutide_intelligence(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute complete Semaglutide/Tirzepatide market intelligence workflow"""
        try:
            # Generate request ID if not provided
            if not request_id:
                request_id = f"sema_intel_{int(datetime.utcnow().timestamp())}_{str(uuid.uuid4())[:8]}"
            
            logger.info(f"Starting Semaglutide market intelligence workflow: {request_id}")
            
            # Get workflow configuration
            workflow_summary = self.workflow.get_workflow_summary()
            logger.info(f"Workflow will execute {workflow_summary['api_call_estimates']['total_calls']} total API calls")
            
            # Execute searches for each source in parallel
            search_tasks = []
            search_requests = self.workflow.generate_search_requests()
            
            for i, search_req in enumerate(search_requests):
                # Create individual ingestion request for each source
                ingestion_request = IngestionRequest(
                    query=search_req["query"],
                    num_results=search_req["num_results"],
                    extraction_mode=self.config.extraction_mode,
                    request_id=f"{request_id}_source_{i}_{search_req['source_name'].lower()}"
                )
                
                # Add source metadata to filters
                ingestion_request.filters = {
                    "source_name": search_req["source_name"],
                    "source_type": search_req["source_type"],
                    "base_url": search_req["base_url"],
                    "priority": search_req["priority"],
                    "market_intelligence_parent": request_id
                }
                
                task = self.orchestrator.process_request(
                    query=ingestion_request.query,
                    num_results=ingestion_request.num_results,
                    extraction_mode=ingestion_request.extraction_mode,
                    request_id=ingestion_request.request_id,
                    filters=ingestion_request.filters
                )
                search_tasks.append((search_req["source_name"], task))
            
            # Execute all searches in parallel
            logger.info(f"Executing {len(search_tasks)} parallel source searches")
            source_results = {}
            
            for source_name, task in search_tasks:
                try:
                    result = await task
                    source_results[source_name] = result
                    logger.info(f"Completed search for {source_name}: {result.content_extracted} content items extracted")
                except Exception as e:
                    logger.error(f"Search failed for {source_name}: {str(e)}")
                    source_results[source_name] = {"error": str(e), "status": "failed"}
            
            # Aggregate results across all sources
            aggregated_results = await self._aggregate_market_intelligence(request_id, source_results)
            
            # Generate final market intelligence report
            final_report = await self._generate_intelligence_report(request_id, aggregated_results, workflow_summary)
            
            logger.info(f"Market intelligence workflow completed: {request_id}")
            return final_report
            
        except Exception as e:
            logger.error(f"Market intelligence workflow failed: {str(e)}")
            raise Exception(f"Market intelligence execution failed: {str(e)}")
    
    async def _aggregate_market_intelligence(self, request_id: str, source_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate results from all sources into unified intelligence"""
        try:
            aggregated = {
                "request_id": request_id,
                "total_sources": len(source_results),
                "successful_sources": 0,
                "failed_sources": 0,
                "total_urls_found": 0,
                "total_content_extracted": 0,
                "content_by_source": {},
                "content_by_type": {"regulatory": [], "clinical": [], "academic": []},
                "high_quality_content": [],
                "all_content": [],
                "processing_summary": {}
            }
            
            for source_name, result in source_results.items():
                if isinstance(result, dict) and "error" in result:
                    aggregated["failed_sources"] += 1
                    aggregated["processing_summary"][source_name] = {
                        "status": "failed",
                        "error": result["error"]
                    }
                    continue
                
                # Successful result
                aggregated["successful_sources"] += 1
                aggregated["total_urls_found"] += result.urls_found
                aggregated["total_content_extracted"] += result.content_extracted
                
                # Categorize content by source
                source_content = {
                    "source_name": source_name,
                    "urls_found": result.urls_found,
                    "content_extracted": result.content_extracted,
                    "high_quality_count": len(result.high_quality_content),
                    "content_items": result.high_quality_content
                }
                aggregated["content_by_source"][source_name] = source_content
                
                # Categorize by source type
                source_type = result.filters.get("source_type", "unknown") if hasattr(result, 'filters') else "unknown"
                if source_type in aggregated["content_by_type"]:
                    aggregated["content_by_type"][source_type].extend(result.high_quality_content)
                
                # Add to overall collections
                aggregated["high_quality_content"].extend(result.high_quality_content)
                aggregated["all_content"].extend(result.aggregated_content)
                
                # Processing summary
                aggregated["processing_summary"][source_name] = {
                    "status": "completed",
                    "urls_found": result.urls_found,
                    "content_extracted": result.content_extracted,
                    "processing_time": result.processing_time,
                    "success_rate": result.get_success_rate()
                }
            
            # Calculate overall statistics
            aggregated["overall_success_rate"] = (
                aggregated["total_content_extracted"] / aggregated["total_urls_found"] * 100
                if aggregated["total_urls_found"] > 0 else 0
            )
            
            # Deduplicate content by URL
            aggregated["deduplicated_content"] = self._deduplicate_content(aggregated["high_quality_content"])
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Failed to aggregate market intelligence: {str(e)}")
            raise
    
    def _deduplicate_content(self, content_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate content based on URL"""
        seen_urls = set()
        deduplicated = []
        
        for item in content_items:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                deduplicated.append(item)
        
        logger.info(f"Deduplicated {len(content_items)} items to {len(deduplicated)} unique items")
        return deduplicated
    
    async def _generate_intelligence_report(self, request_id: str, aggregated_results: Dict[str, Any], workflow_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final market intelligence report"""
        try:
            report = {
                "report_metadata": {
                    "request_id": request_id,
                    "title": self.config.title,
                    "objective": self.config.objective,
                    "priority": self.config.priority,
                    "created_by": self.config.created_by,
                    "generated_at": datetime.utcnow().isoformat(),
                    "time_range": {
                        "start": self.config.start_date.isoformat(),
                        "end": self.config.end_date.isoformat()
                    }
                },
                
                "execution_summary": {
                    "workflow_config": workflow_summary["workflow_config"],
                    "api_calls_executed": workflow_summary["api_call_estimates"],
                    "sources_processed": aggregated_results["total_sources"],
                    "successful_sources": aggregated_results["successful_sources"],
                    "failed_sources": aggregated_results["failed_sources"],
                    "total_urls_discovered": aggregated_results["total_urls_found"],
                    "total_content_extracted": aggregated_results["total_content_extracted"],
                    "overall_success_rate": aggregated_results["overall_success_rate"],
                    "unique_content_items": len(aggregated_results["deduplicated_content"])
                },
                
                "intelligence_data": {
                    "regulatory_content": {
                        "source": "FDA",
                        "count": len(aggregated_results["content_by_type"]["regulatory"]),
                        "items": aggregated_results["content_by_type"]["regulatory"]
                    },
                    "clinical_content": {
                        "source": "ClinicalTrials.gov", 
                        "count": len(aggregated_results["content_by_type"]["clinical"]),
                        "items": aggregated_results["content_by_type"]["clinical"]
                    },
                    "academic_content": {
                        "source": "NIH",
                        "count": len(aggregated_results["content_by_type"]["academic"]),
                        "items": aggregated_results["content_by_type"]["academic"]
                    }
                },
                
                "content_analysis": {
                    "high_quality_content": aggregated_results["deduplicated_content"],
                    "content_by_source": aggregated_results["content_by_source"],
                    "quality_metrics": {
                        "total_items": len(aggregated_results["all_content"]),
                        "high_quality_items": len(aggregated_results["high_quality_content"]),
                        "unique_items": len(aggregated_results["deduplicated_content"]),
                        "quality_rate": len(aggregated_results["high_quality_content"]) / len(aggregated_results["all_content"]) * 100 if aggregated_results["all_content"] else 0
                    }
                },
                
                "processing_details": aggregated_results["processing_summary"],
                
                "keywords_used": self.config.primary_keywords,
                
                "storage_info": {
                    "report_path": f"market_intelligence/{request_id}/final_report.json",
                    "raw_data_path": f"market_intelligence/{request_id}/raw_data.json"
                }
            }
            
            # Add structured output examples as requested
            report["structured_outputs"] = []
            for item in aggregated_results["deduplicated_content"][:5]:  # First 5 as examples
                structured_item = {
                    "source": self._get_source_from_url(item.get("url", "")),
                    "url": item.get("url", ""),
                    "summary": item.get("content", "")[:500] + "..." if len(item.get("content", "")) > 500 else item.get("content", ""),
                    "category": self._categorize_content(item),
                    "title": item.get("title", ""),
                    "extraction_confidence": item.get("extraction_confidence", 0.0),
                    "word_count": item.get("word_count", 0)
                }
                report["structured_outputs"].append(structured_item)
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate intelligence report: {str(e)}")
            raise
    
    def _get_source_from_url(self, url: str) -> str:
        """Determine source name from URL"""
        if "fda.gov" in url:
            return "FDA"
        elif "nih.gov" in url:
            return "NIH"
        elif "clinicaltrials.gov" in url:
            return "ClinicalTrials.gov"
        else:
            return "Unknown"
    
    def _categorize_content(self, item: Dict[str, Any]) -> str:
        """Categorize content based on source and content analysis"""
        url = item.get("url", "").lower()
        content = item.get("content", "").lower()
        
        if "fda.gov" in url or "regulatory" in content:
            return "regulatory"
        elif "clinicaltrials.gov" in url or "clinical trial" in content:
            return "clinical"
        elif "nih.gov" in url or "research" in content or "study" in content:
            return "academic"
        else:
            return "general"
    
    async def get_workflow_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of market intelligence workflow"""
        try:
            status = await self.orchestrator.get_status(request_id)
            if status:
                return {
                    "request_id": request_id,
                    "status": status.status,
                    "current_stage": status.current_stage,
                    "progress_percentage": status.progress_percentage,
                    "urls_found": status.urls_found,
                    "content_extracted": status.content_extracted,
                    "errors": status.errors,
                    "warnings": status.warnings
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get workflow status: {str(e)}")
            return None
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get current configuration summary"""
        return self.workflow.get_workflow_summary() 