# Agent 1 Deduplication Implementation

## 10-Line Prompt:
Create content deduplication agent that processes extracted content from Stage 0 to identify and cluster similar articles into parent-child relationships, includes semantic similarity analysis using Amazon Titan embeddings with cosine similarity calculations, hierarchical clustering algorithm that groups similar content based on configurable similarity thresholds, real OpenAI/Bedrock API integration for generating comprehensive parent summaries from clustered content, mock implementations for testing with predefined similarity patterns and synthetic clustering results, response processing that validates clustering quality and generates parent-child metadata, service orchestration that manages the complete deduplication pipeline from embedding generation to parent creation, storage operations that save clustered content and embeddings for downstream agents, database operations that track parent-child relationships and clustering metadata in knowledge base, and environment-based configuration supporting both real and mock implementations for development and production deployment.

## What it covers: 
Content clustering, similarity analysis, parent summary generation, embedding management
## Methods: 
Semantic embeddings, cosine similarity, hierarchical clustering, content consolidation
## Why: 
Eliminate duplicate content, create consolidated summaries, improve data quality

---

## models.py
```python
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class SimilarityThreshold(str, Enum):
    EXACT_DUPLICATE = "exact_duplicate"  # 0.95+
    SAME_STORY = "same_story"           # 0.85-0.95
    RELATED_CONTENT = "related_content"  # 0.70-0.85
    UNIQUE_CONTENT = "unique_content"    # <0.70

class ContentItem(BaseModel):
    """Individual content item for deduplication"""
    id: str = Field(..., description="Unique content identifier")
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Content title")
    content: str = Field(..., description="Full content text")
    summary: str = Field(..., description="Content summary")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    word_count: int = Field(default=0)
    extraction_confidence: float = Field(default=0.0)
    
    # Deduplication fields
    embedding: Optional[List[float]] = Field(default=None, description="Content embedding vector")
    cluster_id: Optional[str] = Field(default=None, description="Assigned cluster ID")
    parent_id: Optional[str] = Field(default=None, description="Parent content ID if duplicate")
    similarity_scores: Dict[str, float] = Field(default_factory=dict, description="Similarity to other content")
    is_parent: bool = Field(default=False, description="Is this a parent summary")
    child_count: int = Field(default=0, description="Number of child items")

class ContentCluster(BaseModel):
    """Group of similar content items"""
    cluster_id: str = Field(..., description="Cluster identifier")
    content_items: List[ContentItem] = Field(..., description="Items in cluster")
    parent_summary: Optional[str] = Field(default=None, description="Generated parent summary")
    cluster_confidence: float = Field(default=0.0, description="Clustering confidence")
    similarity_threshold: SimilarityThreshold = Field(..., description="Similarity level")
    centroid_embedding: Optional[List[float]] = Field(default=None, description="Cluster centroid")
    
    # Metadata
    average_confidence: float = Field(default=0.0)
    total_word_count: int = Field(default=0)
    source_diversity: int = Field(default=0, description="Number of unique domains")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_metrics(self):
        """Calculate cluster metrics"""
        if self.content_items:
            confidences = [item.extraction_confidence for item in self.content_items]
            self.average_confidence = sum(confidences) / len(confidences)
            
            self.total_word_count = sum(item.word_count for item in self.content_items)
            
            domains = set()
            for item in self.content_items:
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(item.url).netloc
                    domains.add(domain)
                except:
                    pass
            self.source_diversity = len(domains)

class DeduplicationRequest(BaseModel):
    """Request for content deduplication"""
    request_id: str = Field(..., description="Request identifier")
    content_items: List[ContentItem] = Field(..., description="Content to deduplicate")
    similarity_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    clustering_method: str = Field(default="hierarchical", description="Clustering algorithm")
    generate_parent_summaries: bool = Field(default=True)
    max_cluster_size: int = Field(default=10, ge=2, le=50)

class DeduplicationResponse(BaseModel):
    """Response from deduplication process"""
    request_id: str = Field(..., description="Request identifier")
    
    # Input data
    total_input_items: int = Field(..., description="Total input content items")
    
    # Clustering results
    clusters: List[ContentCluster] = Field(..., description="Content clusters")
    unique_items: List[ContentItem] = Field(..., description="Items with no duplicates")
    
    # Summary statistics
    total_clusters: int = Field(default=0)
    items_clustered: int = Field(default=0)
    items_unique: int = Field(default=0)
    parent_summaries_generated: int = Field(default=0)
    
    # Quality metrics
    average_cluster_confidence: float = Field(default=0.0)
    deduplication_ratio: float = Field(default=0.0, description="Reduction in content items")
    
    # Processing metadata
    processing_time: float = Field(default=0.0)
    embeddings_generated: int = Field(default=0)
    similarity_calculations: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_summary_stats(self):
        """Calculate summary statistics"""
        self.total_clusters = len(self.clusters)
        self.items_clustered = sum(len(cluster.content_items) for cluster in self.clusters)
        self.items_unique = len(self.unique_items)
        self.parent_summaries_generated = sum(1 for cluster in self.clusters if cluster.parent_summary)
        
        if self.clusters:
            confidences = [cluster.cluster_confidence for cluster in self.clusters]
            self.average_cluster_confidence = sum(confidences) / len(confidences)
        
        # Calculate deduplication ratio
        total_final_items = self.total_clusters + self.items_unique
        if self.total_input_items > 0:
            self.deduplication_ratio = (1 - total_final_items / self.total_input_items) * 100

class SimilarityMatrix(BaseModel):
    """Matrix of similarity scores between content items"""
    item_ids: List[str] = Field(..., description="Content item IDs")
    similarity_scores: List[List[float]] = Field(..., description="Similarity matrix")
    threshold: float = Field(..., description="Similarity threshold used")
    
    def get_similarity(self, id1: str, id2: str) -> Optional[float]:
        """Get similarity score between two items"""
        try:
            idx1 = self.item_ids.index(id1)
            idx2 = self.item_ids.index(id2)
            return self.similarity_scores[idx1][idx2]
        except (ValueError, IndexError):
            return None
    
    def get_similar_items(self, item_id: str, min_threshold: float = None) -> List[Tuple[str, float]]:
        """Get items similar to given item"""
        threshold = min_threshold or self.threshold
        similar = []
        
        try:
            idx = self.item_ids.index(item_id)
            for i, score in enumerate(self.similarity_scores[idx]):
                if i != idx and score >= threshold:
                    similar.append((self.item_ids[i], score))
            
            # Sort by similarity score (descending)
            similar.sort(key=lambda x: x[1], reverse=True)
            
        except ValueError:
            pass
        
        return similar
```

## openai_api.py
```python
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .models import ContentCluster, ContentItem
from ...config.settings import settings
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIAPI:
    """OpenAI client for content deduplication tasks"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def generate_parent_summary(self, cluster: ContentCluster) -> str:
        """Generate parent summary for content cluster"""
        try:
            if not cluster.content_items:
                return ""
            
            # Prepare content for summarization
            content_texts = []
            for item in cluster.content_items:
                content_preview = f"Title: {item.title}\nURL: {item.url}\nContent: {item.content[:1000]}..."
                content_texts.append(content_preview)
            
            combined_content = "\n\n---\n\n".join(content_texts)
            
            prompt = self._build_summarization_prompt(combined_content, len(cluster.content_items))
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert content analyst specializing in creating comprehensive summaries from multiple related articles."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3,
                presence_penalty=0.1
            )
            
            summary = response.choices[0].message.content.strip()
            
            logger.info(f"Generated parent summary for cluster {cluster.cluster_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Parent summary generation failed: {str(e)}")
            return f"Summary generation failed for {len(cluster.content_items)} related articles."
    
    async def analyze_content_similarity(self, item1: ContentItem, item2: ContentItem) -> Dict[str, Any]:
        """Analyze semantic similarity between content items"""
        try:
            prompt = self._build_similarity_analysis_prompt(item1, item2)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in content analysis and similarity detection. Provide structured analysis of content similarity."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            analysis = response.choices[0].message.content.strip()
            
            # Parse analysis for similarity score and reasoning
            similarity_data = self._parse_similarity_analysis(analysis)
            
            return similarity_data
            
        except Exception as e:
            logger.error(f"Similarity analysis failed: {str(e)}")
            return {"similarity_score": 0.0, "reasoning": "Analysis failed", "confidence": 0.0}
    
    async def improve_cluster_quality(self, cluster: ContentCluster) -> ContentCluster:
        """Analyze and improve cluster quality"""
        try:
            cluster_description = self._describe_cluster(cluster)
            
            prompt = f"""
            Analyze this content cluster and suggest improvements:
            
            {cluster_description}
            
            Provide recommendations for:
            1. Items that might not belong in this cluster
            2. Potential sub-clusters within this group
            3. Overall cluster coherence score (0-1)
            4. Suggested cluster title/theme
            
            Format as JSON with keys: outliers, subclusters, coherence_score, theme
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a clustering quality analyst. Provide structured analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            analysis = response.choices[0].message.content.strip()
            quality_data = self._parse_cluster_analysis(analysis)
            
            # Apply improvements to cluster
            improved_cluster = self._apply_cluster_improvements(cluster, quality_data)
            
            return improved_cluster
            
        except Exception as e:
            logger.error(f"Cluster improvement failed: {str(e)}")
            return cluster
    
    def _build_summarization_prompt(self, content: str, item_count: int) -> str:
        """Build prompt for parent summary generation"""
        return f"""
        Create a comprehensive summary that consolidates the following {item_count} related articles into a single, coherent narrative.
        
        Requirements:
        1. Identify the main topic/theme across all articles
        2. Synthesize key facts and findings from all sources
        3. Maintain factual accuracy and cite when information appears in multiple sources
        4. Highlight any conflicting information or different perspectives
        5. Structure the summary with clear sections (overview, key points, implications)
        6. Keep the summary between 300-500 words
        
        Source Articles:
        {content}
        
        Provide a well-structured summary that someone could read instead of all individual articles:
        """
    
    def _build_similarity_analysis_prompt(self, item1: ContentItem, item2: ContentItem) -> str:
        """Build prompt for similarity analysis"""
        return f"""
        Analyze the similarity between these two content items:
        
        Content 1:
        Title: {item1.title}
        URL: {item1.url}
        Content: {item1.content[:800]}...
        
        Content 2:
        Title: {item2.title}
        URL: {item2.url}
        Content: {item2.content[:800]}...
        
        Provide analysis with:
        1. Similarity score (0.0-1.0)
        2. Main similarities identified
        3. Key differences
        4. Confidence in assessment (0.0-1.0)
        5. Reasoning for the score
        
        Focus on semantic similarity, not just keyword overlap.
        """
    
    def _parse_similarity_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse similarity analysis response"""
        # Simple parsing - in production, could use structured output
        import re
        
        score_match = re.search(r'similarity.*?(\d+\.?\d*)', analysis.lower())
        confidence_match = re.search(r'confidence.*?(\d+\.?\d*)', analysis.lower())
        
        similarity_score = float(score_match.group(1)) if score_match else 0.5
        confidence = float(confidence_match.group(1)) if confidence_match else 0.5
        
        # Normalize scores to 0-1 range
        similarity_score = min(max(similarity_score, 0.0), 1.0)
        confidence = min(max(confidence, 0.0), 1.0)
        
        return {
            "similarity_score": similarity_score,
            "confidence": confidence,
            "reasoning": analysis,
            "method": "openai_analysis"
        }
    
    def _describe_cluster(self, cluster: ContentCluster) -> str:
        """Create description of cluster for analysis"""
        descriptions = []
        for i, item in enumerate(cluster.content_items):
            desc = f"Item {i+1}: {item.title} - {item.content[:200]}..."
            descriptions.append(desc)
        
        return f"""
        Cluster ID: {cluster.cluster_id}
        Items: {len(cluster.content_items)}
        Average Confidence: {cluster.average_confidence:.2f}
        
        Content Items:
        {chr(10).join(descriptions)}
        """
    
    def _parse_cluster_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse cluster quality analysis"""
        try:
            import json
            # Try to parse as JSON first
            return json.loads(analysis)
        except:
            # Fallback to simple parsing
            return {
                "coherence_score": 0.7,
                "theme": "Related content",
                "outliers": [],
                "subclusters": []
            }
    
    def _apply_cluster_improvements(self, cluster: ContentCluster, improvements: Dict[str, Any]) -> ContentCluster:
        """Apply improvements to cluster"""
        # Update cluster confidence based on coherence score
        if "coherence_score" in improvements:
            cluster.cluster_confidence = improvements["coherence_score"]
        
        # Could implement outlier removal, sub-clustering, etc.
        # For now, just update metadata
        cluster.metadata = cluster.metadata or {}
        cluster.metadata.update({
            "quality_analysis": improvements,
            "improved_at": datetime.utcnow().isoformat()
        })
        
        return cluster
```

## openai_mock.py
```python
import asyncio
from typing import List, Dict, Any
from datetime import datetime
from .models import ContentCluster, ContentItem
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIMock:
    """Mock OpenAI client for testing deduplication"""
    
    def __init__(self):
        self.mock_summaries = self._generate_mock_summaries()
    
    async def generate_parent_summary(self, cluster: ContentCluster) -> str:
        """Generate mock parent summary"""
        await asyncio.sleep(0.2)  # Simulate API latency
        
        logger.info(f"Mock generating parent summary for cluster {cluster.cluster_id}")
        
        if not cluster.content_items:
            return "No content available for summary."
        
        # Select appropriate mock summary based on content
        summary_type = self._classify_cluster_content(cluster)
        base_summary = self.mock_summaries.get(summary_type, self.mock_summaries["general"])
        
        # Customize summary with cluster details
        customized_summary = self._customize_summary(base_summary, cluster)
        
        return customized_summary
    
    async def analyze_content_similarity(self, item1: ContentItem, item2: ContentItem) -> Dict[str, Any]:
        """Mock content similarity analysis"""
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Calculate mock similarity based on title and content overlap
        similarity_score = self._calculate_mock_similarity(item1, item2)
        
        confidence = 0.85 if similarity_score > 0.7 else 0.6
        
        reasoning = self._generate_similarity_reasoning(item1, item2, similarity_score)
        
        return {
            "similarity_score": similarity_score,
            "confidence": confidence,
            "reasoning": reasoning,
            "method": "mock_analysis"
        }
    
    async def improve_cluster_quality(self, cluster: ContentCluster) -> ContentCluster:
        """Mock cluster quality improvement"""
        await asyncio.sleep(0.1)
        
        # Simulate quality analysis
        coherence_score = min(cluster.average_confidence + 0.1, 1.0)
        
        # Add mock improvements
        cluster.cluster_confidence = coherence_score
        cluster.metadata = cluster.metadata or {}
        cluster.metadata.update({
            "quality_analysis": {
                "coherence_score": coherence_score,
                "theme": f"Cluster theme for {len(cluster.content_items)} items",
                "outliers": [],
                "subclusters": []
            },
            "improved_at": datetime.utcnow().isoformat(),
            "improvement_method": "mock"
        })
        
        return cluster
    
    def _generate_mock_summaries(self) -> Dict[str, str]:
        """Generate mock summary templates"""
        return {
            "pharmaceutical": """
            This cluster contains articles discussing pharmaceutical industry developments, particularly focusing on regulatory changes and AI integration. Multiple sources report on new FDA guidelines for AI-powered drug discovery tools, emphasizing the need for transparency and validation in machine learning models used for therapeutic development. The consensus across sources indicates that pharmaceutical companies are adapting to stricter compliance requirements while investing in AI technologies to accelerate drug development processes. Key themes include regulatory compliance, AI innovation, and industry transformation.
            """,
            "regulation": """
            These articles cover regulatory framework developments in healthcare and pharmaceutical industries. Sources consistently report on new governmental guidelines and policy changes affecting AI implementation in medical applications. The main focus is on balancing innovation with safety requirements, ensuring patient protection while enabling technological advancement. Regulatory bodies are establishing clear standards for AI validation, documentation requirements, and ongoing monitoring of AI-powered medical tools.
            """,
            "technology": """
            This content cluster discusses technological advancements in healthcare and life sciences, with particular emphasis on artificial intelligence applications. Articles describe various AI implementations including drug discovery platforms, diagnostic tools, and patient care optimization systems. Common themes include machine learning algorithm development, clinical trial efficiency improvements, and the integration of AI into existing healthcare workflows. Sources highlight both opportunities and challenges in healthcare technology adoption.
            """,
            "general": """
            This cluster contains related articles covering a common topic or theme. The content has been analyzed and determined to discuss similar subjects from different perspectives or sources. Key information has been consolidated to provide a comprehensive overview of the topic. Multiple sources contribute different insights and details to create a more complete understanding of the subject matter.
            """
        }
    
    def _classify_cluster_content(self, cluster: ContentCluster) -> str:
        """Classify cluster content to select appropriate summary"""
        # Simple classification based on keywords in titles/content
        all_text = " ".join([item.title + " " + item.content for item in cluster.content_items]).lower()
        
        if any(word in all_text for word in ["pharmaceutical", "pharma", "drug", "fda"]):
            return "pharmaceutical"
        elif any(word in all_text for word in ["regulation", "regulatory", "compliance", "policy"]):
            return "regulation"
        elif any(word in all_text for word in ["ai", "artificial intelligence", "machine learning", "technology"]):
            return "technology"
        else:
            return "general"
    
    def _customize_summary(self, base_summary: str, cluster: ContentCluster) -> str:
        """Customize summary with cluster-specific details"""
        customizations = {
            "{item_count}": str(len(cluster.content_items)),
            "{confidence}": f"{cluster.average_confidence:.1f}",
            "{source_count}": str(cluster.source_diversity),
            "{word_count}": str(cluster.total_word_count)
        }
        
        customized = base_summary.strip()
        for placeholder, value in customizations.items():
            customized = customized.replace(placeholder, value)
        
        # Add cluster-specific prefix
        prefix = f"Analysis of {len(cluster.content_items)} related articles reveals: "
        
        return prefix + customized
    
    def _calculate_mock_similarity(self, item1: ContentItem, item2: ContentItem) -> float:
        """Calculate mock similarity score"""
        # Simple similarity based on title and content overlap
        title1_words = set(item1.title.lower().split())
        title2_words = set(item2.title.lower().split())
        
        content1_words = set(item1.content.lower().split()[:100])  # First 100 words
        content2_words = set(item2.content.lower().split()[:100])
        
        # Title similarity (weighted more heavily)
        title_intersection = len(title1_words & title2_words)
        title_union = len(title1_words | title2_words)
        title_similarity = title_intersection / title_union if title_union > 0 else 0
        
        # Content similarity
        content_intersection = len(content1_words & content2_words)
        content_union = len(content1_words | content2_words)
        content_similarity = content_intersection / content_union if content_union > 0 else 0
        
        # Combined similarity (title weighted 70%, content 30%)
        combined_similarity = (title_similarity * 0.7) + (content_similarity * 0.3)
        
        # Add some randomness to make it more realistic
        import random
        random.seed(hash(item1.id + item2.id))  # Deterministic randomness
        noise = random.uniform(-0.1, 0.1)
        
        final_similarity = max(0.0, min(1.0, combined_similarity + noise))
        
        return round(final_similarity, 3)
    
    def _generate_similarity_reasoning(self, item1: ContentItem, item2: ContentItem, score: float) -> str:
        """Generate mock reasoning for similarity score"""
        if score >= 0.9:
            return f"Very high similarity detected. Articles share nearly identical topics and key concepts. Score: {score:.2f}"
        elif score >= 0.7:
            return f"High similarity found. Articles discuss the same general topic with significant overlap in themes and content. Score: {score:.2f}"
        elif score >= 0.5:
            return f"Moderate similarity identified. Articles share some common themes but have distinct perspectives or focus areas. Score: {score:.2f}"
        else:
            return f"Low similarity detected. Articles appear to cover different topics or have minimal thematic overlap. Score: {score:.2f}"
```

## embedding_api.py
```python
import asyncio
import boto3
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError
from .models import ContentItem
from ...config.settings import settings
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingAPI:
    """Amazon Titan Embeddings API client"""
    
    def __init__(self):
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bedrock_runtime = self.session.client('bedrock-runtime')
        self.model_id = "amazon.titan-embed-text-v1"
        self.max_tokens = 8000  # Titan embedding model limit
    
    async def generate_embeddings(self, content_items: List[ContentItem]) -> Dict[str, List[float]]:
        """Generate embeddings for content items"""
        try:
            logger.info(f"Generating embeddings for {len(content_items)} content items")
            
            embeddings = {}
            
            for item in content_items:
                try:
                    # Prepare text for embedding
                    text = self._prepare_text_for_embedding(item)
                    
                    # Generate embedding
                    embedding = await self._generate_single_embedding(text)
                    
                    if embedding:
                        embeddings[item.id] = embedding
                        item.embedding = embedding
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Failed to generate embedding for {item.id}: {str(e)}")
                    continue
            
            logger.info(f"Successfully generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    async def _generate_single_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for single text"""
        try:
            # Truncate text if too long
            truncated_text = self._truncate_text(text)
            
            body = {
                "inputText": truncated_text
            }
            
            # Make async call to Bedrock
            response = await self._call_bedrock_embedding(body)
            
            if response and "embedding" in response:
                return response["embedding"]
            
            return None
            
        except Exception as e:
            logger.error(f"Single embedding generation failed: {str(e)}")
            return None
    
    async def _call_bedrock_embedding(self, body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make async call to Bedrock embedding API"""
        try:
            # Run in thread pool since boto3 is sync
            loop = asyncio.get_event_loop()
            
            response = await loop.run_in_executor(
                None,
                lambda: self.bedrock_runtime.invoke_model(
                    modelId=self.model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps(body)
                )
            )
            
            import json
            response_body = json.loads(response["body"].read())
            
            return response_body
            
        except ClientError as e:
            logger.error(f"Bedrock API error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Embedding API call failed: {str(e)}")
            return None
    
    def _prepare_text_for_embedding(self, item: ContentItem) -> str:
        """Prepare content text for embedding generation"""
        # Combine title and content with appropriate weighting
        title_weight = 3  # Title appears 3 times to increase importance
        
        text_parts = []
        
        # Add weighted title
        if item.title:
            text_parts.extend([item.title] * title_weight)
        
        # Add content
        if item.content:
            text_parts.append(item.content)
        
        # Add summary if available and different from content
        if item.summary and item.summary != item.content:
            text_parts.append(item.summary)
        
        combined_text = " ".join(text_parts)
        
        return combined_text
    
    def _truncate_text(self, text: str) -> str:
        """Truncate text to fit model limits"""
        if not text:
            return ""
        
        # Estimate tokens (rough approximation: 1 token ≈ 4 characters)
        estimated_tokens = len(text) // 4
        
        if estimated_tokens <= self.max_tokens:
            return text
        
        # Truncate to approximate token limit
        max_chars = self.max_tokens * 4
        
        if len(text) <= max_chars:
            return text
        
        # Truncate at word boundary
        truncated = text[:max_chars]
        last_space = truncated.rfind(' ')
        
        if last_space > max_chars * 0.8:  # If we're not losing too much
            truncated = truncated[:last_space]
        
        return truncated
    
    async def calculate_similarity_matrix(self, embeddings: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """Calculate cosine similarity matrix for embeddings"""
        try:
            import numpy as np
            
            item_ids = list(embeddings.keys())
            similarity_matrix = {}
            
            logger.info(f"Calculating similarity matrix for {len(item_ids)} items")
            
            for i, id1 in enumerate(item_ids):
                similarity_matrix[id1] = {}
                
                for j, id2 in enumerate(item_ids):
                    if i == j:
                        similarity_matrix[id1][id2] = 1.0
                    elif id2 in similarity_matrix and id1 in similarity_matrix[id2]:
                        # Use already calculated similarity (symmetric)
                        similarity_matrix[id1][id2] = similarity_matrix[id2][id1]
                    else:
                        # Calculate cosine similarity
                        similarity = self._cosine_similarity(
                            embeddings[id1], 
                            embeddings[id2]
                        )
                        similarity_matrix[id1][id2] = similarity
            
            logger.info("Similarity matrix calculation completed")
            return similarity_matrix
            
        except Exception as e:
            logger.error(f"Similarity matrix calculation failed: {str(e)}")
            return {}
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import numpy as np
            
            # Convert to numpy arrays
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            similarity = dot_product / (norm_a * norm_b)
            
            # Ensure result is in valid range
            return max(0.0, min(1.0, float(similarity)))
            
        except Exception as e:
            logger.warning(f"Cosine similarity calculation failed: {str(e)}")
            return 0.0
```

## embedding_mock.py
```python
import asyncio
import random
from typing import List, Dict, Any, Optional
from .models import ContentItem
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class EmbeddingMock:
    """Mock embedding API for testing"""
    
    def __init__(self):
        self.embedding_dimension = 1536  # Match Titan embedding dimensions
        random.seed(42)  # For reproducible results
    
    async def generate_embeddings(self, content_items: List[ContentItem]) -> Dict[str, List[float]]:
        """Generate mock embeddings for content items"""
        await asyncio.sleep(0.5)  # Simulate API latency
        
        logger.info(f"Mock generating embeddings for {len(content_items)} content items")
        
        embeddings = {}
        
        for item in content_items:
            # Generate deterministic mock embedding based on content
            embedding = self._generate_mock_embedding(item)
            embeddings[item.id] = embedding
            item.embedding = embedding
        
        logger.info(f"Mock generated {len(embeddings)} embeddings")
        return embeddings
    
    async def calculate_similarity_matrix(self, embeddings: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """Calculate mock similarity matrix"""
        await asyncio.sleep(0.2)
        
        item_ids = list(embeddings.keys())
        similarity_matrix = {}
        
        logger.info(f"Mock calculating similarity matrix for {len(item_ids)} items")
        
        for i, id1 in enumerate(item_ids):
            similarity_matrix[id1] = {}
            
            for j, id2 in enumerate(item_ids):
                if i == j:
                    similarity_matrix[id1][id2] = 1.0
                else:
                    # Calculate mock similarity
                    similarity = self._calculate_mock_similarity(
                        embeddings[id1], 
                        embeddings[id2],
                        id1,
                        id2
                    )
                    similarity_matrix[id1][id2] = similarity
        
        return similarity_matrix
    
    def _generate_mock_embedding(self, item: ContentItem) -> List[float]:
        """Generate deterministic mock embedding"""
        # Use content hash to create deterministic but varied embeddings
        content_hash = hash(item.title + item.content)
        random.seed(content_hash)
        
        # Generate base embedding
        embedding = [random.gauss(0, 1) for _ in range(self.embedding_dimension)]
        
        # Add content-specific features
        embedding = self._add_content_features(embedding, item)
        
        # Normalize to unit vector
        magnitude = sum(x**2 for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding
    
    def _add_content_features(self, embedding: List[float], item: ContentItem) -> List[float]:
        """Add content-specific features to make similar content have similar embeddings"""
        # Keywords that should cluster together
        keyword_groups = {
            "pharmaceutical": ["pharmaceutical", "pharma", "drug", "medicine", "fda", "clinical"],
            "ai_tech": ["ai", "artificial intelligence", "machine learning", "algorithm", "data"],
            "regulation": ["regulation", "regulatory", "compliance", "policy", "law", "guideline"],
            "business": ["business", "market", "company", "industry", "commercial", "revenue"]
        }
        
        content_text = (item.title + " " + item.content).lower()
        
        # Adjust embedding based on keyword presence
        for group_name, keywords in keyword_groups.items():
            keyword_score = sum(1 for keyword in keywords if keyword in content_text)
            if keyword_score > 0:
                # Modify specific dimensions based on topic
                group_hash = hash(group_name)
                start_dim = abs(group_hash) % (self.embedding_dimension - 100)
                
                for i in range(start_dim, start_dim + 50):
                    embedding[i] += keyword_score * 0.5
        
        return embedding
    
    def _calculate_mock_similarity(self, vec1: List[float], vec2: List[float], id1: str, id2: str) -> float:
        """Calculate mock similarity with realistic patterns"""
        # Basic cosine similarity
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(x**2 for x in vec1) ** 0.5
        magnitude2 = sum(x**2 for x in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        base_similarity = dot_product / (magnitude1 * magnitude2)
        base_similarity = max(0.0, min(1.0, base_similarity))
        
        # Add some realistic clustering patterns
        similarity = self._adjust_similarity_for_realism(base_similarity, id1, id2)
        
        return round(similarity, 3)
    
    def _adjust_similarity_for_realism(self, base_similarity: float, id1: str, id2: str) -> float:
        """Adjust similarity to create realistic clustering patterns"""
        # Create some high-similarity pairs for testing clustering
        id_pair = tuple(sorted([id1, id2]))
        pair_hash = hash(id_pair)
        
        # 10% chance of very high similarity (near duplicates)
        if abs(pair_hash) % 10 == 0:
            return max(base_similarity, 0.92 + random.uniform(0, 0.05))
        
        # 20% chance of high similarity (same story)
        elif abs(pair_hash) % 5 == 0:
            return max(base_similarity, 0.80 + random.uniform(0, 0.10))
        
        # 30% chance of moderate similarity (related content)
        elif abs(pair_hash) % 3 == 0:
            return max(base_similarity, 0.65 + random.uniform(0, 0.10))
        
        # Otherwise, use base similarity with small adjustment
        else:
            adjustment = random.uniform(-0.1, 0.1)
            return max(0.0, min(1.0, base_similarity + adjustment))
```

## similarity_engine.py
```python
import asyncio
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from .models import ContentItem, SimilarityMatrix, SimilarityThreshold
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class SimilarityEngine:
    """Engine for calculating and analyzing content similarity"""
    
    def __init__(self):
        self.similarity_thresholds = {
            SimilarityThreshold.EXACT_DUPLICATE: 0.95,
            SimilarityThreshold.SAME_STORY: 0.85,
            SimilarityThreshold.RELATED_CONTENT: 0.70,
            SimilarityThreshold.UNIQUE_CONTENT: 0.70  # Below this is unique
        }
    
    async def calculate_similarity_matrix(self, content_items: List[ContentItem]) -> SimilarityMatrix:
        """Calculate full similarity matrix for content items"""
        try:
            logger.info(f"Calculating similarity matrix for {len(content_items)} items")
            
            # Ensure all items have embeddings
            items_with_embeddings = [item for item in content_items if item.embedding]
            
            if len(items_with_embeddings) != len(content_items):
                logger.warning(f"Only {len(items_with_embeddings)}/{len(content_items)} items have embeddings")
            
            item_ids = [item.id for item in items_with_embeddings]
            embeddings = [item.embedding for item in items_with_embeddings]
            
            # Calculate similarity matrix
            similarity_scores = await self._compute_pairwise_similarities(embeddings)
            
            matrix = SimilarityMatrix(
                item_ids=item_ids,
                similarity_scores=similarity_scores,
                threshold=self.similarity_thresholds[SimilarityThreshold.SAME_STORY]
            )
            
            logger.info("Similarity matrix calculation completed")
            return matrix
            
        except Exception as e:
            logger.error(f"Similarity matrix calculation failed: {str(e)}")
            raise
    
    async def _compute_pairwise_similarities(self, embeddings: List[List[float]]) -> List[List[float]]:
        """Compute pairwise cosine similarities"""
        n = len(embeddings)
        similarity_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Convert to numpy for efficient computation
        embeddings_array = np.array(embeddings)
        
        # Normalize embeddings
        norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        normalized_embeddings = embeddings_array / norms
        
        # Calculate cosine similarity matrix
        similarity_array = np.dot(normalized_embeddings, normalized_embeddings.T)
        
        # Convert back to list and ensure diagonal is 1.0
        for i in range(n):
            for j in range(n):
                if i == j:
                    similarity_matrix[i][j] = 1.0
                else:
                    similarity_matrix[i][j] = float(similarity_array[i][j])
        
        return similarity_matrix
    
    def identify_similar_pairs(self, matrix: SimilarityMatrix, threshold: float = None) -> List[Tuple[str, str, float]]:
        """Identify pairs of similar content above threshold"""
        if threshold is None:
            threshold = self.similarity_thresholds[SimilarityThreshold.SAME_STORY]
        
        similar_pairs = []
        
        for i, id1 in enumerate(matrix.item_ids):
            for j, id2 in enumerate(matrix.item_ids):
                if i < j:  # Only check upper triangle to avoid duplicates
                    similarity = matrix.similarity_scores[i][j]
                    if similarity >= threshold:
                        similar_pairs.append((id1, id2, similarity))
        
        # Sort by similarity (descending)
        similar_pairs.sort(key=lambda x: x[2], reverse=True)
        
        logger.info(f"Found {len(similar_pairs)} similar pairs above threshold {threshold}")
        return similar_pairs
    
    def classify_similarity_level(self, similarity_score: float) -> SimilarityThreshold:
        """Classify similarity score into threshold category"""
        if similarity_score >= self.similarity_thresholds[SimilarityThreshold.EXACT_DUPLICATE]:
            return SimilarityThreshold.EXACT_DUPLICATE
        elif similarity_score >= self.similarity_thresholds[SimilarityThreshold.SAME_STORY]:
            return SimilarityThreshold.SAME_STORY
        elif similarity_score >= self.similarity_thresholds[SimilarityThreshold.RELATED_CONTENT]:
            return SimilarityThreshold.RELATED_CONTENT
        else:
            return SimilarityThreshold.UNIQUE_CONTENT
    
    def find_content_clusters(self, matrix: SimilarityMatrix, min_similarity: float = 0.85) -> List[List[str]]:
        """Find clusters of similar content using connected components"""
        try:
            # Build adjacency list for similarity graph
            adjacency = {item_id: [] for item_id in matrix.item_ids}
            
            for i, id1 in enumerate(matrix.item_ids):
                for j, id2 in enumerate(matrix.item_ids):
                    if i != j and matrix.similarity_scores[i][j] >= min_similarity:
                        adjacency[id1].append(id2)
            
            # Find connected components (clusters)
            clusters = []
            visited = set()
            
            for item_id in matrix.item_ids:
                if item_id not in visited:
                    cluster = self._dfs_cluster(item_id, adjacency, visited)
                    if len(cluster) > 1:  # Only keep clusters with multiple items
                        clusters.append(cluster)
            
            logger.info(f"Found {len(clusters)} clusters with similarity >= {min_similarity}")
            return clusters
            
        except Exception as e:
            logger.error(f"Cluster finding failed: {str(e)}")
            return []
    
    def _dfs_cluster(self, start_id: str, adjacency: Dict[str, List[str]], visited: set) -> List[str]:
        """Depth-first search to find connected component"""
        cluster = []
        stack = [start_id]
        
        while stack:
            current_id = stack.pop()
            if current_id not in visited:
                visited.add(current_id)
                cluster.append(current_id)
                
                # Add neighbors to stack
                for neighbor_id in adjacency[current_id]:
                    if neighbor_id not in visited:
                        stack.append(neighbor_id)
        
        return cluster
    
    def analyze_cluster_quality(self, cluster_ids: List[str], matrix: SimilarityMatrix) -> Dict[str, Any]:
        """Analyze quality metrics for a cluster"""
        try:
            if len(cluster_ids) < 2:
                return {"average_similarity": 0.0, "min_similarity": 0.0, "max_similarity": 0.0, "cohesion": 0.0}
            
            similarities = []
            
            # Get all pairwise similarities within cluster
            for i, id1 in enumerate(cluster_ids):
                for j, id2 in enumerate(cluster_ids):
                    if i < j:
                        similarity = matrix.get_similarity(id1, id2)
                        if similarity is not None:
                            similarities.append(similarity)
            
            if not similarities:
                return {"average_similarity": 0.0, "min_similarity": 0.0, "max_similarity": 0.0, "cohesion": 0.0}
            
            avg_similarity = np.mean(similarities)
            min_similarity = np.min(similarities)
            max_similarity = np.max(similarities)
            
            # Cohesion: how tightly clustered the items are
            cohesion = avg_similarity - np.std(similarities)
            
            return {
                "average_similarity": float(avg_similarity),
                "min_similarity": float(min_similarity),
                "max_similarity": float(max_similarity),
                "cohesion": float(cohesion),
                "similarity_std": float(np.std(similarities)),
                "pairwise_count": len(similarities)
            }
            
        except Exception as e:
            logger.error(f"Cluster quality analysis failed: {str(e)}")
            return {"average_similarity": 0.0, "min_similarity": 0.0, "max_similarity": 0.0, "cohesion": 0.0}
    
    def get_content_neighbors(self, item_id: str, matrix: SimilarityMatrix, k: int = 5) -> List[Tuple[str, float]]:
        """Get k most similar content items to given item"""
        try:
            if item_id not in matrix.item_ids:
                return []
            
            item_index = matrix.item_ids.index(item_id)
            similarities = []
            
            for i, other_id in enumerate(matrix.item_ids):
                if i != item_index:
                    similarity = matrix.similarity_scores[item_index][i]
                    similarities.append((other_id, similarity))
            
            # Sort by similarity and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:k]
            
        except Exception as e:
            logger.error(f"Neighbor finding failed for {item_id}: {str(e)}")
            return []
```

## clustering_service.py
```python
from typing import List, Dict, Any, Optional
from datetime import datetime
from .models import ContentItem, ContentCluster, SimilarityThreshold
from .similarity_engine import SimilarityEngine
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class ClusteringService:
    """Service for clustering similar content items"""
    
    def __init__(self):
        self.similarity_engine = SimilarityEngine()
        self.min_cluster_size = 2
        self.max_cluster_size = 10
    
    async def cluster_content(self, content_items: List[ContentItem], similarity_threshold: float = 0.85) -> List[ContentCluster]:
        """Cluster content items based on similarity"""
        try:
            logger.info(f"Clustering {len(content_items)} content items with threshold {similarity_threshold}")
            
            if len(content_items) < 2:
                logger.info("Insufficient items for clustering")
                return []
            
            # Calculate similarity matrix
            similarity_matrix = await self.similarity_engine.calculate_similarity_matrix(content_items)
            
            # Find clusters
            cluster_groups = self.similarity_engine.find_content_clusters(similarity_matrix, similarity_threshold)
            
            # Create content clusters
            clusters = []
            content_by_id = {item.id: item for item in content_items}
            
            for i, cluster_ids in enumerate(cluster_groups):
                cluster_items = [content_by_id[item_id] for item_id in cluster_ids if item_id in content_by_id]
                
                if len(cluster_items) >= self.min_cluster_size:
                    cluster = await self._create_content_cluster(cluster_items, similarity_matrix, i)
                    clusters.append(cluster)
            
            logger.info(f"Created {len(clusters)} content clusters")
            return clusters
            
        except Exception as e:
            logger.error(f"Content clustering failed: {str(e)}")
            return []
    
    async def _create_content_cluster(self, items: List[ContentItem], similarity_matrix, cluster_index: int) -> ContentCluster:
        """Create ContentCluster from similar items"""
        cluster_id = f"cluster_{cluster_index}_{int(datetime.utcnow().timestamp())}"
        
        # Analyze cluster quality
        item_ids = [item.id for item in items]
        quality_metrics = self.similarity_engine.analyze_cluster_quality(item_ids, similarity_matrix)
        
        # Determine similarity threshold level
        avg_similarity = quality_metrics.get("average_similarity", 0.0)
        similarity_level = self.similarity_engine.classify_similarity_level(avg_similarity)
        
        # Create cluster
        cluster = ContentCluster(
            cluster_id=cluster_id,
            content_items=items,
            cluster_confidence=avg_similarity,
            similarity_threshold=similarity_level
        )
        
        # Calculate cluster metrics
        cluster.calculate_metrics()
        
        # Add quality metrics to metadata
        cluster.metadata = {
            "quality_metrics": quality_metrics,
            "clustering_method": "hierarchical",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Update item cluster assignments
        for item in items:
            item.cluster_id = cluster_id
            item.is_parent = False  # Will be set later if parent summary is generated
        
        logger.debug(f"Created cluster {cluster_id} with {len(items)} items")
        return cluster
    
    def split_large_clusters(self, clusters: List[ContentCluster]) -> List[ContentCluster]:
        """Split clusters that exceed maximum size"""
        split_clusters = []
        
        for cluster in clusters:
            if len(cluster.content_items) <= self.max_cluster_size:
                split_clusters.append(cluster)
            else:
                logger.info(f"Splitting large cluster {cluster.cluster_id} with {len(cluster.content_items)} items")
                sub_clusters = self._split_cluster(cluster)
                split_clusters.extend(sub_clusters)
        
        return split_clusters
    
    def _split_cluster(self, cluster: ContentCluster) -> List[ContentCluster]:
        """Split a large cluster into smaller sub-clusters"""
        try:
            items = cluster.content_items
            
            # Simple splitting: divide by time or alphabetically
            # In production, could use more sophisticated methods
            
            # Sort by URL (as a proxy for source/time)
            sorted_items = sorted(items, key=lambda x: x.url)
            
            # Split into chunks of max_cluster_size
            sub_clusters = []
            for i in range(0, len(sorted_items), self.max_cluster_size):
                chunk = sorted_items[i:i + self.max_cluster_size]
                
                if len(chunk) >= self.min_cluster_size:
                    sub_cluster_id = f"{cluster.cluster_id}_split_{len(sub_clusters)}"
                    
                    sub_cluster = ContentCluster(
                        cluster_id=sub_cluster_id,
                        content_items=chunk,
                        cluster_confidence=cluster.cluster_confidence * 0.9,  # Slightly reduce confidence
                        similarity_threshold=cluster.similarity_threshold
                    )
                    
                    sub_cluster.calculate_metrics()
                    sub_cluster.metadata = {
                        "parent_cluster": cluster.cluster_id,
                        "split_method": "size_based",
                        "created_at": datetime.utcnow().isoformat()
                    }
                    
                    # Update item assignments
                    for item in chunk:
                        item.cluster_id = sub_cluster_id
                    
                    sub_clusters.append(sub_cluster)
            
            logger.info(f"Split cluster into {len(sub_clusters)} sub-clusters")
            return sub_clusters
            
        except Exception as e:
            logger.error(f"Cluster splitting failed: {str(e)}")
            return [cluster]  # Return original cluster if splitting fails
    
    def merge_similar_clusters(self, clusters: List[ContentCluster], merge_threshold: float = 0.9) -> List[ContentCluster]:
        """Merge clusters that are very similar to each other"""
        try:
            if len(clusters) < 2:
                return clusters
            
            logger.info(f"Checking for cluster merges with threshold {merge_threshold}")
            
            merged_clusters = []
            used_clusters = set()
            
            for i, cluster1 in enumerate(clusters):
                if i in used_clusters:
                    continue
                
                merge_candidates = [cluster1]
                used_clusters.add(i)
                
                # Find clusters to merge with cluster1
                for j, cluster2 in enumerate(clusters):
                    if j <= i or j in used_clusters:
                        continue
                    
                    # Calculate inter-cluster similarity
                    inter_similarity = self._calculate_inter_cluster_similarity(cluster1, cluster2)
                    
                    if inter_similarity >= merge_threshold:
                        merge_candidates.append(cluster2)
                        used_clusters.add(j)
                
                # Merge if multiple candidates
                if len(merge_candidates) > 1:
                    merged_cluster = self._merge_clusters(merge_candidates)
                    merged_clusters.append(merged_cluster)
                else:
                    merged_clusters.append(cluster1)
            
            logger.info(f"Merged {len(clusters)} clusters into {len(merged_clusters)} clusters")
            return merged_clusters
            
        except Exception as e:
            logger.error(f"Cluster merging failed: {str(e)}")
            return clusters
    
    def _calculate_inter_cluster_similarity(self, cluster1: ContentCluster, cluster2: ContentCluster) -> float:
        """Calculate similarity between two clusters"""
        try:
            # Simple approach: average similarity between all pairs
            similarities = []
            
            for item1 in cluster1.content_items:
                for item2 in cluster2.content_items:
                    if item1.embedding and item2.embedding:
                        similarity = self._cosine_similarity(item1.embedding, item2.embedding)
                        similarities.append(similarity)
            
            return sum(similarities) / len(similarities) if similarities else 0.0
            
        except Exception as e:
            logger.error(f"Inter-cluster similarity calculation failed: {str(e)}")
            return 0.0
    
    def _merge_clusters(self, clusters: List[ContentCluster]) -> ContentCluster:
        """Merge multiple clusters into one"""
        try:
            all_items = []
            for cluster in clusters:
                all_items.extend(cluster.content_items)
            
            # Create merged cluster ID
            cluster_ids = [c.cluster_id for c in clusters]
            merged_id = f"merged_{'_'.join(cluster_ids[:2])}"  # Limit ID length
            
            # Calculate merged confidence (average weighted by cluster size)
            total_items = len(all_items)
            weighted_confidence = sum(
                cluster.cluster_confidence * len(cluster.content_items) 
                for cluster in clusters
            ) / total_items
            
            # Determine similarity threshold (most restrictive)
            similarity_thresholds = [cluster.similarity_threshold for cluster in clusters]
            merged_threshold = min(similarity_thresholds)
            
            merged_cluster = ContentCluster(
                cluster_id=merged_id,
                content_items=all_items,
                cluster_confidence=weighted_confidence,
                similarity_threshold=merged_threshold
            )
            
            merged_cluster.calculate_metrics()
            merged_cluster.metadata = {
                "merged_from": cluster_ids,
                "merge_method": "similarity_based",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Update item assignments
            for item in all_items:
                item.cluster_id = merged_id
            
            return merged_cluster
            
        except Exception as e:
            logger.error(f"Cluster merging failed: {str(e)}")
            return clusters[0] if clusters else None
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import numpy as np
            
            a = np.array(vec1)
            b = np.array(vec2)
            
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            if norm_a == 0 or norm_b == 0:
                return 0.0
            
            return float(dot_product / (norm_a * norm_b))
            
        except Exception as e:
            logger.warning(f"Cosine similarity calculation failed: {str(e)}")
            return 0.0
```

## service.py
```python
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from .models import DeduplicationRequest, DeduplicationResponse, ContentItem, ContentCluster
from .clustering_service import ClusteringService
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class DeduplicationService:
    """Main deduplication service orchestrating the complete pipeline"""
    
    def __init__(self):
        self.embedding_client = ServiceFactory.get_embedding_client()
        self.openai_client = ServiceFactory.get_openai_client()
        self.clustering_service = ClusteringService()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process_deduplication(self, request: DeduplicationRequest) -> DeduplicationResponse:
        """Execute complete deduplication pipeline"""
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting deduplication for request {request.request_id}")
            
            # Stage 1: Generate embeddings
            await self._generate_embeddings(request.content_items)
            
            # Stage 2: Cluster similar content
            clusters = await self._cluster_content(request)
            
            # Stage 3: Generate parent summaries
            if request.generate_parent_summaries:
                clusters = await self._generate_parent_summaries(clusters)
            
            # Stage 4: Identify unique items
            unique_items = self._identify_unique_items(request.content_items, clusters)
            
            # Create response
            response = self._create_response(request, clusters, unique_items, start_time)
            
            # Store results
            await self._store_results(response)
            
            logger.info(f"Deduplication completed: {response.total_clusters} clusters, {response.items_unique} unique items")
            return response
            
        except Exception as e:
            logger.error(f"Deduplication failed for {request.request_id}: {str(e)}")
            raise Exception(f"Deduplication processing failed: {str(e)}")
    
    async def _generate_embeddings(self, content_items: List[ContentItem]):
        """Generate embeddings for all content items"""
        try:
            logger.info(f"Generating embeddings for {len(content_items)} items")
            
            # Filter items that don't already have embeddings
            items_needing_embeddings = [item for item in content_items if not item.embedding]
            
            if not items_needing_embeddings:
                logger.info("All items already have embeddings")
                return
            
            # Generate embeddings
            embeddings = await self.embedding_client.generate_embeddings(items_needing_embeddings)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    async def _cluster_content(self, request: DeduplicationRequest) -> List[ContentCluster]:
        """Cluster content based on similarity"""
        try:
            logger.info("Starting content clustering")
            
            # Initial clustering
            clusters = await self.clustering_service.cluster_content(
                request.content_items,
                request.similarity_threshold
            )
            
            # Split large clusters if needed
            if request.max_cluster_size:
                self.clustering_service.max_cluster_size = request.max_cluster_size
                clusters = self.clustering_service.split_large_clusters(clusters)
            
            # Merge very similar clusters
            clusters = self.clustering_service.merge_similar_clusters(clusters)
            
            logger.info(f"Clustering completed: {len(clusters)} clusters created")
            return clusters
            
        except Exception as e:
            logger.error(f"Content clustering failed: {str(e)}")
            raise
    
    async def _generate_parent_summaries(self, clusters: List[ContentCluster]) -> List[ContentCluster]:
        """Generate parent summaries for clusters"""
        try:
            logger.info(f"Generating parent summaries for {len(clusters)} clusters")
            
            for cluster in clusters:
                try:
                    if len(cluster.content_items) >= 2:
                        summary = await self.openai_client.generate_parent_summary(cluster)
                        
                        if summary:
                            cluster.parent_summary = summary
                            
                            # Mark the first item as parent and add summary
                            if cluster.content_items:
                                parent_item = cluster.content_items[0]
                                parent_item.is_parent = True
                                parent_item.child_count = len(cluster.content_items) - 1
                                
                                # Store summary as content
                                parent_item.content = summary
                                parent_item.summary = summary[:500] + "..." if len(summary) > 500 else summary
                
                except Exception as e:
                    logger.warning(f"Failed to generate summary for cluster {cluster.cluster_id}: {str(e)}")
                    continue
            
            summaries_generated = sum(1 for cluster in clusters if cluster.parent_summary)
            logger.info(f"Generated {summaries_generated} parent summaries")
            
            return clusters
            
        except Exception as e:
            logger.error(f"Parent summary generation failed: {str(e)}")
            return clusters
    
    def _identify_unique_items(self, all_items: List[ContentItem], clusters: List[ContentCluster]) -> List[ContentItem]:
        """Identify items that don't belong to any cluster"""
        clustered_item_ids = set()
        
        for cluster in clusters:
            for item in cluster.content_items:
                clustered_item_ids.add(item.id)
        
        unique_items = [item for item in all_items if item.id not in clustered_item_ids]
        
        logger.info(f"Identified {len(unique_items)} unique items")
        return unique_items
    
    def _create_response(self, request: DeduplicationRequest, clusters: List[ContentCluster], unique_items: List[ContentItem], start_time: datetime) -> DeduplicationResponse:
        """Create deduplication response"""
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        response = DeduplicationResponse(
            request_id=request.request_id,
            total_input_items=len(request.content_items),
            clusters=clusters,
            unique_items=unique_items,
            processing_time=processing_time,
            embeddings_generated=len([item for item in request.content_items if item.embedding])
        )
        
        # Calculate summary statistics
        response.calculate_summary_stats()
        
        return response
    
    async def _store_results(self, response: DeduplicationResponse):
        """Store deduplication results"""
        try:
            # Store complete response
            storage_key = f"deduplication_results/{response.request_id}.json"
            await self.storage_client.save_json(storage_key, response.dict())
            
            # Store individual clusters
            for cluster in response.clusters:
                cluster_key = f"deduplication_clusters/{response.request_id}/{cluster.cluster_id}.json"
                await self.storage_client.save_json(cluster_key, cluster.dict())
            
            # Store metadata in database
            await self.database_client.save_item("deduplication_results", {
                "request_id": response.request_id,
                "total_input_items": response.total_input_items,
                "total_clusters": response.total_clusters,
                "items_clustered": response.items_clustered,
                "items_unique": response.items_unique,
                "deduplication_ratio": response.deduplication_ratio,
                "processing_time": response.processing_time,
                "storage_key": storage_key,
                "created_at": response.created_at.isoformat()
            })
            
            logger.info(f"Stored deduplication results: {storage_key}")
            
        except Exception as e:
            logger.error(f"Failed to store deduplication results: {str(e)}")
```

## storage.py
```python
from typing import Dict, Any, List, Optional
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class DeduplicationStorage:
    """Handle deduplication-specific storage operations"""
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def save_deduplication_results(self, request_id: str, results: Dict[str, Any]) -> bool:
        """Save complete deduplication results"""
        try:
            key = f"deduplication_results/{request_id}.json"
            success = await self.storage_client.save_json(key, results)
            
            if success:
                logger.info(f"Saved deduplication results: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Deduplication results save error: {str(e)}")
            return False
    
    async def save_content_clusters(self, request_id: str, clusters: List[Dict[str, Any]]) -> bool:
        """Save individual content clusters"""
        try:
            success_count = 0
            
            for cluster in clusters:
                cluster_id = cluster.get("cluster_id", "unknown")
                key = f"deduplication_clusters/{request_id}/{cluster_id}.json"
                
                if await self.storage_client.save_json(key, cluster):
                    success_count += 1
            
            logger.info(f"Saved {success_count}/{len(clusters)} clusters")
            return success_count == len(clusters)
            
        except Exception as e:
            logger.error(f"Cluster storage error: {str(e)}")
            return False
    
    async def save_embeddings(self, request_id: str, embeddings: Dict[str, List[float]]) -> bool:
        """Save content embeddings"""
        try:
            key = f"deduplication_embeddings/{request_id}.json"
            success = await self.storage_client.save_json(key, embeddings)
            
            if success:
                logger.info(f"Saved embeddings: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Embeddings save error: {str(e)}")
            return False
    
    async def load_deduplication_results(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Load deduplication results"""
        try:
            key = f"deduplication_results/{request_id}.json"
            results = await self.storage_client.load_json(key)
            
            if results:
                logger.info(f"Loaded deduplication results: {key}")
            
            return results
            
        except Exception as e:
            logger.error(f"Deduplication results load error: {str(e)}")
            return None
```

## database.py
```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class DeduplicationDatabase:
    """Handle deduplication database operations"""
    
    def __init__(self):
        self.db_client = ServiceFactory.get_database_client()
        self.table_name = "deduplication_results"
    
    async def save_deduplication_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save deduplication metadata"""
        try:
            if 'created_at' not in metadata:
                metadata['created_at'] = datetime.utcnow().isoformat()
            
            success = await self.db_client.save_item(self.table_name, metadata)
            
            if success:
                logger.info(f"Saved deduplication metadata: {metadata.get('request_id')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Deduplication metadata save error: {str(e)}")
            return False
    
    async def save_cluster_relationships(self, request_id: str, clusters: List[Dict[str, Any]]) -> bool:
        """Save parent-child relationships for clusters"""
        try:
            table_name = "content_clusters"
            success_count = 0
            
            for cluster in clusters:
                cluster_data = {
                    "cluster_id": cluster.get("cluster_id"),
                    "request_id": request_id,
                    "item_count": len(cluster.get("content_items", [])),
                    "cluster_confidence": cluster.get("cluster_confidence", 0.0),
                    "similarity_threshold": cluster.get("similarity_threshold"),
                    "has_parent_summary": bool(cluster.get("parent_summary")),
                    "created_at": datetime.utcnow().isoformat()
                }
                
                if await self.db_client.save_item(table_name, cluster_data):
                    success_count += 1
            
            logger.info(f"Saved {success_count}/{len(clusters)} cluster relationships")
            return success_count == len(clusters)
            
        except Exception as e:
            logger.error(f"Cluster relationships save error: {str(e)}")
            return False
    
    async def get_deduplication_stats(self, request_id: str) -> Dict[str, Any]:
        """Get deduplication statistics"""
        try:
            metadata = await self.db_client.get_item(self.table_name, {"request_id": request_id})
            
            if not metadata:
                return {}
            
            # Get cluster details
            clusters = await self.db_client.query_items(
                "content_clusters",
                KeyConditionExpression="request_id = :request_id",
                ExpressionAttributeValues={":request_id": request_id}
            )
            
            stats = {
                "request_id": request_id,
                "total_input_items": metadata.get("total_input_items", 0),
                "total_clusters": metadata.get("total_clusters", 0),
                "items_clustered": metadata.get("items_clustered", 0),
                "items_unique": metadata.get("items_unique", 0),
                "deduplication_ratio": metadata.get("deduplication_ratio", 0.0),
                "processing_time": metadata.get("processing_time", 0.0),
                "created_at": metadata.get("created_at"),
                "cluster_details": clusters
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Deduplication stats error: {str(e)}")
            return {}
```