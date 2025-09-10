import logging
import sys
from typing import Optional
from ...config.settings import settings

class Logger:
    """Simple logger class wrapper"""
    
    @staticmethod
    def get_logger(name: Optional[str] = None) -> logging.Logger:
        """Get configured logger instance"""
        return get_logger(name)
    
    @staticmethod
    def info(message: str):
        """Log info message"""
        logger = get_logger()
        logger.info(message)
    
    @staticmethod
    def error(message: str):
        """Log error message"""
        logger = get_logger()
        logger.error(message)
    
    @staticmethod
    def warning(message: str):
        """Log warning message"""
        logger = get_logger()
        logger.warning(message)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get configured logger instance"""
    logger = logging.getLogger(name or __name__)
    
    if not logger.handlers:
        # Configure handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Set format
        if settings.ENVIRONMENT == "prod":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set level
        if settings.ENVIRONMENT == "prod":
            logger.setLevel(logging.WARNING)
        else:
            logger.setLevel(logging.INFO)
    
    return logger 