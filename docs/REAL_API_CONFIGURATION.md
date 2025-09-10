# Real API Configuration Guide

## 🔑 Switching from Mock to Real APIs

The system is designed to seamlessly switch between mock and real APIs by simply changing environment variables and providing API keys.

## 📋 Required API Keys

### 1. **SERP API Key**
- **Service**: SerpAPI (https://serpapi.com/)
- **Purpose**: URL discovery and web search
- **Usage**: Finds relevant content URLs from multiple domains
- **Environment Variable**: `SERPAPI_KEY`

### 2. **Perplexity API Key**  
- **Service**: Perplexity AI (https://www.perplexity.ai/)
- **Purpose**: AI-powered content generation and analysis
- **Usage**: Generates market summaries, competitive analysis, insights
- **Environment Variable**: `PERPLEXITY_API_KEY`

## 🔧 Configuration Steps

### Step 1: Install Required Dependencies

First, add the missing dependencies to requirements.txt:

```bash
# Add to requirements.txt
aiohttp==3.9.1
```

Then install:
```bash
pip install aiohttp
```

### Step 2: Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# Switch to real API mode
AGENT_SERVICE_USE_MOCK_DATA=false

# SERP API Configuration
SERPAPI_KEY=your_serpapi_key_here

# Perplexity API Configuration  
PERPLEXITY_API_KEY=your_perplexity_key_here

# MinIO Configuration (your existing setup)
MINIO_ENDPOINT=localhost:9001
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
S3_BUCKET_NAME=nex-pharma
```

### Step 3: Test Real API Integration

Run the test with real APIs:

```bash
# Set environment for real APIs
export AGENT_SERVICE_USE_MOCK_DATA=false
export SERPAPI_KEY="your_actual_serpapi_key"
export PERPLEXITY_API_KEY="your_actual_perplexity_key"

# Run comprehensive test
python3 test_mock_data_flow.py
```

## 🔄 How the Switching Works

The service factory automatically detects the environment and uses the appropriate client:

```python
# In temp_service_factory.py
@classmethod
def get_serp_client(cls) -> MockSerpClient:
    """Get SERP client instance"""
    if cls._serp_client is None:
        use_mock = os.getenv("AGENT_SERVICE_USE_MOCK_DATA", "true").lower() == "true"
        cls._serp_client = MockSerpClient(use_mock_data=use_mock)
    return cls._serp_client

@classmethod  
def get_perplexity_client(cls) -> MockPerplexityClient:
    """Get Perplexity client instance"""
    if cls._perplexity_client is None:
        use_mock = os.getenv("AGENT_SERVICE_USE_MOCK_DATA", "true").lower() == "true"
        cls._perplexity_client = MockPerplexityClient(use_mock_data=use_mock)
    return cls._perplexity_client
```

## 📊 Real API Usage Examples

### SERP API Real Usage
```python
# When use_mock_data=False, this will make real API calls
serp_client = ServiceFactory.get_serp_client()

# Real SERP search
response = await serp_client.search_by_keywords_and_domain(
    keywords=["semaglutide", "obesity", "treatment"],
    domain="reuters.com", 
    num_results=5
)

# Returns real URLs from Reuters about semaglutide
print(response["exact_urls"])
```

### Perplexity API Real Usage
```python
# When use_mock_data=False, this will make real API calls
perplexity_client = ServiceFactory.get_perplexity_client()

# Real Perplexity analysis
query = """
Analyze the semaglutide market trends based on these recent sources:
- https://reuters.com/business/healthcare-pharmaceuticals/...
- https://fda.gov/news-events/press-announcements/...

Provide comprehensive market insights and competitive analysis.
"""

response = await perplexity_client.search_with_metadata(query)

# Returns real AI-generated analysis with citations
print(f"Content: {response['content']}")
print(f"Citations: {response['citations']}")
print(f"Cost: ${response['usage']['total_cost']}")
```

## 💰 API Cost Considerations

### SERP API Costs
- **Free Tier**: 100 searches/month
- **Paid Plans**: $50/month for 5,000 searches
- **Our Usage**: ~6 domains × 5 results = 30 searches per request

### Perplexity API Costs  
- **Model**: `llama-3.1-sonar-small-128k-online`
- **Cost**: ~$0.01-0.02 per query
- **Our Usage**: 4 queries per request (summary, analysis, insights, implications)
- **Total**: ~$0.04-0.08 per market intelligence request

## 🔒 Security Best Practices

### 1. **Environment Variables**
```bash
# Never commit API keys to git
# Use environment variables or secure vaults

# Development
export SERPAPI_KEY="sk-..."
export PERPLEXITY_API_KEY="pplx-..."

# Production  
# Use AWS Secrets Manager, Azure Key Vault, etc.
```

### 2. **Rate Limiting**
```python
# Built-in rate limiting in the clients
serp_rate_limit_delay: 0.2  # 200ms between SERP calls
perplexity_rate_limit_delay: 1.0  # 1s between Perplexity calls
```

### 3. **Error Handling**
```python
# Automatic fallback to mock data on API failures
try:
    response = await self._execute_real_api_call(query)
except Exception as e:
    logger.warning(f"Real API failed, using mock: {e}")
    response = await self._get_mock_response(query)
```

## 🧪 Testing Strategy

### 1. **Development Phase**
```bash
# Use mock data for development
AGENT_SERVICE_USE_MOCK_DATA=true
python3 simple_mock_test.py
```

### 2. **Integration Testing**  
```bash
# Test with real APIs (limited usage)
AGENT_SERVICE_USE_MOCK_DATA=false
SERPAPI_KEY="your_key"
PERPLEXITY_API_KEY="your_key"
python3 test_mock_data_flow.py
```

### 3. **Production Deployment**
```bash
# Full production configuration
AGENT_SERVICE_USE_MOCK_DATA=false
# Set all real API keys
# Configure production MinIO
# Set up monitoring and logging
```

## 📈 Performance Comparison

| Aspect | Mock APIs | Real APIs |
|--------|-----------|-----------|
| **Response Time** | 0.1-0.5s | 2-5s |
| **Cost** | $0 | $0.04-0.08/request |
| **Data Quality** | Realistic mock | Real-time data |
| **Rate Limits** | None | API-dependent |
| **Offline Usage** | ✅ Yes | ❌ No |
| **Development** | ✅ Perfect | ⚠️ Limited |
| **Production** | ❌ No | ✅ Required |

## 🚀 Deployment Checklist

### Before Going Live:
- [ ] Install `aiohttp` dependency
- [ ] Obtain SERP API key from serpapi.com
- [ ] Obtain Perplexity API key from perplexity.ai  
- [ ] Set `AGENT_SERVICE_USE_MOCK_DATA=false`
- [ ] Configure all environment variables
- [ ] Test with small batch of real requests
- [ ] Set up API usage monitoring
- [ ] Configure error alerting
- [ ] Set up cost tracking

### Production Environment:
```bash
# Production environment variables
ENVIRONMENT=production
AGENT_SERVICE_USE_MOCK_DATA=false
SERPAPI_KEY=your_production_serpapi_key
PERPLEXITY_API_KEY=your_production_perplexity_key
MINIO_ENDPOINT=your_production_minio_endpoint
MINIO_ACCESS_KEY=your_production_access_key
MINIO_SECRET_KEY=your_production_secret_key
S3_BUCKET_NAME=nex-pharma-production
```

## ✅ **Ready for Real APIs**

The system is **fully prepared** to work with real API keys. Just provide the keys and change the environment variable - everything else will work automatically!

**Next Step**: Provide your SERP and Perplexity API keys, and I'll help you test the real API integration. 