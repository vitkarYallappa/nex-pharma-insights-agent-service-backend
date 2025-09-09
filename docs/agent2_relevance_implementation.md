# Agent 2 Relevance Implementation

## 10-Line Prompt:
Create content relevance filtering agent that processes deduplicated content from Agent 1 to evaluate strategic relevance using Key Intelligence Questions (KIQs) and Critical Intelligence Topics (KITs), includes sophisticated scoring algorithms that combine KIQ alignment, strategic priority, content quality, and temporal relevance into composite relevance scores, real OpenAI/Bedrock API integration for semantic analysis of content relevance against predefined intelligence frameworks, mock implementations that simulate realistic relevance scoring patterns for testing, KIQ evaluation engine that assesses how well content answers specific strategic intelligence questions, KIT classification system that organizes content into structured intelligence categories, multi-dimensional relevance scoring with configurable thresholds for include/exclude/manual-review decisions, service orchestration managing the complete relevance filtering pipeline, storage operations saving relevance metadata and filtered content for downstream agents, and database operations tracking relevance scores and KIQ/KIT mappings in enhanced knowledge base structure.

## What it covers: 
Strategic relevance assessment, KIQ/KIT framework implementation, content filtering
## Methods: 
Relevance scoring algorithms, semantic analysis, strategic alignment evaluation
## Why: 
Quality gate for content pipeline, strategic focus, intelligence value optimization

---

## models.py
```python
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class RelevanceDecision(str, Enum):
    INCLUDE = "include"
    EXCLUDE = "exclude"
    MANUAL_REVIEW = "manual_review"

class KIQCategory(str, Enum):
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    REGULATORY_LANDSCAPE = "regulatory_landscape"
    MARKET_DYNAMICS = "market_dynamics"
    TECHNOLOGY_INNOVATION = "technology_innovation"
    RISK_ASSESSMENT = "risk_assessment"
    STRATEGIC_PLANNING = "strategic_planning"

class KeyIntelligenceQuestion(BaseModel):
    """Key Intelligence Question definition"""
    id: str = Field(..., description="KIQ identifier")
    category: KIQCategory = Field(..., description="KIQ category")
    question: str = Field(..., description="Intelligence question")
    keywords: List[str] = Field(..., description="Related keywords")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="Question importance weight")
    contexts: List[str] = Field(default_factory=list, description="Relevant contexts")
    
    def calculate_keyword_match_score(self, content: str) -> float:
        """Calculate keyword match score for content"""
        content_lower = content.lower()
        matches = sum(1 for keyword in self.keywords if keyword.lower() in content_lower)
        return min(matches / len(self.keywords), 1.0) if self.keywords else 0.0

class CriticalIntelligenceTopic(BaseModel):
    """Critical Intelligence Topic definition"""
    kit_id: str = Field(..., description="KIT identifier")
    name: str = Field(..., description="Topic name")
    description: str = Field(..., description="Topic description")
    priority: str = Field(default="medium", description="Priority level")
    associated_kiqs: List[str] = Field(..., description="Associated KIQ IDs")
    content_types: List[str] = Field(default_factory=list)
    update_frequency: str = Field(default="weekly")
    stakeholders: List[str] = Field(default_factory=list)

class KIQAlignment(BaseModel):
    """KIQ alignment assessment for content"""
    kiq_id: str = Field(..., description="KIQ identifier")
    alignment_score: float = Field(..., ge=0.0, le=1.0, description="Alignment score")
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence")
    gaps: List[str] = Field(default_factory=list, description="Information gaps")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Assessment confidence")

class KITClassification(BaseModel):
    """KIT classification for content"""
    kit_id: str = Field(..., description="KIT identifier")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Classification confidence")
    relevance_type: str = Field(default="primary", description="primary|secondary|tertiary")
    reasoning: str = Field(default="", description="Classification reasoning")

class RelevanceScores(BaseModel):
    """Multi-dimensional relevance scores"""
    kiq_alignment: float = Field(default=0.0, ge=0.0, le=1.0, description="KIQ alignment score")
    strategic_priority: float = Field(default=0.0, ge=0.0, le=1.0, description="Strategic priority score")
    content_quality: float = Field(default=0.0, ge=0.0, le=1.0, description="Content quality score")
    temporal_relevance: float = Field(default=0.0, ge=0.0, le=1.0, description="Temporal relevance score")
    composite_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Composite relevance score")
    
    def calculate_composite_score(self, weights: Dict[str, float] = None) -> float:
        """Calculate weighted composite score"""
        default_weights = {
            "kiq_alignment": 0.4,
            "strategic_priority": 0.3,
            "content_quality": 0.2,
            "temporal_relevance": 0.1
        }
        
        weights = weights or default_weights
        
        self.composite_score = (
            self.kiq_alignment * weights.get("kiq_alignment", 0.4) +
            self.strategic_priority * weights.get("strategic_priority", 0.3) +
            self.content_quality * weights.get("content_quality", 0.2) +
            self.temporal_relevance * weights.get("temporal_relevance", 0.1)
        )
        
        return self.composite_score

class RelevantContent(BaseModel):
    """Content item with relevance assessment"""
    id: str = Field(..., description="Content identifier")
    original_content: Dict[str, Any] = Field(..., description="Original content data")
    
    # Relevance assessment
    relevance_scores: RelevanceScores = Field(..., description="Relevance scores")
    processing_decision: RelevanceDecision = Field(..., description="Processing decision")
    
    # KIQ/KIT analysis
    kiq_alignments: List[KIQAlignment] = Field(default_factory=list)
    kit_classifications: List[KITClassification] = Field(default_factory=list)
    
    # Strategic value
    strategic_value: Dict[str, float] = Field(default_factory=dict)
    immediate_actionability: float = Field(default=0.0, ge=0.0, le=1.0)
    future_monitoring_value: float = Field(default=0.0, ge=0.0, le=1.0)
    intelligence_completeness: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Processing metadata
    processing_timestamp: datetime = Field(default_factory=datetime.utcnow)
    processing_notes: List[str] = Field(default_factory=list)
    
    def get_primary_kit(self) -> Optional[KITClassification]:
        """Get primary KIT classification"""
        primary_kits = [kit for kit in self.kit_classifications if kit.relevance_type == "primary"]
        return max(primary_kits, key=lambda x: x.confidence) if primary_kits else None
    
    def get_top_kiq_alignments(self, limit: int = 3) -> List[KIQAlignment]:
        """Get top KIQ alignments by score"""
        return sorted(self.kiq_alignments, key=lambda x: x.alignment_score, reverse=True)[:limit]

class RelevanceRequest(BaseModel):
    """Request for relevance assessment"""
    request_id: str = Field(..., description="Request identifier")
    content_items: List[Dict[str, Any]] = Field(..., description="Content to assess")
    kiqs: List[KeyIntelligenceQuestion] = Field(..., description="KIQs to evaluate against")
    kits: List[CriticalIntelligenceTopic] = Field(..., description="KITs for classification")
    
    # Scoring configuration
    relevance_threshold: float = Field(default=0.65, ge=0.0, le=1.0)
    manual_review_threshold: float = Field(default=0.55, ge=0.0, le=1.0)
    score_weights: Dict[str, float] = Field(default_factory=dict)
    
    # Processing options
    include_low_quality: bool = Field(default=False)
    require_kiq_alignment: bool = Field(default=True)
    min_strategic_priority: float = Field(default=0.0, ge=0.0, le=1.0)

class RelevanceResponse(BaseModel):
    """Response from relevance assessment"""
    request_id: str = Field(..., description="Request identifier")
    
    # Input summary
    total_input_items: int = Field(..., description="Total content items assessed")
    
    # Processing results
    included_content: List[RelevantContent] = Field(default_factory=list)
    excluded_content: List[RelevantContent] = Field(default_factory=list)
    manual_review_content: List[RelevantContent] = Field(default_factory=list)
    
    # Summary statistics
    inclusion_rate: float = Field(default=0.0, description="Percentage of content included")
    average_relevance_score: float = Field(default=0.0, description="Average relevance score")
    kiq_coverage: Dict[str, int] = Field(default_factory=dict, description="Content count per KIQ")
    kit_distribution: Dict[str, int] = Field(default_factory=dict, description="Content count per KIT")
    
    # Quality metrics
    high_confidence_items: int = Field(default=0, description="Items with high confidence scores")
    strategic_value_items: int = Field(default=0, description="Items with high strategic value")
    
    # Processing metadata
    processing_time: float = Field(default=0.0)
    kiqs_evaluated: int = Field(default=0)
    kits_used: int = Field(default=0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_summary_stats(self):
        """Calculate summary statistics"""
        self.inclusion_rate = (len(self.included_content) / self.total_input_items * 100) if self.total_input_items > 0 else 0.0
        
        all_scores = []
        for content_list in [self.included_content, self.excluded_content, self.manual_review_content]:
            all_scores.extend([item.relevance_scores.composite_score for item in content_list])
        
        self.average_relevance_score = sum(all_scores) / len(all_scores) if all_scores else 0.0
        
        # Calculate KIQ coverage
        self.kiq_coverage = {}
        for item in self.included_content:
            for alignment in item.kiq_alignments:
                self.kiq_coverage[alignment.kiq_id] = self.kiq_coverage.get(alignment.kiq_id, 0) + 1
        
        # Calculate KIT distribution
        self.kit_distribution = {}
        for item in self.included_content:
            for classification in item.kit_classifications:
                self.kit_distribution[classification.kit_id] = self.kit_distribution.get(classification.kit_id, 0) + 1
        
        # Count high-value items
        self.high_confidence_items = sum(1 for item in self.included_content if item.relevance_scores.composite_score >= 0.8)
        self.strategic_value_items = sum(1 for item in self.included_content if item.immediate_actionability >= 0.7)
```

## openai_api.py
```python
import asyncio
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .models import KeyIntelligenceQuestion, CriticalIntelligenceTopic, KIQAlignment, KITClassification
from ...config.settings import settings
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIAPI:
    """OpenAI client for relevance assessment tasks"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def assess_kiq_alignment(self, content: Dict[str, Any], kiq: KeyIntelligenceQuestion) -> KIQAlignment:
        """Assess how well content aligns with a KIQ"""
        try:
            content_text = self._extract_content_text(content)
            
            prompt = self._build_kiq_assessment_prompt(content_text, kiq)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert intelligence analyst specializing in assessing content relevance against strategic intelligence questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return KIQAlignment(
                kiq_id=kiq.id,
                alignment_score=float(result.get("alignment_score", 0.0)),
                evidence=result.get("evidence", []),
                gaps=result.get("gaps", []),
                confidence=float(result.get("confidence", 0.0))
            )
            
        except Exception as e:
            logger.error(f"KIQ alignment assessment failed for {kiq.id}: {str(e)}")
            return KIQAlignment(
                kiq_id=kiq.id,
                alignment_score=0.0,
                evidence=[],
                gaps=["Assessment failed"],
                confidence=0.0
            )
    
    async def classify_content_kit(self, content: Dict[str, Any], kits: List[CriticalIntelligenceTopic]) -> List[KITClassification]:
        """Classify content into KIT categories"""
        try:
            content_text = self._extract_content_text(content)
            
            prompt = self._build_kit_classification_prompt(content_text, kits)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in intelligence topic classification and content categorization."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            classifications = []
            
            for kit_result in result.get("classifications", []):
                classification = KITClassification(
                    kit_id=kit_result.get("kit_id"),
                    confidence=float(kit_result.get("confidence", 0.0)),
                    relevance_type=kit_result.get("relevance_type", "secondary"),
                    reasoning=kit_result.get("reasoning", "")
                )
                classifications.append(classification)
            
            return classifications
            
        except Exception as e:
            logger.error(f"KIT classification failed: {str(e)}")
            return []
    
    async def assess_strategic_value(self, content: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, float]:
        """Assess strategic value dimensions of content"""
        try:
            content_text = self._extract_content_text(content)
            
            prompt = self._build_strategic_value_prompt(content_text, context)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strategic intelligence analyst assessing content value for decision-making."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "immediate_actionability": float(result.get("immediate_actionability", 0.0)),
                "future_monitoring_value": float(result.get("future_monitoring_value", 0.0)),
                "intelligence_completeness": float(result.get("intelligence_completeness", 0.0)),
                "stakeholder_relevance": float(result.get("stakeholder_relevance", 0.0)),
                "risk_factor": float(result.get("risk_factor", 0.0))
            }
            
        except Exception as e:
            logger.error(f"Strategic value assessment failed: {str(e)}")
            return {
                "immediate_actionability": 0.0,
                "future_monitoring_value": 0.0,
                "intelligence_completeness": 0.0,
                "stakeholder_relevance": 0.0,
                "risk_factor": 0.0
            }
    
    async def analyze_content_quality(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content quality metrics"""
        try:
            content_text = self._extract_content_text(content)
            
            prompt = f"""
            Analyze the quality of this content for intelligence purposes:
            
            Title: {content.get('title', 'No title')}
            Content: {content_text[:1500]}...
            
            Assess and provide scores (0.0-1.0) for:
            1. factual_density - Amount of concrete facts vs opinion
            2. source_authority - Credibility of the source
            3. information_clarity - How clear and understandable the content is
            4. completeness - How complete the information appears
            5. actionability - How actionable the information is
            6. verification_level - How well-verified the information seems
            
            Respond in JSON format with scores and brief explanations.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a content quality analyst for intelligence assessment."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            logger.error(f"Content quality analysis failed: {str(e)}")
            return {"factual_density": 0.5, "source_authority": 0.5, "information_clarity": 0.5}
    
    def _extract_content_text(self, content: Dict[str, Any]) -> str:
        """Extract text content for analysis"""
        text_parts = []
        
        if content.get("title"):
            text_parts.append(f"Title: {content['title']}")
        
        if content.get("content"):
            text_parts.append(f"Content: {content['content']}")
        
        if content.get("summary"):
            text_parts.append(f"Summary: {content['summary']}")
        
        return "\n\n".join(text_parts)
    
    def _build_kiq_assessment_prompt(self, content: str, kiq: KeyIntelligenceQuestion) -> str:
        """Build prompt for KIQ alignment assessment"""
        return f"""
        Assess how well this content answers the following Key Intelligence Question:
        
        KIQ: {kiq.question}
        Category: {kiq.category.value}
        Keywords: {', '.join(kiq.keywords)}
        Contexts: {', '.join(kiq.contexts)}
        
        Content to assess:
        {content[:2000]}
        
        Provide assessment in JSON format:
        {{
            "alignment_score": 0.0-1.0,
            "evidence": ["specific evidence from content that answers the KIQ"],
            "gaps": ["information gaps that prevent fully answering the KIQ"],
            "confidence": 0.0-1.0,
            "reasoning": "explanation of the assessment"
        }}
        
        Scoring guidelines:
        - 0.9-1.0: Directly and comprehensively answers the KIQ
        - 0.7-0.9: Significantly addresses the KIQ with good detail
        - 0.5-0.7: Partially addresses the KIQ
        - 0.3-0.5: Tangentially related to the KIQ
        - 0.0-0.3: Little to no relevance to the KIQ
        """
    
    def _build_kit_classification_prompt(self, content: str, kits: List[CriticalIntelligenceTopic]) -> str:
        """Build prompt for KIT classification"""
        kit_descriptions = []
        for kit in kits:
            kit_descriptions.append(f"- {kit.kit_id}: {kit.name} - {kit.description}")
        
        return f"""
        Classify this content into the most relevant Critical Intelligence Topics (KITs):
        
        Available KITs:
        {chr(10).join(kit_descriptions)}
        
        Content to classify:
        {content[:2000]}
        
        Provide classification in JSON format:
        {{
            "classifications": [
                {{
                    "kit_id": "KIT-XXX",
                    "confidence": 0.0-1.0,
                    "relevance_type": "primary|secondary|tertiary",
                    "reasoning": "why this content fits this KIT"
                }}
            ]
        }}
        
        Guidelines:
        - Primary: Main focus of the content
        - Secondary: Significant related topic
        - Tertiary: Minor relevance
        - Only include KITs with confidence >= 0.3
        """
    
    def _build_strategic_value_prompt(self, content: str, context: Dict[str, Any] = None) -> str:
        """Build prompt for strategic value assessment"""
        context_info = ""
        if context:
            context_info = f"Business context: {context.get('business_context', '')}\n"
        
        return f"""
        Assess the strategic value of this content for business intelligence:
        
        {context_info}
        Content:
        {content[:1500]}
        
        Provide assessment in JSON format:
        {{
            "immediate_actionability": 0.0-1.0,
            "future_monitoring_value": 0.0-1.0,
            "intelligence_completeness": 0.0-1.0,
            "stakeholder_relevance": 0.0-1.0,
            "risk_factor": 0.0-1.0,
            "reasoning": "explanation of the strategic value assessment"
        }}
        
        Scoring criteria:
        - Immediate actionability: Can decisions be made based on this info?
        - Future monitoring value: Should this trend be monitored?
        - Intelligence completeness: How complete is the intelligence picture?
        - Stakeholder relevance: How relevant to key stakeholders?
        - Risk factor: Does this indicate potential risks?
        """
```

## openai_mock.py
```python
import asyncio
import random
from typing import List, Dict, Any
from .models import KeyIntelligenceQuestion, CriticalIntelligenceTopic, KIQAlignment, KITClassification
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIMock:
    """Mock OpenAI client for testing relevance assessment"""
    
    def __init__(self):
        random.seed(42)  # For reproducible results
    
    async def assess_kiq_alignment(self, content: Dict[str, Any], kiq: KeyIntelligenceQuestion) -> KIQAlignment:
        """Mock KIQ alignment assessment"""
        await asyncio.sleep(0.1)  # Simulate API latency
        
        content_text = self._extract_content_text(content)
        
        # Calculate mock alignment based on keyword matching
        keyword_score = kiq.calculate_keyword_match_score(content_text)
        
        # Add some realistic variation
        base_score = keyword_score * 0.8 + random.uniform(0.0, 0.2)
        alignment_score = min(max(base_score, 0.0), 1.0)
        
        # Generate mock evidence and gaps
        evidence = self._generate_mock_evidence(content, kiq, alignment_score)
        gaps = self._generate_mock_gaps(kiq, alignment_score)
        
        confidence = min(alignment_score + random.uniform(0.0, 0.2), 1.0)
        
        logger.debug(f"Mock KIQ alignment for {kiq.id}: {alignment_score:.2f}")
        
        return KIQAlignment(
            kiq_id=kiq.id,
            alignment_score=alignment_score,
            evidence=evidence,
            gaps=gaps,
            confidence=confidence
        )
    
    async def classify_content_kit(self, content: Dict[str, Any], kits: List[CriticalIntelligenceTopic]) -> List[KITClassification]:
        """Mock KIT classification"""
        await asyncio.sleep(0.1)
        
        content_text = self._extract_content_text(content).lower()
        classifications = []
        
        for kit in kits:
            # Calculate relevance based on description keywords
            description_words = kit.description.lower().split()
            name_words = kit.name.lower().split()
            
            relevance_score = 0.0
            
            # Check name relevance (higher weight)
            for word in name_words:
                if word in content_text:
                    relevance_score += 0.3
            
            # Check description relevance
            for word in description_words:
                if word in content_text:
                    relevance_score += 0.1
            
            # Add randomness
            relevance_score += random.uniform(0.0, 0.3)
            relevance_score = min(relevance_score, 1.0)
            
            # Only include if above threshold
            if relevance_score >= 0.3:
                relevance_type = self._determine_relevance_type(relevance_score)
                reasoning = self._generate_kit_reasoning(content, kit, relevance_score)
                
                classification = KITClassification(
                    kit_id=kit.kit_id,
                    confidence=relevance_score,
                    relevance_type=relevance_type,
                    reasoning=reasoning
                )
                classifications.append(classification)
        
        # Sort by confidence
        classifications.sort(key=lambda x: x.confidence, reverse=True)
        
        logger.debug(f"Mock KIT classifications: {len(classifications)} KITs matched")
        
        return classifications[:3]  # Return top 3
    
    async def assess_strategic_value(self, content: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, float]:
        """Mock strategic value assessment"""
        await asyncio.sleep(0.1)
        
        # Base scores on content characteristics
        content_text = self._extract_content_text(content)
        
        # Mock scoring based on content indicators
        immediate_actionability = self._assess_actionability(content_text)
        future_monitoring_value = self._assess_monitoring_value(content_text)
        intelligence_completeness = self._assess_completeness(content)
        stakeholder_relevance = self._assess_stakeholder_relevance(content_text)
        risk_factor = self._assess_risk_factor(content_text)
        
        return {
            "immediate_actionability": immediate_actionability,
            "future_monitoring_value": future_monitoring_value,
            "intelligence_completeness": intelligence_completeness,
            "stakeholder_relevance": stakeholder_relevance,
            "risk_factor": risk_factor
        }
    
    async def analyze_content_quality(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Mock content quality analysis"""
        await asyncio.sleep(0.05)
        
        # Mock quality scores based on content characteristics
        content_text = self._extract_content_text(content)
        word_count = len(content_text.split())
        
        # Base quality on various factors
        factual_density = min(0.4 + (word_count / 1000) * 0.5, 1.0)
        source_authority = self._assess_source_authority(content)
        information_clarity = random.uniform(0.6, 0.9)
        completeness = min(0.3 + (word_count / 500) * 0.6, 1.0)
        actionability = random.uniform(0.4, 0.8)
        verification_level = random.uniform(0.5, 0.8)
        
        return {
            "factual_density": factual_density,
            "source_authority": source_authority,
            "information_clarity": information_clarity,
            "completeness": completeness,
            "actionability": actionability,
            "verification_level": verification_level,
            "overall_quality": (factual_density + source_authority + information_clarity) / 3
        }
    
    def _extract_content_text(self, content: Dict[str, Any]) -> str:
        """Extract text content for analysis"""
        text_parts = []
        
        if content.get("title"):
            text_parts.append(content["title"])
        
        if content.get("content"):
            text_parts.append(content["content"])
        
        if content.get("summary"):
            text_parts.append(content["summary"])
        
        return " ".join(text_parts)
    
    def _generate_mock_evidence(self, content: Dict[str, Any], kiq: KeyIntelligenceQuestion, score: float) -> List[str]:
        """Generate mock evidence list"""
        if score < 0.3:
            return []
        
        evidence_templates = [
            f"Content mentions {random.choice(kiq.keywords)} in context of {kiq.category.value}",
            f"Article discusses topic directly related to {kiq.question[:50]}...",
            f"Source provides specific data relevant to {kiq.category.value}",
            "Content includes factual information addressing the intelligence question",
            "Multiple data points support the strategic intelligence need"
        ]
        
        num_evidence = int(score * 3) + 1  # 1-4 evidence items based on score
        return random.sample(evidence_templates, min(num_evidence, len(evidence_templates)))
    
    def _generate_mock_gaps(self, kiq: KeyIntelligenceQuestion, score: float) -> List[str]:
        """Generate mock information gaps"""
        if score > 0.8:
            return []
        
        gap_templates = [
            "Missing quantitative data to fully answer the question",
            "Lacks specific timeline information",
            "No mention of competitive implications",
            "Limited geographic scope coverage",
            "Insufficient detail on implementation specifics",
            "Missing risk assessment components"
        ]
        
        num_gaps = max(1, int((1 - score) * 3))  # More gaps for lower scores
        return random.sample(gap_templates, min(num_gaps, len(gap_templates)))
    
    def _determine_relevance_type(self, score: float) -> str:
        """Determine KIT relevance type based on score"""
        if score >= 0.7:
            return "primary"
        elif score >= 0.5:
            return "secondary"
        else:
            return "tertiary"
    
    def _generate_kit_reasoning(self, content: Dict[str, Any], kit: CriticalIntelligenceTopic, score: float) -> str:
        """Generate mock reasoning for KIT classification"""
        if score >= 0.7:
            return f"Content directly addresses {kit.name} with substantial relevant information"
        elif score >= 0.5:
            return f"Content has significant relevance to {kit.name} topic area"
        else:
            return f"Content tangentially relates to {kit.name} concepts"
    
    def _assess_actionability(self, content_text: str) -> float:
        """Mock assessment of immediate actionability"""
        actionable_indicators = ["should", "must", "recommend", "urgent", "immediate", "action", "decision"]
        content_lower = content_text.lower()
        
        base_score = sum(0.1 for indicator in actionable_indicators if indicator in content_lower)
        return min(base_score + random.uniform(0.2, 0.5), 1.0)
    
    def _assess_monitoring_value(self, content_text: str) -> float:
        """Mock assessment of future monitoring value"""
        monitoring_indicators = ["trend", "forecast", "future", "predict", "outlook", "emerging", "developing"]
        content_lower = content_text.lower()
        
        base_score = sum(0.1 for indicator in monitoring_indicators if indicator in content_lower)
        return min(base_score + random.uniform(0.3, 0.6), 1.0)
    
    def _assess_completeness(self, content: Dict[str, Any]) -> float:
        """Mock assessment of intelligence completeness"""
        word_count = len(self._extract_content_text(content).split())
        
        # More words generally indicate more completeness
        base_score = min(word_count / 1000, 0.8)
        return base_score + random.uniform(0.1, 0.2)
    
    def _assess_stakeholder_relevance(self, content_text: str) -> float:
        """Mock assessment of stakeholder relevance"""
        stakeholder_indicators = ["executive", "board", "management", "leadership", "decision", "strategy"]
        content_lower = content_text.lower()
        
        base_score = sum(0.1 for indicator in stakeholder_indicators if indicator in content_lower)
        return min(base_score + random.uniform(0.4, 0.7), 1.0)
    
    def _assess_risk_factor(self, content_text: str) -> float:
        """Mock assessment of risk factors"""
        risk_indicators = ["risk", "threat", "challenge", "concern", "warning", "alert", "danger"]
        content_lower = content_text.lower()
        
        base_score = sum(0.15 for indicator in risk_indicators if indicator in content_lower)
        return min(base_score + random.uniform(0.1, 0.4), 1.0)
    
    def _assess_source_authority(self, content: Dict[str, Any]) -> float:
        """Mock assessment of source authority"""
        url = content.get("url", "")
        domain = content.get("domain", "")
        
        # Authority based on domain
        authoritative_domains = [".gov", ".edu", "reuters", "bloomberg", "wsj", "fda", "sec"]
        
        authority_score = 0.5  # Base score
        
        for auth_domain in authoritative_domains:
            if auth_domain in url.lower() or auth_domain in domain.lower():
                authority_score += 0.3
                break
        
        return min(authority_score + random.uniform(0.0, 0.2), 1.0)
```

## kiq_engine.py
```python
from typing import List, Dict, Any, Optional
import asyncio
from .models import KeyIntelligenceQuestion, KIQAlignment, KIQCategory
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class KIQEngine:
    """Engine for evaluating content against Key Intelligence Questions"""
    
    def __init__(self):
        self.openai_client = ServiceFactory.get_openai_client()
        self.default_kiqs = self._load_default_kiqs()
    
    async def evaluate_content_against_kiqs(self, content: Dict[str, Any], kiqs: List[KeyIntelligenceQuestion]) -> List[KIQAlignment]:
        """Evaluate how well content aligns with KIQs"""
        try:
            logger.info(f"Evaluating content against {len(kiqs)} KIQs")
            
            alignments = []
            
            for kiq in kiqs:
                try:
                    alignment = await self.openai_client.assess_kiq_alignment(content, kiq)
                    alignments.append(alignment)
                    
                    # Rate limiting
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"KIQ evaluation failed for {kiq.id}: {str(e)}")
                    continue
            
            # Sort by alignment score
            alignments.sort(key=lambda x: x.alignment_score, reverse=True)
            
            logger.info(f"Completed KIQ evaluation: {len(alignments)} alignments")
            return alignments
            
        except Exception as e:
            logger.error(f"KIQ evaluation failed: {str(e)}")
            return []
    
    def calculate_kiq_coverage_score(self, alignments: List[KIQAlignment], threshold: float = 0.6) -> float:
        """Calculate overall KIQ coverage score"""
        if not alignments:
            return 0.0
        
        # Count alignments above threshold
        strong_alignments = [a for a in alignments if a.alignment_score >= threshold]
        
        # Calculate weighted score
        total_weight = sum(a.alignment_score for a in alignments)
        strong_weight = sum(a.alignment_score for a in strong_alignments)
        
        coverage_ratio = len(strong_alignments) / len(alignments)
        weighted_ratio = strong_weight / total_weight if total_weight > 0 else 0
        
        # Combined score
        coverage_score = (coverage_ratio * 0.6) + (weighted_ratio * 0.4)
        
        return min(coverage_score, 1.0)
    
    def identify_kiq_gaps(self, alignments: List[KIQAlignment], kiqs: List[KeyIntelligenceQuestion]) -> List[str]:
        """Identify KIQs that are poorly addressed"""
        gaps = []
        
        for alignment in alignments:
            if alignment.alignment_score < 0.5:
                # Find the KIQ for this alignment
                kiq = next((k for k in kiqs if k.id == alignment.kiq_id), None)
                if kiq:
                    gaps.extend(alignment.gaps)
        
        return list(set(gaps))  # Remove duplicates
    
    def get_top_kiq_alignments(self, alignments: List[KIQAlignment], limit: int = 3) -> List[KIQAlignment]:
        """Get top KIQ alignments by score"""
        sorted_alignments = sorted(alignments, key=lambda x: x.alignment_score, reverse=True)
        return sorted_alignments[:limit]
    
    def filter_kiqs_by_category(self, kiqs: List[KeyIntelligenceQuestion], category: KIQCategory) -> List[KeyIntelligenceQuestion]:
        """Filter KIQs by category"""
        return [kiq for kiq in kiqs if kiq.category == category]
    
    def calculate_category_coverage(self, alignments: List[KIQAlignment], kiqs: List[KeyIntelligenceQuestion]) -> Dict[str, float]:
        """Calculate coverage by KIQ category"""
        category_scores = {}
        category_counts = {}
        
        # Group alignments by category
        for alignment in alignments:
            kiq = next((k for k in kiqs if k.id == alignment.kiq_id), None)
            if kiq:
                category = kiq.category.value
                
                if category not in category_scores:
                    category_scores[category] = 0.0
                    category_counts[category] = 0
                
                category_scores[category] += alignment.alignment_score
                category_counts[category] += 1
        
        # Calculate average scores
        category_coverage = {}
        for category, total_score in category_scores.items():
            count = category_counts[category]
            category_coverage[category] = total_score / count if count > 0 else 0.0
        
        return category_coverage
    
    def _load_default_kiqs(self) -> List[KeyIntelligenceQuestion]:
        """Load default KIQ set for pharmaceutical industry"""
        return [
            KeyIntelligenceQuestion(
                id="KIQ-001",
                category=KIQCategory.COMPETITIVE_INTELLIGENCE,
                question="What are competitors' drug development pipelines and timelines?",
                keywords=["pipeline", "phase", "clinical trial", "FDA approval", "competitor", "drug development"],
                weight=0.9,
                contexts=["regulatory", "development", "market_entry"]
            ),
            KeyIntelligenceQuestion(
                id="KIQ-002",
                category=KIQCategory.REGULATORY_LANDSCAPE,
                question="What regulatory changes affect our therapeutic areas?",
                keywords=["FDA", "EMA", "regulation", "guideline", "approval", "safety", "compliance"],
                weight=0.95,
                contexts=["compliance", "market_access", "safety"]
            ),
            KeyIntelligenceQuestion(
                id="KIQ-003",
                category=KIQCategory.MARKET_DYNAMICS,
                question="What are pricing pressures and market access challenges?",
                keywords=["pricing", "reimbursement", "payer", "formulary", "access", "cost"],
                weight=0.85,
                contexts=["commercial", "market_access", "pricing"]
            ),
            KeyIntelligenceQuestion(
                id="KIQ-004",
                category=KIQCategory.TECHNOLOGY_INNOVATION,
                question="What emerging technologies could disrupt our markets?",
                keywords=["AI", "digital health", "biomarker", "precision medicine", "technology"],
                weight=0.8,
                contexts=["innovation", "disruption", "technology"]
            ),
            KeyIntelligenceQuestion(
                id="KIQ-005",
                category=KIQCategory.RISK_ASSESSMENT,
                question="What are potential regulatory or safety risks?",
                keywords=["risk", "safety", "adverse event", "recall", "warning", "liability"],
                weight=0.9,
                contexts=["risk_management", "safety", "compliance"]
            )
        ]
```

## kit_classifier.py
```python
from typing import List, Dict, Any, Optional
import asyncio
from .models import CriticalIntelligenceTopic, KITClassification
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class KITClassifier:
    """Classifier for organizing content into Critical Intelligence Topics"""
    
    def __init__(self):
        self.openai_client = ServiceFactory.get_openai_client()
        self.default_kits = self._load_default_kits()
    
    async def classify_content(self, content: Dict[str, Any], kits: List[CriticalIntelligenceTopic]) -> List[KITClassification]:
        """Classify content into KIT categories"""
        try:
            logger.info(f"Classifying content into {len(kits)} KITs")
            
            classifications = await self.openai_client.classify_content_kit(content, kits)
            
            # Enhance classifications with additional analysis
            enhanced_classifications = self._enhance_classifications(content, classifications, kits)
            
            # Filter and sort results
            final_classifications = self._filter_and_rank_classifications(enhanced_classifications)
            
            logger.info(f"Content classified into {len(final_classifications)} KITs")
            return final_classifications
            
        except Exception as e:
            logger.error(f"KIT classification failed: {str(e)}")
            return []
    
    def _enhance_classifications(self, content: Dict[str, Any], classifications: List[KITClassification], kits: List[CriticalIntelligenceTopic]) -> List[KITClassification]:
        """Enhance classifications with additional analysis"""
        enhanced = []
        
        for classification in classifications:
            # Find the KIT
            kit = next((k for k in kits if k.kit_id == classification.kit_id), None)
            if not kit:
                continue
            
            # Enhance with keyword matching
            keyword_score = self._calculate_keyword_match(content, kit)
            
            # Adjust confidence based on keyword matching
            adjusted_confidence = (classification.confidence * 0.7) + (keyword_score * 0.3)
            
            enhanced_classification = KITClassification(
                kit_id=classification.kit_id,
                confidence=min(adjusted_confidence, 1.0),
                relevance_type=classification.relevance_type,
                reasoning=f"{classification.reasoning} (keyword match: {keyword_score:.2f})"
            )
            
            enhanced.append(enhanced_classification)
        
        return enhanced
    
    def _calculate_keyword_match(self, content: Dict[str, Any], kit: CriticalIntelligenceTopic) -> float:
        """Calculate keyword match score for KIT"""
        content_text = self._extract_content_text(content).lower()
        
        # Extract keywords from KIT name and description
        kit_keywords = []
        kit_keywords.extend(kit.name.lower().split())
        kit_keywords.extend(kit.description.lower().split())
        
        # Remove common words
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        kit_keywords = [word for word in kit_keywords if word not in stop_words and len(word) > 2]
        
        # Calculate match score
        matches = sum(1 for keyword in kit_keywords if keyword in content_text)
        
        return min(matches / len(kit_keywords), 1.0) if kit_keywords else 0.0
    
    def _filter_and_rank_classifications(self, classifications: List[KITClassification]) -> List[KITClassification]:
        """Filter and rank classifications"""
        # Filter by minimum confidence
        filtered = [c for c in classifications if c.confidence >= 0.3]
        
        # Sort by confidence
        filtered.sort(key=lambda x: x.confidence, reverse=True)
        
        # Limit to top classifications
        return filtered[:5]
    
    def calculate_kit_distribution(self, all_classifications: List[List[KITClassification]]) -> Dict[str, int]:
        """Calculate distribution of content across KITs"""
        kit_counts = {}
        
        for classifications in all_classifications:
            for classification in classifications:
                if classification.relevance_type == "primary":
                    kit_counts[classification.kit_id] = kit_counts.get(classification.kit_id, 0) + 1
        
        return kit_counts
    
    def identify_underrepresented_kits(self, kit_distribution: Dict[str, int], kits: List[CriticalIntelligenceTopic], threshold: int = 2) -> List[str]:
        """Identify KITs with insufficient content coverage"""
        underrepresented = []
        
        for kit in kits:
            count = kit_distribution.get(kit.kit_id, 0)
            if count < threshold:
                underrepresented.append(kit.kit_id)
        
        return underrepresented
    
    def get_kit_by_priority(self, kits: List[CriticalIntelligenceTopic], priority: str) -> List[CriticalIntelligenceTopic]:
        """Get KITs filtered by priority level"""
        return [kit for kit in kits if kit.priority.lower() == priority.lower()]
    
    def _extract_content_text(self, content: Dict[str, Any]) -> str:
        """Extract text content for analysis"""
        text_parts = []
        
        if content.get("title"):
            text_parts.append(content["title"])
        
        if content.get("content"):
            text_parts.append(content["content"])
        
        if content.get("summary"):
            text_parts.append(content["summary"])
        
        return " ".join(text_parts)
    
    def _load_default_kits(self) -> List[CriticalIntelligenceTopic]:
        """Load default KIT set for pharmaceutical industry"""
        return [
            CriticalIntelligenceTopic(
                kit_id="KIT-001",
                name="Competitive Pipeline Intelligence",
                description="Monitor competitor drug development and market strategies",
                priority="high",
                associated_kiqs=["KIQ-001", "KIQ-003"],
                content_types=["clinical_data", "regulatory_filings", "earnings_calls"],
                update_frequency="daily",
                stakeholders=["R&D", "Business Development", "Commercial"]
            ),
            CriticalIntelligenceTopic(
                kit_id="KIT-002",
                name="Regulatory Environment Monitoring",
                description="Track regulatory changes and policy developments",
                priority="critical",
                associated_kiqs=["KIQ-002"],
                content_types=["regulatory_guidance", "policy_announcements"],
                update_frequency="real_time",
                stakeholders=["Regulatory Affairs", "Legal", "Quality"]
            ),
            CriticalIntelligenceTopic(
                kit_id="KIT-003",
                name="Market Access Intelligence",
                description="Monitor payer trends and access challenges",
                priority="high",
                associated_kiqs=["KIQ-003"],
                content_types=["payer_policies", "health_economics", "market_research"],
                update_frequency="weekly",
                stakeholders=["Market Access", "Commercial", "Health Economics"]
            ),
            CriticalIntelligenceTopic(
                kit_id="KIT-004",
                name="Technology Innovation Tracking",
                description="Monitor emerging technologies and digital health trends",
                priority="medium",
                associated_kiqs=["KIQ-004"],
                content_types=["technology_reports", "innovation_news", "patent_filings"],
                update_frequency="weekly",
                stakeholders=["Innovation", "Digital Health", "R&D"]
            )
        ]
```

## scoring_engine.py
```python
from typing import Dict, Any, List, Optional
from .models import RelevanceScores, KIQAlignment, KITClassification, RelevanceDecision
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class ScoringEngine:
    """Engine for calculating multi-dimensional relevance scores"""
    
    def __init__(self):
        self.default_weights = {
            "kiq_alignment": 0.4,
            "strategic_priority": 0.3,
            "content_quality": 0.2,
            "temporal_relevance": 0.1
        }
        
        self.default_thresholds = {
            "include": 0.65,
            "manual_review": 0.55,
            "exclude": 0.55  # Below this threshold
        }
    
    def calculate_relevance_scores(self, 
                                 content: Dict[str, Any],
                                 kiq_alignments: List[KIQAlignment],
                                 kit_classifications: List[KITClassification],
                                 quality_metrics: Dict[str, Any],
                                 strategic_values: Dict[str, float],
                                 weights: Dict[str, float] = None) -> RelevanceScores:
        """Calculate comprehensive relevance scores"""
        try:
            weights = weights or self.default_weights
            
            # Calculate individual dimension scores
            kiq_score = self._calculate_kiq_alignment_score(kiq_alignments)
            priority_score = self._calculate_strategic_priority_score(kit_classifications, strategic_values)
            quality_score = self._calculate_content_quality_score(quality_metrics)
            temporal_score = self._calculate_temporal_relevance_score(content)
            
            # Create relevance scores object
            scores = RelevanceScores(
                kiq_alignment=kiq_score,
                strategic_priority=priority_score,
                content_quality=quality_score,
                temporal_relevance=temporal_score
            )
            
            # Calculate composite score
            scores.calculate_composite_score(weights)
            
            logger.debug(f"Calculated relevance scores: composite={scores.composite_score:.2f}")
            return scores
            
        except Exception as e:
            logger.error(f"Relevance score calculation failed: {str(e)}")
            return RelevanceScores()
    
    def make_relevance_decision(self, relevance_scores: RelevanceScores, thresholds: Dict[str, float] = None) -> RelevanceDecision:
        """Make include/exclude/review decision based on scores"""
        thresholds = thresholds or self.default_thresholds
        
        composite_score = relevance_scores.composite_score
        
        if composite_score >= thresholds["include"]:
            return RelevanceDecision.INCLUDE
        elif composite_score >= thresholds["manual_review"]:
            return RelevanceDecision.MANUAL_REVIEW
        else:
            return RelevanceDecision.EXCLUDE
    
    def _calculate_kiq_alignment_score(self, alignments: List[KIQAlignment]) -> float:
        """Calculate KIQ alignment dimension score"""
        if not alignments:
            return 0.0
        
        # Weighted average of top alignments
        top_alignments = sorted(alignments, key=lambda x: x.alignment_score, reverse=True)[:3]
        
        if not top_alignments:
            return 0.0
        
        # Weight the top alignment more heavily
        weights = [0.5, 0.3, 0.2]
        weighted_sum = 0.0
        total_weight = 0.0
        
        for i, alignment in enumerate(top_alignments):
            weight = weights[i] if i < len(weights) else 0.1
            weighted_sum += alignment.alignment_score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _calculate_strategic_priority_score(self, classifications: List[KITClassification], strategic_values: Dict[str, float]) -> float:
        """Calculate strategic priority dimension score"""
        if not classifications:
            return 0.0
        
        # Get highest confidence classification
        primary_classification = max(classifications, key=lambda x: x.confidence)
        
        # Base score from classification confidence
        base_score = primary_classification.confidence
        
        # Adjust based on strategic values
        strategic_multiplier = 1.0
        
        # Immediate actionability boosts priority
        actionability = strategic_values.get("immediate_actionability", 0.0)
        strategic_multiplier += actionability * 0.3
        
        # Risk factor also boosts priority
        risk_factor = strategic_values.get("risk_factor", 0.0)
        strategic_multiplier += risk_factor * 0.2
        
        # Stakeholder relevance
        stakeholder_relevance = strategic_values.get("stakeholder_relevance", 0.0)
        strategic_multiplier += stakeholder_relevance * 0.2
        
        final_score = base_score * strategic_multiplier
        return min(final_score, 1.0)
    
    def _calculate_content_quality_score(self, quality_metrics: Dict[str, Any]) -> float:
        """Calculate content quality dimension score"""
        if not quality_metrics:
            return 0.5  # Default moderate quality
        
        # Key quality factors
        factual_density = quality_metrics.get("factual_density", 0.5)
        source_authority = quality_metrics.get("source_authority", 0.5)
        information_clarity = quality_metrics.get("information_clarity", 0.5)
        completeness = quality_metrics.get("completeness", 0.5)
        verification_level = quality_metrics.get("verification_level", 0.5)
        
        # Weighted average
        quality_score = (
            factual_density * 0.25 +
            source_authority * 0.25 +
            information_clarity * 0.2 +
            completeness * 0.2 +
            verification_level * 0.1
        )
        
        return min(quality_score, 1.0)
    
    def _calculate_temporal_relevance_score(self, content: Dict[str, Any]) -> float:
        """Calculate temporal relevance dimension score"""
        try:
            from datetime import datetime, timedelta
            
            # Try to extract publication date
            pub_date = content.get("published_date")
            if isinstance(pub_date, str):
                try:
                    pub_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                except:
                    pub_date = None
            
            if not pub_date:
                return 0.5  # Default moderate temporal relevance
            
            # Calculate recency score
            now = datetime.utcnow()
            days_old = (now - pub_date).days
            
            # Recency scoring curve
            if days_old <= 1:
                recency_score = 1.0
            elif days_old <= 7:
                recency_score = 0.9
            elif days_old <= 30:
                recency_score = 0.7
            elif days_old <= 90:
                recency_score = 0.5
            elif days_old <= 180:
                recency_score = 0.3
            else:
                recency_score = 0.1
            
            # Check for trend momentum indicators
            content_text = (content.get("content", "") + " " + content.get("title", "")).lower()
            
            trend_indicators = ["trend", "emerging", "growing", "increasing", "rising", "future", "upcoming"]
            trend_momentum = sum(0.1 for indicator in trend_indicators if indicator in content_text)
            trend_momentum = min(trend_momentum, 0.3)
            
            # Combined temporal score
            temporal_score = (recency_score * 0.8) + (trend_momentum * 0.2)
            
            return min(temporal_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Temporal relevance calculation failed: {str(e)}")
            return 0.5
    
    def analyze_score_distribution(self, all_scores: List[RelevanceScores]) -> Dict[str, Any]:
        """Analyze distribution of relevance scores"""
        if not all_scores:
            return {}
        
        composite_scores = [score.composite_score for score in all_scores]
        
        return {
            "total_items": len(all_scores),
            "average_score": sum(composite_scores) / len(composite_scores),
            "median_score": sorted(composite_scores)[len(composite_scores) // 2],
            "high_relevance_count": sum(1 for score in composite_scores if score >= 0.8),
            "medium_relevance_count": sum(1 for score in composite_scores if 0.5 <= score < 0.8),
            "low_relevance_count": sum(1 for score in composite_scores if score < 0.5),
            "score_quartiles": self._calculate_quartiles(composite_scores)
        }
    
    def _calculate_quartiles(self, scores: List[float]) -> Dict[str, float]:
        """Calculate score quartiles"""
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        
        return {
            "q1": sorted_scores[n // 4],
            "q2": sorted_scores[n // 2],
            "q3": sorted_scores[3 * n // 4]
        }
    
    def suggest_threshold_adjustments(self, decisions: List[RelevanceDecision], scores: List[RelevanceScores]) -> Dict[str, float]:
        """Suggest threshold adjustments based on outcomes"""
        if len(decisions) != len(scores):
            return self.default_thresholds
        
        # Analyze current threshold performance
        included_scores = [score.composite_score for i, score in enumerate(scores) if decisions[i] == RelevanceDecision.INCLUDE]
        excluded_scores = [score.composite_score for i, score in enumerate(scores) if decisions[i] == RelevanceDecision.EXCLUDE]
        
        if not included_scores or not excluded_scores:
            return self.default_thresholds
        
        # Calculate optimal thresholds
        min_included = min(included_scores)
        max_excluded = max(excluded_scores)
        
        # Suggest new thresholds with safety margin
        suggested_include = (min_included + max_excluded) / 2
        suggested_review = max_excluded + 0.05
        
        return {
            "include": max(suggested_include, 0.6),
            "manual_review": max(suggested_review, 0.5),
            "exclude": max(suggested_review, 0.5)
        }
```

## service.py
```python
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from .models import RelevanceRequest, RelevanceResponse, RelevantContent, RelevanceDecision
from .kiq_engine import KIQEngine
from .kit_classifier import KITClassifier
from .scoring_engine import ScoringEngine
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class RelevanceService:
    """Main relevance service for content filtering and assessment"""
    
    def __init__(self):
        self.openai_client = ServiceFactory.get_openai_client()
        self.kiq_engine = KIQEngine()
        self.kit_classifier = KITClassifier()
        self.scoring_engine = ScoringEngine()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def process_relevance_assessment(self, request: RelevanceRequest) -> RelevanceResponse:
        """Execute complete relevance assessment pipeline"""
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting relevance assessment for request {request.request_id}")
            
            # Process each content item
            relevant_content_items = []
            
            for i, content_item in enumerate(request.content_items):
                try:
                    logger.debug(f"Processing item {i+1}/{len(request.content_items)}")
                    
                    relevant_content = await self._assess_single_item(content_item, request)
                    relevant_content_items.append(relevant_content)
                    
                except Exception as e:
                    logger.warning(f"Failed to assess item {i+1}: {str(e)}")
                    continue
            
            # Categorize results
            response = self._categorize_results(request, relevant_content_items, start_time)
            
            # Store results
            await self._store_results(response)
            
            logger.info(f"Relevance assessment completed: {len(response.included_content)} included, {len(response.excluded_content)} excluded")
            return response
            
        except Exception as e:
            logger.error(f"Relevance assessment failed for {request.request_id}: {str(e)}")
            raise Exception(f"Relevance assessment failed: {str(e)}")
    
    async def _assess_single_item(self, content: Dict[str, Any], request: RelevanceRequest) -> RelevantContent:
        """Assess relevance of single content item"""
        try:
            # Stage 1: KIQ alignment assessment
            kiq_alignments = await self.kiq_engine.evaluate_content_against_kiqs(content, request.kiqs)
            
            # Stage 2: KIT classification
            kit_classifications = await self.kit_classifier.classify_content(content, request.kits)
            
            # Stage 3: Content quality analysis
            quality_metrics = await self.openai_client.analyze_content_quality(content)
            
            # Stage 4: Strategic value assessment
            strategic_values = await self.openai_client.assess_strategic_value(content)
            
            # Stage 5: Calculate relevance scores
            relevance_scores = self.scoring_engine.calculate_relevance_scores(
                content=content,
                kiq_alignments=kiq_alignments,
                kit_classifications=kit_classifications,
                quality_metrics=quality_metrics,
                strategic_values=strategic_values,
                weights=request.score_weights
            )
            
            # Stage 6: Make processing decision
            processing_decision = self.scoring_engine.make_relevance_decision(
                relevance_scores,
                {
                    "include": request.relevance_threshold,
                    "manual_review": request.manual_review_threshold,
                    "exclude": request.manual_review_threshold
                }
            )
            
            # Apply additional filters
            if request.require_kiq_alignment and not kiq_alignments:
                processing_decision = RelevanceDecision.EXCLUDE
            
            if strategic_values.get("immediate_actionability", 0.0) < request.min_strategic_priority:
                if processing_decision == RelevanceDecision.INCLUDE:
                    processing_decision = RelevanceDecision.MANUAL_REVIEW
            
            # Create relevant content object
            relevant_content = RelevantContent(
                id=content.get("id", "unknown"),
                original_content=content,
                relevance_scores=relevance_scores,
                processing_decision=processing_decision,
                kiq_alignments=kiq_alignments,
                kit_classifications=kit_classifications,
                strategic_value=strategic_values,
                immediate_actionability=strategic_values.get("immediate_actionability", 0.0),
                future_monitoring_value=strategic_values.get("future_monitoring_value", 0.0),
                intelligence_completeness=strategic_values.get("intelligence_completeness", 0.0)
            )
            
            return relevant_content
            
        except Exception as e:
            logger.error(f"Single item assessment failed: {str(e)}")
            raise
    
    def _categorize_results(self, request: RelevanceRequest, relevant_items: List[RelevantContent], start_time: datetime) -> RelevanceResponse:
        """Categorize results into included/excluded/review"""
        included_content = []
        excluded_content = []
        manual_review_content = []
        
        for item in relevant_items:
            if item.processing_decision == RelevanceDecision.INCLUDE:
                included_content.append(item)
            elif item.processing_decision == RelevanceDecision.EXCLUDE:
                excluded_content.append(item)
            else:
                manual_review_content.append(item)
        
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        response = RelevanceResponse(
            request_id=request.request_id,
            total_input_items=len(request.content_items),
            included_content=included_content,
            excluded_content=excluded_content,
            manual_review_content=manual_review_content,
            processing_time=processing_time,
            kiqs_evaluated=len(request.kiqs),
            kits_used=len(request.kits)
        )
        
        # Calculate summary statistics
        response.calculate_summary_stats()
        
        return response
    
    async def _store_results(self, response: RelevanceResponse):
        """Store relevance assessment results"""
        try:
            # Store complete response
            storage_key = f"relevance_results/{response.request_id}.json"
            await self.storage_client.save_json(storage_key, response.dict())
            
            # Store included content separately for easy access
            included_key = f"relevance_included/{response.request_id}.json"
            included_data = [item.dict() for item in response.included_content]
            await self.storage_client.save_json(included_key, included_data)
            
            # Store metadata in database
            await self.database_client.save_item("relevance_assessments", {
                "request_id": response.request_id,
                "total_input_items": response.total_input_items,
                "included_count": len(response.included_content),
                "excluded_count": len(response.excluded_content),
                "manual_review_count": len(response.manual_review_content),
                "inclusion_rate": response.inclusion_rate,
                "average_relevance_score": response.average_relevance_score,
                "processing_time": response.processing_time,
                "storage_key": storage_key,
                "included_key": included_key,
                "created_at": response.created_at.isoformat()
            })
            
            logger.info(f"Stored relevance results: {storage_key}")
            
        except Exception as e:
            logger.error(f"Failed to store relevance results: {str(e)}")
```

## storage.py
```python
from typing import Dict, Any, List, Optional
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class RelevanceStorage:
    """Handle relevance-specific storage operations"""
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def save_relevance_results(self, request_id: str, results: Dict[str, Any]) -> bool:
        """Save complete relevance assessment results"""
        try:
            key = f"relevance_results/{request_id}.json"
            success = await self.storage_client.save_json(key, results)
            
            if success:
                logger.info(f"Saved relevance results: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Relevance results save error: {str(e)}")
            return False
    
    async def save_filtered_content(self, request_id: str, included_content: List[Dict[str, Any]]) -> bool:
        """Save filtered relevant content"""
        try:
            key = f"relevance_included/{request_id}.json"
            success = await self.storage_client.save_json(key, included_content)
            
            if success:
                logger.info(f"Saved filtered content: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Filtered content save error: {str(e)}")
            return False
```

## database.py
```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class RelevanceDatabase:
    """Handle relevance database operations"""
    
    def __init__(self):
        self.db_client = ServiceFactory.get_database_client()
        self.table_name = "relevance_assessments"
    
    async def save_relevance_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save relevance assessment metadata"""
        try:
            if 'created_at' not in metadata:
                metadata['created_at'] = datetime.utcnow().isoformat()
            
            success = await self.db_client.save_item(self.table_name, metadata)
            
            if success:
                logger.info(f"Saved relevance metadata: {metadata.get('request_id')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Relevance metadata save error: {str(e)}")
            return False
    
    async def get_relevance_stats(self, request_id: str) -> Dict[str, Any]:
        """Get relevance assessment statistics"""
        try:
            metadata = await self.db_client.get_item(self.table_name, {"request_id": request_id})
            
            if not metadata:
                return {}
            
            return {
                "request_id": request_id,
                "total_input_items": metadata.get("total_input_items", 0),
                "included_count": metadata.get("included_count", 0),
                "excluded_count": metadata.get("excluded_count", 0),
                "manual_review_count": metadata.get("manual_review_count", 0),
                "inclusion_rate": metadata.get("inclusion_rate", 0.0),
                "average_relevance_score": metadata.get("average_relevance_score", 0.0),
                "processing_time": metadata.get("processing_time", 0.0),
                "created_at": metadata.get("created_at")
            }
            
        except Exception as e:
            logger.error(f"Relevance stats error: {str(e)}")
            return {}
```