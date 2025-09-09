# Agent 3 Insights Implementation

## 10-Line Prompt:
Create strategic insights generation agent that processes relevance-filtered content from Agent 2 to extract KIQ-focused insights and strategic intelligence, includes sophisticated RAG retrieval system that queries knowledge base with relevance filters and semantic search capabilities, real OpenAI/Bedrock API integration for generating insights that directly address Key Intelligence Questions with evidence-based analysis, mock implementations that simulate realistic insight generation patterns and strategic analysis for testing, insight categorization system organizing findings into risk factors, trend analysis, opportunities, and knowledge gaps, cross-KIT pattern recognition that identifies trends spanning multiple intelligence topics and strategic themes, gap analysis engine that highlights missing information preventing complete KIQ answers, service orchestration managing the complete insights generation pipeline from retrieval to synthesis, storage operations saving generated insights with KIQ mappings and evidence tracking, and database operations maintaining insight metadata and strategic intelligence relationships in knowledge base structure.

## What it covers: 
Strategic insight extraction, KIQ-focused analysis, RAG retrieval, pattern recognition
## Methods: 
Knowledge base querying, insight synthesis, gap analysis, evidence correlation
## Why: 
Transform filtered content into actionable intelligence, strategic decision support

---

## models.py
```python
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class InsightCategory(str, Enum):
    RISK_FACTOR = "risk_factor"
    TREND_ANALYSIS = "trend_analysis"
    OPPORTUNITY = "opportunity"
    KNOWLEDGE_GAP = "knowledge_gap"
    COMPETITIVE_INTELLIGENCE = "competitive_intelligence"
    REGULATORY_UPDATE = "regulatory_update"
    MARKET_SHIFT = "market_shift"
    TECHNOLOGY_ADVANCEMENT = "technology_advancement"

class InsightConfidence(str, Enum):
    HIGH = "high"          # 0.8-1.0
    MEDIUM = "medium"      # 0.6-0.8
    LOW = "low"            # 0.4-0.6
    SPECULATIVE = "speculative"  # 0.0-0.4

class KIQInsight(BaseModel):
    """Insight specifically addressing a Key Intelligence Question"""
    kiq_id: str = Field(..., description="Associated KIQ identifier")
    insight: str = Field(..., description="Strategic insight content")
    category: InsightCategory = Field(..., description="Insight category")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Insight confidence score")
    completeness: float = Field(..., ge=0.0, le=1.0, description="How completely this addresses the KIQ")
    
    # Evidence and sources
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence points")
    source_content_ids: List[str] = Field(default_factory=list, description="Source content IDs")
    citation_count: int = Field(default=0, description="Number of supporting citations")
    
    # Gap analysis
    information_gaps: List[str] = Field(default_factory=list, description="Missing information")
    follow_up_questions: List[str] = Field(default_factory=list, description="Additional questions raised")
    
    # Metadata
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_confidence_level(self) -> InsightConfidence:
        """Get confidence level enum"""
        if self.confidence >= 0.8:
            return InsightConfidence.HIGH
        elif self.confidence >= 0.6:
            return InsightConfidence.MEDIUM
        elif self.confidence >= 0.4:
            return InsightConfidence.LOW
        else:
            return InsightConfidence.SPECULATIVE

class KITInsight(BaseModel):
    """Insights organized by Critical Intelligence Topic"""
    kit_id: str = Field(..., description="Associated KIT identifier")
    insights: List[str] = Field(..., description="Key insights for this KIT")
    strategic_implications: str = Field(..., description="Strategic implications for this KIT area")
    monitoring_recommendations: List[str] = Field(default_factory=list, description="What to monitor going forward")
    
    # Priority and urgency
    priority_level: str = Field(default="medium", description="Priority level for action")
    urgency_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Urgency for attention")
    
    # Trend analysis
    trend_direction: str = Field(default="stable", description="increasing|decreasing|stable|volatile")
    trend_confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Confidence in trend assessment")
    
    # Related content
    supporting_content_count: int = Field(default=0, description="Number of supporting content items")
    content_quality_average: float = Field(default=0.0, description="Average quality of supporting content")

class CrossKITPattern(BaseModel):
    """Pattern spanning multiple KIT areas"""
    pattern_id: str = Field(..., description="Pattern identifier")
    pattern_description: str = Field(..., description="Description of the cross-KIT pattern")
    affected_kits: List[str] = Field(..., description="KITs affected by this pattern")
    pattern_strength: float = Field(..., ge=0.0, le=1.0, description="Strength of the pattern")
    
    # Strategic significance
    strategic_significance: str = Field(..., description="Why this pattern matters strategically")
    business_impact: str = Field(default="medium", description="low|medium|high")
    
    # Temporal aspects
    emergence_timeframe: str = Field(default="unknown", description="When pattern emerged")
    projected_duration: str = Field(default="unknown", description="Expected duration")
    
    # Evidence
    supporting_evidence: List[str] = Field(default_factory=list)
    correlation_strength: float = Field(default=0.0, ge=0.0, le=1.0)

class InsightSynthesis(BaseModel):
    """Synthesized insights across all analysis"""
    executive_summary: str = Field(..., description="High-level synthesis for executives")
    key_findings: List[str] = Field(..., description="Primary findings")
    strategic_recommendations: List[str] = Field(..., description="Strategic recommendations")
    immediate_actions: List[str] = Field(default_factory=list, description="Immediate action items")
    
    # Risk and opportunity balance
    risk_level: str = Field(default="medium", description="Overall risk assessment")
    opportunity_level: str = Field(default="medium", description="Overall opportunity assessment")
    
    # Confidence and completeness
    synthesis_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    information_completeness: float = Field(default=0.0, ge=0.0, le=1.0)

class InsightsRequest(BaseModel):
    """Request for insights generation"""
    request_id: str = Field(..., description="Request identifier")
    user_prompt: str = Field(..., description="User's focus for insights")
    
    # Content sources
    content_request_ids: List[str] = Field(default_factory=list, description="Request IDs to analyze")
    specific_content_ids: List[str] = Field(default_factory=list, description="Specific content IDs")
    
    # Analysis parameters
    focus_kiqs: List[str] = Field(default_factory=list, description="KIQs to focus on")
    focus_kits: List[str] = Field(default_factory=list, description="KITs to focus on")
    insight_categories: List[InsightCategory] = Field(default_factory=list, description="Categories to include")
    
    # Retrieval configuration
    max_content_items: int = Field(default=50, ge=1, le=200, description="Max content items to analyze")
    min_relevance_score: float = Field(default=0.65, ge=0.0, le=1.0, description="Min relevance score")
    include_cross_kit_analysis: bool = Field(default=True)
    
    # Output preferences
    include_synthesis: bool = Field(default=True)
    max_insights_per_kiq: int = Field(default=5, ge=1, le=10)
    confidence_threshold: float = Field(default=0.4, ge=0.0, le=1.0)

class InsightsResponse(BaseModel):
    """Response from insights generation"""
    request_id: str = Field(..., description="Request identifier")
    user_prompt: str = Field(..., description="Original user prompt")
    
    # Generated insights
    kiq_focused_insights: List[KIQInsight] = Field(default_factory=list, description="KIQ-focused insights")
    kit_insights: List[KITInsight] = Field(default_factory=list, description="KIT-organized insights")
    cross_kit_patterns: List[CrossKITPattern] = Field(default_factory=list, description="Cross-KIT patterns")
    synthesis: Optional[InsightSynthesis] = Field(default=None, description="Overall synthesis")
    
    # Content analysis summary
    content_analyzed: int = Field(default=0, description="Number of content items analyzed")
    kiqs_addressed: int = Field(default=0, description="Number of KIQs addressed")
    kits_covered: int = Field(default=0, description="Number of KITs covered")
    
    # Quality metrics
    average_insight_confidence: float = Field(default=0.0, description="Average confidence across insights")
    high_confidence_insights: int = Field(default=0, description="Number of high-confidence insights")
    knowledge_gaps_identified: int = Field(default=0, description="Number of knowledge gaps found")
    
    # Processing metadata
    processing_time: float = Field(default=0.0)
    retrieval_time: float = Field(default=0.0)
    analysis_time: float = Field(default=0.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def calculate_summary_stats(self):
        """Calculate summary statistics"""
        self.kiqs_addressed = len(set(insight.kiq_id for insight in self.kiq_focused_insights))
        self.kits_covered = len(set(insight.kit_id for insight in self.kit_insights))
        
        if self.kiq_focused_insights:
            confidences = [insight.confidence for insight in self.kiq_focused_insights]
            self.average_insight_confidence = sum(confidences) / len(confidences)
            self.high_confidence_insights = sum(1 for c in confidences if c >= 0.8)
        
        self.knowledge_gaps_identified = sum(len(insight.information_gaps) for insight in self.kiq_focused_insights)

class RAGRetrievalConfig(BaseModel):
    """Configuration for RAG retrieval"""
    number_of_results: int = Field(default=20, ge=1, le=100)
    search_type: str = Field(default="HYBRID", description="SEMANTIC|LEXICAL|HYBRID")
    
    # Vector search configuration
    vector_search_results: int = Field(default=30, ge=1, le=100)
    
    # Filtering
    min_relevance_score: float = Field(default=0.65, ge=0.0, le=1.0)
    request_ids: List[str] = Field(default_factory=list)
    kiq_ids: List[str] = Field(default_factory=list)
    kit_ids: List[str] = Field(default_factory=list)
    
    # Content quality filters
    min_extraction_confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    require_high_quality: bool = Field(default=False)

class RetrievedContent(BaseModel):
    """Content retrieved from knowledge base"""
    content_id: str = Field(..., description="Content identifier")
    title: str = Field(..., description="Content title")
    content: str = Field(..., description="Content text")
    summary: str = Field(default="", description="Content summary")
    
    # Relevance metadata
    relevance_score: float = Field(default=0.0, description="Relevance score")
    kiq_alignments: List[str] = Field(default_factory=list, description="Aligned KIQ IDs")
    kit_classifications: List[str] = Field(default_factory=list, description="KIT classifications")
    
    # Quality indicators
    extraction_confidence: float = Field(default=0.0, description="Content extraction confidence")
    source_authority: float = Field(default=0.0, description="Source authority score")
    
    # Metadata
    url: str = Field(default="", description="Source URL")
    domain: str = Field(default="", description="Source domain")
    published_date: Optional[datetime] = Field(default=None)
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)
```

## openai_api.py
```python
import asyncio
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from .models import KIQInsight, KITInsight, CrossKITPattern, InsightSynthesis, InsightCategory, RetrievedContent
from ...config.settings import settings
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIAPI:
    """OpenAI client for insights generation tasks"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def generate_kiq_insights(self, retrieved_content: List[RetrievedContent], kiq_context: Dict[str, Any], user_prompt: str) -> List[KIQInsight]:
        """Generate insights focused on specific KIQs"""
        try:
            content_text = self._prepare_content_for_analysis(retrieved_content)
            
            prompt = self._build_kiq_insights_prompt(content_text, kiq_context, user_prompt)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert strategic intelligence analyst generating KIQ-focused insights from filtered, high-relevance content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            insights = []
            
            for insight_data in result.get("kiq_focused_insights", []):
                insight = KIQInsight(
                    kiq_id=insight_data.get("kiq_id"),
                    insight=insight_data.get("insight"),
                    category=InsightCategory(insight_data.get("category", "trend_analysis")),
                    confidence=float(insight_data.get("confidence", 0.0)),
                    completeness=float(insight_data.get("completeness", 0.0)),
                    evidence=insight_data.get("evidence", []),
                    source_content_ids=self._extract_source_ids(retrieved_content, insight_data.get("insight", "")),
                    citation_count=len(insight_data.get("evidence", [])),
                    information_gaps=insight_data.get("information_gaps", []),
                    follow_up_questions=insight_data.get("follow_up_questions", [])
                )
                insights.append(insight)
            
            logger.info(f"Generated {len(insights)} KIQ-focused insights")
            return insights
            
        except Exception as e:
            logger.error(f"KIQ insights generation failed: {str(e)}")
            return []
    
    async def generate_kit_insights(self, retrieved_content: List[RetrievedContent], kit_context: Dict[str, Any], user_prompt: str) -> List[KITInsight]:
        """Generate insights organized by KIT areas"""
        try:
            content_text = self._prepare_content_for_analysis(retrieved_content)
            
            prompt = self._build_kit_insights_prompt(content_text, kit_context, user_prompt)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert in organizing strategic intelligence by topic areas and identifying implications."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            kit_insights = []
            
            for kit_data in result.get("kit_insights", []):
                supporting_content = [c for c in retrieved_content if kit_data.get("kit_id") in c.kit_classifications]
                
                kit_insight = KITInsight(
                    kit_id=kit_data.get("kit_id"),
                    insights=kit_data.get("insights", []),
                    strategic_implications=kit_data.get("strategic_implications", ""),
                    monitoring_recommendations=kit_data.get("monitoring_recommendations", []),
                    priority_level=kit_data.get("priority_level", "medium"),
                    urgency_score=float(kit_data.get("urgency_score", 0.5)),
                    trend_direction=kit_data.get("trend_direction", "stable"),
                    trend_confidence=float(kit_data.get("trend_confidence", 0.5)),
                    supporting_content_count=len(supporting_content),
                    content_quality_average=sum(c.extraction_confidence for c in supporting_content) / len(supporting_content) if supporting_content else 0.0
                )
                kit_insights.append(kit_insight)
            
            logger.info(f"Generated {len(kit_insights)} KIT insights")
            return kit_insights
            
        except Exception as e:
            logger.error(f"KIT insights generation failed: {str(e)}")
            return []
    
    async def identify_cross_kit_patterns(self, retrieved_content: List[RetrievedContent], kit_insights: List[KITInsight]) -> List[CrossKITPattern]:
        """Identify patterns spanning multiple KIT areas"""
        try:
            if len(kit_insights) < 2:
                return []
            
            content_summary = self._summarize_content_for_patterns(retrieved_content)
            kit_summary = self._summarize_kit_insights(kit_insights)
            
            prompt = self._build_cross_kit_pattern_prompt(content_summary, kit_summary)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying strategic patterns and connections across different intelligence topic areas."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            patterns = []
            
            for pattern_data in result.get("cross_kit_patterns", []):
                pattern = CrossKITPattern(
                    pattern_id=f"pattern_{int(datetime.utcnow().timestamp())}_{len(patterns)}",
                    pattern_description=pattern_data.get("pattern", ""),
                    affected_kits=pattern_data.get("affected_kits", []),
                    pattern_strength=float(pattern_data.get("pattern_strength", 0.0)),
                    strategic_significance=pattern_data.get("strategic_significance", ""),
                    business_impact=pattern_data.get("business_impact", "medium"),
                    emergence_timeframe=pattern_data.get("emergence_timeframe", "unknown"),
                    projected_duration=pattern_data.get("projected_duration", "unknown"),
                    supporting_evidence=pattern_data.get("supporting_evidence", []),
                    correlation_strength=float(pattern_data.get("correlation_strength", 0.0))
                )
                patterns.append(pattern)
            
            logger.info(f"Identified {len(patterns)} cross-KIT patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Cross-KIT pattern identification failed: {str(e)}")
            return []
    
    async def synthesize_insights(self, kiq_insights: List[KIQInsight], kit_insights: List[KITInsight], cross_kit_patterns: List[CrossKITPattern], user_prompt: str) -> InsightSynthesis:
        """Create executive synthesis of all insights"""
        try:
            synthesis_input = self._prepare_synthesis_input(kiq_insights, kit_insights, cross_kit_patterns)
            
            prompt = self._build_synthesis_prompt(synthesis_input, user_prompt)
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior strategic advisor creating executive-level synthesis of intelligence insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            synthesis = InsightSynthesis(
                executive_summary=result.get("executive_summary", ""),
                key_findings=result.get("key_findings", []),
                strategic_recommendations=result.get("strategic_recommendations", []),
                immediate_actions=result.get("immediate_actions", []),
                risk_level=result.get("risk_level", "medium"),
                opportunity_level=result.get("opportunity_level", "medium"),
                synthesis_confidence=float(result.get("synthesis_confidence", 0.0)),
                information_completeness=float(result.get("information_completeness", 0.0))
            )
            
            logger.info("Generated executive synthesis")
            return synthesis
            
        except Exception as e:
            logger.error(f"Synthesis generation failed: {str(e)}")
            return InsightSynthesis(
                executive_summary="Synthesis generation failed",
                key_findings=[],
                strategic_recommendations=[]
            )
    
    def _prepare_content_for_analysis(self, content: List[RetrievedContent]) -> str:
        """Prepare retrieved content for analysis"""
        content_parts = []
        
        for i, item in enumerate(content[:20]):  # Limit to prevent token overflow
            content_part = f"""
Content {i+1}:
Title: {item.title}
Source: {item.domain}
Relevance Score: {item.relevance_score:.2f}
Content: {item.content[:800]}...
KIQ Alignments: {', '.join(item.kiq_alignments)}
KIT Classifications: {', '.join(item.kit_classifications)}
---
"""
            content_parts.append(content_part)
        
        return "\n".join(content_parts)
    
    def _build_kiq_insights_prompt(self, content: str, kiq_context: Dict[str, Any], user_prompt: str) -> str:
        """Build prompt for KIQ-focused insights"""
        return f"""
Analyze this strategically relevant, pre-filtered content for insights that directly address Key Intelligence Questions (KIQs).

KIQ Context: {json.dumps(kiq_context, indent=2)}

User Focus: {user_prompt}

Content to Analyze:
{content}

Generate insights in this JSON format:
{{
  "kiq_focused_insights": [
    {{
      "kiq_id": "KIQ-XXX",
      "insight": "specific insight addressing the KIQ with evidence",
      "category": "risk_factor|trend_analysis|opportunity|knowledge_gap|competitive_intelligence|regulatory_update|market_shift|technology_advancement",
      "confidence": 0.0-1.0,
      "completeness": 0.0-1.0,
      "evidence": ["specific evidence from content"],
      "information_gaps": ["what's still needed to fully answer KIQ"],
      "follow_up_questions": ["additional questions this insight raises"]
    }}
  ]
}}

Focus on:
1. Direct answers to KIQs with supporting evidence
2. Identifying patterns and trends
3. Highlighting risks and opportunities
4. Noting information gaps that prevent complete KIQ answers
5. Ensuring insights are actionable and strategic
"""
    
    def _build_kit_insights_prompt(self, content: str, kit_context: Dict[str, Any], user_prompt: str) -> str:
        """Build prompt for KIT-organized insights"""
        return f"""
Organize strategic insights by Critical Intelligence Topics (KITs) based on this content.

KIT Context: {json.dumps(kit_context, indent=2)}

User Focus: {user_prompt}

Content to Analyze:
{content}

Generate KIT-organized insights in JSON format:
{{
  "kit_insights": [
    {{
      "kit_id": "KIT-XXX",
      "insights": ["key insights specific to this KIT"],
      "strategic_implications": "how this affects the KIT area strategically",
      "monitoring_recommendations": ["what to watch going forward"],
      "priority_level": "low|medium|high|critical",
      "urgency_score": 0.0-1.0,
      "trend_direction": "increasing|decreasing|stable|volatile",
      "trend_confidence": 0.0-1.0
    }}
  ]
}}

For each KIT:
1. Extract insights relevant to that intelligence topic
2. Assess strategic implications for that area
3. Recommend monitoring activities
4. Evaluate priority and urgency
5. Identify trend directions with confidence levels
"""
    
    def _build_cross_kit_pattern_prompt(self, content_summary: str, kit_summary: str) -> str:
        """Build prompt for cross-KIT pattern identification"""
        return f"""
Identify strategic patterns that span multiple Critical Intelligence Topics (KITs).

Content Summary:
{content_summary}

KIT Insights Summary:
{kit_summary}

Look for patterns that connect multiple KITs and provide strategic insights in JSON format:
{{
  "cross_kit_patterns": [
    {{
      "pattern": "description of pattern spanning multiple KITs",
      "affected_kits": ["KIT-001", "KIT-002"],
      "pattern_strength": 0.0-1.0,
      "strategic_significance": "why this pattern matters strategically",
      "business_impact": "low|medium|high",
      "emergence_timeframe": "when this pattern emerged",
      "projected_duration": "expected duration of pattern",
      "supporting_evidence": ["evidence supporting this pattern"],
      "correlation_strength": 0.0-1.0
    }}
  ]
}}

Focus on:
1. Patterns that affect multiple KIT areas
2. Emerging trends connecting different topics
3. Correlations between different intelligence areas
4. Strategic implications of these connections
"""
    
    def _build_synthesis_prompt(self, synthesis_input: str, user_prompt: str) -> str:
        """Build prompt for executive synthesis"""
        return f"""
Create an executive-level synthesis of strategic intelligence insights.

User Focus: {user_prompt}

All Insights and Patterns:
{synthesis_input}

Provide executive synthesis in JSON format:
{{
  "executive_summary": "concise executive summary for leadership",
  "key_findings": ["3-5 most important findings"],
  "strategic_recommendations": ["specific strategic recommendations"],
  "immediate_actions": ["actions that should be taken immediately"],
  "risk_level": "low|medium|high|critical",
  "opportunity_level": "low|medium|high|exceptional",
  "synthesis_confidence": 0.0-1.0,
  "information_completeness": 0.0-1.0
}}

Requirements:
1. Focus on strategic implications for decision-making
2. Highlight most critical insights requiring action
3. Balance risks and opportunities
4. Provide clear, actionable recommendations
5. Assess overall confidence and information completeness
"""
    
    def _extract_source_ids(self, content: List[RetrievedContent], insight_text: str) -> List[str]:
        """Extract source content IDs that likely contributed to insight"""
        # Simple implementation - could be enhanced with more sophisticated matching
        source_ids = []
        
        insight_words = set(insight_text.lower().split())
        
        for item in content:
            item_words = set((item.title + " " + item.content).lower().split())
            overlap = len(insight_words & item_words)
            
            if overlap > 5:  # Threshold for likely contribution
                source_ids.append(item.content_id)
        
        return source_ids[:5]  # Limit to top 5 sources
    
    def _summarize_content_for_patterns(self, content: List[RetrievedContent]) -> str:
        """Create summary of content for pattern analysis"""
        summaries = []
        
        for item in content[:10]:  # Limit for token management
            summary = f"- {item.title} (KITs: {', '.join(item.kit_classifications)}): {item.summary[:200]}..."
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def _summarize_kit_insights(self, kit_insights: List[KITInsight]) -> str:
        """Create summary of KIT insights"""
        summaries = []
        
        for insight in kit_insights:
            summary = f"KIT {insight.kit_id}: {insight.strategic_implications[:200]}..."
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def _prepare_synthesis_input(self, kiq_insights: List[KIQInsight], kit_insights: List[KITInsight], patterns: List[CrossKITPattern]) -> str:
        """Prepare all insights for synthesis"""
        sections = []
        
        # KIQ insights
        if kiq_insights:
            kiq_section = "KIQ Insights:\n"
            for insight in kiq_insights[:10]:
                kiq_section += f"- {insight.kiq_id}: {insight.insight[:200]}...\n"
            sections.append(kiq_section)
        
        # KIT insights
        if kit_insights:
            kit_section = "KIT Insights:\n"
            for insight in kit_insights:
                kit_section += f"- {insight.kit_id}: {insight.strategic_implications[:200]}...\n"
            sections.append(kit_section)
        
        # Cross-KIT patterns
        if patterns:
            pattern_section = "Cross-KIT Patterns:\n"
            for pattern in patterns:
                pattern_section += f"- {pattern.pattern_description[:200]}...\n"
            sections.append(pattern_section)
        
        return "\n\n".join(sections)
```

## openai_mock.py
```python
import asyncio
import random
from typing import List, Dict, Any
from datetime import datetime
from .models import KIQInsight, KITInsight, CrossKITPattern, InsightSynthesis, InsightCategory, RetrievedContent
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class OpenAIMock:
    """Mock OpenAI client for testing insights generation"""
    
    def __init__(self):
        random.seed(42)  # For reproducible results
        self.mock_insights = self._generate_mock_insights()
    
    async def generate_kiq_insights(self, retrieved_content: List[RetrievedContent], kiq_context: Dict[str, Any], user_prompt: str) -> List[KIQInsight]:
        """Generate mock KIQ-focused insights"""
        await asyncio.sleep(0.3)  # Simulate API latency
        
        logger.info(f"Mock generating KIQ insights from {len(retrieved_content)} content items")
        
        insights = []
        kiq_ids = list(kiq_context.keys()) if kiq_context else ["KIQ-001", "KIQ-002", "KIQ-003"]
        
        for i, kiq_id in enumerate(kiq_ids[:5]):  # Limit to 5 KIQs
            insight_category = self._select_insight_category(user_prompt, i)
            
            insight = KIQInsight(
                kiq_id=kiq_id,
                insight=self._generate_mock_insight_text(kiq_id, insight_category, retrieved_content),
                category=insight_category,
                confidence=random.uniform(0.6, 0.9),
                completeness=random.uniform(0.5, 0.8),
                evidence=self._generate_mock_evidence(retrieved_content, insight_category),
                source_content_ids=self._select_source_content_ids(retrieved_content),
                citation_count=random.randint(2, 6),
                information_gaps=self._generate_mock_gaps(kiq_id),
                follow_up_questions=self._generate_mock_follow_up_questions(kiq_id)
            )
            insights.append(insight)
        
        logger.info(f"Generated {len(insights)} mock KIQ insights")
        return insights
    
    async def generate_kit_insights(self, retrieved_content: List[RetrievedContent], kit_context: Dict[str, Any], user_prompt: str) -> List[KITInsight]:
        """Generate mock KIT-organized insights"""
        await asyncio.sleep(0.2)
        
        logger.info(f"Mock generating KIT insights from {len(retrieved_content)} content items")
        
        kit_insights = []
        kit_ids = list(kit_context.keys()) if kit_context else ["KIT-001", "KIT-002", "KIT-003", "KIT-004"]
        
        for kit_id in kit_ids[:4]:  # Limit to 4 KITs
            supporting_content = [c for c in retrieved_content if kit_id in c.kit_classifications]
            
            kit_insight = KITInsight(
                kit_id=kit_id,
                insights=self._generate_kit_specific_insights(kit_id),
                strategic_implications=self._generate_strategic_implications(kit_id),
                monitoring_recommendations=self._generate_monitoring_recommendations(kit_id),
                priority_level=random.choice(["medium", "high", "critical"]),
                urgency_score=random.uniform(0.4, 0.9),
                trend_direction=random.choice(["increasing", "stable", "volatile"]),
                trend_confidence=random.uniform(0.6, 0.9),
                supporting_content_count=len(supporting_content) if supporting_content else random.randint(3, 8),
                content_quality_average=random.uniform(0.7, 0.9)
            )
            kit_insights.append(kit_insight)
        
        logger.info(f"Generated {len(kit_insights)} mock KIT insights")
        return kit_insights
    
    async def identify_cross_kit_patterns(self, retrieved_content: List[RetrievedContent], kit_insights: List[KITInsight]) -> List[CrossKITPattern]:
        """Generate mock cross-KIT patterns"""
        await asyncio.sleep(0.2)
        
        if len(kit_insights) < 2:
            return []
        
        logger.info(f"Mock identifying cross-KIT patterns from {len(kit_insights)} KIT insights")
        
        patterns = []
        
        # Generate 2-3 patterns
        for i in range(random.randint(2, 3)):
            affected_kits = random.sample([insight.kit_id for insight in kit_insights], 
                                        min(random.randint(2, 3), len(kit_insights)))
            
            pattern = CrossKITPattern(
                pattern_id=f"mock_pattern_{i+1}",
                pattern_description=self._generate_pattern_description(affected_kits),
                affected_kits=affected_kits,
                pattern_strength=random.uniform(0.6, 0.9),
                strategic_significance=self._generate_pattern_significance(affected_kits),
                business_impact=random.choice(["medium", "high"]),
                emergence_timeframe="recent months",
                projected_duration="6-12 months",
                supporting_evidence=self._generate_pattern_evidence(affected_kits),
                correlation_strength=random.uniform(0.7, 0.9)
            )
            patterns.append(pattern)
        
        logger.info(f"Generated {len(patterns)} mock cross-KIT patterns")
        return patterns
    
    async def synthesize_insights(self, kiq_insights: List[KIQInsight], kit_insights: List[KITInsight], cross_kit_patterns: List[CrossKITPattern], user_prompt: str) -> InsightSynthesis:
        """Generate mock executive synthesis"""
        await asyncio.sleep(0.2)
        
        logger.info("Mock generating executive synthesis")
        
        synthesis = InsightSynthesis(
            executive_summary=self._generate_executive_summary(user_prompt, len(kiq_insights), len(kit_insights)),
            key_findings=self._generate_key_findings(kiq_insights, kit_insights),
            strategic_recommendations=self._generate_strategic_recommendations(kit_insights),
            immediate_actions=self._generate_immediate_actions(kiq_insights),
            risk_level=random.choice(["medium", "high"]),
            opportunity_level=random.choice(["medium", "high"]),
            synthesis_confidence=random.uniform(0.7, 0.9),
            information_completeness=random.uniform(0.6, 0.8)
        )
        
        return synthesis
    
    def _generate_mock_insights(self) -> Dict[str, Dict[str, str]]:
        """Generate mock insight templates"""
        return {
            "risk_factor": {
                "regulatory": "New regulatory requirements may impact compliance timelines and increase operational costs",
                "competitive": "Increased competitive pressure from new market entrants with innovative approaches",
                "technology": "Emerging technology disruptions pose risks to current business models"
            },
            "trend_analysis": {
                "market": "Market trends indicate accelerating adoption of AI-powered solutions across the industry",
                "regulatory": "Regulatory frameworks are evolving to accommodate new technologies while maintaining safety standards",
                "competitive": "Competitive landscape shows consolidation trends and strategic partnerships"
            },
            "opportunity": {
                "innovation": "Innovation opportunities exist in emerging technology applications for strategic advantage",
                "market": "Market expansion opportunities identified in underserved segments",
                "partnership": "Strategic partnership opportunities could accelerate market penetration"
            }
        }
    
    def _select_insight_category(self, user_prompt: str, index: int) -> InsightCategory:
        """Select appropriate insight category"""
        prompt_lower = user_prompt.lower()
        
        if "risk" in prompt_lower:
            return InsightCategory.RISK_FACTOR
        elif "trend" in prompt_lower:
            return InsightCategory.TREND_ANALYSIS
        elif "opportunity" in prompt_lower:
            return InsightCategory.OPPORTUNITY
        elif "regulation" in prompt_lower:
            return InsightCategory.REGULATORY_UPDATE
        elif "competitive" in prompt_lower:
            return InsightCategory.COMPETITIVE_INTELLIGENCE
        else:
            categories = [InsightCategory.TREND_ANALYSIS, InsightCategory.OPPORTUNITY, InsightCategory.RISK_FACTOR]
            return categories[index % len(categories)]
    
    def _generate_mock_insight_text(self, kiq_id: str, category: InsightCategory, content: List[RetrievedContent]) -> str:
        """Generate mock insight text"""
        content_themes = self._extract_content_themes(content)
        
        base_insights = {
            InsightCategory.RISK_FACTOR: f"Analysis reveals potential risks in {content_themes} that could impact strategic objectives and require mitigation strategies.",
            InsightCategory.TREND_ANALYSIS: f"Emerging trends in {content_themes} indicate significant shifts in market dynamics and competitive landscape.",
            InsightCategory.OPPORTUNITY: f"Strategic opportunities identified in {content_themes} present potential for competitive advantage and market expansion.",
            InsightCategory.REGULATORY_UPDATE: f"Regulatory developments in {content_themes} require attention and may necessitate compliance adjustments.",
            InsightCategory.COMPETITIVE_INTELLIGENCE: f"Competitive intelligence indicates changes in {content_themes} affecting market positioning."
        }
        
        return base_insights.get(category, f"Strategic insight regarding {content_themes} with implications for {kiq_id}.")
    
    def _extract_content_themes(self, content: List[RetrievedContent]) -> str:
        """Extract themes from content for insight generation"""
        if not content:
            return "industry developments"
        
        # Simple theme extraction based on titles
        common_words = []
        for item in content[:5]:
            words = item.title.lower().split()
            common_words.extend([w for w in words if len(w) > 4])
        
        # Get most common words
        word_counts = {}
        for word in common_words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if top_words:
            return ", ".join([word for word, count in top_words])
        else:
            return "industry developments"
    
    def _generate_mock_evidence(self, content: List[RetrievedContent], category: InsightCategory) -> List[str]:
        """Generate mock evidence list"""
        evidence_templates = {
            InsightCategory.RISK_FACTOR: [
                "Multiple sources indicate potential regulatory challenges",
                "Industry reports highlight emerging competitive threats",
                "Expert analysis suggests market volatility risks"
            ],
            InsightCategory.TREND_ANALYSIS: [
                "Data shows consistent growth patterns across market segments",
                "Industry surveys reveal changing customer preferences",
                "Technical reports indicate accelerating technology adoption"
            ],
            InsightCategory.OPPORTUNITY: [
                "Market research identifies underserved customer segments",
                "Technology developments create new product possibilities",
                "Regulatory changes open new market opportunities"
            ]
        }
        
        base_evidence = evidence_templates.get(category, ["Supporting evidence from multiple sources"])
        
        # Add content-specific evidence
        if content:
            content_evidence = f"Analysis of {len(content)} relevant sources supports this finding"
            base_evidence.append(content_evidence)
        
        return base_evidence[:4]
    
    def _select_source_content_ids(self, content: List[RetrievedContent]) -> List[str]:
        """Select mock source content IDs"""
        return [item.content_id for item in random.sample(content, min(3, len(content)))]
    
    def _generate_mock_gaps(self, kiq_id: str) -> List[str]:
        """Generate mock information gaps"""
        gap_templates = [
            "Quantitative data needed to validate trend magnitude",
            "Geographic scope requires expansion for complete analysis",
            "Timeline information missing for strategic planning",
            "Competitive response data not yet available"
        ]
        
        return random.sample(gap_templates, random.randint(1, 3))
    
    def _generate_mock_follow_up_questions(self, kiq_id: str) -> List[str]:
        """Generate mock follow-up questions"""
        question_templates = [
            "What are the specific implementation timelines?",
            "How will this impact existing strategic initiatives?",
            "What resources will be required for response?",
            "Are there regional variations to consider?"
        ]
        
        return random.sample(question_templates, random.randint(1, 2))
    
    def _generate_kit_specific_insights(self, kit_id: str) -> List[str]:
        """Generate insights specific to a KIT"""
        kit_insights = {
            "KIT-001": [
                "Competitive pipeline analysis reveals accelerated development timelines",
                "New market entrants are focusing on innovative delivery mechanisms",
                "Strategic partnerships are becoming critical for market access"
            ],
            "KIT-002": [
                "Regulatory guidance updates require immediate compliance review",
                "New safety standards impact development protocols",
                "International regulatory harmonization creates opportunities"
            ],
            "KIT-003": [
                "Market access challenges increasing in key territories",
                "Payer pressure on pricing continues to intensify",
                "Value-based contracts gaining acceptance among stakeholders"
            ],
            "KIT-004": [
                "AI and digital health innovations accelerating across industry",
                "Technology partnerships becoming strategic differentiators",
                "Data analytics capabilities essential for competitive advantage"
            ]
        }
        
        return kit_insights.get(kit_id, ["Strategic developments relevant to this intelligence topic"])
    
    def _generate_strategic_implications(self, kit_id: str) -> str:
        """Generate strategic implications for KIT"""
        implications = {
            "KIT-001": "Competitive intelligence indicates need for accelerated innovation cycles and strategic partnership evaluation to maintain market position.",
            "KIT-002": "Regulatory environment changes require immediate compliance assessment and may impact development timelines and resource allocation.",
            "KIT-003": "Market access challenges necessitate enhanced stakeholder engagement and alternative pricing strategies for sustainable growth.",
            "KIT-004": "Technology innovation trends suggest investment in digital capabilities and data analytics is critical for future competitiveness."
        }
        
        return implications.get(kit_id, "Strategic implications require further analysis and stakeholder consultation.")
    
    def _generate_monitoring_recommendations(self, kit_id: str) -> List[str]:
        """Generate monitoring recommendations for KIT"""
        recommendations = {
            "KIT-001": [
                "Monitor competitive clinical trial databases weekly",
                "Track partnership announcements and strategic alliances",
                "Analyze competitor financial reports for R&D investments"
            ],
            "KIT-002": [
                "Monitor regulatory agency websites for guidance updates",
                "Track policy consultations and industry feedback",
                "Analyze regulatory approval timelines and trends"
            ],
            "KIT-003": [
                "Monitor payer policy changes and formulary updates",
                "Track health technology assessment outcomes",
                "Analyze market access trends across key territories"
            ],
            "KIT-004": [
                "Monitor technology patent filings and innovations",
                "Track digital health partnership announcements",
                "Analyze AI and data analytics investment trends"
            ]
        }
        
        return recommendations.get(kit_id, ["Continue monitoring relevant industry developments"])
    
    def _generate_pattern_description(self, affected_kits: List[str]) -> str:
        """Generate description for cross-KIT pattern"""
        kit_themes = {
            "KIT-001": "competitive dynamics",
            "KIT-002": "regulatory environment",
            "KIT-003": "market access",
            "KIT-004": "technology innovation"
        }
        
        themes = [kit_themes.get(kit_id, "intelligence area") for kit_id in affected_kits]
        
        return f"Strategic pattern connecting {' and '.join(themes)} indicating coordinated industry transformation with implications for multiple business areas."
    
    def _generate_pattern_significance(self, affected_kits: List[str]) -> str:
        """Generate strategic significance for pattern"""
        return f"This pattern affects {len(affected_kits)} critical intelligence areas simultaneously, suggesting systematic industry changes requiring coordinated strategic response and cross-functional collaboration."
    
    def _generate_pattern_evidence(self, affected_kits: List[str]) -> List[str]:
        """Generate evidence for cross-KIT pattern"""
        return [
            f"Correlated developments observed across {len(affected_kits)} intelligence topics",
            "Multiple independent sources report similar trends",
            "Timeline analysis shows synchronized emergence across areas",
            "Industry expert commentary confirms pattern significance"
        ]
    
    def _generate_executive_summary(self, user_prompt: str, kiq_count: int, kit_count: int) -> str:
        """Generate executive summary"""
        return f"Strategic intelligence analysis addressing {kiq_count} key questions across {kit_count} critical topics reveals significant developments requiring executive attention. Analysis focused on {user_prompt} indicates both opportunities and risks that demand immediate strategic consideration and coordinated response across multiple business functions."
    
    def _generate_key_findings(self, kiq_insights: List[KIQInsight], kit_insights: List[KITInsight]) -> List[str]:
        """Generate key findings"""
        findings = [
            "Strategic intelligence reveals accelerating industry transformation",
            "Multiple intelligence areas show coordinated development patterns",
            "Risk factors require immediate mitigation planning",
            "Opportunity landscape demands strategic investment decisions"
        ]
        
        if kiq_insights:
            high_confidence = [i for i in kiq_insights if i.confidence >= 0.8]
            if high_confidence:
                findings.append(f"High-confidence insights available for {len(high_confidence)} strategic questions")
        
        return findings[:4]
    
    def _generate_strategic_recommendations(self, kit_insights: List[KITInsight]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = [
            "Establish cross-functional response team for coordinated strategy execution",
            "Accelerate strategic planning cycles to address rapid industry changes",
            "Enhance intelligence gathering capabilities in critical areas",
            "Develop scenario planning for multiple strategic outcomes"
        ]
        
        high_priority_kits = [k for k in kit_insights if k.priority_level in ["high", "critical"]]
        if high_priority_kits:
            recommendations.append(f"Prioritize immediate action on {len(high_priority_kits)} critical intelligence areas")
        
        return recommendations[:4]
    
    def _generate_immediate_actions(self, kiq_insights: List[KIQInsight]) -> List[str]:
        """Generate immediate actions"""
        actions = [
            "Convene strategic leadership meeting within 48 hours",
            "Initiate enhanced monitoring of critical intelligence areas",
            "Prepare stakeholder briefings on key developments",
            "Review resource allocation for strategic response"
        ]
        
        risk_insights = [i for i in kiq_insights if i.category == InsightCategory.RISK_FACTOR]
        if risk_insights:
            actions.append("Activate risk management protocols for identified threats")
        
        return actions[:4]
```

## rag_retrieval.py
```python
import asyncio
from typing import List, Dict, Any, Optional
from .models import RAGRetrievalConfig, RetrievedContent
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class RAGRetrieval:
    """RAG retrieval system for knowledge base querying"""
    
    def __init__(self):
        self.database_client = ServiceFactory.get_database_client()
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def retrieve_relevant_content(self, query: str, config: RAGRetrievalConfig) -> List[RetrievedContent]:
        """Retrieve relevant content from knowledge base"""
        try:
            logger.info(f"Retrieving content for query: {query[:100]}...")
            
            # Stage 1: Vector similarity search
            vector_results = await self._vector_search(query, config)
            
            # Stage 2: Apply filters
            filtered_results = self._apply_filters(vector_results, config)
            
            # Stage 3: Enhance with metadata
            enhanced_results = await self._enhance_with_metadata(filtered_results)
            
            # Stage 4: Rank and limit results
            final_results = self._rank_and_limit_results(enhanced_results, config)
            
            logger.info(f"Retrieved {len(final_results)} relevant content items")
            return final_results
            
        except Exception as e:
            logger.error(f"Content retrieval failed: {str(e)}")
            return []
    
    async def retrieve_by_filters(self, config: RAGRetrievalConfig) -> List[RetrievedContent]:
        """Retrieve content based on filters without semantic search"""
        try:
            logger.info("Retrieving content by filters")
            
            # Build filter query
            filter_query = self._build_filter_query(config)
            
            # Query knowledge base
            results = await self.database_client.query_items(
                "knowledge_base",
                **filter_query
            )
            
            # Convert to RetrievedContent objects
            retrieved_content = []
            for result in results:
                content = await self._convert_to_retrieved_content(result)
                if content:
                    retrieved_content.append(content)
            
            # Rank and limit
            final_results = self._rank_and_limit_results(retrieved_content, config)
            
            logger.info(f"Retrieved {len(final_results)} filtered content items")
            return final_results
            
        except Exception as e:
            logger.error(f"Filter-based retrieval failed: {str(e)}")
            return []
    
    async def _vector_search(self, query: str, config: RAGRetrievalConfig) -> List[Dict[str, Any]]:
        """Perform vector similarity search"""
        try:
            # Mock implementation - in production, this would use a vector database
            # like Amazon OpenSearch, Pinecone, or similar
            
            # For now, simulate vector search results
            mock_results = await self._mock_vector_search(query, config)
            
            return mock_results
            
        except Exception as e:
            logger.error(f"Vector search failed: {str(e)}")
            return []
    
    async def _mock_vector_search(self, query: str, config: RAGRetrievalConfig) -> List[Dict[str, Any]]:
        """Mock vector search implementation"""
        # This would be replaced with actual vector database integration
        
        # Query knowledge base for all relevant content
        all_content = await self.database_client.query_items("knowledge_base")
        
        # Simple text-based relevance scoring
        scored_results = []
        query_words = set(query.lower().split())
        
        for item in all_content:
            title = item.get("title", "").lower()
            content = item.get("content", "").lower()
            
            title_words = set(title.split())
            content_words = set(content.split())
            
            # Calculate simple relevance score
            title_overlap = len(query_words & title_words)
            content_overlap = len(query_words & content_words)
            
            relevance_score = (title_overlap * 2 + content_overlap) / len(query_words)
            
            if relevance_score > 0:
                item["relevance_score"] = min(relevance_score, 1.0)
                scored_results.append(item)
        
        # Sort by relevance score
        scored_results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        
        return scored_results[:config.vector_search_results]
    
    def _apply_filters(self, results: List[Dict[str, Any]], config: RAGRetrievalConfig) -> List[Dict[str, Any]]:
        """Apply relevance and metadata filters"""
        filtered = []
        
        for result in results:
            # Relevance score filter
            relevance_score = result.get("relevance_score", 0.0)
            if relevance_score < config.min_relevance_score:
                continue
            
            # Request ID filter
            if config.request_ids:
                request_id = result.get("request_id", "")
                if request_id not in config.request_ids:
                    continue
            
            # KIQ filter
            if config.kiq_ids:
                kiq_alignments = result.get("kiq_alignments", [])
                if not any(kiq_id in str(kiq_alignments) for kiq_id in config.kiq_ids):
                    continue
            
            # KIT filter
            if config.kit_ids:
                kit_classifications = result.get("kit_classifications", [])
                if not any(kit_id in str(kit_classifications) for kit_id in config.kit_ids):
                    continue
            
            # Extraction confidence filter
            extraction_confidence = result.get("extraction_confidence", 0.0)
            if extraction_confidence < config.min_extraction_confidence:
                continue
            
            # High quality filter
            if config.require_high_quality:
                quality_score = result.get("content_quality_score", 0.0)
                if quality_score < 0.7:
                    continue
            
            filtered.append(result)
        
        return filtered
    
    async def _enhance_with_metadata(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enhance results with additional metadata"""
        enhanced = []
        
        for result in results:
            try:
                # Load full content if needed
                if "full_content" not in result:
                    storage_key = result.get("storage_key")
                    if storage_key:
                        full_content = await self.storage_client.load_json(storage_key)
                        if full_content:
                            result.update(full_content)
                
                enhanced.append(result)
                
            except Exception as e:
                logger.warning(f"Failed to enhance result: {str(e)}")
                enhanced.append(result)  # Include anyway
        
        return enhanced
    
    def _rank_and_limit_results(self, results: List[RetrievedContent], config: RAGRetrievalConfig) -> List[RetrievedContent]:
        """Rank and limit results"""
        # Sort by relevance score
        sorted_results = sorted(results, key=lambda x: x.relevance_score, reverse=True)
        
        # Limit to requested number
        limited_results = sorted_results[:config.number_of_results]
        
        return limited_results
    
    def _build_filter_query(self, config: RAGRetrievalConfig) -> Dict[str, Any]:
        """Build DynamoDB filter query"""
        query_params = {}
        
        # Base query parameters
        query_params["Limit"] = config.number_of_results
        
        # Add filters
        filter_expressions = []
        expression_values = {}
        
        if config.min_relevance_score > 0:
            filter_expressions.append("relevance_score >= :min_relevance")
            expression_values[":min_relevance"] = config.min_relevance_score
        
        if config.request_ids:
            filter_expressions.append("request_id IN (:request_ids)")
            expression_values[":request_ids"] = config.request_ids
        
        if config.min_extraction_confidence > 0:
            filter_expressions.append("extraction_confidence >= :min_extraction")
            expression_values[":min_extraction"] = config.min_extraction_confidence
        
        if filter_expressions:
            query_params["FilterExpression"] = " AND ".join(filter_expressions)
            query_params["ExpressionAttributeValues"] = expression_values
        
        return query_params
    
    async def _convert_to_retrieved_content(self, item: Dict[str, Any]) -> Optional[RetrievedContent]:
        """Convert database item to RetrievedContent"""
        try:
            # Extract KIQ alignments
            kiq_alignments = []
            if "kiq_alignments" in item:
                kiq_alignments = [alignment.get("kiq_id", "") for alignment in item["kiq_alignments"]]
            
            # Extract KIT classifications
            kit_classifications = []
            if "kit_classifications" in item:
                kit_classifications = [classification.get("kit_id", "") for classification in item["kit_classifications"]]
            
            content = RetrievedContent(
                content_id=item.get("id", "unknown"),
                title=item.get("title", ""),
                content=item.get("content", ""),
                summary=item.get("summary", ""),
                relevance_score=item.get("relevance_score", 0.0),
                kiq_alignments=kiq_alignments,
                kit_classifications=kit_classifications,
                extraction_confidence=item.get("extraction_confidence", 0.0),
                source_authority=item.get("source_authority", 0.0),
                url=item.get("url", ""),
                domain=item.get("domain", ""),
                published_date=item.get("published_date")
            )
            
            return content
            
        except Exception as e:
            logger.warning(f"Failed to convert item to RetrievedContent: {str(e)}")
            return None
    
    async def get_content_by_ids(self, content_ids: List[str]) -> List[RetrievedContent]:
        """Retrieve specific content by IDs"""
        try:
            retrieved_content = []
            
            for content_id in content_ids:
                try:
                    item = await self.database_client.get_item("knowledge_base", {"id": content_id})
                    if item:
                        content = await self._convert_to_retrieved_content(item)
                        if content:
                            retrieved_content.append(content)
                
                except Exception as e:
                    logger.warning(f"Failed to retrieve content {content_id}: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(retrieved_content)} content items by ID")
            return retrieved_content
            
        except Exception as e:
            logger.error(f"Content ID retrieval failed: {str(e)}")
            return []
    
    async def get_content_stats(self, request_ids: List[str] = None) -> Dict[str, Any]:
        """Get statistics about available content"""
        try:
            # Build query for content statistics
            query_params = {}
            
            if request_ids:
                query_params["FilterExpression"] = "request_id IN (:request_ids)"
                query_params["ExpressionAttributeValues"] = {":request_ids": request_ids}
            
            # Get content items
            items = await self.database_client.query_items("knowledge_base", **query_params)
            
            stats = {
                "total_items": len(items),
                "high_relevance_items": sum(1 for item in items if item.get("relevance_score", 0) >= 0.8),
                "high_quality_items": sum(1 for item in items if item.get("extraction_confidence", 0) >= 0.8),
                "kiq_coverage": {},
                "kit_coverage": {},
                "average_relevance": 0.0,
                "average_quality": 0.0
            }
            
            if items:
                # Calculate averages
                relevance_scores = [item.get("relevance_score", 0.0) for item in items]
                quality_scores = [item.get("extraction_confidence", 0.0) for item in items]
                
                stats["average_relevance"] = sum(relevance_scores) / len(relevance_scores)
                stats["average_quality"] = sum(quality_scores) / len(quality_scores)
                
                # Calculate coverage
                for item in items:
                    kiq_alignments = item.get("kiq_alignments", [])
                    for alignment in kiq_alignments:
                        kiq_id = alignment.get("kiq_id", "")
                        if kiq_id:
                            stats["kiq_coverage"][kiq_id] = stats["kiq_coverage"].get(kiq_id, 0) + 1
                    
                    kit_classifications = item.get("kit_classifications", [])
                    for classification in kit_classifications:
                        kit_id = classification.get("kit_id", "")
                        if kit_id:
                            stats["kit_coverage"][kit_id] = stats["kit_coverage"].get(kit_id, 0) + 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Content stats retrieval failed: {str(e)}")
            return {}
```

## service.py
```python
from typing import List, Dict, Any, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from .models import InsightsRequest, InsightsResponse, RAGRetrievalConfig
from .rag_retrieval import RAGRetrieval
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class InsightsService:
    """Main insights service for strategic intelligence generation"""
    
    def __init__(self):
        self.openai_client = ServiceFactory.get_openai_client()
        self.rag_retrieval = RAGRetrieval()
        self.storage_client = ServiceFactory.get_storage_client()
        self.database_client = ServiceFactory.get_database_client()
    
    async def generate_insights(self, request: InsightsRequest) -> InsightsResponse:
        """Generate strategic insights from knowledge base content"""
        start_time = datetime.utcnow()
        
        try:
            logger.info(f"Starting insights generation for request {request.request_id}")
            
            # Stage 1: Retrieve relevant content
            retrieval_start = datetime.utcnow()
            retrieved_content = await self._retrieve_content(request)
            retrieval_time = (datetime.utcnow() - retrieval_start).total_seconds()
            
            if not retrieved_content:
                logger.warning("No relevant content retrieved for insights generation")
                return self._create_empty_response(request, retrieval_time)
            
            # Stage 2: Generate insights
            analysis_start = datetime.utcnow()
            
            # Load KIQ and KIT context
            kiq_context = await self._load_kiq_context(request.focus_kiqs)
            kit_context = await self._load_kit_context(request.focus_kits)
            
            # Generate KIQ-focused insights
            kiq_insights = await self.openai_client.generate_kiq_insights(
                retrieved_content, kiq_context, request.user_prompt
            )
            
            # Generate KIT-organized insights
            kit_insights = await self.openai_client.generate_kit_insights(
                retrieved_content, kit_context, request.user_prompt
            )
            
            # Identify cross-KIT patterns
            cross_kit_patterns = []
            if request.include_cross_kit_analysis:
                cross_kit_patterns = await self.openai_client.identify_cross_kit_patterns(
                    retrieved_content, kit_insights
                )
            
            # Generate synthesis
            synthesis = None
            if request.include_synthesis:
                synthesis = await self.openai_client.synthesize_insights(
                    kiq_insights, kit_insights, cross_kit_patterns, request.user_prompt
                )
            
            analysis_time = (datetime.utcnow() - analysis_start).total_seconds()
            
            # Create response
            response = self._create_response(
                request, retrieved_content, kiq_insights, kit_insights, 
                cross_kit_patterns, synthesis, retrieval_time, analysis_time, start_time
            )
            
            # Store results
            await self._store_insights(response)
            
            logger.info(f"Insights generation completed: {len(response.kiq_focused_insights)} KIQ insights, {len(response.kit_insights)} KIT insights")
            return response
            
        except Exception as e:
            logger.error(f"Insights generation failed for {request.request_id}: {str(e)}")
            raise Exception(f"Insights generation failed: {str(e)}")
    
    async def _retrieve_content(self, request: InsightsRequest) -> List:
        """Retrieve relevant content for insights generation"""
        try:
            config = RAGRetrievalConfig(
                number_of_results=request.max_content_items,
                min_relevance_score=request.min_relevance_score,
                request_ids=request.content_request_ids,
                kiq_ids=request.focus_kiqs,
                kit_ids=request.focus_kits,
                require_high_quality=True
            )
            
            if request.specific_content_ids:
                # Retrieve specific content by IDs
                specific_content = await self.rag_retrieval.get_content_by_ids(request.specific_content_ids)
                
                # Also retrieve by query for additional context
                query_content = await self.rag_retrieval.retrieve_relevant_content(request.user_prompt, config)
                
                # Combine and deduplicate
                all_content = specific_content + query_content
                seen_ids = set()
                deduped_content = []
                
                for content in all_content:
                    if content.content_id not in seen_ids:
                        seen_ids.add(content.content_id)
                        deduped_content.append(content)
                
                return deduped_content[:request.max_content_items]
            
            else:
                # Retrieve by semantic search
                return await self.rag_retrieval.retrieve_relevant_content(request.user_prompt, config)
            
        except Exception as e:
            logger.error(f"Content retrieval failed: {str(e)}")
            return []
    
    async def _load_kiq_context(self, focus_kiqs: List[str]) -> Dict[str, Any]:
        """Load KIQ context information"""
        try:
            kiq_context = {}
            
            # Load KIQ definitions (this would typically come from a configuration store)
            default_kiqs = {
                "KIQ-001": {
                    "question": "What are competitors' drug development pipelines and timelines?",
                    "category": "competitive_intelligence",
                    "keywords": ["pipeline", "phase", "clinical trial", "competitor"]
                },
                "KIQ-002": {
                    "question": "What regulatory changes affect our therapeutic areas?",
                    "category": "regulatory_landscape", 
                    "keywords": ["FDA", "regulation", "guideline", "approval"]
                },
                "KIQ-003": {
                    "question": "What are pricing pressures and market access challenges?",
                    "category": "market_dynamics",
                    "keywords": ["pricing", "reimbursement", "payer", "access"]
                }
            }
            
            if focus_kiqs:
                for kiq_id in focus_kiqs:
                    if kiq_id in default_kiqs:
                        kiq_context[kiq_id] = default_kiqs[kiq_id]
            else:
                kiq_context = default_kiqs
            
            return kiq_context
            
        except Exception as e:
            logger.error(f"KIQ context loading failed: {str(e)}")
            return {}
    
    async def _load_kit_context(self, focus_kits: List[str]) -> Dict[str, Any]:
        """Load KIT context information"""
        try:
            kit_context = {}
            
            # Load KIT definitions (this would typically come from a configuration store)
            default_kits = {
                "KIT-001": {
                    "name": "Competitive Pipeline Intelligence",
                    "description": "Monitor competitor drug development and market strategies",
                    "priority": "high"
                },
                "KIT-002": {
                    "name": "Regulatory Environment Monitoring",
                    "description": "Track regulatory changes and policy developments",
                    "priority": "critical"
                },
                "KIT-003": {
                    "name": "Market Access Intelligence",
                    "description": "Monitor payer trends and access challenges",
                    "priority": "high"
                },
                "KIT-004": {
                    "name": "Technology Innovation Tracking",
                    "description": "Monitor emerging technologies and digital health trends",
                    "priority": "medium"
                }
            }
            
            if focus_kits:
                for kit_id in focus_kits:
                    if kit_id in default_kits:
                        kit_context[kit_id] = default_kits[kit_id]
            else:
                kit_context = default_kits
            
            return kit_context
            
        except Exception as e:
            logger.error(f"KIT context loading failed: {str(e)}")
            return {}
    
    def _create_response(self, request, retrieved_content, kiq_insights, kit_insights, 
                        cross_kit_patterns, synthesis, retrieval_time, analysis_time, start_time) -> InsightsResponse:
        """Create insights response"""
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        response = InsightsResponse(
            request_id=request.request_id,
            user_prompt=request.user_prompt,
            kiq_focused_insights=kiq_insights,
            kit_insights=kit_insights,
            cross_kit_patterns=cross_kit_patterns,
            synthesis=synthesis,
            content_analyzed=len(retrieved_content),
            processing_time=processing_time,
            retrieval_time=retrieval_time,
            analysis_time=analysis_time
        )
        
        # Calculate summary statistics
        response.calculate_summary_stats()
        
        return response
    
    def _create_empty_response(self, request: InsightsRequest, retrieval_time: float) -> InsightsResponse:
        """Create empty response when no content is retrieved"""
        return InsightsResponse(
            request_id=request.request_id,
            user_prompt=request.user_prompt,
            content_analyzed=0,
            retrieval_time=retrieval_time,
            processing_time=retrieval_time
        )
    
    async def _store_insights(self, response: InsightsResponse):
        """Store generated insights"""
        try:
            # Store complete response
            storage_key = f"insights_results/{response.request_id}.json"
            await self.storage_client.save_json(storage_key, response.dict())
            
            # Store individual KIQ insights
            for i, insight in enumerate(response.kiq_focused_insights):
                insight_key = f"insights_kiq/{response.request_id}/{i}.json"
                await self.storage_client.save_json(insight_key, insight.dict())
            
            # Store metadata in database
            await self.database_client.save_item("insights_generations", {
                "request_id": response.request_id,
                "user_prompt": response.user_prompt,
                "content_analyzed": response.content_analyzed,
                "kiqs_addressed": response.kiqs_addressed,
                "kits_covered": response.kits_covered,
                "average_insight_confidence": response.average_insight_confidence,
                "high_confidence_insights": response.high_confidence_insights,
                "processing_time": response.processing_time,
                "storage_key": storage_key,
                "created_at": response.created_at.isoformat()
            })
            
            logger.info(f"Stored insights results: {storage_key}")
            
        except Exception as e:
            logger.error(f"Failed to store insights: {str(e)}")
```

## storage.py
```python
from typing import Dict, Any, List, Optional
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class InsightsStorage:
    """Handle insights-specific storage operations"""
    
    def __init__(self):
        self.storage_client = ServiceFactory.get_storage_client()
    
    async def save_insights_results(self, request_id: str, results: Dict[str, Any]) -> bool:
        """Save complete insights results"""
        try:
            key = f"insights_results/{request_id}.json"
            success = await self.storage_client.save_json(key, results)
            
            if success:
                logger.info(f"Saved insights results: {key}")
            
            return success
            
        except Exception as e:
            logger.error(f"Insights results save error: {str(e)}")
            return False
    
    async def save_kiq_insights(self, request_id: str, kiq_insights: List[Dict[str, Any]]) -> bool:
        """Save individual KIQ insights"""
        try:
            success_count = 0
            
            for i, insight in enumerate(kiq_insights):
                key = f"insights_kiq/{request_id}/{i}.json"
                if await self.storage_client.save_json(key, insight):
                    success_count += 1
            
            logger.info(f"Saved {success_count}/{len(kiq_insights)} KIQ insights")
            return success_count == len(kiq_insights)
            
        except Exception as e:
            logger.error(f"KIQ insights save error: {str(e)}")
            return False
```

## database.py
```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from ...config.service_factory import ServiceFactory
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)

class InsightsDatabase:
    """Handle insights database operations"""
    
    def __init__(self):
        self.db_client = ServiceFactory.get_database_client()
        self.table_name = "insights_generations"
    
    async def save_insights_metadata(self, metadata: Dict[str, Any]) -> bool:
        """Save insights generation metadata"""
        try:
            if 'created_at' not in metadata:
                metadata['created_at'] = datetime.utcnow().isoformat()
            
            success = await self.db_client.save_item(self.table_name, metadata)
            
            if success:
                logger.info(f"Saved insights metadata: {metadata.get('request_id')}")
            
            return success
            
        except Exception as e:
            logger.error(f"Insights metadata save error: {str(e)}")
            return False
    
    async def get_insights_stats(self, request_id: str) -> Dict[str, Any]:
        """Get insights generation statistics"""
        try:
            metadata = await self.db_client.get_item(self.table_name, {"request_id": request_id})
            
            if not metadata:
                return {}
            
            return {
                "request_id": request_id,
                "user_prompt": metadata.get("user_prompt", ""),
                "content_analyzed": metadata.get("content_analyzed", 0),
                "kiqs_addressed": metadata.get("kiqs_addressed", 0),
                "kits_covered": metadata.get("kits_covered", 0),
                "average_insight_confidence": metadata.get("average_insight_confidence", 0.0),
                "high_confidence_insights": metadata.get("high_confidence_insights", 0),
                "processing_time": metadata.get("processing_time", 0.0),
                "created_at": metadata.get("created_at")
            }
            
        except Exception as e:
            logger.error(f"Insights stats error: {str(e)}")
            return {}
```