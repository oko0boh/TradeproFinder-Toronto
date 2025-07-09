"""
Flask application for Tradepro Finder Toronto.
"""

from flask import Flask, request, redirect
from flask_cors import CORS
import os
import sys
import logging
import sqlite3
from datetime import datetime

# Import the Blueprint
from routes import main as main_blueprint
from security import init_security
from error_handlers import init_error_handling
from database_manager import DatabaseManager
from local_cache import LocalCache
from api_monitor import APIMonitor
from config import config
from rollback_manager import RollbackManager
from logging.handlers import RotatingFileHandler

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
        conn = sqlite3.connect('data/service_providers.db')
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
    
    # Register blueprint
    app.register_blueprint(main_blueprint)

    @app.before_request
    def before_request():
        """Pre-request processing."""
        # Force HTTPS in production
        if not request.is_secure and app.config['ENV'] == 'production':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
    
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
