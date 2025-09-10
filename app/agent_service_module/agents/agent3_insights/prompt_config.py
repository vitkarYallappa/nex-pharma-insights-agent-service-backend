"""
Prompt Configuration for Agent 3 - Insights Generation

Clean and modular prompt templates for generating insights from content.
"""

from typing import Dict, Any

class InsightPromptConfig:
    """Configuration class for insight generation prompts"""
    
    # System prompt for insight generation
    SYSTEM_PROMPT = """You are an expert pharmaceutical market intelligence analyst specializing in generating actionable insights from research content.

Your role is to:
1. Analyze pharmaceutical and healthcare content
2. Extract key market insights and trends
3. Identify business opportunities and risks
4. Provide strategic recommendations
5. Highlight competitive intelligence

Focus on:
- Market dynamics and trends
- Regulatory developments
- Clinical trial outcomes
- Competitive landscape
- Investment opportunities
- Risk factors
- Strategic implications"""

    # Main insight generation prompt
    INSIGHT_GENERATION_PROMPT = """Analyze the following pharmaceutical market content and generate comprehensive insights:

CONTENT TO ANALYZE:
{content}

ANALYSIS REQUIREMENTS:
1. **Market Insights**: Key market trends, size, growth opportunities
2. **Competitive Intelligence**: Competitor activities, market positioning
3. **Regulatory Impact**: Regulatory changes, compliance requirements
4. **Clinical Developments**: Trial results, drug approvals, pipeline updates
5. **Investment Opportunities**: Potential investments, partnerships, M&A
6. **Risk Assessment**: Market risks, regulatory risks, competitive threats
7. **Strategic Recommendations**: Actionable next steps and strategies

RESPONSE FORMAT:
Provide insights in the following JSON structure:
{{
    "market_insights": [
        {{
            "insight": "Clear, actionable insight",
            "category": "market_trend|competitive|regulatory|clinical|investment|risk",
            "confidence_score": 0.0-1.0,
            "impact_level": "high|medium|low",
            "time_horizon": "immediate|short_term|medium_term|long_term",
            "supporting_evidence": ["evidence1", "evidence2"]
        }}
    ],
    "key_themes": ["theme1", "theme2", "theme3"],
    "strategic_recommendations": [
        {{
            "recommendation": "Specific actionable recommendation",
            "priority": "high|medium|low",
            "rationale": "Why this recommendation is important"
        }}
    ],
    "risk_factors": [
        {{
            "risk": "Identified risk",
            "severity": "high|medium|low",
            "mitigation": "Suggested mitigation strategy"
        }}
    ]
}}

Generate comprehensive, actionable insights that provide clear business value."""

    # Summary prompt for multiple sources
    MULTI_SOURCE_SUMMARY_PROMPT = """You are analyzing content from multiple pharmaceutical sources. Generate a consolidated insight summary:

SOURCES ANALYZED:
{source_count} sources including: {source_types}

CONTENT SUMMARY:
{content_summary}

Generate a high-level executive summary focusing on:
1. Cross-source patterns and trends
2. Conflicting information or perspectives
3. Overall market implications
4. Priority action items

Keep the summary concise but comprehensive, highlighting the most critical insights for pharmaceutical decision-makers."""

    @classmethod
    def get_insight_prompt(cls, content: str, metadata: Dict[str, Any] = None) -> str:
        """Get formatted insight generation prompt"""
        return cls.INSIGHT_GENERATION_PROMPT.format(content=content)
    
    @classmethod
    def get_multi_source_prompt(cls, content_summary: str, source_count: int, source_types: str) -> str:
        """Get formatted multi-source summary prompt"""
        return cls.MULTI_SOURCE_SUMMARY_PROMPT.format(
            source_count=source_count,
            source_types=source_types,
            content_summary=content_summary
        )
    
    @classmethod
    def get_system_prompt(cls) -> str:
        """Get system prompt"""
        return cls.SYSTEM_PROMPT

# Model configuration
MODEL_CONFIG = {
    "anthropic_direct": {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4000,
        "temperature": 0.3
    },
    "aws_bedrock": {
        "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "max_tokens": 4000,
        "temperature": 0.3
    }
}

# Response validation schema
EXPECTED_RESPONSE_KEYS = [
    "market_insights",
    "key_themes", 
    "strategic_recommendations",
    "risk_factors"
] 