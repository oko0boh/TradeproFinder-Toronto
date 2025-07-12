"""
Flask application for Tradepro Finder Toronto.
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, request, redirect
from flask_cors import CORS
from flask_seasurf import SeaSurf
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
from routes import main as main_blueprint
from local_cache import LocalCache
from api_monitor import APIMonitor
from database_manager import DatabaseManager
from init_db import init_service_providers_db, init_search_cache_db
from security import init_security
from error_handlers import init_error_handling
from rollback_manager import RollbackManager
from logging.handlers import RotatingFileHandler
import sqlite3
# Import Google Places API and Search Service
from google_places_api import GooglePlacesAPI
from search_service import SearchService

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler('logs/app.log')  # Log to file
    ]
)

# Configure logger
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('logs/app.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s'
))
logger.addHandler(file_handler)

# Database initialization functions
def init_service_providers_db():
    """Initialize the service providers database."""
    conn = None
    try:
        conn = sqlite3.connect('service_providers.db')
        cursor = conn.cursor()
        
        # Create service providers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS service_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                location TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                website TEXT,
                description TEXT,
                rating REAL,
                reviews INTEGER,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Create quote requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quote_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                service TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL
            )
        ''')
        
        # Create professional registrations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS professional_registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                phone TEXT NOT NULL,
                company TEXT NOT NULL,
                service TEXT NOT NULL,
                location TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Service providers database initialized successfully")
    except Exception as e:
        print(f"Error initializing service providers database: {str(e)}")
        if conn:
            conn.close()
        raise e

def init_search_cache_db():
    """Initialize the search cache database."""
    conn = None
    try:
        conn = sqlite3.connect('data/search_cache.db')
        cursor = conn.cursor()
        
        # Create search cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                location TEXT NOT NULL,
                results TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                UNIQUE(service, location)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Search cache database initialized successfully")
    except Exception as e:
        print(f"Error initializing search cache database: {str(e)}")
        if conn:
            conn.close()
        raise e

class SQLiteDatabase:
    """SQLite database wrapper."""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
        
    def execute(self, query, params=()):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor
        
    def query_all(self, query, params=()):
        cursor = self.execute(query, params)
        return cursor.fetchall()
        
    def query_one(self, query, params=()):
        cursor = self.execute(query, params)
        return cursor.fetchone()
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

def create_app(config_name='development'):
    """Create Flask application."""
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize databases
    init_service_providers_db()
    init_search_cache_db()
    
    # Initialize extensions
    init_security(app)
    init_error_handling(app)
    
    # Initialize CORS
    CORS(app, resources={
        r"/*": {"origins": app.config['CORS_ORIGINS']}
    })
    
    # Initialize database
    db = DatabaseManager()
    
    # Initialize cache
    cache = LocalCache()
    
    # Initialize API monitor
    api_monitor = APIMonitor()
    
    # Initialize Google Places API and search service
    google_api_key = os.environ.get('GOOGLE_PLACES_API_KEY')
    app.google_places = GooglePlacesAPI(api_key=google_api_key)
    app.search_service = SearchService(db_manager=db, api_key=google_api_key)
    
    # Register blueprint
    app.register_blueprint(main_blueprint)

    @app.before_request
    def before_request():
        """Pre-request processing."""
        # Railway handles HTTPS at the proxy level, so we don't need to redirect
        # This prevents redirect loops
        pass
    
    @app.after_request
    def after_request(response):
        """Post-request processing."""
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    # Initialize databases within app context
    with app.app_context():
        try:
            init_service_providers_db()
            init_search_cache_db()
        except Exception as e:
            logger.error(f"Error initializing databases: {str(e)}")

    return app

# For local development
if __name__ == '__main__':
    try:
        app = create_app('development')
        port = int(os.environ.get('PORT', 5000))
        app.run(host='127.0.0.1', port=port, debug=True)
            
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        raise
