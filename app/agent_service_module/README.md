# Agent Service Module

A modular agent service system with environment-based configuration and factory pattern for seamless switching between real and mock implementations.

## 🏗️ Architecture

```
agent_service_module/
├── config/                 # Configuration management
│   ├── settings.py         # Main configuration
│   ├── environments.py     # Environment-specific configs
│   ├── service_factory.py  # Service factory for DI
│   └── mock_factory.py     # Mock service factory
├── agents/                 # Agent implementations
│   ├── stage0_serp/        # SERP search agent
│   ├── stage0_perplexity/  # Perplexity search agent
│   ├── stage0_orchestrator/# Orchestration agent
│   ├── agent1_deduplication/# Content deduplication
│   ├── agent2_relevance/   # Relevance scoring
│   ├── agent3_insights/    # Insight generation
│   └── agent4_implications/# Impact analysis
├── shared/                 # Shared components
│   ├── database/           # Database clients & mocks
│   ├── storage/            # Storage clients & mocks
│   ├── models/             # Common data models
│   └── utils/              # Utilities & exceptions
└── environments/           # Environment configs
    ├── .env.local          # Local development
    ├── .env.dev            # Development
    ├── .env.staging        # Staging
    ├── .env.prod           # Production
    └── .env.mock           # Testing/Mock
```

## 🚀 Key Features

### 1. **Environment-Based Configuration**
- Single environment variable controls entire system behavior
- Seamless switching between local/dev/staging/prod/mock
- No code changes required for environment switching

### 2. **Factory Pattern Implementation**
- Automatic injection of real/mock implementations
- Clean separation of concerns
- Easy testing and development

### 3. **Modular Agent Architecture**
- Each agent is completely self-contained
- Consistent API across all agents
- Easy to add new agents or modify existing ones

### 4. **Complete API Abstraction**
- Real and mock implementations for every external service
- Consistent interfaces across all implementations
- Perfect for testing and development

## 🛠️ Usage

### Environment Switching

```bash
# Local development with real APIs
export ENVIRONMENT=local
python main.py

# Mock everything for testing
export ENVIRONMENT=mock
python main.py

# Production deployment
export ENVIRONMENT=prod
python main.py
```

### Using Agents in Code

```python
from app.agent_service_module.agents.agent1_deduplication.service import Agent1DeduplicationService
from app.agent_service_module.agents.agent1_deduplication.models import Agent1DeduplicationRequest

# Create service (automatically uses correct implementation based on environment)
service = Agent1DeduplicationService()

# Create request
request = Agent1DeduplicationRequest(
    request_id="example-001",
    content="Content to process"
)

# Process (uses real or mock APIs based on environment)
response = await service.process(request)
```

### Configuration Management

```python
from app.agent_service_module.config.settings import settings

# Access configuration
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Using mocks: {settings.USE_MOCK_APIS}")
print(f"Storage type: {settings.STORAGE_TYPE}")
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Values |
|----------|-------------|---------|
| `ENVIRONMENT` | Current environment | `local`, `dev`, `staging`, `prod`, `mock` |
| `USE_MOCK_APIS` | Use mock API implementations | `true`, `false` |
| `USE_MOCK_STORAGE` | Use mock storage | `true`, `false` |
| `USE_MOCK_DATABASE` | Use mock database | `true`, `false` |

### API Configuration

```env
# API Keys
OPENAI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
SERP_API_KEY=your_key_here

# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
```

### Storage Configuration

```env
# Storage Type
STORAGE_TYPE=minio  # or 's3'

# Minio (Local)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# S3 (Production)
S3_BUCKET_NAME=agent-content-bucket
```

## 🧪 Testing

The system includes comprehensive mock implementations for all external services:

```python
# Set mock environment
import os
os.environ['ENVIRONMENT'] = 'mock'

# All services now use mocks automatically
service = Agent1DeduplicationService()
response = await service.process(request)  # Uses mocks
```

## 📦 Agent Structure

Each agent follows a consistent structure:

```
agent_name/
├── __init__.py
├── models.py              # Request/Response models
├── service.py             # Main service logic
├── *_api.py              # Real API implementations
├── *_mock.py             # Mock API implementations
├── *_response.py         # Response models
├── storage.py            # Storage operations
├── database.py           # Database operations
└── [specialized files]   # Agent-specific components
```

## 🔄 Adding New Agents

1. Create agent directory under `agents/`
2. Implement required files following the pattern
3. Add factory methods in `service_factory.py` and `mock_factory.py`
4. Update `agents/__init__.py` to export the service

## 🌍 Environment Configurations

### Local Development
- Uses local Minio for storage
- Uses local DynamoDB
- Real API calls (with your keys)

### Mock/Testing
- All services mocked
- No external dependencies
- Perfect for CI/CD and testing

### Production
- Uses AWS S3 for storage
- Uses AWS DynamoDB
- Real API calls with production keys

## 🚦 Getting Started

1. **Set up environment:**
   ```bash
   export ENVIRONMENT=local
   ```

2. **Configure API keys in environment file:**
   ```bash
   cp app/agent_service_module/environments/.env.local .env.local
   # Edit .env.local with your API keys
   ```

3. **Run example:**
   ```bash
   python app/agent_service_module/example_usage.py
   ```

## 🎯 Benefits

- **Single Point of Change**: Switch entire system with one variable
- **No Code Changes**: Same code works in all environments
- **Easy Testing**: Mock everything with one setting
- **Gradual Migration**: Can mock specific services while keeping others real
- **Environment Isolation**: Clear separation between environments
- **Secret Management**: Environment-specific secrets
- **Dependency Injection**: Clean separation of concerns

This architecture provides maximum flexibility with minimal code changes when switching between environments! 