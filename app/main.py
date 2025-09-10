from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config.unified_settings import settings
from app.core.logging import setup_logging
from app.core.database import db_connection
from app.middleware.cors_middleware import setup_cors
from app.middleware.logging_middleware import LoggingMiddleware
from app.routes.project_routes import router as project_router
from app.routes.market_intelligence_routes import router as market_intelligence_router
# Import other route modules here
# from app.routes.request_routes import router as request_router
# from app.routes.content_repository_routes import router as content_repository_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Agent Service...")
    
    # Setup logging
    setup_logging()
    
    # Check database connection
    if not db_connection.health_check():
        logger.error("Failed to connect to DynamoDB")
        raise Exception("Database connection failed")
    
    logger.info("Agent Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Agent Service...")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url=settings.DOCS_URL,
    redoc_url=settings.REDOC_URL
)

# Setup middleware
setup_cors(app)
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(project_router, prefix=settings.API_V1_PREFIX)
app.include_router(market_intelligence_router)
# app.include_router(request_router, prefix=settings.api_prefix)
# app.include_router(content_repository_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_healthy = db_connection.health_check()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected",
        "version": settings.VERSION
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 