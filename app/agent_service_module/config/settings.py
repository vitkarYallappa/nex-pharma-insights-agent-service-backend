"""
DEPRECATED: This settings file has been replaced by unified_settings.py

This file is kept for backward compatibility but now imports from the unified settings.
All new code should import from app.config.unified_settings directly.
"""

# Import from unified settings for backward compatibility
from ...config.unified_settings import settings

# Re-export the settings instance
__all__ = ['settings'] 