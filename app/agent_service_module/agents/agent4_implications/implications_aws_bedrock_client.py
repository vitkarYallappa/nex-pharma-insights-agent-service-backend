"""
AWS Bedrock with Anthropic Claude integration for Agent 4 Implications
Provides enterprise-grade access to Claude models through AWS Bedrock
"""

import asyncio
import json
import boto3
from typing import List, Dict, Any, Optional
from datetime import datetime
from botocore.exceptions import ClientError, BotoCoreError
from .models import (
    StrategicImplication, ScenarioOutcome, StakeholderAnalysis, PriorityMatrix,
    ResourceRequirement, TimeHorizon, ImpactLevel, StakeholderRole, ActionCategory,
    UrgencyLevel, InsightContext
)
from ...config.settings import settings
from ...shared.utils.logger import get_logger

logger = get_logger(__name__)


class BedrockAPI:
    """AWS Bedrock client for Anthropic Claude implications generation"""

    def __init__(self):
        # Initialize AWS Bedrock client
        self.bedrock_client = boto3.client(
            'bedrock-runtime',
            region_name=getattr(settings, 'AWS_REGION', 'us-east-1'),
            aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
            aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        )

        # Bedrock model configuration
        self.model_id = getattr(settings, 'BEDROCK_MODEL_ID', 'anthropic.claude-3-sonnet-20240229-v1:0')
        self.max_tokens = getattr(settings, 'BEDROCK_MAX_TOKENS', 4000)
        self.temperature = getattr(settings, 'BEDROCK_TEMPERATURE', 0.2)
        self.top_p = getattr(settings, 'BEDROCK_TOP_P', 0.9)

        # Rate limiting and retry configuration
        self.max_retries = getattr(settings, 'BEDROCK_MAX_RETRIES', 3)
        self.retry_delay = getattr(settings, 'BEDROCK_RETRY_DELAY', 1.0)

    async def generate_strategic_implications(
            self, insights_context: List[InsightContext],
            stakeholder_role: StakeholderRole,
            organizational_context: str
    ) -> List[StrategicImplication]:
        """Generate strategic implications using AWS Bedrock"""
        try:
            insights_summary = self._prepare_insights_for_analysis(insights_context)
            prompt = self._build_implications_prompt(insights_summary, stakeholder_role, organizational_context)

            # Prepare Bedrock request
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "system": "You are a senior strategic advisor generating actionable implications from intelligence insights for specific stakeholders. Always respond with valid JSON."
            }

            # Make Bedrock API call with retry logic
            response = await self._invoke_bedrock_with_retry(body)

            if not response:
                logger.error("Failed to get response from Bedrock")
                return []

            # Parse response
            result = self._parse_bedrock_response(response)

            if not result:
                logger.error("Failed to parse JSON from Bedrock response")
                return []

            implications = []

            for impl_data in result.get("strategic_implications", []):
                try:
                    implication = StrategicImplication(
                        implication_id=f"bedrock_impl_{int(datetime.utcnow().timestamp())}_{len(implications)}",
                        implication=impl_data.get("implication", ""),
                        timeframe=TimeHorizon(impl_data.get("timeframe", "medium_term")),
                        impact_level=ImpactLevel(impl_data.get("impact_level", "medium")),
                        probability=float(impl_data.get("probability", 0.5)),
                        primary_stakeholders=self._parse_stakeholders(impl_data.get("primary_stakeholders", [])),
                        stakeholder_relevance=float(impl_data.get("stakeholder_relevance", 0.5)),
                        action_required=impl_data.get("action_required", ""),
                        action_category=ActionCategory(impl_data.get("action_category", "strategic_planning")),
                        resources_needed=impl_data.get("resources_needed", []),
                        estimated_cost=impl_data.get("estimated_cost", "TBD"),
                        dependencies=impl_data.get("dependencies", []),
                        constraints=impl_data.get("constraints", []),
                        risks=impl_data.get("risks", []),
                        success_metrics=impl_data.get("success_metrics", []),
                        milestones=impl_data.get("milestones", []),
                        source_insight_ids=self._extract_source_insight_ids(insights_context,
                                                                            impl_data.get("implication", "")),
                        confidence=float(impl_data.get("confidence", 0.0))
                    )
                    implications.append(implication)
                except Exception as e:
                    logger.warning(f"Failed to parse implication: {str(e)}")
                    continue

            logger.info(f"Generated {len(implications)} strategic implications via Bedrock")
            return implications

        except Exception as e:
            logger.error(f"Bedrock implications generation failed: {str(e)}")
            return []

    async def generate_scenario_planning(
            self, implications: List[StrategicImplication],
            insights_context: List[InsightContext]
    ) -> List[ScenarioOutcome]:
        """Generate scenario planning using AWS Bedrock"""
        try:
            implications_summary = self._summarize_implications_for_scenarios(implications)
            insights_summary = self._prepare_insights_for_analysis(insights_context)

            prompt = self._build_scenario_planning_prompt(implications_summary, insights_summary)

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.max_tokens,
                "temperature": 0.3,
                "top_p": self.top_p,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "system": "You are an expert strategic planner creating scenario analyses and contingency planning. Always respond with valid JSON."
            }

            response = await self._invoke_bedrock_with_retry(body)

            if not response:
                logger.error("Failed to get scenario response from Bedrock")
                return []

            result = self._parse_bedrock_response(response)

            if not result:
                logger.error("Failed to parse JSON from Bedrock scenario response")
                return []

            scenarios = []

            for scenario_data in result.get("scenario_planning", []):
                try:
                    scenario = ScenarioOutcome(
                        scenario_id=f"bedrock_scenario_{int(datetime.utcnow().timestamp())}_{len(scenarios)}",
                        scenario=scenario_data.get("scenario", ""),
                        probability=float(scenario_data.get("probability", 0.0)),
                        potential_impact=ImpactLevel(scenario_data.get("potential_impact", "medium")),
                        affected_stakeholders=self._parse_stakeholders(scenario_data.get("affected_stakeholders", [])),
                        implications=scenario_data.get("implications", []),
                        preparation_actions=scenario_data.get("preparation_actions", []),
                        response_strategies=scenario_data.get("response_strategies", []),
                        early_warning_signals=scenario_data.get("early_warning_signals", []),
                        monitoring_requirements=scenario_data.get("monitoring_requirements", []),
                        resource_requirements=scenario_data.get("resource_requirements", []),
                        timeline_considerations=scenario_data.get("timeline_considerations", "")
                    )
                    scenarios.append(scenario)
                except Exception as e:
                    logger.warning(f"Failed to parse scenario: {str(e)}")
                    continue

            logger.info(f"Generated {len(scenarios)} scenario outcomes via Bedrock")
            return scenarios

        except Exception as e:
            logger.error(f"Bedrock scenario planning generation failed: {str(e)}")
            return []

    async def generate_stakeholder_analysis(
            self, implications: List[StrategicImplication],
            stakeholder_roles: List[StakeholderRole]
    ) -> Dict[str, StakeholderAnalysis]:
        """Generate stakeholder-specific analysis using AWS Bedrock"""
        try:
            stakeholder_analyses = {}

            for stakeholder_role in stakeholder_roles:
                relevant_implications = [
                    impl for impl in implications
                    if stakeholder_role in impl.primary_stakeholders or impl.stakeholder_relevance > 0.6
                ]

                if not relevant_implications:
                    continue

                implications_summary = self._summarize_implications_for_stakeholder(relevant_implications,
                                                                                    stakeholder_role)
                prompt = self._build_stakeholder_analysis_prompt(implications_summary, stakeholder_role)

                body = {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 2000,
                    "temperature": self.temperature,
                    "top_p": self.top_p,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "system": f"You are advising {stakeholder_role.value} on strategic implications and actions. Always respond with valid JSON."
                }

                response = await self._invoke_bedrock_with_retry(body)

                if response:
                    result = self._parse_bedrock_response(response)

                    if result:
                        analysis_data = result.get("stakeholder_analysis", {})

                        analysis = StakeholderAnalysis(
                            stakeholder_role=stakeholder_role,
                            relevant_implications=[impl.implication_id for impl in relevant_implications],
                            priority_implications=self._identify_priority_implications(relevant_implications),
                            key_concerns=analysis_data.get("key_concerns", []),
                            decision_requirements=analysis_data.get("decision_requirements", []),
                            information_needs=analysis_data.get("information_needs", []),
                            immediate_actions=analysis_data.get("immediate_actions", []),
                            strategic_actions=analysis_data.get("strategic_actions", []),
                            key_messages=analysis_data.get("key_messages", []),
                            communication_urgency=self._assess_communication_urgency(relevant_implications),
                            escalation_requirements=analysis_data.get("escalation_requirements", []),
                            success_factors=analysis_data.get("success_factors", []),
                            potential_obstacles=analysis_data.get("potential_obstacles", [])
                        )

                        stakeholder_analyses[stakeholder_role.value] = analysis

            logger.info(f"Generated Bedrock stakeholder analysis for {len(stakeholder_analyses)} roles")
            return stakeholder_analyses

        except Exception as e:
            logger.error(f"Bedrock stakeholder analysis generation failed: {str(e)}")
            return {}

    async def synthesize_insights(
            self, kiq_insights: List, kit_insights: List,
            cross_kit_patterns: List, user_prompt: str
    ) -> Dict[str, Any]:
        """Create executive synthesis using AWS Bedrock"""
        try:
            synthesis_input = self._prepare_synthesis_input(kiq_insights, kit_insights, cross_kit_patterns)
            prompt = self._build_synthesis_prompt(synthesis_input, user_prompt)

            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "system": "You are a senior strategic advisor creating executive-level synthesis of intelligence insights. Always respond with valid JSON."
            }

            response = await self._invoke_bedrock_with_retry(body)

            if response:
                result = self._parse_bedrock_response(response)

                if result:
                    synthesis = {
                        "executive_summary": result.get("executive_summary", ""),
                        "key_findings": result.get("key_findings", []),
                        "strategic_recommendations": result.get("strategic_recommendations", []),
                        "immediate_actions": result.get("immediate_actions", []),
                        "risk_level": result.get("risk_level", "medium"),
                        "opportunity_level": result.get("opportunity_level", "medium"),
                        "synthesis_confidence": float(result.get("synthesis_confidence", 0.0)),
                        "information_completeness": float(result.get("information_completeness", 0.0))
                    }

                    logger.info("Generated Bedrock executive synthesis")
                    return synthesis
                else:
                    logger.error("Failed to parse Bedrock synthesis response")
                    return {}
            else:
                logger.error("Failed to get synthesis response from Bedrock")
                return {}

        except Exception as e:
            logger.error(f"Bedrock synthesis generation failed: {str(e)}")
            return {}

    async def generate_priority_matrix(self, implications: List[StrategicImplication]) -> PriorityMatrix:
        """Generate priority matrix using business logic (no API call needed)"""
        try:
            matrix = PriorityMatrix()

            for impl in implications:
                quadrant = impl.get_priority_quadrant()
                action_item = f"{impl.action_required} ({impl.timeframe.value})"

                if quadrant.value == "urgent_important":
                    matrix.urgent_important.append(action_item)
                elif quadrant.value == "important_not_urgent":
                    matrix.important_not_urgent.append(action_item)
                elif quadrant.value == "urgent_not_important":
                    matrix.urgent_not_important.append(action_item)
                else:
                    matrix.neither.append(action_item)

            logger.info("Generated priority matrix")
            return matrix

        except Exception as e:
            logger.error(f"Priority matrix generation failed: {str(e)}")
            return PriorityMatrix()

    # Core Bedrock Integration Methods

    async def _invoke_bedrock_with_retry(self, body: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Invoke Bedrock API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Convert body to JSON string for Bedrock
                body_json = json.dumps(body)

                # Make the Bedrock API call
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    contentType='application/json',
                    accept='application/json',
                    body=body_json
                )

                # Parse the response
                response_body = json.loads(response['body'].read())

                logger.debug(f"Bedrock API call successful on attempt {attempt + 1}")
                return response_body

            except ClientError as e:
                error_code = e.response['Error']['Code']
                error_message = e.response['Error']['Message']

                logger.warning(f"Bedrock API error on attempt {attempt + 1}: {error_code} - {error_message}")

                # Handle specific error types
                if error_code in ['ThrottlingException', 'ServiceQuotaExceededException']:
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Retrying in {wait_time} seconds...")
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error("Max retries exceeded for throttling error")
                        return None
                elif error_code in ['ValidationException', 'AccessDeniedException']:
                    logger.error(f"Non-retryable error: {error_code} - {error_message}")
                    return None
                else:
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay)
                        continue
                    else:
                        logger.error(f"Max retries exceeded for error: {error_code}")
                        return None

            except BotoCoreError as e:
                logger.warning(f"BotoCore error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    logger.error("Max retries exceeded for BotoCore error")
                    return None

            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    logger.error("Max retries exceeded for unexpected error")
                    return None

        return None

    def _parse_bedrock_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Bedrock response and extract JSON content"""
        try:
            # Bedrock returns content in a specific format
            content = response.get('content', [])

            if not content:
                logger.error("No content in Bedrock response")
                return None

            # Extract text from the first content block
            text_content = ""
            for content_block in content:
                if content_block.get('type') == 'text':
                    text_content = content_block.get('text', '')
                    break

            if not text_content:
                logger.error("No text content found in Bedrock response")
                return None

            # Extract and parse JSON from the text content
            return self._extract_json_from_text(text_content)

        except Exception as e:
            logger.error(f"Error parsing Bedrock response: {str(e)}")
            return None

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract and parse JSON from text response"""
        try:
            # Find JSON boundaries
            json_start = text.find('{')
            json_end = text.rfind('}') + 1

            if json_start >= 0 and json_end > json_start:
                json_content = text[json_start:json_end]
                return json.loads(json_content)
            else:
                # Try parsing the entire text as JSON
                return json.loads(text.strip())

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.debug(f"Content that failed to parse: {text[:500]}...")
            return None

    # Helper Methods (shared with other API implementations)

    def _prepare_insights_for_analysis(self, insights_context: List[InsightContext]) -> str:
        """Prepare insights for analysis"""
        insights_parts = []

        for i, insight in enumerate(insights_context[:15]):
            insight_part = f"""
Insight {i + 1}:
Type: {insight.insight_type}
Content: {insight.insight_content}
KIQ: {insight.kiq_id or 'N/A'}
KIT: {insight.kit_id or 'N/A'}
Category: {insight.category}
Confidence: {insight.confidence:.2f}
---
"""
            insights_parts.append(insight_part)

        return "\n".join(insights_parts)

    def _build_implications_prompt(self, insights_summary: str, stakeholder_role: StakeholderRole,
                                   organizational_context: str) -> str:
        """Build comprehensive prompt for strategic implications"""
        return f"""
Transform strategic insights into actionable implications for {stakeholder_role.value}.

Organizational Context: {organizational_context}

Strategic Insights:
{insights_summary}

Generate strategic implications in JSON format:
{{
  "strategic_implications": [
    {{
      "implication": "strategic impact and what it means for the organization",
      "timeframe": "immediate|short_term|medium_term|long_term",
      "impact_level": "low|medium|high|critical",
      "probability": 0.0-1.0,
      "primary_stakeholders": ["executive_leadership", "risk_management", "business_development", "technical_teams", "regulatory_affairs", "commercial_teams", "investors_analysts", "operations", "legal_compliance", "research_development"],
      "stakeholder_relevance": 0.0-1.0,
      "action_required": "specific action needed",
      "action_category": "immediate_response|strategic_planning|risk_mitigation|opportunity_capture|monitoring_surveillance|stakeholder_communication|resource_allocation|process_improvement",
      "resources_needed": ["specific resources required"],
      "estimated_cost": "cost estimate or resource requirement",
      "dependencies": ["what must happen first"],
      "constraints": ["limitations or constraints"],
      "risks": ["implementation risks"],
      "success_metrics": ["how to measure success"],
      "milestones": ["key milestones"],
      "confidence": 0.0-1.0
    }}
  ]
}}

Focus on:
1. Actionable implications with clear next steps
2. Time-sensitive actions requiring immediate attention
3. Strategic initiatives with long-term impact
4. Resource requirements and constraints
5. Stakeholder-specific relevance and urgency
6. Measurable outcomes and success criteria

Ensure all field values match the specified enums exactly.
"""

    def _build_scenario_planning_prompt(self, implications_summary: str, insights_summary: str) -> str:
        """Build prompt for scenario planning"""
        return f"""
Create scenario planning based on strategic implications and insights.

Strategic Implications:
{implications_summary}

Supporting Insights:
{insights_summary}

Generate scenario outcomes in JSON format:
{{
  "scenario_planning": [
    {{
      "scenario": "description of potential future outcome",
      "probability": 0.0-1.0,
      "potential_impact": "low|medium|high|critical",
      "affected_stakeholders": ["executive_leadership", "risk_management", "business_development", "technical_teams", "regulatory_affairs", "commercial_teams", "investors_analysts", "operations", "legal_compliance", "research_development"],
      "implications": ["what this scenario means"],
      "preparation_actions": ["actions to prepare for this scenario"],
      "response_strategies": ["how to respond if scenario occurs"],
      "early_warning_signals": ["signals this scenario is emerging"],
      "monitoring_requirements": ["what to monitor"],
      "resource_requirements": ["resources needed for response"],
      "timeline_considerations": "timeline factors"
    }}
  ]
}}

Requirements:
1. Create 3-5 realistic scenarios with different probability levels
2. Include both positive and negative outcomes
3. Focus on scenarios with strategic significance
4. Provide actionable preparation and response strategies
5. Identify clear early warning indicators
"""

    def _build_stakeholder_analysis_prompt(self, implications_summary: str, stakeholder_role: StakeholderRole) -> str:
        """Build prompt for stakeholder analysis"""
        return f"""
Create stakeholder-specific analysis for {stakeholder_role.value}.

Relevant Strategic Implications:
{implications_summary}

Generate stakeholder analysis in JSON format:
{{
  "stakeholder_analysis": {{
    "key_concerns": ["primary concerns for this stakeholder"],
    "decision_requirements": ["decisions this stakeholder needs to make"],
    "information_needs": ["information this stakeholder requires"],
    "immediate_actions": ["actions needed within 30 days"],
    "strategic_actions": ["longer-term actions"],
    "key_messages": ["key messages for this stakeholder"],
    "escalation_requirements": ["when to escalate to senior leadership"],
    "success_factors": ["factors for successful execution"],
    "potential_obstacles": ["potential obstacles or challenges"]
  }}
}}

Tailor analysis for {stakeholder_role.value} perspective:
1. Focus on decisions and actions within their authority
2. Address their specific concerns and priorities
3. Provide clear, actionable guidance
4. Consider their resource constraints and capabilities
5. Include communication and coordination requirements
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

    def _parse_stakeholders(self, stakeholder_list: List[str]) -> List[StakeholderRole]:
        """Parse stakeholder roles from strings"""
        stakeholders = []
        for stakeholder_str in stakeholder_list:
            try:
                stakeholder = StakeholderRole(stakeholder_str.lower().replace(" ", "_"))
                stakeholders.append(stakeholder)
            except ValueError:
                stakeholders.append(StakeholderRole.EXECUTIVE_LEADERSHIP)
        return stakeholders

    def _extract_source_insight_ids(self, insights_context: List[InsightContext], implication_text: str) -> List[str]:
        """Extract source insight IDs that contributed to implication"""
        source_ids = []
        implication_words = set(implication_text.lower().split())

        for insight in insights_context:
            insight_words = set(insight.insight_content.lower().split())
            overlap = len(implication_words & insight_words)

            if overlap > 3:
                source_ids.append(insight.insight_id)

        return source_ids[:3]

    def _summarize_implications_for_scenarios(self, implications: List[StrategicImplication]) -> str:
        """Summarize implications for scenario planning"""
        summaries = []

        for impl in implications[:10]:
            summary = f"- {impl.implication} (Impact: {impl.impact_level.value}, Timeline: {impl.timeframe.value})"
            summaries.append(summary)

        return "\n".join(summaries)

    def _summarize_implications_for_stakeholder(self, implications: List[StrategicImplication],
                                                stakeholder: StakeholderRole) -> str:
        """Summarize implications for specific stakeholder"""
        summaries = []

        for impl in implications:
            summary = f"- {impl.implication}\n  Action: {impl.action_required}\n  Timeline: {impl.timeframe.value}\n  Impact: {impl.impact_level.value}"
            summaries.append(summary)

        return "\n".join(summaries)

    def _identify_priority_implications(self, implications: List[StrategicImplication]) -> List[str]:
        """Identify high-priority implications"""
        priority_implications = []

        for impl in implications:
            if (impl.impact_level in [ImpactLevel.HIGH, ImpactLevel.CRITICAL] or
                    impl.timeframe == TimeHorizon.IMMEDIATE or
                    impl.stakeholder_relevance > 0.8):
                priority_implications.append(impl.implication_id)

        return priority_implications

    def _assess_communication_urgency(self, implications: List[StrategicImplication]) -> UrgencyLevel:
        """Assess communication urgency based on implications"""
        max_urgency = UrgencyLevel.LOW

        for impl in implications:
            impl_urgency = impl.get_urgency_level()
            if impl_urgency == UrgencyLevel.URGENT:
                return UrgencyLevel.URGENT
            elif impl_urgency == UrgencyLevel.HIGH and max_urgency != UrgencyLevel.URGENT:
                max_urgency = UrgencyLevel.HIGH
            elif impl_urgency == UrgencyLevel.MEDIUM and max_urgency == UrgencyLevel.LOW:
                max_urgency = UrgencyLevel.MEDIUM

        return max_urgency

    def _prepare_synthesis_input(self, kiq_insights: List, kit_insights: List, patterns: List) -> str:
        """Prepare all insights for synthesis"""
        sections = []

        if kiq_insights:
            kiq_section = "KIQ Insights:\n"
            for insight in kiq_insights[:10]:
                if hasattr(insight, 'insight'):
                    kiq_section += f"- {insight.kiq_id}: {insight.insight[:200]}...\n"
            sections.append(kiq_section)

        if kit_insights:
            kit_section = "KIT Insights:\n"
            for insight in kit_insights:
                if hasattr(insight, 'strategic_implications'):
                    kit_section += f"- {insight.kit_id}: {insight.strategic_implications[:200]}...\n"
            sections.append(kit_section)

        if patterns:
            pattern_section = "Cross-KIT Patterns:\n"
            for pattern in patterns:
                if hasattr(pattern, 'pattern_description'):
                    pattern_section += f"- {pattern.pattern_description[:200]}...\n"
            sections.append(pattern_section)

        return "\n\n".join(sections)

    # Health check and monitoring methods

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on Bedrock connection"""
        try:
            # Simple test request to verify connectivity
            test_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 10,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": "Say 'OK'"
                    }
                ]
            }

            response = await self._invoke_bedrock_with_retry(test_body)

            if response:
                return {
                    "status": "healthy",
                    "model_id": self.model_id,
                    "region": getattr(settings, 'AWS_REGION', 'us-east-1'),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Failed to get response from Bedrock",
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the configured model"""
        return {
            "model_id": self.model_id,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "region": getattr(settings, 'AWS_REGION', 'us-east-1')
        }