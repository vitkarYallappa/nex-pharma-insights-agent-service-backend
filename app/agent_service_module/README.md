# Agent Service Module

A modular agent service system with production-ready configuration and service factory pattern for real API implementations.

## 📁 Project Structure

```
agent_service_module/
├── agents/                 # Individual agent implementations
│   ├── agent1_deduplication/
│   ├── agent2_relevance/
│   ├── agent3_insights/
│   ├── agent4_implications/
│   ├── stage0_orchestrator/
│   ├── stage0_perplexity/
│   └── stage0_serp/
├── config/
│   ├── settings.py         # Environment configuration
│   └── service_factory.py  # Production service factory
├── shared/                 # Shared components
│   ├── database/           # Database clients
│   ├── storage/            # Storage clients
│   └── utils/              # Utilities
└── services/               # Core services
```

## 🚀 Quick Start

### Environment Setup

Create a `.env` file with your configuration:

```bash
# API Keys
OPENAI_API_KEY=your_openai_key
PERPLEXITY_API_KEY=your_perplexity_key
SERP_API_KEY=your_serp_key

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Storage (MinIO for development, S3 for production)
STORAGE_TYPE=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Database
DYNAMODB_ENDPOINT=http://localhost:8000  # Local DynamoDB
```

### Basic Usage

```python
from app.agent_service_module.config.service_factory import ServiceFactory

# Get service instances
perplexity = ServiceFactory.get_perplexity_client()
serp = ServiceFactory.get_serp_client()
storage = ServiceFactory.get_storage_client()

# Process market intelligence request
response = await perplexity.search("semaglutide market analysis")
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `PERPLEXITY_API_KEY` | Perplexity API key | `pplx-...` |
| `SERP_API_KEY` | SERP API key | `your_key` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `STORAGE_TYPE` | Storage backend | `minio`, `s3` |
| `DYNAMODB_ENDPOINT` | DynamoDB endpoint | `http://localhost:8000` |

### Service Factory

The service factory provides production-ready implementations:

```python
from app.agent_service_module.config.service_factory import ServiceFactory

# All services use real API implementations
openai_client = ServiceFactory.get_openai_client()
bedrock_client = ServiceFactory.get_bedrock_client()
perplexity_client = ServiceFactory.get_perplexity_client()
serp_client = ServiceFactory.get_serp_client()
storage_client = ServiceFactory.get_storage_client()
database_client = ServiceFactory.get_database_client()
```

## 🏗️ Architecture

### Agent System
- **Stage 0**: Data collection (SERP, Perplexity, Orchestrator)
- **Agent 1**: Deduplication and similarity analysis
- **Agent 2**: Relevance scoring and classification
- **Agent 3**: Insight generation and analysis
- **Agent 4**: Implications and impact assessment

### Shared Components
- **Database**: DynamoDB client with connection management
- **Storage**: S3/MinIO client with unified interface
- **Utils**: Logging, validation, text processing utilities

## 📊 Usage Examples

### Market Intelligence Workflow

```python
from app.agent_service_module.services.market_intelligence_service import MarketIntelligenceService

# Initialize service
service = MarketIntelligenceService()

# Process market intelligence request
request = {
    "query": "semaglutide market trends",
    "domains": ["reuters.com", "bloomberg.com", "fda.gov"],
    "analysis_depth": "comprehensive"
}

result = await service.process_request(request)
```

### Individual Agent Usage

```python
# Stage 0: URL Discovery
from app.agent_service_module.agents.stage0_serp.service import SerpService
serp_service = SerpService()
urls = await serp_service.discover_urls("semaglutide news")

# Stage 0: Content Extraction  
from app.agent_service_module.agents.stage0_perplexity.service import PerplexityService
perplexity_service = PerplexityService()
content = await perplexity_service.extract_content(urls)

# Agent 1: Deduplication
from app.agent_service_module.agents.agent1_deduplication.service import DeduplicationService
dedup_service = DeduplicationService()
unique_content = await dedup_service.deduplicate(content)
```

## 🔒 Security

### API Key Management
- Store API keys in environment variables
- Use secure key management services in production
- Rotate keys regularly
- Monitor API usage

### Access Control
- Configure IAM roles for AWS services
- Use least privilege principle
- Enable logging and monitoring
- Set up billing alerts

## 🚀 Deployment

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set up local services (MinIO, DynamoDB)
docker-compose up -d

# Run tests
python -m pytest tests/
```

### Production
```bash
# Set production environment variables
export STORAGE_TYPE=s3
export S3_BUCKET_NAME=your-production-bucket
# Remove DYNAMODB_ENDPOINT for AWS DynamoDB

# Deploy to your platform
# Configure monitoring and logging
# Set up auto-scaling
```

## 📈 Monitoring

### Metrics to Track
- API response times
- Error rates
- API costs
- Storage usage
- Database performance

### Logging
All services include structured logging with:
- Request/response tracking
- Error details
- Performance metrics
- Cost tracking

## 🧪 Testing

```bash
# Run unit tests
python -m pytest tests/unit/

# Run integration tests
python -m pytest tests/integration/

# Run end-to-end tests
python test_root_orchestrator_api.py
```

## 📚 Documentation

- [Agent Service Guide](../docs/agent_service.md)
- [API Configuration](../docs/REAL_API_CONFIGURATION.md)
- [DynamoDB Tables](../docs/DYNAMODB_TABLE_SPECIFICATIONS.md)
- [Root Orchestrator Guide](../docs/ROOT_ORCHESTRATOR_DEVELOPER_GUIDE.md)

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure production readiness
5. Test with real APIs before deployment 