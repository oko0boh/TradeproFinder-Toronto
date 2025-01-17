"""
Development configuration.
"""

from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    
    DEBUG = True
    DEVELOPMENT = True
    
    # Security
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    
    # Cache
    CACHE_TYPE = 'simple'
    
    # Mail
    MAIL_DEBUG = True
    
    # CORS
    CORS_ORIGINS = ['http://localhost:5000']
