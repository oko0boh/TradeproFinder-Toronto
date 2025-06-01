"""
Production configuration for Tradepro Finder Toronto.
"""

import os
from .base import BaseConfig

class ProductionConfig(BaseConfig):
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Security
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # CSRF protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SSL_STRICT = True
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_POOL_TIMEOUT = 30
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
    CACHE_DEFAULT_TIMEOUT = 3600
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL')
    
    # Mail
    MAIL_SERVER = os.getenv('SMTP_SERVER')
    MAIL_PORT = int(os.getenv('SMTP_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('SMTP_USERNAME')
    MAIL_PASSWORD = os.getenv('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('ADMIN_EMAIL')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/app.log'  # Use relative path in the app directory
    LOG_MAX_SIZE = 10485760  # 10MB
    LOG_BACKUPS = 5
    
    # API
    GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
    API_TIMEOUT = 30
    MAX_RETRIES = 3
    
    # CORS
    CORS_ORIGINS = [
        'https://tradeprofindertoronto.com',
        'https://www.tradeprofindertoronto.com'
    ]
    
    # File uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = '/var/www/tradepro-finder/uploads'
    
    # Sentry error tracking
    SENTRY_DSN = os.getenv('SENTRY_DSN')
