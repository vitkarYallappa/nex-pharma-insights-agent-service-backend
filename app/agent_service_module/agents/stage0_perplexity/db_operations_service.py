"""
Perplexity Database Operations Service
Centralized service for all Perplexity-related database operations
Handles: content_summary, content_repository, content_url_mapping, and S3 storage
"""

import json
import uuid
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...config.service_factory import ServiceFactory
from .content_summary_model import ContentSummaryModel
from .content_repository_model import ContentRepositoryModel
from .content_url_mapping_model import ContentUrlMappingModel
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class PerplexityDbOperationsService:
    """
    Centralized database operations service for Perplexity
    
    Handles ALL storage operations:
    1. Content Summary storage
    2. Content Repository storage  
    3. Content URL Mapping storage
    4. S3/MinIO file storage
    5. Perplexity results storage
    """
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def store_perplexity_extraction_complete(self, request_id: str, extracted_content: List[Dict[str, Any]], 
                                                  request_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Store complete Perplexity extraction with all related data
        
        Args:
            request_id: The request identifier
            extracted_content: List of extracted content items
            request_details: Optional request metadata
            
        Returns:
            Dict with storage results and UUIDs
        """
        try:
            logger.info(f"🗄️ Starting complete Perplexity storage for request: {request_id}")
            
            # Generate shared UUID for all related records
            shared_uuid = str(uuid.uuid4())
            
            # Default request details if not provided
            if not request_details:
                request_details = {
                    "request_id": request_id,
                    "project_id": "default_project",
                    "user_id": "default_user",
                    "request_type": "perplexity_extraction"
                }
            
            storage_results = {
                "shared_uuid": shared_uuid,
                "request_id": request_id,
                "stored_items": [],
                "s3_files": [],
                "database_records": 0,
                "errors": []
            }
            
            # Store each content item with all related data
            for i, content_item in enumerate(extracted_content):
                try:
                    item_result = await self._store_single_content_item(
                        content_item, request_id, request_details, shared_uuid, i
                    )
                    storage_results["stored_items"].append(item_result)
                    storage_results["s3_files"].extend(item_result.get("s3_files", []))
                    storage_results["database_records"] += item_result.get("db_records", 0)
                    
                except Exception as e:
                    error_msg = f"Failed to store content item {i}: {str(e)}"
                    logger.error(error_msg)
                    storage_results["errors"].append(error_msg)
            
            # Store aggregated Perplexity results
            await self._store_perplexity_results_summary(request_id, extracted_content, storage_results)
            
            logger.info(f"✅ Completed Perplexity storage: {storage_results['database_records']} DB records, {len(storage_results['s3_files'])} S3 files")
            return storage_results
            
        except Exception as e:
            logger.error(f"❌ Error in complete Perplexity storage: {str(e)}")
            raise
    
    async def _store_single_content_item(self, content_item: Dict[str, Any], request_id: str, 
                                       request_details: Dict[str, Any], shared_uuid: str, index: int) -> Dict[str, Any]:
        """Store a single content item across all models"""
        
        # Generate unique UUID for this content item
        item_uuid = f"{shared_uuid}_{index}"
        
        # Extract content details
        url = content_item.get('url', f'unknown_url_{index}')
        title = content_item.get('title', f'Untitled Content {index}')
        content_text = content_item.get('content', content_item.get('summary', ''))
        word_count = content_item.get('word_count', len(content_text.split()) if content_text else 0)
        confidence = content_item.get('confidence', content_item.get('extraction_confidence', 0.8))
        
        # Create content hash
        content_hash = hashlib.md5(content_text.encode('utf-8')).hexdigest()
        
        project_id = request_details.get('project_id', 'unknown')
        user_id = request_details.get('user_id', 'unknown')
        
        item_result = {
            "item_uuid": item_uuid,
            "url": url,
            "title": title,
            "s3_files": [],
            "db_records": 0
        }
        
        try:
            # 1. Store content in S3/MinIO
            s3_path = await self._store_content_in_s3(content_item, request_id, item_uuid, index)
            if s3_path:
                item_result["s3_files"].append(s3_path)
            
            # 2. Store in ContentSummaryModel
            await self._store_content_summary(
                item_uuid, content_text, s3_path, confidence, 
                request_id, project_id, user_id
            )
            item_result["db_records"] += 1
            
            # 3. Store in ContentRepositoryModel  
            await self._store_content_repository(
                item_uuid, request_id, project_id, url, title, 
                content_hash, confidence
            )
            item_result["db_records"] += 1
            
            # 4. Store in ContentUrlMappingModel
            await self._store_content_url_mapping(
                item_uuid, url, title, confidence
            )
            item_result["db_records"] += 1
            
            logger.info(f"📦 Stored content item {index}: {title[:50]}...")
            
        except Exception as e:
            logger.error(f"Error storing content item {index}: {str(e)}")
            raise
        
        return item_result
    
    async def _store_content_in_s3(self, content_item: Dict[str, Any], request_id: str, 
                                  item_uuid: str, index: int) -> Optional[str]:
        """Store content in S3/MinIO"""
        try:
            # Create S3 path
            s3_key = f"perplexity_content/{request_id}/{item_uuid}.json"
            
            # Prepare content data
            content_data = {
                "item_uuid": item_uuid,
                "request_id": request_id,
                "index": index,
                "url": content_item.get('url'),
                "title": content_item.get('title'),
                "content": content_item.get('content', content_item.get('summary', '')),
                "word_count": content_item.get('word_count'),
                "confidence": content_item.get('confidence', content_item.get('extraction_confidence')),
                "metadata": content_item.get('metadata', {}),
                "extracted_at": datetime.utcnow().isoformat()
            }
            
            # Store in S3
            content_json = json.dumps(content_data, indent=2)
            success = await self.storage_client.upload_content(
                content_json.encode('utf-8'),
                s3_key,
                'application/json'
            )
            
            if success:
                logger.debug(f"💾 Stored content in S3: {s3_key}")
                return s3_key
            else:
                logger.error(f"Failed to store content in S3: {s3_key}")
                return None
                
        except Exception as e:
            logger.error(f"Error storing content in S3: {str(e)}")
            return None
    
    async def _store_content_summary(self, item_uuid: str, content_text: str, file_path: Optional[str],
                                   confidence: float, request_id: str, project_id: str, user_id: str):
        """Store in ContentSummaryModel"""
        try:
            # Create summary (first 500 chars)
            summary_text = content_text[:500] + "..." if len(content_text) > 500 else content_text
            
            created_by_info = f"perplexity_extractor_{request_id}_project_{project_id}_user_{user_id}"
            
            content_summary = ContentSummaryModel.create_new(
                url_id=item_uuid,
                content_id=item_uuid,
                summary_text=summary_text,
                summary_content_file_path=file_path or f"perplexity_content/{request_id}/{item_uuid}.json",
                confidence_score=confidence,
                version=1,
                is_canonical=True,
                preferred_choice=True,
                created_by=created_by_info
            )
            
            # Override pk to use item_uuid
            content_summary.pk = item_uuid
            
            # Store in database
            table_name = ContentSummaryModel.table_name()
            await self.database_client.put_item(table_name, content_summary.to_dict())
            
            logger.debug(f"📝 Stored ContentSummary: {item_uuid}")
            
        except Exception as e:
            logger.error(f"Error storing ContentSummary: {str(e)}")
            raise
    
    async def _store_content_repository(self, item_uuid: str, request_id: str, project_id: str,
                                      url: str, title: str, content_hash: str, confidence: float):
        """Store in ContentRepositoryModel"""
        try:
            # Determine relevance type based on confidence
            if confidence >= 0.8:
                relevance_type = "high"
            elif confidence >= 0.6:
                relevance_type = "medium"
            else:
                relevance_type = "low"
            
            content_repo = ContentRepositoryModel.create_new(
                request_id=request_id,
                project_id=project_id,
                canonical_url=url,
                title=title,
                content_hash=content_hash,
                source_type="perplexity_extraction",
                relevance_type=relevance_type,
                version=1,
                is_canonical=True
            )
            
            # Override pk to use item_uuid
            content_repo.pk = item_uuid
            
            # Store in database
            table_name = ContentRepositoryModel.table_name()
            await self.database_client.put_item(table_name, content_repo.to_dict())
            
            logger.debug(f"🗂️ Stored ContentRepository: {item_uuid}")
            
        except Exception as e:
            logger.error(f"Error storing ContentRepository: {str(e)}")
            raise
    
    async def _store_content_url_mapping(self, item_uuid: str, url: str, title: str, confidence: float):
        """Store in ContentUrlMappingModel"""
        try:
            # Extract domain from URL
            from urllib.parse import urlparse
            try:
                domain = urlparse(url).netloc
            except:
                domain = "unknown_domain"
            
            url_mapping = ContentUrlMappingModel.create_new(
                discovered_url=url,
                title=title,
                content_id=item_uuid,
                source_domain=domain,
                is_canonical=True,
                dedup_confidence=confidence,
                dedup_method="perplexity_extraction"
            )
            
            # Override pk to use item_uuid
            url_mapping.pk = item_uuid
            
            # Store in database
            table_name = ContentUrlMappingModel.table_name()
            await self.database_client.put_item(table_name, url_mapping.to_dict())
            
            logger.debug(f"🔗 Stored ContentUrlMapping: {item_uuid}")
            
        except Exception as e:
            logger.error(f"Error storing ContentUrlMapping: {str(e)}")
            raise
    
    async def _store_perplexity_results_summary(self, request_id: str, extracted_content: List[Dict[str, Any]], 
                                              storage_results: Dict[str, Any]):
        """Store aggregated Perplexity results summary"""
        try:
            # Create summary results
            summary_data = {
                "request_id": request_id,
                "shared_uuid": storage_results["shared_uuid"],
                "total_items": len(extracted_content),
                "successful_items": len(storage_results["stored_items"]),
                "failed_items": len(storage_results["errors"]),
                "database_records": storage_results["database_records"],
                "s3_files": storage_results["s3_files"],
                "errors": storage_results["errors"],
                "processing_completed_at": datetime.utcnow().isoformat(),
                "items_summary": [
                    {
                        "uuid": item.get("item_uuid"),
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "s3_files": item.get("s3_files", [])
                    }
                    for item in storage_results["stored_items"]
                ]
            }
            
            # Store summary in S3
            summary_key = f"perplexity_results/{request_id}.json"
            summary_json = json.dumps(summary_data, indent=2)
            
            success = await self.storage_client.upload_content(
                summary_json.encode('utf-8'),
                summary_key,
                'application/json'
            )
            
            if success:
                logger.info(f"📊 Stored Perplexity results summary: {summary_key}")
            else:
                logger.error(f"Failed to store Perplexity results summary: {summary_key}")
                
        except Exception as e:
            logger.error(f"Error storing Perplexity results summary: {str(e)}")
    
    async def get_content_by_request_id(self, request_id: str) -> List[Dict[str, Any]]:
        """Retrieve all content for a request ID"""
        try:
            # Get from S3 summary first
            summary_key = f"perplexity_results/{request_id}.json"
            content_bytes = await self.storage_client.get_content(summary_key)
            
            if content_bytes:
                summary_data = json.loads(content_bytes.decode('utf-8'))
                return summary_data.get("items_summary", [])
            
            # Fallback to database query if needed
            logger.warning(f"No S3 summary found for {request_id}, querying database")
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving content for request {request_id}: {str(e)}")
            return [] 