"""
Testing configuration.
"""

from .base import BaseConfig

class TestingConfig(BaseConfig):
    """Testing configuration."""
    
    TESTING = True
    DEBUG = False
    
    # Security
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    
    # Cache
    CACHE_TYPE = 'simple'
    
    # Mail
    MAIL_SUPPRESS_SEND = True
