# 🔑 Production API Configuration

## Production API Setup

The system uses real API implementations for production deployment. Configure the following environment variables for production use.

### Required Environment Variables

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Perplexity Configuration  
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# SERP API Configuration
SERP_API_KEY=your_serpapi_key_here

# AWS/Bedrock Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# Storage Configuration
STORAGE_TYPE=s3  # or "minio" for local development
S3_BUCKET_NAME=your-production-bucket-name

# Database Configuration  
DYNAMODB_REGION=us-east-1
# Leave DYNAMODB_ENDPOINT empty for production AWS DynamoDB
```

### Development Environment Variables

For local development with MinIO:

```bash
# Storage Configuration for Development
STORAGE_TYPE=minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Database Configuration for Development
DYNAMODB_ENDPOINT=http://localhost:8000  # Local DynamoDB
```

### Service Factory Configuration

The service factory automatically provides real implementations:

```python
from app.agent_service_module.config.service_factory import ServiceFactory

# All methods return real API clients
openai_client = ServiceFactory.get_openai_client()
bedrock_client = ServiceFactory.get_bedrock_client()
perplexity_client = ServiceFactory.get_perplexity_client()
serp_client = ServiceFactory.get_serp_client()
storage_client = ServiceFactory.get_storage_client()
database_client = ServiceFactory.get_database_client()
```

### Testing Production APIs

```python
# Test real API endpoints
python3 test_root_orchestrator_api.py
```

### Production Deployment Checklist

- [ ] Set all required API keys
- [ ] Configure AWS credentials
- [ ] Set up production S3 bucket
- [ ] Configure production DynamoDB tables
- [ ] Test all API endpoints
- [ ] Monitor API usage and costs

### API Cost Monitoring

Monitor usage for:
- OpenAI API calls
- Perplexity API calls  
- SERP API calls
- AWS Bedrock calls
- AWS S3 storage
- AWS DynamoDB operations

### Error Handling

All services include proper error handling and logging. Check logs for API failures and rate limiting issues.

### Security Best Practices

- Store API keys in environment variables or secure key management
- Use IAM roles for AWS services when possible
- Rotate API keys regularly
- Monitor API usage for anomalies
- Set up billing alerts for cost control 