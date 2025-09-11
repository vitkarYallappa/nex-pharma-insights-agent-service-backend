"""
Temporary Market Intelligence Service for Root Orchestrator

This service integrates with Perplexity API to provide real market intelligence
capabilities while maintaining compatibility with the existing workflow.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import uuid

from . import MarketIntelligenceRequest
from .temp_logger import get_logger
from .temp_service_factory import ServiceFactory

logger = get_logger(__name__)


class MarketIntelligenceService:
    """
    Market Intelligence Service with Perplexity API integration.
    
    This service provides real market intelligence capabilities using Perplexity API
    for content generation, analysis, and insights while maintaining the existing workflow.
    """
    
    def __init__(self):
        self.processing_time = 10  # Base processing time
        self.perplexity_client = ServiceFactory.get_perplexity_client()
        self.serp_client = ServiceFactory.get_serp_client()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
        
        # Default source domains for URL discovery
        self.source_domains = [
            "reuters.com"
        ]
        
        # Default keywords for semaglutide intelligence
        self.semaglutide_keywords = [
            "semaglutide", "tirzepatide", "wegovy", "ozempic", "mounjaro"
        ]
    
    async def execute_semaglutide_intelligence(self, request_id: str) -> Dict[str, Any]:
        """
        Execute the Semaglutide market intelligence workflow using Perplexity API.
        
        Args:
            request_id: The request identifier
            
        Returns:
            Dict[str, Any]: Market intelligence results with Perplexity-generated content
        """
        try:
            logger.info(f"Starting Semaglutide intelligence workflow for request: {request_id}")
            
            # Stage 0: URL Discovery via SERP
            logger.info(f"🚀 Stage 0: Starting URL Discovery for {request_id}")
            await self._simulate_stage("url_discovery", 1)
            discovered_urls = await self._discover_relevant_urls(request_id)
            logger.info(f"🔍 Stage 0 Complete: Found {discovered_urls.get('total_urls_discovered', 0)} URLs")
            
            # Stage 1: Content Extraction and Summary Storage
            logger.info(f"🚀 Stage 1: Starting Content Extraction for {request_id}")
            await self._simulate_stage("content_extraction", 2)
            content_summary = await self._extract_and_store_content(request_id, discovered_urls)
            logger.info(f"📄 Stage 1 Complete: Extracted {content_summary.get('successful_extractions', 0)} content items")
            
            # Stage 2: Final Summary Assembly  
            logger.info(f"🚀 Stage 2: Starting Summary Assembly for {request_id}")
            await self._simulate_stage("summary_assembly", 1)
            results = await self._assemble_final_summary(request_id, discovered_urls, content_summary)
            logger.info(f"📋 Stage 2 Complete: Assembly status = {results.get('status', 'unknown')}")
            
            logger.info(f"Semaglutide intelligence workflow completed for request: {request_id}")
            return results
            
        except Exception as e:
            logger.error(f"Semaglutide intelligence workflow failed for request {request_id}: {e}")
            raise
    
    async def _simulate_stage(self, stage_name: str, duration: int):
        """Simulate a processing stage with delay"""
        logger.info(f"Processing stage: {stage_name}")
        await asyncio.sleep(duration)
    
    def _generate_production_results(self, request_id: str) -> Dict[str, Any]:
        """Generate production results structure"""
        
        # Production report data structure
        report_data = {
            "executive_summary": "Market intelligence analysis completed successfully.",
            "key_findings": [],
            "sources_analyzed": [],
            "content_breakdown": {},
            "quality_metrics": {}
        }
        
        return {
            "request_id": request_id,
            "status": "completed",
            "generated_at": datetime.utcnow().isoformat(),
            "processing_time": self.processing_time,
            "report_data": report_data,
            "metadata": {
                "version": "1.0",
                "service": "MarketIntelligenceService",
                "workflow": "semaglutide_intelligence"
            }
        }
    
    async def _discover_relevant_urls(self, request_id: str) -> Dict[str, Any]:
        """Discover relevant URLs using SERP API"""
        try:
            logger.info(f"Starting URL discovery for request: {request_id}")
            
            discovered_urls = []
            total_searches = 0
            
            # Search each domain with ALL semaglutide keywords at once
            for domain in self.source_domains[:1]:  # Limit to top 3 domains for efficiency
                try:
                    source_config = {"name": domain, "type": "domain", "url": f"https://{domain}"}
                    
                    # Generate and log the SERP URL for debugging
                    serp_url = self.serp_client.build_serp_url(
                        keywords=self.semaglutide_keywords,  # Send all keywords at once
                        source=source_config,
                        date_filter="cdr:1"  # Custom date range filter
                    )
                    logger.info(f"🔗 Generated SERP URL: {serp_url}")
                    
                    # Use SERP API to search with ALL keywords at once
                    response = await self.serp_client.search_with_query_builder(
                        keywords=self.semaglutide_keywords,  # Send all keywords at once
                        source=source_config,
                        date_filter="cdr:1"  # Add date filter for recent results
                    )
                    
                    total_searches += 1
                    
                    # Extract URLs from SERP results
                    if response and response.results:
                        for result in response.results[:2]:  # Top 5 results per domain
                            if result.url and result.url not in discovered_urls:
                                discovered_urls.append(result.url)
                    
                    # Rate limiting between domains
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.warning(f"SERP search failed for {domain}: {e}")
                    continue
            
            logger.info(f"URL discovery completed: {len(discovered_urls)} URLs found from {total_searches} searches")
            
            return {
                "discovered_urls": discovered_urls[:2],  # Limit to top 10 URLs
                "total_urls_discovered": len(discovered_urls),
                "searches_performed": total_searches,
                "domains_searched": self.source_domains[:3],
                "keywords_used": self.semaglutide_keywords,  # Now using all keywords
                "discovery_completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"URL discovery failed: {e}")
            return {
                "discovered_urls": [],
                "total_urls_discovered": 0,
                "searches_performed": 0,
                "error": str(e),
                "discovery_completed_at": datetime.utcnow().isoformat()
            }
    
    async def _extract_and_store_content(self, request_id: str, discovered_urls: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content from discovered URLs and store summaries"""
        try:
            import uuid
            from datetime import datetime
            import re
            
            logger.info(f"🔍 Starting content extraction for request: {request_id}")
            
            extracted_content = []
            urls_to_process = discovered_urls.get("discovered_urls", [])[:5]  # Process top 5 URLs
            
            logger.info(f"📋 URLs to process: {len(urls_to_process)} URLs")
            logger.info(f"📋 URL list: {urls_to_process}")
            
            for i, url in enumerate(urls_to_process, 1):
                try:
                    logger.info(f"🌐 [{i}/{len(urls_to_process)}] Processing URL: {url}")
                    
                    # Extract content using Perplexity
                    logger.info(f"🔄 Calling Perplexity API for: {url}")
                    content = await self.perplexity_client.extract_single_url(url)
                    logger.info(f"✅ Perplexity response received for: {url}")
                    
                    if content and content.content:
                        logger.info(f"📄 Content extracted successfully: {len(content.content)} chars")
                        # Generate storage path: request_id/uuid/sanitized_url_timestamp
                        content_uuid = str(uuid.uuid4())
                        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                        sanitized_url = re.sub(r'[^a-zA-Z0-9_-]', '_', url.replace('https://', '').replace('http://', ''))
                        
                        storage_path = f"{request_id}/{content_uuid}/{sanitized_url}_{timestamp}.json"
                        
                        # Prepare content for storage
                        content_data = {
                            "url": url,
                            "title": content.title,
                            "summary": content.content,
                            "extracted_at": datetime.utcnow().isoformat(),
                            "word_count": content.word_count,
                            "confidence": content.extraction_confidence,
                            "metadata": content.metadata
                        }
                        
                        # Store in S3 using upload_content method
                        import json
                        content_json = json.dumps(content_data, indent=2)
                        success = await self.storage_client.upload_content(
                            content_json.encode('utf-8'),
                            storage_path,
                            'application/json'
                        )
                        
                        if success:
                            extracted_content.append({
                                "url": url,
                                "storage_path": storage_path,
                                "title": content.title,
                                "word_count": content.word_count,
                                "confidence": content.extraction_confidence
                            })
                            logger.info(f"💾 ✅ Stored content for {url} at {storage_path}")
                        else:
                            logger.error(f"💾 ❌ Failed to store content for {url}")
                    else:
                        logger.warning(f"📄 ❌ No content extracted from {url}")
                        
                except Exception as e:
                    logger.error(f"🚨 Exception processing {url}: {e}")
                    import traceback
                    logger.error(f"🚨 Traceback: {traceback.format_exc()}")
                    continue
            
            logger.info(f"🎯 Content extraction completed: {len(extracted_content)}/{len(urls_to_process)} successful")
            
            # Create and save Perplexity summary
            await self._create_perplexity_summary(request_id, extracted_content, urls_to_process)
            
            return {
                "extracted_content": extracted_content,
                "total_processed": len(urls_to_process),
                "successful_extractions": len(extracted_content),
                "storage_base_path": request_id
            }
            
        except Exception as e:
            logger.error(f"🚨 Content extraction failed: {e}")
            import traceback
            logger.error(f"🚨 Full traceback: {traceback.format_exc()}")
            return {
                "extracted_content": [],
                "total_processed": 0,
                "successful_extractions": 0,
                "error": str(e)
            }
    
    async def _create_perplexity_summary(self, request_id: str, extracted_content: List[Dict[str, Any]], urls_processed: List[str]) -> bool:
        """Create and save Perplexity extraction summaries using existing content_summary table"""
        try:
            # Import the existing content summary model
            from ..agent_service_module.agents.stage0_perplexity.content_summary_model import ContentSummaryModel
            
            logger.info(f"📊 Creating Perplexity summaries for request: {request_id}")
            
            summaries_created = 0
            
            # Create individual summaries for each extracted content
            for i, item in enumerate(extracted_content):
                try:
                    # Generate IDs for the summary
                    url_id = str(uuid.uuid4())
                    content_id = str(uuid.uuid4())
                    
                    # Create summary text from the extracted content
                    title = item.get('title', 'Untitled')
                    url = item.get('url', 'Unknown URL')
                    word_count = item.get('word_count', 0)
                    confidence = item.get('confidence', 0.0)
                    
                    summary_text = f"Content extracted from {title} ({url}). Word count: {word_count}, Confidence: {confidence:.2f}"
                    
                    # Use the storage path as the file path
                    file_path = item.get('storage_path', f"perplexity_content/{request_id}/{i}.json")
                    
                    # Create content summary using existing model
                    content_summary = ContentSummaryModel.create_new(
                        url_id=url_id,
                        content_id=content_id,
                        summary_text=summary_text,
                        summary_content_file_path=file_path,
                        confidence_score=confidence,
                        version=1,
                        is_canonical=True,
                        preferred_choice=True,
                        created_by=f"perplexity_extractor_{request_id}"
                    )
                    
                    # Save to database using the existing database client
                    table_name = ContentSummaryModel.table_name()
                    success = await self.database_client.put_item(table_name, content_summary.to_dict())
                    
                    if success:
                        summaries_created += 1
                        logger.info(f"📊 ✅ Content summary saved: {title[:50]}...")
                    else:
                        logger.error(f"📊 ❌ Failed to save content summary: {title[:50]}...")
                        
                except Exception as item_error:
                    logger.error(f"📊 🚨 Error processing item {i}: {item_error}")
                    continue
            
            # Create an overall summary for the request
            if summaries_created > 0:
                overall_summary_text = f"Perplexity extraction completed for request {request_id}. Successfully processed {summaries_created}/{len(extracted_content)} URLs."
                
                overall_summary = ContentSummaryModel.create_new(
                    url_id=str(uuid.uuid4()),
                    content_id=str(uuid.uuid4()),
                    summary_text=overall_summary_text,
                    summary_content_file_path=f"{request_id}/perplexity_overall_summary.json",
                    confidence_score=summaries_created / len(extracted_content) if extracted_content else 0.0,
                    version=1,
                    is_canonical=True,
                    preferred_choice=True,
                                        created_by=f"perplexity_orchestrator_{request_id}"
                )
                
                table_name = ContentSummaryModel.table_name()
                await self.database_client.put_item(table_name, overall_summary.to_dict())
                
                logger.info(f"📊 ✅ Overall Perplexity summary saved for request: {request_id}")
                logger.info(f"📊 Summary: {overall_summary_text}")
            
            return summaries_created > 0
            
        except Exception as e:
            logger.error(f"📊 🚨 Error creating Perplexity summaries: {e}")
            import traceback
            logger.error(f"📊 🚨 Traceback: {traceback.format_exc()}")
            return False
    
    async def _assemble_final_summary(self, request_id: str, discovered_urls: Dict[str, Any], content_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Assemble final summary for Stage1 processing"""
        try:
            # Store summary metadata for Stage1 orchestrator
            summary_path = f"{request_id}/stage0_summary.json"
            
            summary_data = {
                "request_id": request_id,
                "stage0_completed_at": datetime.utcnow().isoformat(),
                "url_discovery": discovered_urls,
                "content_extraction": content_summary,
                "ready_for_stage1": True,
                "extracted_files": [item["storage_path"] for item in content_summary.get("extracted_content", [])]
            }
            
            # Store stage0 summary
            import json
            summary_json = json.dumps(summary_data, indent=2)
            await self.storage_client.upload_content(
                summary_json.encode('utf-8'),
                summary_path,
                'application/json'
            )
            
            return {
                "request_id": request_id,
                "status": "completed",
                "summary_path": summary_path,
                "urls_discovered": discovered_urls.get("total_urls_discovered", 0),
                "content_extracted": content_summary.get("successful_extractions", 0),
                "ready_for_agents": True
            }
            
        except Exception as e:
            logger.error(f"Final summary assembly failed: {e}")
            return {
                "request_id": request_id,
                "status": "failed",
                "error": str(e)
            } 