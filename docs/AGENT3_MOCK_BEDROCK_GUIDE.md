# Agent 3 Mock Bedrock Guide

This guide explains how to use the mock Bedrock functionality in Agent 3 Insights to bypass AWS Bedrock API issues and use realistic mock data instead.

## Overview

The mock Bedrock functionality provides:
- ✅ Realistic pharmaceutical market insights
- ✅ Context-aware content analysis
- ✅ Proper data structure matching real API responses
- ✅ No AWS credentials required
- ✅ Fast response times for testing/development

## Usage Methods

### Method 1: Environment Variable

Set the environment variable to enable mock mode globally:

```bash
export BEDROCK_MOCK_MODE=true
```

Then use Agent 3 normally:

```python
from app.agent_service_module.agents.agent3_insights.service import Agent3InsightsService
from app.agent_service_module.agents.agent3_insights.models import Agent3InsightsRequest

service = Agent3InsightsService()

request = Agent3InsightsRequest(
    request_id="test_001",
    content="Your pharmaceutical content here...",
    api_provider="aws_bedrock"  # Will use mock due to env var
)

response = await service.process(request)
```

### Method 2: Explicit Mock Provider

Use the explicit mock provider in your request:

```python
request = Agent3InsightsRequest(
    request_id="test_002",
    content="Your content...",
    api_provider="aws_bedrock_mock"  # Explicit mock mode
)

response = await service.process(request)
```

### Method 3: S3 Processing with Mock Config

For S3-based processing, use the config parameter:

```python
config = {
    "use_mock_bedrock": True,
    "analysis_type": "market_intelligence"
}

result = await service.process_from_s3(
    request_id="test_003",
    s3_path="s3://bucket/content.json",
    output_table="insights_table",
    config=config
)
```

## Mock Data Features

The mock system provides realistic insights based on content analysis:

### Content-Aware Analysis
- Detects pharmaceutical keywords (semaglutide, ozempic, wegovy, etc.)
- Adjusts context based on detected themes
- Provides relevant market insights

### Structured Output
- **Market Insights**: 3 detailed insights with categories, confidence scores
- **Key Themes**: Extracted from content keywords
- **Strategic Recommendations**: 3 actionable recommendations
- **Risk Factors**: 3 identified risks with mitigation strategies

### Example Output Structure

```json
{
  "market_insights": [
    {
      "insight": "The GLP-1 receptor agonist market shows significant growth potential...",
      "category": "market_trend",
      "confidence_score": 0.85,
      "impact_level": "high",
      "time_horizon": "medium_term",
      "supporting_evidence": ["Market projections...", "Regulatory environment..."]
    }
  ],
  "key_themes": ["diabetes/obesity treatment", "market analysis"],
  "strategic_recommendations": [...],
  "risk_factors": [...]
}
```

## Testing

Run the comprehensive test suite:

```bash
python3 test_agent3_bedrock_mock.py
```

Or run the example:

```bash
python3 examples/agent3_mock_bedrock_example.py
```

## Benefits

1. **No AWS Setup Required**: Bypass AWS credential and configuration issues
2. **Fast Development**: Instant responses without API latency
3. **Realistic Data**: Content-aware mock insights for testing
4. **Cost Effective**: No API charges during development/testing
5. **Reliable**: No network dependencies or API rate limits

## When to Use Mock Mode

- ✅ Development and testing
- ✅ CI/CD pipelines
- ✅ Demos and presentations
- ✅ When AWS Bedrock is unavailable
- ✅ Cost-conscious development

## Switching Back to Real API

To use the real AWS Bedrock API:

1. Remove or set `BEDROCK_MOCK_MODE=false`
2. Use `api_provider="aws_bedrock"` (not `aws_bedrock_mock`)
3. Remove `use_mock_bedrock` from config
4. Ensure AWS credentials are properly configured

## Mock vs Real API Comparison

| Feature | Mock Mode | Real API |
|---------|-----------|----------|
| Setup | No credentials needed | AWS credentials required |
| Speed | ~500ms | 2-5 seconds |
| Cost | Free | Per-token charges |
| Reliability | 100% uptime | Depends on AWS |
| Data Quality | Realistic templates | AI-generated insights |
| Customization | Keyword-based | Full AI analysis |

The mock mode is perfect for development, testing, and situations where you need reliable, fast responses without the complexity of AWS setup. 