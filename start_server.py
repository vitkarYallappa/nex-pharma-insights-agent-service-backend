#!/usr/bin/env python3
"""
FastAPI Agent Service Startup Script
"""

import uvicorn
from app.config.settings import settings

if __name__ == "__main__":
    print(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📍 Server: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 Docs: http://localhost:{settings.PORT}{settings.DOCS_URL}")
    print(f"🏥 Health: http://localhost:{settings.PORT}/health")
    print(f"🌍 Environment: {settings.ENVIRONMENT}")
    print()
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 