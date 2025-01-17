import sqlite3
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # Initialize all databases
        self.cache_results = SQLiteDatabase('local_cache.db')
        self.user_submissions = SQLiteDatabase('user_submissions.db')
        self.contact_requests = SQLiteDatabase('contact_requests.db')
        self.service_providers = SQLiteDatabase('service_providers.db')
        
        # Initialize all tables
        self._init_tables()
    
    def _init_tables(self):
        # Cache table
        self.cache_results.initialize_cache_database()
        
        # Users table
        self.user_submissions.execute('''
            CREATE TABLE IF NOT EXISTS user_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                name TEXT,
                message TEXT,
                service_type TEXT,
                location TEXT,
                submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Contacts table
        self.contact_requests.execute('''
            CREATE TABLE IF NOT EXISTS contact_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                name TEXT,
                message TEXT,
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Service providers table
        self.service_providers.execute('''
            CREATE TABLE IF NOT EXISTS service_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                business_name TEXT,
                contact_name TEXT,
                email TEXT,
                phone TEXT,
                service_types TEXT,
                locations TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

class SQLiteDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        logger.info(f"Initializing SQLite database: {db_path}")
    
    def execute(self, query, params=()):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
            conn.commit()
    
    def fetch_one(self, query, params=()):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()
    
    def fetch_all(self, query, params=()):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def insert(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, list(data.values()))
            conn.commit()
            return conn.lastrowid
            
    def find_one(self, query):
        """MongoDB-like find_one method"""
        table_name = 'cached_results'  # Default table for caching
        where_conditions = []
        params = []
        
        for key, value in query.items():
            if isinstance(value, dict):
                # Handle MongoDB-style operators
                for op, val in value.items():
                    if op == '$gt':
                        where_conditions.append(f"{key} > ?")
                        params.append(val)
            else:
                where_conditions.append(f"{key} = ?")
                params.append(value)
        
        where_clause = ' AND '.join(where_conditions) if where_conditions else '1=1'
        query = f'SELECT * FROM {table_name} WHERE {where_clause}'
        
        return self.fetch_one(query, params)
        
    def insert_one(self, data):
        """MongoDB-like insert_one method"""
        return self.insert('cached_results', data)
        
    def replace_one(self, filter_dict, replacement, upsert=False):
        """MongoDB-like replace_one method"""
        where_conditions = []
        params = []
        
        for key, value in filter_dict.items():
            where_conditions.append(f"{key} = ?")
            params.append(value)
        
        where_clause = ' AND '.join(where_conditions)
        
        # Try to update first
        update_query = f'''
            UPDATE cached_results 
            SET {', '.join(f'{k} = ?' for k in replacement.keys())}
            WHERE {where_clause}
        '''
        update_params = list(replacement.values()) + params
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(update_query, update_params)
            if cursor.rowcount == 0 and upsert:
                # If no rows were updated and upsert is True, insert new record
                self.insert_one(replacement)
            conn.commit()
            
    def delete_one(self, filter_dict):
        """MongoDB-like delete_one method"""
        where_conditions = []
        params = []
        
        for key, value in filter_dict.items():
            where_conditions.append(f"{key} = ?")
            params.append(value)
        
        where_clause = ' AND '.join(where_conditions)
        query = f'DELETE FROM cached_results WHERE {where_clause} LIMIT 1'
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
            conn.commit()
            
    def delete_many(self, filter_dict=None):
        """MongoDB-like delete_many method"""
        if filter_dict:
            where_conditions = []
            params = []
            
            for key, value in filter_dict.items():
                where_conditions.append(f"{key} = ?")
                params.append(value)
            
            where_clause = ' AND '.join(where_conditions)
            query = f'DELETE FROM cached_results WHERE {where_clause}'
        else:
            query = 'DELETE FROM cached_results'
            params = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(query, params)
            conn.commit()

    def initialize_cache_database(self):
        """Initialize the cache database with required tables."""
        self.execute('''
            CREATE TABLE IF NOT EXISTS cached_results (
                cache_key TEXT PRIMARY KEY,
                results TEXT,
                page_number INTEGER,
                next_page_token TEXT,
                total_results INTEGER,
                timestamp TEXT,
                expiry TEXT
            )
        ''')
