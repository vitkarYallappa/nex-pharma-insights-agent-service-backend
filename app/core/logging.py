import logging
import logging.handlers
import sys
import os
from app.config.unified_settings import settings


def setup_logging():
    """Setup application logging configuration."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Create file handler
    log_file_path = settings.log_file_path
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path,
        maxBytes=settings.LOG_MAX_SIZE,
        backupCount=settings.LOG_BACKUP_COUNT
    )
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    
    # Add both handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure specific loggers
    loggers = [
        'app',
        'uvicorn',
        'fastapi'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Log that logging is configured
    logging.info(f"Logging configured - Console: YES, File: {log_file_path}")
    logging.info(f"Log level: {settings.LOG_LEVEL}")
    
    return log_file_path 