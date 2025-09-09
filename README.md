# FastAPI Agent Service

A modern, scalable FastAPI microservice with DynamoDB integration, following clean architecture principles.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **DynamoDB Integration**: NoSQL database with boto3 client
- **Layered Architecture**: Clear separation between routes, controllers, services, and repositories
- **Pydantic Validation**: Request/response validation and serialization
- **Modular Design**: Three core modules (project, request, content_repository)
- **Async Support**: Full asynchronous request handling
- **Auto Documentation**: OpenAPI/Swagger documentation
- **Health Checks**: Built-in health monitoring endpoints
- **Logging**: Comprehensive logging with middleware
- **CORS Support**: Configurable CORS middleware

## Architecture

The service follows a clean architecture pattern with the following layers:

```
┌─────────────────┐
│     Routes      │ ← HTTP endpoints and routing
├─────────────────┤
│   Controllers   │ ← Request/Response handling
├─────────────────┤
│    Services     │ ← Business logic
├─────────────────┤
│  Repositories   │ ← Data access layer
├─────────────────┤
│    Database     │ ← DynamoDB connection
└─────────────────┘
```

## Project Structure

```
app/
├── __init__.py
├── main.py                     # FastAPI application entry point
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuration settings
├── core/
│   ├── __init__.py
│   ├── database.py             # Database connection
│   ├── exceptions.py           # Custom exceptions
│   └── logging.py              # Logging configuration
├── models/
│   ├── __init__.py
│   ├── base_model.py           # Base model class
│   ├── project_model.py        # Project data model
│   ├── request_model.py        # Request data model
│   └── content_repository_model.py
├── schemas/
│   ├── __init__.py
│   ├── base_schema.py          # Base Pydantic schemas
│   ├── project_schema.py       # Project request/response schemas
│   ├── request_schema.py       # Request schemas
│   └── content_repository_schema.py
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py      # Base repository class
│   ├── project_repository.py   # Project data access
│   ├── request_repository.py   # Request data access
│   └── content_repository_repository.py
├── services/
│   ├── __init__.py
│   ├── base_service.py         # Base service class
│   ├── project_service.py      # Project business logic
│   ├── request_service.py      # Request business logic
│   └── content_repository_service.py
├── controllers/
│   ├── __init__.py
│   ├── base_controller.py      # Base controller class
│   ├── project_controller.py   # Project API handlers
│   ├── request_controller.py   # Request API handlers
│   └── content_repository_controller.py
├── routes/
│   ├── __init__.py
│   ├── project_routes.py       # Project endpoints
│   ├── request_routes.py       # Request endpoints
│   └── content_repository_routes.py
├── middleware/
│   ├── __init__.py
│   ├── cors_middleware.py      # CORS configuration
│   └── logging_middleware.py   # Request logging
└── utils/
    ├── __init__.py
    └── helpers.py              # Utility functions
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nex-pharma-insights-agent-service-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

## Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

```env
# Application Settings
APP_NAME=Agent Service
APP_VERSION=1.0.0
DEBUG=false

# API Settings
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# AWS DynamoDB Settings
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
DYNAMODB_ENDPOINT_URL=http://localhost:8000  # For local DynamoDB

# Table Names
PROJECTS_TABLE=projects
REQUESTS_TABLE=requests
CONTENT_REPOSITORY_TABLE=content_repository

# Logging
LOG_LEVEL=INFO
```

## Running the Application

### Development Mode

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

### Projects
- `GET /api/v1/projects/` - Get all projects (with pagination)
- `GET /api/v1/projects/{project_id}` - Get project by ID
- `POST /api/v1/projects/` - Create new project
- `PUT /api/v1/projects/{project_id}` - Update project
- `DELETE /api/v1/projects/{project_id}` - Delete project
- `GET /api/v1/projects/owner/{owner_id}` - Get projects by owner
- `GET /api/v1/projects/search/?q={query}` - Search projects

## Example Usage

### Create a Project

```bash
curl -X POST "http://localhost:8000/api/v1/projects/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "My Project",
       "description": "A sample project",
       "owner_id": "user123",
       "tags": ["sample", "test"],
       "metadata": {"priority": "high"}
     }'
```

### Get All Projects

```bash
curl "http://localhost:8000/api/v1/projects/?page=1&page_size=10"
```

### Search Projects

```bash
curl "http://localhost:8000/api/v1/projects/search/?q=sample"
```

## Database Setup

### Local DynamoDB

For development, you can use DynamoDB Local:

```bash
# Download and run DynamoDB Local
docker run -p 8000:8000 amazon/dynamodb-local

# Create tables (you'll need to implement table creation scripts)
```

### AWS DynamoDB

For production, configure your AWS credentials and ensure the tables exist:

- `projects`
- `requests`
- `content_repository`

## Development

### Adding New Modules

To add a new module (e.g., `users`):

1. Create model in `app/models/user_model.py`
2. Create schemas in `app/schemas/user_schema.py`
3. Create repository in `app/repositories/user_repository.py`
4. Create service in `app/services/user_service.py`
5. Create controller in `app/controllers/user_controller.py`
6. Create routes in `app/routes/user_routes.py`
7. Include router in `app/main.py`

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to all classes and methods
- Keep functions focused and small
- Use meaningful variable names

## Testing

```bash
# Run tests (implement test suite)
pytest

# Run with coverage
pytest --cov=app
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  agent-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AWS_REGION=us-east-1
    volumes:
      - .env:/app/.env
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team. 