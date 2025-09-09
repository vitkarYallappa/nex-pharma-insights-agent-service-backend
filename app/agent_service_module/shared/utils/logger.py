import logging
import sys
from typing import Optional
from ...config.settings import settings

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